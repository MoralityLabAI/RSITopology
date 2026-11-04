from fractions import Fraction

from source_fiber import (
    ACTIONS,
    SOURCES,
    WORLDS,
    build_result,
    bump,
    bump_prime,
    fisher_information,
    globally_good_actions,
    joint_pmf,
    joint_pmf_derivative,
    risk,
    two_action_fiber_value,
)


def test_complete_source_experiments_are_equal_to_first_order() -> None:
    for theta in SOURCES:
        assert bump(theta) == 0
        assert bump_prime(theta) == 0
        assert joint_pmf(-1, theta) == joint_pmf(1, theta)
        assert joint_pmf_derivative(-1, theta) == joint_pmf_derivative(1, theta)


def test_local_fisher_information_is_positive_and_exact() -> None:
    assert fisher_information(-1, Fraction(0)) == Fraction(3, 32)
    assert fisher_information(1, Fraction(0)) == Fraction(3, 32)


def test_each_world_has_exactly_one_opposite_good_action() -> None:
    for world in WORLDS:
        assert globally_good_actions(world) == frozenset((-world,))
        assert risk(world, -world, Fraction(1)) == Fraction(7, 16)
        assert risk(world, world, Fraction(1)) == Fraction(11, 16)


def test_exact_source_fiber_value() -> None:
    good_sets = [globally_good_actions(world) for world in WORLDS]
    q, value = two_action_fiber_value(good_sets)
    assert q == Fraction(1, 2)
    assert value == Fraction(1, 2)


def test_no_deterministic_action_succeeds_in_both_worlds() -> None:
    for action in ACTIONS:
        assert not all(action in globally_good_actions(world) for world in WORLDS)


def test_result_gates_and_claim_boundary() -> None:
    result = build_result()
    assert result["all_gates_passed"]
    assert result["fiber_certificate"]["randomized_uniform_success"] == "1/2"
    assert result["adjudication"]["candidate_negative_result"] is True
    assert result["adjudication"]["problem_resolved"] is False
