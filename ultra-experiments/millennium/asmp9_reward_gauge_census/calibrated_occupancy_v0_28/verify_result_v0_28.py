from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
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


def q(value):
    return value if isinstance(value, Fraction) else Fraction(str(value))


def rank(matrix):
    rows = [list(map(q, row)) for row in matrix]
    if not rows:
        return 0
    columns = len(rows[0])
    result = 0
    for column in range(columns):
        pivot = next(
            (
                index
                for index in range(result, len(rows))
                if rows[index][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[result], rows[pivot] = rows[pivot], rows[result]
        value = rows[result][column]
        rows[result] = [entry / value for entry in rows[result]]
        for index in range(len(rows)):
            if index == result or rows[index][column] == 0:
                continue
            factor = rows[index][column]
            rows[index] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(rows[index], rows[result])
            ]
        result += 1
    return result


def dot(row, vector):
    return sum((q(a) * q(b) for a, b in zip(row, vector)), Fraction(0))


def as_float_matrix(matrix):
    return np.asarray(
        [[float(q(entry)) for entry in row] for row in matrix],
        dtype=float,
    )


def fixed_horizon(matrix):
    return max(
        1,
        *(
            sum(max(int(entry), 0) for entry in row)
            for row in matrix
        ),
        *(
            sum(max(-int(entry), 0) for entry in row)
            for row in matrix
        ),
    )


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
    checks["homogeneous_rows"] = all(
        row["law_pass"] for row in result["homogeneous_rows"]
    )
    checks["adaptive_rows"] = all(
        row["adaptive_pass"] and row["transcript_count"] > 0
        for row in result["homogeneous_rows"]
    )
    checks["unknown_numeraire"] = result["gate_passes"][
        "G3_unknown_numeraire_control"
    ]
    checks["calibrated_numeraire"] = (
        result["gate_passes"]["G4_calibrated_numeraire"]
        and result["gates"]["G4_calibrated_numeraire"][
            "scale_break_checks"
        ]
        == 2
    )
    mdp_protocol = {
        cell["name"]: cell["matrix"]
        for cell in protocol["fresh_validation"]["homogeneous_cells"]
    }
    mdp_protocol["unknown_numeraire"] = protocol["fresh_validation"][
        "unknown_numeraire_cell"
    ]["matrix"]
    mdp_protocol["calibrated_numeraire"] = protocol["fresh_validation"][
        "calibrated_numeraire_cell"
    ]["matrix"]
    mdp_checks = []
    for row in result["mdp_rows"]:
        matrix = mdp_protocol[row["name"]]
        horizon = fixed_horizon(matrix)
        query_count = len(matrix)
        mdp_checks.append(
            row["pass"]
            and row["query_initial_states"] == query_count
            and row["fixed_horizon"] == horizon
            and row["transition_count"] == 2 * query_count * horizon
            and row["state_count"] == query_count * (1 + 2 * horizon)
        )
    checks["finite_mdp_rows"] = (
        len(result["mdp_rows"]) == len(mdp_protocol)
        and all(mdp_checks)
    )
    quotient_protocol = {
        cell["name"]: cell
        for cell in protocol["fresh_validation"]["quotient_cells"]
    }
    quotient_checks = []
    for row in result["quotient_rows"]:
        cell = quotient_protocol[row["name"]]
        matrix_rank = rank(cell["matrix"])
        gauge_rank = rank(cell["gauge_basis"])
        annihilates = all(
            dot(measurement, gauge) == 0
            for measurement in cell["matrix"]
            for gauge in cell["gauge_basis"]
        )
        expected = (
            annihilates
            and matrix_rank == len(cell["matrix"][0]) - gauge_rank
        )
        quotient_checks.append(
            row["measurement_rank"] == matrix_rank
            and row["identifiable_modulo_gauge"] == expected
            and row["pass"]
        )
    checks["quotient_rows"] = all(quotient_checks)
    checks["non_gauge_witness"] = next(
        row
        for row in result["quotient_rows"]
        if row["name"] == "fresh_disconnected_constant_gauge"
    )["witness_pass"]
    robust_protocol = {
        cell["name"]: cell
        for cell in protocol["fresh_validation"]["robust_cells"]
    }
    robust_checks = []
    for row in result["robust_rows"]:
        cell = robust_protocol[row["name"]]
        matrix = as_float_matrix(cell["matrix"])
        basis = as_float_matrix(cell["quotient_basis"]).T
        singular = np.linalg.svd(matrix @ basis, compute_uv=False)
        positive = singular[singular > 1e-12]
        sigma = float(np.min(positive))
        robust_checks.append(
            abs(row["sigma_min"] - sigma) < 1e-12
            and abs(row["amplification"] - 1 / sigma) < 1e-9
        )
    checks["robust_rows"] = all(robust_checks)
    checks["conditioning_separation"] = (
        result["gates"]["G7_robust_conditioning"]["amplification_ratio"]
        >= protocol["fresh_validation"]["robust_gate"][
            "minimum_ill_to_well_amplification_ratio"
        ]
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
