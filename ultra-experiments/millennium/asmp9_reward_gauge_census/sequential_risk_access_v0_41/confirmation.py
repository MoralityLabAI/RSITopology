"""Disjoint rational-channel confirmation fixture for ASMP-9 v0.41."""

from __future__ import annotations

from fractions import Fraction as Q

from sequential_access import (
    DecisionProblem,
    QueryChannel,
    adaptive_upper_generators,
    binary_group_problem,
    classification_problem,
    directed_upper_deficiency,
    nonadaptive_upper_generators,
    qstr,
)


SIGNATURES = {
    "root_q": (0, 0, 1, 1),
    "left_q": (0, 1, 0, 0),
    "right_q": (0, 0, 0, 1),
}
ERROR_RATES = {
    "root_q": Q(1, 5),
    "left_q": Q(1, 4),
    "right_q": Q(1, 3),
}


def noisy_binary_query(
    name: str, signature: tuple[int, ...], error: Q
) -> QueryChannel:
    return QueryChannel(
        name,
        tuple(
            (Q(1) - error, error)
            if outcome == 0
            else (error, Q(1) - error)
            for outcome in signature
        ),
    )


CONFIRMATION_QUERIES = tuple(
    noisy_binary_query(name, SIGNATURES[name], ERROR_RATES[name])
    for name in ("root_q", "left_q", "right_q")
)
CLASSIFICATION = classification_problem(4)
ROOT_GROUP = binary_group_problem(
    "root_group_asymmetric",
    (0, 0, 1, 1),
    false_positive_cost=Q(1, 3),
    false_negative_cost=Q(2, 3),
)
FULL_RISK = ((Q(0), Q(0), Q(0), Q(0)),)


def _cell(
    mode: str,
    problem: DecisionProblem,
    horizon: int,
) -> dict:
    compiler = (
        adaptive_upper_generators
        if mode == "adaptive"
        else nonadaptive_upper_generators
    )
    generators = compiler(CONFIRMATION_QUERIES, problem, horizon)
    certificate = directed_upper_deficiency(generators, FULL_RISK)
    active_weights = [
        {
            "generator_index": index,
            "weight": qstr(weight),
        }
        for index, weight in enumerate(certificate.source_weights)
        if weight
    ]
    return {
        "mode": mode,
        "decision_problem": problem.name,
        "horizon": horizon,
        "upper_generator_count": len(generators),
        "deficiency_to_full": qstr(certificate.epsilon),
        "source_risk": [
            qstr(value) for value in certificate.source_risk
        ],
        "active_source_weights": active_weights,
    }


def run_confirmation() -> dict:
    classification_cells = [
        _cell(mode, CLASSIFICATION, horizon)
        for horizon in (0, 1, 2)
        for mode in ("adaptive", "nonadaptive")
    ]
    group_cells = [
        _cell(mode, ROOT_GROUP, 2)
        for mode in ("adaptive", "nonadaptive")
    ]
    by_key = {
        (
            row["decision_problem"],
            row["horizon"],
            row["mode"],
        ): Q(row["deficiency_to_full"])
        for row in classification_cells + group_cells
    }
    classification_adaptive = by_key[
        (CLASSIFICATION.name, 2, "adaptive")
    ]
    classification_open = by_key[
        (CLASSIFICATION.name, 2, "nonadaptive")
    ]
    group_adaptive = by_key[(ROOT_GROUP.name, 2, "adaptive")]
    group_open = by_key[(ROOT_GROUP.name, 2, "nonadaptive")]
    gates = {
        "B0": (
            by_key[(CLASSIFICATION.name, 0, "adaptive")] == Q(3, 4)
            and by_key[(CLASSIFICATION.name, 1, "adaptive")] == Q(3, 5)
            and classification_adaptive == Q(61, 135)
        ),
        "N0": all(
            by_key[(CLASSIFICATION.name, horizon, "adaptive")]
            == by_key[
                (CLASSIFICATION.name, horizon, "nonadaptive")
            ]
            for horizon in (0, 1)
        ),
        "A0": (
            classification_open == Q(13, 25)
            and classification_adaptive == Q(61, 135)
            and classification_open - classification_adaptive
            == Q(46, 675)
        ),
        "D0": (
            group_adaptive == Q(4, 45)
            and group_open == Q(4, 45)
        ),
        "X0": all(
            len(set(row["source_risk"])) == 1
            for row in classification_cells + group_cells
        ),
    }
    return {
        "query_channels": {
            query.name: {
                "signature": list(SIGNATURES[query.name]),
                "error_rate": qstr(ERROR_RATES[query.name]),
            }
            for query in CONFIRMATION_QUERIES
        },
        "classification_cells": classification_cells,
        "group_cells": group_cells,
        "adaptivity_gap": qstr(
            classification_open - classification_adaptive
        ),
        "gates": gates,
    }
