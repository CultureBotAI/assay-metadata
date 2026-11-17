"""Execute pinned KG-Microbe assay generator on retained and candidate metadata."""
import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType


def replay(kg_root, commit, metadata):
    def source(path):
        return subprocess.check_output(["git", "-C", str(kg_root), "show", f"{commit}:{path}"])
    raw = source("kg_microbe/utils/mapping_file_utils.py")
    constants_raw = source("kg_microbe/transform_utils/constants.py")
    constants = ModuleType("kg_microbe.transform_utils.constants")
    for node in ast.parse(constants_raw).body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    setattr(constants, target.id, value)
    function = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == "generate_assay_nodes")
    namespace = {"List": list}
    sys.modules[constants.__name__] = constants
    # Execute the explicitly selected owner revision, never a command from evidence.
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<pinned-KG-generator>", "exec"), namespace)  # noqa: S102
    headers = ["id", "category", "name", "provided_by", "description"]
    rows = namespace["generate_assay_nodes"](metadata, headers, provided_by="infores:bacdive")
    selected = [dict(zip(headers, row)) for row in rows if row[0] == "kgmicrobe.assay:API_20E_CIT"]
    if len(selected) != 1:
        raise ValueError("Expected exactly one regenerated CIT node")
    return {"node": selected[0], "generator_sha256": hashlib.sha256(raw).hexdigest(),
            "constants_sha256": hashlib.sha256(constants_raw).hexdigest(), "kg_commit": commit}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kg-root", type=Path, required=True)
    parser.add_argument("--kg-commit", required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.kg_root, args.kg_commit, json.loads(args.metadata.read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))
