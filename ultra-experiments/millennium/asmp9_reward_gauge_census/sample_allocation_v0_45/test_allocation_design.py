from __future__ import annotations

from fractions import Fraction as Q
from pathlib import Path
import sys

import pytest


HERE = Path(__file__).resolve().parent
V41 = HERE.parent / "sequential_risk_access_v0_41"
for path in (HERE, V41):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from allocation_design import (  # noqa: E402
    asymptotic_continuous_lower,
    enumerate_policy_occupancies,
    exact_upper_for_allocation,
    evaluate_allocation,
    information_for_allocation,
    method_of_types_kl_upper,
    optimize_constructive_upper,
    optimize_serial_control,
    positive_allocations,
    registered_constructive_upper,
    symmetric_binomial_bayes_error,
    two_point_radius_lower,
)
from sequential_access import (  # noqa: E402
    ADAPTIVITY_GAP_QUERIES,
    adaptive_upper_generators,
    binary_group_problem,
    classification_problem,
    directed_upper_deficiency,
)


QUERY_NAMES = tuple(query.name for query in ADAPTIVITY_GAP_QUERIES)


def setup_problem(problem):
    envelopes = enumerate_policy_occupancies(
        ADAPTIVITY_GAP_QUERIES, problem, 2
    )
    reference = (tuple([Q(0)] * problem.target_count),)
    return envelopes, reference


@pytest.mark.parametrize(
    "problem",
    (
        classification_problem(4),
        binary_group_problem(
            "root_group", (0, 0, 1, 1), false_positive_cost=Q(1)
        ),
    ),
)
def test_occupancy_risks_match_existing_compiler(problem):
    envelopes, _ = setup_problem(problem)
    envelope_risks = tuple(
        sorted({envelope.risk for envelope in envelopes})
    )
    compiler = adaptive_upper_generators(
        ADAPTIVITY_GAP_QUERIES, problem, 2
    )
    assert directed_upper_deficiency(
        envelope_risks, compiler
    ).epsilon == 0
    assert directed_upper_deficiency(
        compiler, envelope_risks
    ).epsilon == 0


def test_method_of_types_bound_is_outward_and_decreasing():
    values = [
        method_of_types_kl_upper(n, 3, "0.05")
        for n in range(1, 25)
    ]
    assert all(left > right for left, right in zip(values, values[1:]))
    assert all(value > 0 for value in values)


def test_positive_allocation_universe_is_exact():
    rows = positive_allocations(54, 3)
    assert len(rows) == 1378
    assert len(set(rows)) == len(rows)
    assert all(sum(row) == 54 and min(row) >= 1 for row in rows)


def test_information_matches_registered_branch_policy():
    problem = classification_problem(4)
    envelopes, _ = setup_problem(problem)
    policy = next(
        row
        for row in envelopes
        if row.code == "root(left(A0,A1),right(A2,A3))"
    )
    information = information_for_allocation(
        policy, (8, 8, 8), 3
    )
    kappa = method_of_types_kl_upper(8, 3, "0.05")
    assert information == tuple([2 * kappa] * 4)


def test_classification_allocation_strictly_beats_uniform():
    result = optimize_constructive_upper(
        54, "branch_classification"
    )
    assert result["evaluated_allocations"] == 1378
    assert result["strict_improvement"]
    assert result["optimum"] == (22, 16, 16)


def test_root_group_allocation_strictly_prioritizes_root():
    result = optimize_constructive_upper(
        54, "root_group"
    )
    assert result["evaluated_allocations"] == 1378
    assert result["strict_improvement"]
    assert result["optimum"] == (52, 1, 1)


def test_serial_control_recovers_uniform_allocation():
    result = optimize_serial_control(54, 3)
    assert result["evaluated_allocations"] == 1378
    assert result["uniform"] == (18, 18, 18)
    assert result["uniform_is_optimal"]
    assert result["optima"] == ((18, 18, 18),)


@pytest.mark.parametrize(
    "problem,mode,allocations",
    (
        (
            classification_problem(4),
            "branch_classification",
            ((18, 18, 18), (22, 16, 16), (30, 12, 12)),
        ),
        (
            binary_group_problem(
                "root_group",
                (0, 0, 1, 1),
                false_positive_cost=Q(1),
            ),
            "root_group",
            ((18, 18, 18), (52, 1, 1), (30, 12, 12)),
        ),
    ),
)
def test_closed_form_matches_exact_deficiency_lp(
    problem, mode, allocations
):
    envelopes, reference = setup_problem(problem)
    for allocation in allocations:
        assert exact_upper_for_allocation(
            envelopes, problem, allocation, 3, reference
        ) == registered_constructive_upper(allocation, mode)


def test_continuous_lower_benchmarks_are_valid():
    classification = asymptotic_continuous_lower(
        24, 3, "0.05", "branch_classification"
    )
    group = asymptotic_continuous_lower(
        24, 3, "0.05", "root_group"
    )
    for problem, lower in (
        (classification_problem(4), classification),
        (
            binary_group_problem(
                "root_group",
                (0, 0, 1, 1),
                false_positive_cost=Q(1),
            ),
            group,
        ),
    ):
        mode = (
            "branch_classification"
            if problem.name == "4_class_identification"
            else "root_group"
        )
        result = optimize_constructive_upper(24, mode)
        assert lower <= float(result["best_upper"])


@pytest.mark.parametrize(
    "samples,expected",
    (
        (17, Q(37, 200)),
        (20, Q(7, 40)),
        (26, Q(31, 200)),
        (58, Q(21, 200)),
    ),
)
def test_two_point_radius_lower_is_exact_on_registered_grid(
    samples, expected
):
    result = two_point_radius_lower(samples)
    assert result["radius_lower"] == expected
    assert result["bayes_error"] > Q(1, 20)
    assert result["next_grid_error"] <= Q(1, 20)


def test_symmetric_binomial_error_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        symmetric_binomial_bayes_error(0, Q(1, 4))


def test_evaluate_allocation_fails_on_missing_cell():
    problem = classification_problem(4)
    envelopes, reference = setup_problem(problem)
    with pytest.raises(ValueError):
        evaluate_allocation(
            envelopes, problem, (12, 12), 3, reference
        )


@pytest.mark.parametrize(
    "call,args",
    (
        (positive_allocations, (2, 3)),
        (method_of_types_kl_upper, (0, 3, "0.05")),
        (
            asymptotic_continuous_lower,
            (24, 3, "0.05", "unknown"),
        ),
        (
            registered_constructive_upper,
            ((18, 18, 18), "unknown"),
        ),
    ),
)
def test_invalid_inputs_fail_closed(call, args):
    with pytest.raises(ValueError):
        call(*args)
