# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BacDive API Assay Metadata Extractor - Extracts API assay metadata from BacDive bacterial database (99,392 strain records) and maps well codes to chemical/enzyme identifiers (CHEBI, PubChem, EC, RHEA, GO, KEGG).

**Key Achievement**: 100% validation coverage across all 17 API kits (503 unique well codes mapped).

## Essential Commands

### Development Setup
```bash
# Install dependencies (uses uv package manager)
uv sync

# Install in development mode
uv pip install -e .
```

### Core Workflow
```bash
# Extract metadata from BacDive JSON
make extract                    # Or: uv run extract-metadata

# Validate mappings (fast, ~5 seconds)
make validate                   # Uses local ontology files

# Validate API kit well codes against official docs
make validate-api              # 59/59 wells validated

# Validate mappings against actual extracted data
make validate-data             # 503/503 codes validated

# Complete validation (slow, ~20 minutes)
make validate-full             # Includes PubChem/KEGG API calls

# Run all validations
make all                       # extract + validate + validate-api + validate-data
```

### Testing
```bash
# Run tests
make test                      # Or: uv run pytest -v

# Track ontology file versions
make track-files
```

## Architecture Overview

### Core Pipeline
```
BacDive JSON → Parser → Chemical Mapper → Metadata Builder → JSON Output
                            ↓
                    Validation System (3 layers)
```

### Key Components

**1. Parser (`parser.py`)**
- Extracts API assay data from BacDive JSON
- Identifies 17 API kit types (API zym, API 50CHac, API 20E, etc.)
- Processes 99,392 bacterial strain records
- Extracts well codes and test results

**2. Chemical Mapper (`mappers.py`)** - **CRITICAL FILE**
- **503 well codes mapped** across 4 dictionaries:
  - `SUBSTRATE_MAPPINGS`: Chemicals with CHEBI/PubChem IDs (89 entries)
  - `ENZYME_TESTS`: Enzyme activity tests (16 entries)
  - `ENZYME_ACTIVITY_TESTS`: Glycosidases, arylamidases (51 entries)
  - `PHENOTYPIC_TESTS`: Non-enzymatic tests (10 entries)
- **Kit-Specific Mappings** (`KIT_SPECIFIC_MAPPINGS`): Context-aware mappings
  - Handles codes that mean different things in different kits
  - Example: "MAN" = D-Mannose in API 20E, D-Mannitol in API 20NE
- `get_substrate_mapping(code, kit_name)`: Context-aware lookup
- `get_chemical_info()`: Retrieves identifiers for substrates
- `get_enzyme_info()`: Maps enzymes to EC numbers and RHEA reactions

**3. Validation System (3-Layer Approach)**

**Layer 1: Ontology Validation** (`validate_fast.py`, `validate_mappings.py`)
- Validates CHEBI, EC, GO identifiers against KG-Microbe ontology files
- Fast validation: `make validate` (~5 sec)
- Full validation: `make validate-full` (~20 min, includes API calls)

**Layer 2: Official Documentation Validation** (`validate_api_kits.py`)
- Cross-references mappings with bioMérieux official API kit documentation
- Validates 59 wells from API 20E, API 20NE, API zym kits
- Uses kit-specific context for accurate validation
- Command: `make validate-api`

**Layer 3: Data-Driven Validation** (`validate_against_data.py`)
- Validates mappings against actual extracted BacDive data
- Checks all 503 unique well codes across 17 kits
- Identifies unmapped codes in real-world usage
- Command: `make validate-data`

**4. Metadata Builder (`metadata_builder.py`)**
- Consolidates well codes across all strains
- Links chemicals to multiple API kits
- Generates final JSON outputs

### Critical Design Patterns

**Kit-Specific Context System**
```python
# Problem: "MAN" means different things in different kits
# Solution: Kit-specific mappings with fallback to global defaults

KIT_SPECIFIC_MAPPINGS = {
    "API 20E": {
        "MAN": {"name": "D-Mannose", "chebi": "CHEBI:4208"}
    },
    "API 20NE": {
        "MAN": {"name": "D-Mannitol", "chebi": "CHEBI:16899"}
    }
}

# Usage
mapping = mapper.get_substrate_mapping("MAN", kit_name="API 20E")
```

**Multi-Dictionary Lookup Strategy**
When mapping a well code, check dictionaries in order:
1. `KIT_SPECIFIC_MAPPINGS[kit_name][code]` (if kit context known)
2. `SUBSTRATE_MAPPINGS[code]`
3. `ENZYME_TESTS[code]`
4. `ENZYME_ACTIVITY_TESTS[code]`
5. `PHENOTYPIC_TESTS[code]`

## Data Flow

```
Input: bacdive_strains.json (835 MB)
   ↓
Parser extracts API assay data
   ↓
Chemical Mapper resolves well codes → CHEBI/PubChem/EC IDs
   ↓
Metadata Builder consolidates across strains
   ↓
Output: data/assay_metadata.json (596 KB)
        data/api_kits_list.json (12 KB)
        data/assay_kits_simple.json (421 KB)
```

## Important Files

**Source Files (Edit These)**
- `src/bacdive_assay_metadata/mappers.py` - All well code mappings
  - Primary source of truth for substrate/enzyme mappings
  - Update Google Sheets first, then export to this file

**Validation Outputs (Read These)**
- `validation_report.json` - Ontology validation results
- `api_kit_validation_report.json` - Official docs validation (59 wells)
- `data_validation_report.json` - Data-driven validation (503 codes)
- `ontology_file_metadata.json` - Ontology file hashes for version control

**Reference Documentation**
- `API_WELL_CODE_SOURCES.md` - How well codes are verified (e.g., GLU = glucose not glutamate)
- `VALIDATION.md` - Validation system details
- `WORKFLOW.md` - Complete data workflow (Google Sheets → Code → Validation)

## Working with Mappings

### Adding New Substrate Mappings
1. Add to `SUBSTRATE_MAPPINGS` in `mappers.py`:
```python
"CODE": {
    "name": "Chemical Name",
    "chebi": "CHEBI:XXXXX",
    "pubchem": "XXXXXX"
}
```
2. Run `make validate` to check identifiers
3. Run `make validate-data` to verify against extracted data

### Adding Kit-Specific Mappings
For codes that mean different things in different kits:
```python
KIT_SPECIFIC_MAPPINGS = {
    "API Kit Name": {
        "CODE": {"name": "...", "chebi": "CHEBI:..."}
    }
}
```

### Adding Enzyme Mappings
For enzyme activity tests:
```python
ENZYME_ACTIVITY_TESTS = {
    "CODE": "Enzyme Name"
}
```

## API Kit Types (17 Total)

All kits have 100% mapping coverage:

| Kit | Strains | Wells | Type |
|-----|---------|-------|------|
| API zym | 11,747 | 20 | Enzyme profiling |
| API 50CHac | 6,853 | 49 | Carbohydrate fermentation |
| API biotype100 | 3,599 | 99 | Carbon source assimilation |
| API rID32STR | 3,666 | 32 | Bacterial identification |
| API 20NE | 3,833 | 21 | Non-Enterobacteriaceae ID |
| API 20E | 3,452 | 19 | Enterobacteriaceae ID |
| API coryne | 3,287 | 21 | Corynebacterium ID |
| API rID32A | 2,198 | 29 | Anaerobe ID |
| API ID32E | 1,438 | 32 | Enterobacteriaceae ID |
| API NH | 1,407 | 13 | Neisseria/Haemophilus ID |
| API ID32STA | 839 | 26 | Staphylococcus ID |
| API CAM | 370 | 21 | Campylobacter ID |
| API 20STR | 311 | 20 | Streptococcus ID |
| API LIST | 270 | 10 | Listeria ID |
| API STA | 220 | 20 | Staphylococcus ID |
| API 20A | 185 | 21 | Anaerobe ID |
| API 50CHas | 13 | 50 | Carbohydrate assimilation |

## Validation Coverage

- **Ontology IDs**: 81/84 CHEBI (96.4%), 39/39 EC (100%), 55 GO terms
- **Official Docs**: 59/59 wells (100%) - API 20E, 20NE, API zym
- **Data-Driven**: 503/503 codes (100%) - All 17 kits

## Common Issues

**Issue**: "Well code not found in mappings"
**Solution**: Add to appropriate dictionary in `mappers.py`, check if kit-specific context needed

**Issue**: "CHEBI ID not found" validation error
**Solution**: Verify ID exists at https://www.ebi.ac.uk/chebi/, update in `mappers.py`

**Issue**: "Kit validation shows mismatch"
**Solution**: Check if code is context-dependent, add to `KIT_SPECIFIC_MAPPINGS`

**Issue**: "Data validation shows unmapped codes"
**Solution**: Run `make validate-data` to identify codes, add mappings, re-validate

## Development Notes

- Uses `uv` for fast Python package management (not pip/conda)
- Python 3.12+ required
- Validation before commits is mandatory
- Update Google Sheets (source of truth) before editing `mappers.py`
- Kit-specific context critical for accurate mappings
- All validation reports are auto-generated, don't edit manually
