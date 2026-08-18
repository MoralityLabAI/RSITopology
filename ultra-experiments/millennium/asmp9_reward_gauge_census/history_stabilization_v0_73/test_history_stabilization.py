from __future__ import annotations

from history_stabilization import (
    RewardMachine,
    binary_machine_registry,
    delayed_prefix_census,
    distinguishing_depth,
    fixed_partition,
    machine_census,
    pair_equivalence_census_two_state,
    partition_at_depth,
    shortest_distinguishing_word,
)


def test_two_state_registry_is_complete() -> None:
    machines = binary_machine_registry(2)
    assert len(machines) == 256
    assert all(machine.state_count == 2 for machine in machines)


def test_k_minus_one_partition_bound_on_complete_two_state_registry() -> None:
    census = machine_census(2)
    assert census["machine_count"] == 256
    assert census["depth_counts"] == {"0": 64, "1": 192}
    assert census["maximum_depth"] <= 1
    assert sum(census["depth_counts"].values()) == 256


def test_compact_census_matches_object_api_on_all_two_state_machines() -> None:
    object_counts: dict[str, int] = {}
    for machine in binary_machine_registry(2):
        key = str(distinguishing_depth(machine))
        object_counts[key] = object_counts.get(key, 0) + 1
    assert object_counts == machine_census(2)["depth_counts"]


def test_k_minus_one_partition_bound_on_complete_three_state_registry() -> None:
    census = machine_census(3)
    assert census["machine_count"] == 46_656
    assert census["depth_counts"] == {"0": 2_916, "1": 25_596, "2": 18_144}
    assert census["maximum_depth"] <= 2
    assert sum(census["depth_counts"].values()) == 46_656


def test_pair_product_bound_on_all_two_state_pairs() -> None:
    census = pair_equivalence_census_two_state()
    assert census["unordered_pairs_with_repetition"] == 32_896
    assert census["equivalent"] == 1_768
    assert census["distinguishable"] == 31_128
    assert census["maximum_word_length"] == 3
    assert census["equivalent"] + census["distinguishable"] == 32_896
    assert census["maximum_word_length"] <= census["product_bound"]


def test_delayed_bonus_defeats_every_finite_prefix_in_registry() -> None:
    census = delayed_prefix_census(12)
    assert census["all_prefixes_indistinguishable"]
    assert census["all_delayed_witnesses_nonstationary"]
    assert census["records"][-1]["delayed_minimum_unary_states"] == 14


def test_explicit_machine_needs_depth_two_to_split_states() -> None:
    # State 2 separates immediately. States 0 and 1 emit equal first rewards,
    # but transition to states with distinct second-step rewards.
    machine = RewardMachine(
        state_count=3,
        alphabet_size=1,
        transition={(0, 0): 1, (1, 0): 2, (2, 0): 2},
        reward={(0, 0): 0, (1, 0): 0, (2, 0): 1},
    )
    assert partition_at_depth(machine, 1) == (0, 0, 1)
    assert partition_at_depth(machine, 2) == fixed_partition(machine)
    assert distinguishing_depth(machine) == 2


def test_shortest_distinguishing_word_is_constructive() -> None:
    left = RewardMachine(
        state_count=2,
        alphabet_size=1,
        transition={(0, 0): 1, (1, 0): 1},
        reward={(0, 0): 0, (1, 0): 0},
    )
    right = RewardMachine(
        state_count=2,
        alphabet_size=1,
        transition={(0, 0): 1, (1, 0): 1},
        reward={(0, 0): 0, (1, 0): 1},
    )
    assert shortest_distinguishing_word(left, right) == (0, 0)
