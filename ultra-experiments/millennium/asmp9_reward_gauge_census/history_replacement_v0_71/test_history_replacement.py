from __future__ import annotations

from fractions import Fraction

from history_replacement import (
    binary_valuation_census,
    canonical_fixtures,
    canonical_history_replacement,
    enumerate_histories,
    factor_markov_reward,
    replay_replacement,
)


def test_history_enumeration_is_prefix_closed() -> None:
    system = canonical_fixtures()["markov_additive"]
    histories = enumerate_histories(system.edges, system.start, system.horizon)
    assert histories == (
        tuple(),
        ("a",),
        ("b",),
        ("a", "z"),
        ("b", "z"),
    )
    assert all(path[:-1] in histories for path in histories if path)


def test_additive_fixture_recovers_edge_rewards() -> None:
    result = factor_markov_reward(canonical_fixtures()["markov_additive"])
    assert result.factorizes
    assert result.edge_rewards == {"a": "1", "b": "2", "z": "3"}
    assert result.obstruction_coefficients is None


def test_history_interaction_emits_exact_left_kernel_witness() -> None:
    system = canonical_fixtures()["history_interaction"]
    result = factor_markov_reward(system)
    assert not result.factorizes
    assert result.obstruction_coefficients
    assert Fraction(result.obstruction_value) != 0

    histories = system.histories()
    coefficients = {
        path: Fraction(result.obstruction_coefficients.get(path, "0"))
        for path in histories
    }
    for edge in system.edges:
        count_sum = sum(
            coefficients[path] * path.count(edge.edge_id)
            for path in histories
        )
        assert count_sum == 0
    value_sum = sum(
        coefficients[path] * system.values[path] for path in histories
    )
    assert value_sum == Fraction(result.obstruction_value)


def test_markov_fixture_needs_no_history_split() -> None:
    system = canonical_fixtures()["markov_additive"]
    replacement = canonical_history_replacement(system)
    assert not replacement.needs_history_augmentation
    assert replay_replacement(system, replacement)
    assert replacement.history_to_class[("a",)] == (
        replacement.history_to_class[("b",)]
    )


def test_interaction_fixture_splits_same_state_same_time_histories() -> None:
    system = canonical_fixtures()["history_interaction"]
    replacement = canonical_history_replacement(system)
    assert replacement.needs_history_augmentation
    assert replacement.class_count == replacement.state_time_count + 1
    assert replacement.history_to_class[("a",)] != (
        replacement.history_to_class[("b",)]
    )
    assert replay_replacement(system, replacement)


def test_replacement_transition_rewards_reconstruct_every_path() -> None:
    for system in canonical_fixtures().values():
        replacement = canonical_history_replacement(system)
        assert replay_replacement(system, replacement)


def test_complete_binary_valuation_census() -> None:
    census = binary_valuation_census()
    assert census == {
        "total": 16,
        "factorizing": 6,
        "nonfactorizing": 10,
        "history_augmented": 10,
        "replay_failures": 0,
    }
