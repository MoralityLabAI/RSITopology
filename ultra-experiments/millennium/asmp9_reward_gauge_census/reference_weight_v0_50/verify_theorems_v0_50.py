"""Independent exhaustive verification for ASMP-9 v0.50."""

from __future__ import annotations

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

from reference_weight import (
    minimal_reference_switch_witness,
    minimax_regret_certificate,
    ordering_cost,
    ordering_weight_region,
    robust_chain_certificate,
    weight_region_contains,
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


def monotone_binary_tables(width: int):
    size = 1 << width
    result = []
    for encoded in range(1 << size):
        table = tuple(
            Q((encoded >> mask) & 1) for mask in range(size)
        )
        if table[0]:
            continue
        valid = True
        for mask in range(size):
            for index in range(width):
                bit = 1 << index
                if not mask & bit and table[mask] > table[mask | bit]:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            result.append(table)
    return tuple(result)


def exhaustive_optima(bounds, weights):
    orders = tuple(permutations(range(len(weights))))
    rows = {
        order: ordering_cost(order, bounds, weights)
        for order in orders
    }
    optimum = min(rows.values())
    return frozenset(
        order for order, value in rows.items() if value == optimum
    )


def exhaustive_common(bound_tables, vertices):
    result = set(permutations(range(len(vertices[0]))))
    for table in bound_tables:
        for vertex in vertices:
            result.intersection_update(
                exhaustive_optima(table, vertex)
            )
    return frozenset(result)


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
        str(HERE / "test_reference_weight.py"),
        str(HERE / "test_verifier_v0_50.py"),
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


def positive_denominator_grid(total: int, width: int):
    if width != 3:
        raise ValueError("frozen verifier expects width three")
    return tuple(
        (Q(first, total), Q(second, total), Q(third, total))
        for first in range(1, total)
        for second in range(1, total - first)
        for third in (total - first - second,)
        if third > 0
    )


def exhaustive_universe_audit(registration):
    tables = monotone_binary_tables(3)
    vertices = tuple(
        tuple(Q(value) for value in row)
        for row in registration["reference_vertices"]
    )
    pair_mismatches = 0
    regret_mismatches = 0
    interpolation_mismatches = 0
    robust_pair_count = 0
    no_robust_pair_count = 0
    interpolation_checks = 0
    coefficients = tuple(
        Q(value)
        for value in registration["interpolation_coefficients"]
    )

    for first in tables:
        for second in tables:
            bound_tables = (first, second)
            exact = exhaustive_common(bound_tables, vertices)
            certificate = robust_chain_certificate(
                bound_tables, vertices
            )
            if (
                certificate.robust_optimizer_count != len(exact)
                or certificate.robust_optimizer_exists != bool(exact)
                or (
                    exact
                    and certificate.lexicographic_robust_order
                    != min(exact)
                )
                or (
                    not exact
                    and certificate.lexicographic_robust_order is not None
                )
            ):
                pair_mismatches += 1

            regret = minimax_regret_certificate(
                bound_tables, vertices
            )
            if (regret.optimum == 0) != bool(exact):
                regret_mismatches += 1

            if exact:
                robust_pair_count += 1
                order = min(exact)
                for coefficient in coefficients:
                    point = tuple(
                        coefficient * vertices[0][index]
                        + (1 - coefficient) * vertices[1][index]
                        for index in range(3)
                    )
                    for table in bound_tables:
                        interpolation_checks += 1
                        if order not in exhaustive_optima(table, point):
                            interpolation_mismatches += 1
            else:
                no_robust_pair_count += 1

    grid = positive_denominator_grid(
        registration["region_grid_denominator"], 3
    )
    region_checks = 0
    region_mismatches = 0
    orders = tuple(permutations(range(3)))
    for table in tables:
        for order in orders:
            region = ordering_weight_region(order, (table,))
            for point in grid:
                region_checks += 1
                exact = order in exhaustive_optima(table, point)
                if weight_region_contains(region, point) != exact:
                    region_mismatches += 1

    return {
        "table_count": len(tables),
        "expected_table_count": registration[
            "expected_admissible_table_count"
        ],
        "ordered_pair_count": len(tables) ** 2,
        "expected_ordered_pair_count": registration[
            "expected_ordered_pair_count"
        ],
        "robust_pair_count": robust_pair_count,
        "no_robust_pair_count": no_robust_pair_count,
        "robust_chain_mismatches": pair_mismatches,
        "regret_equivalence_mismatches": regret_mismatches,
        "interpolation_checks": interpolation_checks,
        "interpolation_mismatches": interpolation_mismatches,
        "region_grid_count": len(grid),
        "region_checks": region_checks,
        "expected_region_checks": registration[
            "expected_region_checks"
        ],
        "region_mismatches": region_mismatches,
    }


def minimal_witness_audit():
    witness = minimal_reference_switch_witness()
    return {
        "bounds": [qstr(value) for value in witness["bounds"]],
        "vertices": [
            [qstr(value) for value in row]
            for row in witness["vertices"]
        ],
        "robust_optimizer_count": witness[
            "robust_optimizer_count"
        ],
        "boundary_size": len(witness["boundary"]),
        "minimax_regret": qstr(witness["minimax_regret"]),
        "minimax_optimizer_count": witness[
            "minimax_optimizer_count"
        ],
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
    certificate = robust_chain_certificate(
        (
            tuple(Q(value) for value in subset["classification"]),
            tuple(Q(value) for value in subset["root_group"]),
        ),
        (weights,),
    )
    return {
        "robust_optimizer_count": certificate.robust_optimizer_count,
        "robust_optimizer_exists": certificate.robust_optimizer_exists,
    }


def main() -> None:
    registration_path = HERE / "verification_registration_v0_50.json"
    output = HERE / "VERIFY_RESULT_v0_50.json"
    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    started = time.perf_counter()
    process = psutil.Process()
    source_match, source_checks = validate_source_hashes(registration)
    tests = run_tests(registration["expected_test_count"])
    exhaustive = exhaustive_universe_audit(registration)
    minimal = minimal_witness_audit()
    v048 = recover_v048()
    elapsed = time.perf_counter() - started
    peak = process.memory_info().peak_wset

    gates = {
        "H0": source_match,
        "T0": tests["ok"],
        "D0": (
            exhaustive["table_count"]
            == exhaustive["expected_table_count"]
            and exhaustive["ordered_pair_count"]
            == exhaustive["expected_ordered_pair_count"]
            and exhaustive["robust_chain_mismatches"] == 0
        ),
        "R0": (
            exhaustive["region_checks"]
            == exhaustive["expected_region_checks"]
            and exhaustive["region_mismatches"] == 0
        ),
        "V0": (
            exhaustive["interpolation_checks"] > 0
            and exhaustive["interpolation_mismatches"] == 0
        ),
        "M0": (
            minimal["bounds"] == ["0", "0", "0", "1"]
            and minimal["robust_optimizer_count"] == 0
            and minimal["boundary_size"] > 0
            and minimal["minimax_regret"] == "1/2"
            and minimal["minimax_optimizer_count"] == 2
        ),
        "Q0": exhaustive["regret_equivalence_mismatches"] == 0,
        "B0": (
            v048["robust_optimizer_count"] == 1_451_520
            and v048["robust_optimizer_exists"]
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
        "schema": "asmp9-v0.50-theorem-verification-v1",
        "protocol_id": registration["protocol_id"],
        "registration_sha256": hashlib.sha256(
            registration_bytes
        ).hexdigest(),
        "status": (
            "finite_reference_weight_theorem_verified"
            if ok
            else "finite_reference_weight_theorem_not_verified"
        ),
        "ok": ok,
        "gates": gates,
        "tests": tests,
        "exhaustive_three_outcome": exhaustive,
        "minimal_witness": minimal,
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
