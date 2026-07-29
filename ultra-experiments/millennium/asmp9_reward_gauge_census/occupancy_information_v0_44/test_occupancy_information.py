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

from occupancy_information import (  # noqa: E402
    enumerate_policy_envelopes,
    information_radii,
    multinomial_chi_square,
    policy_specific_interval,
    query_chi_square_costs,
    robust_directed_deficiency_interval,
    sqrt_fraction_upper,
    uniform_information_interval,
)
from sequential_access import (  # noqa: E402
    ADAPTIVITY_GAP_QUERIES,
    QueryChannel,
    adaptive_upper_generators,
    binary_group_problem,
    classification_problem,
    directed_upper_deficiency,
)


def perturbed_queries(eta: Q) -> tuple[QueryChannel, ...]:
    rows = []
    for query in ADAPTIVITY_GAP_QUERIES:
        if query.name == "root":
            rows.append(query)
            continue
        rows.append(
            QueryChannel(
                query.name,
                tuple(
                    (
                        (Q(1) - eta, eta)
                        if row[0] == 1
                        else (eta, Q(1) - eta)
                    )
                    for row in query.rows
                ),
            )
        )
    return tuple(rows)


def fixtures(eta: Q, problem):
    center = ADAPTIVITY_GAP_QUERIES
    actual = perturbed_queries(eta)
    costs = query_chi_square_costs(center, actual)
    envelopes = enumerate_policy_envelopes(
        center, problem, 2, costs
    )
    reference = (tuple([Q(0)] * problem.target_count),)
    return center, actual, costs, envelopes, reference


@pytest.mark.parametrize(
    "problem",
    (
        classification_problem(4),
        binary_group_problem(
            "root_group", (0, 0, 1, 1), false_positive_cost=Q(1)
        ),
    ),
)
def test_envelope_risks_match_existing_compiler(problem):
    center, _, costs, envelopes, _ = fixtures(Q(1, 20), problem)
    compiler = set(
        adaptive_upper_generators(center, problem, 2)
    )
    envelope_risks = {envelope.risk for envelope in envelopes}
    assert compiler.issubset(envelope_risks)
    assert directed_upper_deficiency(
        tuple(envelope_risks), tuple(compiler)
    ).epsilon == 0
    assert directed_upper_deficiency(
        tuple(compiler), tuple(envelope_risks)
    ).epsilon == 0
    assert costs[(0, "root")] == 0
    assert costs[(0, "left")] == Q(1, 19)


def test_repeatable_policy_supremum_reproduces_h_max_cost():
    problem = classification_problem(4)
    center, _, costs, envelopes, _ = fixtures(Q(1, 20), problem)
    for target in range(problem.target_count):
        observed = max(
            envelope.information[target] for envelope in envelopes
        )
        expected = 2 * max(
            costs[(target, query.name)] for query in center
        )
        assert observed == expected


@pytest.mark.parametrize("eta", (Q(1, 100), Q(1, 50), Q(1, 20), Q(1, 10)))
def test_policy_interval_contains_actual_classification_deficiency(eta: Q):
    problem = classification_problem(4)
    center, actual, costs, envelopes, reference = fixtures(eta, problem)
    policy = policy_specific_interval(envelopes, problem, reference)
    uniform = uniform_information_interval(
        envelopes, problem, center, costs, 2, reference
    )
    actual_deficiency = directed_upper_deficiency(
        adaptive_upper_generators(actual, problem, 2), reference
    ).epsilon
    assert policy.lower <= actual_deficiency <= policy.upper
    assert policy.upper < uniform.upper


@pytest.mark.parametrize("eta", (Q(1, 100), Q(1, 50), Q(1, 20), Q(1, 10)))
def test_group_decision_avoids_uncertain_queries_exactly(eta: Q):
    problem = binary_group_problem(
        "root_group", (0, 0, 1, 1), false_positive_cost=Q(1)
    )
    center, actual, costs, envelopes, reference = fixtures(eta, problem)
    policy = policy_specific_interval(envelopes, problem, reference)
    uniform = uniform_information_interval(
        envelopes, problem, center, costs, 2, reference
    )
    actual_deficiency = directed_upper_deficiency(
        adaptive_upper_generators(actual, problem, 2), reference
    ).epsilon
    assert actual_deficiency == 0
    assert policy.lower == policy.point == policy.upper == 0
    assert uniform.upper > 0


def test_policy_radius_is_strictly_smaller_on_zero_risk_classifier():
    problem = classification_problem(4)
    center, _, costs, envelopes, reference = fixtures(Q(1, 20), problem)
    radii = information_radii(envelopes, problem)
    zero_risk_rows = [
        (envelope, radius)
        for envelope, radius in zip(envelopes, radii)
        if envelope.risk == tuple([Q(0)] * 4)
    ]
    assert zero_risk_rows
    smallest = min(max(radius) for _, radius in zero_risk_rows)
    global_interval = uniform_information_interval(
        envelopes, problem, center, costs, 2, reference
    )
    assert smallest < global_interval.upper


def test_robust_box_interval_contains_all_vertex_deficiencies():
    source = ((Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1, 4)))
    radii = ((Q(1, 20), Q(1, 10)), (Q(1, 10), Q(1, 20)))
    reference = ((Q(0), Q(0)),)
    zero = ((Q(0), Q(0)),)
    interval = robust_directed_deficiency_interval(
        source, radii, reference, zero
    )
    for signs in (
        (-1, -1, -1, -1),
        (-1, -1, 1, 1),
        (-1, 1, -1, 1),
        (-1, 1, 1, -1),
        (1, -1, -1, 1),
        (1, -1, 1, -1),
        (1, 1, -1, -1),
        (1, 1, 1, 1),
    ):
        actual = (
            (
                source[0][0] + signs[0] * radii[0][0],
                source[0][1] + signs[1] * radii[0][1],
            ),
            (
                source[1][0] + signs[2] * radii[1][0],
                source[1][1] + signs[3] * radii[1][1],
            ),
        )
        deficiency = directed_upper_deficiency(
            actual, reference
        ).epsilon
        assert interval.lower <= deficiency <= interval.upper


def test_robust_box_interval_handles_reference_uncertainty():
    source = ((Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1, 4)))
    source_radii = (
        (Q(1, 20), Q(1, 10)),
        (Q(1, 10), Q(1, 20)),
    )
    reference = ((Q(1, 20), Q(1, 20)),)
    reference_radii = ((Q(1, 100), Q(1, 50)),)
    interval = robust_directed_deficiency_interval(
        source, source_radii, reference, reference_radii
    )
    for mask in range(64):
        signs = tuple(1 if mask & (1 << bit) else -1 for bit in range(6))
        actual_source = (
            (
                source[0][0] + signs[0] * source_radii[0][0],
                source[0][1] + signs[1] * source_radii[0][1],
            ),
            (
                source[1][0] + signs[2] * source_radii[1][0],
                source[1][1] + signs[3] * source_radii[1][1],
            ),
        )
        actual_reference = (
            (
                reference[0][0] + signs[4] * reference_radii[0][0],
                reference[0][1] + signs[5] * reference_radii[0][1],
            ),
        )
        deficiency = directed_upper_deficiency(
            actual_source, actual_reference
        ).epsilon
        assert interval.lower <= deficiency <= interval.upper


def test_query_budgets_reduce_the_information_supremum():
    problem = classification_problem(4)
    center = (ADAPTIVITY_GAP_QUERIES[1],)
    actual = (perturbed_queries(Q(1, 20))[1],)
    costs = query_chi_square_costs(center, actual)
    repeatable = enumerate_policy_envelopes(
        center, problem, 2, costs
    )
    once = enumerate_policy_envelopes(
        center,
        problem,
        2,
        costs,
        query_budgets={"left": 1},
    )
    assert max(max(row.information) for row in repeatable) == Q(2, 19)
    assert max(max(row.information) for row in once) == Q(1, 19)


def test_rational_square_root_is_outward():
    for value in (Q(0), Q(1, 2), Q(2), Q(9, 16), Q(17, 31)):
        upper = sqrt_fraction_upper(value, decimal_digits=12)
        assert upper**2 >= value
        if upper:
            step = Q(1, 10**12)
            assert upper - step < 0 or (upper - step) ** 2 < value


def test_multinomial_chi_square_support_checks():
    assert multinomial_chi_square(
        (Q(1), Q(0)), (Q(19, 20), Q(1, 20))
    ) == Q(1, 19)
    with pytest.raises(ValueError):
        multinomial_chi_square(
            (Q(1, 2), Q(1, 2)), (Q(1), Q(0))
        )


@pytest.mark.parametrize(
    "call,args",
    (
        (
            enumerate_policy_envelopes,
            (ADAPTIVITY_GAP_QUERIES, classification_problem(4), -1, {}),
        ),
        (sqrt_fraction_upper, (Q(-1),)),
        (
            robust_directed_deficiency_interval,
            (((Q(0),),), (), ((Q(0),),), ((Q(0),),)),
        ),
    ),
)
def test_invalid_inputs_fail_closed(call, args):
    with pytest.raises(ValueError):
        call(*args)
