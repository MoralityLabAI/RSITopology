from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def graph_invariants(num_items, num_contexts, edges):
    node_count = num_items + num_contexts
    parent = list(range(node_count))

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    for item, context in edges:
        union(item, num_items + context)
    components = len({find(node) for node in range(node_count)})
    return {
        "vertices": node_count,
        "edges": len(edges),
        "components": components,
        "incidence_rank": node_count - components,
        "cycle_rank": len(edges) - node_count + components,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    registration = json.loads(args.registration.read_text())
    protocol = json.loads((REPO / registration["protocol_path"]).read_text())
    result = json.loads(args.result.read_text())
    receipt = json.loads(args.receipt.read_text())
    checks = {}
    checks["registration_hash"] = (
        sha256(args.registration)
        == result["registration_sha256"]
        == receipt["registration_sha256"]
    )
    checks["result_hash"] = sha256(args.result) == receipt["result_sha256"]
    checks["protocol_hash"] = (
        sha256(REPO / registration["protocol_path"])
        == receipt["protocol_sha256"]
    )
    checks["sealed_files"] = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    expected_graphs = {
        cell["name"]: graph_invariants(
            int(cell["num_items"]),
            int(cell["num_contexts"]),
            tuple(tuple(edge) for edge in cell["edges"]),
        )
        for cell in protocol["fresh_validation"]["graph_cells"]
    }
    checks["graph_invariants"] = all(
        row["invariants"] == expected_graphs[row["name"]]
        for row in result["graph_rows"]
    )
    checks["cycle_liveness_status"] = all(
        (
            expected_graphs[row["name"]]["cycle_rank"] == 0
            and row["liveness_status"]
            == "factorization_unavailable_by_design"
        )
        or (
            expected_graphs[row["name"]]["cycle_rank"] > 0
            and row["liveness_status"] == "live_refutation_observed"
        )
        for row in result["graph_rows"]
    )
    checks["ledger"] = all(row["ledger_match"] for row in result["graph_rows"])
    checks["factorization"] = all(
        row["factorization_consistent"] for row in result["graph_rows"]
    )
    checks["obstruction"] = (
        result["gates"]["G2_arbitrary_midpoint_obstruction"][
            "thresholds_identical"
        ]
        and result["gates"]["G2_arbitrary_midpoint_obstruction"][
            "maximum_item_displacement"
        ]
        != "0"
    )
    checks["localization"] = (
        result["gates"]["G1_shared_midpoint_link_shape"]["link_mismatches"] == 0
        and result["gates"]["G1_shared_midpoint_link_shape"][
            "checked_thresholds"
        ]
        > 5000
    )
    checks["robust_bounds"] = all(
        row["quotient_error"] <= row["registered_bound"] + 1e-10
        and np.isfinite(row["registered_bound"])
        for row in result["robust_rows"]
    )
    checks["gate_universe"] = set(result["gate_passes"]) == set(
        protocol["gate_ids"]
    )
    checks["all_gates_pass"] = all(result["gate_passes"].values())
    checks["verdict"] = (
        result["verdict"] == protocol["verdict_map"]["all_gates_pass"]
    )
    checks["claim_boundary"] = (
        "ASMP-9 is resolved."
        in protocol["structured_claims"]["forbidden"]
        and "no novelty is claimed" in protocol["claim_boundary"]
    )
    checks["resource_caps"] = (
        receipt["wall_seconds"] <= protocol["resource_caps"]["wall_seconds"]
        and receipt["peak_resident_bytes"]
        <= protocol["resource_caps"]["peak_resident_bytes"]
    )
    output = {
        "check_count": len(checks),
        "checks": checks,
        "pass": all(checks.values()),
        "receipt_sha256": sha256(args.receipt),
        "result_sha256": sha256(args.result),
        "verifier_sha256": sha256(Path(__file__)),
    }
    write_json_exclusive(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

