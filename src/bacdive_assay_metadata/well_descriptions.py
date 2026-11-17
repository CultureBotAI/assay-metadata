"""Kit-specific procedure descriptions, separate from global substrate labels."""


def describe_kit_well(kit_name: str, well_code: str, fallback: str | None) -> str | None:
    """Return only a definition supported for this exact kit and well.

    API 20E CIT: bioMerieux insert 07584J (2010/05), reading table IV,
    PDF page 8. The manufacturer identifies citrate utilization for CIT;
    carbohydrate fermentation/oxidation entries are separate wells.
    See docs/api20e-cit-definition.md for the retained source identity.
    """
    if (kit_name, well_code) == ("API 20E", "CIT"):
        return "Tests for citrate utilization in the API 20E CIT well"
    return fallback
