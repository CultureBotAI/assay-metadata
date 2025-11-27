#!/usr/bin/env python3
"""Check for complete enzyme coverage (EC OR GO) in assay_kits_simple.json"""

import json
from pathlib import Path

def check_enzyme_complete_coverage(json_file: str):
    """Check for enzymes with neither EC numbers nor GO terms."""

    with open(json_file) as f:
        data = json.load(f)

    enzymes_without_any_id = []
    enzymes_with_ec = []
    enzymes_with_go_only = []
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
                go_terms = well.get('go_terms', [])
                enzyme_names = well.get('enzyme_name', [])

                has_ec = ec_numbers and any(ec for ec in ec_numbers)
                has_go = go_terms and any(go for go in go_terms)

                enzyme_info = {
                    'kit': kit_name,
                    'well_name': well_name,
                    'enzyme_name': enzyme_names[0] if enzyme_names else 'Unknown',
                    'label': well.get('label', [''])[0] if well.get('label') else '',
                    'ec_numbers': ec_numbers,
                    'go_terms': go_terms,
                }

                if has_ec:
                    enzymes_with_ec.append(enzyme_info)
                elif has_go:
                    enzymes_with_go_only.append(enzyme_info)
                else:
                    # Neither EC nor GO
                    enzymes_without_any_id.append(enzyme_info)

    # Print results
    print("=" * 80)
    print("API Assay Enzyme Complete Coverage Check (EC OR GO)")
    print("=" * 80)
    print(f"Total enzyme wells: {total_enzyme_wells}")
    print(f"Enzymes with EC numbers: {len(enzymes_with_ec)} ({len(enzymes_with_ec)/total_enzyme_wells*100:.1f}%)")
    print(f"Enzymes with GO terms only (no EC): {len(enzymes_with_go_only)} ({len(enzymes_with_go_only)/total_enzyme_wells*100:.1f}%)")
    print(f"Enzymes with NEITHER EC nor GO: {len(enzymes_without_any_id)} ({len(enzymes_without_any_id)/total_enzyme_wells*100:.1f}%)")
    print()
    print(f"TOTAL COVERAGE (EC or GO): {len(enzymes_with_ec) + len(enzymes_with_go_only)}/{total_enzyme_wells} " +
          f"({(len(enzymes_with_ec) + len(enzymes_with_go_only))/total_enzyme_wells*100:.1f}%)")
    print("=" * 80)

    if enzymes_with_go_only:
        print("\n📊 Enzymes with GO terms only (no EC):")
        print("-" * 80)
        by_kit = {}
        for enzyme in enzymes_with_go_only:
            kit = enzyme['kit']
            if kit not in by_kit:
                by_kit[kit] = []
            by_kit[kit].append(enzyme)

        for kit_name, enzymes in sorted(by_kit.items()):
            print(f"\n{kit_name} ({len(enzymes)} enzymes):")
            for enzyme in enzymes:
                print(f"  - {enzyme['well_name']}: {enzyme['label']}")
                print(f"    GO terms: {', '.join(enzyme['go_terms'])}")

    if enzymes_without_any_id:
        print("\n\n❌ Enzymes with NEITHER EC nor GO:")
        print("-" * 80)
        by_kit = {}
        for enzyme in enzymes_without_any_id:
            kit = enzyme['kit']
            if kit not in by_kit:
                by_kit[kit] = []
            by_kit[kit].append(enzyme)

        for kit_name, enzymes in sorted(by_kit.items()):
            print(f"\n{kit_name} ({len(enzymes)} enzymes):")
            for enzyme in enzymes:
                print(f"  - {enzyme['well_name']}")
                print(f"    Label: {enzyme['label']}")
                print(f"    Enzyme: {enzyme['enzyme_name']}")
    else:
        print("\n\n✅ ALL enzyme wells have either EC numbers or GO terms!")

    return {
        'total': total_enzyme_wells,
        'with_ec': len(enzymes_with_ec),
        'with_go_only': len(enzymes_with_go_only),
        'without_any': len(enzymes_without_any_id),
        'coverage_percent': (len(enzymes_with_ec) + len(enzymes_with_go_only))/total_enzyme_wells*100
    }


if __name__ == "__main__":
    json_file = "data/assay_kits_simple.json"
    results = check_enzyme_complete_coverage(json_file)
