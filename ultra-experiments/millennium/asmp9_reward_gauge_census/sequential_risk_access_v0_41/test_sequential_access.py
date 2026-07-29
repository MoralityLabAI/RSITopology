from fractions import Fraction as Q

from sequential_access import (
    ADAPTIVITY_GAP_QUERIES,
    DecisionProblem,
    QueryChannel,
    adaptive_upper_generators,
    binary_group_problem,
    burned_adaptivity_gap,
    classification_problem,
    directed_upper_deficiency,
    fixed_sequence_upper_generators,
    nonadaptive_upper_generators,
    query_step_generators,
    terminal_generators,
    upper_minimal_generators,
    zero_risk_available,
)


def test_terminal_generators_are_action_risks():
    problem = classification_problem(3)
    assert terminal_generators(problem) == (
        (Q(0), Q(1), Q(1)),
        (Q(1), Q(0), Q(1)),
        (Q(1), Q(1), Q(0)),
    )


def test_upper_pruning_preserves_only_coordinate_minimal_vectors():
    assert upper_minimal_generators(
        ((Q(0), Q(1)), (Q(0), Q(1)), (Q(1), Q(1)))
    ) == ((Q(0), Q(1)),)


def test_stochastic_query_step_is_exact():
    query = QueryChannel(
        "noisy",
        (
            (Q(3, 4), Q(1, 4)),
            (Q(1, 4), Q(3, 4)),
        ),
    )
    problem = classification_problem(2)
    stepped = query_step_generators(query, terminal_generators(problem))
    assert (Q(1, 4), Q(1, 4)) in stepped


def test_adaptive_two_step_policy_identifies_all_four_targets():
    problem = classification_problem(4)
    adaptive = adaptive_upper_generators(
        ADAPTIVITY_GAP_QUERIES, problem, 2
    )
    assert zero_risk_available(adaptive)


def test_no_two_query_open_loop_sequence_identifies_all_targets():
    problem = classification_problem(4)
    for first in ADAPTIVITY_GAP_QUERIES:
        for second in ADAPTIVITY_GAP_QUERIES:
            assert not zero_risk_available(
                fixed_sequence_upper_generators(
                    (first, second), problem
                )
            )
    assert not zero_risk_available(
        nonadaptive_upper_generators(
            ADAPTIVITY_GAP_QUERIES, problem, 2
        )
    )


def test_three_query_open_loop_access_recovers_exactly():
    problem = classification_problem(4)
    assert zero_risk_available(
        nonadaptive_upper_generators(
            ADAPTIVITY_GAP_QUERIES, problem, 3
        )
    )


def test_directed_deficiency_recovers_half_for_two_unresolved_targets():
    source = ((Q(0), Q(1)), (Q(1), Q(0)))
    reference = ((Q(0), Q(0)),)
    certificate = directed_upper_deficiency(source, reference)
    assert certificate.epsilon == Q(1, 2)
    assert certificate.source_risk == (Q(1, 2), Q(1, 2))


def test_burned_gap_reports_exact_crossover():
    result = burned_adaptivity_gap()
    assert result["adaptive_h2"]["deficiency_to_full"]["epsilon"] == "0"
    assert result["nonadaptive_h2"]["deficiency_to_full"]["epsilon"] == "1/4"
    assert result["nonadaptive_h3"]["deficiency_to_full"]["epsilon"] == "0"
    assert result["prediction_match"] == {
        "adaptive_h2": True,
        "nonadaptive_h2": False,
        "nonadaptive_h3": True,
    }


def test_problem_validation_rejects_negative_loss():
    try:
        DecisionProblem("bad", ((Q(-1), Q(0)),))
    except ValueError:
        pass
    else:
        raise AssertionError("negative loss was accepted")


def test_binary_group_problem_keeps_asymmetric_costs_exact():
    problem = binary_group_problem(
        "group",
        (0, 0, 1, 1),
        false_positive_cost=Q(1, 3),
        false_negative_cost=Q(2, 3),
    )
    assert problem.losses == (
        (Q(0), Q(1, 3)),
        (Q(0), Q(1, 3)),
        (Q(2, 3), Q(0)),
        (Q(2, 3), Q(0)),
    )
