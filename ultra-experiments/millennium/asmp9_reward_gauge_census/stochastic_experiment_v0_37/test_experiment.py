from fractions import Fraction
from itertools import product

from experiment import (
    BinaryExperiment,
    connected_components,
    directional_deficiency,
    minimax_correspondence_risk,
    minimax_sample_risk,
    population_observation_sets,
    sampled_support_sets,
)


Q = Fraction


def experiment(*rows: tuple[Fraction, ...]) -> BinaryExperiment:
    return BinaryExperiment(tuple(tuple(row) for row in rows))


def test_directional_deficiency_identity_is_zero() -> None:
    source = experiment(
        (Q(1, 5), Q(2, 5)),
        (Q(3, 5), Q(4, 5)),
        (Q(1, 2), Q(1, 2)),
    )
    optimum = directional_deficiency(source, source)
    assert optimum.value == 0
    assert all(0 <= value <= 1 for value in optimum.variables[:2])
    assert optimum.dual_weights
    assert all(weight >= 0 for weight in optimum.dual_weights)


def test_directional_deficiency_detects_information_asymmetry() -> None:
    uninformative = experiment(
        (Q(1, 2), Q(1, 2)),
        (Q(1, 2), Q(1, 2)),
        (Q(1, 2), Q(1, 2)),
    )
    informative = experiment(
        (Q(1, 4), Q(1, 4)),
        (Q(1, 2), Q(1, 2)),
        (Q(3, 4), Q(3, 4)),
    )
    assert directional_deficiency(informative, uninformative).value == 0
    assert (
        directional_deficiency(uninformative, informative).value
        == Q(1, 4)
    )


def test_same_sampled_zero_error_quotient_can_hide_risk_gap() -> None:
    uninformative = experiment(
        (Q(1, 2), Q(1, 2)),
        (Q(1, 2), Q(1, 2)),
        (Q(1, 2), Q(1, 2)),
    )
    informative = experiment(
        (Q(1, 10), Q(1, 5)),
        (Q(1, 10), Q(1, 5)),
        (Q(4, 5), Q(9, 10)),
    )
    assert connected_components(sampled_support_sets(uninformative)) == (
        (0, 1, 2),
    )
    assert connected_components(sampled_support_sets(informative)) == (
        (0, 1, 2),
    )
    decision = (0, 0, 1)
    assert minimax_sample_risk(uninformative, decision).value == Q(1, 2)
    assert minimax_sample_risk(informative, decision).value == Q(1, 5)


def test_population_component_quotient_hides_identity_risk() -> None:
    path = (
        frozenset(("a",)),
        frozenset(("a", "b")),
        frozenset(("b",)),
    )
    complete = (
        frozenset(("a",)),
        frozenset(("a",)),
        frozenset(("a",)),
    )
    assert connected_components(path) == ((0, 1, 2),)
    assert connected_components(complete) == ((0, 1, 2),)
    assert minimax_correspondence_risk(path, (0, 1, 2)).value == Q(1, 2)
    assert (
        minimax_correspondence_risk(complete, (0, 1, 2)).value
        == Q(2, 3)
    )


def test_full_deficiency_can_be_conservative_for_target_decisions() -> None:
    source = experiment(
        (Q(0), Q(0)),
        (Q(0), Q(0)),
        (Q(0), Q(0)),
    )
    nuisance_only = experiment(
        (Q(0), Q(1)),
        (Q(0), Q(1)),
        (Q(0), Q(1)),
    )
    assert directional_deficiency(source, nuisance_only).value == Q(1, 2)
    for decision in product((0, 1), repeat=3):
        assert minimax_sample_risk(source, decision).value == (
            minimax_sample_risk(nuisance_only, decision).value
        )
    assert minimax_sample_risk(source, (0, 1, 2)).value == (
        minimax_sample_risk(nuisance_only, (0, 1, 2)).value
    )


def test_deficiency_bounds_registered_target_only_risk_gaps() -> None:
    experiments = (
        experiment(
            (Q(1, 2), Q(1, 2)),
            (Q(1, 2), Q(1, 2)),
            (Q(1, 2), Q(1, 2)),
        ),
        experiment(
            (Q(1, 4), Q(1, 4)),
            (Q(1, 2), Q(1, 2)),
            (Q(3, 4), Q(3, 4)),
        ),
        experiment(
            (Q(0), Q(1)),
            (Q(0), Q(1)),
            (Q(0), Q(1)),
        ),
    )
    decisions = tuple(product((0, 1), repeat=3)) + ((0, 1, 2),)
    for source in experiments:
        for target in experiments:
            bound = directional_deficiency(source, target).value
            for decision in decisions:
                source_risk = minimax_sample_risk(source, decision).value
                target_risk = minimax_sample_risk(target, decision).value
                assert source_risk <= target_risk + bound


def test_population_and_sample_oracles_are_not_conflated() -> None:
    value = experiment(
        (Q(0), Q(1)),
        (Q(0), Q(1)),
        (Q(0), Q(1)),
    )
    assert population_observation_sets(value) == (
        frozenset((Q(0), Q(1))),
        frozenset((Q(0), Q(1))),
        frozenset((Q(0), Q(1))),
    )
    assert sampled_support_sets(value) == (
        frozenset((0, 1)),
        frozenset((0, 1)),
        frozenset((0, 1)),
    )


def test_binary_experiment_rejects_invalid_shapes() -> None:
    try:
        BinaryExperiment(((Q(0),), (Q(0), Q(1))))
    except ValueError as error:
        assert "ragged" in str(error)
    else:
        raise AssertionError("ragged experiment was accepted")

    try:
        BinaryExperiment(((Q(-1),),))
    except ValueError as error:
        assert "[0,1]" in str(error)
    else:
        raise AssertionError("invalid probability was accepted")
