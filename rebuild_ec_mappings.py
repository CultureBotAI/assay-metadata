#!/usr/bin/env python3
"""
Rebuild EC number mappings using exact matching against ExpASy ENZYME database.

This script:
1. Loads all unique enzyme names
2. Runs exact matching algorithm
3. Generates detailed mapping report
4. Creates new EC mappings for mappers.py
"""

import json
from pathlib import Path
from enzyme_ec_exact_matcher import ExpAsyEnzymeDatabase, EnzymeECMatcher
from typing import Dict, List, Optional, Tuple


class ECMappingRebuilder:
    """Rebuild EC mappings with exact matching."""

    def __init__(self, database: ExpAsyEnzymeDatabase):
        """Initialize rebuilder."""
        self.database = database
        self.matcher = EnzymeECMatcher(database)
        self.results = {
            'exact_primary': [],
            'exact_synonym': [],
            'partial_ec': [],
            'unmapped': []
        }

    def process_enzyme(self, enzyme_name: str) -> Dict:
        """Process a single enzyme name.

        Returns:
            Dict with match results
        """
        # Try exact match with substrate handling
        result = self.matcher.match_with_substrate(enzyme_name)

        if result:
            ec, matched_name, match_type, substrate = result
            return {
                'enzyme_name': enzyme_name,
                'ec_number': ec,
                'matched_name': matched_name,
                'match_type': match_type,
                'substrate': substrate,
                'category': f'exact_{match_type}'
            }

        # Try finding enzyme family
        partial_ec = self.matcher.find_enzyme_family(enzyme_name)
        if partial_ec:
            return {
                'enzyme_name': enzyme_name,
                'ec_number': partial_ec,
                'matched_name': None,
                'match_type': 'partial',
                'substrate': None,
                'category': 'partial_ec'
            }

        # Unmapped
        return {
            'enzyme_name': enzyme_name,
            'ec_number': None,
            'matched_name': None,
            'match_type': None,
            'substrate': None,
            'category': 'unmapped'
        }

    def process_all_enzymes(self, enzyme_names: List[str]) -> None:
        """Process all enzyme names."""
        print(f"\nProcessing {len(enzyme_names)} enzyme names...")

        for enzyme_name in enzyme_names:
            result = self.process_enzyme(enzyme_name)
            category = result['category']

            self.results[category].append(result)

    def generate_report(self, output_path: str = "ec_mapping_report.md") -> None:
        """Generate detailed mapping report in Markdown."""
        total = sum(len(results) for results in self.results.values())

        report = ["# EC Number Mapping Report - Exact Matching\n"]
        report.append(f"**Generated**: {Path().absolute()}\n")
        report.append(f"**Total Enzymes**: {total}\n")
        report.append("\n## Summary\n")

        # Summary statistics
        report.append("| Category | Count | Percentage |\n")
        report.append("|----------|-------|------------|\n")

        for category, results in self.results.items():
            count = len(results)
            pct = (count / total * 100) if total > 0 else 0
            display_name = category.replace('_', ' ').title()
            report.append(f"| {display_name} | {count} | {pct:.1f}% |\n")

        # Exact Primary Matches
        report.append("\n## Exact Matches (Primary Name)\n")
        report.append(f"**Count**: {len(self.results['exact_primary'])}\n\n")

        if self.results['exact_primary']:
            report.append("| Enzyme Name | EC Number | Matched Name |\n")
            report.append("|-------------|-----------|-------------|\n")
            for r in sorted(self.results['exact_primary'], key=lambda x: x['enzyme_name']):
                substrate_note = f" ({r['substrate']})" if r['substrate'] else ""
                report.append(f"| {r['enzyme_name']}{substrate_note} | {r['ec_number']} | {r['matched_name']} |\n")

        # Exact Synonym Matches
        report.append("\n## Exact Matches (Synonym)\n")
        report.append(f"**Count**: {len(self.results['exact_synonym'])}\n\n")

        if self.results['exact_synonym']:
            report.append("| Enzyme Name | EC Number | Matched Synonym |\n")
            report.append("|-------------|-----------|---------------|\n")
            for r in sorted(self.results['exact_synonym'], key=lambda x: x['enzyme_name']):
                substrate_note = f" ({r['substrate']})" if r['substrate'] else ""
                report.append(f"| {r['enzyme_name']}{substrate_note} | {r['ec_number']} | {r['matched_name']} |\n")

        # Partial EC Assignments
        report.append("\n## Partial EC Assignments (Enzyme Family)\n")
        report.append(f"**Count**: {len(self.results['partial_ec'])}\n\n")

        if self.results['partial_ec']:
            report.append("| Enzyme Name | Partial EC | Note |\n")
            report.append("|-------------|-----------|------|\n")
            for r in sorted(self.results['partial_ec'], key=lambda x: x['enzyme_name']):
                report.append(f"| {r['enzyme_name']} | {r['ec_number']} | Enzyme family level |\n")

        # Unmapped
        report.append("\n## Unmapped Enzymes\n")
        report.append(f"**Count**: {len(self.results['unmapped'])}\n\n")

        if self.results['unmapped']:
            report.append("| Enzyme Name | Reason |\n")
            report.append("|-------------|--------|\n")
            for r in sorted(self.results['unmapped'], key=lambda x: x['enzyme_name']):
                report.append(f"| {r['enzyme_name']} | No exact or family match |\n")

        # Write report
        with open(output_path, 'w') as f:
            f.writelines(report)

        print(f"\nReport saved to {output_path}")

    def generate_python_mappings(self, output_path: str = "new_ec_mappings.py") -> None:
        """Generate Python code for new EC mappings."""
        lines = ["# Generated EC Mappings from ExpASy ENZYME Database\n"]
        lines.append("# Using exact matching algorithm\n\n")

        # ENZYME_EC_MAPPINGS - for exact matches only
        lines.append("ENZYME_EC_MAPPINGS = {\n")

        all_exact = self.results['exact_primary'] + self.results['exact_synonym']
        for r in sorted(all_exact, key=lambda x: x['enzyme_name']):
            substrate_note = f" ({r['substrate']})" if r['substrate'] else ""
            match_note = f" # Matched: {r['matched_name']} ({r['match_type']})"
            lines.append(f"    \"{r['enzyme_name']}\": \"{r['ec_number']}\",{match_note}\n")

        lines.append("}\n\n")

        # Partial EC mappings (enzyme family level)
        lines.append("# Partial EC Numbers (Enzyme Family Level)\n")
        lines.append("PARTIAL_EC_MAPPINGS = {\n")

        for r in sorted(self.results['partial_ec'], key=lambda x: x['enzyme_name']):
            lines.append(f"    \"{r['enzyme_name']}\": \"{r['ec_number']}\",  # Enzyme family\n")

        lines.append("}\n\n")

        # Unmapped enzymes
        lines.append("# Unmapped Enzymes (No EC Assignment)\n")
        lines.append("UNMAPPED_ENZYMES = [\n")

        for r in sorted(self.results['unmapped'], key=lambda x: x['enzyme_name']):
            lines.append(f"    \"{r['enzyme_name']}\",\n")

        lines.append("]\n")

        # Write file
        with open(output_path, 'w') as f:
            f.writelines(lines)

        print(f"Python mappings saved to {output_path}")

    def generate_tsv(self, output_path: str = "ec_mappings_exact.tsv") -> None:
        """Generate TSV file with all mappings."""
        lines = ["enzyme_name\tec_number\tmatch_type\tmatched_name\tsubstrate\n"]

        all_mapped = (
            self.results['exact_primary'] +
            self.results['exact_synonym'] +
            self.results['partial_ec']
        )

        for r in sorted(all_mapped, key=lambda x: x['enzyme_name']):
            substrate = r['substrate'] or ''
            matched_name = r['matched_name'] or ''
            match_type = r['match_type'] or 'partial'
            lines.append(f"{r['enzyme_name']}\t{r['ec_number']}\t{match_type}\t{matched_name}\t{substrate}\n")

        with open(output_path, 'w') as f:
            f.writelines(lines)

        print(f"TSV mappings saved to {output_path}")


def main():
    """Main function."""
    print("=" * 70)
    print("EC Number Mapping Rebuilder - Exact Matching")
    print("=" * 70)

    # Load database
    print("\nLoading ExpASy ENZYME database...")
    db = ExpAsyEnzymeDatabase.load_cache("expasy_enzyme_db.json")

    # Load enzyme names
    print("Loading enzyme names...")
    with open("unique_enzyme_names.txt", 'r') as f:
        enzyme_names = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(enzyme_names)} enzyme names")

    # Process all enzymes
    rebuilder = ECMappingRebuilder(db)
    rebuilder.process_all_enzymes(enzyme_names)

    # Generate outputs
    print("\n" + "=" * 70)
    print("Generating Outputs")
    print("=" * 70)

    rebuilder.generate_report("ec_mapping_report.md")
    rebuilder.generate_python_mappings("new_ec_mappings.py")
    rebuilder.generate_tsv("ec_mappings_exact.tsv")

    # Print summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    total = sum(len(results) for results in rebuilder.results.values())
    for category, results in rebuilder.results.items():
        count = len(results)
        pct = (count / total * 100) if total > 0 else 0
        display_name = category.replace('_', ' ').title()
        print(f"  {display_name}: {count} ({pct:.1f}%)")

    print("\n" + "=" * 70)
    print("✓ EC mappings rebuilt successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
