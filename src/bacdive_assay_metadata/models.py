"""Data models for API assay metadata."""

from typing import Optional
from pydantic import BaseModel, Field


class ChemicalIdentifiers(BaseModel):
    """Chemical identifiers from various databases."""

    chebi_id: Optional[str] = Field(None, description="CHEBI identifier")
    chebi_name: Optional[str] = Field(None, description="CHEBI preferred name")
    pubchem_cid: Optional[str] = Field(None, description="PubChem Compound ID")
    pubchem_name: Optional[str] = Field(None, description="PubChem compound name")
    inchi: Optional[str] = Field(None, description="InChI identifier")
    smiles: Optional[str] = Field(None, description="SMILES notation")


class EnzymeIdentifiers(BaseModel):
    """Enzyme identifiers from various databases."""

    ec_number: Optional[str] = Field(None, description="EC number (catalytic reaction)")
    ec_name: Optional[str] = Field(None, description="EC enzyme name")
    rhea_ids: list[str] = Field(default_factory=list, description="RHEA reaction IDs")
    enzyme_name: str = Field(..., description="Common enzyme name")

    # Gene Ontology
    go_terms: list[str] = Field(default_factory=list, description="GO molecular function terms")
    go_names: list[str] = Field(default_factory=list, description="GO term names")

    # KEGG
    kegg_ko: Optional[str] = Field(None, description="KEGG Orthology identifier")
    kegg_reaction: Optional[str] = Field(None, description="KEGG Reaction identifier")

    # MetaCyc
    metacyc_reaction: Optional[str] = Field(None, description="MetaCyc reaction identifier")
    metacyc_pathway: list[str] = Field(default_factory=list, description="MetaCyc pathway identifiers")


class WellMetadata(BaseModel):
    """Metadata for a single well/test in an API assay."""

    code: str = Field(..., description="Well code (e.g., GLU, URE)")
    label: str = Field(..., description="Human-readable label")
    well_type: str = Field(..., description="Type: substrate, enzyme, or other")
    description: Optional[str] = Field(None, description="Description of the test")

    # Chemical identifiers (for substrate wells)
    chemical_ids: Optional[ChemicalIdentifiers] = None

    # Enzyme identifiers (for enzyme wells)
    enzyme_ids: Optional[EnzymeIdentifiers] = None

    # API kits that use this well
    used_in_kits: list[str] = Field(default_factory=list, description="API kit names")


class APIKitMetadata(BaseModel):
    """Metadata for an API assay kit."""

    kit_name: str = Field(..., description="API kit name (e.g., API zym)")
    description: str = Field(..., description="Kit purpose and usage")
    category: str = Field(..., description="Kit category")
    well_count: int = Field(..., description="Number of wells/tests")
    wells: list[str] = Field(..., description="List of well codes in order")
    occurrence_count: int = Field(0, description="Number of times found in dataset")

    class Config:
        json_schema_extra = {
            "example": {
                "kit_name": "API zym",
                "description": "Enzyme activity testing for 19 different enzymes",
                "category": "Enzyme profiling",
                "well_count": 20,
                "wells": ["Control", "Alkaline phosphatase", "Esterase"],
                "occurrence_count": 11747
            }
        }


class AssayMetadata(BaseModel):
    """Complete assay metadata collection."""

    api_kits: list[APIKitMetadata] = Field(..., description="All API kit metadata")
    wells: dict[str, WellMetadata] = Field(..., description="All well metadata by code")
    enzymes: dict[str, EnzymeIdentifiers] = Field(..., description="All enzyme metadata")
    statistics: dict[str, int] = Field(default_factory=dict, description="Dataset statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "api_kits": [],
                "wells": {},
                "enzymes": {},
                "statistics": {
                    "total_strains": 99392,
                    "total_api_kits": 17,
                    "total_unique_wells": 150
                }
            }
        }
