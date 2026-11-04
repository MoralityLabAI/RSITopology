"""Independent exhaustive verification for ASMP-9 v0.49."""

from __future__ import annotations

from fractions import Fraction as Q
import hashlib
from itertools import permutations
import json
from pathlib import Path
import subprocess
import sys
import time

import psutil

from common_ordering import (
    common_chain_certificate,
    finite_buehler_subset_bounds,
    ordering_gauge_certificate,
    ordering_gauge_scale_compatibility,
    tight_predecessor_dag,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V048 = HERE.parent / "ordering_modulus_v0_48"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def ordering_cost(ordering, bounds, weights):
    mask = 0
    value = Q(0)
    for index in ordering:
        mask |= 1 << index
        value += weights[index] * bounds[mask]
    return value


def exhaustive_optima(bounds, weights):
    rows = [
        (ordering_cost(ordering, bounds, weights), ordering)
        for ordering in permutations(range(len(weights)))
    ]
    optimum = min(value for value, _ in rows)
    return optimum, frozenset(
        ordering for value, ordering in rows if value == optimum
    )


def monotone_binary_tables(width: int):
    size = 1 << width
    tables = []
    for encoded in range(1 << size):
        table = tuple(
            Q((encoded >> mask) & 1) for mask in range(size)
        )
        if table[0]:
            continue
        valid = True
        for mask in range(size):
            for index in range(width):
                if not mask & (1 << index):
                    if table[mask] > table[mask | (1 << index)]:
                        valid = False
                        break
            if not valid:
                break
        if valid:
            tables.append(table)
    return tuple(tables)


def validate_source_hashes(registration):
    checks = []
    for relative, expected in registration["source_sha256"].items():
        path = REPO / relative
        actual = sha256(path) if path.is_file() else None
        checks.append(
            {
                "path": relative,
                "expected": expected,
                "actual": actual,
                "match": actual == expected,
            }
        )
    return all(row["match"] for row in checks), checks


def run_tests(expected: int):
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        str(HERE / "test_common_ordering.py"),
    ]
    environment = dict(__import__("os").environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
    )
    output = (completed.stdout + completed.stderr).strip()
    return {
        "ok": completed.returncode == 0
        and f"{expected} passed" in output,
        "expected": expected,
        "returncode": completed.returncode,
        "output": output,
    }


def minimal_witness():
    rows = (
        (Q(9, 10), Q(1, 10)),
        (Q(1, 10), Q(9, 10)),
    )
    first = finite_buehler_subset_bounds(
        (Q(0), Q(1)), rows, Q(1, 5)
    )
    second = finite_buehler_subset_bounds(
        (Q(1), Q(0)), rows, Q(1, 5)
    )
    weights = (Q(1, 2), Q(1, 2))
    first_optimum, first_orders = exhaustive_optima(first, weights)
    second_optimum, second_orders = exhaustive_optima(second, weights)
    first_cross = min(
        ordering_cost(order, first, weights)
        for order in second_orders
    ) - first_optimum
    second_cross = min(
        ordering_cost(order, second, weights)
        for order in first_orders
    ) - second_optimum

    one_parameter_checks = 0
    one_parameter_failures = 0
    for probability in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
        row = ((probability, Q(1) - probability),)
        for first_risk in (Q(0), Q(1), Q(2)):
            for second_risk in (Q(0), Q(1), Q(2)):
                first_table = finite_buehler_subset_bounds(
                    (first_risk,), row, Q(1, 5)
                )
                second_table = finite_buehler_subset_bounds(
                    (second_risk,), row, Q(1, 5)
                )
                _, first_set = exhaustive_optima(first_table, weights)
                _, second_set = exhaustive_optima(
                    second_table, weights
                )
                one_parameter_checks += 1
                if not first_set.intersection(second_set):
                    one_parameter_failures += 1
    return {
        "first_bounds": [qstr(value) for value in first],
        "second_bounds": [qstr(value) for value in second],
        "first_optimum": qstr(first_optimum),
        "second_optimum": qstr(second_optimum),
        "common_optimizer_count": len(
            first_orders.intersection(second_orders)
        ),
        "first_cross_regret": qstr(first_cross),
        "second_cross_regret": qstr(second_cross),
        "one_outcome_order_count": 1,
        "one_parameter_checks": one_parameter_checks,
        "one_parameter_failures": one_parameter_failures,
    }


def exhaustive_four_outcome_audit(registration):
    width = 4
    weights = (Q(1, 10), Q(1, 5), Q(3, 10), Q(2, 5))
    tables = monotone_binary_tables(width)
    exhaustive = {}
    dag_mismatches = 0
    for index, table in enumerate(tables):
        optimum, orders = exhaustive_optima(table, weights)
        exhaustive[index] = (optimum, orders)
        dag = tight_predecessor_dag(table, weights)
        if dag.values[-1] != optimum:
            dag_mismatches += 1
        if dag.optimizer_counts[-1] != len(orders):
            dag_mismatches += 1

    pair_mismatches = 0
    gauge_pairs = 0
    gauge_failures = 0
    for first_index, first in enumerate(tables):
        for second_index, second in enumerate(tables):
            certificate = common_chain_certificate(
                first, second, weights
            )
            exact_common = len(
                exhaustive[first_index][1].intersection(
                    exhaustive[second_index][1]
                )
            )
            if certificate.common_optimizer_count != exact_common:
                pair_mismatches += 1

            scale_result = ordering_gauge_scale_compatibility(
                first, second, weights
            )
            if scale_result.status == "unique_positive_scale":
                scale = scale_result.unique_scale
            elif scale_result.status == "every_positive_scale":
                scale = Q(1)
            else:
                continue
            if scale is None:
                raise AssertionError("positive scale status lacks scale")
            gauge_pairs += 1
            gauge = ordering_gauge_certificate(
                first, second, weights, scale
            )
            if not gauge.valid or gauge.additive_constant is None:
                gauge_failures += 1
                continue
            for ordering in permutations(range(width)):
                if ordering_cost(ordering, second, weights) != (
                    scale * ordering_cost(ordering, first, weights)
                    + gauge.additive_constant
                ):
                    gauge_failures += 1
                    break
            if exhaustive[first_index][1] != exhaustive[second_index][1]:
                gauge_failures += 1
    return {
        "table_count": len(tables),
        "expected_table_count": registration[
            "expected_monotone_binary_table_count"
        ],
        "ordered_pair_count": len(tables) ** 2,
        "expected_ordered_pair_count": registration[
            "expected_ordered_pair_count"
        ],
        "tight_dag_mismatches": dag_mismatches,
        "common_chain_mismatches": pair_mismatches,
        "positive_gauge_pairs": gauge_pairs,
        "gauge_failures": gauge_failures,
    }


def recover_v048():
    subset = json.loads(
        (
            V048 / "artifacts_v0_48" / "subset_bounds_v0_48.json"
        ).read_text(encoding="utf-8")
    )
    result = json.loads(
        (
            V048 / "artifacts_v0_48" / "result_v0_48.json"
        ).read_text(encoding="utf-8")
    )
    weights = tuple(
        Q(value)
        for value in result["scientific"]["primary"][
            "reference_weights"
        ]
    )
    first = tuple(Q(value) for value in subset["classification"])
    second = tuple(Q(value) for value in subset["root_group"])
    common = common_chain_certificate(first, second, weights)
    gauge = ordering_gauge_scale_compatibility(
        first, second, weights
    )
    return {
        "first_optimizer_count": common.first_optimizer_count,
        "second_optimizer_count": common.second_optimizer_count,
        "common_optimizer_count": common.common_optimizer_count,
        "gauge_scale_status": gauge.status,
        "distinct_required_scale_count": len(
            gauge.distinct_required_scales
        ),
    }


def main() -> None:
    registration_path = HERE / "verification_registration_v0_49.json"
    output = HERE / "VERIFY_RESULT_v0_49.json"
    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    started = time.perf_counter()
    process = psutil.Process()
    source_match, source_checks = validate_source_hashes(registration)
    tests = run_tests(registration["expected_test_count"])
    minimal = minimal_witness()
    exhaustive = exhaustive_four_outcome_audit(registration)
    v048 = recover_v048()
    elapsed = time.perf_counter() - started
    peak = process.memory_info().peak_wset
    gates = {
        "H0": source_match,
        "T0": tests["ok"],
        "M0": (
            minimal["first_bounds"] == ["0", "0", "1", "1"]
            and minimal["second_bounds"] == ["0", "1", "0", "1"]
            and minimal["common_optimizer_count"] == 0
            and minimal["first_cross_regret"] == "1/2"
            and minimal["second_cross_regret"] == "1/2"
            and minimal["one_outcome_order_count"] == 1
            and minimal["one_parameter_failures"] == 0
        ),
        "D0": (
            exhaustive["table_count"]
            == exhaustive["expected_table_count"]
            and exhaustive["ordered_pair_count"]
            == exhaustive["expected_ordered_pair_count"]
            and exhaustive["tight_dag_mismatches"] == 0
            and exhaustive["common_chain_mismatches"] == 0
        ),
        "G0": exhaustive["gauge_failures"] == 0
        and exhaustive["positive_gauge_pairs"] > 0,
        "V0": (
            v048["first_optimizer_count"] == 1_451_520
            and v048["second_optimizer_count"] == 4_354_560
            and v048["common_optimizer_count"] == 1_451_520
            and v048["gauge_scale_status"] == "no_positive_scale"
            and v048["distinct_required_scale_count"] > 1
        ),
        "RESOURCE": (
            elapsed
            <= registration["resource_ceiling"]["seconds"]
            and peak
            <= registration["resource_ceiling"][
                "peak_aggregate_working_set_bytes"
            ]
        ),
    }
    ok = all(gates.values())
    payload = {
        "schema": "asmp9-v0.49-theorem-verification-v1",
        "protocol_id": registration["protocol_id"],
        "registration_sha256": hashlib.sha256(
            registration_bytes
        ).hexdigest(),
        "status": (
            "finite_common_ordering_theorem_verified"
            if ok
            else "finite_common_ordering_theorem_not_verified"
        ),
        "ok": ok,
        "gates": gates,
        "tests": tests,
        "minimal_witness": minimal,
        "exhaustive_four_outcome": exhaustive,
        "v0_48_recovery": v048,
        "resource": {
            "elapsed_seconds": elapsed,
            "peak_working_set_bytes": peak,
            "worker_processes": 1,
        },
        "source_checks": source_checks,
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if output.exists() and output.read_bytes() != encoded:
        raise RuntimeError("write-once verification result mismatch")
    output.write_bytes(encoded)
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(not ok)


if __name__ == "__main__":
    main()
