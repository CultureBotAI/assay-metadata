"""Main CLI script for extracting API assay metadata from BacDive data."""

import argparse
import json
from pathlib import Path
import sys

from .metadata_builder import MetadataBuilder


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Extract API assay metadata from BacDive JSON data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract metadata from default location
  extract-metadata

  # Specify custom input file
  extract-metadata --input path/to/bacdive_strains.json

  # Specify custom output directory
  extract-metadata --output-dir processed_data/

  # Generate both consolidated and individual kit files
  extract-metadata --split-kits
        """
    )

    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path("bacdive_strains.json"),
        help="Path to BacDive JSON input file (default: bacdive_strains.json)",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("data"),
        help="Output directory for metadata files (default: data/)",
    )

    parser.add_argument(
        "--split-kits",
        action="store_true",
        help="Generate individual JSON files for each API kit",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (indented)",
    )

    parser.add_argument(
        "--simple",
        action="store_true",
        help="Generate simplified output with wells nested in kits",
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Build metadata
    try:
        builder = MetadataBuilder(args.input)
        metadata = builder.build()
    except Exception as e:
        print(f"Error building metadata: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Determine JSON formatting
    json_kwargs = {"indent": 2} if args.pretty else {}

    # Write consolidated metadata file
    output_path = args.output_dir / "assay_metadata.json"
    print(f"\nWriting consolidated metadata to {output_path}...")

    with open(output_path, "w", encoding="utf-8") as f:
        # Convert to dict for JSON serialization
        metadata_dict = metadata.model_dump(exclude_none=True)
        json.dump(metadata_dict, f, **json_kwargs)

    print(f"✓ Wrote {output_path}")

    # Write API kits summary
    kits_path = args.output_dir / "api_kits_list.json"
    print(f"Writing API kits summary to {kits_path}...")

    kits_data = {
        "total_kits": len(metadata.api_kits),
        "kits": [kit.model_dump(exclude_none=True) for kit in metadata.api_kits],
    }

    with open(kits_path, "w", encoding="utf-8") as f:
        json.dump(kits_data, f, **json_kwargs)

    print(f"✓ Wrote {kits_path}")

    # Optionally write individual kit files
    if args.split_kits:
        kits_dir = args.output_dir / "kits"
        kits_dir.mkdir(exist_ok=True)
        print(f"\nWriting individual kit files to {kits_dir}/...")

        for kit in metadata.api_kits:
            # Create safe filename
            safe_name = kit.kit_name.replace(" ", "_").replace("/", "-")
            kit_path = kits_dir / f"{safe_name}.json"

            # Get wells for this kit
            kit_wells = {
                code: metadata.wells[code].model_dump(exclude_none=True)
                for code in kit.wells
                if code in metadata.wells
            }

            kit_data = {
                "kit": kit.model_dump(exclude_none=True),
                "wells": kit_wells,
            }

            with open(kit_path, "w", encoding="utf-8") as f:
                json.dump(kit_data, f, **json_kwargs)

            print(f"  ✓ {kit_path}")

    # Write statistics summary
    stats_path = args.output_dir / "statistics.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(metadata.statistics, f, indent=2)

    print(f"\n✓ Wrote statistics to {stats_path}")

    # Write simplified output if requested
    if args.simple:
        simple_path = args.output_dir / "assay_kits_simple.json"
        print(f"\nWriting simplified output to {simple_path}...")

        # Build simplified structure with wells nested in kits
        # ALL VALUES AS LISTS (scalars become single-element lists)
        simple_data = {
            "api_kits": []
        }

        for kit in metadata.api_kits:
            kit_data = {
                "kit_name": kit.kit_name,
                "description": kit.description,
                "category": kit.category,
                "well_count": kit.well_count,
                "occurrence_count": kit.occurrence_count,
                "wells": []
            }

            # Add well details for each well in this kit
            for well_code in kit.wells:
                if well_code in metadata.wells:
                    well = metadata.wells[well_code]

                    # Flatten all features into lists
                    well_entry = {
                        "name": well_code,  # Well code
                        "label": [well.label] if well.label else [],
                        "type": [well.well_type] if well.well_type else [],
                        "description": [well.description] if well.description else [],
                    }

                    # Add chemical identifiers as flat lists
                    if well.chemical_ids:
                        chem = well.chemical_ids
                        well_entry["chebi_id"] = [chem.chebi_id] if chem.chebi_id else []
                        well_entry["chebi_name"] = [chem.chebi_name] if chem.chebi_name else []
                        well_entry["pubchem_cid"] = [chem.pubchem_cid] if chem.pubchem_cid else []
                        well_entry["pubchem_name"] = [chem.pubchem_name] if chem.pubchem_name else []
                        well_entry["inchi"] = [chem.inchi] if chem.inchi else []
                        well_entry["smiles"] = [chem.smiles] if chem.smiles else []
                    else:
                        well_entry["chebi_id"] = []
                        well_entry["chebi_name"] = []
                        well_entry["pubchem_cid"] = []
                        well_entry["pubchem_name"] = []
                        well_entry["inchi"] = []
                        well_entry["smiles"] = []

                    # Add enzyme identifiers as flat lists
                    if well.enzyme_ids:
                        enz = well.enzyme_ids
                        well_entry["enzyme_name"] = [enz.enzyme_name] if enz.enzyme_name else []
                        well_entry["ec_number"] = [enz.ec_number] if enz.ec_number else []
                        well_entry["ec_name"] = [enz.ec_name] if enz.ec_name else []
                        well_entry["go_terms"] = enz.go_terms if enz.go_terms else []
                        well_entry["go_names"] = enz.go_names if enz.go_names else []
                        well_entry["kegg_ko"] = [enz.kegg_ko] if enz.kegg_ko else []
                        well_entry["kegg_reaction"] = [enz.kegg_reaction] if enz.kegg_reaction else []
                        well_entry["rhea_ids"] = enz.rhea_ids if enz.rhea_ids else []
                        well_entry["metacyc_reaction"] = [enz.metacyc_reaction] if enz.metacyc_reaction else []
                        well_entry["metacyc_pathway"] = enz.metacyc_pathway if enz.metacyc_pathway else []
                    else:
                        well_entry["enzyme_name"] = []
                        well_entry["ec_number"] = []
                        well_entry["ec_name"] = []
                        well_entry["go_terms"] = []
                        well_entry["go_names"] = []
                        well_entry["kegg_ko"] = []
                        well_entry["kegg_reaction"] = []
                        well_entry["rhea_ids"] = []
                        well_entry["metacyc_reaction"] = []
                        well_entry["metacyc_pathway"] = []

                    kit_data["wells"].append(well_entry)

            simple_data["api_kits"].append(kit_data)

        with open(simple_path, "w", encoding="utf-8") as f:
            json.dump(simple_data, f, **json_kwargs)

        print(f"✓ Wrote {simple_path}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Input file: {args.input}")
    print(f"Output directory: {args.output_dir}")
    print(f"API kits found: {metadata.statistics['total_api_kits']}")
    print(f"Unique wells: {metadata.statistics['total_unique_wells']}")
    print(f"Unique enzymes: {metadata.statistics['total_unique_enzymes']}")
    print(f"Total strains processed: {metadata.statistics['total_strains']:,}")
    print("=" * 70)

    print("\nMetadata extraction complete! 🎉")


if __name__ == "__main__":
    main()
