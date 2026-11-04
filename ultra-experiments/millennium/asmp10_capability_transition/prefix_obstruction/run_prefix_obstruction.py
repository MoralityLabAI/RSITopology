#!/usr/bin/env python3
"""Exact Hermite-prefix obstruction census for ASMP-10."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def derivative_monomial(degree: int, order: int, x: int) -> Fraction:
    if degree < order:
        return Fraction(0)
    coefficient = math.factorial(degree) // math.factorial(degree - order)
    return Fraction(coefficient * (x ** (degree - order)))


def hermite_matrix(n_nodes: int, jet_order: int, degree: int) -> list[list[Fraction]]:
    return [
        [derivative_monomial(column, order, node) for column in range(degree + 1)]
        for node in range(n_nodes)
        for order in range(jet_order + 1)
    ]


def exact_rank(matrix: Iterable[Iterable[Fraction]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next((r for r in range(pivot_row, rows) if work[r][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def multiply_polynomials(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return out


def invisible_witness(n_nodes: int, jet_order: int) -> list[Fraction]:
    coefficients = [Fraction(1)]
    for node in range(n_nodes):
        factor = [Fraction(-node), Fraction(1)]
        for _ in range(jet_order + 1):
            coefficients = multiply_polynomials(coefficients, factor)
    return coefficients


def matvec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum((a * b for a, b in zip(row, vector)), Fraction(0)) for row in matrix]


def polynomial_derivative_value(coefficients: list[Fraction], x: int) -> Fraction:
    return sum(
        (Fraction(degree) * coefficient * (x ** (degree - 1))
         for degree, coefficient in enumerate(coefficients) if degree),
        Fraction(0),
    )


def mirage_pair(n_nodes: int, jet_order: int) -> dict[str, object]:
    witness = invisible_witness(n_nodes, jet_order)
    threshold_degree = n_nodes * (jet_order + 1)
    matrix = hermite_matrix(n_nodes, jet_order, threshold_degree)
    kernel_values = matvec(matrix, witness)
    derivative_at_unobserved = polynomial_derivative_value(witness, n_nodes)
    if derivative_at_unobserved == 0:
        raise AssertionError("registered witness has zero derivative at the first unobserved node")
    epsilon = Fraction(1, 1) / derivative_at_unobserved

    plus_state = Fraction(0)
    minus_state = Fraction(0)
    prefix_equal = True
    for _ in range(n_nodes):
        # The perturbation gradient vanishes at every registered prefix node.
        plus_state += 1
        minus_state += 1
        prefix_equal = prefix_equal and plus_state == minus_state

    plus_future = plus_state - (-1 + epsilon * derivative_at_unobserved)
    minus_future = minus_state - (-1 - epsilon * derivative_at_unobserved)
    threshold = Fraction(n_nodes + 1)
    plus_score = plus_future - threshold
    minus_score = minus_future - threshold

    return {
        "degree": threshold_degree,
        "kernel_exact": all(value == 0 for value in kernel_values),
        "prefix_equal": prefix_equal and plus_state == n_nodes and minus_state == n_nodes,
        "epsilon": str(epsilon),
        "q_prime_at_first_unobserved": str(derivative_at_unobserved),
        "plus_future_state": str(plus_future),
        "minus_future_state": str(minus_future),
        "plus_future_score": str(plus_score),
        "minus_future_score": str(minus_score),
        "capabilities_differ": (plus_score > 0) != (minus_score > 0),
    }


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def validate_registration(path: Path) -> dict[str, object]:
    registration = json.loads(path.read_text(encoding="utf-8"))
    bindings = registration["bindings"]
    expected = {
        ROOT / "PROTOCOL_v0_1.md": bindings["protocol_sha256"],
        ROOT / "run_prefix_obstruction.py": bindings["runner_sha256"],
        ROOT / "test_prefix_obstruction.py": bindings["tests_sha256"],
    }
    mismatches = [
        str(file_path)
        for file_path, expected_hash in expected.items()
        if sha256_file(file_path) != expected_hash
    ]
    if mismatches:
        raise RuntimeError(f"registration binding mismatch: {mismatches}")
    return registration


def run_census() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    witnesses: list[dict[str, object]] = []
    for n_nodes in (1, 2, 3, 4, 6):
        for jet_order in (1, 2, 3):
            observations = n_nodes * (jet_order + 1)
            degrees = sorted({max(0, observations - 2), observations - 1, observations, observations + 1})
            for degree in degrees:
                rank = exact_rank(hermite_matrix(n_nodes, jet_order, degree))
                rows.append(
                    {
                        "n_nodes": n_nodes,
                        "jet_order": jet_order,
                        "degree": degree,
                        "observations": observations,
                        "rank": rank,
                        "expected_rank": min(degree + 1, observations),
                        "nullity": degree + 1 - rank,
                    }
                )
            witness = mirage_pair(n_nodes, jet_order)
            witness.update({"n_nodes": n_nodes, "jet_order": jet_order})
            witnesses.append(witness)

    r0 = all(row["rank"] == row["expected_rank"] for row in rows)
    i0_rows = [row for row in rows if row["degree"] == row["observations"] - 1]
    i0 = bool(i0_rows) and all(row["nullity"] == 0 for row in i0_rows)
    o0 = all(
        witness["degree"] == witness["n_nodes"] * (witness["jet_order"] + 1)
        and witness["kernel_exact"]
        and witness["prefix_equal"]
        and witness["plus_future_score"] == "-1"
        and witness["minus_future_score"] == "1"
        and witness["capabilities_differ"]
        for witness in witnesses
    )
    c0 = any(row["nullity"] > 0 for row in rows) and any(row["nullity"] == 0 for row in rows)
    gates = {"R0_exact_rank": r0, "I0_identification": i0, "O0_obstruction": o0, "C0_controls": c0}
    verdict = (
        "finite_prefix_obstruction_established_for_registered_class"
        if all(gates.values())
        else "instrument_failed"
    )
    return {"schema_version": "asmp10_prefix_obstruction_result_v0_1", "gates": gates, "verdict": verdict, "rows": rows, "witnesses": witnesses}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    registration = validate_registration(args.registration.resolve())
    result = run_census()
    result_path = args.output_dir.resolve() / "result.json"
    atomic_json(result_path, result)
    receipt = {
        "schema_version": "asmp10_prefix_obstruction_receipt_v0_1",
        "registration_sha256": sha256_file(args.registration.resolve()),
        "registration_source_commit": registration["source_commit"],
        "result_sha256": sha256_file(result_path),
        "verdict": result["verdict"],
    }
    atomic_json(args.output_dir.resolve() / "receipt.json", receipt)
    print(json.dumps({"gates": result["gates"], "verdict": result["verdict"]}, sort_keys=True))
    return 0 if result["verdict"] != "instrument_failed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

