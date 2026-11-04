"""Exact counterexample to factorization-only local safety sufficiency."""

from __future__ import annotations

from fractions import Fraction


ACTIONS = (-1, 1)
RADIUS = Fraction(1, 2)
THRESHOLD = Fraction(1, 2)
UTILITY_FLOOR = Fraction(4, 5)


def observation_probability(theta: Fraction) -> Fraction:
    return Fraction(1, 2) + theta / 4


def risk(action: int, theta: Fraction) -> Fraction:
    if action not in ACTIONS:
        raise ValueError("action must be -1 or +1")
    return Fraction(1, 2) + action * theta / 4


def build_local_counterexample() -> dict[str, object]:
    fisher = (Fraction(1, 4) ** 2) / (Fraction(1, 2) * Fraction(1, 2))
    rows = {}
    for action in ACTIONS:
        endpoint_risks = (
            risk(action, -RADIUS),
            risk(action, RADIUS),
        )
        rows[str(action)] = {
            "risk_derivative": f"{action}/4",
            "score_derivative": "1/4",
            "factor_through_score": str(action),
            "minimum_risk": (
                f"{min(endpoint_risks).numerator}/{min(endpoint_risks).denominator}"
            ),
            "maximum_risk": (
                f"{max(endpoint_risks).numerator}/{max(endpoint_risks).denominator}"
            ),
            "globally_safe_on_local_ball": max(endpoint_risks) <= THRESHOLD,
            "utility": "1/1",
        }
    gates = {
        "dominated_qmd_full_support": (
            observation_probability(-RADIUS) == Fraction(3, 8)
            and observation_probability(RADIUS) == Fraction(5, 8)
        ),
        "positive_fisher_information": fisher == Fraction(1, 4),
        "both_risk_derivatives_factor_continuously": all(
            Fraction(action, 4) / Fraction(1, 4) == action for action in ACTIONS
        ),
        "strict_conditioning_margin": fisher > 0,
        "utility_floor_met_by_every_action": Fraction(1) >= UTILITY_FLOOR,
        "no_registered_action_is_uniformly_safe": all(
            not rows[str(action)]["globally_safe_on_local_ball"] for action in ACTIONS
        ),
    }
    return {
        "schema_version": "asmp2_local_factorization_counterexample_v0_5",
        "theta_adv": "[-1/2,1/2]",
        "source_reference": "0",
        "observation": "Bernoulli(1/2+theta/4)",
        "actions": list(ACTIONS),
        "policy_randomization": "not_registered",
        "risk": "1/2+action*theta/4",
        "safety_threshold": "1/2",
        "utility": "1",
        "utility_floor": "4/5",
        "fisher_information": "1/4",
        "action_rows": rows,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "conclusion": (
            "pathwise factorization and positive conditioning are not sufficient "
            "for the stated safety certificate without robust feasibility/margin"
        ),
    }
