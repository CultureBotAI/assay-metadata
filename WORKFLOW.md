# BacDive Assay Metadata - Data Workflow

**Project**: KG-Microbe / BacDive Assay Metadata
**Purpose**: Document the complete data workflow from source to validated output

---

## Overview

This project extracts and validates API assay metadata from BacDive JSON data, with multi-database identifier mappings (CHEBI, PubChem, EC, GO, KEGG).

```
Google Sheets → XLSX → Python Mappings → Validation → Knowledge Graph
      ↑                                        ↓
      └────────────── Fix errors ─────────────┘
```

---

## Data Flow

### 1. Source Data (Google Sheets)
- **Location**: Google Sheets (curated by team)
- **Content**:
  - Substrate mappings (CHEBI, PubChem)
  - Enzyme annotations (EC, GO, KEGG)
  - Well codes and descriptions

### 2. Export to Code
- **Format**: XLSX or direct editing of `mappers.py`
- **Files**:
  - `src/bacdive_assay_metadata/mappers.py`
    - `SUBSTRATE_MAPPINGS` dictionary (86 entries)
    - `ENZYME_ANNOTATIONS` dictionary (54 entries)

### 3. Validation
- **Command**: `make validate`
- **Process**:
  1. Load ontology files (CHEBI, EC, GO from KG-Microbe)
  2. Validate all identifiers
  3. Generate validation report
  4. Report errors and warnings

### 4. Fix Errors
- **Where**: Google Sheets (primary source)
- **How**: Update incorrect IDs in sheets
- **Then**: Re-export to `mappers.py`

### 5. Final Output
- **Files**:
  - `data/assay_metadata.json` (standard format)
  - `data/assay_kits_simple.json` (simplified format)
  - `data/api_kits_list.json` (kit summaries)

---

## Initial Setup (One-Time)

### Step 1: Validate Initial Data
```bash
make validate
```

**Expected**: 3 errors, 8 warnings (initial dataset issues)

### Step 2: Review Validation Reports
```bash
cat notes/VALIDATION_ERRORS_DETAILED.md      # Invalid IDs
cat notes/DEPRECATED_TERMS_REPORT.md         # Deprecated terms
cat notes/FINAL_MAPPING_STATS.md             # Overall statistics
```

### Step 3: Apply One-Time Fixes (Optional)
```bash
# This creates a backup and applies all 11 fixes to mappers.py
uv run python3 scripts/apply_fixes.py
```

**Output**:
- Backup: `mappers.py.backup-{timestamp}`
- Report: `notes/FINAL_FIXED_MAPPING_STATS.md`

**Verify**:
```bash
make validate
# Expected: 0 errors, 0 warnings ✅
```

### Step 4: Update Source Google Sheets ⚠️ IMPORTANT
Copy corrected values from validation reports back to Google Sheets:

| Error | Sheet Column | Old Value | New Value |
|-------|--------------|-----------|-----------|
| 5-Ketogluconic acid | CHEBI | CHEBI:17991 | CHEBI:17426 |
| 5-Ketogluconic acid | PubChem | 160957 | 5460352 |
| D-Tagatose | CHEBI | CHEBI:17004 | CHEBI:16443 |
| Cyclodextrin | Name | Cyclodextrin | alpha-Cyclodextrin |
| Cyclodextrin | CHEBI | CHEBI:495083 | CHEBI:40585 |
| Cyclodextrin | PubChem | (empty) | 444041 |
| Dulcitol | CHEBI | CHEBI:42118 | CHEBI:16813 |
| D-Lyxose | CHEBI | CHEBI:12301 | CHEBI:62318 |
| Gamma-glutamyl transferase | GO | GO:0003840 | GO:0036374 |
| Cytochrome oxidase | EC | 1.9.3.1 | 7.1.1.9 |
| Nitrate reductase | EC | 1.7.99.4 | 1.7.5.1 |
| Gelatinase | EC | 3.4.24.4 | 3.4.24.24 |

**Why this matters**: Future exports from Google Sheets will have correct values.

---

## Regular Workflow (After Initial Setup)

### When to Run

Run this workflow when:
- Adding new substrates or enzymes
- Updating existing mappings
- Periodic data refresh from BacDive

### Steps

#### 1. Update Google Sheets
- Add new entries or update existing ones
- Ensure all required columns are filled
- Double-check identifier formats (CHEBI:XXXXX, GO:XXXXXXX, etc.)

#### 2. Export to Code
```bash
# Option A: Export XLSX and process (if you have an import script)
python import_from_xlsx.py

# Option B: Manually update mappers.py
vim src/bacdive_assay_metadata/mappers.py
```

#### 3. Validate
```bash
make validate
```

**If errors found**:
- ❌ **DO NOT** run `apply_fixes.py` again
- ✅ **DO** fix errors in Google Sheets
- ✅ Re-export and validate

**Expected**: 0 errors, 0 warnings

#### 4. Extract Metadata
```bash
make extract
```

**Output**:
- `data/assay_metadata.json`
- `data/assay_kits_simple.json`
- `data/api_kits_list.json`
- `data/statistics.json`

#### 5. Commit Changes
```bash
git add src/bacdive_assay_metadata/mappers.py
git add data/*.json
git commit -m "Update assay metadata mappings"
```

---

## Validation System

### Fast Validation (Recommended)
```bash
make validate
```
- **Time**: ~5 seconds
- **Validates**: CHEBI, EC, GO (local files)
- **Use**: During development, pre-commit

### Full Validation (Comprehensive)
```bash
make validate-full
```
- **Time**: ~20 minutes
- **Validates**: All databases (includes PubChem, KEGG API calls)
- **Use**: Before major releases, periodic checks

### Output Files
- `validation_report.json` - Detailed errors/warnings
- `ontology_file_metadata.json` - File hashes for version control

---

## Important Notes

### ✅ DO
- Update source Google Sheets when errors are found
- Run validation before committing changes
- Keep ontology file metadata tracked
- Document any new mappings

### ❌ DO NOT
- Run `apply_fixes.py` more than once (it's a one-time cleanup)
- Commit without validating first
- Ignore validation warnings
- Hard-code fixes in downstream code

---

## Error Handling

### If Validation Fails

#### 1. Invalid IDs (Errors)
**Symptom**: "CHEBI ID not found", "EC number not found"

**Solution**:
1. Check ID format (CHEBI:XXXXX, GO:XXXXXXX, EC:X.X.X.X)
2. Verify ID exists in ontology database:
   - CHEBI: https://www.ebi.ac.uk/chebi/
   - GO: http://geneontology.org/
   - EC: https://www.enzyme-database.org/
3. Update in Google Sheets
4. Re-export and validate

#### 2. Deprecated Terms (Warnings)
**Symptom**: "CHEBI ID deprecated", "GO term obsolete"

**Solution**:
1. Find replacement in validation report
2. Update in Google Sheets
3. Re-export and validate

#### 3. Missing Mappings
**Symptom**: Empty cells, None values

**Solution**:
1. Research correct identifier:
   - PubChem: Search by name
   - CHEBI: Search by name or formula
   - GO: Search by enzyme function
   - KEGG: Search by EC or enzyme name
2. Add to Google Sheets
3. Re-export and validate

---

## File Organization

```
assay-metadata/
├── src/bacdive_assay_metadata/
│   ├── mappers.py              # Main mappings (edit via Google Sheets)
│   ├── validate_mappings.py    # Validation system
│   └── validate_fast.py        # Fast validation
├── scripts/
│   ├── apply_fixes.py          # ONE-TIME cleanup utility
│   └── README.md               # Script documentation
├── data/
│   └── *.json                  # Generated outputs
├── notes/                      # Reference documentation
│   ├── FINAL_MAPPING_STATS.md      # Pre-fix statistics
│   ├── FINAL_FIXED_MAPPING_STATS.md # Post-fix statistics (after cleanup)
│   ├── VALIDATION_ERRORS_DETAILED.md # Invalid ID analysis
│   ├── DEPRECATED_TERMS_REPORT.md   # Deprecated term analysis
│   └── README.md               # Notes directory guide
├── VALIDATION.md               # Validation guide
└── WORKFLOW.md                 # This file
```

---

## Version Control

### What to Commit
✅ `src/bacdive_assay_metadata/mappers.py` - Source mappings
✅ `ontology_file_metadata.json` - File hashes (not actual files)
✅ Documentation updates
✅ `data/*.json` - Generated outputs (optional)

### What NOT to Commit
❌ Large ontology TSV files (use KG-Microbe reference)
❌ Backup files (`*.backup-*`)
❌ Temporary validation reports (regenerate as needed)

---

## References

### Documentation
- `README.md` - Project overview and installation
- `VALIDATION.md` - Validation system details
- `WORKFLOW.md` - This document
- `scripts/README.md` - One-time utility scripts

### Validation Reports
- `notes/VALIDATION_ERRORS_DETAILED.md` - Invalid ID analysis
- `notes/DEPRECATED_TERMS_REPORT.md` - Deprecated term analysis
- `notes/FINAL_MAPPING_STATS.md` - Initial statistics
- `notes/FINAL_FIXED_MAPPING_STATS.md` - After-fix statistics

### Databases
- CHEBI: https://www.ebi.ac.uk/chebi/
- PubChem: https://pubchem.ncbi.nlm.nih.gov/
- EC: https://www.enzyme-database.org/
- GO: http://geneontology.org/
- KEGG: https://www.genome.jp/kegg/

---

## Quick Reference

```bash
# Initial setup (one-time)
make validate                           # Find errors
uv run python3 scripts/apply_fixes.py   # Fix errors
make validate                           # Verify (0 errors)
# → Update Google Sheets with corrections

# Regular workflow
# 1. Update Google Sheets
# 2. Export to mappers.py
make validate                           # Check for errors
make extract                            # Generate outputs
git commit                              # Commit changes

# Validation options
make validate         # Fast (~5 sec)
make validate-full    # Complete (~20 min)
make track-files      # Track ontology versions
```

---

**Last Updated**: 2025-11-17
**Status**: Production Ready
**Version**: 2.0
