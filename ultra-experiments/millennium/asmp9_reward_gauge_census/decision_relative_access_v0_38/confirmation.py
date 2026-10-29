"""Prospective ASMP-9 v0.38 confirmation runner.

Do not execute ``run_confirmation`` until the protocol and registration are
committed and pushed. Importing this module or running structural tests does
not evaluate the confirmation grid.
"""

from __future__ import annotations

from fractions import Fraction as Q

from relative_deficiency import (
    ExpandedExperiment,
    FiniteExperiment,
    independent_binary_product,
    independent_binary_product_expanded,
    marginalize_nuisance,
    ordinary_deficiency,
    optimized_value_gap,
    policy_regret_problem,
    relative_deficiency,
)


CONFIRMATION_STRENGTHS = (
    (Q(5, 7), Q(2, 7)),
    (Q(7, 8), Q(1, 8)),
    (Q(5, 8), Q(3, 8)),
)
NUISANCE_ONE_PROBABILITIES = (Q(1, 2), Q(2, 3))
QUERY_NAMES = ("q_target_0", "q_target_1", "q_gauge_shift")
BURNED_STRENGTHS = (
    (Q(2, 3), Q(1, 3)),
    (Q(3, 4), Q(1, 4)),
    (Q(4, 5), Q(1, 5)),
    (Q(3, 5), Q(2, 5)),
)


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def policy_problem():
    occupancies = (
        (Q(1), Q(0), Q(0)),
        (Q(0), Q(1), Q(0)),
        (Q(0), Q(0), Q(1)),
    )
    return policy_regret_problem(
        "three_policy_regret", occupancies, occupancies
    )


def expanded_for_subset(
    high: Q, low: Q, subset: tuple[str, ...]
) -> ExpandedExperiment:
    target_queries = {
        "q_target_0": (high, low, low),
        "q_target_1": (low, high, low),
    }
    queries = []
    for name in subset:
        if name in target_queries:
            queries.append(
                tuple((value, value) for value in target_queries[name])
            )
        elif name == "q_gauge_shift":
            queries.append(((Q(0), Q(1)),) * 3)
        else:
            raise KeyError(name)
    if not queries:
        return ExpandedExperiment(
            (
                ((Q(1),), (Q(1),)),
                ((Q(1),), (Q(1),)),
                ((Q(1),), (Q(1),)),
            )
        )
    return independent_binary_product_expanded(tuple(queries))


def marginal_for_subset(
    high: Q,
    low: Q,
    nuisance_one_probability: Q,
    subset: tuple[str, ...],
) -> FiniteExperiment:
    expanded = expanded_for_subset(high, low, subset)
    nuisance_law = (
        (Q(1) - nuisance_one_probability, nuisance_one_probability),
    ) * 3
    return marginalize_nuisance(expanded, nuisance_law)


def canonical_target_experiment(
    high: Q, low: Q, subset: tuple[str, ...]
) -> FiniteExperiment:
    target_queries = {
        "q_target_0": (high, low, low),
        "q_target_1": (low, high, low),
    }
    retained = tuple(name for name in subset if name in target_queries)
    if not retained:
        return FiniteExperiment(((Q(1),), (Q(1),), (Q(1),)))
    return independent_binary_product(
        tuple(target_queries[name] for name in retained)
    )


def _certificate_row(
    high: Q, low: Q, nuisance_one_probability: Q
) -> dict:
    problem = policy_problem()
    full_subset = QUERY_NAMES
    target_subset = ("q_target_0", "q_target_1")
    full_marginal = marginal_for_subset(
        high, low, nuisance_one_probability, full_subset
    )
    target_marginal = marginal_for_subset(
        high, low, nuisance_one_probability, target_subset
    )
    canonical_full = canonical_target_experiment(
        high, low, target_subset
    )
    q0 = canonical_target_experiment(high, low, ("q_target_0",))
    q1 = canonical_target_experiment(high, low, ("q_target_1",))
    empty = canonical_target_experiment(high, low, ())
    gauge_marginal = marginal_for_subset(
        high, low, nuisance_one_probability, ("q_gauge_shift",)
    )

    q0_relative = relative_deficiency(q0, canonical_full, (problem,))
    q1_relative = relative_deficiency(q1, canonical_full, (problem,))
    empty_relative = relative_deficiency(empty, canonical_full, (problem,))
    gauge_relative = relative_deficiency(
        gauge_marginal, canonical_full, (problem,)
    )
    target_full_relative = relative_deficiency(
        target_marginal, canonical_full, (problem,)
    )
    appended_ancillary = ordinary_deficiency(
        target_marginal, full_marginal
    )
    dropped_ancillary = ordinary_deficiency(
        full_marginal, target_marginal
    )
    expanded_missing_gauge = ordinary_deficiency(
        expanded_for_subset(high, low, target_subset).flatten(),
        expanded_for_subset(high, low, full_subset).flatten(),
    )
    half_gap = (high - low) / 2
    return {
        "high": qstr(high),
        "low": qstr(low),
        "gap": qstr(high - low),
        "half_gap": qstr(half_gap),
        "nuisance_one_probability": qstr(nuisance_one_probability),
        "q0_relative_deficiency": qstr(q0_relative.epsilon),
        "q1_relative_deficiency": qstr(q1_relative.epsilon),
        "empty_relative_deficiency": qstr(empty_relative.epsilon),
        "gauge_relative_deficiency": qstr(gauge_relative.epsilon),
        "target_pair_relative_deficiency": qstr(
            target_full_relative.epsilon
        ),
        "append_ancillary_deficiency": qstr(appended_ancillary.epsilon),
        "drop_ancillary_deficiency": qstr(dropped_ancillary.epsilon),
        "expanded_missing_gauge_deficiency": qstr(
            expanded_missing_gauge.epsilon
        ),
        "q0_value_gap": qstr(
            optimized_value_gap(q0, canonical_full, (problem,))
        ),
        "q1_value_gap": qstr(
            optimized_value_gap(q1, canonical_full, (problem,))
        ),
        "gates": {
            "T0_deletion_formula": (
                q0_relative.epsilon == half_gap
                and q1_relative.epsilon == half_gap
            ),
            "G0_target_gauge_null": (
                target_full_relative.epsilon == 0
                and appended_ancillary.epsilon == 0
                and dropped_ancillary.epsilon == 0
                and gauge_relative.epsilon == empty_relative.epsilon
            ),
            "E0_expanded_separation": (
                expanded_missing_gauge.epsilon == Q(1, 2)
            ),
            "A0_boundary_nonvacuity": (
                empty_relative.epsilon > half_gap
            ),
        },
    }


def run_confirmation() -> dict:
    rows = [
        _certificate_row(high, low, nuisance_probability)
        for high, low in CONFIRMATION_STRENGTHS
        for nuisance_probability in NUISANCE_ONE_PROBABILITIES
    ]
    gate_names = (
        "T0_deletion_formula",
        "G0_target_gauge_null",
        "E0_expanded_separation",
        "A0_boundary_nonvacuity",
    )
    gates = {
        name: all(row["gates"][name] for row in rows)
        for name in gate_names
    }
    return {
        "status": (
            "finite_decision_relative_access_threshold_established"
            if all(gates.values())
            else "registered_gate_failed"
        ),
        "rows": rows,
        "gates": gates,
        "row_count": len(rows),
    }

