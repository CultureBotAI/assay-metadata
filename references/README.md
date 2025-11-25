# API Kit Reference Documents

This directory contains publicly available reference documents used for validating and documenting API assay well code mappings.

**Note**: These files are not committed to the repository (listed in `.gitignore`) but can be re-downloaded using the URLs below.

---

## API 20E - Enterobacteriaceae Identification

### API_20E_MicrobeOnline.html
- **Source**: Microbe Online educational resource
- **URL**: https://microbeonline.com/api-20e-test-system/
- **Description**: Comprehensive guide to API 20E test system, including test principles, procedures, and interpretation
- **File Size**: ~116K
- **Content**:
  - Well-by-well test descriptions
  - Substrate information
  - Interpretation guidelines
  - Quality control procedures

---

## API 20NE - Non-Enterobacteriaceae Gram-Negative Identification

### API_20NE_Instructions_FIU.pdf
- **Source**: Florida International University Microbiology Lab Manual
- **URL**: https://faculty.fiu.edu/~makemson/MCB3020Lab/API20neInstructions.pdf
- **Description**: Official lab instructions for API 20NE test system
- **File Size**: ~203K
- **Content**:
  - Complete well code list with substrate names
  - Step-by-step procedures
  - Result interpretation
  - Expected reactions

### API_20NE_MicrobeOnline.html
- **Source**: Microbe Online educational resource
- **URL**: https://microbeonline.com/api-20ne-test-principle-procedure-results/
- **Description**: Educational guide for API 20NE test system
- **File Size**: ~79K
- **Content**:
  - Test principles
  - Well descriptions
  - Procedure overview
  - Result interpretation

---

## API zym - Enzyme Activity Profiling

### API_zym_MicrobeOnline.html
- **Source**: Microbe Online educational resource
- **URL**: https://microbeonline.com/api-zym-test-principle-procedure-results/
- **Description**: Guide to API zym enzyme activity test system
- **File Size**: ~78K
- **Content**:
  - 19 enzyme tests description
  - Chromogenic substrate information
  - Interpretation of enzyme activities
  - Application in bacterial identification

---

## Usage in This Project

These reference documents are used to:

1. **Validate well code mappings** - Cross-reference our mappings in `mappers.py` against official documentation
2. **Verify substrate identities** - Confirm chemical names and identifiers (CHEBI, PubChem)
3. **Document provenance** - Provide traceable sources for all mappings
4. **Resolve ambiguities** - Clarify context-dependent codes that vary between kits

All mappings in `src/bacdive_assay_metadata/mappers.py` are based on these official sources and are validated using:
- `make validate-api` - Cross-reference with official well code definitions
- `make validate` - Validate identifiers against CHEBI/EC/GO ontologies
- `make validate-data` - Validate against actual extracted BacDive data

---

## Re-downloading References

To re-download these files:

```bash
# API 20E guide
curl -L "https://microbeonline.com/api-20e-test-system/" \
  -o "references/API_20E_MicrobeOnline.html"

# API 20NE instructions (FIU)
curl -L "https://faculty.fiu.edu/~makemson/MCB3020Lab/API20neInstructions.pdf" \
  -o "references/API_20NE_Instructions_FIU.pdf"

# API 20NE guide
curl -L "https://microbeonline.com/api-20ne-test-principle-procedure-results/" \
  -o "references/API_20NE_MicrobeOnline.html"

# API zym guide
curl -L "https://microbeonline.com/api-zym-test-principle-procedure-results/" \
  -o "references/API_zym_MicrobeOnline.html"
```

---

## Official bioMérieux Documentation

The official bioMérieux package inserts (product documentation shipped with kits) are **not publicly available online** and are therefore not included in this directory. However, the hard-coded reference mappings in `src/bacdive_assay_metadata/validate_api_kits.py` are based on these official sources:

- API 20E Package Insert (REF 20 100/20 160)
- API 20NE Package Insert (REF 20 050)
- API zym Package Insert
- API 50CHac Documentation

These official definitions are cited in the code with source references and are used as the ground truth for validation.

---

## Additional Resources

### CHEBI Database
- **URL**: https://www.ebi.ac.uk/chebi/
- **Usage**: Chemical identifier validation and lookup

### PubChem Database
- **URL**: https://pubchem.ncbi.nlm.nih.gov/
- **Usage**: Alternative chemical identifiers and cross-references

### Enzyme Database (EC Numbers)
- **URL**: https://www.enzyme-database.org/
- **Usage**: Enzyme classification and nomenclature

### RHEA Reactions Database
- **URL**: https://www.rhea-db.org/
- **Usage**: Enzyme-catalyzed reaction identifiers

---

## Maintenance

**Last Updated**: 2025-11-24

These reference documents should be periodically checked for updates, especially if:
- New API kit types are added to BacDive
- bioMérieux updates their test systems
- Educational resources are moved or updated
- New official documentation becomes available

To check if URLs are still valid, run:
```bash
for file in references/*.html; do
    echo "Checking $file..."
    # URLs are documented in this README
done
```
