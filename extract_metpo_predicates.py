#!/usr/bin/env python3
"""Extract METPO predicates from OWL file for assay result mapping."""

import re
import xml.etree.ElementTree as ET
from collections import defaultdict

def extract_metpo_predicates(owl_file):
    """Extract METPO predicates with IDs and labels."""

    tree = ET.parse(owl_file)
    root = tree.getroot()

    # Define namespaces
    namespaces = {
        'owl': 'http://www.w3.org/2002/07/owl#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'obo': 'http://purl.obolibrary.org/obo/',
    }

    predicates = {}

    # Find all ObjectProperty elements
    for obj_prop in root.findall('.//owl:ObjectProperty', namespaces):
        about = obj_prop.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
        if not about or 'metpo' not in about.lower():
            continue

        # Extract ID from URL
        metpo_id = about.split('/')[-1]

        # Get label
        label_elem = obj_prop.find('rdfs:label', namespaces)
        if label_elem is not None:
            label = label_elem.text
            predicates[label] = {
                'id': metpo_id,
                'url': about,
                'label': label
            }

    return predicates


def main():
    owl_file = 'metpo.owl'
    predicates = extract_metpo_predicates(owl_file)

    # Keywords of interest for API assays
    keywords = [
        'ferment', 'produce', 'reduce', 'oxidize', 'hydrolyze',
        'assimilate', 'accumulate', 'utilize', 'grow',
        'has', 'lack', 'positive', 'negative', 'enzyme'
    ]

    print("=" * 80)
    print("METPO PREDICATES FOR API ASSAYS")
    print("=" * 80)
    print()

    # Group by category
    categories = defaultdict(list)

    for label, info in sorted(predicates.items()):
        label_lower = label.lower()

        # Categorize
        if any(k in label_lower for k in ['ferment']):
            categories['Fermentation'].append(info)
        elif any(k in label_lower for k in ['produce', 'production']):
            categories['Production'].append(info)
        elif any(k in label_lower for k in ['reduce', 'reduction']):
            categories['Reduction'].append(info)
        elif any(k in label_lower for k in ['oxidize', 'oxidation']):
            categories['Oxidation'].append(info)
        elif any(k in label_lower for k in ['hydrolyze', 'hydrolysis']):
            categories['Hydrolysis'].append(info)
        elif any(k in label_lower for k in ['assimilate', 'assimilation']):
            categories['Assimilation'].append(info)
        elif any(k in label_lower for k in ['accumulate']):
            categories['Accumulation'].append(info)
        elif any(k in label_lower for k in ['utilize', 'utilization']):
            categories['Utilization'].append(info)
        elif any(k in label_lower for k in ['grow', 'growth']):
            categories['Growth'].append(info)
        elif any(k in label_lower for k in ['enzyme', 'activity']):
            categories['Enzyme Activity'].append(info)
        elif any(k in label_lower for k in ['positive', 'negative', 'has', 'lack', 'does not']):
            categories['General'].append(info)

    # Print categorized
    for category, preds in sorted(categories.items()):
        if preds:
            print(f"\n{category}:")
            print("-" * 80)
            for pred in preds:
                print(f"  {pred['label']:<50} METPO:{pred['id']}")

    # Print all relevant predicates
    print("\n" + "=" * 80)
    print("ALL RELEVANT PREDICATES (sorted)")
    print("=" * 80)

    relevant = []
    for label, info in predicates.items():
        if any(k in label.lower() for k in keywords):
            relevant.append(info)

    for pred in sorted(relevant, key=lambda x: x['label']):
        print(f"{pred['label']:<50} METPO:{pred['id']}")

    print(f"\nTotal relevant predicates: {len(relevant)}")
    print(f"Total all predicates: {len(predicates)}")


if __name__ == "__main__":
    main()
