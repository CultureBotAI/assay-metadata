# Deterministic EC Number Assignment Plan for API Assay Enzymes

**Version**: 1.0
**Date**: 2025-11-26
**Status**: Planning

---

## Overview

This document outlines a deterministic, reproducible methodology for assigning EC (Enzyme Commission) numbers to the 30 API assay enzymes currently lacking EC identifiers.

**Current Status**:
- Total enzyme wells: 158
- With EC numbers: 108 (68.4%)
- **Without EC numbers: 50 wells (30 unique enzymes)**

---

## Methodology: Deterministic EC Assignment

### Principle

All EC number assignments must be:
1. **Traceable** - Sourced from authoritative databases or official documentation
2. **Reproducible** - Same enzyme name → same EC number lookup
3. **Validated** - Cross-referenced against KG-Microbe EC ontology
4. **Documented** - Sources cited in code comments

### Authoritative Sources (Priority Order)

1. **ExpASy ENZYME Database** (https://enzyme.expasy.org/)
   - Official IUBMB Enzyme Nomenclature database
   - Search by enzyme name → retrieve official EC number
   - Most authoritative source for EC numbers

2. **BRENDA** (https://www.brenda-enzymes.org/)
   - Comprehensive enzyme information system
   - Cross-references multiple databases
   - Includes substrate specificity

3. **UniProt** (https://www.uniprot.org/)
   - Protein database with EC annotations
   - Search by enzyme name → find consensus EC numbers

4. **bioMérieux API Kit Documentation**
   - Official package inserts
   - Educational resources (Microbe Online, FIU manuals)
   - Already downloaded in `references/` directory

5. **KG-Microbe EC Ontology** (local validation)
   - `ec_nodes.tsv` - 249,191 EC terms
   - Used for validation, not lookup

---

## Enzyme Categories and Assignment Strategy

### Category 1: HIGH FEASIBILITY - Glycosidases (7 enzymes)

**Enzymes**:
- `alpha ARA` - α-arabinosidase
- `alpha FUC` - α-fucosidase
- `alpha GLU` - α-glucosidase
- `alphaMAL` - α-maltosidase
- `alpha MAN` - α-mannosidase
- `beta GLU` - β-glucosidase
- `beta MAN` - β-mannosidase

**Also in "other"**:
- `beta NAG` - β-N-acetyl-glucosaminidase
- `beta GP` - β-glycosidase (generic, may not have specific EC)
- `ONPG` - o-Nitrophenyl-β-D-galactopyranoside (β-galactosidase test)

**Strategy**:
1. Search ExpASy ENZYME by exact name (e.g., "alpha-arabinosidase")
2. Retrieve canonical EC number
3. Verify EC exists in KG-Microbe `ec_nodes.tsv`
4. Cross-reference with BRENDA for substrate specificity
5. Document source in code comment

**Expected Mappings** (to be verified):
```python
{
    "alpha ARA": "EC:3.2.1.55",  # α-L-arabinofuranosidase
    "alpha FUC": "EC:3.2.1.51",  # α-L-fucosidase
    "alpha GLU": "EC:3.2.1.20",  # α-glucosidase
    "alphaMAL": "EC:3.2.1.20",   # α-glucosidase (maltose-specific)
    "alpha MAN": "EC:3.2.1.24",  # α-mannosidase
    "beta GLU": "EC:3.2.1.21",   # β-glucosidase
    "beta MAN": "EC:3.2.1.25",   # β-mannosidase
    "beta NAG": "EC:3.2.1.52",   # β-N-acetylhexosaminidase
    "ONPG": "EC:3.2.1.23",       # β-galactosidase
}
```

---

### Category 2: MEDIUM FEASIBILITY - Arylamidases (11 enzymes)

**Enzymes**:
- `APPA` - Alanine-phenylalanine-proline arylamidase
- `ArgA` - Arginine arylamidase
- `AspA` - Aspartic acid arylamidase
- `GGA` / `LGA` - Glutamyl glutamic acid arylamidase
- `GlyA` - Glycine arylamidase
- `HisA` - Histidine arylamidase
- `PheA` - Phenylalanine arylamidase
- `ProA` - Proline arylamidase
- `SerA` - Serine arylamidase
- `TyrA` - Tyrosine arylamidase

**Challenge**: Arylamidases are often substrate-specific variants of broader aminopeptidase classes.

**Strategy**:
1. Check if already in `EnzymeMapper.ENZYME_ANNOTATIONS` with GO terms
2. Search ExpASy for "X-arylamidase" or "aminopeptidase"
3. If no specific EC, use general aminopeptidase EC with comment
4. Cross-reference with bioMérieux documentation
5. Document substrate specificity in comments

**Example Mappings**:
```python
{
    "ArgA": "GO:0070006",  # Already has GO term, metalloaminopeptidase
    "ProA": "GO:0016805",  # Already has GO term, dipeptidase activity
    # May not assign EC if too substrate-specific
}
```

---

### Category 3: MEDIUM FEASIBILITY - Reductases (2 enzymes)

**Enzymes**:
- `NO3` - Nitrate reduction (nitrate reductase)
- `NO2` - Nitrite reduction (nitrite reductase)

**Challenge**: Multiple EC numbers exist depending on electron acceptor/donor.

**Strategy**:
1. Search ExpASy for "nitrate reductase" and "nitrite reductase"
2. Identify most common EC for bacterial assays
3. Review bioMérieux documentation for test mechanism
4. May assign multiple EC numbers or most general one
5. Document in comment which EC variant and why

**Expected Mappings**:
```python
{
    "NO3": "EC:1.7.99.4",  # Nitrate reductase (most common bacterial)
    "NO2": ["EC:1.7.2.1", "EC:1.7.5.1"],  # Multiple nitrite reductases
}
```

---

### Category 4: LOW FEASIBILITY - Multi-enzyme Pathways (6 enzymes)

**Enzymes**:
- `GLU_ Ferm` - Glucose fermentation
- `GLU_ Assim` - Glucose assimilation
- `VP` - Voges-Proskauer (acetoin production)
- `H2S` - Hydrogen sulfide production
- `IND` - Indole production
- `N2` - Nitrogen gas production

**Challenge**: These are phenotypic tests for metabolic pathways involving multiple enzymes.

**Strategy**:
1. **DO NOT** assign single EC numbers (scientifically inaccurate)
2. Document as pathway tests in comments
3. Consider adding pathway identifiers (KEGG, MetaCyc) instead
4. Leave EC field as `None` with explanatory comment

**Exception**:
- `IND` (Indole production) - Primarily tryptophanase (EC:4.1.99.1)
  - Can assign EC if bioMérieux docs confirm single enzyme test

---

### Category 5: CASE-BY-CASE - Other (4 enzymes)

**Enzymes**:
- `TRP` - Tryptophane test
- `beta NAG` - β-N-acetyl-glucosaminidase (actually a glycosidase, HIGH feasibility)
- `ONPG` - o-Nitrophenyl-β-D-galactopyranoside (β-galactosidase, HIGH feasibility)
- `beta GP` - β-glycosidase (generic term, may not have specific EC)

**Strategy**: Evaluate individually using ExpASy and bioMérieux docs.

---

## Implementation Plan

### Phase 1: Research and Verification (Deterministic Lookup)

**For each enzyme without EC**:

1. **Lookup in ExpASy ENZYME**
   ```bash
   # Manual or programmatic lookup
   curl "https://enzyme.expasy.org/cgi-bin/enzyme/enzyme-search-ec?field1=DESCRIPTION&search1=alpha-arabinosidase"
   ```

2. **Cross-reference with BRENDA**
   - Verify substrate specificity
   - Check for bacterial-specific variants

3. **Check bioMérieux Documentation**
   - Review downloaded references in `references/`
   - Look for EC numbers mentioned in official docs
   - Check test mechanism description

4. **Validate Against KG-Microbe EC Ontology**
   ```bash
   grep "EC:3.2.1.55" /path/to/ec_nodes.tsv
   ```

5. **Document Findings**
   - Create `EC_LOOKUP_RESULTS.csv` with columns:
     - Code, Enzyme Name, Proposed EC, Source, Validated, Notes

---

### Phase 2: Update mappers.py

**Current Structure**:
```python
# ChemicalMapper
ENZYME_TESTS = {
    "URE": "Urease",  # Just enzyme name, no EC
    ...
}

ENZYME_ACTIVITY_TESTS = {
    "ArgA": "Arginine arylamidase",  # Just enzyme name, no EC
    ...
}
```

**Proposed Update**:

**Option A**: Keep dictionaries simple, add EC in comments
```python
ENZYME_TESTS = {
    "URE": "Urease",  # EC:3.5.1.5
    "IND": "Indole production",  # Tryptophanase, EC:4.1.99.1
    "NO3": "Nitrate reduction",  # EC:1.7.99.4 (nitrate reductase)
    ...
}
```

**Option B**: Convert to nested dicts (breaking change)
```python
ENZYME_TESTS = {
    "URE": {"name": "Urease", "ec": "3.5.1.5"},
    "IND": {"name": "Indole production", "ec": "4.1.99.1"},
    "NO3": {"name": "Nitrate reduction", "ec": "1.7.99.4"},
    ...
}
```

**Option C**: Create new `ENZYME_EC_MAPPINGS` dictionary
```python
# Keep existing dicts unchanged
ENZYME_TESTS = {...}  # unchanged
ENZYME_ACTIVITY_TESTS = {...}  # unchanged

# New mapping
ENZYME_EC_MAPPINGS = {
    "alpha ARA": "3.2.1.55",
    "alpha FUC": "3.2.1.51",
    "alpha GLU": "3.2.1.20",
    ...
}
```

**Recommendation**: Use **Option C** to avoid breaking existing code.

---

### Phase 3: Update Metadata Builder

**File**: `src/bacdive_assay_metadata/metadata_builder.py`

**Current**: Enzyme EC numbers come from `EnzymeMapper.ENZYME_ANNOTATIONS`

**Update**: Add lookup in new `ENZYME_EC_MAPPINGS` dictionary
```python
def _get_enzyme_ec(self, well_code: str) -> Optional[str]:
    """Get EC number for enzyme well code."""
    # Check ENZYME_EC_MAPPINGS first
    if well_code in self.chem_mapper.ENZYME_EC_MAPPINGS:
        return self.chem_mapper.ENZYME_EC_MAPPINGS[well_code]

    # Check ENZYME_ANNOTATIONS (existing logic)
    ...
```

---

### Phase 4: Validation

**Automated Validation**:

1. **EC Ontology Validation**
   ```bash
   make validate
   ```
   - Checks all EC numbers against `ec_nodes.tsv`
   - Flags invalid or deprecated EC numbers

2. **Data-Driven Validation**
   ```bash
   make validate-data
   ```
   - Ensures all enzyme wells have mappings

3. **Coverage Report**
   ```python
   # Generate report showing before/after EC coverage
   Total enzyme wells: 158
   Before: 108/158 (68.4%)
   After: ???/158 (??%)
   ```

**Manual Review**:
- Peer review of EC assignments
- Check against bioMérieux documentation
- Verify no conflicts with existing mappings

---

### Phase 5: Documentation and Commit

**Files to Update**:
1. `src/bacdive_assay_metadata/mappers.py` - Add EC mappings
2. `EC_LOOKUP_RESULTS.csv` - Research documentation
3. `MAPPING_METHODOLOGY.md` - Update with EC assignment process
4. `VALIDATION.md` - Update EC validation stats
5. `README.md` - Update EC coverage statistics

**Commit Message Template**:
```
Add EC numbers for [X] API assay enzymes using deterministic lookup

Phase 1: High-feasibility enzymes (glycosidases)
- Added EC numbers for 9 glycosidase tests
- Sources: ExpASy ENZYME, BRENDA, bioMérieux docs
- All EC numbers validated against KG-Microbe EC ontology

Mappings:
- alpha ARA → EC:3.2.1.55 (α-L-arabinofuranosidase)
- alpha FUC → EC:3.2.1.51 (α-L-fucosidase)
- [... list all]

Result: EC coverage improved from 68.4% to XX%

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Expected Outcomes

### EC Number Coverage Improvement

**Before**:
- Total enzyme wells: 158
- With EC: 108 (68.4%)
- Without EC: 50 (31.6%)

**After (Conservative Estimate)**:
- High feasibility (glycosidases): +9 EC numbers
- Medium feasibility (some arylamidases): +5 EC numbers
- Medium feasibility (reductases): +2 EC numbers
- Low feasibility (pathways): +1 EC number (IND only)
- **Total new EC assignments: ~17**
- **New coverage: 125/158 (79.1%)**

**After (Optimistic Estimate)**:
- All glycosidases: +9
- Most arylamidases (with GO terms): +8
- Reductases: +2
- ONPG, IND, TRP: +3
- **Total new EC assignments: ~22**
- **New coverage: 130/158 (82.3%)**

### Remaining Unmapped

**Will NOT assign EC (scientifically appropriate)**:
- `VP` - Voges-Proskauer (multi-enzyme pathway)
- `H2S` - Hydrogen sulfide production (pathway)
- `N2` - Nitrogen gas production (pathway)
- `GLU_ Ferm` / `GLU_ Assim` - Fermentation/assimilation (pathways)
- Possibly `beta GP` - Too generic

**Total expected unmapped: 5-8 enzymes** (legitimate reasons)

---

## Timeline Estimate

**Phase 1: Research** - 2-3 hours
- Lookup 30 enzymes in ExpASy/BRENDA
- Document findings in CSV
- Cross-reference with bioMérieux docs

**Phase 2: Implementation** - 1 hour
- Update mappers.py with new EC mappings
- Add ENZYME_EC_MAPPINGS dictionary
- Update metadata builder logic

**Phase 3: Validation** - 30 minutes
- Run `make validate`
- Run `make extract`
- Verify EC numbers in output

**Phase 4: Documentation** - 1 hour
- Update methodology docs
- Create EC lookup results CSV
- Write comprehensive commit message

**Total: ~5 hours**

---

## Success Criteria

1. ✅ All high-feasibility enzymes (glycosidases) have EC numbers
2. ✅ All EC numbers validated against KG-Microbe EC ontology
3. ✅ No deprecated EC numbers introduced
4. ✅ All sources documented in code or CSV
5. ✅ EC coverage improved by at least 10 percentage points
6. ✅ No breaking changes to existing mappings
7. ✅ All validation tests pass

---

## Risk Mitigation

**Risk**: Assigning incorrect EC numbers
**Mitigation**: Three-source verification (ExpASy + BRENDA + bioMérieux)

**Risk**: Breaking existing code
**Mitigation**: Use new dictionary instead of modifying existing ones

**Risk**: Deprecated EC numbers
**Mitigation**: Validate against KG-Microbe EC ontology before committing

**Risk**: Substrate-specific vs. general EC conflict
**Mitigation**: Document substrate specificity in comments, use most general applicable EC

---

## Next Steps

1. ✅ **Review and approve this plan**
2. ⏳ **Phase 1**: Begin deterministic EC lookup for glycosidases
3. ⏳ **Phase 2**: Implement ENZYME_EC_MAPPINGS
4. ⏳ **Phase 3**: Validate and test
5. ⏳ **Phase 4**: Document and commit

---

## References

- ExpASy ENZYME: https://enzyme.expasy.org/
- BRENDA: https://www.brenda-enzymes.org/
- IUBMB Enzyme Nomenclature: https://iubmb.qmul.ac.uk/enzyme/
- KG-Microbe EC Ontology: `kg-microbe/data/transformed/ontologies/ec_nodes.tsv`
- bioMérieux References: `references/README.md`
