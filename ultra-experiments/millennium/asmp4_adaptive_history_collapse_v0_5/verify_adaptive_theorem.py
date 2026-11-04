"""Independent verifier for the adaptive-history ASMP-4 successor theorem."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from functools import lru_cache
from math import isqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / "asmp4_heterogeneous_port_costs_v0_4"
PROBABILITIES = (
    Fraction(1, 2),
    Fraction(1, 4),
    Fraction(1, 8),
    Fraction(1, 8),
)


def prefix_free(words: tuple[str, ...]) -> bool:
    return all(
        not right.startswith(left) for left in words for right in words if left != right
    )


def independent_codebooks() -> tuple[tuple[str, ...], ...]:
    words = tuple(
        format(value, f"0{length}b")
        for length in range(1, 4)
        for value in range(2**length)
    )
    unlabelled = tuple(
        group for group in itertools.combinations(words, 4) if prefix_free(group)
    )
    return tuple(
        labelled for group in unlabelled for labelled in itertools.permutations(group)
    )


def partition(codebook: tuple[str, ...], tick: int) -> tuple[tuple[int, ...], ...]:
    groups: dict[str, list[int]] = {}
    for plan, word in enumerate(codebook):
        prefix = word[: min(tick, len(word))]
        groups.setdefault(prefix, []).append(plan)
    return tuple(sorted(tuple(group) for group in groups.values()))


def signature(
    codebook: tuple[str, ...],
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple(partition(codebook, tick) for tick in (1, 2, 3))


def factorable(
    read: tuple[tuple[tuple[int, ...], ...], ...],
    write: tuple[tuple[tuple[int, ...], ...], ...],
) -> bool:
    for read_partition, write_partition in zip(read, write, strict=True):
        write_sets = tuple(set(block) for block in write_partition)
        if not all(
            any(set(block) <= target for target in write_sets)
            for block in read_partition
        ):
            return False
    return True


def independent_actions() -> dict[str, object]:
    codebooks = independent_codebooks()
    reads: dict[object, set[Fraction]] = {}
    writes: dict[object, set[tuple[int, ...]]] = {}
    for codebook in codebooks:
        key = signature(codebook)
        lengths = tuple(map(len, codebook))
        cost = sum(
            (
                probability * length
                for probability, length in zip(PROBABILITIES, lengths, strict=True)
            ),
            start=Fraction(0),
        )
        reads.setdefault(key, set()).add(cost)
        writes.setdefault(key, set()).add(lengths)

    actions = set()
    causal_pairs = 0
    for read_signature, costs in reads.items():
        for write_signature, length_vectors in writes.items():
            if not factorable(read_signature, write_signature):
                continue
            causal_pairs += 1
            actions.update(
                (cost, vector) for cost in costs for vector in length_vectors
            )
    minimal = tuple(
        action
        for action in sorted(actions)
        if not any(
            other != action
            and other[0] <= action[0]
            and all(
                left <= right for left, right in zip(other[1], action[1], strict=True)
            )
            for other in actions
        )
    )
    return {
        "codebooks": len(codebooks),
        "reveal_signatures": len(reads),
        "read_keys": sum(map(len, reads.values())),
        "write_keys": sum(map(len, writes.values())),
        "causal_pairs": causal_pairs,
        "actions": len(actions),
        "minimal": minimal,
    }


def independent_bellman(
    actions: tuple[tuple[Fraction, tuple[int, ...]], ...], max_blocks: int = 8
) -> list[dict[int, Fraction]]:
    values: list[dict[int, Fraction]] = [{0: Fraction(0)}]
    for blocks in range(1, max_blocks + 1):
        row = {}
        for budget in range(2 * blocks, 3 * blocks + 1):
            candidates = []
            for read_cost, write_lengths in actions:
                continuation = Fraction(0)
                feasible = True
                for probability, write_length in zip(
                    PROBABILITIES, write_lengths, strict=True
                ):
                    child_budget = budget - write_length
                    if child_budget < 2 * (blocks - 1):
                        feasible = False
                        break
                    if blocks > 1:
                        child_budget = min(child_budget, 3 * (blocks - 1))
                        continuation += probability * values[blocks - 1][child_budget]
                if feasible:
                    candidates.append(read_cost + continuation)
            row[budget] = min(candidates)
        values.append(row)
    return values


def independent_two_block_replay() -> dict[str, object]:
    huffman = (1, 2, 3, 3)
    balanced = (2, 2, 2, 2)
    expected = Fraction(0)
    worst = 0
    histories = 0
    for first in range(4):
        second_lengths = huffman if first < 2 else balanced
        for second in range(4):
            probability = PROBABILITIES[first] * PROBABILITIES[second]
            total = huffman[first] + second_lengths[second]
            expected += probability * total
            worst = max(worst, total)
            histories += 1
    return {"histories": histories, "expected": str(expected), "worst": worst}


def independent_two_block_census(
    actions: tuple[tuple[Fraction, tuple[int, ...]], ...],
) -> dict[str, object]:
    scaled = tuple((int(8 * read), writes) for read, writes in actions)
    children = tuple(
        (
            4 * first[0] + 2 * second[0] + third[0] + fourth[0],
            tuple(max(action[1]) for action in (first, second, third, fourth)),
        )
        for first, second, third, fourth in itertools.product(scaled, repeat=4)
    )
    points: dict[tuple[int, int], int] = {}
    for root_read, root_lengths in scaled:
        for child_read, child_worsts in children:
            point = (
                8 * root_read + child_read,
                max(
                    root_length + child_worst
                    for root_length, child_worst in zip(
                        root_lengths, child_worsts, strict=True
                    )
                ),
            )
            points[point] = points.get(point, 0) + 1
    minima = tuple(
        point
        for point in sorted(points)
        if not any(
            other != point and other[0] <= point[0] and other[1] <= point[1]
            for other in points
        )
    )
    return {
        "trees": len(actions) ** 5,
        "points": len(points),
        "minima": [(str(Fraction(read, 64)), write) for read, write in minima],
        "minimum_counts": [points[point] for point in minima],
    }


def independent_guard(blocks: int, slack: int) -> dict[str, object]:
    active = {0: Fraction(1)}
    stopped = Fraction(0)
    read = Fraction(0)
    increments = (
        (-1, Fraction(1, 2)),
        (0, Fraction(1, 4)),
        (1, Fraction(1, 4)),
    )
    for _ in range(blocks):
        active_mass = sum(active.values(), start=Fraction(0))
        read += Fraction(7, 4) * active_mass + 2 * stopped
        new_active: dict[int, Fraction] = {}
        new_stopped = stopped
        for surplus, state_mass in active.items():
            for increment, probability in increments:
                target = surplus + increment
                mass = state_mass * probability
                if target == slack:
                    new_stopped += mass
                else:
                    new_active[target] = new_active.get(target, Fraction(0)) + mass
        active = new_active
        stopped = new_stopped
    martingale_factor = sum(
        (
            probability * Fraction(2) ** increment
            for increment, probability in increments
        ),
        start=Fraction(0),
    )
    return {
        "expected": str(read),
        "stopped_probability": str(stopped),
        "hitting_bound": str(Fraction(1, 2**slack)),
        "worst_write": 2 * blocks + slack,
        "martingale_factor": str(martingale_factor),
        "pass": (
            stopped <= Fraction(1, 2**slack)
            and read <= Fraction(7, 4) * blocks + Fraction(blocks, 4 * 2**slack)
            and martingale_factor == 1
        ),
    }


def independent_probability_phase(total_mass: int = 16) -> dict[str, object]:
    laws = []
    for first_mass in range(1, total_mass):
        for second_mass in range(1, first_mass + 1):
            for third_mass in range(1, second_mass + 1):
                fourth_mass = total_mass - first_mass - second_mass - third_mass
                if 1 <= fourth_mass <= third_mass:
                    laws.append((first_mass, second_mass, third_mass, fourth_mass))
    phases = {"skew": 0, "boundary": 0, "balanced": 0}
    failures = []
    for masses in laws:
        first, second, third, fourth = (Fraction(mass, total_mass) for mass in masses)
        tail = third + fourth
        expected = 3 - 2 * first - second
        if expected < 2:
            phase = "skew"
            multiplier = first / tail
            factor = first / multiplier + second + tail * multiplier
            valid = multiplier > 1 and factor == 1 and expected - 2 < 0
        elif expected == 2:
            phase = "boundary"
            valid = 2 * first + second == 1
        else:
            phase = "balanced"
            valid = 2 * first + second < 1
        phases[phase] += 1
        if not valid:
            failures.append(masses)
    return {
        "laws": len(laws),
        "skew": phases["skew"],
        "boundary": phases["boundary"],
        "balanced": phases["balanced"],
        "failures": failures,
        "pass": not failures,
    }


@lru_cache(maxsize=None)
def independent_length_profiles(leaves: int) -> tuple[tuple[int, ...], ...]:
    if leaves == 1:
        return ((0,),)
    profiles = set()
    for left_count in range(1, leaves):
        for left in independent_length_profiles(left_count):
            for right in independent_length_profiles(leaves - left_count):
                profiles.add(
                    tuple(
                        sorted(
                            tuple(depth + 1 for depth in left)
                            + tuple(depth + 1 for depth in right)
                        )
                    )
                )
    return tuple(sorted(profiles))


def independent_mass_laws(atoms: int, total: int) -> tuple[tuple[int, ...], ...]:
    laws = []

    def visit(remaining: int, count: int, cap: int, prefix: tuple[int, ...]):
        if count == 0:
            if remaining == 0:
                laws.append(prefix)
            return
        for value in range(min(cap, remaining - count + 1), 0, -1):
            residual = remaining - value
            if count - 1 <= residual <= value * (count - 1):
                visit(residual, count - 1, value, prefix + (value,))

    visit(total, atoms, total, ())
    return tuple(laws)


def independent_finite_alphabets(total: int = 12) -> dict[str, object]:
    modes = {"fixed_equal": 0, "direct": 0, "guard": 0}
    profile_counts = {}
    laws = 0
    failures = []
    for plans in range(2, 7):
        profiles = independent_length_profiles(plans)
        profile_counts[plans] = len(profiles)
        fixed = (plans - 1).bit_length()
        for masses in independent_mass_laws(plans, total):
            laws += 1
            probabilities = tuple(Fraction(mass, total) for mass in masses)
            expected, lengths = min(
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
            maximum_surplus = max(lengths) - fixed
            if expected == fixed:
                mode = "fixed_equal"
                valid = True
            elif maximum_surplus <= 0:
                mode = "direct"
                valid = expected < fixed
            else:
                mode = "guard"
                valid = False
                for power in range(1, 65):
                    multiplier = 1 + Fraction(1, 2**power)
                    factor = sum(
                        (
                            probability * multiplier ** (length - fixed)
                            for probability, length in zip(
                                probabilities, lengths, strict=True
                            )
                        ),
                        start=Fraction(0),
                    )
                    if factor < 1:
                        valid = expected < fixed and multiplier > 1
                        break
            modes[mode] += 1
            if not valid:
                failures.append((plans, masses))
    return {
        "laws": laws,
        "profiles": profile_counts,
        "modes": modes,
        "failures": failures,
        "pass": not failures,
    }


def independent_markov_guard(blocks: int = 32, slack: int = 5) -> dict[str, object]:
    lengths = (1, 2, 3, 3)
    transitions = tuple(
        tuple(
            ((state + offset) % 4, PROBABILITIES[offset], lengths[offset])
            for offset in range(4)
        )
        for state in range(4)
    )
    active = {(0, 0): Fraction(1)}
    stopped = Fraction(0)
    expected = Fraction(0)
    for _ in range(blocks):
        active_mass = sum(active.values(), start=Fraction(0))
        expected += Fraction(7, 4) * active_mass + 2 * stopped
        new_active: dict[tuple[int, int], Fraction] = {}
        new_stopped = stopped
        for (state, surplus), state_mass in active.items():
            for plan, probability, length in transitions[state]:
                target = surplus + length - 2
                mass = state_mass * probability
                if target == slack:
                    new_stopped += mass
                else:
                    key = (plan, target)
                    new_active[key] = new_active.get(key, Fraction(0)) + mass
        active = new_active
        stopped = new_stopped
    factors = tuple(
        sum(
            (
                probability * Fraction(2) ** (length - 2)
                for _, probability, length in row
            ),
            start=Fraction(0),
        )
        for row in transitions
    )
    iid = independent_guard(blocks, slack)
    return {
        "expected": str(expected),
        "stopped": str(stopped),
        "conditional_factors": [str(value) for value in factors],
        "correlated": transitions[0][0][1] != transitions[1][3][1],
        "matches_iid": (
            str(expected) == iid["expected"]
            and str(stopped) == iid["stopped_probability"]
        ),
        "pass": all(value == 1 for value in factors),
    }


def independent_nonuniform_law(round_index: int) -> tuple[Fraction, ...]:
    if round_index % 2 == 0:
        return PROBABILITIES
    weak_index = (round_index - 1) // 2
    epsilon = Fraction(1, 2 ** (weak_index + 4))
    return (
        Fraction(3, 8) + epsilon / 2,
        Fraction(1, 4),
        Fraction(3, 16) - epsilon / 4,
        Fraction(3, 16) - epsilon / 4,
    )


def independent_vanishing_guard(
    horizons: tuple[int, ...] = (16, 32, 64, 128),
) -> dict[str, object]:
    lengths = (1, 2, 3, 3)
    rows = []
    for blocks in horizons:
        threshold = isqrt(blocks - 1) + 1
        active = {0: Fraction(1)}
        stopped = Fraction(0)
        guarded = Fraction(0)
        fast = Fraction(0)
        for round_index in range(blocks):
            probabilities = independent_nonuniform_law(round_index)
            fast += sum(
                (
                    probability * length
                    for probability, length in zip(probabilities, lengths, strict=True)
                ),
                start=Fraction(0),
            )
            guarded += 2 * stopped
            next_active: dict[int, Fraction] = {}
            next_stopped = stopped
            for surplus, state_mass in active.items():
                for probability, length in zip(probabilities, lengths, strict=True):
                    mass = state_mass * probability
                    guarded += mass * length
                    target = surplus + length - 2
                    if target >= threshold:
                        next_stopped += mass
                    else:
                        next_active[target] = (
                            next_active.get(target, Fraction(0)) + mass
                        )
            active = next_active
            stopped = next_stopped
        expected_fast = Fraction(15 * blocks, 8) - Fraction(1, 8) * (
            1 - Fraction(1, 2 ** (blocks // 2))
        )
        rows.append(
            {
                "blocks": blocks,
                "threshold": threshold,
                "hit": stopped,
                "fast": fast,
                "guarded": guarded,
                "formula": fast == expected_fast,
                "coupling": guarded <= fast + 2 * blocks * stopped,
            }
        )
    weak_factors = []
    for weak_index in range(max(horizons) // 2):
        probabilities = independent_nonuniform_law(2 * weak_index + 1)
        weak_factors.append(
            sum(
                (
                    probability * Fraction(2) ** (length - 2)
                    for probability, length in zip(probabilities, lengths, strict=True)
                ),
                start=Fraction(0),
            )
        )
    hits = [row["hit"] for row in rows]
    return {
        "horizons": list(horizons),
        "thresholds": [row["threshold"] for row in rows],
        "hit_probabilities": [float(row["hit"]) for row in rows],
        "fast_rate_limit": "15/8",
        "write_rate_limit": "2",
        "drift_limit": "-1/8",
        "uniform_mgf": False,
        "pass": (
            all(row["formula"] and row["coupling"] for row in rows)
            and all(value > 1 for value in weak_factors)
            and all(left > right for left, right in zip(hits, hits[1:]))
        ),
    }


def independent_stationary_renewal(cutoff: int = 32) -> dict[str, object]:
    lengths = (1, 2, 3, 3)
    weight = Fraction(1)
    normalizer = Fraction(0)
    drift_numerator = Fraction(0)
    weak_factors = []
    huffman_optimal = True
    minimum_reset = Fraction(1)
    advance_positive = True
    for state in range(cutoff):
        probabilities = independent_nonuniform_law(state)
        expected = sum(
            (
                probability * length
                for probability, length in zip(probabilities, lengths, strict=True)
            ),
            start=Fraction(0),
        )
        reset = probabilities[0]
        normalizer += weight
        drift_numerator += weight * (expected - 2)
        minimum_reset = min(minimum_reset, reset)
        advance_positive &= 1 - reset > 0
        huffman_optimal &= 2 * probabilities[0] + probabilities[1] > 1
        if state % 2 == 1:
            weak_factors.append(
                sum(
                    (
                        probability * Fraction(2) ** (length - 2)
                        for probability, length in zip(
                            probabilities, lengths, strict=True
                        )
                    ),
                    start=Fraction(0),
                )
            )
        weight *= 1 - reset
    tail = Fraction(8, 3) * weight
    drift_lower = (drift_numerator - tail / 4) / normalizer
    drift_upper = drift_numerator / (normalizer + tail)
    read_lower = 2 + drift_lower
    read_upper = 2 + drift_upper
    pi_zero_lower = 1 / (normalizer + tail)
    ergodic = (
        minimum_reset >= Fraction(3, 8)
        and advance_positive
        and independent_nonuniform_law(0)[0] > 0
    )
    return {
        "cutoff": cutoff,
        "tail_bound": float(tail),
        "pi_zero_lower": float(pi_zero_lower),
        "drift_interval": [float(drift_lower), float(drift_upper)],
        "read_interval": [float(read_lower), float(read_upper)],
        "huffman_optimal": huffman_optimal,
        "uniform_mgf": False,
        "ergodic": ergodic,
        "pass": (
            minimum_reset >= Fraction(3, 8)
            and ergodic
            and huffman_optimal
            and all(value > 1 for value in weak_factors)
            and tail < Fraction(1, 10**7)
            and Fraction(-1, 4) < drift_lower <= drift_upper < 0
            and read_upper - read_lower < Fraction(1, 10**8)
            and pi_zero_lower >= Fraction(3, 8)
        ),
    }


def independent_stationary_predictor(
    renewal: dict[str, object], max_plans: int = 8
) -> dict[str, object]:
    rows = []
    for plans in range(2, max_plans + 1):
        profiles = independent_length_profiles(plans)
        fixed = (plans - 1).bit_length()
        rows.append(
            {
                "plans": plans,
                "count": len(profiles),
                "minimum_worst": min(max(profile) for profile in profiles),
                "maximum_depth": max(max(profile) for profile in profiles),
                "fixed": fixed,
                "depth_bound": all(max(profile) <= plans - 1 for profile in profiles),
            }
        )
    return {
        "profile_counts": {row["plans"]: row["count"] for row in rows},
        "fixtures": [
            "negative_drift_guard",
            "uniform_mgf_guard",
            "vanishing_maximum_guard",
            "fixed_equal",
        ],
        "closed_region": "[h_H,infinity) x [ceil(log2 m),infinity)",
        "pass": (
            renewal["pass"]
            and all(
                row["minimum_worst"] == row["fixed"] and row["depth_bound"]
                for row in rows
            )
        ),
    }


def independent_variable_support(blocks: int = 64, slack: int = 5) -> dict[str, object]:
    lengths = (1, 2, 3, 3)
    actions = tuple(
        sorted(
            {
                labelled
                for profile in independent_length_profiles(4)
                for labelled in itertools.permutations(profile)
            }
        )
    )
    values = [Fraction(max(action) + 1, 2) for action in actions]
    counts = {
        str(value): sum(candidate == value for candidate in values)
        for value in sorted(set(values))
    }
    active = {0: Fraction(1)}
    stopped = Fraction(0)
    guarded = Fraction(0)
    for round_index in range(blocks):
        if round_index % 2:
            guarded += 1
            continue
        active_mass = sum(active.values(), start=Fraction(0))
        guarded += Fraction(7, 4) * active_mass + 2 * stopped
        next_active: dict[int, Fraction] = {}
        next_stopped = stopped
        for surplus, state_mass in active.items():
            for probability, length in zip(PROBABILITIES, lengths, strict=True):
                mass = state_mass * probability
                target = surplus + length - 2
                if target >= slack:
                    next_stopped += mass
                else:
                    next_active[target] = next_active.get(target, Fraction(0)) + mass
        active = next_active
        stopped = next_stopped
    reference = independent_guard(blocks // 2, slack)
    return {
        "actions": len(actions),
        "value_counts": counts,
        "read_threshold": "11/8",
        "write_threshold": "3/2",
        "closed_region": "[11/8,infinity) x [3/2,infinity)",
        "guard_hit": str(stopped),
        "guarded_read": str(guarded),
        "pass": (
            len(actions) == 13
            and counts == {"3/2": 1, "2": 12}
            and actions[values.index(min(values))] == (2, 2, 2, 2)
            and str(stopped) == reference["stopped_probability"]
        ),
    }


def independent_competing_cycles(blocks: int = 64, slack: int = 5) -> dict[str, object]:
    probabilities_a = (
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(1, 8),
        Fraction(1, 8),
    )
    fast_a = (2, 1, 3, 3)
    potential = (Fraction(0), Fraction(-4, 3), Fraction(-2, 3))
    actions = tuple(
        sorted(
            {
                labelled
                for profile in independent_length_profiles(4)
                for labelled in itertools.permutations(profile)
            }
        )
    )
    rows = []
    for action in actions:
        value = max(
            Fraction(action[0]),
            *(Fraction(action[plan] + 2, 3) for plan in (1, 2, 3)),
        )
        expected_a = sum(
            (
                probability * length
                for probability, length in zip(probabilities_a, action, strict=True)
            ),
            start=Fraction(0),
        )
        rows.append((action, value, Fraction(2, 5) * expected_a + Fraction(3, 5)))
    value = min(row[1] for row in rows)
    optimal = [row for row in rows if row[1] == value]
    baseline = min(optimal, key=lambda row: row[2])[0]
    counts = {
        str(candidate): sum(row[1] == candidate for row in rows)
        for candidate in sorted({row[1] for row in rows})
    }
    action_scores = tuple(
        max(
            Fraction(action[0]) + potential[0],
            *(Fraction(action[plan]) + potential[1] for plan in (1, 2, 3)),
        )
        for action in actions
    )
    action_score_counts = {
        str(candidate): sum(score == candidate for score in action_scores)
        for candidate in sorted(set(action_scores))
    }
    targets = tuple(value + entry for entry in potential)
    shapley = (
        min(action_scores),
        Fraction(1) + potential[2],
        Fraction(1) + potential[0],
    )
    baseline_edges = (
        Fraction(baseline[0]) + potential[0],
        *(Fraction(baseline[plan]) + potential[1] for plan in (1, 2, 3)),
    )
    span = max(potential) - min(potential)
    upper_certificate = (
        all(edge <= targets[0] for edge in baseline_edges)
        and shapley[1] <= targets[1]
        and shapley[2] <= targets[2]
    )
    history_lower_certificate = (
        all(score >= targets[0] for score in action_scores)
        and shapley[1] >= targets[1]
        and shapley[2] >= targets[2]
    )

    worst = (0, 0, 0)
    for _ in range(blocks):
        previous = worst
        worst = (
            max(
                baseline[0] + previous[0],
                *(baseline[plan] + previous[1] for plan in (1, 2, 3)),
            ),
            1 + previous[2],
            1 + previous[0],
        )

    active = {
        (0, 0): Fraction(2, 5),
        (1, 0): Fraction(3, 10),
        (2, 0): Fraction(3, 10),
    }
    stopped: dict[int, Fraction] = {}
    guarded = Fraction(0)
    for _ in range(blocks):
        next_active: dict[tuple[int, int], Fraction] = {}
        next_stopped: dict[int, Fraction] = {}
        for (state, surplus), state_mass in active.items():
            if state == 0:
                probabilities = probabilities_a
                fast_lengths = fast_a
                base_lengths = baseline
                next_states = (0, 1, 1, 1)
            else:
                probabilities = (Fraction(3, 4), Fraction(1, 4))
                fast_lengths = (1, 1)
                base_lengths = (1, 1)
                next_states = (2, 2) if state == 1 else (0, 0)
            for probability, fast, base, next_state in zip(
                probabilities,
                fast_lengths,
                base_lengths,
                next_states,
                strict=True,
            ):
                mass = state_mass * probability
                guarded += mass * fast
                target = surplus + fast - base
                if target >= slack:
                    next_stopped[next_state] = (
                        next_stopped.get(next_state, Fraction(0)) + mass
                    )
                else:
                    key = (next_state, target)
                    next_active[key] = next_active.get(key, Fraction(0)) + mass
        for state, state_mass in stopped.items():
            if state == 0:
                probabilities = probabilities_a
                base_lengths = baseline
                next_states = (0, 1, 1, 1)
            else:
                probabilities = (Fraction(3, 4), Fraction(1, 4))
                base_lengths = (1, 1)
                next_states = (2, 2) if state == 1 else (0, 0)
            for probability, base, next_state in zip(
                probabilities, base_lengths, next_states, strict=True
            ):
                mass = state_mass * probability
                guarded += mass * base
                next_stopped[next_state] = (
                    next_stopped.get(next_state, Fraction(0)) + mass
                )
        active = next_active
        stopped = next_stopped
    hit = sum(stopped.values(), start=Fraction(0))
    mgf_factor = sum(
        (
            probability * Fraction(2) ** (fast - base)
            for probability, fast, base in zip(
                probabilities_a, fast_a, baseline, strict=True
            )
        ),
        start=Fraction(0),
    )
    excess = Fraction(max(worst)) - value * blocks
    bellman_certificate = {
        "potential": [str(entry) for entry in potential],
        "targets": [str(entry) for entry in targets],
        "shapley": [str(entry) for entry in shapley],
        "action_score_counts": action_score_counts,
        "baseline_edges_a": [str(entry) for entry in baseline_edges],
        "span": str(span),
        "upper": upper_certificate,
        "history_lower": history_lower_certificate,
        "excess_within_span": excess <= span,
        "pass": (
            targets == shapley
            and action_score_counts == {"5/3": 3, "2": 4, "3": 6}
            and upper_certificate
            and history_lower_certificate
            and span == Fraction(4, 3)
            and excess <= span
        ),
    }
    return {
        "actions": len(actions),
        "value_counts": counts,
        "write_value": str(value),
        "optimal_count": len(optimal),
        "fast": fast_a,
        "baseline": baseline,
        "read_threshold": "13/10",
        "closed_region": "[13/10,infinity) x [5/3,infinity)",
        "hit": str(hit),
        "guarded": str(guarded),
        "mgf_factor": str(mgf_factor),
        "worst": worst,
        "bellman_certificate": bellman_certificate,
        "pass": (
            len(actions) == 13
            and counts == {"5/3": 3, "2": 4, "3": 6}
            and value == Fraction(5, 3)
            and len(optimal) == 3
            and fast_a == (2, 1, 3, 3)
            and baseline == (1, 2, 3, 3)
            and bellman_certificate["pass"]
            and mgf_factor == 1
            and hit <= Fraction(1, 2**slack)
            and excess <= Fraction(4, 3)
        ),
    }


def theorem_sentinels() -> dict[str, bool]:
    theorem = (ROOT / "THEOREM.md").read_text(encoding="utf-8")
    result = (ROOT / "RESULT.md").read_text(encoding="utf-8")
    audit = (ROOT / "COMPLETION_AUDIT_v0_5.md").read_text(encoding="utf-8")
    canonical_audit = (ROOT / "CANONICAL_SCOPE_AUDIT_v0_5.md").read_text(
        encoding="utf-8"
    )
    stopping = (ROOT / "STOPPING_ARGUMENT_v0_5.md").read_text(encoding="utf-8")
    prior_art = (ROOT / "PRIOR_ART_AUDIT_v0_5.md").read_text(encoding="utf-8")
    return {
        "common_history_scope": "common decoded history" in theorem,
        "bellman_recurrence": "V_n(b)" in theorem and "Bellman" in theorem,
        "exact_guarded_optimizer": (
            "**Theorem 2A (exact guarded optimizer).**" in theorem
            and "V_n(2n+k) = (7/4)n + (1/4) E[(n-tau_k)_+]" in theorem
        ),
        "two_block_counterexample": "57/16" in theorem and "3/16" in theorem,
        "finite_zero_slack_obstruction": "V_n(2n) = 2n" in theorem,
        "martingale_certificate": "M_t = 2^{S_t}" in theorem,
        "logarithmic_slack": "ceil(log2 n)" in theorem,
        "adaptive_rectangle": "[7/12,infinity) x [2/3,infinity)" in theorem,
        "general_probability_phase": (
            "lambda = p_1/(p_3+p_4)" in theorem
            and "Every positive sorted four-plan law" in theorem
        ),
        "general_finite_alphabet": (
            "**Theorem 6 (finite-i.i.d.-alphabet adaptive rectangle).**" in theorem
            and "q=ceil(log2 m)" in theorem
            and "phi'(1)=E[Y]<0" in theorem
        ),
        "conditional_mgf_guard": (
            "**Theorem 7 (uniform conditional-MGF guard).**" in theorem
            and "E[lambda^(ell_t-q) | F_(t-1)] <= 1" in theorem
        ),
        "vanishing_maximum_guard": (
            "**Theorem 8 (vanishing-maximum guard).**" in theorem
            and "S_t/t -> h-q < 0 almost surely" in theorem
            and "[15/8,infinity) x [2,infinity)" in theorem
            and "every fixed multiplier eventually violates" in theorem
        ),
        "stationary_ergodic_separator": (
            "**Theorem 9 (stationary-ergodic MGF separator).**" in theorem
            and "[h_*,infinity) x [2,infinity)" in theorem
            and "1.8161864422 < h_* < 1.8161864463" in theorem
            and "state zero has a self-loop" in theorem
        ),
        "stationary_predictor_rectangle": (
            "**Theorem 10 (stationary-ergodic public-predictor rectangle).**" in theorem
            and "[h_H,infinity) x [q,infinity)" in theorem
            and "P(Theta_t=i | full common history) = p_i(Z_t)" in theorem
            and "1,1,2,3,5,9,16" in theorem
        ),
        "variable_support_mean_payoff": (
            "**Theorem 11 (finite-state variable-support rectangle).**" in theorem
            and "[h,infinity) x [rho,infinity)" in theorem
            and "[11/8,infinity) x [3/2,infinity)" in theorem
            and "Positional determinacy" in theorem
            and "three policies of value `5/3`, four of value `2`, and" in theorem
            and "[13/10,infinity) x [5/3,infinity)" in theorem
            and "v = (0,-4/3,-2/3)" in theorem
            and "arbitrary history-dependent coder" in theorem
        ),
        "fixed_schedule_not_deleted": "fixed-schedule segment remains exact" in result,
        "scope_firewall": "does not amend the canonical v0.1 metric" in result,
        "completion_audit": "Requirement-by-requirement evidence" in audit,
        "canonical_scope_audit": (
            "Normal-form dependency audit" in canonical_audit
            and "Canonical requirement matrix" in canonical_audit
            and "candidate negative" in canonical_audit
            and "finite prefix-code census cannot decide" in canonical_audit
        ),
        "stopping_boundary": (
            "resolved inside the v0.4/v0.5 registered fixture" in stopping
            and "candidate/partial at canonical ASMP-4 scope" in stopping
            and "would add regression coverage" in stopping
        ),
        "prior_art_firewall": (
            "Buffer Overflow in Variable Length Coding" in prior_art
            and "Generalization of Huffman Coding" in prior_art
            and "does **not** claim novelty" in prior_art
        ),
    }


def main() -> int:
    action_report = independent_actions()
    minimal = action_report["minimal"]
    values = independent_bellman(minimal)
    guard_matches_bellman = True
    for blocks in range(1, len(values)):
        for slack in range(blocks + 1):
            guard_value = (
                Fraction(2 * blocks)
                if slack == 0
                else Fraction(independent_guard(blocks, slack)["expected"])
            )
            guard_matches_bellman &= guard_value == values[blocks][2 * blocks + slack]
    replay = independent_two_block_replay()
    two_block_census = independent_two_block_census(minimal)
    guard = independent_guard(32, 5)
    probability_phase = independent_probability_phase()
    finite_alphabets = independent_finite_alphabets()
    markov_guard = independent_markov_guard()
    vanishing_guard = independent_vanishing_guard()
    stationary_renewal = independent_stationary_renewal()
    stationary_predictor = independent_stationary_predictor(stationary_renewal)
    variable_support = independent_variable_support()
    competing_cycles = independent_competing_cycles()
    sentinels = theorem_sentinels()
    claim = json.loads((ROOT / "adaptive_claim_v0_5.json").read_text(encoding="utf-8"))
    previous_claim = json.loads(
        (PREVIOUS / "boundary_claim_v0_4.json").read_text(encoding="utf-8")
    )
    expected_minimal = (
        (Fraction(7, 4), (1, 2, 3, 3)),
        (Fraction(15, 8), (1, 3, 2, 3)),
        (Fraction(15, 8), (1, 3, 3, 2)),
        (Fraction(2), (2, 1, 3, 3)),
        (Fraction(2), (2, 2, 2, 2)),
        (Fraction(9, 4), (2, 3, 1, 3)),
        (Fraction(9, 4), (2, 3, 3, 1)),
        (Fraction(19, 8), (3, 1, 2, 3)),
        (Fraction(19, 8), (3, 1, 3, 2)),
        (Fraction(5, 2), (3, 2, 1, 3)),
        (Fraction(5, 2), (3, 2, 3, 1)),
        (Fraction(21, 8), (3, 3, 1, 2)),
        (Fraction(21, 8), (3, 3, 2, 1)),
    )
    exact_rows = {
        blocks: [str(value) for _, value in sorted(values[blocks].items())]
        for blocks in range(1, 5)
    }
    checks = {
        "I0_independent_deadline_universe": (
            action_report["codebooks"] == 4968
            and action_report["reveal_signatures"] == 27
            and action_report["read_keys"] == 121
            and action_report["write_keys"] == 150
        ),
        "I1_independent_action_reduction": (
            action_report["causal_pairs"] == 72
            and action_report["actions"] == 250
            and minimal == expected_minimal
        ),
        "I2_independent_bellman_values": exact_rows
        == {
            1: ["2", "7/4"],
            2: ["4", "57/16", "7/2"],
            3: ["6", "345/64", "337/64", "21/4"],
            4: ["8", "1851/256", "901/128", "1793/256", "7"],
        },
        "I3_independent_two_block_replay": replay
        == {"histories": 16, "expected": "57/16", "worst": 5},
        "I4_independent_two_block_census": two_block_census
        == {
            "trees": 371293,
            "points": 188,
            "minima": [("7/2", 6), ("57/16", 5), ("4", 4)],
            "minimum_counts": [1, 1, 1],
        },
        "I5_independent_exact_guard_optimizer": guard_matches_bellman,
        "I6_independent_guard_martingale": guard["pass"],
        "I7_independent_probability_phase": probability_phase
        == {
            "laws": 34,
            "skew": 27,
            "boundary": 2,
            "balanced": 5,
            "failures": [],
            "pass": True,
        },
        "I8_independent_finite_alphabets": finite_alphabets
        == {
            "laws": 57,
            "profiles": {2: 1, 3: 1, 4: 2, 5: 3, 6: 5},
            "modes": {"fixed_equal": 10, "direct": 21, "guard": 26},
            "failures": [],
            "pass": True,
        },
        "I9_independent_correlated_markov_guard": (
            markov_guard["pass"]
            and markov_guard["correlated"]
            and markov_guard["matches_iid"]
            and markov_guard["conditional_factors"] == ["1", "1", "1", "1"]
        ),
        "I9b_independent_vanishing_maximum_guard": (
            vanishing_guard["pass"]
            and not vanishing_guard["uniform_mgf"]
            and vanishing_guard["drift_limit"] == "-1/8"
            and vanishing_guard["fast_rate_limit"] == "15/8"
            and vanishing_guard["write_rate_limit"] == "2"
        ),
        "I9c_independent_stationary_ergodic_separator": (
            stationary_renewal["pass"]
            and stationary_renewal["ergodic"]
            and stationary_renewal["huffman_optimal"]
            and not stationary_renewal["uniform_mgf"]
            and 1.81618644 < stationary_renewal["read_interval"][0]
            and stationary_renewal["read_interval"][1] < 1.81618645
        ),
        "I9d_independent_stationary_predictor_rectangle": (
            stationary_predictor["pass"]
            and stationary_predictor["profile_counts"]
            == {2: 1, 3: 1, 4: 2, 5: 3, 6: 5, 7: 9, 8: 16}
            and stationary_predictor["closed_region"]
            == "[h_H,infinity) x [ceil(log2 m),infinity)"
        ),
        "I9e_independent_variable_support_mean_payoff": (
            variable_support["pass"]
            and variable_support["actions"] == 13
            and variable_support["value_counts"] == {"3/2": 1, "2": 12}
            and variable_support["closed_region"] == "[11/8,infinity) x [3/2,infinity)"
        ),
        "I9f_independent_competing_cycle_guard": (
            competing_cycles["pass"]
            and competing_cycles["bellman_certificate"]["pass"]
            and competing_cycles["bellman_certificate"]["potential"]
            == ["0", "-4/3", "-2/3"]
            and competing_cycles["value_counts"] == {"5/3": 3, "2": 4, "3": 6}
            and competing_cycles["fast"] == (2, 1, 3, 3)
            and competing_cycles["baseline"] == (1, 2, 3, 3)
            and competing_cycles["mgf_factor"] == "1"
            and competing_cycles["closed_region"] == "[13/10,infinity) x [5/3,infinity)"
        ),
        "I10_theorem_structure": all(sentinels.values()),
        "I11_claim_scope": (
            claim["problem_id"] == "ASMP-4"
            and claim["common_history_adaptation"]
            and not claim["private_schedule_information"]
            and claim["fixed_public_block_clock"]
            and claim["asymptotic_region_per_tick"]
            == "[7/12,infinity) x [2/3,infinity)"
            and claim["general_probability_phase"]
            == {
                "strict_skew_condition": "2p_1+p_2>1",
                "strict_skew_martingale_multiplier": "p_1/(p_3+p_4)",
                "read_threshold": "min(3-2p_1-p_2,2)",
                "write_threshold": "2",
            }
            and claim["finite_optimal_policy"]
            == "canonical Huffman at positive residual slack; balanced at zero residual slack"
            and claim["finite_stopping_time_value"]
            == "V_n(2n+k)=(7/4)n+(1/4)E[(n-tau_k)_+]"
            and claim["finite_iid_alphabet_theorem"]
            == {
                "plans": "any finite m>=2 with a positive i.i.d. law",
                "read_threshold": "mu = minimum expected binary prefix length",
                "write_threshold": "ceil(log2 m)",
                "adaptive_region_per_block": "[mu,infinity) x [ceil(log2 m),infinity)",
                "guard_slack": "O(log n)",
                "normalization": "per source block on an externally registered fixed clock",
            }
            and claim["conditional_mgf_guard"]
            == {
                "criterion": "E[lambda^(ell_t-q) | common history] <= 1 uniformly for some lambda>1",
                "source_scope": "correlated exogenous finite-plan processes",
                "read_penalty_with_threshold_a": "at most q*n*lambda^(-a)",
                "write_slack_with_threshold_a": (
                    "at most a+L-q-1 when L>q; no guard is needed when L<=q"
                ),
            }
            and claim["vanishing_maximum_guard"]
            == {
                "criterion": "S_t/t -> h-q < 0 almost surely with bounded code lengths",
                "threshold": "a_n -> infinity and a_n=o(n)",
                "read_penalty_rate": (
                    "at most q*P(sup_t S_t >= a_n), which tends to zero"
                ),
                "write_slack": "a_n+L-q-1 when L>q",
                "time_varying_fixture_region_per_block": (
                    "[15/8,infinity) x [2,infinity)"
                ),
            }
            and claim["stationary_ergodic_separator"]
            == {
                "source": "observable renewal-age four-plan Markov source",
                "conditional_code": (
                    "Huffman lengths (1,2,3,3) are optimal at every state"
                ),
                "read_threshold_interval": "(1.8161864422,1.8161864463)",
                "write_threshold": "2",
                "uniform_conditional_mgf": False,
                "adaptive_region_per_block": "[h_*,infinity) x [2,infinity)",
            }
            and claim["stationary_predictor_theorem"]
            == {
                "plans": "any finite m>=2",
                "source": (
                    "stationary ergodic full-support plans with a common "
                    "sufficient predictive state"
                ),
                "read_threshold": (
                    "h_H = E[minimum conditional expected binary prefix length]"
                ),
                "write_threshold": "ceil(log2 m)",
                "adaptive_region_per_block": (
                    "[h_H,infinity) x [ceil(log2 m),infinity)"
                ),
                "guard_condition": (
                    "ergodic Huffman length mean below the fixed-length "
                    "threshold; equality uses the fixed code"
                ),
            }
            and claim["variable_support_theorem"]
            == {
                "source": (
                    "finite strongly connected public unifilar predictor with "
                    "positive enabled-plan laws"
                ),
                "read_threshold": "h = stationary conditional Huffman mean",
                "write_threshold": (
                    "rho = positional prefix-code mean-payoff game value"
                ),
                "adaptive_region_per_block": "[h,infinity) x [rho,infinity)",
                "exact_fixture_region_per_block": ("[11/8,infinity) x [3/2,infinity)"),
                "competing_cycle_fixture_region_per_block": (
                    "[13/10,infinity) x [5/3,infinity)"
                ),
                "competing_cycle_bellman_certificate": (
                    "rho=5/3, v=(0,-4/3,-2/3), span=4/3"
                ),
            }
            and claim["evidence"]["stopping_argument"] == "STOPPING_ARGUMENT_v0_5.md"
            and claim["evidence"]["canonical_scope_audit"]
            == "CANONICAL_SCOPE_AUDIT_v0_5.md"
        ),
        "I12_version_firewall": (
            "public repeated blocks" in previous_claim["claim"]
            and claim["supersedes_fixed_schedule_as_architecture_complete"]
            and not claim["changes_v0_4_finite_frontier"]
            and not claim["changes_canonical_v0_1_metric"]
        ),
    }
    payload = {
        "schema_version": "asmp4_adaptive_history_collapse_independent_v0_5",
        "action_universe": {
            key: value for key, value in action_report.items() if key != "minimal"
        },
        "minimal_actions": [(str(read), lengths) for read, lengths in minimal],
        "bellman_rows": exact_rows,
        "guard_matches_bellman_through_horizon": len(values) - 1,
        "two_block_replay": replay,
        "two_block_census": two_block_census,
        "guard_32_5": guard,
        "probability_phase": probability_phase,
        "finite_iid_alphabets": finite_alphabets,
        "markov_guard": markov_guard,
        "vanishing_maximum_guard": vanishing_guard,
        "stationary_renewal_source": stationary_renewal,
        "stationary_predictor_rectangle": stationary_predictor,
        "variable_support_mean_payoff": variable_support,
        "competing_cycle_mean_payoff": competing_cycles,
        "theorem_sentinels": sentinels,
        "checks": checks,
        "pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
