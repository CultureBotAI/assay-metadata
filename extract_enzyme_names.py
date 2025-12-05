#!/usr/bin/env python3
"""Extract all unique enzyme names from BacDive assay metadata sources."""

import sys
sys.path.insert(0, 'src')

from bacdive_assay_metadata.mappers import ChemicalMapper
from bacdive_assay_metadata.parser import BacDiveParser
import json


def extract_enzyme_names():
    """Extract all unique enzyme names from various sources."""
    print("=" * 70)
    print("Extracting Unique Enzyme Names")
    print("=" * 70)

    all_enzyme_names = set()

    # Source 1: ENZYME_TESTS dictionary
    print("\n1. Extracting from ENZYME_TESTS...")
    mapper = ChemicalMapper()
    for well_code, enzyme_name in mapper.ENZYME_TESTS.items():
        all_enzyme_names.add(enzyme_name)
    print(f"   Found {len(mapper.ENZYME_TESTS)} enzyme tests")

    # Source 2: ENZYME_ACTIVITY_TESTS dictionary
    print("\n2. Extracting from ENZYME_ACTIVITY_TESTS...")
    for well_code, enzyme_name in mapper.ENZYME_ACTIVITY_TESTS.items():
        all_enzyme_names.add(enzyme_name)
    print(f"   Found {len(mapper.ENZYME_ACTIVITY_TESTS)} enzyme activity tests")

    # Source 3: PHENOTYPIC_TESTS dictionary (now classified as enzyme)
    print("\n3. Extracting from PHENOTYPIC_TESTS (now enzyme type)...")
    for well_code, test_name in mapper.PHENOTYPIC_TESTS.items():
        all_enzyme_names.add(test_name)
    print(f"   Found {len(mapper.PHENOTYPIC_TESTS)} phenotypic tests")

    # Source 4: Parse BacDive data to find actual enzyme names
    print("\n4. Parsing BacDive data...")
    try:
        parser = BacDiveParser("bacdive_strains.json")
        parsed_data = parser.parse()

        for enzyme_name in parsed_data.get("enzymes", {}).keys():
            all_enzyme_names.add(enzyme_name)

        print(f"   Found {len(parsed_data.get('enzymes', {}))} enzymes from BacDive data")
    except Exception as e:
        print(f"   Warning: Could not parse BacDive data: {e}")

    # Sort and display all unique names
    sorted_names = sorted(all_enzyme_names)

    print("\n" + "=" * 70)
    print(f"Total Unique Enzyme Names: {len(sorted_names)}")
    print("=" * 70)

    # Save to file
    with open("unique_enzyme_names.txt", "w") as f:
        for name in sorted_names:
            f.write(f"{name}\n")

    print(f"\nSaved to unique_enzyme_names.txt")

    # Display categorization
    print("\n" + "=" * 70)
    print("Name Categories")
    print("=" * 70)

    categories = {
        'With substrate info (parentheses)': [],
        'Activity measurements': [],
        'Generic names': [],
        'Specific enzyme names': [],
    }

    for name in sorted_names:
        if '(' in name and ')' in name:
            categories['With substrate info (parentheses)'].append(name)
        elif 'activity' in name.lower() or 'test' in name.lower():
            categories['Activity measurements'].append(name)
        elif name.lower() in ['control well (no substrate)', 'control']:
            categories['Generic names'].append(name)
        else:
            categories['Specific enzyme names'].append(name)

    for category, names in categories.items():
        if names:
            print(f"\n{category}: {len(names)}")
            for name in names[:5]:  # Show first 5
                print(f"  - {name}")
            if len(names) > 5:
                print(f"  ... and {len(names) - 5} more")

    return sorted_names


if __name__ == "__main__":
    extract_enzyme_names()
