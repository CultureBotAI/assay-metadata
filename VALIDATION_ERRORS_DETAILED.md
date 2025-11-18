# Detailed Error Report - Invalid CHEBI IDs

**Generated**: 2025-11-17
**Status**: 3 errors found in curated mappings

---

## Error 1: 5-Ketogluconic Acid (5KG)

### Current Mapping (INVALID)
**Location**: `src/bacdive_assay_metadata/mappers.py:77`

```python
"5KG": {"name": "5-Ketogluconic acid", "chebi": "CHEBI:17991", "pubchem": "160957"}
```

### Issue
- **CHEBI:17991**: ❌ Does not exist in CHEBI database
- **PubChem CID 160957**: ❌ Incorrect - maps to "Iron Sulfide", not 5-Ketogluconic acid

### Root Cause
Both identifiers are wrong. Appears to be a data entry error.

### Correct Identifiers
After validation against PubChem and CHEBI databases:

| Database | Correct ID | Verified |
|----------|------------|----------|
| **CHEBI** | `CHEBI:17426` | ✅ "5-dehydro-D-gluconic acid" |
| **PubChem** | `5460352` | ✅ "5-Ketogluconic acid" |

**Note**: "5-dehydro-D-gluconic acid" is the IUPAC systematic name for "5-ketogluconic acid" (trivial name).

### Corrected Mapping

```python
"5KG": {"name": "5-Ketogluconic acid", "chebi": "CHEBI:17426", "pubchem": "5460352"}
```

### Verification
```bash
# CHEBI verification
grep "^CHEBI:17426" chebi_nodes.tsv
# Output: CHEBI:17426	5-dehydro-D-gluconic acid

# PubChem verification
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/5460352/description/JSON"
# Returns: "5-Ketogluconic acid"
```

---

## Error 2: D-Tagatose (TAG)

### Current Mapping (INVALID)
**Location**: `src/bacdive_assay_metadata/mappers.py:106`

```python
"TAG": {"name": "D-Tagatose", "chebi": "CHEBI:17004", "pubchem": "439654"}
```

### Issue
- **CHEBI:17004**: ❌ Does not exist in CHEBI database
- **PubChem CID 439654**: ✅ Correct

### Root Cause
CHEBI ID appears to be a typo or data entry error. PubChem ID is correct.

### Correct Identifiers

| Database | Correct ID | Verified |
|----------|------------|----------|
| **CHEBI** | `CHEBI:16443` | ✅ "D-tagatose" |
| **PubChem** | `439654` | ✅ Already correct |

### Corrected Mapping

```python
"TAG": {"name": "D-Tagatose", "chebi": "CHEBI:16443", "pubchem": "439654"}
```

### Verification
```bash
# CHEBI verification
grep "^CHEBI:16443" chebi_nodes.tsv
# Output: CHEBI:16443	D-tagatose	The D-enantiomer of tagatose.

# PubChem verification
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/439654/synonyms/JSON"
# Returns: "D-Tagatose"
```

---

## Error 3: Cyclodextrin (CDEX)

### Current Mapping (INVALID)
**Location**: `src/bacdive_assay_metadata/mappers.py:133`

```python
"CDEX": {"name": "Cyclodextrin", "chebi": "CHEBI:495083", "pubchem": None}
```

### Issue
- **CHEBI:495083**: ❌ Does not exist in CHEBI database
- **PubChem CID**: Missing (None)

### Root Cause
CHEBI ID appears to be a near-miss typo. Valid cyclodextrin IDs exist:
- CHEBI:40585 - alpha-cyclodextrin
- CHEBI:495055 - beta-cyclodextrin (off by 28!)
- CHEBI:495056 - gamma-cyclodextrin (off by 27!)

### BacDive Data Investigation
Searching the source BacDive data shows:
```json
"metabolite": "cyclodextrin"           // Generic term (most common)
"metabolite": "alpha-cyclodextrin"     // Specific type
```

### Recommended Fix
Since BacDive uses both generic "cyclodextrin" and specific "alpha-cyclodextrin", and there's no universal CHEBI ID for generic "cyclodextrin", we should use **alpha-cyclodextrin** as the most common type:

| Database | Recommended ID | Notes |
|----------|---------------|-------|
| **CHEBI** | `CHEBI:40585` | alpha-cyclodextrin (most commonly used) |
| **PubChem** | `444041` | alpha-cyclodextrin |

**Alternative options**:
- CHEBI:495055 / PubChem:444054 - beta-cyclodextrin
- CHEBI:495056 / PubChem:51051622 - gamma-cyclodextrin

### Corrected Mapping (Recommended)

```python
"CDEX": {"name": "alpha-Cyclodextrin", "chebi": "CHEBI:40585", "pubchem": "444041"}
```

Or if generic class is preferred:
```python
# Note: No single CHEBI ID for generic cyclodextrin class
# Must choose a specific type or leave empty
"CDEX": {"name": "Cyclodextrin", "chebi": None, "pubchem": None}
```

### Verification
```bash
# CHEBI verification for alpha-cyclodextrin
grep "^CHEBI:40585" chebi_nodes.tsv
# Output: CHEBI:40585	alpha-cyclodextrin	A cycloamylose composed of six alpha-(1->4) linked D-glucopyranose units.

# All cyclodextrin types
grep -E "^CHEBI:(40585|495055|495056)" chebi_nodes.tsv
# Output:
#   CHEBI:40585  alpha-cyclodextrin  (6 glucose units)
#   CHEBI:495055 beta-cyclodextrin   (7 glucose units)
#   CHEBI:495056 gamma-cyclodextrin  (8 glucose units)
```

---

## Summary of Corrections

### Quick Fix Commands

```bash
# Edit mappers.py and make these changes:

# Line 77: 5-Ketogluconic acid
- "5KG": {"name": "5-Ketogluconic acid", "chebi": "CHEBI:17991", "pubchem": "160957"}
+ "5KG": {"name": "5-Ketogluconic acid", "chebi": "CHEBI:17426", "pubchem": "5460352"}

# Line 106: D-Tagatose
- "TAG": {"name": "D-Tagatose", "chebi": "CHEBI:17004", "pubchem": "439654"}
+ "TAG": {"name": "D-Tagatose", "chebi": "CHEBI:16443", "pubchem": "439654"}

# Line 133: Cyclodextrin
- "CDEX": {"name": "Cyclodextrin", "chebi": "CHEBI:495083", "pubchem": None}
+ "CDEX": {"name": "alpha-Cyclodextrin", "chebi": "CHEBI:40585", "pubchem": "444041"}
```

### Validation After Fix

```bash
# Run validation
make validate

# Expected result: 0 errors, 8 warnings (deprecated terms)
```

---

## Technical Details

### How Errors Were Discovered

1. **Automated validation** against KG-Microbe CHEBI ontology (223,125 terms)
2. **Cross-reference** with PubChem API
3. **Manual verification** of CHEBI database

### Validation Method

```python
# OntologyIndex lookup (validate_mappings.py)
term = chebi_index.lookup("CHEBI:17991")
if term is None:
    # Error: ID not found
```

### Data Sources

| Source | Version | Date | Hash |
|--------|---------|------|------|
| CHEBI nodes | KG-Microbe Sept 2024 | 2024-09-01 | `b21586dc...` |
| PubChem API | Current | 2025-11-17 | N/A |

---

## Impact Assessment

| Error Type | Impact | Priority |
|------------|--------|----------|
| **Invalid CHEBI IDs** | ❌ Critical - Breaks knowledge graph links | **HIGH** |
| **Invalid PubChem IDs** | ⚠️ Moderate - Incorrect chemical structure | **MEDIUM** |
| **Missing IDs** | ℹ️ Low - Reduces data completeness | **LOW** |

### Affected Downstream Systems
- Knowledge graph construction (broken links)
- Chemical property lookup (wrong compound)
- Cross-database mapping (incorrect associations)

**Action Required**: Fix before production deployment

---

## References

- **CHEBI Database**: https://www.ebi.ac.uk/chebi/
- **PubChem**: https://pubchem.ncbi.nlm.nih.gov/
- **KG-Microbe Ontologies**: `/kg-microbe/data/transformed/ontologies/`
- **Validation Script**: `src/bacdive_assay_metadata/validate_mappings.py`

---

**Report Generated by**: BacDive Assay Metadata Validation System
**Next Steps**: Apply corrections and re-run validation
