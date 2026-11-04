from fractions import Fraction as Q

from relative_deficiency import (
    DecisionProblem,
    ExpandedExperiment,
    FiniteExperiment,
    marginalize_nuisance,
    minimax_value,
    ordinary_deficiency,
    optimized_value_gap,
    policy_regret_problem,
    relative_deficiency,
)


BINARY_LOSS = DecisionProblem(
    name="binary_identification",
    losses=((Q(0), Q(1)), (Q(1), Q(0))),
)


def test_blackwell_anchors_are_exact() -> None:
    informative = FiniteExperiment(((Q(1), Q(0)), (Q(0), Q(1))))
    constant = FiniteExperiment(((Q(1), Q(0)), (Q(1), Q(0))))
    assert ordinary_deficiency(informative, constant).epsilon == 0
    assert ordinary_deficiency(constant, informative).epsilon == Q(1, 2)
    assert relative_deficiency(
        informative, constant, (BINARY_LOSS,)
    ).epsilon == 0
    assert relative_deficiency(
        constant, informative, (BINARY_LOSS,)
    ).epsilon == Q(1, 2)


def test_equal_minimax_value_does_not_imply_relative_equivalence() -> None:
    left = FiniteExperiment(((Q(0), Q(1)), (Q(1, 2), Q(1, 2))))
    right = FiniteExperiment(((Q(1, 2), Q(1, 2)), (Q(1), Q(0))))
    assert minimax_value(left, BINARY_LOSS).value == Q(1, 3)
    assert minimax_value(right, BINARY_LOSS).value == Q(1, 3)
    assert optimized_value_gap(left, right, (BINARY_LOSS,)) == 0
    assert relative_deficiency(left, right, (BINARY_LOSS,)).epsilon == Q(
        1, 6
    )


def test_fixed_nuisance_law_separates_target_and_expanded_comparison() -> None:
    constant = ExpandedExperiment(
        (
            ((Q(1), Q(0)), (Q(1), Q(0))),
            ((Q(1), Q(0)), (Q(1), Q(0))),
        )
    )
    nuisance_only = ExpandedExperiment(
        (
            ((Q(1), Q(0)), (Q(0), Q(1))),
            ((Q(1), Q(0)), (Q(0), Q(1))),
        )
    )
    nuisance_law = ((Q(1, 2), Q(1, 2)), (Q(1, 2), Q(1, 2)))
    marginal_constant = marginalize_nuisance(constant, nuisance_law)
    marginal_nuisance = marginalize_nuisance(nuisance_only, nuisance_law)
    assert ordinary_deficiency(
        marginal_constant, marginal_nuisance
    ).epsilon == 0
    assert relative_deficiency(
        marginal_constant, marginal_nuisance, (BINARY_LOSS,)
    ).epsilon == 0
    assert ordinary_deficiency(
        constant.flatten(), nuisance_only.flatten()
    ).epsilon == Q(1, 2)


def test_policy_regret_is_invariant_to_constant_reward_shift() -> None:
    occupancies = ((Q(1), Q(0)), (Q(0), Q(1)))
    base = policy_regret_problem(
        "base", occupancies, ((Q(1), Q(0)), (Q(0), Q(1)))
    )
    shifted = policy_regret_problem(
        "shifted", occupancies, ((Q(2), Q(1)), (Q(1), Q(2)))
    )
    assert base.losses == shifted.losses

