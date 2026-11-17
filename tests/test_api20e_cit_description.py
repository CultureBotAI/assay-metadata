"""Exercise the actual export path and preserve distinct wells and kit contexts."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from bacdive_assay_metadata.well_descriptions import describe_kit_well


def test_cli_kit_specific_definition(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps([{"Physiology and metabolism": {
        "API 20E": {"CIT": "+", "GLU": "-"},
        "API 20NE": {"CIT": "+"},
    }}]))
    output = tmp_path / "export"
    subprocess.run([sys.executable, "-m", "bacdive_assay_metadata.main", "--input", str(source),
                    "--output-dir", str(output), "--simple", "--pretty"], check=True)
    data = json.loads((output / "assay_kits_simple.json").read_text())
    wells = {(k["kit_name"], w["name"]): w for k in data["api_kits"] for w in k["wells"]}
    assert wells["API 20E", "CIT"]["description"] == [
        "Tests for citrate utilization in the API 20E CIT well"]
    assert "fermentation" in wells["API 20NE", "CIT"]["description"][0]
    assert "Glucose" in wells["API 20E", "GLU"]["description"][0]
    assert wells["API 20E", "CIT"]["type"] == ["chemical"]


def test_unknown_kit_or_well_preserves_original():
    assert describe_kit_well("unknown", "CIT", "original") == "original"
    assert describe_kit_well("API 20E", "OTHER", None) is None


def test_refresh_rejects_ambiguous_target_before_writing(tmp_path):
    import pytest
    path = Path(__file__).parents[1] / "scripts/adhoc/refresh_api20e_cit_20261116.py"
    spec = importlib.util.spec_from_file_location("refresh_cit", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = tmp_path / "simple.json"
    original = json.dumps({"api_kits": [{"kit_name": "API 20E", "wells": [
        {"name": "CIT", "description": ["a"]}, {"name": "CIT", "description": ["b"]}]}]})
    target.write_text(original)
    with pytest.raises(ValueError, match="Expected one API 20E CIT"):
        module.refresh(target)
    assert target.read_text() == original
