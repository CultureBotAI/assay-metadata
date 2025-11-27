"""Build comprehensive metadata from parsed BacDive data."""

from pathlib import Path
from typing import Any, Optional
from tqdm import tqdm

from .parser import BacDiveParser
from .mappers import ChemicalMapper, EnzymeMapper, normalize_well_code
from .models import (
    APIKitMetadata,
    AssayMetadata,
    ChemicalIdentifiers,
    EnzymeIdentifiers,
    MetaboliteIdentifiers,
    WellMetadata,
)


class MetadataBuilder:
    """Build comprehensive assay metadata with identifier mappings."""

    def __init__(self, json_path: str | Path):
        """Initialize metadata builder.

        Args:
            json_path: Path to BacDive JSON file
        """
        self.json_path = Path(json_path)
        self.parser = BacDiveParser(json_path)
        self.chem_mapper = ChemicalMapper()
        self.enzyme_mapper = EnzymeMapper()

    def build(self) -> AssayMetadata:
        """Build complete assay metadata.

        Returns:
            AssayMetadata object with all kits, wells, and enzymes
        """
        print("=" * 70)
        print("BacDive API Assay Metadata Builder")
        print("=" * 70)

        # Step 1: Parse BacDive data
        parsed_data = self.parser.parse()

        # Step 2: Build API kit metadata
        print("\nBuilding API kit metadata...")
        api_kits = self._build_api_kits(parsed_data)

        # Step 3: Build well metadata
        print("Building well metadata with identifier mappings...")
        wells = self._build_wells(parsed_data, api_kits)

        # Step 4: Build enzyme metadata
        print("Building enzyme metadata with RHEA mappings...")
        enzymes = self._build_enzymes(parsed_data)

        # Step 5: Build metabolite metadata
        print("Building metabolite metadata with CHEBI/PubChem mappings...")
        metabolites = self._build_metabolites(parsed_data)

        # Step 6: Compile statistics
        statistics = {
            "total_strains": parsed_data["total_strains"],
            "total_api_kits": len(api_kits),
            "total_unique_wells": len(wells),
            "total_unique_enzymes": len(enzymes),
            "total_unique_metabolites": len(metabolites),
            "total_kit_occurrences": sum(kit.occurrence_count for kit in api_kits),
        }

        print("\n" + "=" * 70)
        print("Metadata generation complete!")
        print("=" * 70)
        print(f"API Kits: {statistics['total_api_kits']}")
        print(f"Unique Wells: {statistics['total_unique_wells']}")
        print(f"Unique Enzymes: {statistics['total_unique_enzymes']}")
        print(f"Unique Metabolites: {statistics['total_unique_metabolites']}")
        print(f"Total Strains: {statistics['total_strains']:,}")
        print("=" * 70)

        return AssayMetadata(
            api_kits=api_kits,
            wells=wells,
            enzymes=enzymes,
            metabolites=metabolites,
            statistics=statistics,
        )

    def _build_api_kits(self, parsed_data: dict[str, Any]) -> list[APIKitMetadata]:
        """Build API kit metadata list.

        Args:
            parsed_data: Parsed data from BacDiveParser

        Returns:
            List of APIKitMetadata objects
        """
        api_kits = []
        descriptions = self.parser.get_kit_descriptions()
        categories = self.parser.get_kit_categories()

        for kit_name, kit_data in parsed_data["api_kits"].items():
            api_kit = APIKitMetadata(
                kit_name=kit_name,
                description=descriptions.get(kit_name, "Unknown API kit"),
                category=categories.get(kit_name, "Unknown"),
                well_count=kit_data["well_count"],
                wells=kit_data["wells"],
                occurrence_count=parsed_data["kit_occurrences"].get(kit_name, 0),
            )
            api_kits.append(api_kit)

        # Sort by occurrence count (most common first)
        api_kits.sort(key=lambda x: x.occurrence_count, reverse=True)

        return api_kits

    def _build_wells(
        self,
        parsed_data: dict[str, Any],
        api_kits: list[APIKitMetadata]
    ) -> dict[str, WellMetadata]:
        """Build well metadata with chemical/enzyme identifiers.

        Args:
            parsed_data: Parsed data from BacDiveParser
            api_kits: List of API kit metadata

        Returns:
            Dictionary mapping well codes to WellMetadata
        """
        wells = {}

        for well_code, kit_names in tqdm(
            parsed_data["wells"].items(),
            desc="Processing wells"
        ):
            # Determine well type and get identifiers
            well_type, chem_ids, enzyme_ids = self._classify_well(well_code)

            # Create human-readable label
            label = self._create_well_label(well_code)

            # Get description
            description = self._get_well_description(well_code, well_type)

            wells[well_code] = WellMetadata(
                code=well_code,
                label=label,
                well_type=well_type,
                description=description,
                chemical_ids=chem_ids,
                enzyme_ids=enzyme_ids,
                used_in_kits=sorted(list(kit_names)),
            )

        return wells

    def _classify_well(
        self, well_code: str
    ) -> tuple[str, Optional[ChemicalIdentifiers], Optional[EnzymeIdentifiers]]:
        """Classify a well and get appropriate identifiers.

        Args:
            well_code: Well code

        Returns:
            Tuple of (well_type, chemical_ids, enzyme_ids)
        """
        # Try both original and normalized codes for matching
        normalized = normalize_well_code(well_code)

        # Check if it's an enzyme test (try original code first, then normalized)
        enzyme_name = None
        if well_code in self.chem_mapper.ENZYME_TESTS:
            enzyme_name = self.chem_mapper.ENZYME_TESTS[well_code]
        elif well_code in self.chem_mapper.ENZYME_ACTIVITY_TESTS:
            enzyme_name = self.chem_mapper.ENZYME_ACTIVITY_TESTS[well_code]
        elif normalized in self.chem_mapper.ENZYME_TESTS:
            enzyme_name = self.chem_mapper.ENZYME_TESTS[normalized]
        elif normalized in self.chem_mapper.ENZYME_ACTIVITY_TESTS:
            enzyme_name = self.chem_mapper.ENZYME_ACTIVITY_TESTS[normalized]

        if enzyme_name:
            # Check if EC number is in ENZYME_EC_MAPPINGS (for codes without EC in ENZYME_ANNOTATIONS)
            ec_from_mapping = self.chem_mapper.ENZYME_EC_MAPPINGS.get(well_code)
            if not ec_from_mapping:
                ec_from_mapping = self.chem_mapper.ENZYME_EC_MAPPINGS.get(normalized)

            # Check if GO term mapping exists (for tests without EC numbers)
            go_mapping = self.chem_mapper.GO_TERM_MAPPINGS.get(well_code)
            if not go_mapping:
                go_mapping = self.chem_mapper.GO_TERM_MAPPINGS.get(normalized)

            enzyme_info = self.enzyme_mapper.get_enzyme_info(enzyme_name, ec_from_mapping)

            # If no EC found but GO mapping exists, use GO terms
            if not (enzyme_info.get("ec_number") or ec_from_mapping) and go_mapping:
                enzyme_ids = EnzymeIdentifiers(
                    ec_number=None,
                    ec_name=None,
                    rhea_ids=[],
                    enzyme_name=enzyme_name,
                    go_terms=[go_mapping["go_id"]],
                    go_names=[go_mapping["go_name"]],
                    kegg_ko=None,
                    kegg_reaction=None,
                    metacyc_reaction=None,
                    metacyc_pathway=[],
                )
            else:
                # Standard enzyme IDs with EC (or GO from enzyme_info)
                enzyme_ids = EnzymeIdentifiers(
                    ec_number=enzyme_info.get("ec_number") or ec_from_mapping,  # Use mapping if get_enzyme_info returns None
                    ec_name=enzyme_info.get("ec_name"),
                    rhea_ids=enzyme_info.get("rhea_ids", []),
                    enzyme_name=enzyme_name,
                    go_terms=enzyme_info.get("go_terms", []),
                    go_names=enzyme_info.get("go_names", []),
                    kegg_ko=enzyme_info.get("kegg_ko"),
                    kegg_reaction=enzyme_info.get("kegg_reaction"),
                    metacyc_reaction=enzyme_info.get("metacyc_reaction"),
                    metacyc_pathway=enzyme_info.get("metacyc_pathway", []),
                )
            return "enzyme", None, enzyme_ids

        # Check if it's a phenotypic test
        if well_code in self.chem_mapper.PHENOTYPIC_TESTS or normalized in self.chem_mapper.PHENOTYPIC_TESTS:
            # Phenotypic tests don't have chemical or enzyme IDs
            return "phenotypic", None, None

        # Check if it's a known substrate (try normalized code)
        chem_info = self.chem_mapper.get_chemical_info(normalized, well_code)
        if chem_info:
            chem_ids = ChemicalIdentifiers(
                chebi_id=chem_info.get("chebi_id"),
                chebi_name=chem_info.get("chebi_name"),
                pubchem_cid=chem_info.get("pubchem_cid"),
                pubchem_name=chem_info.get("pubchem_name"),
            )
            return "substrate", chem_ids, None

        # Check if it looks like an enzyme name (contains "ase" or starts with specific prefixes)
        if "ase" in well_code.lower() or well_code.startswith(("alpha", "beta", "Alkaline", "Acid")):
            # Check if EC number is in ENZYME_EC_MAPPINGS
            ec_from_mapping = self.chem_mapper.ENZYME_EC_MAPPINGS.get(well_code)
            if not ec_from_mapping:
                ec_from_mapping = self.chem_mapper.ENZYME_EC_MAPPINGS.get(normalized)

            enzyme_info = self.enzyme_mapper.get_enzyme_info(well_code, ec_from_mapping)
            enzyme_ids = EnzymeIdentifiers(
                enzyme_name=well_code,
                ec_number=enzyme_info.get("ec_number") or ec_from_mapping,  # Use mapping if get_enzyme_info returns None
                ec_name=enzyme_info.get("ec_name"),
                rhea_ids=enzyme_info.get("rhea_ids", []),
                go_terms=enzyme_info.get("go_terms", []),
                go_names=enzyme_info.get("go_names", []),
                kegg_ko=enzyme_info.get("kegg_ko"),
                kegg_reaction=enzyme_info.get("kegg_reaction"),
                metacyc_reaction=enzyme_info.get("metacyc_reaction"),
                metacyc_pathway=enzyme_info.get("metacyc_pathway", []),
            )
            return "enzyme", None, enzyme_ids

        # Check if well_code has a GO term mapping (for pathway tests or generic activities)
        # Priority: EC > GO, so we check GO_TERM_MAPPINGS after EC checks
        go_mapping = self.chem_mapper.GO_TERM_MAPPINGS.get(well_code)
        if not go_mapping:
            go_mapping = self.chem_mapper.GO_TERM_MAPPINGS.get(normalized)

        if go_mapping:
            # Create enzyme IDs with GO term but no EC number
            enzyme_ids = EnzymeIdentifiers(
                enzyme_name=well_code,
                ec_number=None,
                ec_name=None,
                rhea_ids=[],
                go_terms=[go_mapping["go_id"]],
                go_names=[go_mapping["go_name"]],
                kegg_ko=None,
                kegg_reaction=None,
                metacyc_reaction=None,
                metacyc_pathway=[],
            )
            return "enzyme", None, enzyme_ids

        # Default to "other" type
        return "other", None, None

    def _create_well_label(self, well_code: str) -> str:
        """Create human-readable label for a well.

        Args:
            well_code: Well code

        Returns:
            Human-readable label
        """
        # Check if we have a mapping (try original first, then normalized)
        normalized = normalize_well_code(well_code)

        # Try substrate mappings
        if normalized in self.chem_mapper.SUBSTRATE_MAPPINGS:
            return self.chem_mapper.SUBSTRATE_MAPPINGS[normalized]["name"]

        # Try enzyme tests (original first)
        if well_code in self.chem_mapper.ENZYME_TESTS:
            return self.chem_mapper.ENZYME_TESTS[well_code]
        if normalized in self.chem_mapper.ENZYME_TESTS:
            return self.chem_mapper.ENZYME_TESTS[normalized]

        # Try enzyme activity tests (original first)
        if well_code in self.chem_mapper.ENZYME_ACTIVITY_TESTS:
            return self.chem_mapper.ENZYME_ACTIVITY_TESTS[well_code]
        if normalized in self.chem_mapper.ENZYME_ACTIVITY_TESTS:
            return self.chem_mapper.ENZYME_ACTIVITY_TESTS[normalized]

        # Try phenotypic tests (original first)
        if well_code in self.chem_mapper.PHENOTYPIC_TESTS:
            return self.chem_mapper.PHENOTYPIC_TESTS[well_code]
        if normalized in self.chem_mapper.PHENOTYPIC_TESTS:
            return self.chem_mapper.PHENOTYPIC_TESTS[normalized]

        # Return the original code if no mapping found
        return well_code

    def _get_well_description(self, well_code: str, well_type: str) -> str:
        """Get description for a well.

        Args:
            well_code: Well code
            well_type: Type of well

        Returns:
            Description string
        """
        label = self._create_well_label(well_code)

        if well_type == "substrate":
            return f"Tests for utilization/fermentation of {label}"
        elif well_type == "enzyme":
            return f"Tests for {label} activity"
        elif well_type == "phenotypic":
            return f"Phenotypic test: {label}"
        else:
            return f"Biochemical test: {label}"

    def _build_enzymes(self, parsed_data: dict[str, Any]) -> dict[str, EnzymeIdentifiers]:
        """Build enzyme metadata with GO, KEGG, MetaCyc, and RHEA mappings.

        Args:
            parsed_data: Parsed data from BacDiveParser

        Returns:
            Dictionary mapping enzyme names to EnzymeIdentifiers
        """
        enzymes = {}

        for enzyme_name, enzyme_data in tqdm(
            parsed_data["enzymes"].items(),
            desc="Processing enzymes"
        ):
            ec_number = enzyme_data.get("ec_number")

            # Get comprehensive enzyme info including GO, KEGG, MetaCyc
            enzyme_info = self.enzyme_mapper.get_enzyme_info(enzyme_name, ec_number)

            enzymes[enzyme_name] = EnzymeIdentifiers(
                enzyme_name=enzyme_name,
                ec_number=enzyme_info.get("ec_number"),
                ec_name=enzyme_info.get("ec_name"),
                rhea_ids=enzyme_info.get("rhea_ids", []),
                go_terms=enzyme_info.get("go_terms", []),
                go_names=enzyme_info.get("go_names", []),
                kegg_ko=enzyme_info.get("kegg_ko"),
                kegg_reaction=enzyme_info.get("kegg_reaction"),
                metacyc_reaction=enzyme_info.get("metacyc_reaction"),
                metacyc_pathway=enzyme_info.get("metacyc_pathway", []),
            )

        return enzymes

    def _build_metabolites(self, parsed_data: dict[str, Any]) -> dict[str, MetaboliteIdentifiers]:
        """Build metabolite metadata with CHEBI/PubChem mappings.

        Args:
            parsed_data: Parsed data from BacDiveParser

        Returns:
            Dictionary mapping metabolite names to MetaboliteIdentifiers
        """
        metabolites = {}

        for metabolite_name, metabolite_data in tqdm(
            parsed_data["metabolites"].items(),
            desc="Processing metabolites"
        ):
            # Get CHEBI ID from the data (if present in BacDive)
            chebi_id_from_data = metabolite_data.get("chebi_id")

            # Get enriched metabolite info from mapper
            metabolite_info = self.chem_mapper.get_metabolite_info(
                metabolite_name,
                chebi_id_from_data
            )

            # Convert sets to sorted lists for JSON serialization
            utilization_test_types = sorted(list(metabolite_data.get("utilization_test_types", set())))
            production_values = sorted(list(metabolite_data.get("production_values", set())))
            test_names = sorted(list(metabolite_data.get("test_names", set())))

            metabolites[metabolite_name] = MetaboliteIdentifiers(
                metabolite_name=metabolite_name,
                chebi_id=metabolite_info.get("chebi_id"),
                chebi_name=metabolite_info.get("chebi_name"),
                pubchem_cid=metabolite_info.get("pubchem_cid"),
                pubchem_name=metabolite_info.get("pubchem_name"),
                utilization_test_types=utilization_test_types,
                production_values=production_values,
                test_names=test_names,
                utilization_count=metabolite_data.get("utilization_count", 0),
                production_count=metabolite_data.get("production_count", 0),
                test_count=metabolite_data.get("test_count", 0),
            )

        return metabolites
