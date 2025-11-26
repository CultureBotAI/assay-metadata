# BacDive API Assay Metadata Extractor

Extract API assay metadata from BacDive JSON data with comprehensive identifier mappings to CHEBI, EC, RHEA, and PubChem databases.

## Overview

This project analyzes the BacDive bacterial database JSON file to extract:

1. **API Assay Kits** - All 17 API assay kit types found in the data
2. **Well Metadata** - Individual wells/tests with human-readable labels
3. **Identifier Mappings** - Links to CHEBI, PubChem, EC numbers, and RHEA reactions
4. **Enzyme Information** - Enzyme activities with EC classifications

## Features

- ✅ Parses 99,392 bacterial strain records from BacDive
- ✅ Extracts 17 unique API kit types (API zym, API 50CHac, etc.)
- ✅ Maps substrate codes to CHEBI and PubChem identifiers
- ✅ Maps enzyme EC numbers to RHEA reaction databases
- ✅ Generates consolidated JSON metadata files
- ✅ Optional split output for individual API kits
- ✅ Comprehensive statistics and summaries

## Installation

This project uses **uv** for fast, reliable Python package management.

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Dependencies

```bash
# Create virtual environment and install dependencies
uv sync

# Or install in development mode
uv pip install -e .
```

## Usage

### Basic Usage

```bash
# Extract metadata from default location (bacdive_strains.json)
uv run extract-metadata

# Or activate the virtual environment first
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate     # Windows
extract-metadata
```

### Advanced Options

```bash
# Specify custom input file
uv run extract-metadata --input path/to/bacdive_strains.json

# Specify custom output directory
uv run extract-metadata --output-dir processed_data/

# Generate individual files for each API kit
uv run extract-metadata --split-kits

# Pretty-print JSON output (indented)
uv run extract-metadata --pretty

# Combine options
uv run extract-metadata --input bacdive_strains.json \
                        --output-dir data/ \
                        --split-kits \
                        --pretty
```

## Validation

All curated identifier mappings are validated against authoritative sources and actual extracted data. See **[VALIDATION.md](VALIDATION.md)** and **[API_WELL_CODE_SOURCES.md](API_WELL_CODE_SOURCES.md)** for complete details.

### Quick Validation

```bash
# Fast validation using ontology files (~5 seconds)
make validate

# Validate API kit well code mappings against official docs
make validate-api

# Validate mappings against actual extracted data
make validate-data

# Full validation with API calls (~20 minutes)
make validate-full

# Track ontology file versions
make track-files
```

### Validation Sources

| Database | Source | Method |
|----------|--------|--------|
| **CHEBI** | KG-Microbe ontology TSV | Offline lookup |
| **EC** | KG-Microbe ontology TSV | Offline lookup |
| **GO** | KG-Microbe ontology TSV | Offline lookup |
| **PubChem** | PubChem API | Online validation |
| **KEGG** | KEGG API | Online validation |
| **bioMérieux Docs** | Official API kit documentation | Manual curation |

### Validation Coverage

**Ontology Identifiers**: 81/84 CHEBI valid (96.4%), 39/39 EC valid (100%), 55 GO terms valid

**API Kit Well Code Mappings**:
- **100% coverage** across all 17 API kits
- **503/503 well codes** mapped (data-driven validation)
- **59/59 wells** validated against official bioMérieux documentation
- All kits: API zym, API 50CHac, API biotype100, API 20E, API 20NE, API rID32STR, API coryne, API rID32A, API ID32E, API NH, API ID32STA, API CAM, API 20STR, API LIST, API STA, API 20A, API 50CHas

See [VALIDATION.md](VALIDATION.md) for:
- Detailed validation results
- Error and warning details
- Instructions for fixing invalid IDs
- Version control strategy for ontology files

See [API_WELL_CODE_SOURCES.md](API_WELL_CODE_SOURCES.md) for:
- How well codes are verified against official sources
- Kit-specific context for ambiguous codes
- Cross-kit consistency analysis

## Output Files

### Default Output (`data/`)

1. **`assay_metadata.json`** - Consolidated metadata for all API kits, wells, and enzymes
2. **`api_kits_list.json`** - Summary list of all 17 API kit types
3. **`statistics.json`** - Dataset statistics

### With `--split-kits` Option

Additional directory `data/kits/` containing individual JSON files for each kit:
- `API_zym.json`
- `API_50CHac.json`
- `API_20NE.json`
- ... (one file per kit)

## Output Schema

### API Kit Metadata

```json
{
  "kit_name": "API zym",
  "description": "Enzyme activity testing for 19 different enzymes",
  "category": "Enzyme profiling",
  "well_count": 20,
  "wells": ["Control", "Alkaline phosphatase", "Esterase", ...],
  "occurrence_count": 11747
}
```

### Well Metadata

```json
{
  "code": "GLU",
  "label": "D-Glucose",
  "well_type": "substrate",
  "description": "Tests for utilization/fermentation of D-Glucose",
  "chemical_ids": {
    "chebi_id": "CHEBI:17234",
    "chebi_name": "D-Glucose",
    "pubchem_cid": "5793",
    "pubchem_name": "D-Glucose"
  },
  "used_in_kits": ["API 50CHac", "API biotype100", "API 20E"]
}
```

### Enzyme Metadata

```json
{
  "enzyme_name": "beta-galactosidase",
  "ec_number": "3.2.1.23",
  "ec_name": null,
  "rhea_ids": ["10079", "10080", "10081"]
}
```

## API Kit Types Found

The extractor identifies 17 different API assay kits:

| Kit Name | Type | Well Count | Occurrences |
|----------|------|------------|-------------|
| API zym | Enzyme profiling | 20 | 11,747 |
| API 50CHac | Carbohydrate fermentation | 50 | 6,853 |
| API 20NE | Bacterial identification | 21 | 3,833 |
| API rID32STR | Bacterial identification | 32 | 3,666 |
| API biotype100 | Biochemical profiling | 99 | 3,599 |
| API 20E | Bacterial identification | 26 | 3,452 |
| API coryne | Bacterial identification | varies | 3,287 |
| ... | ... | ... | ... |

## Project Structure

```
assay-metadata/
├── src/bacdive_assay_metadata/
│   ├── __init__.py           # Package initialization
│   ├── models.py             # Pydantic data models
│   ├── parser.py             # BacDive JSON parser
│   ├── mappers.py            # Identifier mapping utilities
│   ├── metadata_builder.py  # Metadata construction
│   └── main.py               # CLI entry point
├── data/                     # Output directory (generated)
├── bacdive_strains.json      # Input data file
├── pyproject.toml            # Project configuration
├── .python-version           # Python version specification
└── README.md                 # This file
```

## Development

### Running Tests

```bash
# Install dev dependencies
uv sync --dev

# Run tests (when implemented)
uv run pytest
```

### Code Structure

- **`models.py`** - Pydantic models for type-safe data structures
- **`parser.py`** - Extracts API assay data from BacDive JSON
- **`mappers.py`** - Maps codes to biological database identifiers
- **`metadata_builder.py`** - Orchestrates parsing and mapping
- **`main.py`** - Command-line interface

## Identifier Mapping Coverage

### Chemical Identifiers (CHEBI/PubChem)

- ✅ Monosaccharides: glucose, fructose, galactose, mannose, ribose, xylose, arabinose
- ✅ Disaccharides: maltose, lactose, sucrose, trehalose, cellobiose, melibiose
- ✅ Sugar alcohols: sorbitol, mannitol, inositol, dulcitol, xylitol
- ✅ Organic acids: citrate, lactate, pyruvate, succinate, fumarate
- ✅ Amino acids: tryptophan, glutamine, proline, alanine, serine, tyrosine
- ✅ 100+ substrate mappings total

### Enzyme Identifiers (EC/RHEA)

- ✅ **EC numbers**: 129/158 enzyme wells (81.6% coverage)
  - 10 EC numbers added via deterministic lookup (ExpASy ENZYME, BRENDA)
  - Glycosidases: alpha-arabinofuranosidase, alpha-fucosidase, alpha-glucosidase, alpha-mannosidase, beta-glucosidase, beta-mannosidase, beta-N-acetylhexosaminidase, beta-galactosidase
  - Other enzymes: tryptophanase (indole production)
- ✅ RHEA reaction IDs fetched via API
- ✅ 175 unique enzymes cataloged
- ✅ GO terms for arylamidases and other enzyme activities
- ✅ All EC numbers validated against KG-Microbe EC ontology (249,191 terms)

## Data Sources

- **BacDive**: Bacterial Diversity Metadatabase (99,392 strains)
- **CHEBI**: Chemical Entities of Biological Interest
- **PubChem**: Public chemistry database
- **EC**: Enzyme Commission classification
- **RHEA**: Expert-curated biochemical reactions

## Performance

- Processes 99,392 bacterial strains
- Extracts ~17 API kit types
- Identifies ~150+ unique wells/tests
- Runtime: ~2-5 minutes (depending on system)

## License

This project is part of the KG-Microbe knowledge graph initiative.

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more substrate/chemical mappings
- [ ] Integrate EC name lookups
- [ ] Add InChI/SMILES for chemicals
- [ ] Implement caching for API calls
- [ ] Add unit tests
- [ ] Support for additional output formats (CSV, TSV)

## Citation

If you use this tool, please cite:

- **BacDive**: The Bacterial Diversity Metadatabase
- **CHEBI**: Chemical Entities of Biological Interest
- **RHEA**: Annotated reactions database

## Support

For issues or questions, please open an issue on the repository.
