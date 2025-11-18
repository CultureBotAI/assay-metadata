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

        # Metabolite sections
        self.metabolites: dict[str, dict[str, Any]] = {}  # metabolite_name -> {data}
        self.metabolite_utilization: list[dict[str, Any]] = []  # All utilization records
        self.metabolite_production: list[dict[str, Any]] = []  # All production records
        self.metabolite_tests: list[dict[str, Any]] = []  # All test records

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
        print(f"Found {len(self.metabolites)} unique metabolites")
        print(f"  - Utilization records: {len(self.metabolite_utilization)}")
        print(f"  - Production records: {len(self.metabolite_production)}")
        print(f"  - Test records: {len(self.metabolite_tests)}")

        return {
            "api_kits": self.api_kits,
            "wells": self.wells,
            "enzymes": self.enzymes,
            "metabolites": self.metabolites,
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

        # Process metabolite sections
        metabolite_util = physiology.get("metabolite utilization", [])
        if metabolite_util:
            self._process_metabolite_utilization(metabolite_util)

        metabolite_prod = physiology.get("metabolite production", [])
        if metabolite_prod:
            self._process_metabolite_production(metabolite_prod)

        metabolite_tests = physiology.get("metabolite tests", {})
        if metabolite_tests:
            self._process_metabolite_tests(metabolite_tests)

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

    def _process_metabolite_utilization(self, utilization_data: list[dict[str, Any]]) -> None:
        """Process metabolite utilization data.

        Args:
            utilization_data: List of metabolite utilization records
        """
        for record in utilization_data:
            if not isinstance(record, dict):
                continue

            metabolite_name = record.get("metabolite", "").strip()
            if not metabolite_name:
                continue

            chebi_id = record.get("Chebi-ID")
            test_type = record.get("kind of utilization tested", "").strip()

            # Store raw record
            self.metabolite_utilization.append({
                "metabolite": metabolite_name,
                "chebi_id": chebi_id,
                "test_type": test_type,
                "activity": record.get("utilization activity", "").strip()
            })

            # Aggregate in metabolites dict
            if metabolite_name not in self.metabolites:
                self.metabolites[metabolite_name] = {
                    "name": metabolite_name,
                    "chebi_id": chebi_id,
                    "utilization_test_types": set(),
                    "production_values": set(),
                    "test_names": set(),
                    "utilization_count": 0,
                    "production_count": 0,
                    "test_count": 0
                }

            if test_type:
                self.metabolites[metabolite_name]["utilization_test_types"].add(test_type)
            self.metabolites[metabolite_name]["utilization_count"] += 1

    def _process_metabolite_production(self, production_data: list[dict[str, Any]]) -> None:
        """Process metabolite production data.

        Args:
            production_data: List of metabolite production records
        """
        for record in production_data:
            if not isinstance(record, dict):
                continue

            metabolite_name = record.get("metabolite", "").strip()
            if not metabolite_name:
                continue

            chebi_id = record.get("Chebi-ID")
            production_value = record.get("production", "").strip()

            # Store raw record
            self.metabolite_production.append({
                "metabolite": metabolite_name,
                "chebi_id": chebi_id,
                "production": production_value
            })

            # Aggregate in metabolites dict
            if metabolite_name not in self.metabolites:
                self.metabolites[metabolite_name] = {
                    "name": metabolite_name,
                    "chebi_id": chebi_id,
                    "utilization_test_types": set(),
                    "production_values": set(),
                    "test_names": set(),
                    "utilization_count": 0,
                    "production_count": 0,
                    "test_count": 0
                }

            if production_value:
                self.metabolites[metabolite_name]["production_values"].add(production_value)
            self.metabolites[metabolite_name]["production_count"] += 1

    def _process_metabolite_tests(self, test_data: dict[str, Any] | list[dict[str, Any]]) -> None:
        """Process metabolite test data.

        Args:
            test_data: Dictionary of metabolite test records or list of records
        """
        # Handle case where test_data is a list instead of a dict
        if isinstance(test_data, list):
            # Skip lists - we only process dict-based test data
            return

        for test_name, records in test_data.items():
            if test_name.startswith("@") or not isinstance(records, list):
                continue

            for record in records:
                if not isinstance(record, dict):
                    continue

                metabolite_name = record.get("metabolite", "").strip()
                if not metabolite_name:
                    continue

                chebi_id = record.get("Chebi-ID")
                test_value = record.get(test_name, "").strip()

                # Store raw record
                self.metabolite_tests.append({
                    "test_name": test_name,
                    "metabolite": metabolite_name,
                    "chebi_id": chebi_id,
                    "test_value": test_value
                })

                # Aggregate in metabolites dict
                if metabolite_name not in self.metabolites:
                    self.metabolites[metabolite_name] = {
                        "name": metabolite_name,
                        "chebi_id": chebi_id,
                        "utilization_test_types": set(),
                        "production_values": set(),
                        "test_names": set(),
                        "utilization_count": 0,
                        "production_count": 0,
                        "test_count": 0
                    }

                self.metabolites[metabolite_name]["test_names"].add(test_name)
                self.metabolites[metabolite_name]["test_count"] += 1

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
