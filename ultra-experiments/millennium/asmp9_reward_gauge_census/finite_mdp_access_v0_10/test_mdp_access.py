from __future__ import annotations

from fractions import Fraction

import pytest

from mdp_access import (
    action_difference_matrix,
    baseline_pair_intersection_dimension,
    cyclic_action_kernel,
    deterministic_kernel,
    deterministic_kernels,
    deterministic_policy_witness,
    image_intersection_dimension,
    matrix_rank,
    residual_reward_ambiguity_dimension,
    self_loop_kernel,
    shaping_matrix,
    successor_difference_components,
    trajectory_ambiguity_dimension,
)


@pytest.mark.parametrize("states", range(1, 17))
@pytest.mark.parametrize("actions", (1, 2, 3))
@pytest.mark.parametrize("discount", (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)))
def test_shaping_operator_is_injective(
    states: int, actions: int, discount: Fraction
) -> None:
    kernel = self_loop_kernel(states, actions)
    assert matrix_rank(shaping_matrix(kernel, discount)) == states


@pytest.mark.parametrize("states", range(2, 17))
def test_cyclic_transition_pair_leaves_only_constant(states: int) -> None:
    discount = Fraction(2, 3)
    baseline = self_loop_kernel(states, 2)
    cyclic = cyclic_action_kernel(states, 2)
    assert residual_reward_ambiguity_dimension(
        ((baseline, discount), (cyclic, discount))
    ) == 1
    assert baseline_pair_intersection_dimension(cyclic, discount) == 1


@pytest.mark.parametrize("states", range(2, 17))
def test_two_discount_factors_leave_only_constant(states: int) -> None:
    kernel = cyclic_action_kernel(states, 2)
    assert residual_reward_ambiguity_dimension(
        (
            (kernel, Fraction(1, 2)),
            (kernel, Fraction(3, 4)),
        )
    ) == 1


def test_same_environment_twice_does_not_reduce_ambiguity() -> None:
    kernel = cyclic_action_kernel(5, 2)
    matrix = shaping_matrix(kernel, Fraction(1, 2))
    assert image_intersection_dimension((matrix, matrix)) == 5


def test_successor_component_formula_with_disconnected_kernel() -> None:
    # Successor-difference edges are 0--1 and 2--3.
    kernel = deterministic_kernel(4, 2, (0, 1, 0, 1, 2, 3, 2, 3))
    assert successor_difference_components(kernel) == 2
    assert matrix_rank(action_difference_matrix(kernel)) == 2
    assert baseline_pair_intersection_dimension(kernel, Fraction(1, 2)) == 2


@pytest.mark.parametrize("states", (2, 3))
def test_burned_deterministic_census(states: int) -> None:
    for kernel in deterministic_kernels(states, 2):
        components = successor_difference_components(kernel)
        assert (
            states - matrix_rank(action_difference_matrix(kernel))
            == components
        )
        assert (
            baseline_pair_intersection_dimension(kernel, Fraction(2, 3))
            == components
        )


def test_trajectory_query_graph_components_are_ambiguity_dimension() -> None:
    assert trajectory_ambiguity_dimension(4, ()) == 4
    assert trajectory_ambiguity_dimension(4, ((0, 1), (1, 2))) == 2
    assert (
        trajectory_ambiguity_dimension(
            4, ((0, 1), (1, 2), (2, 3))
        )
        == 1
    )


@pytest.mark.parametrize("states", range(2, 17))
def test_deterministic_policy_counterexample_survives_two_environments(
    states: int,
) -> None:
    witness = deterministic_policy_witness(states, Fraction(1, 2))
    assert witness["same_strict_policy"]
    assert witness["common_gauge_dimension"] == 1
    assert not witness["difference_is_common_constant"]
