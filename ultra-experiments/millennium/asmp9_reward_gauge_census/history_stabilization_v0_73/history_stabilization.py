"""Finite-state and finite-prefix boundaries for ASMP-9 v0.73."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Iterator, Mapping, Sequence


State = int
Symbol = int


@dataclass(frozen=True)
class RewardMachine:
    state_count: int
    alphabet_size: int
    transition: Mapping[tuple[State, Symbol], State]
    reward: Mapping[tuple[State, Symbol], Fraction]

    def validate(self) -> None:
        if self.state_count <= 0 or self.alphabet_size <= 0:
            raise ValueError("machine dimensions must be positive")
        expected = {
            (state, symbol)
            for state in range(self.state_count)
            for symbol in range(self.alphabet_size)
        }
        if set(self.transition) != expected or set(self.reward) != expected:
            raise ValueError("transition and reward tables must be complete")
        if any(
            target < 0 or target >= self.state_count
            for target in self.transition.values()
        ):
            raise ValueError("transition target outside state universe")


def _canonical_classes(keys: Sequence[object]) -> tuple[int, ...]:
    """Assign stable class labels in state order.

    First-occurrence labels avoid an otherwise unnecessary sort and, more
    importantly, make equality of two successive refinement tuples equivalent
    to equality of their partitions.
    """

    unique: dict[object, int] = {}
    labels = []
    for key in keys:
        if key not in unique:
            unique[key] = len(unique)
        labels.append(unique[key])
    return tuple(labels)


def partition_at_depth(machine: RewardMachine, depth: int) -> tuple[int, ...]:
    """State equivalence under reward words of length at most ``depth``."""

    machine.validate()
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    classes = tuple(0 for _ in range(machine.state_count))
    for _ in range(depth):
        classes = _refine(machine, classes)
    return classes


def _refine(machine: RewardMachine, classes: tuple[int, ...]) -> tuple[int, ...]:
    keys = [
        tuple(
            (
                machine.reward[(state, symbol)],
                classes[machine.transition[(state, symbol)]],
            )
            for symbol in range(machine.alphabet_size)
        )
        for state in range(machine.state_count)
    ]
    return _canonical_classes(keys)


def fixed_partition(machine: RewardMachine) -> tuple[int, ...]:
    machine.validate()
    classes = tuple(0 for _ in range(machine.state_count))
    while True:
        refined = _refine(machine, classes)
        if refined == classes:
            return classes
        classes = refined


def distinguishing_depth(machine: RewardMachine) -> int:
    machine.validate()
    return _distinguishing_depth_validated(machine)


def _distinguishing_depth_validated(machine: RewardMachine) -> int:
    classes = tuple(0 for _ in range(machine.state_count))
    for depth in range(machine.state_count):
        refined = _refine(machine, classes)
        if refined == classes:
            return depth
        classes = refined
    raise AssertionError("K-state refinement exceeded K-1 strict refinements")


def shortest_distinguishing_word(
    left: RewardMachine,
    right: RewardMachine,
    *,
    left_start: int = 0,
    right_start: int = 0,
) -> tuple[int, ...] | None:
    """Return a shortest word with different reward output, or ``None``."""

    left.validate()
    right.validate()
    return _shortest_distinguishing_word_validated(
        left,
        right,
        left_start=left_start,
        right_start=right_start,
    )


def _shortest_distinguishing_word_validated(
    left: RewardMachine,
    right: RewardMachine,
    *,
    left_start: int,
    right_start: int,
) -> tuple[int, ...] | None:
    if left.alphabet_size != right.alphabet_size:
        raise ValueError("machines must use the same alphabet")

    queue: deque[tuple[int, int, tuple[int, ...]]] = deque(
        [(left_start, right_start, tuple())]
    )
    visited = {(left_start, right_start)}
    while queue:
        left_state, right_state, prefix = queue.popleft()
        for symbol in range(left.alphabet_size):
            word = prefix + (symbol,)
            if Fraction(left.reward[(left_state, symbol)]) != Fraction(
                right.reward[(right_state, symbol)]
            ):
                return word
            pair = (
                left.transition[(left_state, symbol)],
                right.transition[(right_state, symbol)],
            )
            if pair not in visited:
                visited.add(pair)
                queue.append((pair[0], pair[1], word))
    return None


def _iter_binary_machine_tables(
    state_count: int,
) -> Iterator[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Stream complete binary machines as compact transition/reward tables."""

    cells = state_count * 2
    for transitions in product(range(state_count), repeat=cells):
        for rewards in product((0, 1), repeat=cells):
            yield transitions, rewards


def iter_binary_machines(state_count: int) -> Iterator[RewardMachine]:
    for transitions, rewards in _iter_binary_machine_tables(state_count):
        yield RewardMachine(
                state_count=state_count,
                alphabet_size=2,
                transition={
                    (state, symbol): transitions[state * 2 + symbol]
                    for state in range(state_count)
                    for symbol in range(2)
                },
                reward={
                    (state, symbol): Fraction(rewards[state * 2 + symbol])
                    for state in range(state_count)
                    for symbol in range(2)
                },
            )


def binary_machine_registry(state_count: int) -> tuple[RewardMachine, ...]:
    return tuple(iter_binary_machines(state_count))


def _table_distinguishing_depth(
    state_count: int,
    transitions: tuple[int, ...],
    rewards: tuple[int, ...],
) -> int:
    """Compact equivalent of ``distinguishing_depth`` for exhaustive census."""

    classes = tuple(0 for _ in range(state_count))
    for depth in range(state_count):
        keys = [
            (
                rewards[2 * state],
                classes[transitions[2 * state]],
                rewards[2 * state + 1],
                classes[transitions[2 * state + 1]],
            )
            for state in range(state_count)
        ]
        refined = _canonical_classes(keys)
        if refined == classes:
            return depth
        classes = refined
    raise AssertionError("K-state refinement exceeded K-1 strict refinements")


def machine_census(state_count: int) -> dict[str, object]:
    depth_counts: dict[int, int] = {}
    machine_count = 0
    for transitions, rewards in _iter_binary_machine_tables(state_count):
        machine_count += 1
        depth = _table_distinguishing_depth(state_count, transitions, rewards)
        depth_counts[depth] = depth_counts.get(depth, 0) + 1
    return {
        "state_count": state_count,
        "machine_count": machine_count,
        "depth_counts": {str(key): value for key, value in sorted(depth_counts.items())},
        "maximum_depth": max(depth_counts),
        "bound": state_count - 1,
    }


def pair_equivalence_census_two_state() -> dict[str, int]:
    machines = tuple(_iter_binary_machine_tables(2))
    equivalent = 0
    distinguishable = 0
    maximum_word_length = 0
    for left_index, left in enumerate(machines):
        for right in machines[left_index:]:
            witness = _shortest_distinguishing_word_tables(left, right)
            if witness is None:
                equivalent += 1
            else:
                distinguishable += 1
                maximum_word_length = max(maximum_word_length, len(witness))
                assert len(witness) <= 4
    return {
        "unordered_pairs_with_repetition": len(machines) * (len(machines) + 1) // 2,
        "equivalent": equivalent,
        "distinguishable": distinguishable,
        "maximum_word_length": maximum_word_length,
        "product_bound": 4,
    }


def _shortest_distinguishing_word_tables(
    left: tuple[tuple[int, ...], tuple[int, ...]],
    right: tuple[tuple[int, ...], tuple[int, ...]],
) -> tuple[int, ...] | None:
    """Binary, start-state-zero product search used by the finite census."""

    left_transition, left_reward = left
    right_transition, right_reward = right
    queue: deque[tuple[int, int, tuple[int, ...]]] = deque([(0, 0, tuple())])
    visited = {(0, 0)}
    while queue:
        left_state, right_state, prefix = queue.popleft()
        for symbol in range(2):
            left_index = 2 * left_state + symbol
            right_index = 2 * right_state + symbol
            word = prefix + (symbol,)
            if left_reward[left_index] != right_reward[right_index]:
                return word
            pair = (
                left_transition[left_index],
                right_transition[right_index],
            )
            if pair not in visited:
                visited.add(pair)
                queue.append((pair[0], pair[1], word))
    return None


def delayed_bonus_values(prefix_horizon: int, maximum_length: int) -> tuple[Fraction, ...]:
    if prefix_horizon < 0 or maximum_length < prefix_horizon + 1:
        raise ValueError("maximum length must expose the delayed bonus")
    return tuple(
        Fraction(0 if length <= prefix_horizon else 1)
        for length in range(maximum_length + 1)
    )


def zero_values(maximum_length: int) -> tuple[Fraction, ...]:
    return tuple(Fraction(0) for _ in range(maximum_length + 1))


def stationary_loop_factorizes(values: Sequence[Fraction]) -> bool:
    if len(values) <= 1:
        return True
    base = Fraction(values[0])
    reward = Fraction(values[1]) - base
    return all(
        Fraction(value) == base + index * reward
        for index, value in enumerate(values)
    )


def delayed_prefix_census(maximum_horizon: int) -> dict[str, object]:
    records = []
    for horizon in range(maximum_horizon + 1):
        maximum_length = horizon + 2
        zero = zero_values(maximum_length)
        delayed = delayed_bonus_values(horizon, maximum_length)
        records.append(
            {
                "horizon": horizon,
                "prefix_equal": zero[: horizon + 1] == delayed[: horizon + 1],
                "zero_stationary": stationary_loop_factorizes(zero),
                "delayed_stationary": stationary_loop_factorizes(delayed),
                "delayed_minimum_unary_states": horizon + 2,
            }
        )
    return {
        "maximum_horizon": maximum_horizon,
        "records": records,
        "all_prefixes_indistinguishable": all(
            record["prefix_equal"] for record in records
        ),
        "all_delayed_witnesses_nonstationary": all(
            not record["delayed_stationary"] for record in records
        ),
    }
