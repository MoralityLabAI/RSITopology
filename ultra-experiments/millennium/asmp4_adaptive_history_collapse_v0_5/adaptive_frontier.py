"""Exact finite and asymptotic instruments for adaptive ASMP-4 schedules."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from functools import lru_cache
from math import isqrt
from typing import Any, Iterable, Sequence


PLANS = tuple(range(4))
PLAN_PROBABILITIES = (
    Fraction(1, 2),
    Fraction(1, 4),
    Fraction(1, 8),
    Fraction(1, 8),
)
HUFFMAN_LENGTHS = (1, 2, 3, 3)
BALANCED_LENGTHS = (2, 2, 2, 2)


def _fraction_payload(value: Fraction) -> dict[str, int | float | str]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "exact": str(value),
        "float": float(value),
    }


def is_prefix_free(words: Sequence[str]) -> bool:
    """Return whether distinct binary words form a prefix-free code."""

    return len(set(words)) == len(words) and all(
        not right.startswith(left) for left in words for right in words if left != right
    )


@lru_cache(maxsize=None)
def deadline_codebook_sets(max_length: int = 3) -> tuple[tuple[str, ...], ...]:
    """All unlabelled four-word binary prefix codes within a deadline."""

    if max_length < 2:
        raise ValueError("four binary codewords require max_length at least two")
    words = tuple(
        format(value, f"0{length}b")
        for length in range(1, max_length + 1)
        for value in range(2**length)
    )
    return tuple(
        code
        for code in itertools.combinations(words, len(PLANS))
        if is_prefix_free(code)
    )


@lru_cache(maxsize=None)
def labelled_deadline_codebooks(max_length: int = 3) -> tuple[tuple[str, ...], ...]:
    """All plan labellings of deadline-bounded prefix codes."""

    return tuple(
        labelled
        for code in deadline_codebook_sets(max_length)
        for labelled in itertools.permutations(code)
    )


def observed_prefix(word: str, tick: int) -> str:
    """The synchronous prefix visible by one tick, including completion."""

    if tick < 0:
        raise ValueError("tick must be nonnegative")
    return word[: min(tick, len(word))]


def information_partition(
    codebook: Sequence[str], tick: int
) -> tuple[tuple[int, ...], ...]:
    """Partition plans by the prefix observable at a synchronous tick."""

    groups: dict[str, list[int]] = {}
    for plan, word in enumerate(codebook):
        groups.setdefault(observed_prefix(word, tick), []).append(plan)
    return tuple(sorted(tuple(group) for group in groups.values()))


def reveal_signature(
    codebook: Sequence[str], deadline: int = 3
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Return the plan partitions revealed from tick one to the deadline."""

    return tuple(
        information_partition(codebook, tick) for tick in range(1, deadline + 1)
    )


def partition_refines(
    fine: Sequence[Sequence[int]], coarse: Sequence[Sequence[int]]
) -> bool:
    """Return whether every fine block is contained in one coarse block."""

    coarse_sets = tuple(set(block) for block in coarse)
    return all(any(set(block) <= target for target in coarse_sets) for block in fine)


def causal_signatures(
    read_signature: Sequence[Sequence[Sequence[int]]],
    write_signature: Sequence[Sequence[Sequence[int]]],
) -> bool:
    """Test synchronous no-lag factorization using information partitions."""

    return all(
        partition_refines(read_partition, write_partition)
        for read_partition, write_partition in zip(
            read_signature, write_signature, strict=True
        )
    )


def expected_length(lengths: Sequence[int]) -> Fraction:
    """Expected length under the registered independent four-plan law."""

    if len(lengths) != len(PLAN_PROBABILITIES):
        raise ValueError("one length is required for every registered plan")
    return sum(
        (
            probability * length
            for probability, length in zip(PLAN_PROBABILITIES, lengths, strict=True)
        ),
        start=Fraction(0),
    )


Action = tuple[Fraction, tuple[int, ...]]


def _coordinatewise_action_minima(actions: Iterable[Action]) -> tuple[Action, ...]:
    unique = sorted(set(actions))
    return tuple(
        action
        for action in unique
        if not any(
            other != action
            and other[0] <= action[0]
            and all(
                left <= right for left, right in zip(other[1], action[1], strict=True)
            )
            for other in unique
        )
    )


@lru_cache(maxsize=None)
def adaptive_action_universe() -> dict[str, Any]:
    """Enumerate all deadline actions and their coordinatewise minima."""

    codebooks = labelled_deadline_codebooks()
    read_buckets: dict[
        tuple[tuple[tuple[int, ...], ...], ...],
        dict[Fraction, tuple[str, ...]],
    ] = {}
    write_buckets: dict[
        tuple[tuple[tuple[int, ...], ...], ...],
        dict[tuple[int, ...], tuple[str, ...]],
    ] = {}
    for codebook in codebooks:
        signature = reveal_signature(codebook)
        read_buckets.setdefault(signature, {}).setdefault(
            expected_length(tuple(map(len, codebook))), codebook
        )
        write_buckets.setdefault(signature, {}).setdefault(
            tuple(map(len, codebook)), codebook
        )

    representatives: dict[Action, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    causal_partition_pairs = 0
    for read_signature, read_costs in read_buckets.items():
        for write_signature, write_lengths in write_buckets.items():
            if not causal_signatures(read_signature, write_signature):
                continue
            causal_partition_pairs += 1
            for read_cost, read_codebook in read_costs.items():
                for length_vector, write_codebook in write_lengths.items():
                    representatives.setdefault(
                        (read_cost, length_vector),
                        (read_codebook, write_codebook),
                    )

    actions = tuple(sorted(representatives))
    minima = _coordinatewise_action_minima(actions)
    return {
        "deadline": 3,
        "unlabelled_codebooks": len(deadline_codebook_sets()),
        "labelled_codebooks": len(codebooks),
        "reveal_signatures": len(read_buckets),
        "read_signature_cost_keys": sum(map(len, read_buckets.values())),
        "write_signature_length_keys": sum(map(len, write_buckets.values())),
        "causal_partition_pairs": causal_partition_pairs,
        "action_signatures": actions,
        "coordinatewise_minima": minima,
        "representatives": {action: representatives[action] for action in minima},
    }


def action_universe_report() -> dict[str, Any]:
    """Serialize the complete deadline action census."""

    universe = adaptive_action_universe()
    return {
        "deadline": universe["deadline"],
        "unlabelled_codebooks": universe["unlabelled_codebooks"],
        "labelled_codebooks": universe["labelled_codebooks"],
        "reveal_signatures": universe["reveal_signatures"],
        "read_signature_cost_keys": universe["read_signature_cost_keys"],
        "write_signature_length_keys": universe["write_signature_length_keys"],
        "causal_partition_pairs": universe["causal_partition_pairs"],
        "action_signatures": len(universe["action_signatures"]),
        "coordinatewise_minima": [
            {
                "expected_read_length": _fraction_payload(read_cost),
                "write_length_vector": write_lengths,
                "representative_read_codebook": universe["representatives"][
                    (read_cost, write_lengths)
                ][0],
                "representative_write_codebook": universe["representatives"][
                    (read_cost, write_lengths)
                ][1],
            }
            for read_cost, write_lengths in universe["coordinatewise_minima"]
        ],
        "pass": (
            universe["unlabelled_codebooks"] == 207
            and universe["labelled_codebooks"] == 4968
            and universe["reveal_signatures"] == 27
            and universe["read_signature_cost_keys"] == 121
            and universe["write_signature_length_keys"] == 150
            and universe["causal_partition_pairs"] == 72
            and len(universe["action_signatures"]) == 250
            and len(universe["coordinatewise_minima"]) == 13
        ),
    }


def _child_value(
    values: Sequence[dict[int, Fraction]], blocks: int, budget: int
) -> Fraction | None:
    if budget < 2 * blocks:
        return None
    if blocks == 0:
        return Fraction(0)
    return values[blocks][min(budget, 3 * blocks)]


def adaptive_bellman_report(max_blocks: int = 12) -> dict[str, Any]:
    """Compute the exact history-adaptive finite-horizon Pareto frontier."""

    if max_blocks < 1:
        raise ValueError("max_blocks must be positive")
    actions: tuple[Action, ...] = adaptive_action_universe()["coordinatewise_minima"]
    values: list[dict[int, Fraction]] = [{0: Fraction(0)}]
    policies: list[dict[int, dict[str, Any]]] = [{}]
    horizons = []
    for blocks in range(1, max_blocks + 1):
        horizon_values: dict[int, Fraction] = {}
        horizon_policies: dict[int, dict[str, Any]] = {}
        for budget in range(2 * blocks, 3 * blocks + 1):
            candidates = []
            for action_index, (read_cost, write_lengths) in enumerate(actions):
                child_budgets = tuple(
                    budget - write_length for write_length in write_lengths
                )
                child_values = tuple(
                    _child_value(values, blocks - 1, child_budget)
                    for child_budget in child_budgets
                )
                if any(value is None for value in child_values):
                    continue
                total = read_cost + sum(
                    (
                        probability * value
                        for probability, value in zip(
                            PLAN_PROBABILITIES, child_values, strict=True
                        )
                        if value is not None
                    ),
                    start=Fraction(0),
                )
                candidates.append(
                    (
                        total,
                        action_index,
                        child_budgets,
                    )
                )
            best_value, action_index, child_budgets = min(candidates)
            horizon_values[budget] = best_value
            horizon_policies[budget] = {
                "action_index": action_index,
                "child_budgets": child_budgets,
            }
        values.append(horizon_values)
        policies.append(horizon_policies)
        points = []
        for budget, value in horizon_values.items():
            fixed_schedule_value = Fraction(10 * blocks - budget, 4)
            slack = budget - 2 * blocks
            if slack == 0:
                guard_value = Fraction(2 * blocks)
            else:
                guard_payload = threshold_policy_exact(blocks, slack)[
                    "expected_read_total"
                ]
                guard_value = Fraction(
                    guard_payload["numerator"], guard_payload["denominator"]
                )
            points.append(
                {
                    "worst_write_budget": budget,
                    "minimum_expected_read": _fraction_payload(value),
                    "fixed_schedule_minimum": _fraction_payload(fixed_schedule_value),
                    "strict_adaptive_gain": value < fixed_schedule_value,
                    "guard_policy_value": _fraction_payload(guard_value),
                    "guard_is_bellman_optimal": guard_value == value,
                    "root_action_index": horizon_policies[budget]["action_index"],
                }
            )
        horizons.append(
            {
                "blocks": blocks,
                "frontier_points": points,
                "frontier_size": len(points),
                "strictly_pareto_ordered": all(
                    horizon_values[budget] > horizon_values[budget + 1]
                    for budget in range(2 * blocks, 3 * blocks)
                ),
                "zero_slack_value": _fraction_payload(horizon_values[2 * blocks]),
                "all_huffman_value": _fraction_payload(horizon_values[3 * blocks]),
                "all_interior_points_beat_fixed_schedules": all(
                    point["strict_adaptive_gain"] for point in points[1:-1]
                ),
                "guard_is_optimal_at_every_budget": all(
                    point["guard_is_bellman_optimal"] for point in points
                ),
            }
        )

    return {
        "recurrence": ("V_n(b)=min_a[r(a)+sum_i p_i V_{n-1}(b-w_i(a))]"),
        "infeasible_below": "b<2n",
        "actions_used": len(actions),
        "horizons": horizons,
        "two_block_middle_value": _fraction_payload(values[2][5])
        if max_blocks >= 2
        else None,
        "pass": (
            len(actions) == 13
            and all(row["frontier_size"] == row["blocks"] + 1 for row in horizons)
            and all(row["strictly_pareto_ordered"] for row in horizons)
            and all(
                row["zero_slack_value"]["exact"] == str(2 * row["blocks"])
                for row in horizons
            )
            and all(
                Fraction(
                    row["all_huffman_value"]["numerator"],
                    row["all_huffman_value"]["denominator"],
                )
                == Fraction(7 * row["blocks"], 4)
                for row in horizons
            )
            and all(row["all_interior_points_beat_fixed_schedules"] for row in horizons)
            and all(row["guard_is_optimal_at_every_budget"] for row in horizons)
            and (max_blocks < 2 or values[2][5] == Fraction(57, 16))
        ),
    }


def two_block_adaptive_witness_report() -> dict[str, Any]:
    """Replay the smallest strict improvement over every fixed schedule."""

    rows = []
    expected_read = Fraction(0)
    worst_write = 0
    for first_plan in PLANS:
        second_lengths = HUFFMAN_LENGTHS if first_plan in (0, 1) else BALANCED_LENGTHS
        second_format = "huffman" if first_plan in (0, 1) else "balanced"
        for second_plan in PLANS:
            probability = (
                PLAN_PROBABILITIES[first_plan] * PLAN_PROBABILITIES[second_plan]
            )
            read_total = HUFFMAN_LENGTHS[first_plan] + second_lengths[second_plan]
            write_total = read_total
            expected_read += probability * read_total
            worst_write = max(worst_write, write_total)
            rows.append(
                {
                    "plans": (first_plan, second_plan),
                    "probability": str(probability),
                    "second_format": second_format,
                    "read_total": read_total,
                    "write_total": write_total,
                }
            )
    fixed_schedule_minimum = Fraction(15, 4)
    return {
        "policy": (
            "Huffman first; Huffman after plans 0 or 1; balanced after plans 2 or 3"
        ),
        "histories_replayed": len(rows),
        "expected_read_total": _fraction_payload(expected_read),
        "worst_write_total": worst_write,
        "fixed_schedule_minimum_at_write_five": _fraction_payload(
            fixed_schedule_minimum
        ),
        "strict_read_gain": _fraction_payload(fixed_schedule_minimum - expected_read),
        "rows": rows,
        "pass": (
            len(rows) == 16
            and expected_read == Fraction(57, 16)
            and worst_write == 5
            and fixed_schedule_minimum - expected_read == Fraction(3, 16)
        ),
    }


def exhaustive_two_block_strategy_report() -> dict[str, Any]:
    """Enumerate every two-block tree over the 13 minimal action signatures."""

    actions: tuple[Action, ...] = adaptive_action_universe()["coordinatewise_minima"]
    scaled_actions = tuple(
        (int(8 * read_cost), write_lengths) for read_cost, write_lengths in actions
    )
    child_profiles = tuple(
        (
            4 * first[0] + 2 * second[0] + third[0] + fourth[0],
            tuple(max(action[1]) for action in (first, second, third, fourth)),
        )
        for first, second, third, fourth in itertools.product(scaled_actions, repeat=4)
    )
    point_counts: dict[tuple[int, int], int] = {}
    for root_read, root_writes in scaled_actions:
        for child_read, child_worsts in child_profiles:
            read_numerator_64 = 8 * root_read + child_read
            write_worst = max(
                root_length + child_worst
                for root_length, child_worst in zip(
                    root_writes, child_worsts, strict=True
                )
            )
            point = (read_numerator_64, write_worst)
            point_counts[point] = point_counts.get(point, 0) + 1
    minima = tuple(
        point
        for point in sorted(point_counts)
        if not any(
            other != point and other[0] <= point[0] and other[1] <= point[1]
            for other in point_counts
        )
    )
    return {
        "action_signatures": len(actions),
        "strategy_trees": len(actions) ** 5,
        "aggregate_cost_points": len(point_counts),
        "pareto_minima": [
            {
                "expected_read_total": _fraction_payload(Fraction(read_numerator, 64)),
                "worst_write_total": write_worst,
                "strategy_signatures": point_counts[(read_numerator, write_worst)],
            }
            for read_numerator, write_worst in minima
        ],
        "pass": (
            len(actions) ** 5 == 371293
            and len(point_counts) == 188
            and minima == ((224, 6), (228, 5), (256, 4))
            and all(point_counts[point] == 1 for point in minima)
        ),
    }


def threshold_policy_exact(blocks: int, slack: int) -> dict[str, Any]:
    """Evaluate the guarded Huffman policy by an exact state distribution."""

    if blocks < 1:
        raise ValueError("blocks must be positive")
    if not 1 <= slack <= blocks:
        raise ValueError("slack must lie between one and blocks")

    active = {0: Fraction(1)}
    stopped_probability = Fraction(0)
    expected_read_total = Fraction(0)
    increment_law = {
        -1: Fraction(1, 2),
        0: Fraction(1, 4),
        1: Fraction(1, 4),
    }
    for _ in range(blocks):
        active_probability = sum(active.values(), start=Fraction(0))
        expected_read_total += (
            Fraction(7, 4) * active_probability + Fraction(2) * stopped_probability
        )
        next_active: dict[int, Fraction] = {}
        next_stopped = stopped_probability
        for surplus, state_probability in active.items():
            for increment, increment_probability in increment_law.items():
                next_surplus = surplus + increment
                mass = state_probability * increment_probability
                if next_surplus == slack:
                    next_stopped += mass
                else:
                    next_active[next_surplus] = (
                        next_active.get(next_surplus, Fraction(0)) + mass
                    )
        active = next_active
        stopped_probability = next_stopped

    hitting_bound = Fraction(1, 2**slack)
    read_bound = Fraction(7, 4) * blocks + Fraction(blocks, 4 * 2**slack)
    return {
        "blocks": blocks,
        "slack": slack,
        "worst_write_total": 2 * blocks + slack,
        "expected_read_total": _fraction_payload(expected_read_total),
        "expected_read_per_block": _fraction_payload(expected_read_total / blocks),
        "hitting_probability": _fraction_payload(stopped_probability),
        "doob_hitting_bound": _fraction_payload(hitting_bound),
        "read_upper_bound": _fraction_payload(read_bound),
        "write_per_block_upper_bound": _fraction_payload(
            Fraction(2 * blocks + slack, blocks)
        ),
        "bounds_hold": (
            stopped_probability <= hitting_bound and expected_read_total <= read_bound
        ),
    }


def logarithmic_slack_report(max_blocks: int = 64) -> dict[str, Any]:
    """Certify the sublinear-slack sequence that attains the lower corner."""

    if max_blocks < 2:
        raise ValueError("max_blocks must be at least two")
    selected = tuple(blocks for blocks in (2, 4, 8, 16, 32, 64) if blocks <= max_blocks)
    rows = []
    for blocks in selected:
        slack = (blocks - 1).bit_length()
        row = threshold_policy_exact(blocks, slack)
        row["ceil_log2_blocks"] = slack
        row["normalized_read_excess_bound"] = _fraction_payload(Fraction(1, 4 * blocks))
        row["normalized_write_excess"] = _fraction_payload(Fraction(slack, blocks))
        rows.append(row)
    martingale_factor = sum(
        (
            probability * Fraction(2) ** increment
            for increment, probability in (
                (-1, Fraction(1, 2)),
                (0, Fraction(1, 4)),
                (1, Fraction(1, 4)),
            )
        ),
        start=Fraction(0),
    )
    return {
        "surplus_increment_law": {"-1": "1/2", "0": "1/4", "+1": "1/4"},
        "mean_surplus_increment": "-1/4",
        "exponential_martingale": "M_t=2^{S_t}",
        "martingale_factor": str(martingale_factor),
        "slack_sequence": "k_n=ceil(log2 n)",
        "read_rate_limit_per_block": "7/4",
        "write_rate_limit_per_block": "2",
        "read_rate_limit_per_tick": "7/12",
        "write_rate_limit_per_tick": "2/3",
        "rows": rows,
        "pass": (
            martingale_factor == 1
            and all(row["bounds_hold"] for row in rows)
            and all(
                Fraction(
                    row["normalized_read_excess_bound"]["numerator"],
                    row["normalized_read_excess_bound"]["denominator"],
                )
                == Fraction(1, 4 * row["blocks"])
                for row in rows
            )
        ),
    }


def ordered_probability_laws(total_mass: int = 16) -> tuple[tuple[int, ...], ...]:
    """Positive nonincreasing four-part laws on one rational grid."""

    if total_mass < 4:
        raise ValueError("total_mass must permit four positive atoms")
    laws = []
    for first in range(1, total_mass):
        for second in range(1, first + 1):
            for third in range(1, second + 1):
                fourth = total_mass - first - second - third
                if 1 <= fourth <= third:
                    laws.append((first, second, third, fourth))
    return tuple(laws)


def general_probability_phase_report(total_mass: int = 16) -> dict[str, Any]:
    """Check the adaptive rectangle theorem across the four-plan phase map."""

    rows = []
    for masses in ordered_probability_laws(total_mass):
        probabilities = tuple(Fraction(mass, total_mass) for mass in masses)
        first, second, third, fourth = probabilities
        tail = third + fourth
        huffman_expected = 3 - 2 * first - second
        skew = huffman_expected < 2
        boundary = huffman_expected == 2
        multiplier = first / tail if skew else None
        martingale_factor = (
            first / multiplier + second + tail * multiplier
            if multiplier is not None
            else None
        )
        mean_increment = huffman_expected - 2
        optimal_read = min(huffman_expected, Fraction(2))
        rows.append(
            {
                "masses": masses,
                "probabilities": [str(value) for value in probabilities],
                "phase": "skew" if skew else "boundary" if boundary else "balanced",
                "huffman_expected": str(huffman_expected),
                "mean_surplus_increment": str(mean_increment),
                "exponential_multiplier": (
                    None if multiplier is None else str(multiplier)
                ),
                "martingale_factor": (
                    None if martingale_factor is None else str(martingale_factor)
                ),
                "adaptive_rectangle_per_block": [str(optimal_read), "2"],
                "matches": (
                    (
                        multiplier is not None
                        and multiplier > 1
                        and martingale_factor == 1
                        and mean_increment < 0
                        and 2 * first + second > 1
                    )
                    if skew
                    else (
                        optimal_read == 2
                        and mean_increment >= 0
                        and 2 * first + second <= 1
                    )
                ),
            }
        )
    return {
        "total_mass": total_mass,
        "laws": len(rows),
        "skew_laws": sum(row["phase"] == "skew" for row in rows),
        "boundary_laws": sum(row["phase"] == "boundary" for row in rows),
        "balanced_laws": sum(row["phase"] == "balanced" for row in rows),
        "strict_skew_multiplier": "lambda=p_1/(p_3+p_4)",
        "strict_skew_read_bound": ("E_H*n + (2-E_H)*n*lambda^{-k}"),
        "rows": rows,
        "pass": all(row["matches"] for row in rows),
    }


@lru_cache(maxsize=None)
def full_binary_length_profiles(leaves: int) -> tuple[tuple[int, ...], ...]:
    """All sorted leaf-depth profiles of full binary trees."""

    if leaves < 1:
        raise ValueError("a prefix tree must have at least one leaf")
    if leaves == 1:
        return ((0,),)
    profiles = set()
    for left_leaves in range(1, leaves):
        for left in full_binary_length_profiles(left_leaves):
            for right in full_binary_length_profiles(leaves - left_leaves):
                profiles.add(
                    tuple(
                        sorted(
                            tuple(depth + 1 for depth in left)
                            + tuple(depth + 1 for depth in right)
                        )
                    )
                )
    return tuple(sorted(profiles))


@lru_cache(maxsize=None)
def labelled_full_tree_length_vectors(leaves: int) -> tuple[tuple[int, ...], ...]:
    """All labelled leaf-depth vectors of full binary trees."""

    return tuple(
        sorted(
            {
                labelled
                for profile in full_binary_length_profiles(leaves)
                for labelled in itertools.permutations(profile)
            }
        )
    )


def ordered_mass_laws(atoms: int, total_mass: int) -> tuple[tuple[int, ...], ...]:
    """Positive nonincreasing integer laws of a requested size and mass."""

    if atoms < 1 or total_mass < atoms:
        raise ValueError("total_mass must support the requested positive atoms")
    laws = []

    def extend(
        remaining: int, count: int, maximum: int, prefix: tuple[int, ...]
    ) -> None:
        if count == 0:
            if remaining == 0:
                laws.append(prefix)
            return
        upper = min(maximum, remaining - count + 1)
        for value in range(upper, 0, -1):
            residual = remaining - value
            if count - 1 <= residual <= value * (count - 1):
                extend(residual, count - 1, value, prefix + (value,))

    extend(total_mass, atoms, total_mass, ())
    return tuple(laws)


def _supermartingale_multiplier(
    probabilities: Sequence[Fraction], lengths: Sequence[int], baseline: int
) -> tuple[Fraction, Fraction]:
    """Find an exact rational multiplier with a strict length MGF decrease."""

    mean_surplus = sum(
        (
            probability * (length - baseline)
            for probability, length in zip(probabilities, lengths, strict=True)
        ),
        start=Fraction(0),
    )
    if mean_surplus >= 0 or max(lengths) <= baseline:
        raise ValueError("a guarded multiplier requires negative drift and overshoot")
    for power in range(1, 65):
        multiplier = 1 + Fraction(1, 2**power)
        factor = sum(
            (
                probability * multiplier ** (length - baseline)
                for probability, length in zip(probabilities, lengths, strict=True)
            ),
            start=Fraction(0),
        )
        if factor < 1:
            return multiplier, factor
    raise AssertionError("negative drift yielded no local supermartingale multiplier")


def finite_iid_alphabet_report(
    total_mass: int = 12, max_plans: int = 6
) -> dict[str, Any]:
    """Audit the general finite-i.i.d.-alphabet adaptive rectangle theorem."""

    if max_plans < 2:
        raise ValueError("max_plans must be at least two")
    rows = []
    profile_counts = {}
    for plans in range(2, max_plans + 1):
        profiles = full_binary_length_profiles(plans)
        profile_counts[plans] = len(profiles)
        fixed_worst = (plans - 1).bit_length()
        for masses in ordered_mass_laws(plans, total_mass):
            probabilities = tuple(Fraction(mass, total_mass) for mass in masses)
            optimal_expected, optimal_lengths = min(
                (
                    sum(
                        (
                            probability * length
                            for probability, length in zip(
                                probabilities, profile, strict=True
                            )
                        ),
                        start=Fraction(0),
                    ),
                    profile,
                )
                for profile in profiles
            )
            mean_surplus = optimal_expected - fixed_worst
            maximum_surplus = max(optimal_lengths) - fixed_worst
            if optimal_expected == fixed_worst:
                mode = "fixed_equal"
                multiplier = None
                factor = None
                valid = mean_surplus == 0
            elif maximum_surplus <= 0:
                mode = "direct"
                multiplier = None
                factor = None
                valid = optimal_expected < fixed_worst
            else:
                mode = "guard"
                multiplier, factor = _supermartingale_multiplier(
                    probabilities, optimal_lengths, fixed_worst
                )
                valid = (
                    mean_surplus < 0
                    and multiplier > 1
                    and factor < 1
                    and maximum_surplus > 0
                )
            rows.append(
                {
                    "plans": plans,
                    "masses": masses,
                    "probabilities": [str(value) for value in probabilities],
                    "optimal_expected_length": str(optimal_expected),
                    "minimum_worst_length": fixed_worst,
                    "optimal_length_profile": optimal_lengths,
                    "registered_block_deadline": max(fixed_worst, max(optimal_lengths)),
                    "mean_surplus": str(mean_surplus),
                    "maximum_surplus": maximum_surplus,
                    "construction": mode,
                    "supermartingale_multiplier": (
                        None if multiplier is None else str(multiplier)
                    ),
                    "supermartingale_factor": (None if factor is None else str(factor)),
                    "adaptive_rectangle_per_block": [
                        str(optimal_expected),
                        str(fixed_worst),
                    ],
                    "matches": valid,
                }
            )
    modes = {
        mode: sum(row["construction"] == mode for row in rows)
        for mode in ("fixed_equal", "direct", "guard")
    }
    return {
        "total_mass": total_mass,
        "plan_range": [2, max_plans],
        "profile_counts": profile_counts,
        "laws": len(rows),
        "construction_counts": modes,
        "theorem": (
            "closed adaptive region per block is [mu,infinity) x "
            "[ceil(log2 m),infinity)"
        ),
        "rows": rows,
        "pass": all(row["matches"] for row in rows),
    }


def markov_common_history_guard_report(
    blocks: int = 32, slack: int = 5
) -> dict[str, Any]:
    """Verify a correlated Markov source under a uniform conditional MGF guard."""

    if blocks < 1 or not 1 <= slack <= blocks:
        raise ValueError("require blocks>=1 and 1<=slack<=blocks")
    transition_rows = []
    for state in PLANS:
        row = tuple(
            {
                "plan": (state + offset) % len(PLANS),
                "probability": PLAN_PROBABILITIES[offset],
                "huffman_length": HUFFMAN_LENGTHS[offset],
            }
            for offset in PLANS
        )
        transition_rows.append(row)

    active: dict[tuple[int, int], Fraction] = {(0, 0): Fraction(1)}
    stopped = Fraction(0)
    expected_read = Fraction(0)
    for _ in range(blocks):
        active_mass = sum(active.values(), start=Fraction(0))
        expected_read += Fraction(7, 4) * active_mass + 2 * stopped
        next_active: dict[tuple[int, int], Fraction] = {}
        next_stopped = stopped
        for (state, surplus), state_mass in active.items():
            for transition in transition_rows[state]:
                plan = transition["plan"]
                probability = transition["probability"]
                length = transition["huffman_length"]
                target_surplus = surplus + length - 2
                mass = state_mass * probability
                if target_surplus == slack:
                    next_stopped += mass
                else:
                    key = (plan, target_surplus)
                    next_active[key] = next_active.get(key, Fraction(0)) + mass
        active = next_active
        stopped = next_stopped

    conditional_mgf_rows = []
    for state, row in enumerate(transition_rows):
        factor = sum(
            (
                transition["probability"]
                * Fraction(2) ** (transition["huffman_length"] - 2)
                for transition in row
            ),
            start=Fraction(0),
        )
        conditional_mgf_rows.append(
            {"state": state, "lambda": "2", "conditional_factor": str(factor)}
        )

    iid_guard = threshold_policy_exact(blocks, slack)
    iid_expected = Fraction(
        iid_guard["expected_read_total"]["numerator"],
        iid_guard["expected_read_total"]["denominator"],
    )
    iid_stopped = Fraction(
        iid_guard["hitting_probability"]["numerator"],
        iid_guard["hitting_probability"]["denominator"],
    )
    return {
        "source": "four-state first-order Markov chain",
        "initial_state": 0,
        "transition_rows": [
            [
                {
                    "plan": transition["plan"],
                    "probability": str(transition["probability"]),
                    "huffman_length": transition["huffman_length"],
                }
                for transition in row
            ]
            for row in transition_rows
        ],
        "correlation_witness": {
            "P_next_0_given_0": "1/2",
            "P_next_0_given_1": "1/8",
        },
        "conditional_mgf_rows": conditional_mgf_rows,
        "blocks": blocks,
        "slack": slack,
        "worst_write_total": 2 * blocks + slack,
        "expected_read_total": _fraction_payload(expected_read),
        "guard_hit_probability": _fraction_payload(stopped),
        "matches_iid_length_process": (
            expected_read == iid_expected and stopped == iid_stopped
        ),
        "pass": (
            all(row["conditional_factor"] == "1" for row in conditional_mgf_rows)
            and expected_read == iid_expected
            and stopped == iid_stopped
            and stopped <= Fraction(1, 2**slack)
        ),
    }


def nonuniform_negative_drift_law(round_index: int) -> tuple[Fraction, ...]:
    """Time-varying four-plan law with no uniform one-step MGF multiplier."""

    if round_index < 0:
        raise ValueError("round_index must be nonnegative")
    if round_index % 2 == 0:
        return PLAN_PROBABILITIES
    weak_index = (round_index - 1) // 2
    epsilon = Fraction(1, 2 ** (weak_index + 4))
    return (
        Fraction(3, 8) + epsilon / 2,
        Fraction(1, 4),
        Fraction(3, 16) - epsilon / 4,
        Fraction(3, 16) - epsilon / 4,
    )


def vanishing_maximum_guard_report(
    horizons: Sequence[int] = (16, 32, 64, 128),
) -> dict[str, Any]:
    """Exact guard replay beyond the uniform conditional-MGF hypothesis."""

    if not horizons or any(blocks < 1 for blocks in horizons):
        raise ValueError("horizons must be a nonempty sequence of positive integers")
    rows = []
    for blocks in horizons:
        slack = isqrt(blocks - 1) + 1
        active: dict[int, Fraction] = {0: Fraction(1)}
        stopped = Fraction(0)
        guarded_read = Fraction(0)
        fast_read = Fraction(0)
        laws_valid = True
        for round_index in range(blocks):
            probabilities = nonuniform_negative_drift_law(round_index)
            laws_valid &= (
                sum(probabilities, start=Fraction(0)) == 1
                and all(value > 0 for value in probabilities)
                and tuple(sorted(probabilities, reverse=True)) == probabilities
            )
            fast_read += sum(
                (
                    probability * length
                    for probability, length in zip(
                        probabilities, HUFFMAN_LENGTHS, strict=True
                    )
                ),
                start=Fraction(0),
            )
            guarded_read += 2 * stopped
            next_active: dict[int, Fraction] = {}
            next_stopped = stopped
            for surplus, state_mass in active.items():
                for probability, length in zip(
                    probabilities, HUFFMAN_LENGTHS, strict=True
                ):
                    mass = state_mass * probability
                    guarded_read += mass * length
                    target = surplus + length - 2
                    if target >= slack:
                        next_stopped += mass
                    else:
                        next_active[target] = (
                            next_active.get(target, Fraction(0)) + mass
                        )
            active = next_active
            stopped = next_stopped

        expected_fast_formula = None
        if blocks % 2 == 0:
            expected_fast_formula = Fraction(15 * blocks, 8) - Fraction(1, 8) * (
                1 - Fraction(1, 2 ** (blocks // 2))
            )
        rows.append(
            {
                "blocks": blocks,
                "slack": slack,
                "worst_write_total": 2 * blocks + slack,
                "fast_read_total": _fraction_payload(fast_read),
                "guarded_read_total": _fraction_payload(guarded_read),
                "guard_hit_probability": _fraction_payload(stopped),
                "guarded_read_rate": _fraction_payload(guarded_read / blocks),
                "laws_valid": laws_valid,
                "fast_total_formula_matches": (
                    expected_fast_formula is None or fast_read == expected_fast_formula
                ),
                "coupling_bound_holds": (
                    guarded_read <= fast_read + 2 * blocks * stopped
                ),
            }
        )

    strong_factor_at_two = sum(
        (
            probability * Fraction(2) ** (length - 2)
            for probability, length in zip(
                nonuniform_negative_drift_law(0), HUFFMAN_LENGTHS, strict=True
            )
        ),
        start=Fraction(0),
    )
    sampled_weak_factors = []
    for weak_index in range(max(horizons) // 2):
        round_index = 2 * weak_index + 1
        factor = sum(
            (
                probability * Fraction(2) ** (length - 2)
                for probability, length in zip(
                    nonuniform_negative_drift_law(round_index),
                    HUFFMAN_LENGTHS,
                    strict=True,
                )
            ),
            start=Fraction(0),
        )
        sampled_weak_factors.append(factor)
    hit_probabilities = [
        Fraction(
            row["guard_hit_probability"]["numerator"],
            row["guard_hit_probability"]["denominator"],
        )
        for row in rows
    ]
    return {
        "source": "independent public time-varying four-plan process",
        "strong_round_drift": "-1/4",
        "weak_round_drift": "-epsilon_j with epsilon_j=2^(-(j+4))",
        "strong_law_surplus_rate": "-1/8",
        "fast_read_rate_limit": "15/8",
        "write_rate_limit": "2",
        "threshold": "ceil(sqrt(n))",
        "strong_conditional_factor_at_lambda_2": str(strong_factor_at_two),
        "weak_boundary_factor_at_lambda_2": "19/16",
        "sampled_weak_factors_at_lambda_2": [
            str(value) for value in sampled_weak_factors
        ],
        "uniform_one_step_mgf_hypothesis_holds": False,
        "rows": rows,
        "pass": (
            strong_factor_at_two == 1
            and all(value > 1 for value in sampled_weak_factors)
            and all(row["laws_valid"] for row in rows)
            and all(row["fast_total_formula_matches"] for row in rows)
            and all(row["coupling_bound_holds"] for row in rows)
            and all(
                left > right
                for left, right in zip(hit_probabilities, hit_probabilities[1:])
            )
        ),
    }


def stationary_renewal_source_report(cutoff: int = 32) -> dict[str, Any]:
    """Certify a stationary ergodic separator from the uniform-MGF theorem."""

    if cutoff < 2:
        raise ValueError("cutoff must be at least two")
    weight = Fraction(1)
    normalizer_prefix = Fraction(0)
    drift_numerator_prefix = Fraction(0)
    minimum_reset = Fraction(1)
    advance_positive = True
    huffman_optimal = True
    weak_factors_at_two = []
    sample_rows = []
    for state in range(cutoff):
        probabilities = nonuniform_negative_drift_law(state)
        expected_length = sum(
            (
                probability * length
                for probability, length in zip(
                    probabilities, HUFFMAN_LENGTHS, strict=True
                )
            ),
            start=Fraction(0),
        )
        drift = expected_length - 2
        reset_probability = probabilities[0]
        factor_at_two = sum(
            (
                probability * Fraction(2) ** (length - 2)
                for probability, length in zip(
                    probabilities, HUFFMAN_LENGTHS, strict=True
                )
            ),
            start=Fraction(0),
        )
        normalizer_prefix += weight
        drift_numerator_prefix += weight * drift
        minimum_reset = min(minimum_reset, reset_probability)
        advance_positive &= 1 - reset_probability > 0
        huffman_optimal &= 2 * probabilities[0] + probabilities[1] > 1
        if state % 2 == 1:
            weak_factors_at_two.append(factor_at_two)
        if state < 4 or state >= cutoff - 2:
            sample_rows.append(
                {
                    "state": state,
                    "stationary_weight_unnormalized": str(weight),
                    "reset_probability": str(reset_probability),
                    "surplus_drift": str(drift),
                    "conditional_factor_at_lambda_2": str(factor_at_two),
                }
            )
        weight *= 1 - reset_probability

    tail_weight_bound = Fraction(8, 3) * weight
    normalizer_lower = normalizer_prefix
    normalizer_upper = normalizer_prefix + tail_weight_bound
    drift_lower = (drift_numerator_prefix - tail_weight_bound / 4) / normalizer_lower
    drift_upper = drift_numerator_prefix / normalizer_upper
    read_lower = 2 + drift_lower
    read_upper = 2 + drift_upper
    pi_zero_lower = 1 / normalizer_upper
    pi_zero_upper = 1 / normalizer_lower
    state_zero_self_loop = nonuniform_negative_drift_law(0)[0]
    irreducible = minimum_reset > 0 and advance_positive
    aperiodic = state_zero_self_loop > 0
    positive_recurrent = minimum_reset >= Fraction(3, 8)
    return {
        "source": "observable countable-state renewal Markov source",
        "state_update": "reset to 0 on plan 0; otherwise increment age",
        "initial_state": 0,
        "stationary_initialization": (
            "pi; state-zero initialization has the same asymptotic rates"
        ),
        "cutoff": cutoff,
        "uniform_reset_probability_lower_bound": "3/8",
        "minimum_sampled_reset_probability": str(minimum_reset),
        "state_zero_self_loop_probability": str(state_zero_self_loop),
        "irreducible": irreducible,
        "aperiodic": aperiodic,
        "positive_recurrent": positive_recurrent,
        "conditional_huffman_optimal": huffman_optimal,
        "uniform_one_step_mgf_hypothesis_holds": False,
        "weak_factor_limit_at_lambda_2": "19/16",
        "sampled_weak_factors_at_lambda_2": [
            str(value) for value in weak_factors_at_two
        ],
        "stationary_tail_weight_bound": _fraction_payload(tail_weight_bound),
        "stationary_pi_zero_interval": {
            "lower": _fraction_payload(pi_zero_lower),
            "upper": _fraction_payload(pi_zero_upper),
        },
        "stationary_surplus_rate_interval": {
            "lower": _fraction_payload(drift_lower),
            "upper": _fraction_payload(drift_upper),
        },
        "stationary_read_rate_interval": {
            "lower": _fraction_payload(read_lower),
            "upper": _fraction_payload(read_upper),
        },
        "write_rate_limit": "2",
        "sample_states": sample_rows,
        "pass": (
            minimum_reset >= Fraction(3, 8)
            and irreducible
            and aperiodic
            and positive_recurrent
            and huffman_optimal
            and all(value > 1 for value in weak_factors_at_two)
            and tail_weight_bound < Fraction(1, 10**7)
            and Fraction(-1, 4) < drift_lower <= drift_upper < 0
            and read_lower <= read_upper < 2
            and read_upper - read_lower < Fraction(1, 10**8)
            and pi_zero_lower >= Fraction(3, 8)
        ),
    }


def stationary_predictor_rectangle_report(
    max_plans: int = 8, renewal_report: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Audit the finite-alphabet ingredients of the stationary predictor theorem."""

    if max_plans < 2:
        raise ValueError("max_plans must be at least two")
    profile_rows = []
    for plans in range(2, max_plans + 1):
        profiles = full_binary_length_profiles(plans)
        fixed_worst = (plans - 1).bit_length()
        fixed_words = tuple(format(value, f"0{fixed_worst}b") for value in range(plans))
        profile_rows.append(
            {
                "plans": plans,
                "profile_count": len(profiles),
                "minimum_profile_worst_length": min(
                    max(profile) for profile in profiles
                ),
                "maximum_profile_depth": max(max(profile) for profile in profiles),
                "fixed_worst_length": fixed_worst,
                "fixed_code_prefix_free": is_prefix_free(fixed_words),
                "huffman_depth_bound": all(
                    max(profile) <= plans - 1 for profile in profiles
                ),
            }
        )
    renewal = (
        stationary_renewal_source_report() if renewal_report is None else renewal_report
    )
    fixtures = [
        {
            "source": "registered four-plan i.i.d.",
            "read_threshold": "7/4",
            "write_threshold": "2",
            "mode": "negative_drift_guard",
        },
        {
            "source": "rotating-Huffman four-state Markov",
            "read_threshold": "7/4",
            "write_threshold": "2",
            "mode": "uniform_mgf_guard",
        },
        {
            "source": "renewal-age stationary ergodic",
            "read_threshold_interval": [
                renewal["stationary_read_rate_interval"]["lower"]["float"],
                renewal["stationary_read_rate_interval"]["upper"]["float"],
            ],
            "write_threshold": "2",
            "mode": "vanishing_maximum_guard",
        },
        {
            "source": "uniform four-plan i.i.d.",
            "read_threshold": "2",
            "write_threshold": "2",
            "mode": "fixed_equal",
        },
    ]
    return {
        "theorem_scope": (
            "stationary ergodic finite full-support plan sources with a "
            "common sufficient predictive state"
        ),
        "plan_range": [2, max_plans],
        "profile_counts": {row["plans"]: row["profile_count"] for row in profile_rows},
        "profile_rows": profile_rows,
        "fixtures": fixtures,
        "closed_region": "[h_H,infinity) x [ceil(log2 m),infinity)",
        "pass": (
            renewal["pass"]
            and all(
                row["minimum_profile_worst_length"] == row["fixed_worst_length"]
                and row["fixed_code_prefix_free"]
                and row["huffman_depth_bound"]
                for row in profile_rows
            )
        ),
    }


def variable_support_mean_payoff_report(
    blocks: int = 64, slack: int = 5
) -> dict[str, Any]:
    """Exact two-state variable-support mean-payoff coding fixture."""

    if blocks < 2 or blocks % 2 or slack < 1:
        raise ValueError("require a positive even block count and positive slack")
    four_plan_actions = labelled_full_tree_length_vectors(4)
    policy_rows = []
    for lengths in four_plan_actions:
        cycle_mean = Fraction(max(lengths) + 1, 2)
        expected_write = Fraction(1, 2) * (
            sum(
                (
                    probability * length
                    for probability, length in zip(
                        PLAN_PROBABILITIES, lengths, strict=True
                    )
                ),
                start=Fraction(0),
            )
            + 1
        )
        policy_rows.append(
            {
                "state_a_lengths": lengths,
                "state_b_lengths": (1, 1),
                "maximum_cycle_mean": str(cycle_mean),
                "stationary_expected_length": str(expected_write),
            }
        )
    write_value = min(Fraction(row["maximum_cycle_mean"]) for row in policy_rows)
    optimal_rows = [
        row for row in policy_rows if Fraction(row["maximum_cycle_mean"]) == write_value
    ]
    value_counts = {
        str(value): sum(
            Fraction(row["maximum_cycle_mean"]) == value for row in policy_rows
        )
        for value in sorted(
            {Fraction(row["maximum_cycle_mean"]) for row in policy_rows}
        )
    }

    active: dict[int, Fraction] = {0: Fraction(1)}
    stopped = Fraction(0)
    guarded_read = Fraction(0)
    for round_index in range(blocks):
        if round_index % 2 == 1:
            guarded_read += 1
            continue
        active_mass = sum(active.values(), start=Fraction(0))
        guarded_read += Fraction(7, 4) * active_mass + 2 * stopped
        next_active: dict[int, Fraction] = {}
        next_stopped = stopped
        for surplus, state_mass in active.items():
            for probability, length in zip(
                PLAN_PROBABILITIES, HUFFMAN_LENGTHS, strict=True
            ):
                mass = state_mass * probability
                target = surplus + length - 2
                if target >= slack:
                    next_stopped += mass
                else:
                    next_active[target] = next_active.get(target, Fraction(0)) + mass
        active = next_active
        stopped = next_stopped

    reference_guard = threshold_policy_exact(blocks // 2, slack)
    reference_hit = Fraction(
        reference_guard["hitting_probability"]["numerator"],
        reference_guard["hitting_probability"]["denominator"],
    )
    fast_read = Fraction(11 * blocks, 8)
    baseline_worst = Fraction(3 * blocks, 2)
    return {
        "source": "alternating four-plan/two-plan public predictor",
        "state_graph": "A->B->A",
        "state_a_probabilities": [str(value) for value in PLAN_PROBABILITIES],
        "state_b_probabilities": ["3/4", "1/4"],
        "write_policy_count": len(policy_rows),
        "write_value_counts": value_counts,
        "optimal_write_policy_count": len(optimal_rows),
        "optimal_write_policy": optimal_rows[0],
        "read_threshold": "11/8",
        "write_threshold": "3/2",
        "fast_minus_baseline_stationary_drift": "-1/8",
        "closed_region": "[11/8,infinity) x [3/2,infinity)",
        "guard_replay": {
            "blocks": blocks,
            "slack": slack,
            "fast_read_total": _fraction_payload(fast_read),
            "guarded_read_total": _fraction_payload(guarded_read),
            "baseline_worst_write_total": _fraction_payload(baseline_worst),
            "guarded_worst_write_total": _fraction_payload(baseline_worst + slack),
            "hit_probability": _fraction_payload(stopped),
            "matches_iid_active_round_guard": stopped == reference_hit,
            "coupling_bound_holds": guarded_read <= fast_read + blocks * stopped,
        },
        "policy_rows": policy_rows,
        "pass": (
            len(four_plan_actions) == 13
            and value_counts == {"3/2": 1, "2": 12}
            and len(optimal_rows) == 1
            and tuple(optimal_rows[0]["state_a_lengths"]) == BALANCED_LENGTHS
            and Fraction(optimal_rows[0]["stationary_expected_length"])
            == Fraction(3, 2)
            and stopped == reference_hit
            and guarded_read <= fast_read + blocks * stopped
        ),
    }


def competing_cycle_mean_payoff_report(
    blocks: int = 64, slack: int = 5
) -> dict[str, Any]:
    """Nontrivial three-state mean-payoff census with distinct optimal codes."""

    if blocks < 1 or slack < 1:
        raise ValueError("blocks and slack must be positive")
    source_probabilities = (
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(1, 8),
        Fraction(1, 8),
    )
    fast_lengths = (2, 1, 3, 3)
    potential = (Fraction(0), Fraction(-4, 3), Fraction(-2, 3))
    policy_rows = []
    for lengths in labelled_full_tree_length_vectors(4):
        cycle_means = (
            Fraction(lengths[0]),
            *(Fraction(lengths[plan] + 2, 3) for plan in (1, 2, 3)),
        )
        value = max(cycle_means)
        bellman_action_score = max(
            Fraction(lengths[0]) + potential[0],
            *(Fraction(lengths[plan]) + potential[1] for plan in (1, 2, 3)),
        )
        state_a_expected = sum(
            (
                probability * length
                for probability, length in zip(
                    source_probabilities, lengths, strict=True
                )
            ),
            start=Fraction(0),
        )
        stationary_expected = Fraction(2, 5) * state_a_expected + Fraction(3, 5)
        policy_rows.append(
            {
                "state_a_lengths": lengths,
                "cycle_means": [str(mean) for mean in cycle_means],
                "mean_payoff_value": str(value),
                "bellman_action_score": str(bellman_action_score),
                "stationary_expected_length": str(stationary_expected),
            }
        )
    write_value = min(Fraction(row["mean_payoff_value"]) for row in policy_rows)
    optimal_rows = [
        row for row in policy_rows if Fraction(row["mean_payoff_value"]) == write_value
    ]
    selected_baseline = min(
        optimal_rows, key=lambda row: Fraction(row["stationary_expected_length"])
    )
    baseline_lengths = tuple(selected_baseline["state_a_lengths"])
    value_counts = {
        str(value): sum(
            Fraction(row["mean_payoff_value"]) == value for row in policy_rows
        )
        for value in sorted({Fraction(row["mean_payoff_value"]) for row in policy_rows})
    }
    action_score_counts = {
        str(score): sum(
            Fraction(row["bellman_action_score"]) == score for row in policy_rows
        )
        for score in sorted(
            {Fraction(row["bellman_action_score"]) for row in policy_rows}
        )
    }
    state_targets = tuple(write_value + value for value in potential)
    shapley_values = (
        min(Fraction(row["bellman_action_score"]) for row in policy_rows),
        Fraction(1) + potential[2],
        Fraction(1) + potential[0],
    )
    baseline_edge_values = {
        "A": [
            str(Fraction(baseline_lengths[0]) + potential[0]),
            *(
                str(Fraction(baseline_lengths[plan]) + potential[1])
                for plan in (1, 2, 3)
            ),
        ],
        "B": [str(Fraction(1) + potential[2])],
        "C": [str(Fraction(1) + potential[0])],
    }
    upper_policy_certificate = (
        all(Fraction(value) <= state_targets[0] for value in baseline_edge_values["A"])
        and Fraction(baseline_edge_values["B"][0]) <= state_targets[1]
        and Fraction(baseline_edge_values["C"][0]) <= state_targets[2]
    )
    arbitrary_history_lower_certificate = (
        all(
            Fraction(row["bellman_action_score"]) >= state_targets[0]
            for row in policy_rows
        )
        and shapley_values[1] >= state_targets[1]
        and shapley_values[2] >= state_targets[2]
    )
    potential_span = max(potential) - min(potential)

    worst_values = (0, 0, 0)
    for _ in range(blocks):
        previous = worst_values
        worst_values = (
            max(
                baseline_lengths[0] + previous[0],
                *(baseline_lengths[plan] + previous[1] for plan in (1, 2, 3)),
            ),
            1 + previous[2],
            1 + previous[0],
        )
    baseline_worst = max(worst_values)

    active: dict[tuple[int, int], Fraction] = {
        (0, 0): Fraction(2, 5),
        (1, 0): Fraction(3, 10),
        (2, 0): Fraction(3, 10),
    }
    stopped: dict[int, Fraction] = {}
    guarded_read = Fraction(0)
    for _ in range(blocks):
        next_active: dict[tuple[int, int], Fraction] = {}
        next_stopped: dict[int, Fraction] = {}
        for (state, surplus), state_mass in active.items():
            if state == 0:
                probabilities = source_probabilities
                read_lengths = fast_lengths
                reference_lengths = baseline_lengths
                next_states = (0, 1, 1, 1)
            else:
                probabilities = (Fraction(3, 4), Fraction(1, 4))
                read_lengths = (1, 1)
                reference_lengths = (1, 1)
                next_states = (2, 2) if state == 1 else (0, 0)
            for probability, read_length, reference_length, next_state in zip(
                probabilities,
                read_lengths,
                reference_lengths,
                next_states,
                strict=True,
            ):
                mass = state_mass * probability
                guarded_read += mass * read_length
                target = surplus + read_length - reference_length
                if target >= slack:
                    next_stopped[next_state] = (
                        next_stopped.get(next_state, Fraction(0)) + mass
                    )
                else:
                    key = (next_state, target)
                    next_active[key] = next_active.get(key, Fraction(0)) + mass
        for state, state_mass in stopped.items():
            if state == 0:
                probabilities = source_probabilities
                read_lengths = baseline_lengths
                next_states = (0, 1, 1, 1)
            else:
                probabilities = (Fraction(3, 4), Fraction(1, 4))
                read_lengths = (1, 1)
                next_states = (2, 2) if state == 1 else (0, 0)
            for probability, read_length, next_state in zip(
                probabilities, read_lengths, next_states, strict=True
            ):
                mass = state_mass * probability
                guarded_read += mass * read_length
                next_stopped[next_state] = (
                    next_stopped.get(next_state, Fraction(0)) + mass
                )
        active = next_active
        stopped = next_stopped

    hit_probability = sum(stopped.values(), start=Fraction(0))
    fast_read = Fraction(13 * blocks, 10)
    mgf_factor = sum(
        (
            probability * Fraction(2) ** (fast - baseline)
            for probability, fast, baseline in zip(
                source_probabilities,
                fast_lengths,
                baseline_lengths,
                strict=True,
            )
        ),
        start=Fraction(0),
    )
    finite_transient_excess = Fraction(baseline_worst) - write_value * blocks
    bellman_certificate = {
        "state_order": ["A", "B", "C"],
        "rho": str(write_value),
        "potential": [str(value) for value in potential],
        "state_targets": [str(value) for value in state_targets],
        "shapley_values": [str(value) for value in shapley_values],
        "action_score_counts": action_score_counts,
        "baseline_edge_values": baseline_edge_values,
        "potential_span": str(potential_span),
        "upper_policy_certificate": upper_policy_certificate,
        "arbitrary_history_lower_certificate": arbitrary_history_lower_certificate,
        "finite_excess_within_potential_span": finite_transient_excess
        <= potential_span,
        "pass": (
            state_targets == shapley_values
            and action_score_counts == {"5/3": 3, "2": 4, "3": 6}
            and upper_policy_certificate
            and arbitrary_history_lower_certificate
            and potential_span == Fraction(4, 3)
            and finite_transient_excess <= potential_span
        ),
    }
    return {
        "source": "three-state biased self-loop/detour predictor",
        "stationary_state_law": ["2/5", "3/10", "3/10"],
        "state_a_probabilities": [str(value) for value in source_probabilities],
        "fast_huffman_lengths": fast_lengths,
        "write_policy_count": len(policy_rows),
        "write_value_counts": value_counts,
        "write_threshold": str(write_value),
        "optimal_write_policy_count": len(optimal_rows),
        "selected_worst_optimal_lengths": baseline_lengths,
        "selected_baseline_expected_rate": selected_baseline[
            "stationary_expected_length"
        ],
        "read_threshold": "13/10",
        "fast_minus_baseline_stationary_drift": "-1/10",
        "conditional_mgf_factor_at_lambda_2": str(mgf_factor),
        "closed_region": "[13/10,infinity) x [5/3,infinity)",
        "bellman_certificate": bellman_certificate,
        "guard_replay": {
            "blocks": blocks,
            "slack": slack,
            "fast_read_total": _fraction_payload(fast_read),
            "guarded_read_total": _fraction_payload(guarded_read),
            "hit_probability": _fraction_payload(hit_probability),
            "hitting_bound": _fraction_payload(Fraction(1, 2**slack)),
            "baseline_worst_by_initial_state": worst_values,
            "baseline_worst_total": baseline_worst,
            "mean_payoff_linear_term": _fraction_payload(write_value * blocks),
            "finite_transient_excess": _fraction_payload(finite_transient_excess),
            "guarded_worst_total": baseline_worst + slack,
            "coupling_bound_holds": (
                guarded_read <= fast_read + 3 * blocks * hit_probability
            ),
        },
        "policy_rows": policy_rows,
        "pass": (
            len(policy_rows) == 13
            and value_counts == {"5/3": 3, "2": 4, "3": 6}
            and write_value == Fraction(5, 3)
            and len(optimal_rows) == 3
            and baseline_lengths == (1, 2, 3, 3)
            and Fraction(selected_baseline["stationary_expected_length"])
            == Fraction(7, 5)
            and mgf_factor == 1
            and bellman_certificate["pass"]
            and hit_probability <= Fraction(1, 2**slack)
            and finite_transient_excess <= Fraction(4, 3)
            and guarded_read <= fast_read + 3 * blocks * hit_probability
        ),
    }


def verification_payload() -> dict[str, Any]:
    actions = action_universe_report()
    bellman = adaptive_bellman_report()
    witness = two_block_adaptive_witness_report()
    two_block_census = exhaustive_two_block_strategy_report()
    logarithmic = logarithmic_slack_report()
    probability_phase = general_probability_phase_report()
    finite_alphabets = finite_iid_alphabet_report()
    markov_guard = markov_common_history_guard_report()
    vanishing_guard = vanishing_maximum_guard_report()
    stationary_renewal = stationary_renewal_source_report()
    stationary_predictor = stationary_predictor_rectangle_report(
        renewal_report=stationary_renewal
    )
    variable_support = variable_support_mean_payoff_report()
    competing_cycles = competing_cycle_mean_payoff_report()
    expected_minima = [
        (row["expected_read_length"]["exact"], tuple(row["write_length_vector"]))
        for row in actions["coordinatewise_minima"]
    ]
    gates = {
        "A0_complete_deadline_codebook_universe": actions["pass"],
        "A1_exact_thirteen_action_reduction": expected_minima
        == [
            ("7/4", (1, 2, 3, 3)),
            ("15/8", (1, 3, 2, 3)),
            ("15/8", (1, 3, 3, 2)),
            ("2", (2, 1, 3, 3)),
            ("2", (2, 2, 2, 2)),
            ("9/4", (2, 3, 1, 3)),
            ("9/4", (2, 3, 3, 1)),
            ("19/8", (3, 1, 2, 3)),
            ("19/8", (3, 1, 3, 2)),
            ("5/2", (3, 2, 1, 3)),
            ("5/2", (3, 2, 3, 1)),
            ("21/8", (3, 3, 1, 2)),
            ("21/8", (3, 3, 2, 1)),
        ],
        "A2_exact_adaptive_bellman_frontiers": bellman["pass"],
        "A3_two_block_fixed_schedule_counterexample": witness["pass"],
        "A3b_exhaustive_two_block_strategy_census": two_block_census["pass"],
        "A4_negative_drift_exponential_martingale": (
            logarithmic["martingale_factor"] == "1"
            and logarithmic["mean_surplus_increment"] == "-1/4"
        ),
        "A5_logarithmic_slack_corner_certificate": logarithmic["pass"],
        "A6_asymptotic_rectangle_endpoints": (
            logarithmic["read_rate_limit_per_tick"] == "7/12"
            and logarithmic["write_rate_limit_per_tick"] == "2/3"
        ),
        "A7_general_four_plan_probability_phase": (
            probability_phase["pass"]
            and probability_phase["laws"] == 34
            and probability_phase["skew_laws"] == 27
            and probability_phase["boundary_laws"] == 2
            and probability_phase["balanced_laws"] == 5
        ),
        "A8_general_finite_iid_alphabet_rectangle": (
            finite_alphabets["pass"]
            and finite_alphabets["laws"] == 57
            and finite_alphabets["profile_counts"] == {2: 1, 3: 1, 4: 2, 5: 3, 6: 5}
            and finite_alphabets["construction_counts"]
            == {"fixed_equal": 10, "direct": 21, "guard": 26}
        ),
        "A9_correlated_markov_conditional_mgf_guard": (
            markov_guard["pass"]
            and markov_guard["correlation_witness"]
            == {
                "P_next_0_given_0": "1/2",
                "P_next_0_given_1": "1/8",
            }
            and markov_guard["matches_iid_length_process"]
        ),
        "A10_vanishing_maximum_guard_without_uniform_mgf": (
            vanishing_guard["pass"]
            and not vanishing_guard["uniform_one_step_mgf_hypothesis_holds"]
            and vanishing_guard["strong_law_surplus_rate"] == "-1/8"
            and vanishing_guard["fast_read_rate_limit"] == "15/8"
            and vanishing_guard["write_rate_limit"] == "2"
        ),
        "A11_stationary_ergodic_separator_without_uniform_mgf": (
            stationary_renewal["pass"]
            and stationary_renewal["positive_recurrent"]
            and stationary_renewal["aperiodic"]
            and stationary_renewal["irreducible"]
            and stationary_renewal["conditional_huffman_optimal"]
            and not stationary_renewal["uniform_one_step_mgf_hypothesis_holds"]
        ),
        "A12_stationary_ergodic_public_predictor_rectangle": (
            stationary_predictor["pass"]
            and stationary_predictor["profile_counts"]
            == {2: 1, 3: 1, 4: 2, 5: 3, 6: 5, 7: 9, 8: 16}
            and stationary_predictor["closed_region"]
            == "[h_H,infinity) x [ceil(log2 m),infinity)"
        ),
        "A13_variable_support_mean_payoff_rectangle": (
            variable_support["pass"]
            and variable_support["write_policy_count"] == 13
            and variable_support["write_value_counts"] == {"3/2": 1, "2": 12}
            and variable_support["closed_region"] == "[11/8,infinity) x [3/2,infinity)"
        ),
        "A14_competing_cycle_mean_payoff_guard": (
            competing_cycles["pass"]
            and competing_cycles["bellman_certificate"]["pass"]
            and competing_cycles["bellman_certificate"]["potential"]
            == ["0", "-4/3", "-2/3"]
            and competing_cycles["write_value_counts"] == {"5/3": 3, "2": 4, "3": 6}
            and competing_cycles["fast_huffman_lengths"] == (2, 1, 3, 3)
            and competing_cycles["selected_worst_optimal_lengths"] == (1, 2, 3, 3)
            and competing_cycles["closed_region"] == "[13/10,infinity) x [5/3,infinity)"
        ),
    }
    return {
        "schema_version": "asmp4_adaptive_history_collapse_verification_v0_5",
        "fixture": {
            "plan_probabilities": [str(value) for value in PLAN_PROBABILITIES],
            "deadline_ticks": 3,
            "fixed_public_block_clock": True,
            "common_history_adaptation": True,
            "private_schedule_information": False,
        },
        "action_universe": actions,
        "adaptive_bellman": bellman,
        "two_block_witness": witness,
        "two_block_strategy_census": two_block_census,
        "logarithmic_slack": logarithmic,
        "general_probability_phase": probability_phase,
        "finite_iid_alphabets": finite_alphabets,
        "markov_common_history_guard": markov_guard,
        "vanishing_maximum_guard": vanishing_guard,
        "stationary_renewal_source": stationary_renewal,
        "stationary_predictor_rectangle": stationary_predictor,
        "variable_support_mean_payoff": variable_support,
        "competing_cycle_mean_payoff": competing_cycles,
        "gates": gates,
        "pass": all(gates.values()),
    }


def main() -> int:
    payload = verification_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
