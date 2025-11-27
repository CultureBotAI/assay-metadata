#!/usr/bin/env python3
"""Check for enzymes without EC numbers in assay_kits_simple.json"""

import json
from pathlib import Path

def check_enzyme_ec_coverage(json_file: str):
    """Check for enzymes without EC numbers in API assay kits."""

    with open(json_file) as f:
        data = json.load(f)

    enzymes_without_ec = []
    total_enzyme_wells = 0

    for kit in data.get('api_kits', []):
        kit_name = kit['kit_name']

        for well in kit.get('wells', []):
            well_name = well.get('name', 'Unknown')
            well_types = well.get('type', [])

            # Check if this is an enzyme well
            if 'enzyme' in well_types:
                total_enzyme_wells += 1
                ec_numbers = well.get('ec_number', [])
                enzyme_names = well.get('enzyme_name', [])

                # Check if EC number is missing or empty
                if not ec_numbers or all(not ec for ec in ec_numbers):
                    enzymes_without_ec.append({
                        'kit': kit_name,
                        'well_name': well_name,
                        'enzyme_name': enzyme_names[0] if enzyme_names else 'Unknown',
                        'label': well.get('label', [''])[0] if well.get('label') else '',
                        'go_terms': well.get('go_terms', []),
                    })

    # Print results
    print("=" * 80)
    print("API Assay Enzyme EC Number Coverage Check")
    print("=" * 80)
    print(f"Total enzyme wells: {total_enzyme_wells}")
    print(f"Enzymes WITHOUT EC numbers: {len(enzymes_without_ec)}")
    print(f"Coverage: {(total_enzyme_wells - len(enzymes_without_ec)) / total_enzyme_wells * 100:.1f}%")
    print("=" * 80)

    if enzymes_without_ec:
        print("\nEnzymes missing EC numbers:")
        print("-" * 80)

        # Group by kit
        by_kit = {}
        for enzyme in enzymes_without_ec:
            kit = enzyme['kit']
            if kit not in by_kit:
                by_kit[kit] = []
            by_kit[kit].append(enzyme)

        for kit_name, enzymes in sorted(by_kit.items()):
            print(f"\n{kit_name} ({len(enzymes)} enzymes without EC):")
            for enzyme in enzymes:
                print(f"  - {enzyme['well_name']}")
                print(f"    Label: {enzyme['label']}")
                print(f"    Enzyme: {enzyme['enzyme_name']}")
                if enzyme['go_terms']:
                    print(f"    GO terms: {', '.join(enzyme['go_terms'])}")
    else:
        print("\n✅ All enzyme wells have EC numbers!")

    return enzymes_without_ec, total_enzyme_wells


if __name__ == "__main__":
    json_file = "data/assay_kits_simple.json"
    check_enzyme_ec_coverage(json_file)
