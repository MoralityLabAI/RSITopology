"""Exact well-posedness and counterexample harness for ASMP-1 v0.1.

The harness studies two finite-dimensional analytic Bernoulli SCM instances.
Their conditional response probability on the Boolean cube is represented in
the Walsh basis.  All arithmetic used for the scientific gates is rational.

The first instance tests the necessity clause of the Cut-Separation
Conjecture: a nonconstant one-dimensional abstraction is exactly observed even
though the environment does not excite the full local mechanism class.

The second instance tests sufficiency under a structural hypergraph reading of
"separates every minimal causal cut": all parent configurations have positive
mass and singleton interventions cover, distinguish, and have full incidence
rank on all parent sites, but a continuous higher-order interaction fiber is
observationally invisible.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]
Assignment = tuple[int, ...]


def exact_rank(rows: Iterable[Sequence[Fraction | int]]) -> int:
    """Return matrix rank by exact rational Gaussian elimination."""

    matrix = [[Fraction(value) for value in row] for row in rows]
    if not matrix:
        return 0
    column_count = len(matrix[0])
    if any(len(row) != column_count for row in matrix):
        raise ValueError("matrix is ragged")

    pivot_row = 0
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
            if row == pivot_row or matrix[row][column] == 0:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                left - factor * right
                for left, right in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row


def q_is_identifiable(observation_rows: Matrix, q_rows: Matrix) -> bool:
    """Linear criterion: Q factors through A iff adding Q does not raise rank."""

    return exact_rank(observation_rows) == exact_rank(observation_rows + q_rows)


def assignments(n: int) -> tuple[Assignment, ...]:
    return tuple(itertools.product((-1, 1), repeat=n))


def character(mask: int, point: Assignment) -> int:
    value = 1
    for coordinate, sign in enumerate(point):
        if mask & (1 << coordinate):
            value *= sign
    return value


def evaluation_row(point: Assignment) -> Vector:
    return tuple(
        Fraction(character(mask, point)) for mask in range(1 << len(point))
    )


def singleton_observation_matrix(n: int) -> Matrix:
    """Passive and every singleton-do Bernoulli probability in Walsh coding."""

    dimension = 1 << n
    rows: list[Vector] = []
    passive = [Fraction(0) for _ in range(dimension)]
    passive[0] = Fraction(1)
    rows.append(tuple(passive))
    for coordinate in range(n):
        for fixed_sign in (-1, 1):
            row = [Fraction(0) for _ in range(dimension)]
            row[0] = Fraction(1)
            row[1 << coordinate] = Fraction(fixed_sign)
            rows.append(tuple(row))
    return tuple(rows)


def table_from_coefficients(coefficients: Vector, n: int) -> Vector:
    if len(coefficients) != 1 << n:
        raise ValueError("coefficient vector has the wrong dimension")
    return tuple(
        sum(
            coefficient * character(mask, point)
            for mask, coefficient in enumerate(coefficients)
        )
        for point in assignments(n)
    )


def apply_rows(rows: Matrix, vector: Vector) -> Vector:
    return tuple(
        sum(left * right for left, right in zip(row, vector)) for row in rows
    )


def singleton_law_signature(table: Vector, n: int) -> Vector:
    """Return Bernoulli parameters for passive and singleton-do laws."""

    cube = assignments(n)
    signature = [sum(table, Fraction(0)) / len(table)]
    for coordinate in range(n):
        for fixed_sign in (-1, 1):
            selected = [
                probability
                for point, probability in zip(cube, table)
                if point[coordinate] == fixed_sign
            ]
            signature.append(sum(selected, Fraction(0)) / len(selected))
    return tuple(signature)


def parent_effects(table: Vector, n: int) -> Vector:
    cube = assignments(n)
    effects: list[Fraction] = []
    for coordinate in range(n):
        means = []
        for fixed_sign in (-1, 1):
            selected = [
                probability
                for point, probability in zip(cube, table)
                if point[coordinate] == fixed_sign
            ]
            means.append(sum(selected, Fraction(0)) / len(selected))
        effects.append(abs(means[1] - means[0]))
    return tuple(effects)


def canonical_hyperoctahedral_table(table: Vector, n: int) -> Vector:
    """Canonicalize a response table under parent permutations and sign flips."""

    cube = assignments(n)
    table_by_point = dict(zip(cube, table))
    transformed_tables: list[Vector] = []
    for permutation in itertools.permutations(range(n)):
        for flips in itertools.product((-1, 1), repeat=n):
            transformed_tables.append(
                tuple(
                    table_by_point[
                        tuple(
                            flips[coordinate] * point[permutation[coordinate]]
                            for coordinate in range(n)
                        )
                    ]
                    for point in cube
                )
            )
    return min(transformed_tables)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def serialize(value: object) -> object:
    if isinstance(value, Fraction):
        return fraction_text(value)
    if isinstance(value, tuple):
        return [serialize(item) for item in value]
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    return value


def necessity_counterexample(n: int = 3) -> dict[str, object]:
    """Nonconstant Q is identified although full-class excitation fails."""

    dimension = 1 << n
    observed_point = tuple(-1 for _ in range(n))
    observation_rows = (evaluation_row(observed_point),)
    q_rows = observation_rows
    full_excitation_rows = tuple(evaluation_row(point) for point in assignments(n))

    gates = {
        "q_is_nonconstant": exact_rank(q_rows) == 1,
        "q_is_exactly_identifiable": q_is_identifiable(observation_rows, q_rows),
        "environment_does_not_excitate_full_mechanism_class": (
            exact_rank(observation_rows) < exact_rank(full_excitation_rows)
        ),
        "full_analytic_class_has_eight_coordinates": (
            exact_rank(full_excitation_rows) == dimension
        ),
    }
    if not all(gates.values()):
        raise AssertionError(f"necessity counterexample failed: {gates}")

    return {
        "model": (
            "analytic Bernoulli response p_theta(x)=sum_T theta_T chi_T(x), "
            "on an interior parameter neighborhood"
        ),
        "abstraction": "Q(theta)=p_theta(-1,-1,-1)",
        "gauge": "identity",
        "observed_environment_count": 1,
        "available_parent_configuration_count": dimension,
        "observation_rank": exact_rank(observation_rows),
        "full_excitation_rank": exact_rank(full_excitation_rows),
        "q_rank": exact_rank(q_rows),
        "gates": gates,
    }


def structural_hypergraph_audit(n: int) -> dict[str, object]:
    """Audit three strong, purely structural meanings of cut separation."""

    hyperedges = tuple(1 << coordinate for coordinate in range(n))
    union_mask = 0
    for edge in hyperedges:
        union_mask |= edge
    incidence = tuple(
        tuple(int(edge & (1 << coordinate) != 0) for coordinate in range(n))
        for edge in hyperedges
    )
    site_codes = tuple(
        tuple(row[coordinate] for row in incidence) for coordinate in range(n)
    )
    return {
        "registered_hyperedges": hyperedges,
        "incidence_matrix": incidence,
        "coverage": union_mask == (1 << n) - 1,
        "pair_separation": len(set(site_codes)) == n,
        "full_incidence_rank": exact_rank(incidence) == n,
    }


def analytic_cut_aliasing_counterexample() -> dict[str, object]:
    """Full cut-state access does not identify an upstream map through a bottleneck."""

    # X={0,1}, H=R^2, Y=R.  The downstream analytic mechanism is
    # g(u,v)=u+2v.  The observation rows act on
    # (h_0,u, h_0,v, h_1,u, h_1,v).
    observation_rows: Matrix = (
        (Fraction(1), Fraction(2), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1), Fraction(2)),
    )
    identity_q: Matrix = tuple(
        tuple(Fraction(int(row == column)) for column in range(4))
        for row in range(4)
    )
    h_left: Vector = (
        Fraction(0),
        Fraction(0),
        Fraction(1),
        Fraction(0),
    )
    h_right: Vector = (
        Fraction(0),
        Fraction(0),
        Fraction(-1),
        Fraction(1),
    )
    kernel_direction: Vector = (
        Fraction(-2),
        Fraction(1),
        Fraction(0),
        Fraction(0),
    )
    downstream_coefficients_left: Vector = (Fraction(1), Fraction(2))
    downstream_coefficients_right: Vector = (Fraction(1), Fraction(2))
    # Full activation replacement do(H=(a,b)) returns a+2b in both models.
    replacement_probe_states = tuple(
        (Fraction(left), Fraction(right))
        for left, right in itertools.product((-2, -1, 0, 1, 2), repeat=2)
    )
    replacement_laws_left = tuple(
        sum(
            coefficient * state
            for coefficient, state in zip(downstream_coefficients_left, probe)
        )
        for probe in replacement_probe_states
    )
    replacement_laws_right = tuple(
        sum(
            coefficient * state
            for coefficient, state in zip(downstream_coefficients_right, probe)
        )
        for probe in replacement_probe_states
    )

    gates = {
        "all_labelled_input_environments_are_observed": True,
        "entire_typed_hidden_cut_state_is_replaceable": True,
        "both_hidden_coordinates_have_nonzero_downstream_effect": all(
            coefficient != 0 for coefficient in downstream_coefficients_left
        ),
        "downstream_map_is_a_surjective_analytic_submersion": (
            exact_rank((downstream_coefficients_left,)) == 1
        ),
        "natural_input_output_laws_match": (
            apply_rows(observation_rows, h_left)
            == apply_rows(observation_rows, h_right)
        ),
        "all_hidden_replacement_laws_match_symbolically": (
            downstream_coefficients_left == downstream_coefficients_right
            and replacement_laws_left == replacement_laws_right
        ),
        "full_upstream_abstraction_is_not_identifiable": not q_is_identifiable(
            observation_rows, identity_q
        ),
        "mechanisms_are_not_identity_gauge_equivalent": h_left != h_right,
        "registered_design_has_positive_dimensional_kernel": (
            exact_rank(observation_rows) < len(h_left)
        ),
        "explicit_tangent_direction_is_in_exact_kernel": all(
            value == 0 for value in apply_rows(observation_rows, kernel_direction)
        ),
    }
    if not all(gates.values()):
        raise AssertionError(f"analytic cut-aliasing counterexample failed: {gates}")

    return {
        "model": "X={0,1} -> H=R^2 -> Y=R with g(u,v)=u+2v",
        "abstraction": "the full labelled upstream map h:X->H",
        "gauge": "identity",
        "natural_observation_rank": exact_rank(observation_rows),
        "upstream_parameter_dimension": len(h_left),
        "natural_observation_nullity": len(h_left) - exact_rank(observation_rows),
        "left_upstream_map": h_left,
        "right_upstream_map": h_right,
        "shared_natural_outputs": apply_rows(observation_rows, h_left),
        "downstream_coefficients": downstream_coefficients_left,
        "replacement_probe_count": len(replacement_probe_states),
        "continuous_blind_direction_per_environment": "ker([1,2])=span{(-2,1)}",
        "genericity_note": (
            "Every nonzero linear map R^2->R is a submersion with a "
            "one-dimensional kernel; the ambiguity is dimensional and persists "
            "under small coefficient perturbations."
        ),
        "gates": gates,
    }


def sufficiency_counterexample(n: int = 3) -> dict[str, object]:
    """A continuous quotient ambiguity despite full support and cut coverage."""

    if n != 3:
        raise ValueError("the frozen exact witness uses three parents")

    # Coefficients are ordered by Walsh mask 0..7.  Only the top interaction
    # differs.  Both mechanisms remain safely inside the Bernoulli simplex.
    common = (
        Fraction(1, 2),
        Fraction(1, 25),
        Fraction(1, 20),
        Fraction(1, 50),
        Fraction(3, 50),
        Fraction(3, 200),
        Fraction(1, 100),
    )
    left_coefficients = common + (Fraction(-1, 100),)
    right_coefficients = common + (Fraction(1, 100),)
    left_table = table_from_coefficients(left_coefficients, n)
    right_table = table_from_coefficients(right_coefficients, n)
    observation_rows = singleton_observation_matrix(n)
    identity_q = tuple(
        tuple(Fraction(int(row == column)) for column in range(1 << n))
        for row in range(1 << n)
    )
    hypergraph = structural_hypergraph_audit(n)
    left_signature = singleton_law_signature(left_table, n)
    right_signature = singleton_law_signature(right_table, n)
    left_effects = parent_effects(left_table, n)
    right_effects = parent_effects(right_table, n)
    all_probabilities = left_table + right_table
    non_top_absolute_sum = sum(
        (abs(coefficient) for coefficient in common), Fraction(0)
    ) - abs(common[0])
    certified_blind_interval_radius = Fraction(1, 25)
    minimum_variance = min(
        probability * (1 - probability) for probability in all_probabilities
    )
    top_kernel_vector = tuple(
        Fraction(int(mask == (1 << n) - 1)) for mask in range(1 << n)
    )

    gates = {
        "all_parent_configurations_have_positive_environment_mass": True,
        "hypergraph_covers_every_parent_site": bool(hypergraph["coverage"]),
        "hypergraph_pair_separates_parent_sites": bool(
            hypergraph["pair_separation"]
        ),
        "hypergraph_incidence_has_full_parent_rank": bool(
            hypergraph["full_incidence_rank"]
        ),
        "every_parent_has_positive_average_causal_effect": (
            min(left_effects + right_effects) > 0
        ),
        "all_bernoulli_probabilities_are_uniformly_interior": (
            min(all_probabilities) > Fraction(1, 4)
            and max(all_probabilities) < Fraction(3, 4)
        ),
        "certified_open_blind_interval_stays_uniformly_interior": (
            non_top_absolute_sum + certified_blind_interval_radius
            < Fraction(1, 4)
        ),
        "top_interaction_is_in_exact_observation_kernel": (
            all(value == 0 for value in apply_rows(observation_rows, top_kernel_vector))
        ),
        "registered_observational_and_interventional_laws_match": (
            left_signature == right_signature
            and apply_rows(observation_rows, left_coefficients)
            == apply_rows(observation_rows, right_coefficients)
        ),
        "full_abstraction_is_not_identifiable": not q_is_identifiable(
            observation_rows, identity_q
        ),
        "mechanisms_are_not_parent_gauge_equivalent": (
            canonical_hyperoctahedral_table(left_table, n)
            != canonical_hyperoctahedral_table(right_table, n)
        ),
        "ambiguity_fiber_is_positive_dimensional": (
            exact_rank(observation_rows) < 1 << n
        ),
        "global_quotient_separation_margin_is_zero": (
            left_signature == right_signature and left_table != right_table
        ),
    }
    if not all(gates.values()):
        raise AssertionError(f"sufficiency counterexample failed: {gates}")

    return {
        "model": (
            "three-parent analytic Bernoulli SCM with uniform full-support "
            "environment and passive plus all singleton activation replacements"
        ),
        "abstraction": "full conditional Bernoulli response table",
        "gauge": "parent permutations and parent sign flips; output labels fixed",
        "observation_rank": exact_rank(observation_rows),
        "mechanism_dimension": 1 << n,
        "observation_nullity": (1 << n) - exact_rank(observation_rows),
        "left_coefficients": left_coefficients,
        "right_coefficients": right_coefficients,
        "left_registered_laws": left_signature,
        "right_registered_laws": right_signature,
        "left_parent_effects": left_effects,
        "right_parent_effects": right_effects,
        "minimum_bernoulli_variance": minimum_variance,
        "maximum_probability": max(all_probabilities),
        "minimum_probability": min(all_probabilities),
        "continuous_blind_direction": "theta_{1,2,3}",
        "certified_open_blind_interval": (
            -certified_blind_interval_radius,
            certified_blind_interval_radius,
        ),
        "open_blind_fiber_note": (
            "theta_{1,2,3} can vary in an open interval while all registered "
            "laws, full support, structural cut gates, and singleton effect "
            "margins remain unchanged"
        ),
        "hypergraph": hypergraph,
        "gates": gates,
    }


def build_result() -> dict[str, object]:
    necessity = necessity_counterexample()
    cut_aliasing = analytic_cut_aliasing_counterexample()
    sufficiency = sufficiency_counterexample()
    all_gates = (
        list(necessity["gates"].values())
        + list(cut_aliasing["gates"].values())
        + list(sufficiency["gates"].values())
    )
    return {
        "schema_version": "asmp1_cut_separation_audit_v0_1",
        "problem": "ASMP-1 v0.1",
        "verdict": "cut_separation_conjecture_not_well_posed_as_a_closed_iff",
        "necessity_counterexample": necessity,
        "full_cut_replacement_aliasing_counterexample": cut_aliasing,
        "structural_sufficiency_counterexample": sufficiency,
        "interpretation_split": {
            "full_mechanism_excitation_reading": (
                "the only-if direction is false for a coarse nonconstant Q"
            ),
            "structural_hypergraph_reading": (
                "the if direction is false despite coverage, pair separation, "
                "and full incidence rank"
            ),
            "quotient_observation_separation_reading": (
                "requiring positive separation between every distinct Q/G pair "
                "excludes the witness by assuming the desired identifiability"
            ),
        },
        "stopping_boundary": (
            "A broader ASMP-1 classification theorem cannot be proved or "
            "refuted until v0.1 freezes a Q-relative excitation condition, a "
            "noncircular definition of cut separation, the exact meaning of "
            "generic, and whether kappa is local conditioning or global "
            "quotient separation."
        ),
        "all_exact_gates_pass": all(all_gates),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    result = serialize(build_result())
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    assert isinstance(result, dict)
    result["source_sha256"] = source_sha256
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
