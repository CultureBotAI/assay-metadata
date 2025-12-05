"""Identifier mapping utilities for chemicals and enzymes."""

import json
import re
import time
from pathlib import Path
from typing import Optional
import requests
from bioregistry import normalize_curie


class ChemicalMapper:
    """Map substrate codes to CHEBI and PubChem identifiers."""

    # Manual mappings for common API assay substrates
    SUBSTRATE_MAPPINGS = {
        # Monosaccharides
        "GLU": {"name": "D-Glucose", "chebi": "CHEBI:17234", "pubchem": "5793"},
        "FRU": {"name": "D-Fructose", "chebi": "CHEBI:15824", "pubchem": "5984"},
        "GAL": {"name": "D-Galactose", "chebi": "CHEBI:28061", "pubchem": "6036"},
        "MAN": {"name": "D-Mannitol", "chebi": "CHEBI:16899", "pubchem": "6251"},  # API 20NE context; other kits use for Mannose
        "MANN": {"name": "D-Mannose", "chebi": "CHEBI:4208", "pubchem": "18950"},  # Explicit mannose code
        "RIB": {"name": "D-Ribose", "chebi": "CHEBI:47013", "pubchem": "5779"},
        "XYL": {"name": "D-Xylose", "chebi": "CHEBI:17140", "pubchem": "135191"},
        "DXYL": {"name": "D-Xylose", "chebi": "CHEBI:17140", "pubchem": "135191"},
        "LXYL": {"name": "L-Xylose", "chebi": "CHEBI:33917", "pubchem": "5289597"},
        "ARA": {"name": "L-Arabinose", "chebi": "CHEBI:17553", "pubchem": "439195"},
        "LARA": {"name": "L-Arabinose", "chebi": "CHEBI:17553", "pubchem": "439195"},
        "DARA": {"name": "D-Arabinose", "chebi": "CHEBI:16731", "pubchem": "439197"},

        # Disaccharides
        "MAL": {"name": "Maltose", "chebi": "CHEBI:17306", "pubchem": "6255"},
        "LAC": {"name": "Lactose", "chebi": "CHEBI:17716", "pubchem": "6134"},
        "SAC": {"name": "Sucrose", "chebi": "CHEBI:17992", "pubchem": "5988"},
        "TRE": {"name": "Trehalose", "chebi": "CHEBI:16551", "pubchem": "7427"},
        "CEL": {"name": "Cellobiose", "chebi": "CHEBI:17057", "pubchem": "10712"},
        "MEL": {"name": "Melibiose", "chebi": "CHEBI:28117", "pubchem": "440658"},

        # Trisaccharides
        "RAF": {"name": "Raffinose", "chebi": "CHEBI:16634", "pubchem": "439242"},
        "MLZ": {"name": "Melezitose", "chebi": "CHEBI:28283", "pubchem": "92817"},

        # Glycosides and complex carbohydrates
        "AMY": {"name": "Amygdalin", "chebi": "CHEBI:17019", "pubchem": "656516"},  # API 20E context
        "AMYL": {"name": "Starch (Amylose)", "chebi": "CHEBI:28017", "pubchem": "24836924"},  # Polysaccharide
        "GLYG": {"name": "Glycogen", "chebi": "CHEBI:28087", "pubchem": "439177"},
        "INU": {"name": "Inulin", "chebi": "CHEBI:15443", "pubchem": "24763"},

        # Sugar alcohols
        "SOR": {"name": "D-Sorbitol", "chebi": "CHEBI:17924", "pubchem": "5780"},
        "MNE": {"name": "D-Mannose", "chebi": "CHEBI:4208", "pubchem": "18950"},  # API 20NE context; biotype100 uses for Mannitol
        "INO": {"name": "myo-Inositol", "chebi": "CHEBI:17268", "pubchem": "892"},
        "DUL": {"name": "Dulcitol", "chebi": "CHEBI:42118", "pubchem": "11850"},
        "ADO": {"name": "Adonitol", "chebi": "CHEBI:2509", "pubchem": "64639"},

        # Amino sugars
        "NAG": {"name": "N-Acetyl-D-glucosamine", "chebi": "CHEBI:28009", "pubchem": "24139"},

        # Deoxy sugars
        "RHA": {"name": "L-Rhamnose", "chebi": "CHEBI:27907", "pubchem": "25310"},
        "DFUC": {"name": "D-Fucose", "chebi": "CHEBI:42589", "pubchem": "246422"},
        "LFUC": {"name": "L-Fucose", "chebi": "CHEBI:2181", "pubchem": "17106"},

        # Uronic acids
        "GDC": {"name": "Gluconic acid", "chebi": "CHEBI:33198", "pubchem": "10690"},

        # Glycosides
        "ESC": {"name": "Esculin", "chebi": "CHEBI:4806", "pubchem": "5281417"},
        "SAL": {"name": "Salicin", "chebi": "CHEBI:17814", "pubchem": "439503"},
        "ARB": {"name": "Arbutin", "chebi": "CHEBI:2599", "pubchem": "440936"},

        # Organic acids
        "CIT": {"name": "Citrate", "chebi": "CHEBI:30769", "pubchem": "311"},  # Citrate anion
        "LAT": {"name": "Lactate", "chebi": "CHEBI:422", "pubchem": "107689"},  # Lactate anion
        "PAT": {"name": "Pyruvic acid", "chebi": "CHEBI:32816", "pubchem": "1060"},
        "SUC": {"name": "Succinic acid", "chebi": "CHEBI:15741", "pubchem": "1110"},
        "FUM": {"name": "Fumaric acid", "chebi": "CHEBI:18012", "pubchem": "444972"},
        "2KG": {"name": "2-Ketogluconic acid", "chebi": "CHEBI:17978", "pubchem": "7427"},
        "5KG": {"name": "5-Ketogluconic acid", "chebi": "CHEBI:17991", "pubchem": "160957"},

        # Glycerol and polyols
        "GLY": {"name": "Glycerol", "chebi": "CHEBI:17754", "pubchem": "753"},

        # Amino acids
        "TRY": {"name": "L-Tryptophan", "chebi": "CHEBI:16828", "pubchem": "6305"},
        "GLN": {"name": "L-Glutamine", "chebi": "CHEBI:58359", "pubchem": "5961"},
        "PRO": {"name": "L-Proline", "chebi": "CHEBI:26271", "pubchem": "145742"},
        "DALA": {"name": "D-Alanine", "chebi": "CHEBI:15570", "pubchem": "71080"},
        "LALA": {"name": "L-Alanine", "chebi": "CHEBI:16449", "pubchem": "5950"},
        "SER": {"name": "L-Serine", "chebi": "CHEBI:17115", "pubchem": "5951"},
        "TYR": {"name": "L-Tyrosine", "chebi": "CHEBI:17895", "pubchem": "6057"},

        # Organic acids (continued)
        "ADI": {"name": "Adipate", "chebi": "CHEBI:30831", "pubchem": "196"},  # API 20NE context - adipic acid anion

        # Others
        "URE": {"name": "Urea", "chebi": "CHEBI:16199", "pubchem": "1176"},
        "GEL": {"name": "Gelatin", "chebi": "CHEBI:5291", "pubchem": None},
        "ONPG": {"name": "o-Nitrophenyl-β-D-galactopyranoside", "chebi": "CHEBI:70697", "pubchem": "4625"},

        # Modified sugars
        "MDX": {"name": "Methyl-D-xyloside", "chebi": "CHEBI:73011", "pubchem": "92816"},
        "MDM": {"name": "Methyl-α-D-mannopyranoside", "chebi": "CHEBI:50031", "pubchem": "97143"},
        "MDG": {"name": "Methyl-α-D-glucopyranoside", "chebi": "CHEBI:27960", "pubchem": "11266"},

        # Rare sugars
        "LYX": {"name": "D-Lyxose", "chebi": "CHEBI:12301", "pubchem": "439236"},
        "TAG": {"name": "D-Tagatose", "chebi": "CHEBI:17004", "pubchem": "439654"},
        "SBE": {"name": "D-Sorbose", "chebi": "CHEBI:17262", "pubchem": "439192"},
        "GEN": {"name": "Gentiobiose", "chebi": "CHEBI:18296", "pubchem": "53234"},
        "TUR": {"name": "Turanose", "chebi": "CHEBI:27806", "pubchem": "439532"},
        "AMD": {"name": "Amidon (Starch)", "chebi": "CHEBI:28017", "pubchem": "24836924"},  # Alternative name for starch (same as AMYL)
        "XLT": {"name": "Xylitol", "chebi": "CHEBI:17151", "pubchem": "6912"},
        "DARL": {"name": "D-Arabitol", "chebi": "CHEBI:16708", "pubchem": "94154"},
        "LARL": {"name": "L-Arabitol", "chebi": "CHEBI:18087", "pubchem": "439255"},
        "GNT": {"name": "Gluconate", "chebi": "CHEBI:33198", "pubchem": "10690"},

        # Additional substrates
        "ERY": {"name": "Erythritol", "chebi": "CHEBI:17113", "pubchem": "222285"},
        "FUC": {"name": "Fucose", "chebi": "CHEBI:33984", "pubchem": None},
        "Q": {"name": "Quinate", "chebi": "CHEBI:17521", "pubchem": "6508"},
        "G1P": {"name": "Glucose-1-phosphate", "chebi": "CHEBI:16077", "pubchem": "65533"},
        "MLT": {"name": "Malate", "chebi": "CHEBI:30796", "pubchem": "525"},
        "CAP": {"name": "Caprate", "chebi": "CHEBI:30813", "pubchem": "3893"},
        "PAC": {"name": "Phenylacetate", "chebi": "CHEBI:30745", "pubchem": "999"},
        "GAT": {"name": "Galactitol", "chebi": "CHEBI:16813", "pubchem": "11850"},
        "GRT": {"name": "Glucuronate", "chebi": "CHEBI:47926", "pubchem": "94715"},
        "HIS": {"name": "L-Histidine", "chebi": "CHEBI:15971", "pubchem": "6274"},
        "ACE": {"name": "Acetate", "chebi": "CHEBI:30089", "pubchem": "176"},
        "PROP": {"name": "Propionate", "chebi": "CHEBI:30768", "pubchem": "1032"},
        "MNT": {"name": "Maltotriose", "chebi": "CHEBI:17253", "pubchem": "439586"},
        "PUL": {"name": "Pullulan", "chebi": "CHEBI:28653", "pubchem": None},
        "GTA": {"name": "Glutamate", "chebi": "CHEBI:29985", "pubchem": "33032"},
        "ITA": {"name": "Itaconate", "chebi": "CHEBI:30838", "pubchem": "811"},
        "CDEX": {"name": "Cyclodextrin", "chebi": "CHEBI:495083", "pubchem": None},
        "MUC": {"name": "Mucate", "chebi": "CHEBI:30850", "pubchem": "5460682"},
        "3OBU": {"name": "3-Hydroxybutyrate", "chebi": "CHEBI:20067", "pubchem": "441"},
        "2KT": {"name": "2-Ketoglutarate", "chebi": "CHEBI:16810", "pubchem": "51"},
    }

    # Kit-specific mappings that override global defaults
    # Used when kit context is known to handle ambiguous codes
    KIT_SPECIFIC_MAPPINGS = {
        "API 20E": {
            # In API 20E, MAN = D-Mannose (not Mannitol)
            "MAN": {"name": "D-Mannose", "chebi": "CHEBI:4208", "pubchem": "18950"},
            # ONPG is technically the substrate, but official docs refer to enzyme
            "ONPG": {"name": "β-galactosidase", "enzyme": True, "substrate": "o-Nitrophenyl-β-D-galactopyranoside"},
            # Capitalization variant
            "Sor": {"name": "D-Sorbitol", "chebi": "CHEBI:17924", "pubchem": "5780"},
        },
        "API 20NE": {
            # In API 20NE, MAN = D-Mannitol, MNE = D-Mannose
            "MAN": {"name": "D-Mannitol", "chebi": "CHEBI:16899", "pubchem": "6251"},
            "MNE": {"name": "D-Mannose", "chebi": "CHEBI:4208", "pubchem": "18950"},
            # Use official naming
            "NAG": {"name": "N-Acetyl-Glucosamine", "chebi": "CHEBI:28009", "pubchem": "24139"},
            "PAC": {"name": "Phenyl-acetate", "chebi": "CHEBI:30745", "pubchem": "999"},
        },
        "API zym": {
            # Control well has specific naming
            "Control": {"name": "Negative control", "control": True},
            # API zym uses full enzyme names as codes
            "Alkaline phosphatase": {"name": "Alkaline phosphatase", "ec": "3.1.3.1"},
            "Esterase (C4)": {"name": "Esterase (C4)", "ec": "3.1.1.-"},
            "Esterase": {"name": "Esterase (C4)", "ec": "3.1.1.-"},  # Variant without chain length
            "Esterase lipase (C8)": {"name": "Esterase lipase (C8)", "ec": "3.1.1.-"},
            "Esterase Lipase": {"name": "Esterase lipase (C8)", "ec": "3.1.1.-"},  # Spacing variant
            "Lipase (C14)": {"name": "Lipase (C14)", "ec": "3.1.1.3"},
            "Lipase": {"name": "Lipase (C14)", "ec": "3.1.1.3"},  # Variant without chain length
            "Leucine arylamidase": {"name": "Leucine arylamidase", "ec": "3.4.11.1"},
            "Valine arylamidase": {"name": "Valine arylamidase", "ec": "3.4.11.-"},
            "Cystine arylamidase": {"name": "Cystine arylamidase", "ec": "3.4.11.-"},
            "Trypsin": {"name": "Trypsin", "ec": "3.4.21.4"},
            "alpha-Chymotrypsin": {"name": "alpha-Chymotrypsin", "ec": "3.4.21.1"},
            "alpha- Chymotrypsin": {"name": "alpha-Chymotrypsin", "ec": "3.4.21.1"},  # Spacing variant
            "Acid phosphatase": {"name": "Acid phosphatase", "ec": "3.1.3.2"},
            "Naphthol-AS-BI-phosphohydrolase": {"name": "Naphthol-AS-BI-phosphohydrolase", "ec": "3.1.3.-"},
            "alpha-Galactosidase": {"name": "alpha-Galactosidase", "ec": "3.2.1.22"},
            "alpha- Galactosidase": {"name": "alpha-Galactosidase", "ec": "3.2.1.22"},  # Spacing variant
            "beta-Galactosidase": {"name": "beta-Galactosidase", "ec": "3.2.1.23"},
            "beta- Galactosidase": {"name": "beta-Galactosidase", "ec": "3.2.1.23"},  # Spacing variant
            "beta-Glucuronidase": {"name": "beta-Glucuronidase", "ec": "3.2.1.31"},
            "beta- Glucuronidase": {"name": "beta-Glucuronidase", "ec": "3.2.1.31"},  # Spacing variant
            "alpha-Glucosidase": {"name": "alpha-Glucosidase", "ec": "3.2.1.20"},
            "alpha- Glucosidase": {"name": "alpha-Glucosidase", "ec": "3.2.1.20"},  # Spacing variant
            "beta-Glucosidase": {"name": "beta-Glucosidase", "ec": "3.2.1.21"},
            "beta- Glucosidase": {"name": "beta-Glucosidase", "ec": "3.2.1.21"},  # Spacing variant
            "N-acetyl-beta-glucosaminidase": {"name": "N-acetyl-beta-glucosaminidase", "ec": "3.2.1.52"},
            "N-acetyl-beta- glucosaminidase": {"name": "N-acetyl-beta-glucosaminidase", "ec": "3.2.1.52"},  # Spacing variant
            "alpha-Mannosidase": {"name": "alpha-Mannosidase", "ec": "3.2.1.24"},
            "alpha- Mannosidase": {"name": "alpha-Mannosidase", "ec": "3.2.1.24"},  # Spacing variant
            "alpha-Fucosidase": {"name": "alpha-Fucosidase", "ec": "3.2.1.51"},
            "alpha- Fucosidase": {"name": "alpha-Fucosidase", "ec": "3.2.1.51"},  # Spacing variant
        },
    }

    # Well codes that are enzyme tests, not substrates
    ENZYME_TESTS = {
        "URE": "Urease",
        "GEL": "Gelatinase",
        "PAL": "Phenylalanine deaminase",
        "IND": "Indole production",
        "VP": "Voges-Proskauer",
        "TDA": "Tryptophan deaminase",
        "TDA Trp": "Tryptophan deaminase",
        "H2S": "Hydrogen sulfide production",
        "NIT": "Nitrate reductase",
        "NO2": "Nitrite reduction",
        "NO3": "Nitrate reduction",  # API 20NE code
        "N2": "Nitrogen gas production",
        "OX": "Cytochrome oxidase",
        "ONPG": "β-galactosidase (ONPG)",
        "PNG": "β-galactosidase (PNPG)",  # API 20NE code
        "TRP": "Tryptophane test",  # API 20NE code
    }

    # Enzyme activity tests
    ENZYME_ACTIVITY_TESTS = {
        # Decarboxylases and dihydrolases
        "ADH Arg": "Arginine dihydrolase",
        "ADH": "Arginine dihydrolase",
        "LDC Lys": "Lysine decarboxylase",
        "LDC": "Lysine decarboxylase",
        "ODC": "Ornithine decarboxylase",

        # Arylamidases (amino acid arylamidases)
        "ArgA": "Arginine arylamidase",
        "ProA": "Proline arylamidase",
        "LeuA": "Leucine arylamidase",
        "PyrA": "Pyroglutamic acid arylamidase",
        "TyrA": "Tyrosine arylamidase",
        "AlaA": "Alanine arylamidase",
        "GlyA": "Glycine arylamidase",
        "HisA": "Histidine arylamidase",
        "SerA": "Serine arylamidase",
        "PheA": "Phenylalanine arylamidase",
        "LGA": "Glutamyl glutamic acid arylamidase",
        "GGA": "Glutamyl glutamic acid arylamidase",  # Variant code
        "AspA": "Aspartic acid arylamidase",

        # Peptidases and proteases
        "LAP": "Leucine aminopeptidase",
        "PYRA": "Pyrrolidonyl arylamidase",
        "HIP": "Hippurate hydrolysis",
        "GGT": "Gamma-glutamyl transferase",
        "EST": "Esterase",
        "LIP": "Lipase",

        # Glycosidases
        "PNPG": "β-galactosidase (PNPG)",
        "MaGa": "α-galactosidase (Mannosidase)",
        "MbGa": "β-galactosidase",
        "MbGu": "β-glucuronidase",
        "Mbeta DG": "β-galactosidase",
        # Greek letter prefix glycosidases (abbreviated codes from various API kits)
        "alpha GAL": "α-galactosidase",
        "alpha GLU": "α-glucosidase",
        "alpha MAN": "α-mannosidase",
        "alpha ARA": "α-arabinosidase",
        "alpha FUC": "α-fucosidase",
        "alphaMAL": "α-maltosidase",
        "beta GAL": "β-galactosidase",
        "beta GLU": "β-glucosidase",
        "beta GUR": "β-glucuronidase",
        "beta NAG": "β-N-acetyl-glucosaminidase",
        "beta GAR": "β-galactosidase",  # Variant code
        "beta GP": "β-glycosidase",
        "beta MAN": "β-mannosidase",

        # Other enzymes
        "CAT": "Catalase",
        "PYZ": "Pyrazinamidase",
        "PLE": "Phospholipase",
        "APPA": "Alanine-phenylalanine-proline arylamidase",

        # Assimilation/fermentation variants (these appear in different contexts)
        "GLU_ Assim": "Glucose assimilation",
        "GLU_ Ferm": "Glucose fermentation",
    }

    # Phenotypic and morphological tests (not substrates or enzymes)
    PHENOTYPIC_TESTS = {
        "Control": "Control well (no substrate)",
        "NO3": "Nitrate reduction",
        "TRP": "Tryptophan test",
        "MOB": "Motility",
        "SPOR": "Sporulation",
        "GRAM": "Gram stain",
        "TTC": "Tetrazolium reduction",
        "OF-F": "Oxidative-fermentative (fermentative)",
        "OF-O": "Oxidative-fermentative (oxidative)",
        "NOVO": "Novobiocin resistance",
        "RP": "Reverse CAMP test",
        "COCC": "Coagulase test",
        "CATE": "Catalase test",
        "Trypsin": "Trypsin activity",

        # Growth tests
        "NAL": "Nalidixic acid resistance",
        "PEN": "Penicillin resistance",
        "CFZ": "Cefoxitin resistance",

        # Metabolism indicators
        "BET": "Betaine utilization",
        "ETN": "Ethanol utilization",
        "ABT": "Arabitol",
        "MTL": "Mannitol utilization",
        "AVT": "Arabinose variant test",
        "BAT": "Beta-alanine test",
        "CMT": "Coumarin test",
        "CYT": "Cytochrome test",
        "DIM": "Dimethyl test",
        "ERO": "Erythromycin test",
        "GRE": "Green fluorescence",
        "GTE": "Gelatin liquefaction variant",
        "GYT": "Glycerol test variant",
        "HBG": "Hemoglobin test",
        "HIN": "Hippurate test variant",
        "LMLT": "L-Malate test",
        "DMLT": "D-Malate test",
        "LSTR": "L-Serine test",
        "LTAT": "L-Tartrate",
        "DTAT": "D-Tartrate",
        "MTAT": "Meso-Tartrate",
        "LTE": "Lactose variant test",
        "MAC": "MacConkey agar",
        "MTE": "Maltose variant test",
        "PCE": "Penicillin variant",
        "PPAT": "Phenylpyruvic acid test",
        "QAT": "Quinine test",
        "SAT": "Salicin variant test",
        "SUT": "Sucrose variant test",
        "TATE": "Tartrate variant test",
        "TGE": "Trehalose variant test",
        "TTN": "Tetanus toxin",
        "TTE": "Trehalose variant enzyme",
        "APT": "Alanine-phenylalanine-proline test",
        "GNT": "Gluconate",
        "GTT": "Glutamate test",
        "3MDG": "3-Methyl-D-glucose",
        "mOBE": "meta-hydroxybenzoate",
        "pOBE": "para-hydroxybenzoate",
    }

    # EC number mappings for enzyme names - Exact matching from ExpASy ENZYME database
    # Generated 2025-12-04 using deterministic exact matching algorithm
    # Source: ExpASy ENZYME flat file database (enzyme.dat)
    # Method: Exact string matching against primary labels and synonyms
    # 96 exact matches (33.7%), 82 partial matches (28.8%), 107 unmapped (37.5%)
    ENZYME_EC_MAPPINGS = {
        "6-phospho-beta-galactosidase": "3.2.1.85",
        "ACC deaminase": "3.5.99.7",
        "Acid phosphatase": "3.1.3.2",
        "Alkaline phosphatase": "3.1.3.1",
        "Arginine dihydrolase": "3.5.3.6",
        "Catalase": "1.11.1.6",
        "Cytochrome oxidase": "7.1.1.9",
        "D-aminoacylase": "3.5.1.81",
        "DNase": "3.1.21.1",
        "Dnase": "3.1.21.1",
        "Leucine aminopeptidase": "3.4.11.1",
        "Lipase": "3.1.1.3",
        "Lysine decarboxylase": "4.1.1.18",
        "N-acetyl-beta-glucosaminidase": "3.2.1.52",
        "Ornithine decarboxylase": "4.1.1.17",
        "Ribulose-bisphosphate carboxylase": "4.1.1.39",
        "Urease": "3.5.1.5",
        "Xylanase": "3.2.1.32",
        "acetate kinase": "2.7.2.1",
        "acid phosphatase": "3.1.3.2",
        "adenylate cyclase": "4.6.1.1",
        "agarase": "3.2.1.81",
        "alcohol dehydrogenase": "1.1.1.1",
        "alkaline phosphatase": "3.1.3.1",
        "alpha-Amylase": "3.2.1.1",
        "alpha-L-arabinofuranosidase": "3.2.1.55",
        "alpha-L-rhamnosidase": "3.2.1.40",
        "alpha-chymotrypsin": "3.4.21.1",
        "alpha-galactosidase": "3.2.1.22",
        "alpha-glucosidase": "3.2.1.20",
        "alpha-glucuronidase": "3.2.1.139",
        "alpha-mannosidase": "3.2.1.24",
        "alpha-xylosidase": "3.2.1.177",
        "arginine Dihydrolase": "3.5.3.6",
        "arginine decarboxylase": "1.13.12.1",
        "arginine dihydrolase": "3.5.3.6",
        "beta-D-fucosidase": "3.2.1.38",
        "beta-L-arabinosidase": "3.2.1.88",
        "beta-N-acetylgalactosaminidase": "3.2.1.53",
        "beta-galactosidase": "3.2.1.23",
        "beta-glucosidase": "3.2.1.21",
        "beta-glucuronidase": "3.2.1.31",
        "beta-lactamase": "3.5.2.6",
        "beta-mannosidase": "3.2.1.25",
        "beta-xylosidase": "3.2.1.37",
        "carboxylesterase": "3.1.1.1",
        "catalase": "1.11.1.6",
        "cellulase": "3.2.1.4",
        "chitinase": "3.2.1.14",
        "cholesterol esterase": "3.1.1.13",
        "chymotrypsin": "3.4.21.1",
        "cyclomaltodextrin glucanotransferase": "2.4.1.19",
        "cystine aminopeptidase": "3.4.11.3",
        "cytochrome oxidase": "7.1.1.9",
        "cytochrome-c oxidase": "7.1.1.9",
        "endo-1,3(4)-beta-glucanase": "3.2.1.6",
        "endo-1,4-beta-xylanase": "3.2.1.8",
        "fructose-6-phosphate phosphoketolase": "4.1.2.22",
        "gamma-glutamyltransferase": "2.3.2.2",
        "glutamate decarboxylase": "4.1.1.15",
        "glutamate dehydrogenase": "1.4.1.2",
        "heparin lyase": "4.2.2.7",
        "hippurate hydrolase": "3.5.1.32",
        "hyaluronate lyase": "4.2.2.1",
        "hyaluronidase": "3.2.1.35",
        "hydrogenase": "1.12.1.2",
        "leucine aminopeptidase": "3.4.11.1",
        "lipase": "3.1.1.3",
        "lipase (C 14)": "3.1.1.3",
        "lipase (Tween 80)": "3.1.1.3",
        "lysine decarboxylase": "4.1.1.18",
        "lysozyme": "3.2.1.17",
        "methanol dehydrogenase": "1.1.1.244",
        "nitrite reductase": "1.7.2.1",
        "nitrogenase": "1.18.6.1",
        "ornithine decarboxylase": "4.1.1.17",
        "oxoglutarate dehydrogenase": "1.2.4.2",
        "pectinase": "3.2.1.15",
        "penicillinase": "3.5.2.6",
        "phenylalaninase": "1.14.16.1",
        "phenylalanine ammonia-lyase": "4.3.1.24",
        "phosphatase": "3.1.3.52",
        "phosphatidate phosphatase": "3.1.3.4",
        "phosphatidylinositol phospholipase C": "3.1.4.11",
        "phosphoamidase": "3.9.1.1",
        "phosphohydrolase": "3.6.1.54",
        "phospholipase C": "3.1.4.3",
        "superoxide dismutase": "1.15.1.1",
        "thiosulfate reductase": "2.8.1.5",
        "tripeptide aminopeptidase": "3.4.11.4",
        "trypsin": "3.4.21.4",
        "tryptophan decarboxylase": "4.1.1.28",
        "tryptophanase": "1.13.11.11",
        "tyrosinase": "1.10.3.1",
        "urease": "3.5.1.5",
        "xylan 1,4-beta-xylosidase": "3.2.1.37",
    }

    # Partial EC numbers (enzyme family level) for enzymes without exact matches
    # These represent enzyme families where specific EC number cannot be determined
    PARTIAL_EC_MAPPINGS = {
        "Alanine arylamidase": "3.5.-.-",
        "Alanine-phenylalanine-proline arylamidase": "3.5.-.-",
        "Alanyl-Phenylalanyl-Proline arylamidase": "3.5.-.-",
        "Arginine arylamidase": "3.5.-.-",
        "Aspartic acid arylamidase": "3.5.-.-",
        "Esterase": "3.1.1.-",
        "Gamma-glutamyl transferase": "2.-.-.-",
        "Glutamyl glutamic acid arylamidase": "3.5.-.-",
        "Glycine arylamidase": "3.5.-.-",
        "Histidine arylamidase": "3.5.-.-",
        "L-arginine arylamidase": "3.5.-.-",
        "L-arginine dihydrolase": "3.-.-.-",
        "L-aspartate arylamidase": "3.5.-.-",
        "L-leucyl-2-naphthylamide hydrolase": "3.-.-.-",
        "Leucine arylamidase": "3.5.-.-",
        "N-acetyl-glucosidase": "3.2.1.-",
        "Nitrate reductase": "1.-.-.-",
        "Phenylalanine arylamidase": "3.5.-.-",
        "Phospholipase": "3.1.1.-",
        "Proline arylamidase": "3.5.-.-",
        "Pyrazinamidase": "3.5.-.-",
        "Pyroglutamic acid arylamidase": "3.5.-.-",
        "Pyrrolidonyl arylamidase": "3.5.-.-",
        "Serine arylamidase": "3.5.-.-",
        "Tyrosine arylamidase": "3.5.-.-",
        "alanine aminopeptidase": "3.4.-.-",
        "alanine arylamidase": "3.5.-.-",
        "alanine phenylalanin proline arylamidase": "3.5.-.-",
        "arginine arylamidase": "3.5.-.-",
        "benzoyl-D-arginine arylamidase": "3.5.-.-",
        "beta-D-galactosidase": "3.2.1.-",
        "beta-Galactosidase 6-phosphate": "3.2.1.-",
        "beta-alanine arylamidase pNA": "3.5.-.-",
        "beta-galactosaminidase": "3.4.-.-",
        "beta-galactosidase-6-phosphate": "3.2.1.-",
        "beta-glucosaminidase": "3.4.-.-",
        "cystine arylamidase": "3.5.-.-",
        "esterase": "3.1.1.-",
        "esterase (C 4)": "3.1.1.-",
        "esterase Lipase (C 8)": "3.1.1.-",
        "esterase lipase (C 8)": "3.1.1.-",
        "glu-gly-arg-arylamidase": "3.5.-.-",
        "glucosaminidase": "3.4.-.-",
        "glucose isomerase": "5.-.-.-",
        "glucosidase": "3.2.1.-",
        "glutamin glycerin arginin arylamidase": "3.5.-.-",
        "glutamyl arylamidase pNA": "3.5.-.-",
        "glutamyl-glutamate arylamidase": "3.5.-.-",
        "glu–gly–arg arylamidase": "3.5.-.-",
        "glu–gly–arg-arylamidase": "3.5.-.-",
        "glycin arylamidase": "3.5.-.-",
        "glycyl tryptophan arylamidase": "3.5.-.-",
        "histidine arylamidase": "3.5.-.-",
        "l-pyrrolydonyl arylamidase": "3.5.-.-",
        "l-pyrrolyldonyl-arylamidase": "3.5.-.-",
        "leucine arylamidase": "3.5.-.-",
        "leucyl glycin arylamidase": "3.5.-.-",
        "naphthol-AS-BI-phosphohydrolase": "3.-.-.-",
        "nitrate reductase": "1.-.-.-",
        "oxidase": "1.-.-.-",
        "phenylalanine arylamidase": "3.5.-.-",
        "proline-arylamidase": "3.5.-.-",
        "protease": "3.4.-.-",
        "pyrazinamidase": "3.5.-.-",
        "pyroglutamic acid arylamidase": "3.5.-.-",
        "pyrrolidonyl arylamidase": "3.5.-.-",
        "serine arylamidase": "3.5.-.-",
        "skimmed milk protease": "3.4.-.-",
        "tellurite reductase": "1.-.-.-",
        "tween esterase": "3.1.1.-",
        "tyrosine arylamidase": "3.5.-.-",
        "valine aminopeptidase": "3.4.-.-",
        "valine arylamidase": "3.5.-.-",
        "α-galactosidase": "3.2.1.-",
        "α-galactosidase (Mannosidase)": "3.2.1.-",
        "α-glucosidase": "3.2.1.-",
        "β-N-acetyl-glucosaminidase": "3.4.-.-",
        "β-galactosidase": "3.2.1.-",
        "β-galactosidase (ONPG)": "3.2.1.-",
        "β-galactosidase (PNPG)": "3.2.1.-",
        "β-glucosidase": "3.2.1.-",
        "β-glycosidase": "3.2.1.-",
    }

    # GO term mappings for tests that cannot have EC numbers
    # Used when test is too generic or represents multi-enzyme pathway
    # Generated 2025-11-26 - See ENZYME_PATHWAY_ID_ASSIGNMENT.md for sources
    GO_TERM_MAPPINGS = {
        # Generic enzyme activities (too broad for single EC number)
        "beta GP": {
            "go_id": "GO:0004553",
            "go_name": "hydrolase activity, hydrolyzing O-glycosyl compounds",
            "reason": "Generic β-glycosidase, substrate not specified"
        },
        "BETAGP": {  # Normalized version
            "go_id": "GO:0004553",
            "go_name": "hydrolase activity, hydrolyzing O-glycosyl compounds",
            "reason": "Generic β-glycosidase, substrate not specified"
        },

        # Multi-enzyme pathways (cannot assign single EC number)
        "GLU_ Ferm": {
            "go_id": "GO:0019660",
            "go_name": "glycolytic fermentation",
            "reason": "Multi-enzyme pathway: glucose → pyruvate → fermentation products"
        },
        "GLUFERM": {  # Normalized version
            "go_id": "GO:0019660",
            "go_name": "glycolytic fermentation",
            "reason": "Multi-enzyme pathway: glucose → pyruvate → fermentation products"
        },
        "GLU_ Assim": {
            "go_id": "GO:1904659",
            "go_name": "glucose transmembrane transport",
            "reason": "Multi-step process: transport + phosphorylation + metabolism"
        },
        "GLUASSIM": {  # Normalized version
            "go_id": "GO:1904659",
            "go_name": "glucose transmembrane transport",
            "reason": "Multi-step process: transport + phosphorylation + metabolism"
        },
    }

    # METPO predicate mappings for positive and negative assay results
    # Generated 2025-12-02 from METPO ontology v17
    # Maps assay categories to appropriate METPO predicates
    METPO_PREDICATE_MAPPINGS = {
        # Carbohydrate fermentation tests (API 50CHac, API 50CHas, API 20STR)
        "Carbohydrate fermentation": {
            "positive": {"id": "METPO:2000011", "label": "ferments"},
            "negative": {"id": "METPO:2000037", "label": "does not ferment"},
        },

        # Enzyme profiling tests (API zym)
        "Enzyme profiling": {
            "positive": {"id": "METPO:2000302", "label": "shows activity of"},
            "negative": {"id": "METPO:2000303", "label": "does not show activity of"},
        },

        # Biochemical profiling tests (API biotype100)
        "Biochemical profiling": {
            "positive": {"id": "METPO:2000012", "label": "uses for growth"},
            "negative": {"id": "METPO:2000038", "label": "does not use for growth"},
        },

        # Bacterial identification kits (API 20E, API 20NE, API 20A, etc.)
        # Use general metabolic predicates
        "Bacterial identification": {
            "positive": {"id": "METPO:2000002", "label": "assimilates"},
            "negative": {"id": "METPO:2000027", "label": "does not assimilate"},
        },

        # Specific well type overrides (takes precedence over kit category)
        "_well_type_overrides": {
            # Enzyme wells always use enzyme activity predicates
            "enzyme": {
                "positive": {"id": "METPO:2000302", "label": "shows activity of"},
                "negative": {"id": "METPO:2000303", "label": "does not show activity of"},
            },

            # Chemical wells for fermentation
            "chemical_fermentation": {
                "positive": {"id": "METPO:2000011", "label": "ferments"},
                "negative": {"id": "METPO:2000037", "label": "does not ferment"},
            },

            # Chemical wells for utilization/assimilation
            "chemical_utilization": {
                "positive": {"id": "METPO:2000002", "label": "assimilates"},
                "negative": {"id": "METPO:2000027", "label": "does not assimilate"},
            },
        },

        # Specific test overrides (well code → predicate)
        "_well_code_overrides": {
            # Reduction tests
            "NO3": {
                "positive": {"id": "METPO:2000017", "label": "reduces"},
                "negative": {"id": "METPO:2000044", "label": "does not reduce"},
            },
            "NO2": {
                "positive": {"id": "METPO:2000017", "label": "reduces"},
                "negative": {"id": "METPO:2000044", "label": "does not reduce"},
            },
            "N2": {
                "positive": {"id": "METPO:2000017", "label": "reduces"},
                "negative": {"id": "METPO:2000044", "label": "does not reduce"},
            },

            # Production tests
            "H2S": {
                "positive": {"id": "METPO:2000202", "label": "produces"},
                "negative": {"id": "METPO:2000222", "label": "does not produce"},
            },
            "IND": {
                "positive": {"id": "METPO:2000202", "label": "produces"},
                "negative": {"id": "METPO:2000222", "label": "does not produce"},
            },
            "VP": {
                "positive": {"id": "METPO:2000202", "label": "produces"},
                "negative": {"id": "METPO:2000222", "label": "does not produce"},
            },

            # Hydrolysis tests
            "GEL": {
                "positive": {"id": "METPO:2000013", "label": "hydrolyzes"},
                "negative": {"id": "METPO:2000039", "label": "does not hydrolyze"},
            },
            "ESC": {
                "positive": {"id": "METPO:2000013", "label": "hydrolyzes"},
                "negative": {"id": "METPO:2000039", "label": "does not hydrolyze"},
            },

            # Fermentation pathway tests
            "GLU_ Ferm": {
                "positive": {"id": "METPO:2000011", "label": "ferments"},
                "negative": {"id": "METPO:2000037", "label": "does not ferment"},
            },

            # Assimilation tests
            "GLU_ Assim": {
                "positive": {"id": "METPO:2000002", "label": "assimilates"},
                "negative": {"id": "METPO:2000027", "label": "does not assimilate"},
            },
        },
    }

    # Metabolite mappings for BacDive unmapped metabolites (317 total)
    # Researched CHEBI and PubChem IDs - generated 2025-11-18
    METABOLITE_MAPPINGS = {
        "Potassium 5-ketogluconate": {"chebi": None, "pubchem": "23702137"},
        "Potassium 2-ketogluconate": {"chebi": None, "pubchem": None},
        "casein": {"chebi": None, "pubchem": None},
        "esculin ferric citrate": {"chebi": "CHEBI:4853", "pubchem": "5281417"},
        "potassium 5-dehydro-D-gluconate": {"chebi": None, "pubchem": "23702137"},
        "potassium 2-dehydro-D-gluconate": {"chebi": None, "pubchem": None},
        "yeast extract": {"chebi": None, "pubchem": None},
        "peptone": {"chebi": None, "pubchem": None},
        "milk": {"chebi": None, "pubchem": None},
        "casamino acids": {"chebi": None, "pubchem": None},
        "L-alanine 4-nitroanilide": {"chebi": None, "pubchem": None},
        "skimmed milk": {"chebi": None, "pubchem": None},
        "2-oxogluconate": {"chebi": "CHEBI:16810", "pubchem": "164533"},
        "tryptone": {"chebi": None, "pubchem": None},
        "L-lactate": {"chebi": "CHEBI:422", "pubchem": "107689"},
        "maltose hydrate": {"chebi": None, "pubchem": None},
        "1 % sodium lactate": {"chebi": None, "pubchem": None},
        "O-nitrophenyl-beta-D-galactopyranosid": {"chebi": None, "pubchem": None},
        "polysaccharides": {"chebi": None, "pubchem": None},
        "corn oil": {"chebi": None, "pubchem": None},
        "L-proline-4-nitroanilide": {"chebi": None, "pubchem": None},
        "4-nitrophenyl beta-D-galactopyranoside hydrolysate": {"chebi": None, "pubchem": None},
        "casein hydrolysate": {"chebi": None, "pubchem": None},
        "n-acetyl-neuraminic acid": {"chebi": None, "pubchem": None},
        "alpha-hydroxybutyrate": {"chebi": None, "pubchem": None},
        "yeast extract (0.01 %, w/v)": {"chebi": None, "pubchem": None},
        "D-lactate": {"chebi": None, "pubchem": None},
        "D-lactic acid methyl ester": {"chebi": None, "pubchem": None},
        "3-O-methyl alpha-D-glucopyranoside": {"chebi": None, "pubchem": None},
        "gamma-L-glutamate-4-nitroanilide": {"chebi": None, "pubchem": None},
        "egg yolk": {"chebi": None, "pubchem": None},
        "trimethoxybenzoate": {"chebi": None, "pubchem": None},
        "crab shell chitin": {"chebi": None, "pubchem": None},
        "methyl alpha-D-xylopyranoside": {"chebi": None, "pubchem": None},
        "2,3-butanediol": {"chebi": None, "pubchem": "262"},
        "L-glutamate-gamma-3-carboxy-4-nitroanilide": {"chebi": None, "pubchem": None},
        "crystalline cellulose": {"chebi": None, "pubchem": None},
        "(-)-D-rhamnose": {"chebi": None, "pubchem": None},
        "fermented rumen extract": {"chebi": None, "pubchem": None},
        "esculin hydrolysate": {"chebi": None, "pubchem": None},
        "2-deoxythymidine-5'-4-nitrophenyl phosphate": {"chebi": None, "pubchem": None},
        "beef extract": {"chebi": None, "pubchem": None},
        "(+)-D-glycogen": {"chebi": None, "pubchem": None},
        "ferrihydrite": {"chebi": None, "pubchem": None},
        "synanthrin": {"chebi": None, "pubchem": None},
        "butanol": {"chebi": "CHEBI:28885", "pubchem": "263"},
        "sodium malate": {"chebi": None, "pubchem": None},
        "manganese dioxide": {"chebi": "CHEBI:136511", "pubchem": "14801"},
        "soyton": {"chebi": None, "pubchem": None},
        "hydroxy-L-proline": {"chebi": None, "pubchem": None},
        "(2)-D-lactose": {"chebi": None, "pubchem": None},
        "amorphous iron (iii) oxide": {"chebi": None, "pubchem": None},
        "sodium(+)": {"chebi": None, "pubchem": None},
        "(+)-D-galactose": {"chebi": None, "pubchem": None},
        "meat extract": {"chebi": None, "pubchem": None},
        "DL-2-gamma-aminobutyrate": {"chebi": None, "pubchem": None},
        "olive oil": {"chebi": None, "pubchem": None},
        "casitone": {"chebi": None, "pubchem": None},
        "indoxyl acetate": {"chebi": None, "pubchem": None},
        "goethite": {"chebi": None, "pubchem": None},
        "glycyl-L-bromosuccinic glutamic acid": {"chebi": None, "pubchem": None},
        "trehalose dihydrate": {"chebi": None, "pubchem": None},
        "Bacteriochlorophyll alpha": {"chebi": None, "pubchem": None},
        "(+)-L-aspartate": {"chebi": None, "pubchem": None},
        "casamino acids (0.01 %, w/v)": {"chebi": None, "pubchem": None},
        "peptone (0.01 %, w/v)": {"chebi": None, "pubchem": None},
        "(+)-D-mannose": {"chebi": None, "pubchem": None},
        "(+)-D-xylose": {"chebi": None, "pubchem": None},
        "(+)-L-rhamnose": {"chebi": None, "pubchem": None},
        "1-o-methyl alpha-galactopyranoside": {"chebi": None, "pubchem": None},
        "rumen extract": {"chebi": None, "pubchem": None},
        "D-galactose": {"chebi": None, "pubchem": None},
        "1,2-butandiol": {"chebi": None, "pubchem": None},
        "sedoheptulosan": {"chebi": None, "pubchem": None},
        "amorphous fe(iii) oxyhydroxid": {"chebi": None, "pubchem": None},
        "proteose": {"chebi": None, "pubchem": None},
        "polypeptone": {"chebi": None, "pubchem": None},
        "maltose": {"chebi": "CHEBI:17306", "pubchem": "439186"},
        "L-pyroglutamic acid": {"chebi": None, "pubchem": None},
        "(+)-L-glutamate": {"chebi": None, "pubchem": None},
        "(+)-L-ornithine": {"chebi": None, "pubchem": None},
        "(2)-D-fructose": {"chebi": None, "pubchem": None},
        "(+)-D-glucosamine": {"chebi": None, "pubchem": None},
        "(2)-D-lyxose": {"chebi": None, "pubchem": None},
        "(+)-L-lyxitol": {"chebi": None, "pubchem": None},
        "L-aniline-4-nitroanilide": {"chebi": None, "pubchem": None},
        "6-O-alpha-D-glucopyranosyl-D-gluconic acid": {"chebi": None, "pubchem": None},
        "esculin": {"chebi": "CHEBI:4853", "pubchem": "5281417"},
        "L-alanine": {"chebi": "CHEBI:16977", "pubchem": "5950"},
        "aburamycin A": {"chebi": None, "pubchem": None},
        "setamycin": {"chebi": None, "pubchem": None},
        "neomycin E": {"chebi": None, "pubchem": None},
        "neomycin F": {"chebi": None, "pubchem": None},
        "bottromycin": {"chebi": None, "pubchem": None},
        "actinomycin X": {"chebi": None, "pubchem": None},
        "carbomycin": {"chebi": None, "pubchem": None},
        "eurocidin": {"chebi": None, "pubchem": None},
        "2-oxoglutarate": {"chebi": "CHEBI:16810", "pubchem": "164533"},
        "4-nitrophenyl phosphate disodium salt": {"chebi": None, "pubchem": None},
        "sodium fumarate": {"chebi": None, "pubchem": None},
        "methyl alpha-D-glucopyranoside": {"chebi": None, "pubchem": None},
        "synthetic sea salts (sss)": {"chebi": None, "pubchem": None},
        "L-glycine": {"chebi": "CHEBI:15428", "pubchem": "750"},
        "4-nitrophenyl-alpha-D-maltopyranoside": {"chebi": None, "pubchem": None},
        "dipic acid": {"chebi": None, "pubchem": None},
        "Ny-carrageenan": {"chebi": None, "pubchem": None},
        "My-carrageenan": {"chebi": None, "pubchem": None},
        "locust bean gum": {"chebi": None, "pubchem": None},
        "crude oil": {"chebi": None, "pubchem": None},
        "pentatriacontane": {"chebi": None, "pubchem": None},
        "coconut  oil": {"chebi": None, "pubchem": None},
        "oil of cedar wood": {"chebi": None, "pubchem": None},
        "nutrient broth": {"chebi": None, "pubchem": None},
        "potato agar": {"chebi": None, "pubchem": None},
        "4-aminovalerate": {"chebi": None, "pubchem": None},
        "fe(iii) citrate": {"chebi": None, "pubchem": None},
        "flavin adenine dinucleotide": {"chebi": None, "pubchem": None},
        "poly(hexamethylene carbonate)": {"chebi": None, "pubchem": None},
        "poly(tetramethylene carbonate)": {"chebi": None, "pubchem": None},
        "mannoic acid gamma-lactone": {"chebi": None, "pubchem": None},
        "glycerate": {"chebi": None, "pubchem": None},
        "2,3-butanone": {"chebi": None, "pubchem": None},
        "citramalic acid": {"chebi": None, "pubchem": None},
        "D-ribono-1,4-lactone": {"chebi": None, "pubchem": None},
        "DL-carnitine": {"chebi": None, "pubchem": None},
        "dl-octopamine": {"chebi": None, "pubchem": None},
        "methyl beta-D-glucuronic acid": {"chebi": None, "pubchem": None},
        "sec-butylamine": {"chebi": None, "pubchem": None},
        "3-hydroxy 2-butanone": {"chebi": None, "pubchem": None},
        "melibionic acid": {"chebi": None, "pubchem": None},
        "oxalomalic acid": {"chebi": None, "pubchem": None},
        "indochrome": {"chebi": None, "pubchem": None},
        "L-sorbosone": {"chebi": None, "pubchem": None},
        "verdamycin": {"chebi": None, "pubchem": None},
        "pyridomycin": {"chebi": None, "pubchem": None},
        "gardimycin": {"chebi": None, "pubchem": None},
        "dynemicin": {"chebi": None, "pubchem": None},
        "fortimicin B": {"chebi": None, "pubchem": None},
        "halomicin": {"chebi": None, "pubchem": None},
        "abyssomicin B": {"chebi": None, "pubchem": None},
        "abyssomicin C": {"chebi": None, "pubchem": None},
        "abyssomicin D": {"chebi": None, "pubchem": None},
        "abyssomicin G": {"chebi": None, "pubchem": None},
        "abyssomicin H": {"chebi": None, "pubchem": None},
        "atrop-abyssomicin C": {"chebi": None, "pubchem": None},
        "proximicin A": {"chebi": None, "pubchem": None},
        "nocardimicin G": {"chebi": None, "pubchem": None},
        "nocardimicin H": {"chebi": None, "pubchem": None},
        "nocardimicin I": {"chebi": None, "pubchem": None},
        "sandramycin": {"chebi": None, "pubchem": None},
        "3-trehalosamine": {"chebi": None, "pubchem": None},
        "marinostatin": {"chebi": None, "pubchem": None},
        "chlororaphin": {"chebi": None, "pubchem": None},
        "ardacin A": {"chebi": None, "pubchem": None},
        "ardacin B": {"chebi": None, "pubchem": None},
        "ardacin C": {"chebi": None, "pubchem": None},
        "dopsisamine": {"chebi": None, "pubchem": None},
        "vancoresmycin": {"chebi": None, "pubchem": None},
        "decaplanin": {"chebi": None, "pubchem": None},
        "balhimycin": {"chebi": None, "pubchem": None},
        "Ethylenediamine-N,N'-disuccinic acid (EDDS)": {"chebi": None, "pubchem": None},
        "avoparcin": {"chebi": None, "pubchem": None},
        "efrotomycin": {"chebi": None, "pubchem": None},
        "Cetocycline": {"chebi": None, "pubchem": None},
        "azureomycin": {"chebi": None, "pubchem": None},
        "ristocetin A": {"chebi": None, "pubchem": None},
        "ristocetin B": {"chebi": None, "pubchem": None},
        "nocamycin": {"chebi": None, "pubchem": None},
        "texazone": {"chebi": None, "pubchem": None},
        "formamicin": {"chebi": None, "pubchem": None},
        "cycloviracin B1": {"chebi": None, "pubchem": None},
        "cycloviracin B2": {"chebi": None, "pubchem": None},
        "limocrocin": {"chebi": None, "pubchem": None},
        "ascosin": {"chebi": None, "pubchem": None},
        "danomycin": {"chebi": None, "pubchem": None},
        "achromoviromycin": {"chebi": None, "pubchem": None},
        "sarcidin": {"chebi": None, "pubchem": None},
        "cystargin": {"chebi": None, "pubchem": None},
        "actinomycin A": {"chebi": None, "pubchem": None},
        "actinomycin B": {"chebi": None, "pubchem": None},
        "chlorothricin": {"chebi": None, "pubchem": None},
        "ketomycin": {"chebi": None, "pubchem": None},
        "congocidin": {"chebi": None, "pubchem": None},
        "spiramycin": {"chebi": "CHEBI:85260", "pubchem": "5266"},
        "matamycin": {"chebi": None, "pubchem": None},
        "pamamycin": {"chebi": None, "pubchem": None},
        "champamycin B": {"chebi": None, "pubchem": None},
        "rhodomycin A": {"chebi": None, "pubchem": None},
        "rhodomycin B": {"chebi": None, "pubchem": None},
        "aureothricin": {"chebi": None, "pubchem": None},
        "cellostatin": {"chebi": None, "pubchem": None},
        "amphomycin": {"chebi": None, "pubchem": None},
        "bluensomycin": {"chebi": None, "pubchem": None},
        "antimycin A3": {"chebi": None, "pubchem": None},
        "venturicidin A": {"chebi": None, "pubchem": None},
        "venturicidin B": {"chebi": None, "pubchem": None},
        "flavofungin": {"chebi": None, "pubchem": None},
        "caryomycin": {"chebi": None, "pubchem": None},
        "angolamycin": {"chebi": None, "pubchem": None},
        "durhamycin": {"chebi": None, "pubchem": None},
        "etamycin": {"chebi": None, "pubchem": None},
        "collinomycin": {"chebi": None, "pubchem": None},
        "bryamycin": {"chebi": None, "pubchem": None},
        "griseoviridin": {"chebi": None, "pubchem": None},
        "viridogrisein": {"chebi": None, "pubchem": None},
        "alazopeptin": {"chebi": None, "pubchem": None},
        "griseolutein A": {"chebi": None, "pubchem": None},
        "griseolutein B": {"chebi": None, "pubchem": None},
        "blasticidin A": {"chebi": None, "pubchem": None},
        "bandamycin": {"chebi": None, "pubchem": None},
        "cinerubin A": {"chebi": None, "pubchem": None},
        "lydimycin": {"chebi": None, "pubchem": None},
        "mycobacidin": {"chebi": None, "pubchem": None},
        "glebomycin": {"chebi": None, "pubchem": None},
        "demecycline": {"chebi": None, "pubchem": None},
        "amicetin": {"chebi": None, "pubchem": None},
        "bamicetin": {"chebi": None, "pubchem": None},
        "plicacetin": {"chebi": None, "pubchem": None},
        "pactamycin": {"chebi": None, "pubchem": None},
        "staphylomycin M1": {"chebi": None, "pubchem": None},
        "synergistin A": {"chebi": None, "pubchem": None},
        "amphotericin A": {"chebi": None, "pubchem": None},
        "amphotericin B": {"chebi": "CHEBI:2682", "pubchem": "5280965"},
        "cinerubin R": {"chebi": None, "pubchem": None},
        "showdomycin": {"chebi": None, "pubchem": None},
        "acetomycin": {"chebi": None, "pubchem": None},
        "fradicin": {"chebi": None, "pubchem": None},
        "naramycin B": {"chebi": None, "pubchem": None},
        "hortesin": {"chebi": None, "pubchem": None},
        "piericidin": {"chebi": None, "pubchem": None},
        "feldamycin": {"chebi": None, "pubchem": None},
        "fervenulin": {"chebi": None, "pubchem": None},
        "methylenomycin A": {"chebi": None, "pubchem": None},
        "beta-Lipomycin": {"chebi": None, "pubchem": None},
        "spectinomycin": {"chebi": "CHEBI:9215", "pubchem": "15541"},
        "streptovaricin": {"chebi": None, "pubchem": None},
        "oxamicetin": {"chebi": None, "pubchem": None},
        "lomofungin": {"chebi": None, "pubchem": None},
        "decoyinine": {"chebi": None, "pubchem": None},
        "psicofuranine": {"chebi": None, "pubchem": None},
        "neoantimycin": {"chebi": None, "pubchem": None},
        "stallimycin": {"chebi": None, "pubchem": None},
        "netropsin": {"chebi": None, "pubchem": None},
        "cladomycin": {"chebi": None, "pubchem": None},
        "tertiomycin A": {"chebi": None, "pubchem": None},
        "tertiomycin B": {"chebi": None, "pubchem": None},
        "enteromycin": {"chebi": None, "pubchem": None},
        "tuberactinamine A": {"chebi": None, "pubchem": None},
        "tuberactinomycin": {"chebi": None, "pubchem": None},
        "azacolutin": {"chebi": None, "pubchem": None},
        "porfiromycin": {"chebi": None, "pubchem": None},
        "abikoviromycin": {"chebi": None, "pubchem": None},
        "pyrrolomycin B": {"chebi": None, "pubchem": None},
        "angustmycin": {"chebi": None, "pubchem": None},
        "lysocellin": {"chebi": None, "pubchem": None},
        "trans-styrylacetic acid": {"chebi": None, "pubchem": None},
        "hitachimycin": {"chebi": None, "pubchem": None},
        "carminomycin": {"chebi": None, "pubchem": None},
        "actinotiocin": {"chebi": None, "pubchem": None},
        "kijanimicin": {"chebi": None, "pubchem": None},
        "gelatin hydrolyzed": {"chebi": None, "pubchem": None},
        "nutriacholic acid": {"chebi": None, "pubchem": None},
        "phoslactomycin": {"chebi": None, "pubchem": None},
        "sea salts": {"chebi": None, "pubchem": None},
        "1,4-propandiol": {"chebi": None, "pubchem": None},
        "2,4-butanediol": {"chebi": None, "pubchem": None},
        "L-xanthine": {"chebi": None, "pubchem": None},
        "1-chlorobutane": {"chebi": None, "pubchem": None},
        "1-chloropropane": {"chebi": None, "pubchem": None},
        "calcium malate": {"chebi": None, "pubchem": None},
        "L-serine": {"chebi": "CHEBI:17115", "pubchem": "5951"},
        "tryptone/yeast/beef (tyb)": {"chebi": None, "pubchem": None},
        "dried grass extract": {"chebi": None, "pubchem": None},
        "ammonium": {"chebi": "CHEBI:28938", "pubchem": "223"},
        "glucose": {"chebi": "CHEBI:4167", "pubchem": "5793"},
        "natural seawater (nsw)": {"chebi": None, "pubchem": None},
        "dnase agar": {"chebi": None, "pubchem": None},
        "poly-beta-hydroxyalkanoate": {"chebi": None, "pubchem": None},
        "sucrose": {"chebi": "CHEBI:17992", "pubchem": "5988"},
        "D-saccharate": {"chebi": None, "pubchem": None},
        "3-[(4-nitrophenyl)carbamoylamino]propanoic acid": {"chebi": None, "pubchem": None},
        "5-bromo-3-indolyl nonanoate": {"chebi": None, "pubchem": None},
        "L-asparagin": {"chebi": None, "pubchem": None},
        "L-arabito": {"chebi": None, "pubchem": None},
        "grisemycin": {"chebi": None, "pubchem": None},
        "acetylsalicylate": {"chebi": None, "pubchem": None},
        "o-xylene": {"chebi": None, "pubchem": None},
        "fluostatin B": {"chebi": None, "pubchem": None},
        "fluostatin C": {"chebi": None, "pubchem": None},
        "guar gum": {"chebi": None, "pubchem": None},
        "karaya gum": {"chebi": None, "pubchem": None},
        "keratin": {"chebi": None, "pubchem": None},
        "transvalencin A": {"chebi": None, "pubchem": None},
        "transvalencin Z": {"chebi": None, "pubchem": None},
        "2'-isopentenylsaproxanthin": {"chebi": None, "pubchem": None},
        "4,4-dihydroxy-biphenyl": {"chebi": None, "pubchem": None},
        "potassium hydrogen phthalate": {"chebi": None, "pubchem": None},
        "tallysomycin A": {"chebi": None, "pubchem": None},
        "tallysomycin B": {"chebi": None, "pubchem": None},
        "potassium 2-ketogluconate": {"chebi": None, "pubchem": None},
        "miharamycin A": {"chebi": None, "pubchem": None},
        "miharamycin B": {"chebi": None, "pubchem": None},
        "plumbemycin A": {"chebi": None, "pubchem": None},
        "plumbemycin B": {"chebi": None, "pubchem": None},
        "senfolomycin A": {"chebi": None, "pubchem": None},
        "senfolomycin B": {"chebi": None, "pubchem": None},
        "cephamycin A": {"chebi": None, "pubchem": None},
        "cephamycin B": {"chebi": None, "pubchem": None},
        "ascamycin": {"chebi": None, "pubchem": None},
        "dealanylascamycin": {"chebi": None, "pubchem": None},
        "arizonin A1": {"chebi": None, "pubchem": None},
        "arizonin B1": {"chebi": None, "pubchem": None},
        "xanthan gum": {"chebi": None, "pubchem": None},
        "serum": {"chebi": None, "pubchem": None},
        "butamine": {"chebi": None, "pubchem": None},
        "D-mannose": {"chebi": None, "pubchem": None},
        "blood": {"chebi": None, "pubchem": None},
    }

    def get_substrate_mapping(self, code: str, kit_name: Optional[str] = None) -> Optional[dict]:
        """Get substrate mapping with kit-specific context.

        Args:
            code: Well code (e.g., "GLU", "MAN")
            kit_name: Optional API kit name for context-aware mapping (e.g., "API 20E")

        Returns:
            Dictionary with substrate information or None
        """
        # Check kit-specific mappings first if kit context is provided
        if kit_name and kit_name in self.KIT_SPECIFIC_MAPPINGS:
            if code in self.KIT_SPECIFIC_MAPPINGS[kit_name]:
                return self.KIT_SPECIFIC_MAPPINGS[kit_name][code]

        # Fall back to global mapping
        return self.SUBSTRATE_MAPPINGS.get(code)

    def get_chemical_info(self, code: str, label: str, kit_name: Optional[str] = None) -> Optional[dict]:
        """Get chemical identifiers for a substrate code.

        Args:
            code: Well code (e.g., "GLU")
            label: Full label/name of the test
            kit_name: Optional API kit name for context-aware mapping

        Returns:
            Dictionary with chemical identifiers or None
        """
        # Check if it's a substrate (not an enzyme test) using kit-aware mapping
        mapping = self.get_substrate_mapping(code, kit_name)
        if mapping:
            return {
                "chebi_id": mapping.get("chebi"),
                "chebi_name": mapping.get("name"),
                "pubchem_cid": mapping.get("pubchem"),
                "pubchem_name": mapping.get("name"),
            }

        # Try to extract from label
        return self._search_by_name(label)

    def get_metabolite_info(self, metabolite_name: str, chebi_id: Optional[str | int] = None) -> dict:
        """Get metabolite identifiers with CHEBI/PubChem enrichment.

        Args:
            metabolite_name: Metabolite name
            chebi_id: Optional CHEBI ID from BacDive data (can be string or int)

        Returns:
            Dictionary with metabolite identifiers (CHEBI, PubChem)
        """
        # Convert chebi_id to string if it's an integer
        if isinstance(chebi_id, int):
            chebi_id = str(chebi_id)

        # Check if we have manual mappings for this metabolite
        if metabolite_name in self.METABOLITE_MAPPINGS:
            mapping = self.METABOLITE_MAPPINGS[metabolite_name]
            return {
                "chebi_id": mapping.get("chebi") or chebi_id,
                "chebi_name": None,  # Will be enriched during validation
                "pubchem_cid": mapping.get("pubchem"),
                "pubchem_name": None,  # Will be enriched during validation
            }

        # If we have a CHEBI ID from BacDive, use it
        if chebi_id:
            return {
                "chebi_id": chebi_id,
                "chebi_name": None,
                "pubchem_cid": None,
                "pubchem_name": None,
            }

        # No mapping found
        return {
            "chebi_id": None,
            "chebi_name": None,
            "pubchem_cid": None,
            "pubchem_name": None,
        }

    def _search_by_name(self, name: str) -> Optional[dict]:
        """Search for chemical by name (placeholder for API calls).

        Args:
            name: Chemical name

        Returns:
            Dictionary with identifiers or None
        """
        # This could be extended to query PubChem/CHEBI APIs
        # For now, return None for unmapped compounds
        return None

    def get_metpo_predicates(
        self,
        kit_category: str,
        well_code: str,
        well_type: str
    ) -> dict:
        """Get appropriate METPO predicates for positive and negative assay results.

        Args:
            kit_category: Kit category (e.g., "Carbohydrate fermentation", "Enzyme profiling")
            well_code: Well code (e.g., "GLU", "NO3", "Alkaline phosphatase")
            well_type: Well type (e.g., "chemical", "enzyme")

        Returns:
            Dictionary with positive and negative METPO predicates:
            {
                "positive": {"id": "METPO:XXXXXXX", "label": "predicate label"},
                "negative": {"id": "METPO:XXXXXXX", "label": "does not predicate label"}
            }
        """
        # Priority 1: Check for well code override (most specific)
        if well_code in self.METPO_PREDICATE_MAPPINGS.get("_well_code_overrides", {}):
            return self.METPO_PREDICATE_MAPPINGS["_well_code_overrides"][well_code]

        # Priority 2: Check for well type override (enzyme vs chemical)
        if well_type == "enzyme":
            return self.METPO_PREDICATE_MAPPINGS["_well_type_overrides"]["enzyme"]

        # Priority 3: Check kit category
        if kit_category in self.METPO_PREDICATE_MAPPINGS:
            return self.METPO_PREDICATE_MAPPINGS[kit_category]

        # Priority 4: Determine chemical type (fermentation vs utilization)
        if well_type == "chemical":
            if "fermentation" in kit_category.lower():
                return self.METPO_PREDICATE_MAPPINGS["_well_type_overrides"]["chemical_fermentation"]
            else:
                return self.METPO_PREDICATE_MAPPINGS["_well_type_overrides"]["chemical_utilization"]

        # Default: assimilates/does not assimilate
        return {
            "positive": {"id": "METPO:2000002", "label": "assimilates"},
            "negative": {"id": "METPO:2000027", "label": "does not assimilate"},
        }


class EnzymeMapper:
    """Map enzyme names to EC, GO, KEGG, and MetaCyc identifiers."""

    # Comprehensive enzyme activity mappings to GO/KEGG/MetaCyc
    ENZYME_ANNOTATIONS = {
        # Arylamidases - substrate-specific peptidases
        "Arginine arylamidase": {
            "go_terms": ["GO:0070006"],
            "go_names": ["metalloaminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },
        "Proline arylamidase": {
            "go_terms": ["GO:0016805"],
            "go_names": ["dipeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },
        "Leucine arylamidase": {
            "go_terms": ["GO:0004177", "GO:0070006"],
            "go_names": ["aminopeptidase activity", "metalloaminopeptidase activity"],
            "kegg_ko": "K01255",  # leucyl aminopeptidase
            "ec_number": "3.4.11.1",
        },
        "Pyroglutamic acid arylamidase": {
            "go_terms": ["GO:0017095"],
            "go_names": ["pyroglutamyl-peptidase I activity"],
            "kegg_ko": None,
            "ec_number": "3.4.19.3",
        },
        "Tyrosine arylamidase": {
            "go_terms": ["GO:0070006"],
            "go_names": ["metalloaminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },
        "Alanine arylamidase": {
            "go_terms": ["GO:0004177"],
            "go_names": ["aminopeptidase activity"],
            "kegg_ko": "K01256",  # alanyl aminopeptidase
            "ec_number": "3.4.11.2",
        },
        "Glycine arylamidase": {
            "go_terms": ["GO:0004177"],
            "go_names": ["aminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },
        "Histidine arylamidase": {
            "go_terms": ["GO:0070006"],
            "go_names": ["metalloaminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },
        "Serine arylamidase": {
            "go_terms": ["GO:0004177"],
            "go_names": ["aminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },
        "Phenylalanine arylamidase": {
            "go_terms": ["GO:0070006"],
            "go_names": ["metalloaminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },
        "Glutamyl glutamic acid arylamidase": {
            "go_terms": ["GO:0004177"],
            "go_names": ["aminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },
        "Aspartic acid arylamidase": {
            "go_terms": ["GO:0070006"],
            "go_names": ["metalloaminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },

        # Decarboxylases and dihydrolases
        "Arginine dihydrolase": {
            "go_terms": ["GO:0008792"],
            "go_names": ["arginine deiminase activity"],
            "kegg_ko": "K01478",
            "ec_number": "3.5.3.6",
        },
        "Lysine decarboxylase": {
            "go_terms": ["GO:0008923"],
            "go_names": ["lysine decarboxylase activity"],
            "kegg_ko": "K01582",
            "ec_number": "4.1.1.18",
        },
        "Ornithine decarboxylase": {
            "go_terms": ["GO:0004586"],
            "go_names": ["ornithine decarboxylase activity"],
            "kegg_ko": "K01581",
            "ec_number": "4.1.1.17",
        },

        # Peptidases
        "Leucine aminopeptidase": {
            "go_terms": ["GO:0004177", "GO:0070006"],
            "go_names": ["aminopeptidase activity", "metalloaminopeptidase activity"],
            "kegg_ko": "K01255",
            "ec_number": "3.4.11.1",
        },
        "Pyrrolidonyl arylamidase": {
            "go_terms": ["GO:0017095"],
            "go_names": ["pyroglutamyl-peptidase I activity"],
            "kegg_ko": "K01304",
            "ec_number": "3.4.19.3",
        },
        "Hippurate hydrolysis": {
            "go_terms": ["GO:0016810"],
            "go_names": ["hydrolase activity, acting on carbon-nitrogen (but not peptide) bonds"],
            "kegg_ko": None,
            "ec_number": "3.5.1.32",
        },
        "Gamma-glutamyl transferase": {
            "go_terms": ["GO:0003840"],
            "go_names": ["gamma-glutamyltransferase activity"],
            "kegg_ko": "K00681",
            "ec_number": "2.3.2.2",
        },

        # Lipases and esterases
        "Esterase": {
            "go_terms": ["GO:0016788"],
            "go_names": ["hydrolase activity, acting on ester bonds"],
            "kegg_ko": "K01066",
            "ec_number": "3.1.1.-",  # Enzyme family level (no exact match to specific esterase)
        },
        "Lipase": {
            "go_terms": ["GO:0004806"],
            "go_names": ["triglyceride lipase activity"],
            "kegg_ko": "K01046",
            "ec_number": "3.1.1.3",
        },
        "Phospholipase": {
            "go_terms": ["GO:0004620"],
            "go_names": ["phospholipase activity"],
            "kegg_ko": "K01114",
            "ec_number": "3.1.1.32",
        },

        # Glycosidases
        "β-galactosidase": {
            "go_terms": ["GO:0004565"],
            "go_names": ["beta-galactosidase activity"],
            "kegg_ko": "K01190",
            "ec_number": "3.2.1.23",
        },
        "β-galactosidase (PNPG)": {
            "go_terms": ["GO:0004565"],
            "go_names": ["beta-galactosidase activity"],
            "kegg_ko": "K01190",
            "ec_number": "3.2.1.23",
        },
        "α-galactosidase": {
            "go_terms": ["GO:0004557"],
            "go_names": ["alpha-galactosidase activity"],
            "kegg_ko": "K07407",
            "ec_number": "3.2.1.22",
        },
        "α-galactosidase (Mannosidase)": {
            "go_terms": ["GO:0004557"],
            "go_names": ["alpha-galactosidase activity"],
            "kegg_ko": "K07407",
            "ec_number": "3.2.1.22",
        },
        "β-glucuronidase": {
            "go_terms": ["GO:0004566"],
            "go_names": ["beta-glucuronidase activity"],
            "kegg_ko": "K01195",
            "ec_number": "3.2.1.31",
        },

        # Oxidoreductases
        "Catalase": {
            "go_terms": ["GO:0004096"],
            "go_names": ["catalase activity"],
            "kegg_ko": "K03781",
            "ec_number": "1.11.1.6",
        },
        "Cytochrome oxidase": {
            "go_terms": ["GO:0004129"],
            "go_names": ["cytochrome-c oxidase activity"],
            "kegg_ko": "K02274",
            "ec_number": "1.9.3.1",
        },
        "Nitrate reductase": {
            "go_terms": ["GO:0008940"],
            "go_names": ["nitrate reductase activity"],
            "kegg_ko": "K00370",
            "ec_number": "1.7.99.4",
        },

        # Hydrolases
        "Urease": {
            "go_terms": ["GO:0009039"],
            "go_names": ["urease activity"],
            "kegg_ko": "K01428",
            "ec_number": "3.5.1.5",
        },
        "Gelatinase": {
            "go_terms": ["GO:0004222"],
            "go_names": ["metalloendopeptidase activity"],
            "kegg_ko": "K01398",
            "ec_number": "3.4.24.4",
        },
        "Pyrazinamidase": {
            "go_terms": ["GO:0050336"],
            "go_names": ["pyrazinamidase activity"],
            "kegg_ko": None,
            "ec_number": "3.5.1.19",
        },

        # Lyases
        "Phenylalanine deaminase": {
            "go_terms": ["GO:0004664"],
            "go_names": ["phenylalanine ammonia-lyase activity"],
            "kegg_ko": "K10775",
            "ec_number": "4.3.1.24",
        },
        "Tryptophan deaminase": {
            "go_terms": ["GO:0006569"],
            "go_names": ["tryptophan catabolic process"],
            "kegg_ko": None,
            "ec_number": "4.1.99.1",
        },

        # Other enzymes
        "Alanine-phenylalanine-proline arylamidase": {
            "go_terms": ["GO:0004177"],
            "go_names": ["aminopeptidase activity"],
            "kegg_ko": None,
            "ec_number": None,
        },

        # Common enzymes from BacDive data (various capitalizations)
        "alkaline phosphatase": {
            "go_terms": ["GO:0004035"],
            "go_names": ["alkaline phosphatase activity"],
            "kegg_ko": "K01077",
            "ec_number": "3.1.3.1",
        },
        "Alkaline phosphatase": {
            "go_terms": ["GO:0004035"],
            "go_names": ["alkaline phosphatase activity"],
            "kegg_ko": "K01077",
            "ec_number": "3.1.3.1",
        },
        "acid phosphatase": {
            "go_terms": ["GO:0003993"],
            "go_names": ["acid phosphatase activity"],
            "kegg_ko": "K01078",
            "ec_number": "3.1.3.2",
        },
        "Acid phosphatase": {
            "go_terms": ["GO:0003993"],
            "go_names": ["acid phosphatase activity"],
            "kegg_ko": "K01078",
            "ec_number": "3.1.3.2",
        },
        "beta-galactosidase": {
            "go_terms": ["GO:0004565"],
            "go_names": ["beta-galactosidase activity"],
            "kegg_ko": "K01190",
            "ec_number": "3.2.1.23",
        },
        "alpha-galactosidase": {
            "go_terms": ["GO:0004557"],
            "go_names": ["alpha-galactosidase activity"],
            "kegg_ko": "K07407",
            "ec_number": "3.2.1.22",
        },
        "alpha-glucosidase": {
            "go_terms": ["GO:0004558"],
            "go_names": ["alpha-glucosidase activity"],
            "kegg_ko": "K01187",
            "ec_number": "3.2.1.20",
        },
        "beta-glucosidase": {
            "go_terms": ["GO:0008422"],
            "go_names": ["beta-glucosidase activity"],
            "kegg_ko": "K01188",
            "ec_number": "3.2.1.21",
        },
        "N-acetyl-beta-glucosaminidase": {
            "go_terms": ["GO:0004563"],
            "go_names": ["beta-N-acetylhexosaminidase activity"],
            "kegg_ko": "K01207",
            "ec_number": "3.2.1.52",
        },
        "urease": {
            "go_terms": ["GO:0009039"],
            "go_names": ["urease activity"],
            "kegg_ko": "K01428",
            "ec_number": "3.5.1.5",
        },
        "catalase": {
            "go_terms": ["GO:0004096"],
            "go_names": ["catalase activity"],
            "kegg_ko": "K03781",
            "ec_number": "1.11.1.6",
        },
        "cytochrome oxidase": {
            "go_terms": ["GO:0004129"],
            "go_names": ["cytochrome-c oxidase activity"],
            "kegg_ko": "K02274",
            "ec_number": "1.9.3.1",
        },
        "gelatinase": {
            "go_terms": ["GO:0004222"],
            "go_names": ["metalloendopeptidase activity"],
            "kegg_ko": "K01398",
            "ec_number": "3.4.24.4",
        },
        "alcohol dehydrogenase": {
            "go_terms": ["GO:0004022"],
            "go_names": ["alcohol dehydrogenase (NAD+) activity"],
            "kegg_ko": "K00001",
            "ec_number": "1.1.1.1",
        },
        "alanine arylamidase": {
            "go_terms": ["GO:0004177"],
            "go_names": ["aminopeptidase activity"],
            "kegg_ko": "K01256",
            "ec_number": "3.4.11.2",
        },
        "chitinase": {
            "go_terms": ["GO:0004568"],
            "go_names": ["chitinase activity"],
            "kegg_ko": "K01183",
            "ec_number": "3.2.1.14",
        },
        "amylase": {
            "go_terms": ["GO:0004556"],
            "go_names": ["alpha-amylase activity"],
            "kegg_ko": "K01176",
            "ec_number": "3.2.1.1",
        },
        "xylanase": {
            "go_terms": ["GO:0031176"],
            "go_names": ["endo-1,4-beta-xylanase activity"],
            "kegg_ko": "K01181",
            "ec_number": "3.2.1.8",
        },
        # API zym enzymes (note space after dash: "alpha- ")
        "Trypsin": {
            "go_terms": ["GO:0004252"],
            "go_names": ["serine-type endopeptidase activity"],
            "kegg_ko": "K01312",
            "ec_number": "3.4.21.4",
        },
        "alpha- Chymotrypsin": {
            "go_terms": ["GO:0004252"],
            "go_names": ["serine-type endopeptidase activity"],
            "kegg_ko": "K01311",
            "ec_number": "3.4.21.1",
        },
        "Esterase Lipase": {
            "go_terms": ["GO:0052689"],
            "go_names": ["carboxylic ester hydrolase activity"],
            "kegg_ko": "K01066",
            "ec_number": "3.1.1.1",
        },
        "Valine arylamidase": {
            "go_terms": ["GO:0070006"],
            "go_names": ["metalloaminopeptidase activity"],
            "kegg_ko": "K01255",
            "ec_number": "3.4.11.6",
        },
        "Cystine arylamidase": {
            "go_terms": ["GO:0008234"],
            "go_names": ["cysteine-type peptidase activity"],
            "kegg_ko": None,
            "ec_number": "3.4.22.-",
        },
        "Naphthol-AS-BI-phosphohydrolase": {
            "go_terms": ["GO:0004035"],
            "go_names": ["alkaline phosphatase activity"],
            "kegg_ko": "K01077",
            "ec_number": "3.1.3.1",
        },
        "alpha- Galactosidase": {
            "go_terms": ["GO:0004557"],
            "go_names": ["alpha-galactosidase activity"],
            "kegg_ko": "K07407",
            "ec_number": "3.2.1.22",
        },
        "beta- Galactosidase": {
            "go_terms": ["GO:0004565"],
            "go_names": ["beta-galactosidase activity"],
            "kegg_ko": "K01190",
            "ec_number": "3.2.1.23",
        },
        "beta- Glucuronidase": {
            "go_terms": ["GO:0004566"],
            "go_names": ["beta-glucuronidase activity"],
            "kegg_ko": "K01195",
            "ec_number": "3.2.1.31",
        },
        "alpha- Glucosidase": {
            "go_terms": ["GO:0004558"],
            "go_names": ["alpha-glucosidase activity"],
            "kegg_ko": "K01187",
            "ec_number": "3.2.1.20",
        },
        "beta- Glucosidase": {
            "go_terms": ["GO:0008422"],
            "go_names": ["beta-glucosidase activity"],
            "kegg_ko": "K05349",
            "ec_number": "3.2.1.21",
        },
        "N-acetyl-beta- glucosaminidase": {
            "go_terms": ["GO:0004563"],
            "go_names": ["beta-N-acetylhexosaminidase activity"],
            "kegg_ko": "K01207",
            "ec_number": "3.2.1.52",
        },
        "alpha- Mannosidase": {
            "go_terms": ["GO:0004559"],
            "go_names": ["alpha-mannosidase activity"],
            "kegg_ko": "K01191",
            "ec_number": "3.2.1.24",
        },
        "alpha- Fucosidase": {
            "go_terms": ["GO:0004560"],
            "go_names": ["alpha-L-fucosidase activity"],
            "kegg_ko": "K01206",
            "ec_number": "3.2.1.51",
        },
    }

    def __init__(self, rhea_cache_file: str = "rhea_cache.json"):
        """Initialize enzyme mapper with persistent disk caching.

        Args:
            rhea_cache_file: Path to RHEA cache file for deterministic lookups
        """
        self._rhea_cache_file = rhea_cache_file
        self._rhea_cache: dict[str, list[str]] = {}
        self._go_cache: dict[str, dict] = {}

        # Load RHEA cache from disk if it exists (DETERMINISTIC)
        self._load_rhea_cache()

    def _load_rhea_cache(self) -> None:
        """Load RHEA cache from disk for deterministic lookups."""
        try:
            if Path(self._rhea_cache_file).exists():
                with open(self._rhea_cache_file, 'r') as f:
                    self._rhea_cache = json.load(f)
                print(f"Loaded RHEA cache from {self._rhea_cache_file} ({len(self._rhea_cache)} entries)")
        except Exception as e:
            print(f"Warning: Could not load RHEA cache: {e}")
            self._rhea_cache = {}

    def _save_rhea_cache(self) -> None:
        """Save RHEA cache to disk for deterministic future lookups."""
        try:
            with open(self._rhea_cache_file, 'w') as f:
                json.dump(self._rhea_cache, f, indent=2, sort_keys=True)
            print(f"Saved RHEA cache to {self._rhea_cache_file} ({len(self._rhea_cache)} entries)")
        except Exception as e:
            print(f"Warning: Could not save RHEA cache: {e}")

    def get_rhea_reactions(self, ec_number: str) -> list[str]:
        """Get RHEA reaction IDs for an EC number (DETERMINISTIC with caching).

        Args:
            ec_number: EC number (e.g., "3.2.1.23")

        Returns:
            List of RHEA reaction IDs (from cache or API)
        """
        if not ec_number or ec_number == "":
            return []

        # EXACT MATCH lookup in cache (DETERMINISTIC)
        if ec_number in self._rhea_cache:
            return self._rhea_cache[ec_number]

        # Query RHEA API only if not in cache
        rhea_ids = self._query_rhea_api(ec_number)

        # Cache result for deterministic future lookups
        self._rhea_cache[ec_number] = rhea_ids
        self._save_rhea_cache()

        return rhea_ids

    def _query_rhea_api(self, ec_number: str) -> list[str]:
        """Query RHEA API for reactions associated with an EC number.

        Args:
            ec_number: EC number

        Returns:
            List of RHEA reaction IDs
        """
        try:
            url = f"https://www.rhea-db.org/rest/1.0/ws/reaction/ec/{ec_number}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # Extract RHEA IDs from response
                if isinstance(data, dict) and "results" in data:
                    return [str(r.get("rheaId")) for r in data["results"] if "rheaId" in r]
                elif isinstance(data, list):
                    return [str(item.get("rheaId", "")) for item in data if isinstance(item, dict)]

            # Rate limiting
            time.sleep(0.1)

        except Exception as e:
            print(f"Warning: Failed to query RHEA for EC {ec_number}: {e}")

        return []

    def get_enzyme_info(self, name: str, ec_number: Optional[str]) -> dict:
        """Get comprehensive enzyme information including GO, KEGG, MetaCyc.

        Args:
            name: Enzyme name
            ec_number: EC number if available

        Returns:
            Dictionary with enzyme identifiers (EC, GO, KEGG, MetaCyc, RHEA)
        """
        # Check if we have manual annotations for this enzyme
        annotations = self.ENZYME_ANNOTATIONS.get(name, {})

        # Use annotated EC number if available, otherwise use provided
        final_ec = annotations.get("ec_number") or ec_number

        # Get RHEA IDs if we have an EC number
        rhea_ids = []
        if final_ec:
            rhea_ids = self.get_rhea_reactions(final_ec)

        return {
            "enzyme_name": name,
            "ec_number": final_ec,
            "ec_name": self._get_ec_name(final_ec) if final_ec else None,
            "rhea_ids": rhea_ids,
            # GO terms
            "go_terms": annotations.get("go_terms", []),
            "go_names": annotations.get("go_names", []),
            # KEGG
            "kegg_ko": annotations.get("kegg_ko"),
            "kegg_reaction": annotations.get("kegg_reaction"),
            # MetaCyc
            "metacyc_reaction": annotations.get("metacyc_reaction"),
            "metacyc_pathway": annotations.get("metacyc_pathway", []),
        }

    def _get_ec_name(self, ec_number: str) -> Optional[str]:
        """Get EC enzyme name (placeholder for future implementation).

        Args:
            ec_number: EC number

        Returns:
            EC enzyme name or None
        """
        # Could be extended to query enzyme databases
        return None


def normalize_well_code(code: str) -> str:
    """Normalize well codes for consistency.

    NOTE: This normalization is DETERMINISTIC but NOT an exact match.
    It's only used as a fallback when exact matching fails.

    Args:
        code: Raw well code

    Returns:
        Normalized well code (uppercase, no special chars)
    """
    # Remove special characters and standardize - DETERMINISTIC transformation
    normalized = code.strip().upper()
    normalized = re.sub(r'[^A-Z0-9]', '', normalized)
    return normalized
