"""Independent exhaustive verification for ASMP-9 v0.52."""

from __future__ import annotations

from fractions import Fraction as Q
import hashlib
from itertools import permutations, product
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import psutil


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


def independent_monotone_tables():
    rows = []
    for tail in product(range(3), repeat=7):
        table = (0,) + tail
        if all(
            table[mask] <= table[mask | (1 << index)]
            for mask in range(8)
            for index in range(3)
            if not mask & (1 << index)
        ):
            rows.append(table)
    return tuple(rows)


def independent_valid(table, reports):
    for level in (1, 2):
        mask = sum(
            1 << index
            for index, report in enumerate(reports)
            if report < level
        )
        if table[mask] >= level:
            return False
    return True


def independent_orders(reports):
    return tuple(
        order
        for order in permutations(range(len(reports)))
        if all(
            reports[order[index]] <= reports[order[index + 1]]
            for index in range(len(reports) - 1)
        )
    )


def independent_buehler(table, order):
    result = [0] * len(order)
    mask = 0
    for index in order:
        mask |= 1 << index
        result[index] = table[mask]
    return tuple(result)


def independent_cost(reports, weights):
    return sum(
        (Q(report) * weight for report, weight in zip(reports, weights)),
        Q(0),
    )


def denominator_six_grid():
    return tuple(
        (Q(first, 6), Q(second, 6), Q(third, 6))
        for first in range(1, 6)
        for second in range(1, 6 - first)
        for third in (6 - first - second,)
        if third > 0
    )


def table_from_experiment(risks, rows, alpha):
    result = []
    width = len(rows[0])
    for mask in range(1 << width):
        eligible = []
        for risk, row in zip(risks, rows):
            mass = sum(
                row[index]
                for index in range(width)
                if mask & (1 << index)
            )
            if mass > alpha:
                eligible.append(risk)
        result.append(max(eligible, default=0))
    return tuple(result)


def validate_source_hashes(registration):
    rows = []
    for relative, expected in registration["source_sha256"].items():
        path = REPO / relative
        actual = sha256(path) if path.is_file() else None
        rows.append(
            {
                "path": relative,
                "expected": expected,
                "actual": actual,
                "match": actual == expected,
            }
        )
    return all(row["match"] for row in rows), rows


def run_tests(expected):
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        str(HERE / "test_direct_map_completeness.py"),
        str(HERE / "test_verifier_v0_52.py"),
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
        "ok": (
            completed.returncode == 0
            and f"{expected} passed" in output
        ),
        "expected": expected,
        "returncode": completed.returncode,
        "output": output,
    }


def exhaustive_census(registration):
    tables = independent_monotone_tables()
    report_alphabet = (0, 1, 2)
    weights = denominator_six_grid()
    valid_count = 0
    invalid_count = 0
    order_checks = 0
    strict_checks = 0
    dominance_mismatches = 0
    validity_mismatches = 0
    optimum_checks = 0
    optimum_mismatches = 0
    per_table = []
    digest = hashlib.sha256()

    for table_index, table in enumerate(tables):
        valid_maps = []
        row_order_checks = 0
        row_strict_checks = 0
        for reports in product(report_alphabet, repeat=3):
            if not independent_valid(table, reports):
                invalid_count += 1
                continue
            valid_count += 1
            valid_maps.append(reports)
            for order in independent_orders(reports):
                candidate = independent_buehler(table, order)
                order_checks += 1
                row_order_checks += 1
                if not independent_valid(table, candidate):
                    validity_mismatches += 1
                if not all(
                    left <= right
                    for left, right in zip(candidate, reports)
                ):
                    dominance_mismatches += 1
                if any(
                    left < right
                    for left, right in zip(candidate, reports)
                ):
                    strict_checks += 1
                    row_strict_checks += 1

        buehler_maps = tuple(
            dict.fromkeys(
                independent_buehler(table, order)
                for order in permutations(range(3))
            )
        )
        table_values = []
        for reference in weights:
            direct_value = min(
                independent_cost(reports, reference)
                for reports in valid_maps
            )
            buehler_value = min(
                independent_cost(reports, reference)
                for reports in buehler_maps
            )
            optimum_checks += 1
            optimum_mismatches += direct_value != buehler_value
            table_values.append(
                {
                    "reference": [qstr(value) for value in reference],
                    "direct": qstr(direct_value),
                    "buehler": qstr(buehler_value),
                }
            )
        row = {
            "index": table_index,
            "table": list(table),
            "valid_direct_maps": len(valid_maps),
            "consistent_order_checks": row_order_checks,
            "strict_dominance_checks": row_strict_checks,
            "optima": table_values,
        }
        encoded = json.dumps(
            row, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        digest.update(encoded)
        per_table.append(row)

    return {
        "table_count": len(tables),
        "candidate_direct_map_count": len(tables) * 27,
        "valid_direct_map_count": valid_count,
        "invalid_direct_map_count": invalid_count,
        "consistent_order_check_count": order_checks,
        "strict_dominance_check_count": strict_checks,
        "dominance_mismatch_count": dominance_mismatches,
        "buehler_validity_mismatch_count": validity_mismatches,
        "reference_grid_count": len(weights),
        "global_optimum_check_count": optimum_checks,
        "global_optimum_mismatch_count": optimum_mismatches,
        "census_sha256": digest.hexdigest(),
        "per_table": per_table,
        "expected": registration["expected_census"],
    }


def controls():
    table = (0, 1, 1, 2)
    equality = independent_buehler(table, (0, 1))
    strict = independent_buehler(table, (0, 1))
    reconstructed = table_from_experiment(
        (1, 1, 2),
        (
            (Q(1), Q(0)),
            (Q(0), Q(1)),
            (Q(1, 2), Q(1, 2)),
        ),
        Q(1, 2),
    )
    return {
        "table": list(table),
        "equality_input": [1, 2],
        "equality_output": list(equality),
        "strict_input": [2, 2],
        "strict_output": list(strict),
        "strict_coordinates": [
            index
            for index, (left, right) in enumerate(
                zip(strict, (2, 2))
            )
            if left < right
        ],
        "reconstructed_table": list(reconstructed),
    }


def main() -> None:
    registration_path = (
        HERE / "verification_registration_v0_52.json"
    )
    output = HERE / "VERIFY_RESULT_v0_52.json"
    if output.exists():
        raise FileExistsError(
            "write-once verification result already exists"
        )
    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    started = time.perf_counter()
    process = psutil.Process()

    source_ok, source_checks = validate_source_hashes(registration)
    tests = run_tests(registration["expected_test_count"])
    census = exhaustive_census(registration)
    control = controls()
    elapsed = time.perf_counter() - started
    peak = process.memory_info().peak_wset

    expected = registration["expected_census"]
    gates = {
        "H0": source_ok,
        "T0": tests["ok"],
        "U0": all(
            census[key] == value
            for key, value in expected.items()
        ),
        "D0": (
            census["consistent_order_check_count"]
            == expected["consistent_order_check_count"]
            and census["strict_dominance_check_count"]
            == expected["strict_dominance_check_count"]
            and census["dominance_mismatch_count"] == 0
            and census["buehler_validity_mismatch_count"] == 0
        ),
        "O0": (
            census["global_optimum_check_count"]
            == expected["global_optimum_check_count"]
            and census["global_optimum_mismatch_count"] == 0
        ),
        "C0": (
            control["table"] == [0, 1, 1, 2]
            and control["equality_output"] == [1, 2]
            and control["strict_output"] == [1, 2]
            and control["strict_coordinates"] == [0]
        ),
        "X0": control["reconstructed_table"] == [0, 1, 1, 2],
        "RESOURCE": (
            elapsed <= registration["resource_caps"]["seconds"]
            and peak
            <= registration["resource_caps"][
                "peak_working_set_bytes"
            ]
            and registration["resource_caps"]["workers"] == 1
        ),
    }
    result = {
        "schema": "asmp9-v0.52-verification-result-v1",
        "protocol_id": registration["protocol_id"],
        "registration_sha256": hashlib.sha256(
            registration_bytes
        ).hexdigest(),
        "source_commit": registration["source_commit"],
        "ok": all(gates.values()),
        "status": (
            "deterministic_direct_map_completeness_verified"
            if all(gates.values())
            else "verification_failed"
        ),
        "gates": gates,
        "source_checks": source_checks,
        "tests": tests,
        "census": census,
        "controls": control,
        "resource": {
            "elapsed_seconds": elapsed,
            "peak_working_set_bytes": peak,
            "worker_processes": 1,
        },
        "claim_boundary": registration["claim_boundary"],
    }
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
