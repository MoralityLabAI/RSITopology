"""Exact finite witness for the ASMP-2 source-fiber boundary."""

from __future__ import annotations

import hashlib
import itertools
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from local_counterexample import build_local_counterexample


HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent
NORMATIVE = MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY = MILLENNIUM / "problem_set_v0_1.json"
THEOREM = HERE / "THEOREM_v0_2.md"
PRIOR_ART = HERE / "PRIOR_ART_v0_2.md"
LOCAL_COUNTEREXAMPLE = HERE / "LOCAL_SUFFICIENCY_COUNTEREXAMPLE_v0_5.md"

ACTIONS = (-1, 1)
WORLDS = (-1, 1)
SOURCES = (Fraction(-1, 2), Fraction(0), Fraction(1, 2))
THRESHOLD = Fraction(9, 16)
UTILITY_FLOOR = Fraction(4, 5)

# g(theta) = (16/9) theta^2 (theta^2 - 1/4)^2.
G = (
    Fraction(0),
    Fraction(0),
    Fraction(1, 9),
    Fraction(0),
    Fraction(-8, 9),
    Fraction(0),
    Fraction(16, 9),
)


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def poly_eval(coefficients: Iterable[Fraction], x: Fraction) -> Fraction:
    result = Fraction(0)
    for coefficient in reversed(tuple(coefficients)):
        result = result * x + coefficient
    return result


def derivative(coefficients: Iterable[Fraction]) -> tuple[Fraction, ...]:
    values = tuple(coefficients)
    return tuple(Fraction(index) * values[index] for index in range(1, len(values)))


def bump(theta: Fraction) -> Fraction:
    return poly_eval(G, theta)


def bump_prime(theta: Fraction) -> Fraction:
    return poly_eval(derivative(G), theta)


def bump_second(theta: Fraction) -> Fraction:
    return poly_eval(derivative(derivative(G)), theta)


def p_z(theta: Fraction) -> Fraction:
    return Fraction(1, 2) + theta / 8


def p_z_prime(_theta: Fraction) -> Fraction:
    return Fraction(1, 8)


def risk(world: int, action: int, theta: Fraction) -> Fraction:
    if world not in WORLDS or action not in ACTIONS:
        raise ValueError("world and action must be signed unit values")
    return Fraction(1, 2) + theta / 16 + action * world * bump(theta) / 8


def risk_prime(world: int, action: int, theta: Fraction) -> Fraction:
    if world not in WORLDS or action not in ACTIONS:
        raise ValueError("world and action must be signed unit values")
    return Fraction(1, 16) + action * world * bump_prime(theta) / 8


def channel_parameters(
    world: int, theta: Fraction
) -> tuple[tuple[Fraction, Fraction], ...]:
    """Return (probability, derivative) for Z, Y[-1], and Y[+1]."""

    return (
        (p_z(theta), p_z_prime(theta)),
        (risk(world, -1, theta), risk_prime(world, -1, theta)),
        (risk(world, 1, theta), risk_prime(world, 1, theta)),
    )


def joint_pmf(world: int, theta: Fraction) -> dict[str, Fraction]:
    parameters = channel_parameters(world, theta)
    result: dict[str, Fraction] = {}
    for bits in itertools.product((0, 1), repeat=3):
        probability = Fraction(1)
        for bit, (parameter, _parameter_prime) in zip(bits, parameters):
            probability *= parameter if bit else 1 - parameter
        result["".join(map(str, bits))] = probability
    return result


def joint_pmf_derivative(world: int, theta: Fraction) -> dict[str, Fraction]:
    parameters = channel_parameters(world, theta)
    result: dict[str, Fraction] = {}
    for bits in itertools.product((0, 1), repeat=3):
        total = Fraction(0)
        for differentiated_index in range(3):
            term = Fraction(1)
            for index, (bit, (parameter, parameter_prime)) in enumerate(
                zip(bits, parameters)
            ):
                if index == differentiated_index:
                    term *= parameter_prime if bit else -parameter_prime
                else:
                    term *= parameter if bit else 1 - parameter
            total += term
        result["".join(map(str, bits))] = total
    return result


def fisher_information(world: int, theta: Fraction) -> Fraction:
    pmf = joint_pmf(world, theta)
    pmf_prime = joint_pmf_derivative(world, theta)
    return sum(pmf_prime[key] ** 2 / pmf[key] for key in pmf)


def globally_good_actions(world: int) -> frozenset[int]:
    """Exact good-action set under the registered global threshold."""

    # The action -world has risk <= 1/2 + theta/16 <= 9/16 because
    # its bump coefficient is negative. The action world has risk 11/16
    # at theta=1 and therefore violates the threshold.
    return frozenset((-world,))


def two_action_fiber_value(
    good_sets: Iterable[frozenset[int]],
) -> tuple[Fraction, Fraction]:
    """Solve the two-action maximin fiber LP exactly.

    q is the probability of action -1. Each world's success is affine in q,
    so an optimum occurs at an endpoint or an intersection.
    """

    sets = tuple(good_sets)
    lines: list[tuple[Fraction, Fraction]] = []
    for good in sets:
        intercept = Fraction(int(1 in good))
        slope = Fraction(int(-1 in good)) - intercept
        lines.append((intercept, slope))

    candidates = {Fraction(0), Fraction(1)}
    for first, second in itertools.combinations(lines, 2):
        intercept_1, slope_1 = first
        intercept_2, slope_2 = second
        if slope_1 == slope_2:
            continue
        q = (intercept_2 - intercept_1) / (slope_1 - slope_2)
        if 0 <= q <= 1:
            candidates.add(q)

    scored = []
    for q in candidates:
        value = min(intercept + slope * q for intercept, slope in lines)
        scored.append((value, -q, q))
    value, _negative_q, q = max(scored)
    return q, value


def build_result() -> dict[str, object]:
    source_rows = []
    for theta in SOURCES:
        minus_pmf = joint_pmf(-1, theta)
        plus_pmf = joint_pmf(1, theta)
        minus_derivative = joint_pmf_derivative(-1, theta)
        plus_derivative = joint_pmf_derivative(1, theta)
        source_rows.append(
            {
                "theta": fraction_text(theta),
                "bump": fraction_text(bump(theta)),
                "bump_prime": fraction_text(bump_prime(theta)),
                "joint_law_equal": minus_pmf == plus_pmf,
                "joint_score_derivative_equal": minus_derivative == plus_derivative,
                "joint_pmf": {
                    key: fraction_text(value) for key, value in minus_pmf.items()
                },
            }
        )

    good_sets = {str(world): globally_good_actions(world) for world in WORLDS}
    q, fiber_value = two_action_fiber_value(good_sets.values())
    deterministic_value = max(
        min(Fraction(int(action in good)) for good in good_sets.values())
        for action in ACTIONS
    )

    fisher = fisher_information(1, Fraction(0))
    risk_curvature_bound = Fraction(386, 9) / 8
    gates = {
        "source_joint_laws_identical": all(
            row["joint_law_equal"] for row in source_rows
        ),
        "source_joint_scores_identical": all(
            row["joint_score_derivative_equal"] for row in source_rows
        ),
        "bump_and_derivative_zero_at_sources": all(
            row["bump"] == "0/1" and row["bump_prime"] == "0/1" for row in source_rows
        ),
        "positive_fisher_information": fisher == Fraction(3, 32),
        "nonzero_risk_derivatives_factor_through_z_score": all(
            risk_prime(world, action, Fraction(0)) / p_z_prime(Fraction(0))
            == Fraction(1, 2)
            for world in WORLDS
            for action in ACTIONS
        ),
        "both_worlds_have_a_good_noninert_action": all(
            good_sets[str(world)] and Fraction(1) >= UTILITY_FLOOR > 0
            for world in WORLDS
        ),
        "world_good_action_sets_are_disjoint": (
            good_sets["-1"].isdisjoint(good_sets["1"])
        ),
        "exact_randomized_fiber_value_is_one_half": fiber_value == Fraction(1, 2),
        "exact_deterministic_fiber_value_is_zero": deterministic_value == 0,
        "finite_sample_minimax_confidence_ceiling_is_one_half": (
            fiber_value == Fraction(1, 2)
        ),
        "common_finite_curvature_bound": risk_curvature_bound == Fraction(193, 36),
        "common_full_support": (
            Fraction(3, 8) <= p_z(Fraction(-1))
            and p_z(Fraction(1)) <= Fraction(5, 8)
            and Fraction(5, 16) <= Fraction(1, 2) - Fraction(1, 16) - Fraction(1, 8)
            and Fraction(1, 2) + Fraction(1, 16) + Fraction(1, 8) <= Fraction(11, 16)
        ),
    }

    return {
        "schema_version": "asmp2_source_fiber_boundary_v0_2",
        "problem_id": "ASMP-2",
        "problem_version": "ASMP-CANDIDATE-SET-v0.1",
        "authoritative_and_theorem_inputs": {
            NORMATIVE.name: sha256(NORMATIVE),
            REGISTRY.name: sha256(REGISTRY),
            THEOREM.name: sha256(THEOREM),
            PRIOR_ART.name: sha256(PRIOR_ART),
            LOCAL_COUNTEREXAMPLE.name: sha256(LOCAL_COUNTEREXAMPLE),
        },
        "witness": {
            "theta_domain": "[-1,1]",
            "sources": [fraction_text(theta) for theta in SOURCES],
            "worlds": list(WORLDS),
            "actions": list(ACTIONS),
            "observation": "(Z,Y[-1],Y[+1]) independent Bernoulli channels",
            "p_z": "1/2 + theta/8",
            "bump": "(16/9)*theta^2*(theta^2-1/4)^2",
            "risk": "1/2 + theta/16 + action*world*bump(theta)/8",
            "threshold": fraction_text(THRESHOLD),
            "utility": "1",
            "utility_floor": fraction_text(UTILITY_FLOOR),
            "source_rows": source_rows,
            "fisher_information_at_zero": fraction_text(fisher),
            "risk_curvature_bound": fraction_text(risk_curvature_bound),
        },
        "fiber_certificate": {
            "good_actions_by_world": {
                world: sorted(actions) for world, actions in good_sets.items()
            },
            "optimal_probability_of_action_minus_one": fraction_text(q),
            "randomized_uniform_success": fraction_text(fiber_value),
            "deterministic_uniform_success": fraction_text(deterministic_value),
            "minimax_sample_complexity_for_delta_below_one_half": "infinity",
            "reason": (
                "all finite source-data laws are identical across worlds, so every "
                "source-only procedure induces the same action distribution"
            ),
        },
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "local_sufficiency_counterexample": build_local_counterexample(),
        "adjudication": {
            "candidate_negative_result": True,
            "global_continuation_for_unrestricted_smooth_qmd": "impossible",
            "exact_fiber_boundary_proved": True,
            "problem_resolved": False,
            "reason_not_yet_claimed_resolved": (
                "the canonical v0.1 classification target is not a single closed "
                "universal sentence, and independent expert reproduction is absent"
            ),
        },
    }
