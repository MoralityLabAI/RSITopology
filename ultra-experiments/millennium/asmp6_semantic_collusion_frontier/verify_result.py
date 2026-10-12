from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_dir", nargs="?", type=Path, default=ROOT / "artifacts_v0_1")
    args = parser.parse_args()
    artifact_dir = args.artifact_dir.resolve()
    receipt = json.loads((artifact_dir / "receipt.json").read_text(encoding="utf-8"))
    result = json.loads((artifact_dir / "result.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((artifact_dir / "frontier.csv").open(encoding="utf-8")))
    assert len(rows) == 40
    assert result["verdict"] == "finite_registry_frontier_established"
    assert all(result["gates"].values())
    for name, expected in receipt["outputs"].items():
        assert sha256(artifact_dir / name) == expected
    print("ASMP-6 v0.1 artifacts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
