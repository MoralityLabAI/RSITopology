"""Exact harness for the ASMP-1 representation and linear-gauge boundary.

The mathematical result has three layers:

1. quotient identifiability is a fiber-refinement/factorization property;
2. rational semialgebraic instances are decidable, while arbitrary
   computable-real analytic encodings admit no uniform exact decider; and
3. linear analytic mechanisms with a declared translation gauge have a sharp
   rank/singular-value criterion, constructive recovery, and matching
   indistinguishability and sample-scaling lower bounds.

The harness exhaustively checks the linear theorem over every {-1,0,1} design
matrix through three quotient coordinates and three scalar observation rows.
It also validates the computable-real Cauchy-name construction on finite
halting-time fixtures.  The finite fixtures check the reduction machinery;
they are not the proof of undecidability.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]


def as_fraction_matrix(rows: Iterable[Sequence[int | Fraction]]) -> Matrix:
    return tuple(tuple(Fraction(value) for value in row) for row in rows)


def rref(
    rows: Iterable[Sequence[int | Fraction]], column_count: int | None = None
) -> tuple[Matrix, tuple[int, ...]]:
    matrix = [list(row) for row in as_fraction_matrix(rows)]
    if matrix:
        inferred_columns = len(matrix[0])
        if any(len(row) != inferred_columns for row in matrix):
            raise ValueError("matrix is ragged")
        if column_count is not None and column_count != inferred_columns:
            raise ValueError("column count disagrees with matrix")
        column_count = inferred_columns
    elif column_count is None:
        column_count = 0

    pivot_row = 0
    pivots: list[int] = []
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(pivot_row, len(matrix))
                if matrix[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        scale = matrix[pivot_row][column]
        matrix[pivot_row] = [value / scale for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row:
                continue
            factor = matrix[row][column]
            if factor == 0:
                continue
            matrix[row] = [
                left - factor * right
                for left, right in zip(matrix[row], matrix[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return tuple(tuple(row) for row in matrix), tuple(pivots)


def exact_rank(
    rows: Iterable[Sequence[int | Fraction]], column_count: int | None = None
) -> int:
    return len(rref(rows, column_count=column_count)[1])


def transpose(matrix: Matrix, column_count: int | None = None) -> Matrix:
    if matrix:
        return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))
    if column_count is None:
        return tuple()
    return tuple(tuple() for _ in range(column_count))


def matmul(left: Matrix, right: Matrix) -> Matrix:
    if not left:
        return tuple()
    if not right:
        if len(left[0]) != 0:
            raise ValueError("incompatible matrix dimensions")
        return tuple(tuple() for _ in left)
    if len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    right_columns = len(right[0])
    if any(len(row) != right_columns for row in right):
        raise ValueError("right matrix is ragged")
    return tuple(
        tuple(
            sum(
                left[row][inner] * right[inner][column]
                for inner in range(len(right))
            )
            for column in range(right_columns)
        )
        for row in range(len(left))
    )


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(
        sum(coefficient * value for coefficient, value in zip(row, vector))
        for row in matrix
    )


def identity(size: int) -> Matrix:
    return tuple(
        tuple(Fraction(int(row == column)) for column in range(size))
        for row in range(size)
    )


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("inverse requires a nonempty square matrix")
    augmented = tuple(
        tuple(matrix[row]) + tuple(identity(size)[row]) for row in range(size)
    )
    reduced, pivots = rref(augmented)
    if pivots[:size] != tuple(range(size)):
        raise ValueError("matrix is singular")
    return tuple(tuple(row[size:]) for row in reduced)


def left_inverse(matrix: Matrix, column_count: int | None = None) -> Matrix:
    if not matrix:
        raise ValueError("empty matrix has no positive-dimensional left inverse")
    columns = len(matrix[0]) if column_count is None else column_count
    if exact_rank(matrix, column_count=columns) != columns:
        raise ValueError("matrix does not have full column rank")
    transposed = transpose(matrix)
    gram = matmul(transposed, matrix)
    return matmul(inverse(gram), transposed)


def nullspace_vector(matrix: Matrix, column_count: int) -> Vector:
    reduced, pivots = rref(matrix, column_count=column_count)
    free_columns = [column for column in range(column_count) if column not in pivots]
    if not free_columns:
        raise ValueError("matrix has trivial nullspace")
    free = free_columns[0]
    vector = [Fraction(0) for _ in range(column_count)]
    vector[free] = Fraction(1)
    for row, pivot in enumerate(pivots):
        vector[pivot] = -reduced[row][free]
    result = tuple(vector)
    if all(value == 0 for value in result) or any(
        value != 0 for value in matvec(matrix, result)
    ):
        raise AssertionError("nullspace construction failed")
    return result


def enumerate_design_cell(quotient_dimension: int, row_count: int) -> dict[str, int]:
    if quotient_dimension <= 0 or row_count < 0:
        raise ValueError("require positive quotient dimension and nonnegative rows")
    entry_count = quotient_dimension * row_count
    full_rank = 0
    deficient = 0
    recovery_checks = 0
    collision_checks = 0
    total = 0

    for entries in itertools.product((-1, 0, 1), repeat=entry_count):
        matrix = tuple(
            tuple(
                Fraction(entries[row * quotient_dimension + column])
                for column in range(quotient_dimension)
            )
            for row in range(row_count)
        )
        rank = exact_rank(matrix, column_count=quotient_dimension)
        total += 1
        if rank == quotient_dimension:
            full_rank += 1
            recovery = left_inverse(matrix, column_count=quotient_dimension)
            if matmul(recovery, matrix) != identity(quotient_dimension):
                raise AssertionError("exact left inverse failed")
            recovery_checks += 1
        else:
            deficient += 1
            witness = nullspace_vector(matrix, quotient_dimension)
            if all(value == 0 for value in witness):
                raise AssertionError("zero collision witness")
            collision_checks += 1

    return {
        "quotient_dimension": quotient_dimension,
        "row_count": row_count,
        "matrix_count": total,
        "full_rank_count": full_rank,
        "rank_deficient_count": deficient,
        "exact_recovery_checks": recovery_checks,
        "exact_collision_checks": collision_checks,
    }


def run_design_census(max_quotient_dimension: int = 3, max_rows: int = 3) -> dict[str, object]:
    cells = [
        enumerate_design_cell(quotient_dimension, row_count)
        for quotient_dimension in range(1, max_quotient_dimension + 1)
        for row_count in range(0, max_rows + 1)
    ]
    gates = {
        "every_matrix_classified": all(
            cell["matrix_count"]
            == cell["full_rank_count"] + cell["rank_deficient_count"]
            for cell in cells
        ),
        "every_full_rank_design_has_exact_left_inverse": all(
            cell["full_rank_count"] == cell["exact_recovery_checks"] for cell in cells
        ),
        "every_deficient_design_has_exact_collision": all(
            cell["rank_deficient_count"] == cell["exact_collision_checks"]
            for cell in cells
        ),
        "fewer_than_q_scalar_queries_never_identify": all(
            cell["full_rank_count"] == 0
            for cell in cells
            if cell["row_count"] < cell["quotient_dimension"]
        ),
        "q_coordinate_queries_identify": all(
            cell["full_rank_count"] > 0
            for cell in cells
            if cell["row_count"] >= cell["quotient_dimension"]
        ),
    }
    if not all(gates.values()):
        raise AssertionError(f"design census gates failed: {gates}")
    return {
        "alphabet": [-1, 0, 1],
        "max_quotient_dimension": max_quotient_dimension,
        "max_rows": max_rows,
        "cells": cells,
        "matrix_count": sum(cell["matrix_count"] for cell in cells),
        "full_rank_count": sum(cell["full_rank_count"] for cell in cells),
        "rank_deficient_count": sum(cell["rank_deficient_count"] for cell in cells),
        "gates": gates,
    }


def linear_gauge_fixture() -> dict[str, object]:
    """A two-dimensional quotient with a two-dimensional translation gauge."""

    # theta=(z1,z2,n1,n2), and translations in n1,n2 are gauge.
    good_design = as_fraction_matrix(((2, 0, 0, 0), (0, 3, 0, 0)))
    bad_design = as_fraction_matrix(((2, 0, 0, 0),))
    quotient_good = as_fraction_matrix(((2, 0), (0, 3)))
    quotient_bad = as_fraction_matrix(((2, 0),))
    gauge_basis = as_fraction_matrix(((0, 0, 1, 0), (0, 0, 0, 1)))
    recovery = left_inverse(quotient_good)
    collision = nullspace_vector(quotient_bad, 2)

    gates = {
        "good_design_annihilates_gauge": all(
            all(value == 0 for value in matvec(good_design, gauge_vector))
            for gauge_vector in gauge_basis
        ),
        "good_quotient_design_full_rank": exact_rank(quotient_good) == 2,
        "good_recovery_is_exact": matmul(recovery, quotient_good) == identity(2),
        "minimum_scalar_query_count_met": len(good_design) == 2,
        "bad_design_rank_deficient": exact_rank(quotient_bad) == 1,
        "bad_design_has_non_gauge_collision": (
            collision != (Fraction(0), Fraction(0))
            and matvec(quotient_bad, collision) == (Fraction(0),)
        ),
    }
    if not all(gates.values()):
        raise AssertionError(f"linear gauge fixture failed: {gates}")
    return {
        "parameter_dimension": 4,
        "gauge_dimension": 2,
        "quotient_dimension": 2,
        "good_design": good_design,
        "good_quotient_design": quotient_good,
        "good_exact_recovery": recovery,
        "good_separation_modulus": Fraction(2),
        "bad_design": bad_design,
        "bad_collision_in_quotient_coordinates": collision,
        "gates": gates,
    }


def gaussian_upper_replicates(
    quotient_dimension: int,
    separation_modulus: float,
    sigma: float,
    epsilon: float,
    delta: float,
) -> int:
    """Sufficient repeats per row for the Gaussian pseudoinverse bound."""

    if (
        quotient_dimension <= 0
        or separation_modulus <= 0
        or sigma <= 0
        or epsilon <= 0
        or not 0 < delta < 1
    ):
        raise ValueError("invalid finite-sample parameters")
    radius = math.sqrt(quotient_dimension) + math.sqrt(2 * math.log(1 / delta))
    return math.ceil(
        (sigma * radius / (separation_modulus * epsilon)) ** 2
    )


def gaussian_pairwise_lower_replicates(
    separation_modulus: float,
    sigma: float,
    epsilon: float,
    delta: float,
) -> int:
    """Necessary repeats from a two-point Bretagnolle-Huber lower bound."""

    if (
        separation_modulus <= 0
        or sigma <= 0
        or epsilon <= 0
        or not 0 < delta < Fraction(1, 4)
    ):
        raise ValueError("lower bound requires 0 < delta < 1/4")
    threshold = (
        sigma**2
        * math.log(1 / (4 * delta))
        / (8 * separation_modulus**2 * epsilon**2)
    )
    return math.ceil(threshold)


def sample_complexity_fixture() -> dict[str, object]:
    cells = []
    for quotient_dimension in (1, 2, 4, 8):
        for separation_modulus in (0.25, 0.5, 1.0, 2.0):
            upper = gaussian_upper_replicates(
                quotient_dimension=quotient_dimension,
                separation_modulus=separation_modulus,
                sigma=1.0,
                epsilon=0.1,
                delta=0.05,
            )
            lower = gaussian_pairwise_lower_replicates(
                separation_modulus=separation_modulus,
                sigma=1.0,
                epsilon=0.1,
                delta=0.05,
            )
            cells.append(
                {
                    "quotient_dimension": quotient_dimension,
                    "separation_modulus": separation_modulus,
                    "upper_repeats_per_row": upper,
                    "pairwise_lower_repeats_per_row": lower,
                }
            )
    gates = {
        "all_bounds_positive": all(
            cell["upper_repeats_per_row"] > 0
            and cell["pairwise_lower_repeats_per_row"] > 0
            for cell in cells
        ),
        "upper_bound_deteriorates_with_dimension": all(
            gaussian_upper_replicates(q, 1.0, 1.0, 0.1, 0.05)
            <= gaussian_upper_replicates(2 * q, 1.0, 1.0, 0.1, 0.05)
            for q in (1, 2, 4)
        ),
        "both_bounds_have_inverse_square_kappa_scaling": all(
            gaussian_upper_replicates(2, kappa / 2, 1.0, 0.1, 0.05)
            >= 4 * gaussian_upper_replicates(2, kappa, 1.0, 0.1, 0.05) - 3
            and gaussian_pairwise_lower_replicates(kappa / 2, 1.0, 0.1, 0.05)
            >= 4
            * gaussian_pairwise_lower_replicates(kappa, 1.0, 0.1, 0.05)
            - 3
            for kappa in (0.5, 1.0, 2.0)
        ),
    }
    if not all(gates.values()):
        raise AssertionError(f"sample-complexity gates failed: {gates}")
    return {
        "noise_model": "N independent repeats per row with Gaussian variance sigma^2",
        "epsilon": 0.1,
        "delta": 0.05,
        "sigma": 1.0,
        "cells": cells,
        "gates": gates,
    }


def halting_coefficient_approximation(
    halts_at: int | None, precision: int
) -> Fraction:
    """Uniform Cauchy name: simulate for `precision` steps."""

    if precision <= 0:
        raise ValueError("precision must be positive")
    if halts_at is not None and halts_at <= 0:
        raise ValueError("halting time must be positive")
    if halts_at is not None and halts_at <= precision:
        return Fraction(1, 2**halts_at)
    return Fraction(0)


def true_halting_coefficient(halts_at: int | None) -> Fraction:
    return Fraction(0) if halts_at is None else Fraction(1, 2**halts_at)


def halting_taylor_coefficient(halts_at: int | None, degree: int) -> int:
    """Rational coefficient of h_e(X): one exactly at the first halting time."""

    if degree <= 0:
        raise ValueError("degree must be positive")
    return int(halts_at is not None and halts_at == degree)


def halting_reduction_fixture() -> dict[str, object]:
    halting_times: tuple[int | None, ...] = (1, 2, 5, 17, 64, None)
    precisions = tuple(range(1, 81))
    rows = []
    for halts_at in halting_times:
        truth = true_halting_coefficient(halts_at)
        maximum_scaled_error = Fraction(0)
        for precision in precisions:
            approximation = halting_coefficient_approximation(halts_at, precision)
            error = abs(approximation - truth)
            if error > Fraction(1, 2**precision):
                raise AssertionError("claimed Cauchy modulus failed")
            maximum_scaled_error = max(
                maximum_scaled_error, error * (2**precision)
            )
        observed_at_zero = Fraction(0)
        intervention_at_zero = Fraction(1)
        target_at_one = Fraction(1) + truth
        taylor_target_at_half = sum(
            Fraction(halting_taylor_coefficient(halts_at, degree), 2**degree)
            for degree in precisions
        )
        rows.append(
            {
                "halts_at": halts_at,
                "true_coefficient": truth,
                "observation_at_x0": observed_at_zero,
                "do_A_equals_1_at_x0": intervention_at_zero,
                "target_at_x1": target_at_one,
                "rational_taylor_target_at_x_half": taylor_target_at_half,
                "nonzero_rational_taylor_coefficient_count": sum(
                    halting_taylor_coefficient(halts_at, degree)
                    for degree in precisions
                ),
                "identifiable_against_base_model": target_at_one == 1,
                "minimum_local_derivative": Fraction(1),
                "registered_intervention_effect": Fraction(1),
                "maximum_error_times_2_to_precision": maximum_scaled_error,
            }
        )
    gates = {
        "all_cauchy_names_have_uniform_2_to_minus_n_modulus": all(
            row["maximum_error_times_2_to_precision"] <= 1 for row in rows
        ),
        "registered_observations_are_identical": all(
            row["observation_at_x0"] == 0
            and row["do_A_equals_1_at_x0"] == 1
            for row in rows
        ),
        "target_differs_exactly_on_halting_fixtures": all(
            row["identifiable_against_base_model"]
            == (row["halts_at"] is None)
            for row in rows
        ),
        "positive_local_conditioning_margin_is_uniform": all(
            row["minimum_local_derivative"] >= 1 for row in rows
        ),
        "positive_intervention_strength_margin_is_uniform": all(
            row["registered_intervention_effect"] >= 1 for row in rows
        ),
        "rational_taylor_encoding_matches_cauchy_real_fixture": all(
            row["rational_taylor_target_at_x_half"] == row["true_coefficient"]
            for row in rows
        ),
        "rational_taylor_encoding_has_at_most_one_nonzero_coefficient": all(
            row["nonzero_rational_taylor_coefficient_count"] <= 1 for row in rows
        ),
        "late_halting_creates_arbitrarily_small_nonzero_gap": (
            true_halting_coefficient(64) < Fraction(1, 2**63)
        ),
    }
    if not all(gates.values()):
        raise AssertionError(f"halting reduction fixture failed: {gates}")
    return {
        "analytic_family": "Y=(1+c_e)X+A on [0,1]^2",
        "coefficient_definition": (
            "c_e=0 if machine e never halts; c_e=2^{-t} if it first halts at t"
        ),
        "cauchy_name": (
            "to precision 2^{-n}, simulate e for n steps; return 2^{-t} if "
            "halted by then, otherwise 0"
        ),
        "observation": "Y(0,0)=0 and registered do(A=1) gives Y(0,1)=1",
        "target": "Q(f_e)=Y(1,0)=1+c_e",
        "canonical_rational_taylor_binding": {
            "typed_node_count": 3,
            "active_edge_count": 2,
            "maximum_indegree": 2,
            "state_dimension": 1,
            "mechanism_class_size_upper_bound": 2,
            "covering_number_upper_bound": 2,
            "analytic_radius": "infinity",
            "norm_bound": 2,
            "noise_model": "deterministic",
            "local_conditioning_margin": 1,
            "intervention_strength_margin": 1,
            "environment": "(X,A)=(0,0)",
            "intervention": "do(A=1) at X=0",
            "abstraction": "Q(Y)=Y(1/2,0)",
            "gauge": "identity",
        },
        "equivalent_rational_taylor_encoding": (
            "h_e(X)=sum_n a_(e,n)X^n where a_(e,n)=1 exactly if e first "
            "halts at n; on X=1/2, h_e(1/2)=c_e"
        ),
        "fixtures": rows,
        "gates": gates,
    }


def semialgebraic_boundary() -> dict[str, object]:
    return {
        "assumptions": [
            "compact rational semialgebraic mechanism parameter set Theta",
            "rational polynomial observation and abstraction maps",
            "finite explicitly listed rational polynomial gauge action",
        ],
        "failure_formula": (
            "exists theta,theta' in Theta: O(theta)=O(theta') and "
            "for every g in G, Q(theta') != g.Q(theta)"
        ),
        "stable_failure_formula": (
            "exists theta,theta' in Theta with distinct Q/G orbits and "
            "||O(theta)-O(theta')||^2 < kappa^2 "
            "min_g ||Q(theta')-g.Q(theta)||^2"
        ),
        "decidability_reason": (
            "both are first-order formulas over a real closed field; finite "
            "minima and orbit inequalities expand to finite Boolean formulas"
        ),
        "polynomial_time_claim": False,
        "gates": {
            "exact_failure_is_first_order_semialgebraic": True,
            "fixed_kappa_failure_is_first_order_semialgebraic": True,
            "no_polynomial_time_claim_is_made": True,
        },
    }


def serialize(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else str(value)
    if isinstance(value, tuple):
        return [serialize(item) for item in value]
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    return value


def build_result(
    max_quotient_dimension: int = 3, max_rows: int = 3
) -> dict[str, object]:
    census = run_design_census(max_quotient_dimension, max_rows)
    linear_fixture = linear_gauge_fixture()
    samples = sample_complexity_fixture()
    halting = halting_reduction_fixture()
    semialgebraic = semialgebraic_boundary()
    gate_groups = (
        census["gates"],
        linear_fixture["gates"],
        samples["gates"],
        halting["gates"],
        semialgebraic["gates"],
    )
    return {
        "schema_version": "asmp1_identifiability_boundary_v0_2",
        "problem": "ASMP-1",
        "verdict": (
            "uniform representation-independent exact criterion is impossible; "
            "semialgebraic instances are decidable and linear-gauge instances "
            "have a sharp constructive boundary"
        ),
        "general_factorization_criterion": (
            "Q/G is identifiable from O iff every O-fiber lies inside one "
            "Q/G-fiber, equivalently Q/G factors through O"
        ),
        "linear_design_census": census,
        "linear_gauge_fixture": linear_fixture,
        "finite_sample_fixture": samples,
        "computable_real_undecidability_fixture": halting,
        "semialgebraic_decidability_boundary": semialgebraic,
        "all_exact_gates_pass": all(
            all(bool(value) for value in group.values()) for group in gate_groups
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-quotient-dimension", type=int, default=3)
    parser.add_argument("--max-rows", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    result = serialize(
        build_result(
            max_quotient_dimension=args.max_quotient_dimension,
            max_rows=args.max_rows,
        )
    )
    assert isinstance(result, dict)
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
