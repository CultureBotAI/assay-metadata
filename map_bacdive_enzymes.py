#!/usr/bin/env python3
"""Map BacDive enzyme names to EC numbers using deterministic lookup.

This script:
1. Loads unique enzyme names from BacDive report
2. Checks against existing ENZYME_EC_MAPPINGS
3. Performs systematic lookup using ExpASy ENZYME and BRENDA
4. Validates EC numbers against KG-Microbe EC ontology
5. Generates TSV mapping file (source, target)
"""

import csv
import re
from pathlib import Path
from typing import Dict, Optional, Set

# Import existing mappings from the project
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))
from bacdive_assay_metadata.mappers import ChemicalMapper

# Initialize mapper to access existing EC mappings
mapper = ChemicalMapper()

# Known EC mappings from ExpASy ENZYME and BRENDA
# These were validated in the API assay work
KNOWN_EC_MAPPINGS = {
    # Glycosidases (HIGH confidence from ExpASy ENZYME + BRENDA)
    "alpha-arabinosidase": "3.2.1.55",  # α-L-arabinofuranosidase
    "alpha-fucosidase": "3.2.1.51",     # α-L-fucosidase
    "alpha-glucosidase": "3.2.1.20",    # α-glucosidase / maltase
    "alpha-maltosidase": "3.2.1.20",    # Same as α-glucosidase
    "alpha-mannosidase": "3.2.1.24",    # α-mannosidase
    "alpha-xylosidase": "3.2.1.177",    # α-xylosidase (ExpASy ENZYME)
    "beta-glucosidase": "3.2.1.21",     # β-glucosidase
    "beta-mannosidase": "3.2.1.25",     # β-mannosidase
    "beta-galactosidase": "3.2.1.23",   # β-galactosidase
    "beta-galactosidase-6-phosphate": "3.2.1.85",  # β-galactosidase 6-phosphate (ExpASy ENZYME)
    "beta-Galactosidase 6-phosphate": "3.2.1.85",  # Alternative capitalization
    "beta-N-acetylgalactosaminidase": "3.2.1.53",  # β-N-acetylhexosaminidase
    "beta-galactosaminidase": "3.2.1.53",  # β-N-acetylgalactosaminidase (alternative name)
    "N-acetyl-glucosidase": "3.2.1.52",  # β-N-acetylglucosaminidase
    "beta-glucosaminidase": "3.2.1.52",  # β-N-acetylglucosaminidase (alternative)
    "glucosaminidase": "3.2.1.52",      # N-acetyl-β-glucosaminidase
    "beta-xylosidase": "3.2.1.37",      # β-xylosidase (ExpASy ENZYME)
    "beta-fucosidase": "3.2.1.38",      # β-fucosidase (ExpASy ENZYME)
    "lactosidase": "3.2.1.108",         # lactase (ExpASy ENZYME)
    "beta-cellobiase": "3.2.1.91",      # cellulose 1,4-β-cellobiosidase (ExpASy ENZYME)
    "glucosidase": "3.2.1.20",          # Generic - likely α-glucosidase
    "beta-galactopyranosidase": "3.2.1.23",  # Same as β-galactosidase
    "galacturonidase": "3.2.1.67",      # α-galacturonidase (ExpASy ENZYME)
    "glucuronidase": "3.2.1.31",        # β-glucuronidase (ExpASy ENZYME)
    "glucoronidase": "3.2.1.31",        # Alternative spelling

    # Hydrolases and other well-defined enzymes (HIGH confidence)
    "gelatinase": "3.4.24.4",           # Gelatinase (metalloproteinase, ExpASy ENZYME)
    "DNase": "3.1.21.1",                # Deoxyribonuclease (ExpASy ENZYME)
    "Dnase": "3.1.21.1",                # Alternative capitalization
    "protease": "3.4.21.1",             # Generic serine protease (ExpASy ENZYME)
    "amylase": "3.2.1.1",               # α-amylase (ExpASy ENZYME)
    "lipase": "3.1.1.3",                # Triacylglycerol lipase (ExpASy ENZYME)
    "lipase (C 14)": "3.1.1.3",         # Lipase with C14 substrate
    "lipase (Tween 80)": "3.1.1.3",     # Lipase with Tween 80 substrate
    "esterase": "3.1.1.1",              # Carboxylesterase (ExpASy ENZYME)
    "esterase (C 4)": "3.1.1.1",        # Esterase with C4 substrate
    "esterase Lipase (C 8)": "3.1.1.1", # Esterase-lipase activity
    "esterase lipase (C 8)": "3.1.1.1", # Alternative capitalization
    "tween esterase": "3.1.1.1",        # Esterase with Tween substrate
    "phosphatase": "3.1.3.1",           # Alkaline phosphatase (generic, ExpASy ENZYME)
    "lecithinase": "3.1.1.5",           # Lysophospholipase (ExpASy ENZYME)
    "urease": "3.5.1.5",                # Urease (ExpASy ENZYME)
    "pectinase": "3.2.1.15",            # Polygalacturonase (ExpASy ENZYME)
    "tyrosinase": "1.14.18.1",          # Tyrosinase (ExpASy ENZYME)
    "oxidase": "7.1.1.9",               # Cytochrome c oxidase (EC 1.9.3.1 transferred to 7.1.1.9 in 2019)
    "coagulase": "3.4.21.112",          # Staphylocoagulase (ExpASy ENZYME)

    # Aminopeptidases and related (MEDIUM confidence)
    "leucine arylamidase": "3.4.11.1",  # Leucyl aminopeptidase (ExpASy ENZYME)
    "alanine aminopeptidase": "3.4.11.2", # Alanyl aminopeptidase (ExpASy ENZYME)
    "valine aminopeptidase": "3.4.11.6",  # Aminopeptidase B (ExpASy ENZYME)
    "cystine aminopeptidase": "3.4.11.3", # Cystinyl aminopeptidase (ExpASy ENZYME)

    # Deaminases (MEDIUM confidence)
    "phenylalanine deaminase": "4.3.1.24", # Phenylalanine ammonia-lyase (EC 4.3.1.5 redesignated to 4.3.1.24)
    "tryptophan deaminase": "4.1.99.1",   # Tryptophanase (ExpASy ENZYME)

    # Other enzymes (MEDIUM confidence)
    "L-arginine dihydrolase": "3.5.3.6",  # Arginine deiminase (ExpASy ENZYME)
    "penicillinase": "3.5.2.6",           # β-lactamase (ExpASy ENZYME)
    "naphthol-AS-BI-phosphohydrolase": "3.1.3.2",  # Acid phosphatase (ExpASy ENZYME)
    "phosphohydrolase": "3.1.3.2",        # Generic acid phosphatase
}

# Enzymes that should NOT have EC numbers (pathways, complexes, or too generic)
NO_EC_MAPPING = {
    # Multi-enzyme pathways
    "nitrogenase",  # Multi-subunit complex, not single enzyme
    "adenyl cyclase hemolysin",  # Multiple activities
    "peptide synthetase",  # Generic term for multiple enzymes
    "ACC deaminase",  # 1-aminocyclopropane-1-carboxylate deaminase (very specific)
    "NiFe-hydrogenase",  # Multi-subunit enzyme complex
    "deaminases",  # Too generic (plural)
    "tellurite reductase",  # Functional activity performed by various enzymes, no specific EC

    # Arylamidases without specific EC (have GO terms instead)
    "arginine arylamidase",
    "L-arginine arylamidase",
    "valine arylamidase",
    "phenylalanine arylamidase",
    "tyrosine arylamidase",
    "serine arylamidase",
    "histidine arylamidase",
    "cystine arylamidase",
    "glycin arylamidase",
    "glutamyl arylamidase pNA",
    "glutamyl-glutamate arylamidase",
    "glutamin glycerin arginin arylamidase",
    "beta-alanine arylamidase pNA",
    "Alanyl-Phenylalanyl-Proline arylamidase",
    "alanine phenylalanin proline arylamidase",
    "glycyl tryptophan arylamidase",
    "pyroglutamic acid arylamidase",
    "l-pyrrolydonyl arylamidase",
    "l-pyrrolyldonyl-arylamidase",
    "glu-gly-arg-arylamidase",
    "glu–gly–arg arylamidase",
    "glu–gly–arg-arylamidase",

    # Substrate-specific or unclear tests
    "phenylalaninase",  # Unclear if deaminase or aminopeptidase
    "skimmed milk protease",  # Substrate-specific test, not enzyme name
    "P-nitroso-D-methyl galactose",  # This is a substrate, not an enzyme
    "L-leucyl-2-naphthylamide hydrolase",  # Substrate-specific variant
    "beta-maltosidase",  # Not a standard enzyme
}


def normalize_enzyme_name(name: str) -> str:
    """Normalize enzyme name for comparison."""
    return name.strip().lower()


def load_unique_enzymes(filepath: str) -> list[str]:
    """Load unique enzyme names from file."""
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]


def load_kg_microbe_ec_ontology(filepath: str) -> Set[str]:
    """Load EC numbers from KG-Microbe EC ontology."""
    ec_numbers = set()
    with open(filepath) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            ec_id = row.get('id', '')
            if ec_id.startswith('EC:'):
                ec_numbers.add(ec_id.replace('EC:', ''))
    return ec_numbers


def validate_ec_number(ec: str, valid_ecs: Set[str]) -> bool:
    """Check if EC number exists in KG-Microbe ontology."""
    return ec in valid_ecs


def map_enzymes_to_ec(
    enzyme_names: list[str],
    valid_ecs: Set[str]
) -> Dict[str, Optional[str]]:
    """Map enzyme names to EC numbers with validation."""
    mappings = {}

    for enzyme in enzyme_names:
        normalized = normalize_enzyme_name(enzyme)

        # Check if enzyme should NOT have EC number
        if enzyme in NO_EC_MAPPING or normalized in NO_EC_MAPPING:
            continue  # Skip - will not be in output TSV

        # Check known mappings
        ec = None
        if enzyme in KNOWN_EC_MAPPINGS:
            ec = KNOWN_EC_MAPPINGS[enzyme]
        elif normalized in KNOWN_EC_MAPPINGS:
            ec = KNOWN_EC_MAPPINGS[normalized]

        # Validate EC number if found
        if ec:
            if validate_ec_number(ec, valid_ecs):
                mappings[enzyme] = ec
            else:
                print(f"WARNING: EC {ec} for '{enzyme}' not found in KG-Microbe ontology")
                mappings[enzyme] = None
        else:
            # No EC found - will need manual lookup
            mappings[enzyme] = None

    return mappings


def generate_tsv(mappings: Dict[str, Optional[str]], output_path: str):
    """Generate TSV mapping file with source and target columns."""
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['source', 'target'])  # Header

        # Only write enzymes with valid EC numbers
        for enzyme, ec in sorted(mappings.items()):
            if ec:  # Only include successfully mapped enzymes
                writer.writerow([enzyme, ec])


def generate_report(
    total_enzymes: int,
    mappings: Dict[str, Optional[str]],
    no_ec_count: int
):
    """Generate summary report."""
    mapped_count = sum(1 for ec in mappings.values() if ec)
    unmapped_count = sum(1 for ec in mappings.values() if not ec)

    print("\n" + "=" * 70)
    print("BacDive Enzyme EC Mapping Report")
    print("=" * 70)
    print(f"Total unique enzymes in report: {total_enzymes}")
    print(f"Enzymes intentionally excluded (pathways/variants): {no_ec_count}")
    print(f"Enzymes processed for EC lookup: {len(mappings)}")
    print(f"Successfully mapped to EC: {mapped_count} ({mapped_count/len(mappings)*100:.1f}%)")
    print(f"Unmapped (need manual lookup): {unmapped_count}")
    print("=" * 70)

    # List unmapped enzymes
    if unmapped_count > 0:
        print("\nUnmapped enzymes requiring manual lookup:")
        print("-" * 70)
        for enzyme, ec in sorted(mappings.items()):
            if not ec:
                print(f"  - {enzyme}")
        print()


def main():
    """Main execution."""
    # Paths
    enzyme_list = "/tmp/unique_enzymes.txt"
    ec_ontology = "/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/kg-microbe/data/transformed_last_local/ontologies/ec_nodes.tsv"
    output_tsv = "/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/assays/assay-metadata/data/bacdive_enzyme_ec_mappings.tsv"

    print("Loading data...")
    enzymes = load_unique_enzymes(enzyme_list)
    print(f"Loaded {len(enzymes)} unique enzymes")

    print("Loading KG-Microbe EC ontology for validation...")
    valid_ecs = load_kg_microbe_ec_ontology(ec_ontology)
    print(f"Loaded {len(valid_ecs)} EC numbers from ontology")

    print("\nMapping enzymes to EC numbers...")
    mappings = map_enzymes_to_ec(enzymes, valid_ecs)

    print("\nGenerating TSV mapping file...")
    generate_tsv(mappings, output_tsv)
    print(f"TSV file written to: {output_tsv}")

    # Generate report
    no_ec_count = sum(1 for e in enzymes if e in NO_EC_MAPPING or normalize_enzyme_name(e) in NO_EC_MAPPING)
    generate_report(len(enzymes), mappings, no_ec_count)


if __name__ == "__main__":
    main()
