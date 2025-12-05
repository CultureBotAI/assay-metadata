#!/usr/bin/env python3
"""
Exact matching engine for enzyme names to EC numbers using ExpASy ENZYME database.

This module provides deterministic EC number assignment based on exact matching
against primary labels and synonyms from the ExpASy ENZYME flat file database.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class EnzymeEntry:
    """Represents an enzyme entry from ExpASy ENZYME database."""

    ec_number: str
    primary_name: str
    alternate_names: List[str]
    status: str  # "active", "transferred", "deleted"
    transferred_to: Optional[str] = None

    def all_names(self) -> List[str]:
        """Get all names (primary + alternates)."""
        return [self.primary_name] + self.alternate_names


class ExpAsyEnzymeDatabase:
    """Parser and cache for ExpASy ENZYME flat file database."""

    def __init__(self, enzyme_dat_path: str = "enzyme.dat"):
        """Initialize database from enzyme.dat file."""
        self.enzyme_dat_path = Path(enzyme_dat_path)
        self.entries: Dict[str, EnzymeEntry] = {}
        self._name_to_ec: Dict[str, str] = {}

    def parse(self) -> None:
        """Parse enzyme.dat file and build index."""
        print(f"Parsing {self.enzyme_dat_path}...")

        current_entry = {}

        with open(self.enzyme_dat_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip()

                if line.startswith('ID   '):
                    current_entry = {'ec': line[5:].strip()}

                elif line.startswith('DE   '):
                    # Primary name - remove trailing period
                    name = line[5:].strip().rstrip('.')
                    current_entry['primary_name'] = name

                elif line.startswith('AN   '):
                    # Alternate names - may span multiple lines
                    if 'alternate_names' not in current_entry:
                        current_entry['alternate_names'] = []
                    # Remove trailing period and split on semicolon
                    names = line[5:].strip().rstrip('.')
                    current_entry['alternate_names'].append(names)

                elif line.startswith('DE   Transferred entry:'):
                    # Transferred enzyme
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        current_entry['transferred_to'] = match.group(1)
                        current_entry['status'] = 'transferred'

                elif line.startswith('DE   Deleted entry'):
                    current_entry['status'] = 'deleted'

                elif line == '//':
                    # End of entry
                    if 'ec' in current_entry:
                        self._add_entry(current_entry)
                    current_entry = {}

        print(f"Parsed {len(self.entries)} enzyme entries")
        self._build_name_index()

    def _add_entry(self, entry_dict: dict) -> None:
        """Add a parsed entry to the database."""
        ec = entry_dict.get('ec')
        if not ec:
            return

        # Set default status if not specified
        status = entry_dict.get('status', 'active')

        # Get primary name
        primary_name = entry_dict.get('primary_name', '')

        # Get alternate names (may need to be split)
        alt_names_raw = entry_dict.get('alternate_names', [])
        alternate_names = []
        for name_str in alt_names_raw:
            # Split on semicolon if multiple names in one AN field
            for name in name_str.split(';'):
                name = name.strip()
                if name:
                    alternate_names.append(name)

        entry = EnzymeEntry(
            ec_number=ec,
            primary_name=primary_name,
            alternate_names=alternate_names,
            status=status,
            transferred_to=entry_dict.get('transferred_to')
        )

        self.entries[ec] = entry

    def _build_name_index(self) -> None:
        """Build reverse index from normalized names to EC numbers."""
        print("Building name index...")

        for ec, entry in self.entries.items():
            # Only index active entries
            if entry.status != 'active':
                continue

            # Index all names
            for name in entry.all_names():
                normalized = self.normalize_name(name)
                # Store the first (primary) match
                if normalized not in self._name_to_ec:
                    self._name_to_ec[normalized] = ec

        print(f"Indexed {len(self._name_to_ec)} normalized enzyme names")

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize enzyme name for matching.

        Applies:
        - Lowercase conversion
        - Remove extra whitespace
        - Normalize hyphens/dashes
        - Remove punctuation at end
        """
        # Lowercase
        name = name.lower()

        # Normalize whitespace
        name = ' '.join(name.split())

        # Normalize hyphens (em-dash, en-dash to hyphen)
        name = name.replace('—', '-').replace('–', '-')

        # Remove trailing period
        name = name.rstrip('.')

        return name

    def save_cache(self, cache_path: str = "expasy_enzyme_db.json") -> None:
        """Save parsed database to JSON cache."""
        cache_data = {
            'entries': {
                ec: {
                    'ec_number': entry.ec_number,
                    'primary_name': entry.primary_name,
                    'alternate_names': entry.alternate_names,
                    'status': entry.status,
                    'transferred_to': entry.transferred_to
                }
                for ec, entry in self.entries.items()
            },
            'name_index': self._name_to_ec
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)

        print(f"Saved cache to {cache_path}")

    @classmethod
    def load_cache(cls, cache_path: str = "expasy_enzyme_db.json") -> 'ExpAsyEnzymeDatabase':
        """Load database from JSON cache."""
        db = cls.__new__(cls)

        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Reconstruct entries
        db.entries = {}
        for ec, entry_dict in cache_data['entries'].items():
            db.entries[ec] = EnzymeEntry(**entry_dict)

        # Load name index
        db._name_to_ec = cache_data['name_index']

        print(f"Loaded {len(db.entries)} entries from cache")
        return db


class EnzymeECMatcher:
    """Exact matching engine for enzyme names to EC numbers."""

    def __init__(self, database: ExpAsyEnzymeDatabase):
        """Initialize matcher with database."""
        self.database = database

    def extract_substrate_info(self, name: str) -> Tuple[str, Optional[str]]:
        """Extract base enzyme name and substrate specificity.

        Args:
            name: Enzyme name (e.g., "Esterase (C4)", "Esterase Lipase (C8)")

        Returns:
            Tuple of (base_name, substrate_info)
        """
        # Pattern for substrate in parentheses
        match = re.search(r'\(([^)]+)\)$', name.strip())

        if match:
            substrate = match.group(1)
            base_name = name[:match.start()].strip()
            return base_name, substrate

        return name, None

    def match_exact(self, enzyme_name: str) -> Optional[Tuple[str, str, str]]:
        """Find exact EC match for enzyme name.

        Args:
            enzyme_name: Enzyme name to match

        Returns:
            Tuple of (EC number, matched_name, match_type) or None
            match_type: 'primary' or 'synonym'
        """
        normalized = self.database.normalize_name(enzyme_name)

        # Try exact match in name index
        if normalized in self.database._name_to_ec:
            ec = self.database._name_to_ec[normalized]
            entry = self.database.entries[ec]

            # Determine if it's primary or synonym
            normalized_primary = self.database.normalize_name(entry.primary_name)
            if normalized == normalized_primary:
                return (ec, entry.primary_name, 'primary')
            else:
                # Find which alternate name matched
                for alt_name in entry.alternate_names:
                    if normalized == self.database.normalize_name(alt_name):
                        return (ec, alt_name, 'synonym')

        return None

    def match_with_substrate(self, enzyme_name: str) -> Optional[Tuple[str, str, str, Optional[str]]]:
        """Try matching with substrate handling.

        Args:
            enzyme_name: Enzyme name possibly with substrate info

        Returns:
            Tuple of (EC, matched_name, match_type, substrate_info) or None
        """
        # Try exact match first
        result = self.match_exact(enzyme_name)
        if result:
            return (*result, None)

        # Extract substrate info and try base name
        base_name, substrate = self.extract_substrate_info(enzyme_name)
        if substrate:
            result = self.match_exact(base_name)
            if result:
                return (*result, substrate)

        return None

    def find_enzyme_family(self, enzyme_name: str) -> Optional[str]:
        """Try to find enzyme family (partial EC) by keyword matching.

        Args:
            enzyme_name: Enzyme name

        Returns:
            Partial EC number (e.g., "3.1.1.-") or None
        """
        # Extract key terms
        name_lower = enzyme_name.lower()

        # Common enzyme class keywords
        keywords_to_class = {
            'kinase': '2.7.-.-',
            'phosphatase': '3.1.3.-',
            'dehydrogenase': '1.1.1.-',
            'oxidase': '1.-.-.-',
            'reductase': '1.-.-.-',
            'transferase': '2.-.-.-',
            'hydrolase': '3.-.-.-',
            'lyase': '4.-.-.-',
            'isomerase': '5.-.-.-',
            'ligase': '6.-.-.-',
            'esterase': '3.1.1.-',
            'lipase': '3.1.1.-',
            'peptidase': '3.4.-.-',
            'protease': '3.4.-.-',
            'glycosidase': '3.2.1.-',
            'galactosidase': '3.2.1.-',
            'glucosidase': '3.2.1.-',
            'amidase': '3.5.-.-',
            'aminidase': '3.4.-.-',
        }

        for keyword, partial_ec in keywords_to_class.items():
            if keyword in name_lower:
                return partial_ec

        return None


def main():
    """Main function to parse enzyme.dat and create cache."""
    print("=" * 70)
    print("ExpASy ENZYME Database Parser")
    print("=" * 70)

    # Parse enzyme.dat
    db = ExpAsyEnzymeDatabase("enzyme.dat")
    db.parse()

    # Save cache
    db.save_cache("expasy_enzyme_db.json")

    # Test matching
    print("\n" + "=" * 70)
    print("Testing Exact Matcher")
    print("=" * 70)

    matcher = EnzymeECMatcher(db)

    test_names = [
        "carboxylesterase",
        "Esterase",
        "Esterase (C4)",
        "Esterase Lipase",
        "Alkaline phosphatase",
        "alcohol dehydrogenase",
        "Trypsin",
        "beta-Galactosidase",
    ]

    for name in test_names:
        result = matcher.match_with_substrate(name)
        if result:
            ec, matched_name, match_type, substrate = result
            print(f"\n✓ {name}")
            print(f"  EC: {ec}")
            print(f"  Matched: {matched_name} ({match_type})")
            if substrate:
                print(f"  Substrate: {substrate}")
        else:
            family_ec = matcher.find_enzyme_family(name)
            if family_ec:
                print(f"\n~ {name}")
                print(f"  Partial EC: {family_ec} (enzyme family)")
            else:
                print(f"\n✗ {name}")
                print(f"  No match found")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
