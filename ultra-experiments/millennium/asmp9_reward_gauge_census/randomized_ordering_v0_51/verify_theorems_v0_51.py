"""Exhaustive registered verification for ASMP-9 v0.51."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import hashlib
from itertools import permutations
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import psutil

from randomized_ordering import (
    minimal_randomization_gain_witness,
    randomized_ordering_certificate,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def monotone_binary_tables(width: int):
    size = 1 << width
    result = []
    for encoded in range(1 << size):
        table = tuple(
            Q((encoded >> mask) & 1) for mask in range(size)
        )
        if table[0]:
            continue
        if all(
            table[mask] <= table[mask | (1 << index)]
            for mask in range(size)
            for index in range(width)
            if not mask & (1 << index)
        ):
            result.append(table)
    return tuple(result)


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
        str(HERE / "test_randomized_ordering.py"),
        str(HERE / "test_verifier_v0_51.py"),
    ]
    environment = dict(os.environ)
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


def independent_certificate_checks(certificate):
    matrix = certificate.payoff_matrix
    primal = certificate.primal_probabilities
    dual = certificate.dual_probabilities
    value = certificate.randomized_value
    column_expectations = tuple(
        sum(
            (
                primal[action] * matrix[action][scenario]
                for action in range(len(matrix))
            ),
            Q(0),
        )
        for scenario in range(len(matrix[0]))
    )
    row_expectations = tuple(
        sum(
            (
                dual[scenario] * matrix[action][scenario]
                for scenario in range(len(matrix[0]))
            ),
            Q(0),
        )
        for action in range(len(matrix))
    )
    direct_deterministic = min(max(row) for row in matrix)
    common_zero = sum(all(entry == 0 for entry in row) for row in matrix)
    return {
        "primal_simplex": (
            all(probability >= 0 for probability in primal)
            and sum(primal, Q(0)) == 1
        ),
        "dual_simplex": (
            all(probability >= 0 for probability in dual)
            and sum(dual, Q(0)) == 1
        ),
        "primal_feasible": all(
            result <= value for result in column_expectations
        ),
        "dual_feasible": all(
            result >= value for result in row_expectations
        ),
        "primal_slackness": all(
            not primal[action]
            or row_expectations[action] == value
            for action in range(len(matrix))
        ),
        "dual_slackness": all(
            not dual[scenario]
            or column_expectations[scenario] == value
            for scenario in range(len(matrix[0]))
        ),
        "deterministic_value_match": (
            direct_deterministic == certificate.deterministic_value
        ),
        "zero_support_match": (
            (value == 0) == bool(common_zero)
            and common_zero == certificate.common_zero_order_count
        ),
        "randomized_not_worse": (
            value <= certificate.deterministic_value
        ),
    }


def pair_row(first_index, second_index, first, second, vertices):
    certificate = randomized_ordering_certificate(
        (first, second), vertices
    )
    checks = independent_certificate_checks(certificate)
    return {
        "first_table_index": first_index,
        "second_table_index": second_index,
        "common_zero_order_count": certificate.common_zero_order_count,
        "deterministic_value": qstr(certificate.deterministic_value),
        "randomized_value": qstr(certificate.randomized_value),
        "randomization_gain": qstr(certificate.randomization_gain),
        "deterministic_optimizer_count": (
            certificate.deterministic_optimizer_count
        ),
        "primal_support_size": len(
            certificate.primal_support_orders
        ),
        "dual_support_size": len(
            certificate.dual_support_scenarios
        ),
        "primal_probabilities": [
            qstr(value) for value in certificate.primal_probabilities
        ],
        "dual_probabilities": [
            qstr(value) for value in certificate.dual_probabilities
        ],
        "primal_dual_match": certificate.primal_dual_match,
        "certificate_slackness": (
            certificate.complementary_slackness
        ),
        "independent_checks": checks,
    }


def exhaustive_audit(registration):
    tables = monotone_binary_tables(3)
    vertices = tuple(
        tuple(Q(value) for value in row)
        for row in registration["reference_vertices"]
    )
    rows = []
    for first_index, first in enumerate(tables):
        for second_index, second in enumerate(tables):
            rows.append(
                pair_row(
                    first_index,
                    second_index,
                    first,
                    second,
                    vertices,
                )
            )

    primal_dual_failures = sum(
        not row["primal_dual_match"] for row in rows
    )
    certificate_slackness_failures = sum(
        not row["certificate_slackness"] for row in rows
    )
    check_names = tuple(rows[0]["independent_checks"])
    independent_failures = {
        name: sum(
            not row["independent_checks"][name] for row in rows
        )
        for name in check_names
    }
    robust_count = sum(
        row["common_zero_order_count"] > 0 for row in rows
    )
    strict_gain_count = sum(
        Q(row["randomization_gain"]) > 0 for row in rows
    )
    gains = [Q(row["randomization_gain"]) for row in rows]
    maximum_gain = max(gains)
    maximum_rows = [
        (
            row["first_table_index"],
            row["second_table_index"],
        )
        for row, gain in zip(rows, gains)
        if gain == maximum_gain
    ]
    gain_histogram = Counter(gains)
    primal_support_histogram = Counter(
        row["primal_support_size"] for row in rows
    )
    dual_support_histogram = Counter(
        row["dual_support_size"] for row in rows
    )
    return {
        "table_count": len(tables),
        "ordered_pair_count": len(rows),
        "ordering_count": len(tuple(permutations(range(3)))),
        "scenario_count": 2 * len(vertices),
        "robust_zero_pair_count": robust_count,
        "no_robust_zero_pair_count": len(rows) - robust_count,
        "strict_gain_pair_count": strict_gain_count,
        "no_strict_gain_pair_count": len(rows) - strict_gain_count,
        "maximum_gain": qstr(maximum_gain),
        "maximum_gain_pairs": maximum_rows,
        "mean_gain": qstr(sum(gains, Q(0)) / len(gains)),
        "gain_histogram": [
            {
                "gain": qstr(gain),
                "count": gain_histogram[gain],
            }
            for gain in sorted(gain_histogram)
        ],
        "primal_support_histogram": {
            str(key): value
            for key, value in sorted(primal_support_histogram.items())
        },
        "dual_support_histogram": {
            str(key): value
            for key, value in sorted(dual_support_histogram.items())
        },
        "primal_dual_failures": primal_dual_failures,
        "certificate_slackness_failures": (
            certificate_slackness_failures
        ),
        "independent_failures": independent_failures,
        "pair_rows": rows,
    }


def minimal_audit():
    result = minimal_randomization_gain_witness()
    return {
        "deterministic_value": qstr(result.deterministic_value),
        "randomized_value": qstr(result.randomized_value),
        "randomization_gain": qstr(result.randomization_gain),
        "common_zero_order_count": result.common_zero_order_count,
        "primal_probabilities": [
            qstr(value) for value in result.primal_probabilities
        ],
        "dual_probabilities": [
            qstr(value) for value in result.dual_probabilities
        ],
        "primal_dual_match": result.primal_dual_match,
        "complementary_slackness": result.complementary_slackness,
    }


def main() -> None:
    registration_path = HERE / "verification_registration_v0_51.json"
    output = HERE / "VERIFY_RESULT_v0_51.json"
    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    started = time.perf_counter()
    process = psutil.Process()
    source_match, source_checks = validate_source_hashes(registration)
    tests = run_tests(registration["expected_test_count"])
    exhaustive = exhaustive_audit(registration)
    minimal = minimal_audit()
    elapsed = time.perf_counter() - started
    peak = process.memory_info().peak_wset

    failures = exhaustive["independent_failures"]
    gates = {
        "H0": source_match,
        "T0": tests["ok"],
        "U0": (
            exhaustive["table_count"]
            == registration["expected_table_count"]
            and exhaustive["ordered_pair_count"]
            == registration["expected_ordered_pair_count"]
            and exhaustive["ordering_count"]
            == registration["expected_ordering_count"]
            and exhaustive["scenario_count"]
            == registration["expected_scenario_count"]
        ),
        "P0": exhaustive["primal_dual_failures"] == 0,
        "C0": (
            exhaustive["certificate_slackness_failures"] == 0
            and failures["primal_simplex"] == 0
            and failures["dual_simplex"] == 0
            and failures["primal_feasible"] == 0
            and failures["dual_feasible"] == 0
            and failures["primal_slackness"] == 0
            and failures["dual_slackness"] == 0
        ),
        "Z0": failures["zero_support_match"] == 0,
        "R0": (
            failures["deterministic_value_match"] == 0
            and failures["randomized_not_worse"] == 0
        ),
        "B0": (
            exhaustive["robust_zero_pair_count"] == 79
            and exhaustive["no_robust_zero_pair_count"] == 282
        ),
        "M0": (
            minimal["deterministic_value"] == "1/2"
            and minimal["randomized_value"] == "1/4"
            and minimal["randomization_gain"] == "1/4"
            and minimal["common_zero_order_count"] == 0
            and minimal["primal_probabilities"] == ["1/2", "1/2"]
            and minimal["dual_probabilities"] == ["1/2", "1/2"]
            and minimal["primal_dual_match"]
            and minimal["complementary_slackness"]
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
        "schema": "asmp9-v0.51-theorem-verification-v1",
        "protocol_id": registration["protocol_id"],
        "registration_sha256": hashlib.sha256(
            registration_bytes
        ).hexdigest(),
        "status": (
            "finite_randomized_ordering_theorem_verified"
            if ok
            else "finite_randomized_ordering_theorem_not_verified"
        ),
        "ok": ok,
        "gates": gates,
        "tests": tests,
        "minimal_witness": minimal,
        "exhaustive_three_outcome": exhaustive,
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
    print(
        json.dumps(
            {
                "ok": ok,
                "status": payload["status"],
                "gates": gates,
                "registration_sha256": payload[
                    "registration_sha256"
                ],
                "summary": {
                    key: exhaustive[key]
                    for key in (
                        "table_count",
                        "ordered_pair_count",
                        "robust_zero_pair_count",
                        "strict_gain_pair_count",
                        "maximum_gain",
                        "mean_gain",
                        "primal_dual_failures",
                        "certificate_slackness_failures",
                        "independent_failures",
                    )
                },
                "resource": payload["resource"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    raise SystemExit(not ok)


if __name__ == "__main__":
    main()
