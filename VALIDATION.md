# Validation System for Curated Mappings

## Overview

All curated identifier mappings (CHEBI, PubChem, EC, GO, KEGG) are validated against authoritative sources to ensure accuracy and consistency.

## Validation Strategy

### Priority 1: Ontology Files (Fast, Offline)
Validates identifiers using TSV files from **KG-Microbe** ontology directory:
- **CHEBI**: `/kg-microbe/data/transformed/ontologies/chebi_nodes.tsv` (223,125 terms, 73 MB)
- **EC**: `/kg-microbe/data/transformed/ontologies/ec_nodes.tsv` (249,191 terms, 12 MB)
- **GO**: `/kg-microbe/data/transformed/ontologies/go_nodes.tsv` (51,882 terms, 20 MB)

### Priority 2: Web APIs (Slow, Online)
For identifiers not in ontology files:
- **PubChem**: [https://pubchem.ncbi.nlm.nih.gov/rest/pug](https://pubchem.ncbi.nlm.nih.gov/rest/pug)
- **KEGG**: [https://rest.kegg.jp](https://rest.kegg.jp)

## Running Validation

### Fast Validation (Recommended)
Validates CHEBI, EC, and GO using local ontology files (~5 seconds):

```bash
make validate
# or
uv run validate-fast
```

### Full Validation (Complete)
Validates all databases including PubChem and KEGG API calls (~20 minutes):

```bash
make validate-full
# or
uv run validate-mappings
```

### Track File Versions Only
Generate SHA256 hashes of ontology files for version control:

```bash
make track-files
```

### One-Time Fix Application (Optional)
For the initial cleanup, a utility script is available in `scripts/apply_fixes.py`:

```bash
uv run python3 scripts/apply_fixes.py
```

**Note**: This is a **one-time utility** for the initial data cleanup. After fixes are applied and validated:
1. Corrected values should be updated in the source Google Sheets
2. Future data updates will come from the corrected sheets
3. This script does not need to be run again

**What it does**:
- Creates automatic backup of `mappers.py`
- Applies 11 fixes (3 critical errors + 8 deprecated terms)
- Generates `FINAL_FIXED_MAPPING_STATS.md` report
- Shows summary of all changes

## Output Files

### `validation_report.json`
Complete validation results:

```json
{
  "statistics": {
    "substrates_total": 86,
    "chebi_valid": 81,
    "enzymes_total": 54,
    "ec_valid": 39,
    "go_valid": 55
  },
  "errors": [
    "CHEBI ID not found: CHEBI:17991"
  ],
  "warnings": [
    "CHEBI ID deprecated: CHEBI:42118"
  ],
  "summary": {
    "total_errors": 3,
    "total_warnings": 8,
    "valid": false
  }
}
```

### `ontology_file_metadata.json`
SHA256 hashes and metadata for version control:

```json
{
  "chebi_nodes.tsv": {
    "path": "/path/to/chebi_nodes.tsv",
    "sha256": "b21586dc99ad144a7dcdbc74ffcfce4c7d0f92f31ed0909b91ea304afe365363",
    "size_bytes": 76502154,
    "size_human": "73.0 MB",
    "modified_time": 1756772653.2901866
  }
}
```

## Current Validation Results

**Date**: 2025-11-17
**Status**: ⚠️ **3 errors, 8 warnings**

### Errors (Invalid IDs)

| ID | Type | Substrate | Status | Recommended Action |
|----|------|-----------|--------|-------------------|
| `CHEBI:17991` | CHEBI | 5-Ketogluconic acid | ❌ Not found | Find correct CHEBI ID |
| `CHEBI:17004` | CHEBI | D-Tagatose | ❌ Not found | Find correct CHEBI ID |
| `CHEBI:495083` | CHEBI | Cyclodextrin | ❌ Not found | Find correct CHEBI ID |

### Warnings (Deprecated Terms)

| ID | Type | Entity | Status | Action Needed |
|----|------|--------|--------|---------------|
| `CHEBI:42118` | CHEBI | Dulcitol | ⚠️ Deprecated | Consider updating |
| `CHEBI:12301` | CHEBI | Unknown | ⚠️ Deprecated | Consider updating |
| `GO:0003840` | GO | gamma-glutamyltransferase | ⚠️ Obsolete | Update to current term |
| `1.9.3.1` | EC | Cytochrome-c oxidase | ⚠️ Deprecated | Update to current EC |
| `1.7.99.4` | EC | Nitrate reductase | ⚠️ Deprecated | Update to current EC |
| `3.4.24.4` | EC | Pseudolysin | ⚠️ Deprecated | Update to current EC |

**Note**: Warnings indicate deprecated but still resolvable identifiers. Errors indicate identifiers that cannot be found and must be corrected.

## Code Organization

### Validation Scripts

| File | Purpose | Entry Point |
|------|---------|-------------|
| `validate_mappings.py` | Full validation with API calls | `uv run validate-mappings` |
| `validate_fast.py` | Fast validation (ontology files only) | `uv run validate-fast` |

### Key Classes

#### `OntologyIndex`
- Loads TSV files into memory for fast lookup
- Parses CHEBI, EC, GO node files
- Provides `lookup(term_id)` method

```python
# Usage
index = OntologyIndex(Path("chebi_nodes.tsv"))
term = index.lookup("CHEBI:17234")  # Returns dict or None
```

#### `MappingValidator`
- Validates all curated mappings
- Reports errors and warnings
- Generates JSON reports

```python
# Usage
validator = MappingValidator(ontology_dir)
validator.validate_substrate_mappings()
validator.validate_enzyme_mappings()
success = validator.print_report()
```

### Validation Methods

| Method | Database | Source | Deterministic |
|--------|----------|--------|---------------|
| `validate_chebi(id)` | CHEBI | TSV file | ✅ Yes |
| `validate_ec(ec_number)` | EC | TSV file | ✅ Yes |
| `validate_go(go_id)` | GO | TSV file | ✅ Yes |
| `validate_pubchem(cid)` | PubChem | API | ⚠️ Network-dependent |
| `validate_kegg_ko(ko)` | KEGG | API | ⚠️ Network-dependent |

## Version Control Strategy

### Ontology Files (Large, External)
**DO NOT** commit to git (73 MB + 20 MB + 12 MB = 105 MB total).

Instead:
1. Store SHA256 hash in `ontology_file_metadata.json` ✅
2. Document file source and version ✅
3. Commit metadata JSON to git ✅

### Reference Data Location
```
/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/kg-microbe/data/transformed/ontologies/
├── chebi_nodes.tsv (73 MB) - SHA256: b21586dc99ad144a7dcdbc74ffcfce4c7d0f92f31ed0909b91ea304afe365363
├── ec_nodes.tsv (12 MB)    - SHA256: 03d750c44eb04f487f98153d827fbd17357024200a20f8ecf9348bdb6544fba9
└── go_nodes.tsv (20 MB)    - SHA256: 7195eba315bc6ecb2f51fa84480357a51e4569ba03289a8c1cef0c1bf3d36c69
```

**Source**: KG-Microbe ontology pipeline (September 2024)

## Integration with CI/CD

### Recommended Workflow

```bash
# Development
make validate          # Fast check during development

# Pre-commit
make validate          # Ensure no new errors

# CI Pipeline
make validate-full     # Complete validation (nightly)
```

### Exit Codes
- `0`: All mappings valid ✅
- `1`: Errors found (invalid IDs) ❌

## Fixing Validation Errors

### Example: Invalid CHEBI ID

```python
# Current (invalid)
"5KG": {"name": "5-Ketogluconic acid", "chebi": "CHEBI:17991", "pubchem": "160957"}

# Fix steps:
# 1. Search PubChem: https://pubchem.ncbi.nlm.nih.gov/compound/160957
# 2. Find correct CHEBI ID in PubChem record
# 3. Update mappers.py
# 4. Run: make validate

# Updated (valid)
"5KG": {"name": "5-Ketogluconic acid", "chebi": "CHEBI:XXXXX", "pubchem": "160957"}
```

## Statistics

| Metric | Value |
|--------|-------|
| **Substrates** | 86 total |
| CHEBI valid | 81 (94.2%) |
| CHEBI errors | 3 (3.5%) |
| CHEBI deprecated | 2 (2.3%) |
| **Enzymes** | 54 total |
| EC valid | 39 (72.2%) |
| EC deprecated | 4 (7.4%) |
| GO valid | 55 terms |
| GO deprecated | 1 (1.8%) |

## Best Practices

1. **Always run validation** before committing mapping changes
2. **Use fast validation** during development (5 sec vs 20 min)
3. **Fix errors** before warnings (errors = broken, warnings = deprecated)
4. **Update metadata** when ontology files change
5. **Document corrections** in git commit messages

## References

- **CHEBI**: [https://www.ebi.ac.uk/chebi/](https://www.ebi.ac.uk/chebi/)
- **EC**: [https://www.enzyme-database.org/](https://www.enzyme-database.org/)
- **GO**: [http://geneontology.org/](http://geneontology.org/)
- **PubChem**: [https://pubchem.ncbi.nlm.nih.gov/](https://pubchem.ncbi.nlm.nih.gov/)
- **KEGG**: [https://www.genome.jp/kegg/](https://www.genome.jp/kegg/)

---

**Last Updated**: 2025-11-17
**Next Review**: When KG-Microbe ontologies are updated
