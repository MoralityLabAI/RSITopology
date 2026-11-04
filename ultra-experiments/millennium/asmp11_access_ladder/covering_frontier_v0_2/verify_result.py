from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from covering_frontier import verify_cover


ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts_v0_2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    receipt = json.loads((ARTIFACTS / "receipt.json").read_text(encoding="utf-8"))
    result = json.loads((ARTIFACTS / "result.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((ARTIFACTS / "frontier.csv").open(encoding="utf-8")))
    crossovers = list(csv.DictReader((ARTIFACTS / "crossovers.csv").open(encoding="utf-8")))
    witnesses = json.loads((ARTIFACTS / "covering_witnesses.json").read_text(encoding="utf-8"))
    assert len(rows) == 63
    assert len(crossovers) == 18
    assert len(witnesses) == 21
    core_gates = [name for name in result["gates"] if name != "G6_crossover"]
    assert all(result["gates"][name] for name in core_gates)
    assert result["verdict"] in {
        "finite_covering_frontier_with_sample_crossover_established",
        "finite_covering_frontier_established_cost_inversion_not_established",
    }
    for witness in witnesses:
        assert verify_cover(
            witness["n"],
            witness["block_size"],
            witness["support_size"],
            witness["selected_blocks"],
        )
        assert len(witness["selected_blocks"]) == witness["optimum"]
    for name, expected in receipt["outputs"].items():
        assert sha256(ARTIFACTS / name) == expected
    print("ASMP-11 covering frontier v0.2 artifacts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
