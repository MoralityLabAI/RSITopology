"""Artifact verifier for the ASMP-9 reward-gauge census."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.artifact_dir.resolve()
    receipt = json.loads((root / "receipt_v0_1.json").read_text(encoding="utf-8"))
    result = json.loads((root / "result_v0_1.json").read_text(encoding="utf-8"))
    for name, record in receipt["outputs"].items():
        path = root / name
        assert path.is_file(), name
        assert path.stat().st_size == record["bytes"], name
        assert sha256(path) == record["sha256"], name
    assert result["census"]["graph_count"] == 33866
    assert result["verdict"] == receipt["verdict"]
    for name, gate in result["gates"].items():
        assert gate["pass"], name
    ordinal = result["ordinal_counterexample"]
    assert ordinal["exact_returns"][0] != ordinal["exact_returns"][1]
    assert ordinal["ordinal_signs"][0] == ordinal["ordinal_signs"][1]
    assert ordinal["non_gauge_equivalent"]
    print("ASMP-9 artifact verification passed")
    print(f"verdict={result['verdict']} graphs={result['census']['graph_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
