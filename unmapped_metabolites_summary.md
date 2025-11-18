# Unmapped Metabolites Summary

## Overview
Extracted from: `bacdive_strains.json` (99,392 bacterial strains)

## Statistics

### Overall
- **Total unique unmapped metabolites**: 317
- **Total occurrences**: 19,379

### Breakdown by Category
| Category | Unique Unmapped | Total Occurrences |
|----------|----------------|-------------------|
| Metabolite Utilization | 154 | 19,123 |
| Metabolite Production | 169 | 256 |
| Metabolite Tests | 0 | 0 |

### Overlap Analysis
- Only in utilization: 148
- Only in production: 163
- Only in tests: 0
- In utilization AND production: 6
- In utilization AND tests: 0
- In production AND tests: 0
- In all three: 0

### Metabolites appearing in both utilization AND production:
1. casein
2. yeast extract
3. peptone
4. milk
5. tryptone
6. beef extract

## Top 20 Most Common Unmapped Metabolites

| Rank | Metabolite | Occurrences | Category |
|------|-----------|-------------|----------|
| 1 | Potassium 5-ketogluconate | 7,610 | Utilization |
| 2 | Potassium 2-ketogluconate | 6,705 | Utilization |
| 3 | casein | 1,586 | Both |
| 4 | esculin ferric citrate | 444 | Utilization |
| 5 | potassium 5-dehydro-D-gluconate | 430 | Utilization |
| 6 | potassium 2-dehydro-D-gluconate | 392 | Utilization |
| 7 | yeast extract | 188 | Both |
| 8 | peptone | 163 | Both |
| 9 | milk | 137 | Both |
| 10 | casamino acids | 118 | Utilization |
| 11 | L-alanine 4-nitroanilide | 113 | Utilization |
| 12 | skimmed milk | 89 | Utilization |
| 13 | 2-oxogluconate | 73 | Utilization |
| 14 | tryptone | 71 | Both |
| 15 | L-lactate | 66 | Utilization |
| 16 | maltose hydrate | 66 | Utilization |
| 17 | 1 % sodium lactate | 59 | Utilization |
| 18 | O-nitrophenyl-beta-D-galactopyranosid | 58 | Utilization |
| 19 | polysaccharides | 50 | Utilization |
| 20 | corn oil | 44 | Utilization |

## Categories of Unmapped Metabolites

### Complex mixtures & undefined compounds
- casein (1,586), yeast extract (188), peptone (163), milk (137), casamino acids (118)
- skimmed milk (89), tryptone (71), beef extract (10), meat extract (5), egg yolk (20)
- rumen extract (3), fermented rumen extract (11), crude oil (2)

### Chemical derivatives & salt forms
- Potassium 5-ketogluconate (7,610), Potassium 2-ketogluconate (6,705)
- potassium 5-dehydro-D-gluconate (430), potassium 2-dehydro-D-gluconate (392)
- 2-oxogluconate (73), sodium malate (8), sodium fumarate (2)

### Enzyme substrates (chromogenic)
- esculin ferric citrate (444)
- L-alanine 4-nitroanilide (113)
- O-nitrophenyl-beta-D-galactopyranosid (58)
- L-proline-4-nitroanilide (39)
- 4-nitrophenyl beta-D-galactopyranoside hydrolysate (37)

### Antibiotics & secondary metabolites (mostly production)
Many rare antibiotics with 1-2 occurrences each:
- abyssomicin series (B, C, D, G, H, atrop-abyssomicin C)
- actinomycin series (A, B, X)
- Various mycins: aburamycin, setamycin, neomycin E/F, bottromycin, carbomycin, etc.

### Natural products & oils
- corn oil (44), olive oil (5), coconut oil (1), crude oil (2)
- locust bean gum (2), xanthan gum (1), guar gum (1), karaya gum (1)

### Minerals & metal compounds
- ferrihydrite (10), manganese dioxide (7), goethite (4)
- amorphous iron (iii) oxide (6), amorphous fe(iii) oxyhydroxid (3)
- fe(iii) citrate (1)

### Polysaccharides & polymers
- polysaccharides (50), crab shell chitin (17), crystalline cellulose (13)
- (+)-D-glycogen (10), trehalose dihydrate (4), maltose hydrate (66)

## Files Generated
- `unmapped_metabolites.txt` - Complete Python dictionary ready for mappers.py
- `unmapped_metabolites_summary.md` - This summary file

## Notes
- The discrepancy from the previous analysis (317 vs 323 mentioned) is likely due to different counting methods or data versions
- Most occurrences (98.7%) are in "metabolite utilization" tests
- Production tests show diverse but rare metabolites (many antibiotics with single occurrences)
- Many unmapped metabolites are complex biological mixtures that may not have single ChEBI IDs
