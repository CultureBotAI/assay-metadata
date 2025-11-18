"""Validate API kit mappings against actual extracted data.

This script validates that our substrate/enzyme mappings cover all well codes
found in the actual extracted BacDive assay data (not just official documentation).
"""

import json
from pathlib import Path
from typing import Any
from collections import defaultdict

from .mappers import ChemicalMapper


class DataValidator:
    """Validator for checking mappings against actual extracted data."""

    def __init__(self, data_file: Path):
        """Initialize validator with extracted data.

        Args:
            data_file: Path to api_kits_list.json
        """
        self.data_file = data_file
        self.mapper = ChemicalMapper()
        self.unmapped_codes = defaultdict(list)
        self.mapped_codes = defaultdict(list)
        self.coverage_stats = {}

    def load_extracted_data(self) -> dict[str, Any]:
        """Load the extracted API kit data."""
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def check_code_mapping(self, code: str, kit_name: str) -> tuple[bool, str, str]:
        """Check if a well code has a mapping.

        Args:
            code: Well code to check
            kit_name: API kit name for context

        Returns:
            Tuple of (is_mapped, location, name)
        """
        # Check kit-specific mappings first
        mapping = self.mapper.get_substrate_mapping(code, kit_name)
        if mapping:
            location = f"KIT_SPECIFIC[{kit_name}]" if (
                kit_name in self.mapper.KIT_SPECIFIC_MAPPINGS and
                code in self.mapper.KIT_SPECIFIC_MAPPINGS[kit_name]
            ) else "SUBSTRATE_MAPPINGS"
            return (True, location, mapping.get("name", ""))

        # Check enzyme tests
        if code in self.mapper.ENZYME_TESTS:
            return (True, "ENZYME_TESTS", self.mapper.ENZYME_TESTS[code])

        # Check enzyme activity tests
        if code in self.mapper.ENZYME_ACTIVITY_TESTS:
            return (True, "ENZYME_ACTIVITY_TESTS", self.mapper.ENZYME_ACTIVITY_TESTS[code])

        # Check phenotypic tests
        if code in self.mapper.PHENOTYPIC_TESTS:
            return (True, "PHENOTYPIC_TESTS", self.mapper.PHENOTYPIC_TESTS[code])

        return (False, "UNMAPPED", "")

    def validate_kit(self, kit_data: dict[str, Any]) -> dict[str, Any]:
        """Validate mappings for a single kit.

        Args:
            kit_data: Kit data from api_kits_list.json

        Returns:
            Dictionary with validation results
        """
        kit_name = kit_data["kit_name"]
        wells = kit_data["wells"]

        mapped = []
        unmapped = []

        for code in wells:
            is_mapped, location, name = self.check_code_mapping(code, kit_name)

            if is_mapped:
                mapped.append({
                    "code": code,
                    "name": name,
                    "location": location
                })
            else:
                unmapped.append(code)

        coverage_pct = (len(mapped) / len(wells) * 100) if wells else 0

        return {
            "kit_name": kit_name,
            "total_wells": len(wells),
            "mapped": len(mapped),
            "unmapped": len(unmapped),
            "coverage_percent": coverage_pct,
            "mapped_codes": mapped,
            "unmapped_codes": unmapped,
            "occurrence_count": kit_data.get("occurrence_count", 0)
        }

    def validate_all_kits(self) -> dict[str, Any]:
        """Validate all API kits in the extracted data.

        Returns:
            Dictionary with complete validation results
        """
        print("=" * 80)
        print("DATA-DRIVEN API KIT VALIDATION")
        print("=" * 80)
        print(f"\nValidating against extracted data: {self.data_file}")
        print()

        data = self.load_extracted_data()
        results = {}

        total_wells = 0
        total_mapped = 0
        total_unmapped = 0
        all_unmapped_codes = set()

        for kit_data in data["kits"]:
            kit_name = kit_data["kit_name"]
            print(f"Validating {kit_name}...")

            kit_results = self.validate_kit(kit_data)
            results[kit_name] = kit_results

            total_wells += kit_results["total_wells"]
            total_mapped += kit_results["mapped"]
            total_unmapped += kit_results["unmapped"]

            all_unmapped_codes.update(kit_results["unmapped_codes"])

            # Print progress
            coverage = kit_results["coverage_percent"]
            mapped = kit_results["mapped"]
            total = kit_results["total_wells"]
            unmapped = kit_results["unmapped"]

            if coverage == 100:
                print(f"  ✓ {mapped}/{total} ({coverage:.1f}%)")
            else:
                print(f"  ⚠ {mapped}/{total} ({coverage:.1f}%) - {unmapped} unmapped")

        # Calculate overall statistics
        overall_coverage = (total_mapped / total_wells * 100) if total_wells > 0 else 0

        summary = {
            "total_kits": len(results),
            "total_wells": total_wells,
            "total_mapped": total_mapped,
            "total_unmapped": total_unmapped,
            "total_unique_unmapped": len(all_unmapped_codes),
            "coverage_percent": overall_coverage,
            "all_unmapped_codes": sorted(all_unmapped_codes)
        }

        return {
            "kits": results,
            "summary": summary
        }

    def generate_report(self, output_path: Path):
        """Generate comprehensive data validation report.

        Args:
            output_path: Path to save the report
        """
        results = self.validate_all_kits()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Validation report saved to: {output_path}")

        # Print summary
        summary = results["summary"]
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total kits: {summary['total_kits']}")
        print(f"Total well codes: {summary['total_wells']}")
        print(f"Mapped codes: {summary['total_mapped']} ({summary['coverage_percent']:.1f}%)")
        print(f"Unmapped codes: {summary['total_unmapped']}")
        print(f"Unique unmapped: {summary['total_unique_unmapped']}")

        if summary['total_unmapped'] > 0:
            print(f"\n❌ {summary['total_unmapped']} well codes need mapping")
            print(f"\nUnmapped codes ({summary['total_unique_unmapped']} unique):")
            for code in summary['all_unmapped_codes']:
                # Count occurrences across kits
                count = sum(1 for kit in results["kits"].values()
                           if code in kit.get("unmapped_codes", []))
                print(f"  - {code} (appears in {count} kit(s))")
        else:
            print("\n✅ All well codes are mapped!")

        # Show kits with low coverage
        print("\nKits needing attention:")
        for kit_name, kit_data in results["kits"].items():
            if kit_data["coverage_percent"] < 100:
                print(f"  - {kit_name}: {kit_data['coverage_percent']:.1f}% "
                      f"({kit_data['unmapped']} unmapped, {kit_data['occurrence_count']} strains)")

        print("=" * 80)


def main():
    """Run data-driven validation."""
    data_file = Path("data/api_kits_list.json")

    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        print("Please run extraction first: make extract")
        return

    validator = DataValidator(data_file)
    output_path = Path("data_validation_report.json")
    validator.generate_report(output_path)


if __name__ == "__main__":
    main()
