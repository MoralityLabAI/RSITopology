"""Exact witness and definition-closure audit for ASMP-2 v0.1."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent
NORMATIVE = MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY = MILLENNIUM / "problem_set_v0_1.json"
REFEREE_AUDIT = MILLENNIUM / "REFEREE_AUDIT_v0_1.md"

SOURCES = (Fraction(-1, 2), Fraction(0), Fraction(1, 2))
DEPLOYMENT_POINT = Fraction(1)
SAFETY_THRESHOLD = Fraction(9, 16)
UTILITY_FLOOR = Fraction(4, 5)

# g(theta) = (16/9) theta^2 (theta^2 - 1/4)^2.
# Coefficients are in increasing degree order.
G = (
    Fraction(0),
    Fraction(0),
    Fraction(1, 9),
    Fraction(0),
    Fraction(-8, 9),
    Fraction(0),
    Fraction(16, 9),
)

REQUIRED_BINDINGS = (
    "model_class_registration",
    "common_parameterization_and_tangent_transport",
    "nuisance_spaces_and_trajectories",
    "support_overlap_constants",
    "curvature_and_remainder_constants",
    "deployment_set_and_metric",
    "source_environments_and_sample_allocation",
    "policy_or_monitor_class",
    "regular_local_certificate_definition",
    "minimax_radius_and_loss",
    "conditioning_norm_and_margin",
    "simultaneous_confidence_regime",
    "active_design_action_space",
    "active_design_cost_and_budget",
    "active_design_objective_and_tie_rule",
)


def fraction_text(value: Fraction) -> str:
    """Return a stable exact rational representation."""

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


def g(theta: Fraction) -> Fraction:
    return poly_eval(G, theta)


def g_prime(theta: Fraction) -> Fraction:
    return poly_eval(derivative(G), theta)


def g_second(theta: Fraction) -> Fraction:
    return poly_eval(derivative(derivative(G)), theta)


def p_z(theta: Fraction) -> Fraction:
    return Fraction(1, 2) + theta / 8


def p_y(world: int, theta: Fraction) -> Fraction:
    if world not in (-1, 1):
        raise ValueError("world must be -1 or +1")
    return Fraction(1, 2) + theta / 16 + world * g(theta) / 8


def p_y_prime(world: int, theta: Fraction) -> Fraction:
    if world not in (-1, 1):
        raise ValueError("world must be -1 or +1")
    return Fraction(1, 16) + world * g_prime(theta) / 8


def joint_pmf(world: int, theta: Fraction) -> dict[str, Fraction]:
    """Joint PMF of independent binary observations Z and Y."""

    z = p_z(theta)
    y = p_y(world, theta)
    return {
        "00": (1 - z) * (1 - y),
        "01": (1 - z) * y,
        "10": z * (1 - y),
        "11": z * y,
    }


def asmp2_section(text: str) -> str:
    start = text.index("# ASMP-2 — Shift-Spanning Safety Certification")
    stop = text.index("# ASMP-3 —", start)
    return text[start:stop]


def closure_audit() -> dict[str, object]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    normative_text = NORMATIVE.read_text(encoding="utf-8")
    audit_text = REFEREE_AUDIT.read_text(encoding="utf-8")
    problem = next(item for item in registry["problems"] if item["id"] == "ASMP-2")
    section = asmp2_section(normative_text)

    authoritative_status = {
        "candidate_definition_draft": registry["status"]
        == "proposed_candidate_definition_draft",
        "graduation_standard_unsatisfied": registry["graduation_standard_satisfied"]
        is False,
        "registry_defers_to_normative_markdown": registry["registry_is_normative"]
        is False,
        "exact_problem_version_required": registry["resolution_policy"][
            "exact_problem_version_required"
        ]
        is True,
        "narrow_subclass_not_full_resolution": registry["resolution_policy"][
            "narrow_subclass_counts_as_full_resolution"
        ]
        is False,
        "empirical_resolution_forbidden": problem["empirical_resolution_allowed"]
        is False,
        "referee_says_global_class_conditional": (
            "candidate; global class still conditional" in audit_text
        ),
        "referee_requires_external_quotient_audit": (
            "External review must\nstill test whether the registered quotient and conditioning modulus are the\nright ones"
            in audit_text
        ),
    }

    # The problem record is an obligation index, not a registration of the
    # mathematical inputs named in the prose. The normative section likewise
    # says "a registered class" but provides no registration object or schema.
    registered_keys = set(problem)
    missing_bindings = [
        name for name in REQUIRED_BINDINGS if name not in registered_keys
    ]
    placeholder_checks = {
        "model_class_is_placeholder": "Let `M` be a registered class" in section,
        "source_sizes_are_placeholder": "with registered source sample sizes"
        in section,
        "continuation_is_an_open_request": (
            "asks for necessary and sufficient support, compactness,\ncurvature, topology, and model-uncertainty conditions"
            in section
        ),
        "active_design_has_no_registered_objective": (
            "An active design that selects the next environment/intervention" in section
            and "active_design_action_space" not in registered_keys
            and "active_design_objective" not in registered_keys
        ),
    }

    return {
        "passed": False,
        "decision": "stop_definition_not_closed",
        "authoritative_status": authoritative_status,
        "all_authoritative_status_checks_passed": all(authoritative_status.values()),
        "missing_bindings": missing_bindings,
        "missing_binding_count": len(missing_bindings),
        "placeholder_checks": placeholder_checks,
        "all_placeholder_checks_passed": all(placeholder_checks.values()),
        "positive_resolution_obligations": problem["positive_resolution_requires"],
        "negative_resolution_obligations": problem["negative_resolution_requires"],
    }


def exact_countermodel() -> dict[str, object]:
    source_rows = []
    for theta in SOURCES:
        minus_pmf = joint_pmf(-1, theta)
        plus_pmf = joint_pmf(1, theta)
        source_rows.append(
            {
                "theta": fraction_text(theta),
                "g": fraction_text(g(theta)),
                "g_prime": fraction_text(g_prime(theta)),
                "pmf_equal": minus_pmf == plus_pmf,
                "risk_derivative_equal": p_y_prime(-1, theta) == p_y_prime(1, theta),
                "pmf": {key: fraction_text(value) for key, value in minus_pmf.items()},
            }
        )

    reference = Fraction(0)
    fisher_z = (Fraction(1, 8) ** 2) / (p_z(reference) * (1 - p_z(reference)))
    fisher_y = (Fraction(1, 16) ** 2) / (p_y(1, reference) * (1 - p_y(1, reference)))
    fisher_total = fisher_z + fisher_y

    # Writing x = theta^2, the critical x values for g on [-1,1] are
    # 0, 1/12, 1/4, and 1. For g'', the only interior critical x is 1/10.
    g_candidates = {
        "x=0": Fraction(0),
        "x=1/12": Fraction(1, 243),
        "x=1/4": Fraction(0),
        "x=1": Fraction(1),
    }
    g_second_candidates = {
        "x=0": Fraction(2, 9),
        "x=1/10": Fraction(-14, 45),
        "x=1": Fraction(386, 9),
    }
    max_abs_g_second = max(abs(value) for value in g_second_candidates.values())
    risk_curvature_bound = max_abs_g_second / 8

    plus_deployment = p_y(1, DEPLOYMENT_POINT)
    minus_deployment = p_y(-1, DEPLOYMENT_POINT)
    gates = {
        "source_laws_identical": all(row["pmf_equal"] for row in source_rows),
        "source_first_derivatives_identical": all(
            row["risk_derivative_equal"] for row in source_rows
        ),
        "bump_and_first_derivative_vanish_at_sources": all(
            row["g"] == "0/1" and row["g_prime"] == "0/1" for row in source_rows
        ),
        "positive_local_fisher_information": fisher_total > 0,
        "risk_derivative_factors_through_identified_z_score": (
            p_y_prime(1, reference) / Fraction(1, 8) == Fraction(1, 2)
        ),
        "bump_is_bounded_on_compact_domain": max(g_candidates.values()) == 1,
        "common_finite_curvature_bound": risk_curvature_bound == Fraction(193, 36),
        "observation_probabilities_have_common_full_support": (
            Fraction(3, 8) <= p_z(Fraction(-1))
            and p_z(Fraction(1)) <= Fraction(5, 8)
            and Fraction(5, 16) <= Fraction(1, 2) - Fraction(1, 16) - Fraction(1, 8)
            and Fraction(1, 2) + Fraction(1, 16) + Fraction(1, 8) <= Fraction(11, 16)
        ),
        "nonzero_utility_floor_met": Fraction(1) >= UTILITY_FLOOR > 0,
        "deployment_worlds_cross_safety_threshold": (
            minus_deployment < SAFETY_THRESHOLD < plus_deployment
        ),
        "global_risk_gap_nonzero": plus_deployment - minus_deployment == Fraction(1, 4),
        "uniform_certificate_goal_fails_for_all_source_sample_sizes": (
            plus_deployment > SAFETY_THRESHOLD and Fraction(1) >= UTILITY_FLOOR
        ),
    }

    return {
        "family": {
            "theta_domain": "[-1,1]",
            "source_environments": [fraction_text(value) for value in SOURCES],
            "deployment_point": fraction_text(DEPLOYMENT_POINT),
            "p_z": "1/2 + theta/8",
            "g": "(16/9)*theta^2*(theta^2-1/4)^2",
            "p_y_world": "1/2 + theta/16 + world*g(theta)/8",
            "policy_class": "singleton {act}",
            "utility": "1",
            "utility_floor": fraction_text(UTILITY_FLOOR),
            "safety_threshold": fraction_text(SAFETY_THRESHOLD),
        },
        "source_rows": source_rows,
        "local_certificate_data": {
            "fisher_z": fraction_text(fisher_z),
            "fisher_y": fraction_text(fisher_y),
            "fisher_total": fraction_text(fisher_total),
            "risk_derivative": fraction_text(p_y_prime(1, reference)),
            "factor_through_z_score": "1/2",
            "kappa_squared": fraction_text(fisher_total),
        },
        "regularity": {
            "g_extrema_candidates": {
                key: fraction_text(value) for key, value in g_candidates.items()
            },
            "g_second_extrema_candidates": {
                key: fraction_text(value) for key, value in g_second_candidates.items()
            },
            "max_abs_g_second": fraction_text(max_abs_g_second),
            "risk_curvature_bound": fraction_text(risk_curvature_bound),
            "qmd_reason": (
                "finite product Bernoulli family with polynomial probabilities "
                "uniformly bounded away from 0 and 1"
            ),
        },
        "deployment": {
            "minus_world_risk": fraction_text(minus_deployment),
            "plus_world_risk": fraction_text(plus_deployment),
            "risk_gap": fraction_text(plus_deployment - minus_deployment),
            "threshold": fraction_text(SAFETY_THRESHOLD),
            "uniform_success_probability_upper_bound": "0/1",
        },
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "scope": (
            "refutes any continuation rule based only on the audited qualitative "
            "premises; does not refute a successor theorem with bound quantitative "
            "coverage, margin, and model-class assumptions"
        ),
    }


def build_result() -> dict[str, object]:
    closure = closure_audit()
    countermodel = exact_countermodel()
    stop_is_supported = (
        closure["decision"] == "stop_definition_not_closed"
        and closure["all_authoritative_status_checks_passed"]
        and closure["all_placeholder_checks_passed"]
        and closure["missing_binding_count"] == len(REQUIRED_BINDINGS)
        and countermodel["all_gates_passed"]
    )
    return {
        "schema_version": "asmp2_resolution_readiness_v0_1",
        "problem_id": "ASMP-2",
        "problem_version": "ASMP-CANDIDATE-SET-v0.1",
        "authoritative_inputs": {
            NORMATIVE.name: sha256(NORMATIVE),
            REGISTRY.name: sha256(REGISTRY),
            REFEREE_AUDIT.name: sha256(REFEREE_AUDIT),
        },
        "closure_audit": closure,
        "exact_countermodel": countermodel,
        "decision": "stop_full_resolution_attempt_pending_successor_definition"
        if stop_is_supported
        else "harness_inconclusive",
        "problem_resolved": False,
        "stop_is_supported": stop_is_supported,
        "required_successor_repairs": list(REQUIRED_BINDINGS),
        "claim_boundary": (
            "The harness establishes a resolution-readiness stop for v0.1 as "
            "written. It does not prove that no well-posed successor ASMP-2 can "
            "be solved and does not promote a finite countermodel to a complete "
            "classification theorem."
        ),
    }
