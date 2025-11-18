"""Validate curated mappings against ontology files and web APIs."""

import csv
import hashlib
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import requests
from tqdm import tqdm

from .mappers import ChemicalMapper, EnzymeMapper


class OntologyIndex:
    """Index for fast lookup of ontology terms from TSV files."""

    def __init__(self, tsv_path: Path):
        """Load ontology TSV file into memory for fast lookup."""
        self.tsv_path = tsv_path
        self.terms = {}
        self._load()

    def _load(self):
        """Load TSV file into dictionary."""
        if not self.tsv_path.exists():
            print(f"Warning: {self.tsv_path} not found")
            return

        with open(self.tsv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                term_id = row.get("id", "")
                if not term_id:
                    continue

                # Normalize ID format
                if term_id.startswith("https://www.ebi.ac.uk/intenz/"):
                    # Extract EC number from URL
                    match = re.search(r"ec=([0-9.]+)", term_id)
                    if match:
                        term_id = match.group(1)

                self.terms[term_id] = {
                    "id": term_id,
                    "name": row.get("name", ""),
                    "description": row.get("description", ""),
                    "deprecated": row.get("deprecated", "").lower() == "true",
                    "category": row.get("category", ""),
                    "synonym": row.get("synonym", ""),
                }

    def lookup(self, term_id: str) -> Optional[dict[str, Any]]:
        """Lookup a term by ID."""
        return self.terms.get(term_id)


class MappingValidator:
    """Validator for curated chemical and enzyme mappings."""

    def __init__(self, ontology_dir: Path):
        """Initialize validator with ontology directory."""
        self.ontology_dir = ontology_dir
        self.stats = defaultdict(int)
        self.errors = []
        self.warnings = []

        # Load ontology indexes
        print("Loading ontology indexes...")
        self.chebi_index = OntologyIndex(ontology_dir / "chebi_nodes.tsv")
        self.go_index = OntologyIndex(ontology_dir / "go_nodes.tsv")
        self.ec_index = OntologyIndex(ontology_dir / "ec_nodes.tsv")

        print(f"  CHEBI: {len(self.chebi_index.terms):,} terms")
        print(f"  GO: {len(self.go_index.terms):,} terms")
        print(f"  EC: {len(self.ec_index.terms):,} terms")

        # API endpoints
        self.pubchem_api = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.kegg_api = "https://rest.kegg.jp"

    def validate_chebi(self, chebi_id: str) -> bool:
        """Validate CHEBI ID exists and is not deprecated."""
        if not chebi_id:
            return False

        term = self.chebi_index.lookup(chebi_id)
        if not term:
            self.errors.append(f"CHEBI ID not found: {chebi_id}")
            return False

        if term.get("deprecated"):
            self.warnings.append(f"CHEBI ID deprecated: {chebi_id} ({term.get('name')})")
            return True  # Still valid, just deprecated

        self.stats["chebi_valid"] += 1
        return True

    def validate_pubchem(self, pubchem_cid: str) -> bool:
        """Validate PubChem CID via API."""
        if not pubchem_cid:
            return False

        try:
            url = f"{self.pubchem_api}/compound/cid/{pubchem_cid}/description/JSON"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                self.stats["pubchem_valid"] += 1
                return True
            else:
                self.errors.append(f"PubChem CID not found: {pubchem_cid} (HTTP {response.status_code})")
                return False

        except Exception as e:
            self.errors.append(f"PubChem API error for {pubchem_cid}: {e}")
            return False

    def validate_ec(self, ec_number: str) -> bool:
        """Validate EC number exists."""
        if not ec_number:
            return False

        term = self.ec_index.lookup(ec_number)
        if not term:
            self.errors.append(f"EC number not found: {ec_number}")
            return False

        if term.get("deprecated"):
            self.warnings.append(f"EC number deprecated: {ec_number} ({term.get('name')})")
            return True

        self.stats["ec_valid"] += 1
        return True

    def validate_go(self, go_id: str) -> bool:
        """Validate GO term exists and is not deprecated."""
        if not go_id:
            return False

        term = self.go_index.lookup(go_id)
        if not term:
            self.errors.append(f"GO term not found: {go_id}")
            return False

        if term.get("deprecated"):
            self.warnings.append(f"GO term deprecated: {go_id} ({term.get('name')})")
            return True

        self.stats["go_valid"] += 1
        return True

    def validate_kegg_ko(self, kegg_ko: str) -> bool:
        """Validate KEGG KO via API."""
        if not kegg_ko:
            return False

        try:
            url = f"{self.kegg_api}/get/{kegg_ko}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                self.stats["kegg_valid"] += 1
                return True
            else:
                self.errors.append(f"KEGG KO not found: {kegg_ko} (HTTP {response.status_code})")
                return False

        except Exception as e:
            self.errors.append(f"KEGG API error for {kegg_ko}: {e}")
            return False

    def validate_substrate_mappings(self):
        """Validate all substrate mappings."""
        print("\n" + "=" * 70)
        print("VALIDATING SUBSTRATE MAPPINGS")
        print("=" * 70)

        total = len(ChemicalMapper.SUBSTRATE_MAPPINGS)
        print(f"Total substrate mappings: {total}")

        for well_code, mapping in tqdm(ChemicalMapper.SUBSTRATE_MAPPINGS.items(), desc="Substrates"):
            self.stats["substrates_total"] += 1

            # Validate CHEBI
            if "chebi" in mapping:
                self.validate_chebi(mapping["chebi"])
            else:
                self.stats["substrates_no_chebi"] += 1

            # Validate PubChem (with rate limiting)
            if "pubchem" in mapping:
                self.validate_pubchem(mapping["pubchem"])
                time.sleep(0.2)  # Rate limit: 5 requests/second
            else:
                self.stats["substrates_no_pubchem"] += 1

    def validate_enzyme_mappings(self):
        """Validate all enzyme annotations."""
        print("\n" + "=" * 70)
        print("VALIDATING ENZYME MAPPINGS")
        print("=" * 70)

        mapper = EnzymeMapper()
        total = len(mapper.ENZYME_ANNOTATIONS)
        print(f"Total enzyme annotations: {total}")

        for enzyme_name, annotation in tqdm(
            mapper.ENZYME_ANNOTATIONS.items(), desc="Enzymes"
        ):
            self.stats["enzymes_total"] += 1

            # Validate EC number
            if annotation.get("ec_number"):
                self.validate_ec(annotation["ec_number"])
            else:
                self.stats["enzymes_no_ec"] += 1

            # Validate GO terms
            go_terms = annotation.get("go_terms", [])
            if go_terms:
                for go_term in go_terms:
                    self.validate_go(go_term)
            else:
                self.stats["enzymes_no_go"] += 1

            # Validate KEGG KO (with rate limiting)
            if annotation.get("kegg_ko"):
                self.validate_kegg_ko(annotation["kegg_ko"])
                time.sleep(0.2)  # Rate limit
            else:
                self.stats["enzymes_no_kegg"] += 1

    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 70)
        print("VALIDATION REPORT")
        print("=" * 70)

        print("\n📊 STATISTICS:")
        print(f"  Substrates validated: {self.stats['substrates_total']}")
        print(f"    - CHEBI valid: {self.stats['chebi_valid']}")
        print(f"    - CHEBI missing: {self.stats['substrates_no_chebi']}")
        print(f"    - PubChem valid: {self.stats['pubchem_valid']}")
        print(f"    - PubChem missing: {self.stats['substrates_no_pubchem']}")

        print(f"\n  Enzymes validated: {self.stats['enzymes_total']}")
        print(f"    - EC valid: {self.stats['ec_valid']}")
        print(f"    - EC missing: {self.stats['enzymes_no_ec']}")
        print(f"    - GO valid: {self.stats['go_valid']}")
        print(f"    - GO missing: {self.stats['enzymes_no_go']}")
        print(f"    - KEGG valid: {self.stats['kegg_valid']}")
        print(f"    - KEGG missing: {self.stats['enzymes_no_kegg']}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        else:
            print("\n✅ No errors found!")

        print("\n" + "=" * 70)

        return len(self.errors) == 0

    def save_report(self, output_path: Path):
        """Save validation report to JSON."""
        report = {
            "statistics": dict(self.stats),
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "valid": len(self.errors) == 0,
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n📝 Report saved to {output_path}")


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def track_ontology_files(ontology_dir: Path, metadata_path: Path):
    """Track ontology file versions via SHA256 hashes."""
    print("\n" + "=" * 70)
    print("TRACKING ONTOLOGY FILE VERSIONS")
    print("=" * 70)

    files_to_track = [
        "chebi_nodes.tsv",
        "ec_nodes.tsv",
        "go_nodes.tsv",
    ]

    metadata = {}

    for filename in files_to_track:
        file_path = ontology_dir / filename
        if file_path.exists():
            file_hash = compute_file_hash(file_path)
            file_size = file_path.stat().st_size
            file_mtime = file_path.stat().st_mtime

            metadata[filename] = {
                "path": str(file_path),
                "sha256": file_hash,
                "size_bytes": file_size,
                "size_human": f"{file_size / 1024 / 1024:.1f} MB",
                "modified_time": file_mtime,
            }

            print(f"  {filename}:")
            print(f"    SHA256: {file_hash}")
            print(f"    Size: {file_size / 1024 / 1024:.1f} MB")
        else:
            print(f"  {filename}: NOT FOUND")

    # Save metadata
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✅ Metadata saved to {metadata_path}")
    return metadata


def main():
    """Main validation entry point."""
    # Path to KG-Microbe ontologies
    ontology_dir = Path(
        "/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/kg-microbe/data/transformed/ontologies"
    )

    if not ontology_dir.exists():
        print(f"Error: Ontology directory not found: {ontology_dir}")
        sys.exit(1)

    # Track ontology file versions
    metadata_path = Path("ontology_file_metadata.json")
    track_ontology_files(ontology_dir, metadata_path)

    # Create validator
    validator = MappingValidator(ontology_dir)

    # Validate substrates
    validator.validate_substrate_mappings()

    # Validate enzymes
    validator.validate_enzyme_mappings()

    # Print report
    success = validator.print_report()

    # Save report
    report_path = Path("validation_report.json")
    validator.save_report(report_path)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
