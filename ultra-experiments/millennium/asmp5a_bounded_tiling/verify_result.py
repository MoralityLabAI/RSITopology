"""Independent artifact verifier for the ASMP-5A finite seed."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def catalan(index: int) -> int:
    return math.comb(2 * index, index) // (index + 1)


def nondominated(pairs):
    values = {tuple(pair) for pair in pairs}
    return all(
        not any(other != pair and other[0] <= pair[0] and other[1] <= pair[1] for other in values)
        for pair in values
    )


def verify(result_path: Path, receipt_path: Path) -> dict[str, Any]:
    protocol_path = HERE / "protocol_v0_1.json"
    registration_path = HERE / "registration_v0_1.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    rows = result.get("shape_rows", [])
    checks = {
        "result_hash_matches": sha256(result_path) == receipt["result_sha256"],
        "protocol_hash_matches": sha256(protocol_path) == receipt["protocol_sha256"],
        "registration_hash_matches": sha256(registration_path) == receipt["registration_sha256"],
        "registered_sources_match": all(sha256(REPO_ROOT / path) == expected for path, expected in registration["source_hashes"].items()),
        "schema_exact": result.get("schema_version") == "asmp5a_bounded_tiling_result_v0_1",
        "instrument_valid": result.get("instrument_status") == "valid",
        "resource_pass": result.get("resource_receipt", {}).get("pass") is True,
        "row_universe_exact": [row.get("obligations") for row in rows] == list(range(1, protocol["maximum_obligations"] + 1)),
        "catalan_counts_recomputed": all(row["tree_count"] == catalan(row["obligations"] - 1) for row in rows),
        "work_formula_recomputed": all(row["work_nodes"] == 2 * row["obligations"] - 1 for row in rows),
        "depth_formula_recomputed": all(row["minimum_depth"] == math.ceil(math.log2(row["obligations"])) for row in rows),
        "pareto_rows_nondominated": all(nondominated(row["pareto_depth_memory"]) for row in rows),
    }
    budgets = {row["id"]: row["capacities"] for row in result.get("budget_rows", [])}
    checks["registered_ranking_reversal"] = (
        budgets.get("shallow_parallel", {}).get("balanced", 0) > budgets.get("shallow_parallel", {}).get("chain", 0)
        and budgets.get("memory_tight_serial", {}).get("chain", 0) > budgets.get("memory_tight_serial", {}).get("balanced", 0)
    )
    checks["all_runner_gates_pass"] = len(result.get("gates", {})) == 8 and all(gate["pass"] for gate in result["gates"].values())
    passed = all(checks.values())
    return {
        "schema_version": "asmp5a_bounded_tiling_verification_v0_1",
        "instrument_status": "valid" if passed else "invalid",
        "decision": "pass" if passed else "invalid_stop",
        "checks": checks,
        "claim_boundary": protocol["claim_boundary"],
    }


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = verify(args.result.resolve(), args.receipt.resolve())
    write_once(args.output.resolve(), canonical_json(result).encode())
    print(canonical_json(result), end="")
    return 0 if result["decision"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
