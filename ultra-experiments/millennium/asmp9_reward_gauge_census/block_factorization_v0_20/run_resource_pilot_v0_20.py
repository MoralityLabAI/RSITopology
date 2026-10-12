"""Burned resource pilot for the prospective v0.20 design gate."""

from __future__ import annotations

import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path

from block_factorization import PreparedGraph
from run_verification_v0_20 import (
    design_comparison,
    peak_resident_bytes,
)


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts_v0_20" / "resource_pilot_v0_20.json"

# K2,4 was already burned in the v0.18 development registry. Attaching a
# triangle gives the same 8-edge-plus-3-edge block-size profile as the
# registered design cell without evaluating that cell.
BURNED_PROXY_EDGES = (
    (0, 2),
    (0, 3),
    (0, 4),
    (0, 5),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (0, 6),
    (6, 7),
    (7, 0),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    start = time.perf_counter()
    graph = PreparedGraph.build(8, BURNED_PROXY_EDGES)
    row = design_comparison(
        graph, total_budget=12, epsilon=Fraction(3, 11)
    )
    elapsed = time.perf_counter() - start
    receipt = {
        "status": "development_only_all_cells_burned",
        "claim_eligible": False,
        "proxy": "burned_k2_4_plus_triangle",
        "block_edge_counts": [
            len(block) for block in graph.cyclic
        ],
        "total_budget": 12,
        "epsilon": "3/11",
        "allocation_count": row["allocation_count"],
        "exact_match": row["exact_match"],
        "elapsed_seconds": elapsed,
        "peak_resident_bytes": peak_resident_bytes(),
        "source_hashes": {
            "block_factorization.py": sha256(
                HERE / "block_factorization.py"
            ),
            "run_verification_v0_20.py": sha256(
                HERE / "run_verification_v0_20.py"
            ),
            "run_resource_pilot_v0_20.py": sha256(Path(__file__)),
        },
    }
    OUTPUT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
