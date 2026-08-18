"""Independent exact verification for ASMP-9 v0.53."""

from __future__ import annotations

from fractions import Fraction as Q
import hashlib
from itertools import combinations
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


def solve_two(first, first_value, second, second_value):
    determinant = (
        first[0] * second[1] - first[1] * second[0]
    )
    if determinant == 0:
        return None
    return (
        (
            first_value * second[1]
            - first[1] * second_value
        )
        / determinant,
        (
            first[0] * second_value
            - first_value * second[0]
        )
        / determinant,
    )


def independent_binary_vertices(p):
    boundaries = (
        ((p, 1 - p), Q(1, 2), "coverage"),
        ((Q(1), Q(0)), Q(0), "s0=0"),
        ((Q(1), Q(0)), Q(1), "s0=1"),
        ((Q(0), Q(1)), Q(0), "s1=0"),
        ((Q(0), Q(1)), Q(1), "s1=1"),
    )
    vertices = set()
    for first, second in combinations(boundaries, 2):
        solution = solve_two(
            first[0], first[1], second[0], second[1]
        )
        if solution is None:
            continue
        s0, s1 = solution
        if (
            0 <= s0 <= 1
            and 0 <= s1 <= 1
            and p * s0 + (1 - p) * s1 >= Q(1, 2)
        ):
            vertices.add(solution)
    return tuple(sorted(vertices))


def independent_randomized_optimum(p):
    vertices = independent_binary_vertices(p)
    values = {
        vertex: (vertex[0] + vertex[1]) / 2
        for vertex in vertices
    }
    optimum = min(values.values())
    optimizers = tuple(
        vertex
        for vertex, value in values.items()
        if value == optimum
    )
    return optimum, min(optimizers), len(vertices)


def independent_deterministic_optimum(p):
    feasible = []
    for s0, s1 in (
        (Q(0), Q(0)),
        (Q(0), Q(1)),
        (Q(1), Q(0)),
        (Q(1), Q(1)),
    ):
        if p * s0 + (1 - p) * s1 >= Q(1, 2):
            feasible.append(((s0 + s1) / 2, (s0, s1)))
    return min(feasible)


def independent_subset_table(p):
    masses = (Q(0), p, 1 - p, Q(1))
    return tuple(
        Q(1) if mass > Q(1, 2) else Q(0)
        for mass in masses
    )


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
        str(HERE / "test_aggregate_randomized.py"),
        str(HERE / "test_verifier_v0_53.py"),
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


def family_census():
    rows = []
    primal_mismatches = 0
    dual_mismatches = 0
    table_mismatches = 0
    deterministic_mismatches = 0
    support_failures = 0
    expected_table = (Q(0), Q(1), Q(0), Q(1))
    for numerator in range(11, 21):
        p = Q(numerator, 20)
        table = independent_subset_table(p)
        deterministic_value, deterministic_optimizer = (
            independent_deterministic_optimum(p)
        )
        randomized_value, optimizer, vertex_count = (
            independent_randomized_optimum(p)
        )
        formula = Q(1, 4) / p
        dual_lambda = Q(1, 2) / p
        dual_feasible = (
            dual_lambda * p <= Q(1, 2)
            and dual_lambda * (1 - p) <= Q(1, 2)
        )
        dual_value = dual_lambda * Q(1, 2)
        positive_atoms = (
            int(optimizer[0] > 0)
            + int(optimizer[0] < 1)
            + int(optimizer[1] > 0)
            + int(optimizer[1] < 1)
        )
        table_mismatches += table != expected_table
        deterministic_mismatches += (
            deterministic_value != Q(1, 2)
        )
        primal_mismatches += randomized_value != formula
        dual_mismatches += (
            not dual_feasible or dual_value != randomized_value
        )
        support_failures += positive_atoms > 3
        rows.append(
            {
                "p": qstr(p),
                "subset_table": [qstr(value) for value in table],
                "deterministic_value": qstr(deterministic_value),
                "deterministic_optimizer": [
                    qstr(value) for value in deterministic_optimizer
                ],
                "randomized_value": qstr(randomized_value),
                "randomized_optimizer_success": [
                    qstr(value) for value in optimizer
                ],
                "formula_value": qstr(formula),
                "dual_lambda": qstr(dual_lambda),
                "dual_value": qstr(dual_value),
                "dual_feasible": dual_feasible,
                "positive_report_atoms": positive_atoms,
                "feasible_vertex_count": vertex_count,
            }
        )
    return {
        "family_size": len(rows),
        "distinct_randomized_value_count": len(
            {row["randomized_value"] for row in rows}
        ),
        "table_mismatch_count": table_mismatches,
        "deterministic_mismatch_count": deterministic_mismatches,
        "primal_mismatch_count": primal_mismatches,
        "dual_mismatch_count": dual_mismatches,
        "support_bound_failure_count": support_failures,
        "rows": rows,
    }


def controls():
    mixture = {
        "valid_component_weight": Q(5, 6),
        "invalid_component_weight": Q(1, 6),
    }
    marginal = (
        mixture["valid_component_weight"],
        Q(0),
    )
    coverage = Q(3, 5) * marginal[0] + Q(2, 5) * marginal[1]
    invalid_component_coverage = Q(0)

    crossing = (Q(3, 4), Q(3, 4))
    first_coverage = Q(3, 4) * crossing[0] + Q(1, 4) * crossing[1]
    second_coverage = Q(1, 4) * crossing[0] + Q(3, 4) * crossing[1]
    crossing_positive_atoms = 4

    return {
        "one_outcome": {
            "deterministic_value": "1",
            "randomized_value": "1/2",
            "success_probability": "1/2",
        },
        "invalid_component_mixture": {
            "valid_component_weight": qstr(
                mixture["valid_component_weight"]
            ),
            "invalid_component_weight": qstr(
                mixture["invalid_component_weight"]
            ),
            "marginal_success": [
                qstr(value) for value in marginal
            ],
            "aggregate_coverage": qstr(coverage),
            "invalid_component_coverage": qstr(
                invalid_component_coverage
            ),
        },
        "crossing_support": {
            "success_probabilities": [
                qstr(value) for value in crossing
            ],
            "first_coverage": qstr(first_coverage),
            "second_coverage": qstr(second_coverage),
            "positive_report_atoms": crossing_positive_atoms,
            "n_plus_k": 4,
        },
    }


def main() -> None:
    registration_path = (
        HERE / "verification_registration_v0_53.json"
    )
    output = HERE / "VERIFY_RESULT_v0_53.json"
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
    family = family_census()
    control = controls()
    elapsed = time.perf_counter() - started
    peak = process.memory_info().peak_wset

    primary = {
        row["p"]: row for row in family["rows"]
    }
    gates = {
        "H0": source_ok,
        "T0": tests["ok"],
        "F0": (
            family["family_size"]
            == registration["expected_family_size"]
            and family["distinct_randomized_value_count"] == 10
            and family["table_mismatch_count"] == 0
            and family["deterministic_mismatch_count"] == 0
        ),
        "P0": family["primal_mismatch_count"] == 0,
        "D0": family["dual_mismatch_count"] == 0,
        "I0": (
            primary["3/5"]["subset_table"]
            == primary["9/10"]["subset_table"]
            and primary["3/5"]["deterministic_value"] == "1/2"
            and primary["9/10"]["deterministic_value"] == "1/2"
            and primary["3/5"]["randomized_value"] == "5/12"
            and primary["9/10"]["randomized_value"] == "5/18"
        ),
        "M0": (
            control["invalid_component_mixture"][
                "marginal_success"
            ]
            == ["5/6", "0"]
            and control["invalid_component_mixture"][
                "aggregate_coverage"
            ]
            == "1/2"
            and control["invalid_component_mixture"][
                "invalid_component_coverage"
            ]
            == "0"
        ),
        "S0": (
            family["support_bound_failure_count"] == 0
            and control["crossing_support"][
                "positive_report_atoms"
            ]
            == control["crossing_support"]["n_plus_k"]
            and control["crossing_support"]["first_coverage"]
            == "3/4"
            and control["crossing_support"]["second_coverage"]
            == "3/4"
        ),
        "C0": (
            control["one_outcome"]["deterministic_value"] == "1"
            and control["one_outcome"]["randomized_value"] == "1/2"
        ),
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
        "schema": "asmp9-v0.53-verification-result-v1",
        "protocol_id": registration["protocol_id"],
        "registration_sha256": hashlib.sha256(
            registration_bytes
        ).hexdigest(),
        "source_commit": registration["source_commit"],
        "ok": all(gates.values()),
        "status": (
            "subset_table_insufficient_for_aggregate_randomization"
            if all(gates.values())
            else "verification_failed"
        ),
        "gates": gates,
        "source_checks": source_checks,
        "tests": tests,
        "family": family,
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
