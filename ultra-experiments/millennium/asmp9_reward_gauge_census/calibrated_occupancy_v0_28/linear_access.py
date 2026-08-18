from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import ceil, log2
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True)
class TrajectoryPair:
    positive_path: tuple[int, ...]
    negative_path: tuple[int, ...]


@dataclass(frozen=True)
class DeterministicTransition:
    source_state: str
    action: str
    target_state: str
    feature: int


@dataclass(frozen=True)
class OccupancyQuery:
    initial_state: str
    positive_action: str
    negative_action: str
    horizon: int


@dataclass(frozen=True)
class DeterministicFeatureMDP:
    feature_count: int
    states: tuple[str, ...]
    transitions: tuple[DeterministicTransition, ...]
    queries: tuple[OccupancyQuery, ...]


def q(value) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def rational_link(value: Fraction) -> Fraction:
    """Strictly increasing symmetric link with exact rational values."""
    value = q(value)
    return Fraction(1, 2) + value / (2 * (1 + abs(value)))


def rescaled_rational_link(value: Fraction, alpha: Fraction) -> Fraction:
    alpha = q(alpha)
    if alpha <= 0:
        raise ValueError("scale must be positive")
    return rational_link(q(value) / alpha)


def dot(row: Sequence, vector: Sequence) -> Fraction:
    if len(row) != len(vector):
        raise ValueError("dimension mismatch")
    return sum((q(a) * q(b) for a, b in zip(row, vector)), Fraction(0))


def population_law(matrix: Sequence[Sequence], reward: Sequence):
    return tuple(rational_link(dot(row, reward)) for row in matrix)


def scaled_population_law(
    matrix: Sequence[Sequence], reward: Sequence, alpha
):
    alpha = q(alpha)
    scaled_reward = tuple(alpha * q(value) for value in reward)
    return tuple(
        rescaled_rational_link(dot(row, scaled_reward), alpha)
        for row in matrix
    )


def unknown_numeraire_law(
    matrix: Sequence[Sequence],
    reward: Sequence,
    offsets: Sequence,
    coefficient,
):
    if len(matrix) != len(offsets):
        raise ValueError("one offset per row is required")
    coefficient = q(coefficient)
    return tuple(
        rational_link(dot(row, reward) + q(offset) * coefficient)
        for row, offset in zip(matrix, offsets)
    )


def scaled_unknown_numeraire_law(
    matrix: Sequence[Sequence],
    reward: Sequence,
    offsets: Sequence,
    coefficient,
    alpha,
):
    alpha = q(alpha)
    scaled_reward = tuple(alpha * q(value) for value in reward)
    scaled_coefficient = alpha * q(coefficient)
    return tuple(
        rescaled_rational_link(
            dot(row, scaled_reward) + q(offset) * scaled_coefficient,
            alpha,
        )
        for row, offset in zip(matrix, offsets)
    )


def known_numeraire_law(
    matrix: Sequence[Sequence], reward: Sequence, offsets: Sequence
):
    if len(matrix) != len(offsets):
        raise ValueError("one offset per row is required")
    return tuple(
        rational_link(dot(row, reward) + q(offset))
        for row, offset in zip(matrix, offsets)
    )


def scaled_reward_known_numeraire_law(
    matrix: Sequence[Sequence], reward: Sequence, offsets: Sequence, alpha
):
    if len(matrix) != len(offsets):
        raise ValueError("one offset per row is required")
    alpha = q(alpha)
    scaled_reward = tuple(alpha * q(value) for value in reward)
    return tuple(
        rescaled_rational_link(dot(row, scaled_reward) + q(offset), alpha)
        for row, offset in zip(matrix, offsets)
    )


def realize_integer_occupancy_rows(
    matrix: Sequence[Sequence[int]],
) -> tuple[TrajectoryPair, ...]:
    """Realize each integer row as two deterministic feature-emission paths.

    Feature index -1 is a zero-reward padding transition. Each row corresponds
    to one registered initial state whose two actions enter disjoint paths.
    """
    if not matrix:
        raise ValueError("measurement matrix must be nonempty")
    width = len(matrix[0])
    if width == 0 or any(len(row) != width for row in matrix):
        raise ValueError("matrix must be rectangular and nonempty")
    unpadded = []
    for row in matrix:
        if any(not isinstance(value, int) for value in row):
            raise TypeError("finite-MDP construction requires integer rows")
        positive = tuple(
            feature
            for feature, count in enumerate(row)
            for _ in range(max(count, 0))
        )
        negative = tuple(
            feature
            for feature, count in enumerate(row)
            for _ in range(max(-count, 0))
        )
        unpadded.append((positive, negative))
    horizon = max(
        1,
        *(len(path) for pair in unpadded for path in pair),
    )
    pairs = []
    for positive, negative in unpadded:
        pairs.append(
            TrajectoryPair(
                positive + (-1,) * (horizon - len(positive)),
                negative + (-1,) * (horizon - len(negative)),
            )
        )
    return tuple(pairs)


def realize_integer_occupancy_mdp(
    matrix: Sequence[Sequence[int]],
) -> DeterministicFeatureMDP:
    """Build one explicit deterministic finite MDP for all registered rows.

    Each row has one initial state and two available first actions. The actions
    enter disjoint deterministic chains with one shared global horizon. A
    transition emits one registered reward feature, or ``-1`` for zero-reward
    padding. The construction and all action choices are reward-independent.
    """
    pairs = realize_integer_occupancy_rows(matrix)
    feature_count = len(matrix[0])
    transitions: list[DeterministicTransition] = []
    queries: list[OccupancyQuery] = []
    states: set[str] = set()
    for query_index, pair in enumerate(pairs):
        initial_state = f"query-{query_index}:root"
        states.add(initial_state)
        queries.append(
            OccupancyQuery(
                initial_state=initial_state,
                positive_action="positive",
                negative_action="negative",
                horizon=len(pair.positive_path),
            )
        )
        for branch, path in (
            ("positive", pair.positive_path),
            ("negative", pair.negative_path),
        ):
            source = initial_state
            for step, feature in enumerate(path):
                target = f"query-{query_index}:{branch}:{step + 1}"
                action = branch if step == 0 else "continue"
                transitions.append(
                    DeterministicTransition(
                        source_state=source,
                        action=action,
                        target_state=target,
                        feature=feature,
                    )
                )
                states.add(target)
                source = target
    keys = {
        (transition.source_state, transition.action)
        for transition in transitions
    }
    if len(keys) != len(transitions):
        raise RuntimeError("constructed transition system is not deterministic")
    return DeterministicFeatureMDP(
        feature_count=feature_count,
        states=tuple(sorted(states)),
        transitions=tuple(transitions),
        queries=tuple(queries),
    )


def mdp_query_occupancy_difference(
    mdp: DeterministicFeatureMDP, query_index: int
) -> tuple[int, ...]:
    if not 0 <= query_index < len(mdp.queries):
        raise IndexError("query index out of range")
    transition_map = {
        (transition.source_state, transition.action): transition
        for transition in mdp.transitions
    }

    def follow(first_action: str) -> tuple[int, ...]:
        query = mdp.queries[query_index]
        state = query.initial_state
        action = first_action
        occupancy = [0] * mdp.feature_count
        for _ in range(query.horizon):
            transition = transition_map.get((state, action))
            if transition is None:
                raise RuntimeError("registered query path is incomplete")
            if transition.feature >= 0:
                if transition.feature >= mdp.feature_count:
                    raise RuntimeError("transition emits an invalid feature")
                occupancy[transition.feature] += 1
            state = transition.target_state
            action = "continue"
        return tuple(occupancy)

    query = mdp.queries[query_index]
    positive = follow(query.positive_action)
    negative = follow(query.negative_action)
    return tuple(a - b for a, b in zip(positive, negative))


def occupancy_difference(
    pair: TrajectoryPair, feature_count: int
) -> tuple[int, ...]:
    if feature_count <= 0:
        raise ValueError("feature count must be positive")
    result = [0] * feature_count
    for feature in pair.positive_path:
        if feature >= 0:
            result[feature] += 1
    for feature in pair.negative_path:
        if feature >= 0:
            result[feature] -= 1
    return tuple(result)


def calibrated_bisect(
    measurement_value,
    radius,
    tolerance,
) -> tuple[Fraction, int]:
    target = q(measurement_value)
    radius = q(radius)
    tolerance = q(tolerance)
    if radius <= 0 or tolerance <= 0:
        raise ValueError("radius and tolerance must be positive")
    if abs(target) > radius:
        raise ValueError("measurement lies outside numeraire coverage")
    rounds = max(0, ceil(log2(float(radius / tolerance))))
    low, high = -radius, radius
    for step in range(rounds):
        midpoint = (low + high) / 2
        # The calibrated side payment is c=-midpoint.
        sign = (target - midpoint > 0) - (target - midpoint < 0)
        if sign == 0:
            return midpoint, step + 1
        if sign > 0:
            low = midpoint
        else:
            high = midpoint
    return (low + high) / 2, rounds


def adaptive_transcript_law(
    rows: Sequence[Sequence],
    reward: Sequence,
    depth: int,
    policy: Callable[[tuple[int, ...]], int],
    *,
    alpha: Fraction | None = None,
) -> dict[tuple[int, ...], Fraction]:
    """Exact transcript law for a deterministic history-dependent row policy."""
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    distribution: dict[tuple[int, ...], Fraction] = {(): Fraction(1)}
    for _ in range(depth):
        successor: dict[tuple[int, ...], Fraction] = {}
        for history, history_probability in distribution.items():
            row_index = policy(history)
            if not 0 <= row_index < len(rows):
                raise ValueError("adaptive policy selected an invalid row")
            argument = dot(rows[row_index], reward)
            probability = (
                rational_link(argument)
                if alpha is None
                else rescaled_rational_link(argument, alpha)
            )
            successor[history + (1,)] = history_probability * probability
            successor[history + (0,)] = history_probability * (
                1 - probability
            )
        distribution = successor
    return distribution


def rational_rank(matrix: Sequence[Sequence]) -> int:
    rows = [list(map(q, row)) for row in matrix]
    if not rows:
        return 0
    columns = len(rows[0])
    if any(len(row) != columns for row in rows):
        raise ValueError("ragged matrix")
    rank = 0
    for column in range(columns):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for index, row in enumerate(rows):
            if index == rank or row[column] == 0:
                continue
            multiplier = row[column]
            rows[index] = [
                value - multiplier * pivot_entry
                for value, pivot_entry in zip(row, rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def quotient_identifiable(
    measurement: Sequence[Sequence], gauge_basis: Sequence[Sequence]
) -> dict[str, int | bool]:
    if not measurement:
        raise ValueError("measurement matrix must be nonempty")
    parameter_dim = len(measurement[0])
    measurement_rank = rational_rank(measurement)
    gauge_rank = rational_rank(gauge_basis)
    annihilates = all(
        dot(row, gauge) == 0 for row in measurement for gauge in gauge_basis
    )
    exact = annihilates and measurement_rank == parameter_dim - gauge_rank
    return {
        "parameter_dim": parameter_dim,
        "measurement_rank": measurement_rank,
        "gauge_rank": gauge_rank,
        "annihilates_gauge": annihilates,
        "identifiable_modulo_gauge": exact,
    }


def quotient_stability(
    measurement: Sequence[Sequence], quotient_basis: Sequence[Sequence]
) -> dict[str, float | int]:
    matrix = np.asarray(measurement, dtype=float)
    basis = np.asarray(quotient_basis, dtype=float).T
    design = matrix @ basis
    singular = np.linalg.svd(design, compute_uv=False)
    positive = singular[singular > 1e-12]
    sigma_min = float(np.min(positive)) if positive.size else 0.0
    return {
        "quotient_dimension": int(basis.shape[1]),
        "design_rank": int(np.linalg.matrix_rank(design)),
        "sigma_min": sigma_min,
        "amplification": (
            float("inf") if sigma_min == 0.0 else 1.0 / sigma_min
        ),
    }
