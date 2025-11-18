# METPO Relation Mapping Report

**Date:** 2025-11-18
**Purpose:** Map BacDive metabolite utilization relations ("kind of utilization tested") to METPO ontology terms

## Summary

- **Total relations:** 25
- **Successfully mapped:** 19/25 (76%)
- **Need manual review:** 6/25 (24%)

---

## ✅ Successfully Mapped Relations (19/25)

### Direct METPO Predicate Matches (2000xxx series)

| BacDive Relation | METPO ID | METPO Term | Description |
|-----------------|----------|------------|-------------|
| assimilation | https://w3id.org/metpo/2000002 | assimilates | - |
| builds acid from | https://w3id.org/metpo/2000003 | builds acid from | - |
| builds base from | https://w3id.org/metpo/2000004 | builds base from | - |
| builds gas from | https://w3id.org/metpo/2000005 | builds gas from | - |
| carbon source | https://w3id.org/metpo/2000006 | uses as carbon source | - |
| degradation | https://w3id.org/metpo/2000007 | degrades | - |
| electron acceptor | https://w3id.org/metpo/2000008 | uses as electron acceptor | - |
| electron donor | https://w3id.org/metpo/2000009 | uses as electron donor | - |
| energy source | https://w3id.org/metpo/2000010 | uses as energy source | - |
| hydrolysis | https://w3id.org/metpo/2000013 | hydrolyzes | - |
| nitrogen source | https://w3id.org/metpo/2000014 | uses as nitrogen source | - |
| other | https://w3id.org/metpo/2000015 | uses in other way | - |
| reduction | https://w3id.org/metpo/2000017 | reduces | - |
| required for growth | https://w3id.org/metpo/2000018 | requires for growth | - |
| sulfur source | https://w3id.org/metpo/2000020 | uses as sulfur source | - |

### Phenotype/Metabolism Matches (1000xxx series)

| BacDive Relation | METPO ID | METPO Term | Description |
|-----------------|----------|------------|-------------|
| aerobic catabolization | https://w3id.org/metpo/1000602 | aerobic | An oxygen preference in which growth occurs in the presence of molecular oxygen (O₂), typically using O₂ as the terminal electron acceptor. |
| aerobic growth | https://w3id.org/metpo/1000602 | aerobic | An oxygen preference in which growth occurs in the presence of molecular oxygen (O₂), typically using O₂ as the terminal electron acceptor. |
| fermentation | https://w3id.org/metpo/1002005 | Fermentation | A respiration that generates energy through the oxidation of organic compounds without using an external electron acceptor, using organic molecules as both electron donors and final electron acceptors. |
| respiration | https://w3id.org/metpo/1000800 | respiration | A metabolism that is characterized by the method of performing cellular respiration, distinguished primarily by the specific terminal electron acceptor utilized for producing cellular energy. |

---

## ⚠️ Relations Needing Manual Review (6/25)

### 1. anaerobic catabolization
**Issue:** No single clear METPO match
**Potential mappings:**
- https://w3id.org/metpo/1000603 (anaerobic)
- https://w3id.org/metpo/1000605 (facultatively anaerobic)
- https://w3id.org/metpo/1000607 (obligately anaerobic)

**Recommendation:** May need to distinguish between facultative and obligate anaerobic catabolization

### 2. anaerobic growth
**Issue:** No single clear METPO match
**Potential mappings:**
- https://w3id.org/metpo/1000603 (anaerobic)
- https://w3id.org/metpo/1000605 (facultatively anaerobic)
- https://w3id.org/metpo/1000607 (obligately anaerobic)

**Recommendation:** Similar to above - may need facultative/obligate distinction

### 3. anaerobic growth in the dark
**Issue:** Combines anaerobic condition with light requirement
**Potential mappings:**
- https://w3id.org/metpo/1000603 (anaerobic)
- Potential compound predicate needed

**Recommendation:** May require composite annotation (anaerobic + photosensitivity)

### 4. anaerobic growth with light
**Issue:** Combines anaerobic condition with light requirement
**Potential mappings:**
- https://w3id.org/metpo/1000603 (anaerobic)
- Related to phototrophy

**Recommendation:** May require composite annotation (anaerobic + phototrophic)

### 5. growth
**Issue:** Too generic - lacks specificity
**Potential mappings:**
- https://w3id.org/metpo/1000535 (growth range phenotype with numerical limits)
- Generic growth observations

**Recommendation:** Context-dependent - may need more specific relation

### 6. oxidation
**Issue:** No direct METPO predicate match found
**Potential mappings:**
- No clear match in METPO 2000xxx predicates
- Could relate to electron donor/acceptor

**Recommendation:** May need new METPO term or use "degrades" or "uses as electron donor"

---

## Recommendations

1. **Add missing METPO predicates:**
   - `oxidizes` (parallel to existing `reduces`)
   - Anaerobic-specific variants (facultative/obligate)
   - Light-dependent growth modifiers

2. **Create composite annotations:**
   - For complex relations like "anaerobic growth with light"
   - Combine oxygen preference + light requirement

3. **Standardize generic terms:**
   - Map generic "growth" to more specific METPO terms based on context
   - Consider adding contextual metadata

---

## Data Coverage

Based on the generated metadata:
- **Total unique metabolites:** 1,243
- **Utilization records:** 881,660
- **Production records:** 23,157
- **Test records:** 0
- **Strains processed:** 99,392

All 25 relation types have been analyzed and 76% have clear METPO mappings.
