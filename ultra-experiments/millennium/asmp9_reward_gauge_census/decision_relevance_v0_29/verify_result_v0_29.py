from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def q(value):
    return value if isinstance(value, Fraction) else Fraction(str(value))


def dot(left, right):
    return sum((q(a) * q(b) for a, b in zip(left, right)), Fraction(0))


def subtract(left, right):
    return tuple(q(a) - q(b) for a, b in zip(left, right))


def norm_squared(vector):
    return dot(vector, vector)


def values(occupancies, reward):
    return tuple(dot(row, reward) for row in occupancies)


def first_argmax(items):
    maximum = max(items)
    return next(index for index, item in enumerate(items) if item == maximum)


def gauge_valid(occupancies, gauge_basis):
    base = occupancies[0]
    return all(
        dot(subtract(row, base), gauge) == 0
        for row in occupancies[1:]
        for gauge in gauge_basis
    )


def projected_residual(estimated, true, gauge_basis):
    error = subtract(estimated, true)
    if not gauge_basis:
        return error
    gram = [[dot(a, b) for b in gauge_basis] for a in gauge_basis]
    rhs = [dot(a, error) for a in gauge_basis]
    size = len(gram)
    rows = [list(map(q, row)) + [q(value)] for row, value in zip(gram, rhs)]
    for column in range(size):
        pivot = next(
            index
            for index in range(column, size)
            if rows[index][column]
        )
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [entry / scale for entry in rows[column]]
        for index in range(size):
            if index == column:
                continue
            factor = rows[index][column]
            rows[index] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(rows[index], rows[column])
            ]
    coefficients = [row[-1] for row in rows]
    projection = tuple(
        sum(
            (coefficient * gauge[index] for coefficient, gauge in zip(coefficients, gauge_basis)),
            Fraction(0),
        )
        for index in range(len(error))
    )
    return subtract(error, projection)


def evaluate(cell):
    occupancies = cell["policy_occupancies"]
    gauge = cell["gauge_basis"]
    if not gauge_valid(occupancies, gauge):
        return {"available": False}
    true_values = values(occupancies, cell["true_reward"])
    estimated_values = values(occupancies, cell["estimated_reward"])
    true_policy = first_argmax(true_values)
    selected = first_argmax(estimated_values)
    regret = true_values[true_policy] - true_values[selected]
    residual = projected_residual(
        cell["estimated_reward"], cell["true_reward"], gauge
    )
    delta_squared = norm_squared(residual)
    differences = [
        subtract(left, right)
        for left in occupancies
        for right in occupancies
    ]
    diameter_squared = max(map(norm_squared, differences))
    selected_difference_squared = norm_squared(
        subtract(occupancies[true_policy], occupancies[selected])
    )
    return {
        "available": True,
        "delta_squared": delta_squared,
        "diameter_squared": diameter_squared,
        "regret": regret,
        "selected": selected,
        "selected_bound_squared": delta_squared
        * selected_difference_squared,
        "true_policy": true_policy,
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
    fresh = protocol["fresh_validation"]
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
    checks["gate_universe"] = set(result["gate_passes"]) == set(
        protocol["gate_ids"]
    )
    checks["all_gates_pass"] = all(result["gate_passes"].values())
    checks["verdict"] = (
        result["verdict"] == protocol["verdict_map"]["all_gates_pass"]
    )

    nonzero = evaluate(fresh["nonzero_regret_cell"])
    zero = evaluate(fresh["zero_regret_cell"])
    checks["regret_cells"] = (
        nonzero["regret"] > 0
        and nonzero["regret"] ** 2 <= nonzero["selected_bound_squared"]
        and zero["regret"] == 0
    )
    sharp = evaluate(fresh["sharp_cell"])
    checks["sharpness"] = (
        sharp["regret"] > 0
        and sharp["regret"] ** 2 == sharp["selected_bound_squared"]
    )
    checks["gauge_precondition"] = all(
        gauge_valid(
            fresh[name]["policy_occupancies"], fresh[name]["gauge_basis"]
        )
        for name in (
            "nonzero_regret_cell",
            "zero_regret_cell",
            "sharp_cell",
            "strict_margin_cell",
            "equality_margin_cell",
            "composition_cell",
        )
    )
    checks["invalid_gauge"] = not gauge_valid(
        fresh["invalid_gauge_cell"]["policy_occupancies"],
        fresh["invalid_gauge_cell"]["gauge_basis"],
    )
    strict_result = result["cell_results"]["strict_margin"]
    equality_result = result["cell_results"]["equality_margin"]
    checks["strict_margin"] = strict_result["policy_identity_certified"]
    checks["equality_inconclusive"] = (
        not equality_result["policy_identity_certified"]
        and any(
            q(row["margin"]) ** 2
            == q(equality_result["delta_squared"])
            * q(row["difference_squared"])
            for row in equality_result["margin_rows"]
        )
    )
    scale_rows = result["scale_rows"]
    checks["scale_policy_invariance"] = (
        len({row["optimal_policy"] for row in scale_rows}) == 1
    )
    checks["scale_threshold_flip"] = {
        row["fixed_threshold_pass"] for row in scale_rows
    } == {True, False}

    composition = evaluate(fresh["composition_cell"])
    measurement = fresh["composition_cell"]["measurement_matrix"]
    observed_error = tuple(
        dot(row, fresh["composition_cell"]["estimated_reward"])
        - dot(row, fresh["composition_cell"]["true_reward"])
        for row in measurement
    )
    registered_error = tuple(
        map(q, fresh["composition_cell"]["measurement_error"])
    )
    sigma_squared = q(fresh["composition_cell"]["sigma_min_squared"])
    composition_bound_squared = (
        composition["diameter_squared"]
        * norm_squared(registered_error)
        / sigma_squared
    )
    checks["composition_measurement"] = observed_error == registered_error
    checks["composition_bound"] = (
        composition["regret"] > 0
        and composition["regret"] ** 2 <= composition_bound_squared
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
