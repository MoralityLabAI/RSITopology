from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts_v0_1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    receipt = json.loads((ARTIFACTS / "receipt.json").read_text(encoding="utf-8"))
    result = json.loads((ARTIFACTS / "result.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((ARTIFACTS / "access_ladder.csv").open(encoding="utf-8")))
    assert len(rows) == 245
    assert result["verdict"] == "finite_access_ladder_established"
    assert all(result["gates"].values())
    for name, expected in receipt["outputs"].items():
        assert sha256(ARTIFACTS / name) == expected
    print("ASMP-11 v0.1 artifacts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
