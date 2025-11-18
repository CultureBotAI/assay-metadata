"""Parser for extracting API assay data from BacDive JSON."""

import json
from pathlib import Path
from typing import Any
from collections import defaultdict
from tqdm import tqdm


class BacDiveParser:
    """Parse BacDive JSON data to extract API assay information."""

    # Known API kit prefixes
    API_KIT_PREFIXES = ["API "]

    def __init__(self, json_path: str | Path):
        """Initialize parser with path to BacDive JSON file.

        Args:
            json_path: Path to bacdive_strains.json file
        """
        self.json_path = Path(json_path)
        self.api_kits: dict[str, dict[str, Any]] = {}
        self.wells: dict[str, set[str]] = defaultdict(set)  # well_code -> {kit_names}
        self.enzymes: dict[str, dict[str, Any]] = {}
        self.kit_occurrences: dict[str, int] = defaultdict(int)

    def parse(self) -> dict[str, Any]:
        """Parse the BacDive JSON file and extract API assay metadata.

        Returns:
            Dictionary containing extracted API kits, wells, and enzymes
        """
        print(f"Parsing {self.json_path}...")

        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_strains = len(data)
        print(f"Processing {total_strains:,} bacterial strains...")

        # Process each strain
        for strain in tqdm(data, desc="Extracting API assays"):
            self._process_strain(strain)

        print(f"\nFound {len(self.api_kits)} unique API kit types")
        print(f"Found {len(self.wells)} unique wells/tests")
        print(f"Found {len(self.enzymes)} unique enzymes")

        return {
            "api_kits": self.api_kits,
            "wells": self.wells,
            "enzymes": self.enzymes,
            "kit_occurrences": dict(self.kit_occurrences),
            "total_strains": total_strains,
        }

    def _process_strain(self, strain: dict[str, Any]) -> None:
        """Process a single strain record.

        Args:
            strain: Strain data dictionary
        """
        # Extract from "Physiology and metabolism" section
        physiology = strain.get("Physiology and metabolism", {})
        if not physiology:
            return

        # Process enzymes section
        enzymes = physiology.get("enzymes", [])
        if enzymes:
            self._process_enzymes(enzymes)

        # Process API assay sections
        for key, value in physiology.items():
            if key.startswith("API "):
                self._process_api_assay(key, value)

    def _process_enzymes(self, enzymes: list[dict[str, Any]]) -> None:
        """Process enzyme data.

        Args:
            enzymes: List of enzyme records
        """
        for enzyme in enzymes:
            if not isinstance(enzyme, dict):
                continue

            name = enzyme.get("value", "").strip()
            ec_number = enzyme.get("ec", "").strip()

            if name and name not in self.enzymes:
                self.enzymes[name] = {
                    "name": name,
                    "ec_number": ec_number if ec_number else None,
                    "activity_values": set()
                }

            # Track activity values
            activity = enzyme.get("activity", "").strip()
            if activity:
                self.enzymes[name]["activity_values"].add(activity)

    def _process_api_assay(self, kit_name: str, data: Any) -> None:
        """Process an API assay kit result.

        Args:
            kit_name: Name of the API kit (e.g., "API zym")
            data: The assay data (dict or list of dicts)
        """
        # Increment occurrence count
        self.kit_occurrences[kit_name] += 1

        # Handle both single dict and list of dicts
        assay_results = [data] if isinstance(data, dict) else data
        if not isinstance(assay_results, list):
            return

        for assay in assay_results:
            if not isinstance(assay, dict):
                continue

            # Extract well codes (exclude @ref metadata)
            wells = [k for k in assay.keys() if not k.startswith("@")]

            # Store kit information
            if kit_name not in self.api_kits:
                self.api_kits[kit_name] = {
                    "name": kit_name,
                    "wells": wells,
                    "well_count": len(wells),
                }

            # Track which kits use which wells
            for well_code in wells:
                self.wells[well_code].add(kit_name)

    def get_kit_descriptions(self) -> dict[str, str]:
        """Get descriptions for API kits based on their names.

        Returns:
            Dictionary mapping kit names to descriptions
        """
        descriptions = {
            "API zym": "Enzyme activity testing for 19 different enzymes using chromogenic substrates",
            "API 50CHac": "Carbohydrate acidification (fermentation) test with 50 different carbohydrates",
            "API 50CHas": "Carbohydrate assimilation test with 50 different carbohydrates",
            "API 20NE": "Identification system for non-Enterobacteriaceae Gram-negative bacteria",
            "API 20E": "Identification system for Enterobacteriaceae and other Gram-negative bacteria",
            "API rID32STR": "Rapid identification of Streptococcus species with 32 tests",
            "API biotype100": "Comprehensive biochemical profiling with 99 different tests",
            "API coryne": "Identification of Corynebacterium and related bacteria",
            "API rID32A": "Rapid identification of anaerobic bacteria with 32 tests",
            "API ID32E": "Extended identification of Enterobacteriaceae with 32 tests",
            "API NH": "Identification of Neisseria, Haemophilus and related organisms",
            "API ID32STA": "Identification of Staphylococcus and related cocci with 32 tests",
            "API CAM": "Identification of Campylobacter species",
            "API 20STR": "Identification of Streptococcus species with 20 tests",
            "API LIST": "Identification of Listeria species",
            "API STA": "Identification of Staphylococcus species",
            "API 20A": "Identification of anaerobic bacteria with 20 tests",
        }
        return descriptions

    def get_kit_categories(self) -> dict[str, str]:
        """Get category classifications for API kits.

        Returns:
            Dictionary mapping kit names to categories
        """
        categories = {
            "API zym": "Enzyme profiling",
            "API 50CHac": "Carbohydrate fermentation",
            "API 50CHas": "Carbohydrate assimilation",
            "API 20NE": "Bacterial identification",
            "API 20E": "Bacterial identification",
            "API rID32STR": "Bacterial identification",
            "API biotype100": "Biochemical profiling",
            "API coryne": "Bacterial identification",
            "API rID32A": "Bacterial identification",
            "API ID32E": "Bacterial identification",
            "API NH": "Bacterial identification",
            "API ID32STA": "Bacterial identification",
            "API CAM": "Bacterial identification",
            "API 20STR": "Bacterial identification",
            "API LIST": "Bacterial identification",
            "API STA": "Bacterial identification",
            "API 20A": "Bacterial identification",
        }
        return categories
