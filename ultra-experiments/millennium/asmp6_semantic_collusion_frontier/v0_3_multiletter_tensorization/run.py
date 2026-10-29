"""Write-once primary runner for ASMP-6 v0.3.

Do not invoke this entrypoint until the complete source set has been committed.
"""

from __future__ import annotations

import sys as _sys


if __name__ == "__main__" and not (
    _sys.flags.isolated and getattr(_sys.flags, "safe_path", False)
):
    raise SystemExit(
        "refusing unsafe launch before imports; invoke with `python -I run.py ...`"
    )
if __name__ == "__main__":
    _sys.dont_write_bytecode = True


import argparse
import importlib.util
import stat
from pathlib import Path
from types import ModuleType


HERE = Path(__file__).resolve().parent
FROZEN_SOURCE_FILES = (
    "PROTOCOL_v0_3.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "manifest_v0_3.json",
    "multiletter_tensorization.py",
    "run.py",
    "test_multiletter_tensorization.py",
    "verify_independent.py",
)


def _is_reparse_point(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & reparse_flag)


def preflight_live_source_inventory() -> None:
    entries = {entry.name: entry for entry in HERE.iterdir()}
    expected = set(FROZEN_SOURCE_FILES)
    invalid = [
        name
        for name in sorted(expected & set(entries))
        if _is_reparse_point(entries[name]) or not entries[name].is_file()
    ]
    if (
        _is_reparse_point(HERE)
        or set(entries) != expected
        or invalid
    ):
        raise SystemExit(
            "refusing live source inventory before local import: "
            f"missing={sorted(expected - set(entries))}, "
            f"unexpected={sorted(set(entries) - expected)}, invalid={invalid}"
        )


def load_primary_module() -> ModuleType:
    source_path = HERE / "multiletter_tensorization.py"
    spec = importlib.util.spec_from_file_location(
        "_asmp6_v03_frozen_primary", source_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not construct frozen primary module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    preflight_live_source_inventory()
    primary = load_primary_module()
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest_v0_3.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE.parent
        / "artifacts_v0_3_multiletter_tensorization"
        / "result_v0_3.json",
    )
    args = parser.parse_args()

    manifest = primary.load_manifest(args.manifest)
    source_binding = primary.source_commit_binding(args.source_commit)
    result = primary.compile_result(manifest, source_binding)
    try:
        primary.write_once_json(
            args.output, result, max_bytes=manifest["budget"]["max_result_bytes"]
        )
    except primary.ResourceStop as error:
        raise SystemExit(
            f"refusing artifact before path creation; no artifact written: {error}"
        ) from error
    print(args.output)


if __name__ == "__main__":
    main()
