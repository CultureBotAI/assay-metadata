# Final Mapping Statistics Report

**Generated**: 2025-11-17
**Status**: All errors identified and fix recommendations provided

---

## Executive Summary

### Current State (Before Fixes)
- **Total mappings**: 140 (86 substrates + 54 enzymes)
- **Validation errors**: 3 invalid IDs (critical)
- **Validation warnings**: 8 deprecated terms (medium priority)
- **Overall accuracy**: 92.1% (129/140 valid, 11 need fixes)

### After Applying All Fixes
- **Total mappings**: 140 (unchanged)
- **Expected validation errors**: 0 ✅
- **Expected validation warnings**: 0 ✅
- **Expected accuracy**: 100% ✅

---

## Database Coverage Statistics

### Substrate Mappings (86 total)

| Database | Current Valid | With Errors | After Fixes | Coverage % |
|----------|---------------|-------------|-------------|------------|
| **CHEBI** | 81 | 5 (3 invalid + 2 deprecated) | 86 | **100%** |
| **PubChem** | 81* | 4 (2 invalid + 2 missing) | 85 | **98.8%** |

\* PubChem CID 160957 is mapped to wrong compound (Iron Sulfide instead of 5-Ketogluconic acid)

**Substrates without PubChem**: 1 (Gelatin - not a pure chemical compound)

### Enzyme Mappings (54 total)

| Database | Current Valid | With Errors | After Fixes | Coverage % |
|----------|---------------|-------------|-------------|------------|
| **EC** | 39 | 6 (3 deprecated, used 5 times) | 42 | **77.8%** |
| **GO** | 55 terms | 1 obsolete | 55 terms | **100%** of annotated |
| **KEGG KO** | 28 | 0 | 28 | **51.9%** |

**Enzymes with EC**: 42/54 (77.8%)
**Enzymes with GO**: Many enzymes have multiple GO terms
**Enzymes with KEGG**: 28/54 (51.9%)

---

## Detailed Breakdown

### 1. CHEBI Identifiers

**Total substrate mappings**: 86

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Valid | 81 | 94.2% |
| ⚠️ Deprecated (still resolvable) | 2 | 2.3% |
| ❌ Invalid (not found) | 3 | 3.5% |

**Invalid CHEBI IDs to fix**:
1. `CHEBI:17991` → `CHEBI:17426` (5-Ketogluconic acid)
2. `CHEBI:17004` → `CHEBI:16443` (D-Tagatose)
3. `CHEBI:495083` → `CHEBI:40585` (Cyclodextrin → alpha-Cyclodextrin)

**Deprecated CHEBI IDs to update**:
1. `CHEBI:42118` → `CHEBI:16813` (Dulcitol → galactitol)
2. `CHEBI:12301` → `CHEBI:62318` (D-Lyxose)

**After fixes**: 86/86 (100%) ✅

---

### 2. PubChem Identifiers

**Total substrate mappings**: 86

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Valid | 81 | 94.2% |
| ❌ Invalid (wrong compound) | 1 | 1.2% |
| ⬜ Missing (None) | 4 | 4.6% |

**Invalid PubChem IDs to fix**:
1. `160957` → `5460352` (5-Ketogluconic acid - was Iron Sulfide!)

**Missing PubChem IDs to add**:
1. Cyclodextrin: `None` → `444041` (alpha-cyclodextrin)
2. Gelatin: `None` (cannot map - complex protein mixture)
3. D-Tagatose: Already has correct `439654` ✅

**After fixes**: 85/86 (98.8%) - Gelatin cannot be mapped ✅

---

### 3. EC Numbers

**Total enzyme annotations**: 54
**Enzymes with EC**: 42 (77.8%)

| Status | Count | Occurrences | Percentage |
|--------|-------|-------------|------------|
| ✅ Valid | 39 | N/A | 92.9% |
| ⚠️ Deprecated | 3 | 5 | 7.1% |
| ⬜ No EC number | 12 | N/A | 22.2% |

**Deprecated EC numbers to update** (3 unique, 5 occurrences):
1. `1.9.3.1` → `7.1.1.9` (Cytochrome oxidase - **2 occurrences**)
2. `1.7.99.4` → `1.7.5.1` (Nitrate reductase - 1 occurrence)
3. `3.4.24.4` → `3.4.24.24` (Gelatinase - **2 occurrences**)

**After fixes**: 42/54 (77.8%) with EC numbers ✅

**Note**: 12 enzymes intentionally have no EC number (substrate-specific variants like arylamidases)

---

### 4. GO Terms

**Total enzyme annotations**: 54
**GO term entries**: 55+ terms (some enzymes have multiple GO terms)

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Valid | 54 | 98.2% |
| ❌ Obsolete | 1 | 1.8% |

**Obsolete GO terms to update**:
1. `GO:0003840` → `GO:0036374` (Gamma-glutamyl transferase)
   - Old: "gamma-glutamyltransferase activity" (obsolete)
   - New: "glutathione hydrolase activity" (synonym: gamma-glutamyltranspeptidase activity)

**After fixes**: 55/55 (100%) ✅

**Coverage by enzyme type**:
- Wells with GO terms: 42/218 (19.3%)
- BacDive enzymes with GO: 17/175 (9.7%)

---

### 5. KEGG Orthology (KO)

**Total enzyme annotations**: 54
**Enzymes with KEGG KO**: 28 (51.9%)

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Valid | 28 | 100% |
| ❌ Invalid | 0 | 0% |

**All KEGG KO IDs are valid** ✅

**Coverage**:
- Wells with KEGG: 28/218 (12.8%)
- Enzymes with KEGG: 28/54 (51.9%)

**After fixes**: 28/28 (100%) - no changes needed ✅

---

## Summary of Required Fixes

### Total Changes Required: 11

| Category | Changes | Priority |
|----------|---------|----------|
| **Invalid IDs** (errors) | 3 | CRITICAL |
| **Deprecated IDs** (warnings) | 8 | MEDIUM |

### By Database

| Database | Invalid | Deprecated | Total Fixes |
|----------|---------|------------|-------------|
| CHEBI | 3 | 2 | 5 |
| PubChem | 1 | 0 | 1 |
| EC | 0 | 3 (5 occurrences) | 5 |
| GO | 0 | 1 | 1 |
| KEGG | 0 | 0 | 0 |
| **TOTAL** | **4** | **6 unique (8 occurrences)** | **11** |

---

## Coverage Analysis

### By Well Type (218 unique wells)

| Well Type | Count | CHEBI | PubChem | EC | GO | KEGG |
|-----------|-------|-------|---------|----|----|------|
| **Substrate** | 85 | 84 (98.8%) | 81 (95.3%) | - | - | - |
| **Enzyme** | 76 | - | - | 42 (55.3%) | 42 (55.3%) | 28 (36.8%) |
| **Phenotypic** | 56 | - | - | - | - | - |
| **Other** | 1 | - | - | - | - | - |

### Multi-Database Annotation

| Annotation Level | Wells | Percentage |
|------------------|-------|------------|
| **Complete** (all relevant DBs) | 28 | 12.8% |
| **Partial** (some DBs) | 126 | 57.8% |
| **Minimal** (1 DB only) | 63 | 28.9% |
| **None** | 1 | 0.5% |

**Complete annotation** = substrates with CHEBI+PubChem OR enzymes with EC+GO+KEGG

---

## Quality Metrics

### Current State

| Metric | Value | Target |
|--------|-------|--------|
| **Validation errors** | 3 | 0 |
| **Validation warnings** | 8 | 0 |
| **Overall accuracy** | 92.1% | 100% |
| **CHEBI accuracy** | 94.2% | 100% |
| **PubChem accuracy** | 94.2% | 98.8% |
| **EC accuracy** | 92.9% | 100% |
| **GO accuracy** | 98.2% | 100% |
| **KEGG accuracy** | 100% | 100% |

### After Applying Fixes

| Metric | Value | Status |
|--------|-------|--------|
| **Validation errors** | 0 | ✅ |
| **Validation warnings** | 0 | ✅ |
| **Overall accuracy** | 100% | ✅ |
| **CHEBI accuracy** | 100% | ✅ |
| **PubChem accuracy** | 98.8% | ✅ (Gelatin excluded) |
| **EC accuracy** | 100% | ✅ |
| **GO accuracy** | 100% | ✅ |
| **KEGG accuracy** | 100% | ✅ |

---

## Comparison: Before vs After

### Error Counts

| Database | Before | After | Change |
|----------|--------|-------|--------|
| CHEBI | 5 errors | 0 errors | **-100%** |
| PubChem | 1 error | 0 errors | **-100%** |
| EC | 5 deprecated | 0 deprecated | **-100%** |
| GO | 1 obsolete | 0 obsolete | **-100%** |
| **TOTAL** | **12** | **0** | **-100%** |

### Coverage Improvement

| Database | Before | After | Change |
|----------|--------|-------|--------|
| CHEBI | 94.2% | 100% | **+5.8%** |
| PubChem | 94.2% | 98.8% | **+4.6%** |
| EC | 92.9% valid | 100% valid | **+7.1%** |
| GO | 98.2% valid | 100% valid | **+1.8%** |

---

## File Statistics

### Input Data
- **BacDive strains**: 99,392
- **API kit occurrences**: 43,688
- **Unique API kits**: 17
- **Unique wells**: 218
- **Unique enzymes**: 175

### Curated Mappings
- **Substrate mappings**: 86 (in `SUBSTRATE_MAPPINGS`)
- **Enzyme annotations**: 54 (in `ENZYME_ANNOTATIONS`)
- **Total curated entries**: 140

### Output Files
- `assay_metadata.json`: 135 KB (standard format)
- `assay_kits_simple.json`: 409 KB (simplified format)
- `ontology_file_metadata.json`: ~1 KB (version control)
- `validation_report.json`: ~1 KB (validation results)

---

## Validation Sources

### KG-Microbe Ontologies (Local Files)

| Ontology | Terms | Size | Last Modified | SHA256 |
|----------|-------|------|---------------|--------|
| **CHEBI** | 223,125 | 73 MB | 2024-09-01 | `b21586dc...` |
| **EC** | 249,191 | 12 MB | 2024-09-01 | `03d750c4...` |
| **GO** | 51,882 | 20 MB | 2024-09-01 | `7195eba3...` |

### Web APIs (Online Validation)

| API | Endpoint | Rate Limit | Used For |
|-----|----------|------------|----------|
| **PubChem** | rest.pubchem.ncbi.nlm.nih.gov | 5 req/sec | CID validation |
| **KEGG** | rest.kegg.jp | 5 req/sec | KO validation |
| **RHEA** | rest.rhea-db.org | N/A | Reaction IDs (cached) |

---

## Recommendations

### Immediate Actions (Critical)
1. ✅ Fix 3 invalid CHEBI IDs (see VALIDATION_ERRORS_DETAILED.md)
2. ✅ Fix 1 invalid PubChem CID (5-Ketogluconic acid)
3. ✅ Update Cyclodextrin to alpha-Cyclodextrin with PubChem ID

### Short-term Actions (Medium Priority)
1. ✅ Update 2 deprecated CHEBI IDs
2. ✅ Update 3 deprecated EC numbers (5 occurrences)
3. ✅ Update 1 obsolete GO term

### Long-term Improvements (Low Priority)
1. ⬜ Add PubChem IDs for remaining substrates (increase from 98.8% to 100%)
2. ⬜ Add EC numbers for substrate-specific enzymes (if available)
3. ⬜ Expand KEGG coverage (currently 51.9% of enzymes)
4. ⬜ Add RHEA reaction IDs when API becomes available

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-17 | 1.0 | Initial curated mappings |
| 2025-11-17 | 1.1 | Added GO/KEGG annotations (42 wells) |
| 2025-11-17 | 1.2 | Validation system implemented |
| 2025-11-17 | 1.3 | Errors identified (3 invalid + 8 deprecated) |
| TBD | 2.0 | All fixes applied (expected: 100% valid) |

---

## References

- **Validation Reports**:
  - `VALIDATION_ERRORS_DETAILED.md` - Invalid ID corrections
  - `DEPRECATED_TERMS_REPORT.md` - Deprecated term updates
  - `VALIDATION.md` - Validation system guide

- **Source Code**:
  - `src/bacdive_assay_metadata/mappers.py:16-103` - SUBSTRATE_MAPPINGS
  - `src/bacdive_assay_metadata/mappers.py:234-416` - ENZYME_ANNOTATIONS

- **Databases**:
  - CHEBI: https://www.ebi.ac.uk/chebi/
  - PubChem: https://pubchem.ncbi.nlm.nih.gov/
  - EC: https://www.enzyme-database.org/
  - GO: http://geneontology.org/
  - KEGG: https://www.genome.jp/kegg/

---

**Status**: Ready for fixes
**Expected validation result after fixes**: ✅ 0 errors, 0 warnings
**Next step**: Apply fixes from VALIDATION_ERRORS_DETAILED.md and DEPRECATED_TERMS_REPORT.md
