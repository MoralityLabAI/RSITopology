"""Independent verifier for the ASMP-4 heterogeneous port-cost theorem."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROBABILITIES = (
    Fraction(1, 2),
    Fraction(1, 4),
    Fraction(1, 8),
    Fraction(1, 8),
)
SHAPES = {
    "huffman": ("0", "10", "110", "111"),
    "balanced": ("00", "01", "10", "11"),
}


@lru_cache(maxsize=None)
def independent_full_shapes(leaves: int) -> tuple[tuple[str, ...], ...]:
    if leaves == 1:
        return (("",),)
    shapes = set()
    for left_count in range(1, leaves):
        for left in independent_full_shapes(left_count):
            for right in independent_full_shapes(leaves - left_count):
                shapes.add(
                    tuple(
                        sorted(
                            tuple("0" + word for word in left)
                            + tuple("1" + word for word in right)
                        )
                    )
                )
    return tuple(sorted(shapes))


def independent_prefix_free(words: tuple[str, ...]) -> bool:
    for left_index, left in enumerate(words):
        for right_index, right in enumerate(words):
            if left_index != right_index and right.startswith(left):
                return False
    return len(set(words)) == len(words)


def independent_causal(
    input_words: tuple[str, ...], output_words: tuple[str, ...]
) -> bool:
    horizon = max(max(map(len, input_words)), max(map(len, output_words)))
    for tick in range(1, horizon + 1):
        input_partition: dict[str, list[int]] = {}
        for plan, word in enumerate(input_words):
            prefix = word[: min(tick, len(word))]
            input_partition.setdefault(prefix, []).append(plan)
        for block in input_partition.values():
            output_prefixes = {
                output_words[plan][: min(tick, len(output_words[plan]))]
                for plan in block
            }
            if len(output_prefixes) != 1:
                return False
    return True


def independent_safe_replay(
    input_words: tuple[str, ...], output_words: tuple[str, ...]
) -> tuple[int, list[int]]:
    """Construct the realized factor table and replay all terminal controls."""

    horizon = max(max(map(len, input_words)), max(map(len, output_words)))
    table: dict[tuple[int, str], str] = {}
    for plan in range(4):
        for tick in range(1, horizon + 1):
            input_prefix = input_words[plan][: min(tick, len(input_words[plan]))]
            output_prefix = output_words[plan][: min(tick, len(output_words[plan]))]
            key = (tick, input_prefix)
            if key in table and table[key] != output_prefix:
                return 0, [plan]
            table[key] = output_prefix
    failures = []
    for plan in range(4):
        produced = ""
        for tick in range(1, horizon + 1):
            input_prefix = input_words[plan][: min(tick, len(input_words[plan]))]
            next_prefix = table[(tick, input_prefix)]
            if not next_prefix.startswith(produced):
                failures.append(plan)
                break
            produced = next_prefix
        if produced != output_words[plan]:
            failures.append(plan)
    return 4, failures


def independent_matrix() -> dict[str, object]:
    rows = []
    safe_replays = 0
    replay_failures = []
    for input_name, input_shape in SHAPES.items():
        for output_name, output_shape in SHAPES.items():
            feasible = 0
            expected_costs = []
            for input_words in itertools.permutations(input_shape):
                expected = sum(
                    probability * len(word)
                    for probability, word in zip(
                        PROBABILITIES, input_words, strict=True
                    )
                )
                for output_words in itertools.permutations(output_shape):
                    if independent_causal(input_words, output_words):
                        feasible += 1
                        expected_costs.append(expected)
                        replay_count, failures = independent_safe_replay(
                            input_words, output_words
                        )
                        safe_replays += replay_count
                        replay_failures.extend(
                            {
                                "input": input_name,
                                "output": output_name,
                                "plan": plan,
                            }
                            for plan in failures
                        )
            rows.append(
                {
                    "input": input_name,
                    "output": output_name,
                    "feasible": feasible,
                    "minimum_expected": (
                        None if not expected_costs else str(min(expected_costs))
                    ),
                    "worst_output": (
                        None if not expected_costs else max(map(len, output_shape))
                    ),
                }
            )
    return {
        "rows": rows,
        "checked": 4 * 24 * 24,
        "safe_replays": safe_replays,
        "replay_failures": replay_failures,
    }


def independent_complete_universe() -> dict[str, object]:
    codebooks = tuple(
        assignment
        for shape in independent_full_shapes(4)
        for assignment in itertools.permutations(shape)
    )
    feasible = 0
    safe_replays = 0
    failures = []
    points: set[tuple[Fraction, int]] = set()
    for input_words in codebooks:
        read_cost = sum(
            probability * len(word)
            for probability, word in zip(PROBABILITIES, input_words, strict=True)
        )
        for output_words in codebooks:
            if not independent_causal(input_words, output_words):
                continue
            feasible += 1
            replay_count, replay_failures = independent_safe_replay(
                input_words, output_words
            )
            safe_replays += replay_count
            failures.extend(replay_failures)
            points.add((read_cost, max(map(len, output_words))))
    minima = [
        point
        for point in sorted(points)
        if not any(
            other != point and other[0] <= point[0] and other[1] <= point[1]
            for other in points
        )
    ]
    return {
        "shapes": len(independent_full_shapes(4)),
        "codebooks": len(codebooks),
        "pairs": len(codebooks) ** 2,
        "feasible": feasible,
        "safe_replays": safe_replays,
        "failures": failures,
        "pareto": [(str(read), write) for read, write in minima],
    }


def independent_probability_phase(total_mass: int = 16) -> dict[str, object]:
    codebooks = tuple(
        assignment
        for shape in independent_full_shapes(4)
        for assignment in itertools.permutations(shape)
    )
    feasible_pairs = tuple(
        (input_words, max(map(len, output_words)))
        for input_words in codebooks
        for output_words in codebooks
        if independent_causal(input_words, output_words)
    )
    rows = []
    for first in range(1, total_mass):
        for second in range(1, first + 1):
            for third in range(1, second + 1):
                fourth = total_mass - first - second - third
                if not 1 <= fourth <= third:
                    continue
                masses = (first, second, third, fourth)
                probabilities = tuple(Fraction(value, total_mass) for value in masses)
                points = {
                    (
                        sum(
                            probability * len(word)
                            for probability, word in zip(
                                probabilities, input_words, strict=True
                            )
                        ),
                        write_worst,
                    )
                    for input_words, write_worst in feasible_pairs
                }
                minima = [
                    point
                    for point in sorted(points)
                    if not any(
                        other != point and other[0] <= point[0] and other[1] <= point[1]
                        for other in points
                    )
                ]
                skew = 2 * first + second > total_mass
                boundary = 2 * first + second == total_mass
                predicted = (
                    [
                        (
                            Fraction(3 * total_mass - 2 * first - second, total_mass),
                            3,
                        ),
                        (Fraction(2), 2),
                    ]
                    if skew
                    else [(Fraction(2), 2)]
                )
                rows.append(
                    {
                        "phase": (
                            "skew" if skew else "boundary" if boundary else "balanced"
                        ),
                        "matches": minima == predicted,
                    }
                )
    return {
        "laws": len(rows),
        "skew": sum(row["phase"] == "skew" for row in rows),
        "boundary": sum(row["phase"] == "boundary" for row in rows),
        "balanced": sum(row["phase"] == "balanced" for row in rows),
        "pass": all(row["matches"] for row in rows),
    }


def independent_minimal_plan_count() -> list[int]:
    laws = {
        1: (Fraction(1),),
        2: (Fraction(3, 4), Fraction(1, 4)),
        3: (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
        4: PROBABILITIES,
    }
    frontier_sizes = []
    for plans, probabilities in laws.items():
        codebooks = tuple(
            assignment
            for shape in independent_full_shapes(plans)
            for assignment in itertools.permutations(shape)
        )
        points = {
            (
                sum(
                    probability * len(word)
                    for probability, word in zip(
                        probabilities, input_words, strict=True
                    )
                ),
                max(map(len, output_words)),
            )
            for input_words in codebooks
            for output_words in codebooks
            if independent_causal(input_words, output_words)
        }
        minima = [
            point
            for point in points
            if not any(
                other != point and other[0] <= point[0] and other[1] <= point[1]
                for other in points
            )
        ]
        frontier_sizes.append(len(minima))
    return frontier_sizes


def independent_schedule_check(max_blocks: int = 17) -> dict[str, object]:
    rows = []
    for blocks in range(1, max_blocks + 1):
        for huffman_blocks in range(blocks + 1):
            read_total = Fraction(7, 4) * huffman_blocks + 2 * (blocks - huffman_blocks)
            write_total = 3 * huffman_blocks + 2 * (blocks - huffman_blocks)
            rows.append(
                {
                    "blocks": blocks,
                    "huffman_blocks": huffman_blocks,
                    "identity": 4 * read_total + write_total == 10 * blocks,
                }
            )
    return {
        "rows": len(rows),
        "pass": all(row["identity"] for row in rows),
        "lower_corner_excluded": not any(
            Fraction(7, 4) * row["blocks"]
            == Fraction(7, 4) * row["huffman_blocks"]
            + 2 * (row["blocks"] - row["huffman_blocks"])
            and 2 * row["blocks"]
            == 3 * row["huffman_blocks"] + 2 * (row["blocks"] - row["huffman_blocks"])
            for row in rows
        ),
    }


def theorem_sentinels() -> dict[str, bool]:
    theorem = (HERE / "THEOREM.md").read_text(encoding="utf-8")
    result = (HERE / "RESULT.md").read_text(encoding="utf-8")
    audit = (HERE / "COMPLETION_AUDIT_v0_4.md").read_text(encoding="utf-8")
    prior_art = (HERE / "PRIOR_ART_AUDIT_v0_4.md").read_text(encoding="utf-8")
    return {
        "unit_theorem": (
            "**Theorem 1 (unit-rescaled collapse).**" in theorem
            and "[a_r h_J, infinity) x [a_w h_J, infinity)" in theorem
        ),
        "sublinear_uniformity": "sup_L |e_(q,T)(L)| / T -> 0" in theorem,
        "heterogeneous_sandwich": (
            "**Theorem 2 (heterogeneous diagonal sandwich).**" in theorem
            and "E_K is a subset of closure(R_K^(J_r,J_w))" in theorem
        ),
        "causal_criterion": (
            "deterministic synchronous" in theorem
            and "transducer exists exactly when" in theorem
        ),
        "matrix_counts": (
            "| Huffman | Huffman | 48 |" in theorem
            and "| Huffman | balanced | 0 |" in theorem
            and "| balanced | Huffman | 0 |" in theorem
            and "| balanced | balanced | 192 |" in theorem
        ),
        "finite_corner_excluded": (
            "The coordinatewise infimum `(7/4,2)` is not achievable." in theorem
        ),
        "unrestricted_prefix_theorem": (
            "**Theorem 3 (complete four-plan binary-prefix frontier).**" in theorem
            and "Over all finite" in theorem
            and "binary prefix-free read and write codebooks" in theorem
            and "Exactly 960 pairs are causal" in theorem
            and "all 3,840 plan-specific" in theorem
        ),
        "probability_phase_and_minimality": (
            "**Theorem 4 (four-plan skew-law phase).**" in theorem
            and "E_H(p) = 3 - 2 p_1 - p_2" in theorem
            and "If `2 p_1+p_2>1`" in theorem
            and "Four plans are minimal for this phenomenon." in theorem
            and "27 strict-skew laws" in theorem
        ),
        "bilateral_copy_retained": "fixture retains bilateral copy closure" in theorem,
        "asymptotic_frontier": (
            "upward-closure conv{(7/12,1), (2/3,2/3)}" in theorem
            and "coordinatewise lower corner `(7/12,2/3)` is excluded" in result
        ),
        "scope_firewall": (
            "not a counterexample to the frozen" in theorem
            and "boundary strengthening, not a new ASMP-4 resolution claim" in result
        ),
        "completion_audit": (
            "## Requirement-by-requirement evidence" in audit
            and "## Remaining review frontier" in audit
            and "not another parameter sweep" in audit
        ),
        "prior_art_firewall": (
            "This targeted primary-source audit supports the scope boundary"
            in prior_art
            and "support a broad mathematical novelty claim" in prior_art
            and "Cascade multiterminal source coding" in prior_art
            and "Network entropy and data rates required for networked control"
            in prior_art
            and "remains an external-review question" in prior_art
        ),
    }


def canonical_scope_check() -> dict[str, bool]:
    canonical = (HERE.parent / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md").read_text(
        encoding="utf-8"
    )
    start = canonical.index("# ASMP-4")
    stop = canonical.index("\n---", start)
    section = canonical[start:stop]
    return {
        "same_read_cardinality_formula": (
            "r_r(C) = limsup_" in section and "log2 |M_r^C(T)|" in section
        ),
        "same_write_cardinality_formula": (
            "r_w(C) = limsup_" in section and "log2 |M_w^C(T)|" in section
        ),
        "expected_variant_must_be_explicit": (
            "Variable-length variants must charge prefix-free" in section
            and "expected length explicitly" in section
        ),
        "no_side_channels": "uncharged side channel" in section,
    }


def boundary_claim_check() -> dict[str, bool]:
    claim = json.loads((HERE / "boundary_claim_v0_4.json").read_text(encoding="utf-8"))
    return {
        "problem_id": claim["problem_id"] == "ASMP-4",
        "not_new_resolution": claim["status"]
        == "boundary_strengthening_not_new_resolution",
        "canonical_metric_unchanged": claim["canonical_metric_unchanged"] is True,
        "canonical_resolution_preserved": claim["canonical_resolution_preserved"]
        is True,
        "fixed_authority": claim["heterogeneous_fixture"]["control_authority_fixed"]
        is True,
        "no_side_channels": claim["heterogeneous_fixture"]["side_channels"] is False,
        "unrestricted_codebooks": claim["heterogeneous_fixture"]["codebook_class"]
        == "all finite binary prefix-free read/write codebooks",
        "three_tick_deadline": claim["heterogeneous_fixture"]["terminal_deadline_ticks"]
        == 3,
    }


def verify() -> dict[str, object]:
    matrix = independent_matrix()
    complete_universe = independent_complete_universe()
    probability_phase = independent_probability_phase()
    minimal_plans = independent_minimal_plan_count()
    indexed = {(row["input"], row["output"]): row for row in matrix["rows"]}
    schedules = independent_schedule_check()
    sentinels = theorem_sentinels()
    canonical = canonical_scope_check()
    claim = boundary_claim_check()
    checks = {
        "I0_independent_prefix_shapes": all(
            independent_prefix_free(words) for words in SHAPES.values()
        ),
        "I1_independent_transducer_matrix": (
            matrix["checked"] == 2304
            and matrix["safe_replays"] == 960
            and not matrix["replay_failures"]
            and indexed[("huffman", "huffman")]["feasible"] == 48
            and indexed[("huffman", "balanced")]["feasible"] == 0
            and indexed[("balanced", "huffman")]["feasible"] == 0
            and indexed[("balanced", "balanced")]["feasible"] == 192
        ),
        "I2_independent_cost_points": (
            indexed[("huffman", "huffman")]["minimum_expected"] == "7/4"
            and indexed[("huffman", "huffman")]["worst_output"] == 3
            and indexed[("balanced", "balanced")]["minimum_expected"] == "2"
            and indexed[("balanced", "balanced")]["worst_output"] == 2
        ),
        "I3_independent_schedule_frontier": schedules["pass"]
        and schedules["rows"] == 170
        and schedules["lower_corner_excluded"],
        "I4_independent_complete_prefix_universe": complete_universe
        == {
            "shapes": 5,
            "codebooks": 120,
            "pairs": 14400,
            "feasible": 960,
            "safe_replays": 3840,
            "failures": [],
            "pareto": [("7/4", 3), ("2", 2)],
        },
        "I5_independent_skew_probability_phase": probability_phase
        == {
            "laws": 34,
            "skew": 27,
            "boundary": 2,
            "balanced": 5,
            "pass": True,
        },
        "I6_independent_minimal_plan_count": minimal_plans == [1, 1, 1, 2],
        "I7_theorem_structure": all(sentinels.values()),
        "I8_frozen_canonical_scope": all(canonical.values()),
        "I9_boundary_claim_firewall": all(claim.values()),
    }
    return {
        "schema_version": "asmp4_heterogeneous_port_costs_independent_v0_4",
        "matrix": matrix,
        "complete_prefix_universe": complete_universe,
        "probability_phase": probability_phase,
        "minimal_plan_frontier_sizes": minimal_plans,
        "schedules": schedules,
        "theorem_sentinels": sentinels,
        "canonical_scope": canonical,
        "boundary_claim": claim,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    payload = verify()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
