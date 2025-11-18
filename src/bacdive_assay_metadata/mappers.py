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
        "MAN": {"name": "D-Mannose", "chebi": "CHEBI:4208", "pubchem": "18950"},
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

        # Polysaccharides
        "AMY": {"name": "Starch (Amylose)", "chebi": "CHEBI:28017", "pubchem": "24836924"},
        "GLYG": {"name": "Glycogen", "chebi": "CHEBI:28087", "pubchem": "439177"},
        "INU": {"name": "Inulin", "chebi": "CHEBI:15443", "pubchem": "24763"},

        # Sugar alcohols
        "SOR": {"name": "D-Sorbitol", "chebi": "CHEBI:17924", "pubchem": "5780"},
        "MNE": {"name": "D-Mannitol", "chebi": "CHEBI:16899", "pubchem": "6251"},
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
        "CIT": {"name": "Citric acid", "chebi": "CHEBI:30769", "pubchem": "311"},
        "LAT": {"name": "Lactic acid", "chebi": "CHEBI:28358", "pubchem": "612"},
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

        # Nucleosides
        "ADI": {"name": "Adenosine", "chebi": "CHEBI:16335", "pubchem": "60961"},

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
        "AMD": {"name": "Amidon", "chebi": None, "pubchem": None},  # Alternative name for starch
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

    # Well codes that are enzyme tests, not substrates
    ENZYME_TESTS = {
        "URE": "Urease",
        "GEL": "Gelatinase",
        "PAL": "Phenylalanine deaminase",
        "IND": "Indole production",
        "VP": "Voges-Proskauer",
        "TDA Trp": "Tryptophan deaminase",
        "H2S": "Hydrogen sulfide production",
        "NIT": "Nitrate reductase",
        "NO2": "Nitrite reduction",
        "N2": "Nitrogen gas production",
        "OX": "Cytochrome oxidase",
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

    def get_chemical_info(self, code: str, label: str) -> Optional[dict]:
        """Get chemical identifiers for a substrate code.

        Args:
            code: Well code (e.g., "GLU")
            label: Full label/name of the test

        Returns:
            Dictionary with chemical identifiers or None
        """
        # Check if it's a substrate (not an enzyme test)
        if code in self.SUBSTRATE_MAPPINGS:
            mapping = self.SUBSTRATE_MAPPINGS[code]
            return {
                "chebi_id": mapping.get("chebi"),
                "chebi_name": mapping.get("name"),
                "pubchem_cid": mapping.get("pubchem"),
                "pubchem_name": mapping.get("name"),
            }

        # Try to extract from label
        return self._search_by_name(label)

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
            "ec_number": "3.1.1.1",
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
            "go_terms": ["GO:0004295"],
            "go_names": ["trypsin activity"],
            "kegg_ko": "K01312",
            "ec_number": "3.4.21.4",
        },
        "alpha- Chymotrypsin": {
            "go_terms": ["GO:0004263"],
            "go_names": ["obsolete chymotrypsin activity"],
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
