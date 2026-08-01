"""Exact instruments for heterogeneous ASMP-4 port-cost frontiers."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from functools import lru_cache
from typing import Any, Iterable, Sequence


PLANS = tuple(range(4))
PLAN_PROBABILITIES = (
    Fraction(1, 2),
    Fraction(1, 4),
    Fraction(1, 8),
    Fraction(1, 8),
)
CODEBOOK_SHAPES = {
    "huffman": ("0", "10", "110", "111"),
    "balanced": ("00", "01", "10", "11"),
}


@lru_cache(maxsize=None)
def full_binary_shapes(leaves: int) -> tuple[tuple[str, ...], ...]:
    """Enumerate every ordered full binary prefix-tree shape."""

    if leaves < 1:
        raise ValueError("a prefix tree must have at least one leaf")
    if leaves == 1:
        return (("",),)
    shapes: set[tuple[str, ...]] = set()
    for left_leaves in range(1, leaves):
        right_leaves = leaves - left_leaves
        for left in full_binary_shapes(left_leaves):
            for right in full_binary_shapes(right_leaves):
                words = tuple(f"0{word}" for word in left) + tuple(
                    f"1{word}" for word in right
                )
                shapes.add(tuple(sorted(words)))
    return tuple(sorted(shapes))


def labelled_full_codebooks() -> tuple[tuple[str, ...], ...]:
    """All four-plan labellings of all full binary tree shapes."""

    return tuple(
        assignment
        for shape in full_binary_shapes(len(PLANS))
        for assignment in itertools.permutations(shape)
    )


def is_prefix_free(words: Sequence[str]) -> bool:
    """Return whether the distinct binary words form a prefix-free code."""

    return len(set(words)) == len(words) and all(
        not right.startswith(left) for left in words for right in words if left != right
    )


def observed_prefix(word: str, tick: int) -> str:
    """Prefix visible by a synchronous tick, with completion itself visible."""

    if tick < 0:
        raise ValueError("tick must be nonnegative")
    return word[: min(tick, len(word))]


def causal_conflict(
    input_words: Sequence[str], output_words: Sequence[str]
) -> dict[str, int | str] | None:
    """Find a no-lag causality violation for one plan-labelled codebook pair."""

    if len(input_words) != len(output_words):
        raise ValueError("input and output codebooks must label the same plans")
    horizon = max(max(map(len, input_words)), max(map(len, output_words)))
    for tick in range(1, horizon + 1):
        for left, right in itertools.combinations(range(len(input_words)), 2):
            input_left = observed_prefix(input_words[left], tick)
            input_right = observed_prefix(input_words[right], tick)
            output_left = observed_prefix(output_words[left], tick)
            output_right = observed_prefix(output_words[right], tick)
            if input_left == input_right and output_left != output_right:
                return {
                    "tick": tick,
                    "left_plan": left,
                    "right_plan": right,
                    "shared_input_prefix": input_left,
                    "left_output_prefix": output_left,
                    "right_output_prefix": output_right,
                }
    return None


def causal_no_lag(input_words: Sequence[str], output_words: Sequence[str]) -> bool:
    """Test existence of a deterministic synchronous prefix transducer."""

    return causal_conflict(input_words, output_words) is None


def synthesize_prefix_transducer(
    input_words: Sequence[str], output_words: Sequence[str]
) -> dict[tuple[int, str], str]:
    """Construct the realized-prefix table when the factor is causal."""

    conflict = causal_conflict(input_words, output_words)
    if conflict is not None:
        raise ValueError(f"codebooks have a causal conflict: {conflict}")
    horizon = max(max(map(len, input_words)), max(map(len, output_words)))
    table: dict[tuple[int, str], str] = {}
    for plan in range(len(input_words)):
        for tick in range(1, horizon + 1):
            key = (tick, observed_prefix(input_words[plan], tick))
            value = observed_prefix(output_words[plan], tick)
            prior = table.setdefault(key, value)
            if prior != value:
                raise AssertionError("causality check admitted a multivalued table")
    return table


def replay_terminal_control(
    input_words: Sequence[str],
    output_words: Sequence[str],
    plan: int,
    table: dict[tuple[int, str], str],
) -> dict[str, Any]:
    """Replay one disturbance plan and its plan-specific terminal control."""

    horizon = max(max(map(len, input_words)), max(map(len, output_words)))
    produced_prefix = ""
    prefix_consistent = True
    for tick in range(1, horizon + 1):
        input_prefix = observed_prefix(input_words[plan], tick)
        produced = table[(tick, input_prefix)]
        if not produced.startswith(produced_prefix):
            prefix_consistent = False
        produced_prefix = produced
    decoded_plan = output_words.index(produced_prefix)
    return {
        "plan": plan,
        "produced_output_word": produced_prefix,
        "decoded_plan": decoded_plan,
        "terminal_control": f"u_{decoded_plan}",
        "safe": prefix_consistent and decoded_plan == plan,
    }


def expected_length(words: Sequence[str]) -> Fraction:
    """Expected input length under the registered four-plan law."""

    return expected_length_for(words, PLAN_PROBABILITIES)


def expected_length_for(
    words: Sequence[str], probabilities: Sequence[Fraction]
) -> Fraction:
    """Expected prefix length for an explicitly supplied plan law."""

    if len(words) != len(probabilities):
        raise ValueError("words and probabilities must label the same plans")
    if sum(probabilities) != 1 or any(value < 0 for value in probabilities):
        raise ValueError("probabilities must be nonnegative and sum to one")
    return sum(
        (
            probability * len(word)
            for probability, word in zip(probabilities, words, strict=True)
        ),
        start=Fraction(0),
    )


def _fraction_payload(value: Fraction) -> dict[str, int | float | str]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "exact": str(value),
        "float": float(value),
    }


def enumerate_format_matrix() -> dict[str, Any]:
    """Exhaust all 24 x 24 plan labellings for every format pair."""

    rows = []
    for input_format, input_shape in CODEBOOK_SHAPES.items():
        for output_format, output_shape in CODEBOOK_SHAPES.items():
            feasible_assignments = 0
            best_expected: Fraction | None = None
            conflict_example = None
            for input_words in itertools.permutations(input_shape):
                input_cost = expected_length(input_words)
                for output_words in itertools.permutations(output_shape):
                    conflict = causal_conflict(input_words, output_words)
                    if conflict is None:
                        feasible_assignments += 1
                        if best_expected is None or input_cost < best_expected:
                            best_expected = input_cost
                    elif conflict_example is None:
                        conflict_example = {
                            **conflict,
                            "input_words": input_words,
                            "output_words": output_words,
                        }
            rows.append(
                {
                    "input_format": input_format,
                    "output_format": output_format,
                    "assignments_checked": 24 * 24,
                    "feasible_assignments": feasible_assignments,
                    "feasible": feasible_assignments > 0,
                    "best_expected_read_length": (
                        None
                        if best_expected is None
                        else _fraction_payload(best_expected)
                    ),
                    "worst_write_length": (
                        None if best_expected is None else max(map(len, output_shape))
                    ),
                    "conflict_example": conflict_example,
                }
            )
    return {
        "rows": rows,
        "assignments_checked": sum(row["assignments_checked"] for row in rows),
    }


def _pareto_minima(
    points: Iterable[tuple[Fraction, int]],
) -> list[tuple[Fraction, int]]:
    unique = sorted(set(points))
    return [
        point
        for point in unique
        if not any(
            other != point and other[0] <= point[0] and other[1] <= point[1]
            for other in unique
        )
    ]


def finite_prefix_frontier_report() -> dict[str, Any]:
    """Compute the exact finite heterogeneous-cost Pareto frontier."""

    matrix = enumerate_format_matrix()
    points = []
    for row in matrix["rows"]:
        expected = row["best_expected_read_length"]
        if expected is not None:
            points.append(
                (
                    Fraction(expected["numerator"], expected["denominator"]),
                    row["worst_write_length"],
                )
            )
    minima = _pareto_minima(points)
    coordinate_infimum = (
        min(point[0] for point in points),
        min(point[1] for point in points),
    )
    return {
        "matrix": matrix,
        "pareto_minima": [
            {
                "expected_read_length": _fraction_payload(read),
                "worst_write_length": write,
            }
            for read, write in minima
        ],
        "coordinatewise_infimum": {
            "expected_read_length": _fraction_payload(coordinate_infimum[0]),
            "worst_write_length": coordinate_infimum[1],
        },
        "coordinatewise_infimum_achievable": coordinate_infimum in points,
    }


def exhaustive_safe_replay_report() -> dict[str, Any]:
    """Synthesize every feasible transducer and replay every terminal action."""

    feasible_transducers = 0
    plan_replays = 0
    failures = []
    by_format_pair: dict[str, int] = {}
    for input_format, input_shape in CODEBOOK_SHAPES.items():
        for output_format, output_shape in CODEBOOK_SHAPES.items():
            pair_key = f"{input_format}->{output_format}"
            by_format_pair[pair_key] = 0
            for input_words in itertools.permutations(input_shape):
                for output_words in itertools.permutations(output_shape):
                    if not causal_no_lag(input_words, output_words):
                        continue
                    table = synthesize_prefix_transducer(input_words, output_words)
                    feasible_transducers += 1
                    by_format_pair[pair_key] += 1
                    for plan in PLANS:
                        replay = replay_terminal_control(
                            input_words, output_words, plan, table
                        )
                        plan_replays += 1
                        if not replay["safe"]:
                            failures.append(
                                {
                                    "input_format": input_format,
                                    "output_format": output_format,
                                    **replay,
                                }
                            )
    return {
        "feasible_transducers": feasible_transducers,
        "plan_replays": plan_replays,
        "by_format_pair": by_format_pair,
        "failures": failures,
        "pass": not failures,
    }


def complete_prefix_universe_report() -> dict[str, Any]:
    """Enumerate every pair of four-leaf full binary prefix trees."""

    codebooks = labelled_full_codebooks()
    feasible_pairs = 0
    plan_replays = 0
    failures = []
    point_counts: dict[tuple[Fraction, int], int] = {}
    for input_words in codebooks:
        read_cost = expected_length(input_words)
        for output_words in codebooks:
            if not causal_no_lag(input_words, output_words):
                continue
            feasible_pairs += 1
            point = (read_cost, max(map(len, output_words)))
            point_counts[point] = point_counts.get(point, 0) + 1
            table = synthesize_prefix_transducer(input_words, output_words)
            for plan in PLANS:
                replay = replay_terminal_control(input_words, output_words, plan, table)
                plan_replays += 1
                if not replay["safe"]:
                    failures.append(replay)
    minima = _pareto_minima(point_counts)
    return {
        "full_tree_shapes": len(full_binary_shapes(len(PLANS))),
        "labelled_codebooks": len(codebooks),
        "codebook_pairs_checked": len(codebooks) ** 2,
        "feasible_pairs": feasible_pairs,
        "plan_replays": plan_replays,
        "point_histogram": [
            {
                "expected_read_length": _fraction_payload(point[0]),
                "worst_write_length": point[1],
                "feasible_pairs": count,
            }
            for point, count in sorted(point_counts.items())
        ],
        "pareto_minima": [
            {
                "expected_read_length": _fraction_payload(point[0]),
                "worst_write_length": point[1],
            }
            for point in minima
        ],
        "failures": failures,
        "pass": not failures,
    }


def ordered_probability_laws(total_mass: int = 16) -> tuple[tuple[int, ...], ...]:
    """Positive nonincreasing four-part rational laws with fixed denominator."""

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


def skew_probability_phase_report(total_mass: int = 16) -> dict[str, Any]:
    """Check the exact four-plan skew-law phase criterion on a rational grid."""

    codebooks = labelled_full_codebooks()
    feasible_pairs = tuple(
        (input_words, max(map(len, output_words)))
        for input_words in codebooks
        for output_words in codebooks
        if causal_no_lag(input_words, output_words)
    )
    rows = []
    for masses in ordered_probability_laws(total_mass):
        probabilities = tuple(Fraction(value, total_mass) for value in masses)
        points = {
            (expected_length_for(input_words, probabilities), write_worst)
            for input_words, write_worst in feasible_pairs
        }
        minima = _pareto_minima(points)
        skew = 2 * masses[0] + masses[1] > total_mass
        boundary = 2 * masses[0] + masses[1] == total_mass
        unbalanced_cost = Fraction(
            3 * total_mass - 2 * masses[0] - masses[1], total_mass
        )
        predicted = (
            [(unbalanced_cost, 3), (Fraction(2), 2)] if skew else [(Fraction(2), 2)]
        )
        rows.append(
            {
                "masses": masses,
                "probabilities": [str(value) for value in probabilities],
                "two_p1_plus_p2": str(2 * probabilities[0] + probabilities[1]),
                "phase": "skew" if skew else "boundary" if boundary else "balanced",
                "pareto": [(str(read), write) for read, write in minima],
                "predicted": [(str(read), write) for read, write in predicted],
                "matches": minima == predicted,
            }
        )
    return {
        "total_mass": total_mass,
        "laws": len(rows),
        "skew_laws": sum(row["phase"] == "skew" for row in rows),
        "boundary_laws": sum(row["phase"] == "boundary" for row in rows),
        "balanced_laws": sum(row["phase"] == "balanced" for row in rows),
        "rows": rows,
        "pass": all(row["matches"] for row in rows),
    }


def minimal_plan_count_report() -> dict[str, Any]:
    """Confirm that four plans are the first full-tree tradeoff witness."""

    laws = {
        1: (Fraction(1),),
        2: (Fraction(3, 4), Fraction(1, 4)),
        3: (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
        4: PLAN_PROBABILITIES,
    }
    rows = []
    for plans, probabilities in laws.items():
        codebooks = tuple(
            assignment
            for shape in full_binary_shapes(plans)
            for assignment in itertools.permutations(shape)
        )
        points = {
            (
                expected_length_for(input_words, probabilities),
                max(map(len, output_words)),
            )
            for input_words in codebooks
            for output_words in codebooks
            if causal_no_lag(input_words, output_words)
        }
        minima = _pareto_minima(points)
        rows.append(
            {
                "plans": plans,
                "full_shapes": len(full_binary_shapes(plans)),
                "labelled_codebooks": len(codebooks),
                "pareto": [(str(read), write) for read, write in minima],
            }
        )
    return {
        "rows": rows,
        "pass": [len(row["pareto"]) for row in rows] == [1, 1, 1, 2],
    }


def periodic_time_sharing_report(max_blocks: int = 12) -> dict[str, Any]:
    """Enumerate every public fixed format schedule through max_blocks."""

    if max_blocks < 1:
        raise ValueError("max_blocks must be positive")
    rows = []
    for blocks in range(1, max_blocks + 1):
        for huffman_blocks in range(blocks + 1):
            balanced_blocks = blocks - huffman_blocks
            read_total = Fraction(7, 4) * huffman_blocks + 2 * balanced_blocks
            write_total = 3 * huffman_blocks + 2 * balanced_blocks
            rows.append(
                {
                    "blocks": blocks,
                    "huffman_blocks": huffman_blocks,
                    "balanced_blocks": balanced_blocks,
                    "expected_read_total": _fraction_payload(read_total),
                    "worst_write_total": write_total,
                    "expected_read_per_block": _fraction_payload(read_total / blocks),
                    "worst_write_per_block": _fraction_payload(
                        Fraction(write_total, blocks)
                    ),
                    "expected_read_per_tick": _fraction_payload(
                        read_total / (3 * blocks)
                    ),
                    "worst_write_per_tick": _fraction_payload(
                        Fraction(write_total, 3 * blocks)
                    ),
                    "frontier_identity": 4 * read_total + write_total == 10 * blocks,
                }
            )
    return {
        "rows": rows,
        "schedule_count": len(rows),
        "per_block_segment": {
            "huffman_endpoint": ["7/4", "3"],
            "balanced_endpoint": ["2", "2"],
            "line": "R_w = 10 - 4 R_r",
        },
        "per_tick_segment": {
            "huffman_endpoint": ["7/12", "1"],
            "balanced_endpoint": ["2/3", "2/3"],
            "line": "R_w = 10/3 - 4 R_r",
        },
        "pass": all(row["frontier_identity"] for row in rows),
    }


def unit_rescaling_report() -> dict[str, Any]:
    """Exhaust positive rational unit scales on representative base costs."""

    base_costs = tuple(Fraction(value, 2) for value in range(3, 9))
    rows = []
    for read_numerator in range(1, 6):
        for read_denominator in range(1, 5):
            for write_numerator in range(1, 6):
                for write_denominator in range(1, 5):
                    read_scale = Fraction(read_numerator, read_denominator)
                    write_scale = Fraction(write_numerator, write_denominator)
                    read_argmin = min(
                        range(len(base_costs)),
                        key=lambda index: read_scale * base_costs[index],
                    )
                    write_argmin = min(
                        range(len(base_costs)),
                        key=lambda index: write_scale * base_costs[index],
                    )
                    rows.append(
                        {
                            "read_scale": str(read_scale),
                            "write_scale": str(write_scale),
                            "read_argmin": read_argmin,
                            "write_argmin": write_argmin,
                            "common_base_argmin": read_argmin == write_argmin == 0,
                        }
                    )
    return {
        "rows_checked": len(rows),
        "pass": all(row["common_base_argmin"] for row in rows),
    }


def verification_payload() -> dict[str, Any]:
    frontier = finite_prefix_frontier_report()
    matrix_rows = {
        (row["input_format"], row["output_format"]): row
        for row in frontier["matrix"]["rows"]
    }
    schedules = periodic_time_sharing_report()
    rescaling = unit_rescaling_report()
    safe_replay = exhaustive_safe_replay_report()
    complete_universe = complete_prefix_universe_report()
    probability_phase = skew_probability_phase_report()
    minimal_plans = minimal_plan_count_report()
    expected_minima = [
        (row["expected_read_length"]["exact"], row["worst_write_length"])
        for row in frontier["pareto_minima"]
    ]
    gates = {
        "H0_registered_shapes_are_prefix_free": all(
            is_prefix_free(words) for words in CODEBOOK_SHAPES.values()
        ),
        "H1_exhaustive_transducer_matrix": (
            frontier["matrix"]["assignments_checked"] == 2304
            and matrix_rows[("huffman", "huffman")]["feasible_assignments"] == 48
            and matrix_rows[("huffman", "balanced")]["feasible_assignments"] == 0
            and matrix_rows[("balanced", "huffman")]["feasible_assignments"] == 0
            and matrix_rows[("balanced", "balanced")]["feasible_assignments"] == 192
        ),
        "H2_exact_finite_pareto_frontier": expected_minima == [("7/4", 3), ("2", 2)],
        "H3_coordinatewise_infimum_is_excluded": (
            frontier["coordinatewise_infimum"]["expected_read_length"]["exact"] == "7/4"
            and frontier["coordinatewise_infimum"]["worst_write_length"] == 2
            and not frontier["coordinatewise_infimum_achievable"]
        ),
        "H4_exact_periodic_time_sharing_segment": schedules["pass"]
        and schedules["schedule_count"] == 90,
        "H5_positive_unit_rescaling_preserves_the_common_minimizer": (
            rescaling["pass"] and rescaling["rows_checked"] == 400
        ),
        "H6_every_feasible_transducer_replays_all_terminal_controls": (
            safe_replay["pass"]
            and safe_replay["feasible_transducers"] == 240
            and safe_replay["plan_replays"] == 960
            and safe_replay["by_format_pair"]
            == {
                "huffman->huffman": 48,
                "huffman->balanced": 0,
                "balanced->huffman": 0,
                "balanced->balanced": 192,
            }
        ),
        "H7_complete_full_binary_prefix_universe": (
            complete_universe["pass"]
            and complete_universe["full_tree_shapes"] == 5
            and complete_universe["labelled_codebooks"] == 120
            and complete_universe["codebook_pairs_checked"] == 14400
            and complete_universe["feasible_pairs"] == 960
            and complete_universe["plan_replays"] == 3840
            and [
                (
                    row["expected_read_length"]["exact"],
                    row["worst_write_length"],
                )
                for row in complete_universe["pareto_minima"]
            ]
            == [("7/4", 3), ("2", 2)]
        ),
        "H8_exact_skew_probability_phase": (
            probability_phase["pass"]
            and probability_phase["laws"] == 34
            and probability_phase["skew_laws"] == 27
            and probability_phase["boundary_laws"] == 2
            and probability_phase["balanced_laws"] == 5
        ),
        "H9_four_plans_are_minimal_for_this_tradeoff": minimal_plans["pass"],
    }
    return {
        "schema_version": "asmp4_heterogeneous_port_costs_verification_v0_4",
        "fixture": {
            "plan_probabilities": [str(value) for value in PLAN_PROBABILITIES],
            "codebook_shapes": CODEBOOK_SHAPES,
            "synchronous_no_lag": True,
        },
        "frontier": frontier,
        "periodic_time_sharing": schedules,
        "unit_rescaling": rescaling,
        "safe_replay": safe_replay,
        "complete_prefix_universe": complete_universe,
        "skew_probability_phase": probability_phase,
        "minimal_plan_count": minimal_plans,
        "gates": gates,
        "pass": all(gates.values()),
    }


def main() -> int:
    payload = verification_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
