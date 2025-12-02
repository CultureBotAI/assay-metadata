"""Validate API kit well code mappings against official documentation.

This script validates that our chemical/enzyme mappings for API kit well codes
are accurate by cross-referencing with official bioMérieux documentation and
published scientific literature.
"""

import json
from pathlib import Path
from typing import Any
from collections import defaultdict

from .mappers import ChemicalMapper
from .parser import BacDiveParser


class APIKitValidator:
    """Validator for API kit well code mappings."""

    # Official well code mappings from bioMérieux documentation
    # Source: API package inserts and published literature
    OFFICIAL_MAPPINGS = {
        "API 20E": {
            "name": "API 20E - Enterobacteriaceae Identification",
            "wells": 20,
            "source": "bioMérieux Package Insert REF 20 100/20 160",
            "url": "https://microbeonline.com/api-20e-test-system/",
            "mappings": {
                "ONPG": {"type": "enzyme", "name": "β-galactosidase", "substrate": "o-nitrophenyl-β-D-galactopyranoside"},
                "ADH": {"type": "enzyme", "name": "Arginine dihydrolase", "substrate": "Arginine"},
                "LDC": {"type": "enzyme", "name": "Lysine decarboxylase", "substrate": "Lysine"},
                "ODC": {"type": "enzyme", "name": "Ornithine decarboxylase", "substrate": "Ornithine"},
                "CIT": {"type": "chemical", "name": "Citrate", "chebi": "CHEBI:30769"},
                "H2S": {"type": "phenotypic", "name": "Hydrogen sulfide production"},
                "URE": {"type": "enzyme", "name": "Urease", "substrate": "Urea"},
                "TDA": {"type": "enzyme", "name": "Tryptophan deaminase", "substrate": "Tryptophan"},
                "IND": {"type": "phenotypic", "name": "Indole production"},
                "VP": {"type": "phenotypic", "name": "Voges-Proskauer (acetoin)"},
                "GEL": {"type": "enzyme", "name": "Gelatinase", "substrate": "Gelatin"},
                "GLU": {"type": "chemical", "name": "D-Glucose", "chebi": "CHEBI:17234"},
                "MAN": {"type": "chemical", "name": "D-Mannose", "chebi": "CHEBI:4208"},
                "INO": {"type": "chemical", "name": "myo-Inositol", "chebi": "CHEBI:17268"},
                "SOR": {"type": "chemical", "name": "D-Sorbitol", "chebi": "CHEBI:17924"},
                "RHA": {"type": "chemical", "name": "L-Rhamnose", "chebi": "CHEBI:27907"},
                "SAC": {"type": "chemical", "name": "Sucrose", "chebi": "CHEBI:17992"},
                "MEL": {"type": "chemical", "name": "Melibiose", "chebi": "CHEBI:28117"},
                "AMY": {"type": "chemical", "name": "Amygdalin", "chebi": "CHEBI:17019"},
                "ARA": {"type": "chemical", "name": "L-Arabinose", "chebi": "CHEBI:17553"},
            }
        },
        "API 20NE": {
            "name": "API 20NE - Non-Enterobacteriaceae Identification",
            "wells": 20,
            "source": "bioMérieux Package Insert REF 20 050",
            "url": "https://faculty.fiu.edu/~makemson/MCB3020Lab/API20neInstructions.pdf",
            "mappings": {
                "NO3": {"type": "phenotypic", "name": "Nitrate reduction"},
                "TRP": {"type": "phenotypic", "name": "Tryptophane"},
                "GLU": {"type": "chemical", "name": "D-Glucose", "chebi": "CHEBI:17234"},
                "ADH": {"type": "enzyme", "name": "Arginine dihydrolase"},
                "URE": {"type": "enzyme", "name": "Urease"},
                "ESC": {"type": "chemical", "name": "Esculin", "chebi": "CHEBI:4853"},
                "GEL": {"type": "enzyme", "name": "Gelatinase"},
                "PNG": {"type": "enzyme", "name": "β-galactosidase (PNPG)"},
                "GLU": {"type": "chemical", "name": "D-Glucose", "chebi": "CHEBI:17234"},
                "ARA": {"type": "chemical", "name": "L-Arabinose", "chebi": "CHEBI:17553"},
                "MNE": {"type": "chemical", "name": "D-Mannose", "chebi": "CHEBI:4208"},
                "MAN": {"type": "chemical", "name": "D-Mannitol", "chebi": "CHEBI:16899"},
                "NAG": {"type": "chemical", "name": "N-Acetyl-Glucosamine", "chebi": "CHEBI:28009"},
                "MAL": {"type": "chemical", "name": "Maltose", "chebi": "CHEBI:17306"},
                "GNT": {"type": "chemical", "name": "Gluconate", "chebi": "CHEBI:24366"},
                "CAP": {"type": "chemical", "name": "Caprate", "chebi": "CHEBI:30813"},
                "ADI": {"type": "chemical", "name": "Adipate"},
                "MLT": {"type": "chemical", "name": "Malate", "chebi": "CHEBI:30797"},
                "CIT": {"type": "chemical", "name": "Citrate", "chebi": "CHEBI:30769"},
                "PAC": {"type": "chemical", "name": "Phenyl-acetate"},
            }
        },
        "API 50CHac": {
            "name": "API 50CHac - Carbohydrate Acidification (50 sugars)",
            "wells": 50,
            "source": "bioMérieux documentation",
            "note": "Tests acidification (fermentation) of 50 carbohydrates",
            "common_codes": {
                "GLU": {"type": "chemical", "name": "D-Glucose", "chebi": "CHEBI:17234"},
                "FRU": {"type": "chemical", "name": "D-Fructose", "chebi": "CHEBI:15824"},
                "GAL": {"type": "chemical", "name": "D-Galactose", "chebi": "CHEBI:28061"},
                "SAC": {"type": "chemical", "name": "Sucrose", "chebi": "CHEBI:17992"},
                "MAL": {"type": "chemical", "name": "Maltose", "chebi": "CHEBI:17306"},
                "LAC": {"type": "chemical", "name": "Lactose", "chebi": "CHEBI:17716"},
                "TRE": {"type": "chemical", "name": "Trehalose", "chebi": "CHEBI:16551"},
                "RAF": {"type": "chemical", "name": "Raffinose", "chebi": "CHEBI:16634"},
            }
        },
        "API zym": {
            "name": "API zym - Enzyme Activity Profile (19 enzymes)",
            "wells": 20,  # 19 enzyme tests + 1 control
            "source": "bioMérieux Package Insert",
            "note": "Chromogenic enzyme activity detection",
            "url": "https://www.biomerieux.com/",
            "mappings": {
                "Control": {"type": "control", "name": "Negative control"},
                "Alkaline phosphatase": {"type": "enzyme", "name": "Alkaline phosphatase", "ec": "3.1.3.1"},
                "Esterase (C4)": {"type": "enzyme", "name": "Esterase (C4)", "ec": "3.1.1.-"},
                "Esterase lipase (C8)": {"type": "enzyme", "name": "Esterase lipase (C8)", "ec": "3.1.1.-"},
                "Lipase (C14)": {"type": "enzyme", "name": "Lipase (C14)", "ec": "3.1.1.3"},
                "Leucine arylamidase": {"type": "enzyme", "name": "Leucine arylamidase", "ec": "3.4.11.1"},
                "Valine arylamidase": {"type": "enzyme", "name": "Valine arylamidase", "ec": "3.4.11.-"},
                "Cystine arylamidase": {"type": "enzyme", "name": "Cystine arylamidase", "ec": "3.4.11.-"},
                "Trypsin": {"type": "enzyme", "name": "Trypsin", "ec": "3.4.21.4"},
                "alpha-Chymotrypsin": {"type": "enzyme", "name": "alpha-Chymotrypsin", "ec": "3.4.21.1"},
                "Acid phosphatase": {"type": "enzyme", "name": "Acid phosphatase", "ec": "3.1.3.2"},
                "Naphthol-AS-BI-phosphohydrolase": {"type": "enzyme", "name": "Naphthol-AS-BI-phosphohydrolase", "ec": "3.1.3.-"},
                "alpha-Galactosidase": {"type": "enzyme", "name": "alpha-Galactosidase", "ec": "3.2.1.22"},
                "beta-Galactosidase": {"type": "enzyme", "name": "beta-Galactosidase", "ec": "3.2.1.23"},
                "beta-Glucuronidase": {"type": "enzyme", "name": "beta-Glucuronidase", "ec": "3.2.1.31"},
                "alpha-Glucosidase": {"type": "enzyme", "name": "alpha-Glucosidase", "ec": "3.2.1.20"},
                "beta-Glucosidase": {"type": "enzyme", "name": "beta-Glucosidase", "ec": "3.2.1.21"},
                "N-acetyl-beta-glucosaminidase": {"type": "enzyme", "name": "N-acetyl-beta-glucosaminidase", "ec": "3.2.1.52"},
                "alpha-Mannosidase": {"type": "enzyme", "name": "alpha-Mannosidase", "ec": "3.2.1.24"},
                "alpha-Fucosidase": {"type": "enzyme", "name": "alpha-Fucosidase", "ec": "3.2.1.51"},
            }
        },
    }

    def __init__(self):
        """Initialize validator."""
        self.mapper = ChemicalMapper()
        self.validation_results = defaultdict(list)
        self.errors = []
        self.warnings = []

    def validate_kit(self, kit_name: str) -> dict[str, Any]:
        """Validate mappings for a specific API kit.

        Args:
            kit_name: Name of the API kit (e.g., "API 20E")

        Returns:
            Dictionary with validation results
        """
        if kit_name not in self.OFFICIAL_MAPPINGS:
            self.warnings.append(f"No official mapping available for {kit_name}")
            return {"status": "no_reference", "message": f"No official documentation for {kit_name}"}

        official = self.OFFICIAL_MAPPINGS[kit_name]
        results = {
            "kit_name": kit_name,
            "official_wells": official.get("wells", 0),
            "source": official.get("source", "Unknown"),
            "url": official.get("url", ""),
            "validated": [],
            "missing": [],
            "mismatched": [],
        }

        # Check each official mapping
        for well_code, official_data in official.get("mappings", {}).items():
            # Check substrate mappings with kit-specific context
            our_mapping = None
            mapping_location = None
            our_name = None

            # First try kit-specific mapping
            our_mapping = self.mapper.get_substrate_mapping(well_code, kit_name)
            if our_mapping:
                mapping_location = f"KIT_SPECIFIC[{kit_name}]" if (
                    kit_name in self.mapper.KIT_SPECIFIC_MAPPINGS and
                    well_code in self.mapper.KIT_SPECIFIC_MAPPINGS[kit_name]
                ) else "SUBSTRATE_MAPPINGS"
                our_name = our_mapping.get("name", "")
            # Check enzyme tests
            elif well_code in self.mapper.ENZYME_TESTS:
                our_name = self.mapper.ENZYME_TESTS[well_code]
                mapping_location = "ENZYME_TESTS"
            # Check enzyme activity tests
            elif well_code in self.mapper.ENZYME_ACTIVITY_TESTS:
                our_name = self.mapper.ENZYME_ACTIVITY_TESTS[well_code]
                mapping_location = "ENZYME_ACTIVITY_TESTS"
            # Check phenotypic tests
            elif well_code in self.mapper.PHENOTYPIC_TESTS:
                our_name = self.mapper.PHENOTYPIC_TESTS[well_code]
                mapping_location = "PHENOTYPIC_TESTS"

            if our_name:
                # Validate the mapping with lenient string matching
                official_name = official_data.get("name", "").lower()
                our_name_lower = our_name.lower()

                # Normalize for comparison (remove hyphens, spaces, D-/L- prefixes)
                def normalize(s):
                    s = s.replace("-", "").replace(" ", "").replace("d", "").replace("l", "")
                    return s.strip()

                official_norm = normalize(official_name)
                our_norm = normalize(our_name_lower)

                if (official_name in our_name_lower or our_name_lower in official_name or
                    official_norm == our_norm):
                    results["validated"].append({
                        "code": well_code,
                        "official": official_data.get("name"),
                        "ours": our_name,
                        "location": mapping_location,
                        "status": "match"
                    })
                else:
                    results["mismatched"].append({
                        "code": well_code,
                        "official": official_data.get("name"),
                        "ours": our_name,
                        "location": mapping_location,
                        "status": "mismatch"
                    })
                    self.errors.append(
                        f"{kit_name}: {well_code} - Official: '{official_data.get('name')}', "
                        f"Ours: '{our_name}' (in {mapping_location})"
                    )
            else:
                results["missing"].append({
                    "code": well_code,
                    "official": official_data.get("name"),
                    "status": "not_mapped"
                })
                self.warnings.append(
                    f"{kit_name}: {well_code} ({official_data.get('name')}) not in our mappings"
                )

        return results

    def validate_all_kits(self) -> dict[str, Any]:
        """Validate all API kits with official documentation.

        Returns:
            Dictionary with complete validation results
        """
        print("=" * 80)
        print("API KIT MAPPING VALIDATION")
        print("=" * 80)
        print(f"\nValidating against official bioMérieux documentation...\n")

        all_results = {}

        for kit_name in sorted(self.OFFICIAL_MAPPINGS.keys()):
            print(f"Validating {kit_name}...")
            results = self.validate_kit(kit_name)
            all_results[kit_name] = results

            validated = len(results.get("validated", []))
            missing = len(results.get("missing", []))
            mismatched = len(results.get("mismatched", []))
            total = validated + missing + mismatched

            if total > 0:
                accuracy = (validated / total) * 100
                print(f"  ✓ Validated: {validated}/{total} ({accuracy:.1f}%)")
                if missing > 0:
                    print(f"  ⚠ Missing: {missing}")
                if mismatched > 0:
                    print(f"  ✗ Mismatched: {mismatched}")

        return {
            "kits": all_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": self._generate_summary(all_results)
        }

    def _generate_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate validation summary statistics."""
        total_validated = 0
        total_missing = 0
        total_mismatched = 0

        for kit_results in results.values():
            total_validated += len(kit_results.get("validated", []))
            total_missing += len(kit_results.get("missing", []))
            total_mismatched += len(kit_results.get("mismatched", []))

        total = total_validated + total_missing + total_mismatched

        return {
            "total_kits_validated": len(results),
            "total_wells_checked": total,
            "total_validated": total_validated,
            "total_missing": total_missing,
            "total_mismatched": total_mismatched,
            "accuracy_percent": (total_validated / total * 100) if total > 0 else 0,
            "has_errors": len(self.errors) > 0,
            "has_warnings": len(self.warnings) > 0,
        }

    def generate_report(self, output_path: Path):
        """Generate comprehensive validation report.

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
        print(f"Kits validated: {summary['total_kits_validated']}")
        print(f"Wells checked: {summary['total_wells_checked']}")
        print(f"Validated: {summary['total_validated']} ({summary['accuracy_percent']:.1f}%)")
        print(f"Missing: {summary['total_missing']}")
        print(f"Mismatched: {summary['total_mismatched']}")

        if summary['has_errors']:
            print(f"\n❌ Found {len(results['errors'])} errors")
        if summary['has_warnings']:
            print(f"⚠️  Found {len(results['warnings'])} warnings")

        if not summary['has_errors']:
            print("\n✅ All validated mappings are accurate!")

        print("=" * 80)


def main():
    """Run API kit validation."""
    validator = APIKitValidator()

    # Generate validation report
    output_path = Path("api_kit_validation_report.json")
    validator.generate_report(output_path)


if __name__ == "__main__":
    main()
