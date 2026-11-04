from fractions import Fraction as Q

from confirmation import (
    BURNED_STRENGTHS,
    CONFIRMATION_STRENGTHS,
    NUISANCE_ONE_PROBABILITIES,
    QUERY_NAMES,
    canonical_target_experiment,
    expanded_for_subset,
    policy_problem,
)


def test_confirmation_grid_is_disjoint_and_rational() -> None:
    assert set(CONFIRMATION_STRENGTHS).isdisjoint(BURNED_STRENGTHS)
    assert len(set(CONFIRMATION_STRENGTHS)) == 3
    for high, low in CONFIRMATION_STRENGTHS:
        assert Q(0) <= low < high <= Q(1)
    assert NUISANCE_ONE_PROBABILITIES == (Q(1, 2), Q(2, 3))


def test_registered_reward_problem_is_live() -> None:
    problem = policy_problem()
    assert problem.losses == (
        (Q(0), Q(1), Q(1)),
        (Q(1), Q(0), Q(1)),
        (Q(1), Q(1), Q(0)),
    )


def test_query_grammar_dimensions_are_frozen() -> None:
    high, low = CONFIRMATION_STRENGTHS[0]
    canonical = canonical_target_experiment(
        high, low, ("q_target_0", "q_target_1")
    )
    expanded = expanded_for_subset(high, low, QUERY_NAMES)
    assert canonical.target_count == 3
    assert canonical.observation_count == 4
    assert expanded.target_count == 3
    assert expanded.nuisance_count == 2
    assert expanded.observation_count == 8

