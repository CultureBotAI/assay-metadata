"""Regenerate only the API 20E CIT description through the production definition helper."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from bacdive_assay_metadata.well_descriptions import describe_kit_well


def refresh(path):
    original = path.read_bytes()
    data = json.loads(original)
    expected = copy.deepcopy(data)
    matches = [w for k in data["api_kits"] if k["kit_name"] == "API 20E"
               for w in k["wells"] if w["name"] == "CIT"]
    if len(matches) != 1:
        raise ValueError("Expected one API 20E CIT well")
    old = matches[0]["description"]
    if len(old) != 1:
        raise ValueError("Expected one description")
    matches[0]["description"] = [describe_kit_well("API 20E", "CIT", old[0])]
    for kit in expected["api_kits"]:
        if kit["kit_name"] == "API 20E":
            for well in kit["wells"]:
                if well["name"] == "CIT":
                    well["description"] = matches[0]["description"]
    assert data == expected
    # Preserve all existing serialization and bytes outside the single old value.
    new_token = json.dumps(matches[0]["description"][0]).encode()
    serialized = json.dumps(data, indent=2).encode()
    before = json.dumps(json.loads(original), indent=2).encode()
    if original not in (before, before + b"\n"):
        raise ValueError("Unexpected input formatting")
    candidate = serialized + (b"\n" if original.endswith(b"\n") else b"")
    if candidate.count(new_token) != 1:
        raise ValueError("Unexpected candidate count")
    path.write_bytes(candidate)
    return {"path": str(path), "before_sha256": hashlib.sha256(original).hexdigest(),
            "after_sha256": hashlib.sha256(candidate).hexdigest(), "changed_wells": 1,
            "old_description": old[0], "new_description": matches[0]["description"][0]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(refresh(args.input), indent=2))
