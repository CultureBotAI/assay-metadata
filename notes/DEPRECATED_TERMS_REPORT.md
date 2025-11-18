# Deprecated Terms - Detailed Report

**Generated**: 2025-11-17
**Status**: 8 warnings (deprecated but resolvable terms)

---

## Summary

8 deprecated identifiers found in curated mappings. All terms are **still resolvable** but should be updated to current versions for best practices.

| Category | Count | Status |
|----------|-------|--------|
| CHEBI IDs | 2 | ⚠️ Deprecated |
| GO Terms | 1 | ❌ Obsolete |
| EC Numbers | 3 unique (5 occurrences) | ⚠️ Deprecated |

---

## CHEBI Identifiers (2 Deprecated)

### 1. Dulcitol (CHEBI:42118)

**Location**: `mappers.py:51`

**Current Mapping (DEPRECATED)**:
```python
"DUL": {"name": "Dulcitol", "chebi": "CHEBI:42118", "pubchem": "11850"}
```

**Issue**:
- `CHEBI:42118` - Deprecated (empty entry, no name/description)

**Recommended Fix**:
```python
"DUL": {"name": "Dulcitol", "chebi": "CHEBI:16813", "pubchem": "11850"}
```

**Replacement Details**:
- **Current ID**: `CHEBI:16813`
- **Current Name**: "galactitol"
- **Synonyms**: Dulcitol, D-Dulcitol, meso-galactitol
- **Description**: An optically inactive hexitol having meso-configuration
- **Status**: ✅ Active (3 STAR rating in CHEBI)

**Verification**:
```bash
grep "^CHEBI:16813" chebi_nodes.tsv
# CHEBI:16813	galactitol	Dulcitol, D-galactitol
```

---

### 2. D-Lyxose (CHEBI:12301)

**Location**: `mappers.py:105`

**Current Mapping (DEPRECATED)**:
```python
"LYX": {"name": "D-Lyxose", "chebi": "CHEBI:12301", "pubchem": "439236"}
```

**Issue**:
- `CHEBI:12301` - Deprecated (empty entry)

**Recommended Fix**:
```python
"LYX": {"name": "D-Lyxose", "chebi": "CHEBI:62318", "pubchem": "439236"}
```

**Replacement Details**:
- **Current ID**: `CHEBI:62318`
- **Current Name**: "D-lyxose"
- **Description**: Any lyxose having D-configuration
- **Status**: ✅ Active

**Verification**:
```bash
grep "^CHEBI:62318" chebi_nodes.tsv
# CHEBI:62318	D-lyxose	Any lyxose having D-configuration
```

---

## GO Terms (1 Obsolete)

### 3. Gamma-glutamyltransferase Activity (GO:0003840)

**Location**: `mappers.py:423`

**Current Mapping (OBSOLETE)**:
```python
"Gamma-glutamyl transferase": {
    "go_terms": ["GO:0003840"],
    "go_names": ["gamma-glutamyltransferase activity"],
    "kegg_ko": "K00681",
    "ec_number": "2.3.2.2",
}
```

**Issue**:
- `GO:0003840` - ❌ **OBSOLETE** term
- Description: "OBSOLETE. Catalysis of the reaction: (5-L-glutamyl)-peptide + an amino acid = peptide + 5-L-glutamyl-amino acid"

**Recommended Fix**:
```python
"Gamma-glutamyl transferase": {
    "go_terms": ["GO:0036374"],  # ✅ CURRENT REPLACEMENT
    "go_names": ["glutathione hydrolase activity"],  # Primary name, or use synonym
    "kegg_ko": "K00681",  # Keep this
    "ec_number": "2.3.2.2",  # Keep this (NOT deprecated)
}
```

**Replacement Details**:
- **Old GO**: GO:0003840 (obsolete)
- **New GO**: **GO:0036374** (current)
- **Primary Name**: "glutathione hydrolase activity"
- **Synonym**: "gamma-glutamyltranspeptidase activity" (matches enzyme name)
- **EC References**: EC:3.4.19.13 (and also works with EC:2.3.2.2)
- **KEGG K00681 confirms**: Has both EC:2.3.2.2 and EC:3.4.19.13 activities
- **Status**: ✅ Active

**Note**: KEGG K00681 describes this enzyme as "gamma-glutamyltranspeptidase / glutathione hydrolase" with dual EC numbers (2.3.2.2 and 3.4.19.13), confirming GO:0036374 is the correct current term.

**Verification**:
```bash
grep "^GO:0036374" go_nodes.tsv
# GO:0036374	glutathione hydrolase activity	Synonyms: gamma-glutamyltranspeptidase activity

grep "^GO:0003840" go_nodes.tsv
# GO:0003840	obsolete gamma-glutamyltransferase activity	(OBSOLETE)
```

---

## EC Numbers (3 Deprecated)

### 4. Cytochrome-c Oxidase (EC 1.9.3.1) - 2 occurrences

**Locations**:
- `mappers.py:492` (Cytochrome oxidase)
- `mappers.py:614` (cytochrome oxidase - duplicate entry)

**Current Mapping (DEPRECATED)**:
```python
"Cytochrome oxidase": {
    "go_terms": ["GO:0004129"],
    "go_names": ["cytochrome-c oxidase activity"],
    "kegg_ko": "K02274",
    "ec_number": "1.9.3.1",  # DEPRECATED
}
```

**Issue**:
- `EC 1.9.3.1` - Deprecated (empty entry in database)

**Recommended Fix**:
```python
"Cytochrome oxidase": {
    "go_terms": ["GO:0004129"],
    "go_names": ["cytochrome-c oxidase activity"],
    "kegg_ko": "K02274",
    "ec_number": "7.1.1.9",  # NEW
}
```

**Replacement Details**:
- **Old EC**: 1.9.3.1 (deprecated)
- **New EC**: **7.1.1.9** (current)
- **Name**: cytochrome-c oxidase
- **Synonyms**: Warburg's respiratory enzyme, complex IV, cytochrome a3, cytochrome aa3, cytochrome oxidase
- **Status**: ✅ Active

**Note**: This appears **twice** in the mappings (capitalized and lowercase). Both should be updated.

**Verification**:
```bash
grep "ec=7.1.1.9" ec_nodes.tsv
# 7.1.1.9	cytochrome-c oxidase
```

---

### 5. Nitrate Reductase (EC 1.7.99.4)

**Location**: `mappers.py:498`

**Current Mapping (DEPRECATED)**:
```python
"Nitrate reductase": {
    "go_terms": ["GO:0008940"],
    "go_names": ["nitrate reductase activity"],
    "kegg_ko": "K00370",
    "ec_number": "1.7.99.4",  # DEPRECATED
}
```

**Issue**:
- `EC 1.7.99.4` - Deprecated (empty entry in database)

**Recommended Fix**:
```python
"Nitrate reductase": {
    "go_terms": ["GO:0008940"],
    "go_names": ["nitrate reductase activity"],
    "kegg_ko": "K00370",
    "ec_number": "1.7.5.1",  # NEW
}
```

**Replacement Details**:
- **Old EC**: 1.7.99.4 (deprecated)
- **New EC**: **1.7.5.1** (current)
- **Name**: nitrate reductase (quinone)
- **Synonyms**: dissimilatory nitrate reductase, nitrate reductase A, nitrate reductase Z
- **Status**: ✅ Active
- **Confirmed by**: KEGG K00370 → EC 1.7.5.1

**Verification**:
```bash
curl "https://rest.kegg.jp/get/K00370" | grep "EC:"
# EC:1.7.5.1
```

---

### 6. Gelatinase (EC 3.4.24.4) - 2 occurrences

**Locations**:
- `mappers.py:512` (Gelatinase)
- `mappers.py:620` (gelatinase - duplicate entry)

**Current Mapping (DEPRECATED)**:
```python
"Gelatinase": {
    "go_terms": ["GO:0004222"],
    "go_names": ["metalloendopeptidase activity"],
    "kegg_ko": "K01398",
    "ec_number": "3.4.24.4",  # DEPRECATED
}
```

**Issue**:
- `EC 3.4.24.4` - Deprecated (empty entry in database)

**Recommended Fix**:
```python
"Gelatinase": {
    "go_terms": ["GO:0004222"],
    "go_names": ["metalloendopeptidase activity"],
    "kegg_ko": "K01398",
    "ec_number": "3.4.24.24",  # NEW (note extra .24)
}
```

**Replacement Details**:
- **Old EC**: 3.4.24.4 (deprecated)
- **New EC**: **3.4.24.24** (current)
- **Name**: matrix metalloproteinase-2 (gelatinase A)
- **Status**: ✅ Active
- **Confirmed by**: KEGG K01398 → EC 3.4.24.24

**Note**: This appears **twice** in the mappings (capitalized and lowercase). Both should be updated.

**Verification**:
```bash
curl "https://rest.kegg.jp/get/K01398" | grep "EC:"
# EC:3.4.24.24
```

---

## Quick Fix Summary

### All Changes Required

```bash
# Edit src/bacdive_assay_metadata/mappers.py

# Line 51: Dulcitol
- "DUL": {"name": "Dulcitol", "chebi": "CHEBI:42118", "pubchem": "11850"}
+ "DUL": {"name": "Dulcitol", "chebi": "CHEBI:16813", "pubchem": "11850"}

# Line 105: D-Lyxose
- "LYX": {"name": "D-Lyxose", "chebi": "CHEBI:12301", "pubchem": "439236"}
+ "LYX": {"name": "D-Lyxose", "chebi": "CHEBI:62318", "pubchem": "439236"}

# Line 423: Gamma-glutamyl transferase (update obsolete GO term)
  "Gamma-glutamyl transferase": {
-     "go_terms": ["GO:0003840"],
-     "go_names": ["gamma-glutamyltransferase activity"],
+     "go_terms": ["GO:0036374"],
+     "go_names": ["glutathione hydrolase activity"],
      "kegg_ko": "K00681",
      "ec_number": "2.3.2.2",
  },

# Line 492: Cytochrome oxidase (first occurrence)
  "Cytochrome oxidase": {
      "go_terms": ["GO:0004129"],
      "go_names": ["cytochrome-c oxidase activity"],
      "kegg_ko": "K02274",
-     "ec_number": "1.9.3.1",
+     "ec_number": "7.1.1.9",
  },

# Line 498: Nitrate reductase
  "Nitrate reductase": {
      "go_terms": ["GO:0008940"],
      "go_names": ["nitrate reductase activity"],
      "kegg_ko": "K00370",
-     "ec_number": "1.7.99.4",
+     "ec_number": "1.7.5.1",
  },

# Line 512: Gelatinase (first occurrence)
  "Gelatinase": {
      "go_terms": ["GO:0004222"],
      "go_names": ["metalloendopeptidase activity"],
      "kegg_ko": "K01398",
-     "ec_number": "3.4.24.4",
+     "ec_number": "3.4.24.24",
  },

# Line 614: cytochrome oxidase (duplicate - second occurrence)
  "cytochrome oxidase": {
      "go_terms": ["GO:0004129"],
      "go_names": ["cytochrome-c oxidase activity"],
      "kegg_ko": "K02274",
-     "ec_number": "1.9.3.1",
+     "ec_number": "7.1.1.9",
  },

# Line 620: gelatinase (duplicate - second occurrence)
  "gelatinase": {
      "go_terms": ["GO:0004222"],
      "go_names": ["metalloendopeptidase activity"],
      "kegg_ko": "K01398",
-     "ec_number": "3.4.24.4",
+     "ec_number": "3.4.24.24",
  },
```

---

## Impact Assessment

| Term | Severity | Impact | Priority |
|------|----------|--------|----------|
| CHEBI:42118 | ⚠️ Low | Still resolvable | MEDIUM |
| CHEBI:12301 | ⚠️ Low | Still resolvable | MEDIUM |
| GO:0003840 | ❌ High | Obsolete, replaced by GO:0036374 | **HIGH** |
| EC 1.9.3.1 | ⚠️ Medium | Replaced by 7.1.1.9 | MEDIUM |
| EC 1.7.99.4 | ⚠️ Medium | Replaced by 1.7.5.1 | MEDIUM |
| EC 3.4.24.4 | ⚠️ Medium | Replaced by 3.4.24.24 | MEDIUM |

**Priority**: Fix GO:0003840 first (obsolete), then update deprecated terms

---

## Validation After Fix

```bash
# After applying fixes, re-run validation
make validate

# Expected result:
# - 3 errors (invalid CHEBI IDs - see VALIDATION_ERRORS_DETAILED.md)
# - 0 warnings (all deprecated terms fixed)
```

---

## References

- **CHEBI Database**: https://www.ebi.ac.uk/chebi/
- **GO Database**: http://geneontology.org/
- **EC Database**: https://www.enzyme-database.org/
- **KEGG Database**: https://www.genome.jp/kegg/
- **KG-Microbe Ontologies**: `/kg-microbe/data/transformed/ontologies/`

---

**Report Generated**: 2025-11-17
**Next Action**: Apply fixes to mappers.py
**Validation**: Run `make validate` to confirm
