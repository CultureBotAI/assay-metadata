# Simplified API Assay Output Format

## Overview

The simplified output format nests wells directly within each API kit, with **all values as lists** for consistent processing.

## File Location

`data/assay_kits_simple.json` (generated with `--simple` flag)

## Structure

```json
{
  "api_kits": [
    {
      "kit_name": "API zym",
      "description": "Enzyme activity testing for 19 different enzymes...",
      "category": "Enzyme profiling",
      "well_count": 20,
      "occurrence_count": 11747,
      "wells": [
        {
          "name": "Alkaline phosphatase",
          "label": ["Alkaline phosphatase"],
          "type": ["enzyme"],
          "description": ["Tests for Alkaline phosphatase activity"],
          
          "enzyme_name": ["Alkaline phosphatase"],
          "ec_number": ["3.1.3.1"],
          "ec_name": [],
          "go_terms": ["GO:0004035"],
          "go_names": ["alkaline phosphatase activity"],
          "kegg_ko": ["K01077"],
          "kegg_reaction": [],
          "rhea_ids": [],
          "metacyc_reaction": [],
          "metacyc_pathway": [],
          
          "chebi_id": [],
          "chebi_name": [],
          "pubchem_cid": [],
          "pubchem_name": [],
          "inchi": [],
          "smiles": []
        }
      ]
    }
  ]
}
```

## Key Features

### 1. **All Values Are Lists**
- Scalars become single-element lists: `"ec_number": ["3.1.3.1"]`
- Lists stay as lists: `"go_terms": ["GO:0004035"]`
- Empty/null values become empty lists: `"rhea_ids": []`
- **Exception**: `"name"` is always a scalar (well code)

### 2. **Flat Structure**
- No nested `chemical_ids` or `enzyme_ids` objects
- All identifiers at the same level
- Easy to process row-by-row

### 3. **Wells Repeated Per Kit**
- Same well appears in multiple kits (e.g., GLU in 11 kits)
- Total: 503 well entries across 17 kits
- Enables kit-specific processing

## Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | scalar | Well code (unique identifier) | `"GLU"` |
| `label` | list | Human-readable name | `["D-Glucose"]` |
| `type` | list | Well type | `["substrate"]` or `["enzyme"]` or `["phenotypic"]` |
| `description` | list | What the test measures | `["Tests for..."]` |
| **Chemical Identifiers** | | | |
| `chebi_id` | list | CHEBI ontology ID | `["CHEBI:17234"]` |
| `chebi_name` | list | CHEBI chemical name | `["D-Glucose"]` |
| `pubchem_cid` | list | PubChem compound ID | `["5793"]` |
| `pubchem_name` | list | PubChem name | `["D-Glucose"]` |
| `inchi` | list | InChI identifier | `[]` (future) |
| `smiles` | list | SMILES notation | `[]` (future) |
| **Enzyme Identifiers** | | | |
| `enzyme_name` | list | Common enzyme name | `["Urease"]` |
| `ec_number` | list | EC classification | `["3.5.1.5"]` |
| `ec_name` | list | EC enzyme name | `[]` (future) |
| `go_terms` | list | GO molecular function IDs | `["GO:0009039"]` |
| `go_names` | list | GO term names | `["urease activity"]` |
| `kegg_ko` | list | KEGG Orthology ID | `["K01428"]` |
| `kegg_reaction` | list | KEGG Reaction ID | `[]` (future) |
| `rhea_ids` | list | RHEA reaction IDs | `[]` (API issues) |
| `metacyc_reaction` | list | MetaCyc reaction ID | `[]` (future) |
| `metacyc_pathway` | list | MetaCyc pathway IDs | `[]` (future) |

## Examples

### Enzyme Well (Alkaline phosphatase)

```json
{
  "name": "Alkaline phosphatase",
  "label": ["Alkaline phosphatase"],
  "type": ["enzyme"],
  "description": ["Tests for Alkaline phosphatase activity"],
  "enzyme_name": ["Alkaline phosphatase"],
  "ec_number": ["3.1.3.1"],
  "ec_name": [],
  "go_terms": ["GO:0004035"],
  "go_names": ["alkaline phosphatase activity"],
  "kegg_ko": ["K01077"],
  "kegg_reaction": [],
  "rhea_ids": [],
  "metacyc_reaction": [],
  "metacyc_pathway": [],
  "chebi_id": [],
  "chebi_name": [],
  "pubchem_cid": [],
  "pubchem_name": [],
  "inchi": [],
  "smiles": []
}
```

### Substrate Well (GLU - Glucose)

```json
{
  "name": "GLU",
  "label": ["D-Glucose"],
  "type": ["substrate"],
  "description": ["Tests for utilization/fermentation of D-Glucose"],
  "enzyme_name": [],
  "ec_number": [],
  "ec_name": [],
  "go_terms": [],
  "go_names": [],
  "kegg_ko": [],
  "kegg_reaction": [],
  "rhea_ids": [],
  "metacyc_reaction": [],
  "metacyc_pathway": [],
  "chebi_id": ["CHEBI:17234"],
  "chebi_name": ["D-Glucose"],
  "pubchem_cid": ["5793"],
  "pubchem_name": ["D-Glucose"],
  "inchi": [],
  "smiles": []
}
```

### Phenotypic Well (Control)

```json
{
  "name": "Control",
  "label": ["Control well (no substrate)"],
  "type": ["phenotypic"],
  "description": ["Phenotypic test: Control well (no substrate)"],
  "enzyme_name": [],
  "ec_number": [],
  "ec_name": [],
  "go_terms": [],
  "go_names": [],
  "kegg_ko": [],
  "kegg_reaction": [],
  "rhea_ids": [],
  "metacyc_reaction": [],
  "metacyc_pathway": [],
  "chebi_id": [],
  "chebi_name": [],
  "pubchem_cid": [],
  "pubchem_name": [],
  "inchi": [],
  "smiles": []
}
```

## Usage

### Generate Simplified Output

```bash
uv run extract-metadata --simple --pretty
```

### Processing in Python

```python
import json

data = json.load(open('data/assay_kits_simple.json'))

for kit in data['api_kits']:
    print(f"Kit: {kit['kit_name']} ({kit['well_count']} wells)")
    
    for well in kit['wells']:
        # All values are lists - consistent processing
        if well['go_terms']:  # Has GO annotation
            print(f"  {well['name']}: GO:{well['go_terms'][0]}")
        
        if well['chebi_id']:  # Has chemical annotation
            print(f"  {well['name']}: CHEBI:{well['chebi_id'][0]}")
```

### Processing in R

```r
library(jsonlite)

data <- fromJSON('data/assay_kits_simple.json')

# Convert to data frame
wells_df <- do.call(rbind, lapply(data$api_kits, function(kit) {
  wells <- kit$wells
  wells$kit_name <- kit$kit_name
  wells
}))

# Filter wells with GO annotations
go_wells <- wells_df[lengths(wells_df$go_terms) > 0, ]
```

## Statistics

| Metric | Value |
|--------|-------|
| API Kits | 17 unique types |
| Total Well Entries | 503 (wells repeated per kit) |
| Unique Wells | 218 (deduplicated) |
| File Size | ~410 KB |
| Format | JSON with all values as lists |

## Advantages

1. **Consistent Processing**: All values are lists, no type checking needed
2. **Easy Iteration**: Simple loop over kits and wells
3. **Kit-Specific**: Wells appear in context of each kit
4. **Flat Schema**: No nested objects, direct access to all fields
5. **Tabular-Ready**: Can easily convert to CSV/TSV/DataFrame

## Differences from Standard Output

| Feature | Standard Output | Simplified Output |
|---------|----------------|-------------------|
| Structure | Wells at top level | Wells nested in kits |
| Redundancy | 218 unique wells | 503 well entries (repeated) |
| Value Types | Mixed (scalars & lists) | All lists |
| Nesting | `enzyme_ids.go_terms` | `go_terms` (flat) |
| Use Case | Knowledge graphs | Tabular processing |

## Generation

```bash
# Both formats simultaneously
uv run extract-metadata --pretty --simple

# Outputs:
# - data/assay_metadata.json (standard)
# - data/assay_kits_simple.json (simplified)
```
