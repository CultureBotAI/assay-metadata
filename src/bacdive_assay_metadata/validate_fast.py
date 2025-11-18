"""Fast validation using only ontology files (no API calls)."""

import sys
from pathlib import Path

from .validate_mappings import MappingValidator, track_ontology_files
from .mappers import ChemicalMapper, EnzymeMapper


def main():
    """Fast validation entry point."""
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

    print("\n" + "=" * 70)
    print("FAST VALIDATION (Ontology files only, no API calls)")
    print("=" * 70)

    # Validate CHEBI IDs from substrates
    print("\nValidating CHEBI IDs...")
    for well_code, mapping in ChemicalMapper.SUBSTRATE_MAPPINGS.items():
        if "chebi" in mapping and mapping["chebi"]:
            validator.validate_chebi(mapping["chebi"])
            validator.stats["substrates_total"] += 1

    # Validate EC numbers and GO terms from enzymes
    print("Validating EC numbers and GO terms...")
    mapper = EnzymeMapper()
    for enzyme_name, annotation in mapper.ENZYME_ANNOTATIONS.items():
        validator.stats["enzymes_total"] += 1

        # Validate EC
        if annotation.get("ec_number"):
            validator.validate_ec(annotation["ec_number"])

        # Validate GO terms
        for go_term in annotation.get("go_terms", []):
            validator.validate_go(go_term)

    # Print report
    success = validator.print_report()

    # Save report
    report_path = Path("validation_report.json")
    validator.save_report(report_path)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
