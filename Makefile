.PHONY: help install extract validate validate-full track-files clean test all

# Default target
help:
	@echo "BacDive Assay Metadata - Available targets:"
	@echo ""
	@echo "  install         - Install package with uv"
	@echo "  extract         - Extract metadata from BacDive data"
	@echo "  validate        - Validate using ontology files (CHEBI, EC, GO) - RECOMMENDED"
	@echo "  validate-full   - Validate all mappings with API calls (KEGG, PubChem) - SLOW"
	@echo "  track-files     - Track ontology file versions (hashes)"
	@echo "  clean           - Clean generated files"
	@echo "  test            - Run tests"
	@echo "  all             - Install, extract, and validate"
	@echo ""

# Install package
install:
	uv sync

# Extract metadata
extract: install
	@echo "Extracting metadata from BacDive data..."
	uv run extract-metadata --pretty --simple
	@echo "✅ Extraction complete!"

# Validate using ontology files only (RECOMMENDED)
validate: install
	@echo "Validating curated mappings using ontology files..."
	@echo "ℹ️  Validates CHEBI, EC, and GO terms from local TSV files"
	@echo "ℹ️  Use 'make validate-full' for complete validation with API calls"
	uv run validate-fast
	@echo ""
	@echo "Results:"
	@echo "  - validation_report.json"
	@echo "  - ontology_file_metadata.json"

# Validate all mappings (includes API calls - SLOW)
validate-full: install
	@echo "Validating ALL curated mappings (includes API calls)..."
	@echo "⚠️  This will make API calls to PubChem and KEGG (rate-limited, ~20 min)"
	uv run validate-mappings
	@echo ""
	@echo "Results:"
	@echo "  - validation_report.json"
	@echo "  - ontology_file_metadata.json"

# Track ontology file versions only
track-files: install
	@echo "Tracking ontology file versions..."
	uv run python3 -c "from bacdive_assay_metadata.validate_mappings import track_ontology_files; from pathlib import Path; track_ontology_files(Path('/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/kg-microbe/data/transformed/ontologies'), Path('ontology_file_metadata.json'))"

# Clean generated files
clean:
	rm -f data/*.json
	rm -f validation_report.json
	rm -f ontology_file_metadata.json
	rm -f rhea_cache.json
	rm -rf __pycache__
	rm -rf src/**/__pycache__
	rm -rf .pytest_cache
	@echo "✅ Cleaned generated files"

# Run tests
test: install
	uv run pytest -v

# Complete pipeline
all: install extract validate
	@echo "✅ Complete pipeline finished!"
