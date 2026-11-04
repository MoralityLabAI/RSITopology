"""Burned development fixture for ASMP-9 decision-relative access v0.38."""

from __future__ import annotations

import json
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations

from relative_deficiency import (
    ExpandedExperiment,
    FiniteExperiment,
    independent_binary_product,
    independent_binary_product_expanded,
    ordinary_deficiency,
    optimized_value_gap,
    policy_regret_problem,
    relative_deficiency,
)


TARGET_QUERIES = {
    "q_target_0": (Q(3, 4), Q(1, 4), Q(1, 4)),
    "q_target_1": (Q(1, 4), Q(3, 4), Q(1, 4)),
}
GAUGE_QUERY = "q_gauge_shift"
ALL_QUERIES = tuple(TARGET_QUERIES) + (GAUGE_QUERY,)


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def query_subsets() -> tuple[tuple[str, ...], ...]:
    return tuple(
        subset
        for size in range(len(ALL_QUERIES) + 1)
        for subset in combinations(ALL_QUERIES, size)
    )


def target_experiment(subset: tuple[str, ...]) -> FiniteExperiment:
    retained = tuple(name for name in subset if name in TARGET_QUERIES)
    if not retained:
        return FiniteExperiment(((Q(1),), (Q(1),), (Q(1),)))
    return independent_binary_product(
        tuple(TARGET_QUERIES[name] for name in retained)
    )


def expanded_experiment(subset: tuple[str, ...]) -> ExpandedExperiment:
    queries = []
    for name in subset:
        if name in TARGET_QUERIES:
            row = TARGET_QUERIES[name]
            queries.append(tuple((value, value) for value in row))
        elif name == GAUGE_QUERY:
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


@lru_cache(maxsize=1)
def build_result() -> dict:
    occupancies = (
        (Q(1), Q(0), Q(0)),
        (Q(0), Q(1), Q(0)),
        (Q(0), Q(0), Q(1)),
    )
    reward_representatives = occupancies
    problem = policy_regret_problem(
        "three_policy_regret",
        occupancies,
        reward_representatives,
    )
    full_target = target_experiment(ALL_QUERIES)
    full_expanded = expanded_experiment(ALL_QUERIES)
    rows = []
    for subset in query_subsets():
        target = target_experiment(subset)
        expanded = expanded_experiment(subset)
        relative = relative_deficiency(target, full_target, (problem,))
        expanded_deficiency = ordinary_deficiency(
            expanded.flatten(), full_expanded.flatten()
        )
        rows.append(
            {
                "queries": list(subset),
                "query_count": len(subset),
                "target_observations": target.observation_count,
                "expanded_observations": expanded.observation_count,
                "optimized_value_gap": qstr(
                    optimized_value_gap(target, full_target, (problem,))
                ),
                "target_relative_deficiency": qstr(relative.epsilon),
                "expanded_parameter_deficiency": qstr(
                    expanded_deficiency.epsilon
                ),
                "relative_reference_rule": list(relative.reference_rule),
                "relative_rules_checked": relative.rules_checked,
            }
        )
    return {
        "status": "burned_development_only",
        "raw_reward_representatives": {
            "theta_0": [[1, 0, 0], [2, 1, 1]],
            "theta_1": [[0, 1, 0], [1, 2, 1]],
            "theta_2": [[0, 0, 1], [1, 1, 2]],
        },
        "licensed_gauge": "constant reward shift",
        "policy_regret_losses": [
            [qstr(value) for value in row] for row in problem.losses
        ],
        "nuisance_law": "uniform independent constant-shift representative",
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build_result(), indent=2, sort_keys=True))
