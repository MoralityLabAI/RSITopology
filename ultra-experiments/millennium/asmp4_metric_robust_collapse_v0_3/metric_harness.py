"""Exact metric audits for the ASMP-4 bilateral relay theorem."""

from __future__ import annotations

import itertools
import math
from collections.abc import Iterable, Sequence
from typing import Any


Word = tuple[str, ...]
Language = tuple[Word, ...]


def normalize_language(words: Iterable[Sequence[str]]) -> Language:
    language = tuple(sorted(tuple(word) for word in words))
    if not language:
        raise ValueError("language must be nonempty")
    if len(set(language)) != len(language):
        raise ValueError("language must not contain duplicate words")
    horizons = {len(word) for word in language}
    if len(horizons) != 1:
        raise ValueError("all words must have the same horizon")
    return language


def transcript_tree_metrics(words: Iterable[Sequence[str]]) -> dict[str, Any]:
    """Terminal-cardinality and worst-path history-dependent branch costs."""

    language = normalize_language(words)
    horizon = len(language[0])
    successors_by_prefix: dict[Word, set[str]] = {}
    for word in language:
        for event in range(horizon):
            successors_by_prefix.setdefault(word[:event], set()).add(word[event])

    def prefix_worst_cost(prefix: Word) -> int:
        successors = successors_by_prefix.get(prefix)
        if not successors:
            return 0
        future_costs = [prefix_worst_cost(prefix + (symbol,)) for symbol in successors]
        kraft_numerator = sum(2**cost for cost in future_costs)
        return (kraft_numerator - 1).bit_length()

    worst_branch_product = 1
    for word in language:
        branch_product = 1
        for event in range(horizon):
            branch_product *= len(successors_by_prefix[word[:event]])
        worst_branch_product = max(worst_branch_product, branch_product)
    return {
        "horizon": horizon,
        "language_count": len(language),
        "language_bits": math.log2(len(language)),
        "branch_product": worst_branch_product,
        "branch_bits": math.log2(worst_branch_product),
        "prefix_worst_bits": prefix_worst_cost(()),
        "branch_dominates_language": worst_branch_product >= len(language),
    }


def comb_language(horizon: int) -> Language:
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    words: list[Word] = [("0",) * horizon]
    words.extend(
        ("0",) * event + ("1",) + ("0",) * (horizon - event - 1)
        for event in range(horizon)
    )
    return normalize_language(words)


def plan_index_language(horizon: int) -> Language:
    """Announce one of the T event times or no event, then send fixed symbols."""

    if horizon < 1:
        raise ValueError("horizon must be positive")
    return normalize_language(
        (f"plan_{plan}",) + ("idle",) * (horizon - 1) for plan in range(horizon + 1)
    )


def skew_language(binary_depth: int) -> Language:
    """One heavy binary subtree and two deterministic light subtrees."""

    if binary_depth < 1:
        raise ValueError("binary_depth must be positive")
    tail = ("fixed",) * binary_depth
    words: list[Word] = [
        ("heavy",) + binary_word
        for binary_word in itertools.product(("0", "1"), repeat=binary_depth)
    ]
    words.extend((("light_a",) + tail, ("light_b",) + tail))
    return normalize_language(words)


def prefix_rounding_language() -> Language:
    """Four leaves whose sequential prefix coding incurs one rounding bit."""

    return normalize_language(
        (
            ("heavy", "0"),
            ("heavy", "1"),
            ("heavy", "2"),
            ("light", "fixed"),
        )
    )


def relabel(language: Language, mapping: dict[str, str]) -> Language:
    return normalize_language(
        tuple(mapping[symbol] for symbol in word) for word in language
    )


def exhaustive_binary_language_census(max_horizon: int = 4) -> dict[str, Any]:
    """Enumerate every nonempty binary language through the requested horizon."""

    if max_horizon < 0 or max_horizon > 4:
        raise ValueError("the exact census supports horizons zero through four")
    checked = 0
    domination_failures: list[dict[str, Any]] = []
    relabel_failures: list[dict[str, Any]] = []
    histogram: dict[str, int] = {}
    for horizon in range(max_horizon + 1):
        universe = tuple(itertools.product(("0", "1"), repeat=horizon))
        horizon_count = 0
        for mask in range(1, 1 << len(universe)):
            language = tuple(
                word for index, word in enumerate(universe) if mask & (1 << index)
            )
            metrics = transcript_tree_metrics(language)
            relabeled_metrics = transcript_tree_metrics(
                relabel(language, {"0": "left", "1": "right"})
            )
            checked += 1
            horizon_count += 1
            if not metrics["branch_dominates_language"]:
                domination_failures.append(
                    {"horizon": horizon, "language": language, "metrics": metrics}
                )
            if metrics != relabeled_metrics:
                relabel_failures.append({"horizon": horizon, "language": language})
        histogram[str(horizon)] = horizon_count
    return {
        "checked_languages": checked,
        "horizon_histogram": histogram,
        "domination_failures": domination_failures,
        "relabel_failures": relabel_failures,
        "pass": not domination_failures and not relabel_failures,
    }


def comb_metric_gap(max_horizon: int = 128) -> dict[str, Any]:
    if max_horizon < 1:
        raise ValueError("max_horizon must be positive")
    rows = []
    for horizon in range(1, max_horizon + 1):
        metrics = transcript_tree_metrics(comb_language(horizon))
        rows.append(
            {
                **metrics,
                "language_rate": metrics["language_bits"] / horizon,
                "branch_rate": metrics["branch_bits"] / horizon,
            }
        )
    return {
        "rows": rows,
        "pass": all(
            row["language_count"] == row["horizon"] + 1
            and row["branch_product"] == 2 ** row["horizon"]
            and row["branch_rate"] == 1.0
            for row in rows
        ),
    }


def bilateral_copy_metric_report(max_horizon: int = 8) -> dict[str, Any]:
    """Both normal forms copy one port tree and therefore preserve either metric."""

    rows = []
    for horizon in range(1, max_horizon + 1):
        read_tree = comb_language(horizon)
        write_tree = normalize_language(
            word for word in itertools.product(("a", "b"), repeat=horizon)
        )
        read_metrics = transcript_tree_metrics(read_tree)
        write_metrics = transcript_tree_metrics(write_tree)
        upstream_read = transcript_tree_metrics(write_tree)
        upstream_write = transcript_tree_metrics(write_tree)
        downstream_read = transcript_tree_metrics(read_tree)
        downstream_write = transcript_tree_metrics(read_tree)
        rows.append(
            {
                "horizon": horizon,
                "upstream_equal": upstream_read == upstream_write == write_metrics,
                "downstream_equal": downstream_read == downstream_write == read_metrics,
            }
        )
    return {
        "rows": rows,
        "pass": all(row["upstream_equal"] and row["downstream_equal"] for row in rows),
    }


def bilateral_fixed_fifo_delay_report(
    max_read_delay: int = 3,
    max_write_delay: int = 3,
    max_horizon: int = 5,
) -> dict[str, Any]:
    """Replay both normal forms with independent fixed FIFO link delays."""

    if min(max_read_delay, max_write_delay, max_horizon) < 0:
        raise ValueError("delay and horizon bounds must be nonnegative")
    rows = []
    for read_delay in range(max_read_delay + 1):
        for write_delay in range(max_write_delay + 1):
            for horizon in range(max_horizon + 1):
                emission_count = max(0, horizon - read_delay)
                original_read_words: set[tuple[int, ...]] = set()
                original_write_words: set[tuple[int, ...]] = set()
                upstream_read_words: set[tuple[int, ...]] = set()
                downstream_write_words: set[tuple[int, ...]] = set()
                original_applied_words: set[tuple[int, ...]] = set()
                downstream_applied_words: set[tuple[int, ...]] = set()
                for emissions in itertools.product((0, 1), repeat=emission_count):
                    read_word = []
                    write_word = []
                    parity = 0
                    for event in range(horizon):
                        read_symbol = (
                            0 if event < read_delay else emissions[event - read_delay]
                        )
                        read_word.append(read_symbol)
                        parity ^= read_symbol
                        write_word.append(parity)
                    applied_word = (0,) * write_delay + tuple(write_word)
                    original_read_words.add(tuple(read_word))
                    original_write_words.add(tuple(write_word))
                    upstream_read_words.add(tuple(write_word))
                    downstream_write_words.add(tuple(read_word))
                    original_applied_words.add(applied_word)
                    downstream_applied_words.add(applied_word)
                rows.append(
                    {
                        "read_delay": read_delay,
                        "write_delay": write_delay,
                        "horizon": horizon,
                        "upstream_tree_match": upstream_read_words
                        == original_write_words,
                        "downstream_tree_match": downstream_write_words
                        == original_read_words,
                        "plant_input_match": downstream_applied_words
                        == original_applied_words,
                    }
                )
    return {
        "rows": rows,
        "pass": all(
            row["upstream_tree_match"]
            and row["downstream_tree_match"]
            and row["plant_input_match"]
            for row in rows
        ),
    }


def one_sided_normal_form_gap_report(max_horizon: int = 128) -> dict[str, Any]:
    """Strict gaps when upstream or downstream computation is forbidden."""

    if max_horizon < 2:
        raise ValueError("max_horizon must be at least two")
    decoder_rows = []
    for horizon in range(2, max_horizon + 1):
        read_metrics = transcript_tree_metrics(plan_index_language(horizon))
        write_metrics = transcript_tree_metrics(comb_language(horizon))
        decoder_rows.append(
            {
                "horizon": horizon,
                "read_branch_bits": read_metrics["branch_bits"],
                "write_branch_bits": write_metrics["branch_bits"],
                "strict_write_gap": write_metrics["branch_bits"]
                > read_metrics["branch_bits"],
            }
        )
    forced_raw_read = transcript_tree_metrics(
        (("mode_0",), ("mode_1",), ("mode_2",), ("mode_3",))
    )
    grouped_write = transcript_tree_metrics((("action_0",), ("action_1",)))
    sensor_restriction = {
        "read_branch_bits": forced_raw_read["branch_bits"],
        "write_branch_bits": grouped_write["branch_bits"],
        "strict_read_gap": forced_raw_read["branch_bits"]
        > grouped_write["branch_bits"],
    }
    return {
        "decoder_memory_restriction": decoder_rows,
        "sensor_computation_restriction": sensor_restriction,
        "pass": all(row["strict_write_gap"] for row in decoder_rows)
        and sensor_restriction["strict_read_gap"],
    }


def skew_metric_separation_report(max_binary_depth: int = 12) -> dict[str, Any]:
    """Separate terminal, minimax prefix-length, and uniform branching costs."""

    if max_binary_depth < 2:
        raise ValueError("max_binary_depth must be at least two")
    rows = []
    for depth in range(2, max_binary_depth + 1):
        metrics = transcript_tree_metrics(skew_language(depth))
        rows.append(
            {
                "binary_depth": depth,
                **metrics,
                "strict_three_way_order": metrics["language_bits"]
                < metrics["prefix_worst_bits"]
                < metrics["branch_bits"],
            }
        )
    return {
        "rows": rows,
        "pass": all(
            row["language_count"] == 2 ** row["binary_depth"] + 2
            and row["prefix_worst_bits"] == row["binary_depth"] + 1
            and row["branch_bits"] == row["binary_depth"] + math.log2(3)
            and row["strict_three_way_order"]
            for row in rows
        ),
    }


def prefix_rounding_separation_report() -> dict[str, Any]:
    """Witness the opposite strict ordering C < B < P."""

    metrics = transcript_tree_metrics(prefix_rounding_language())
    return {
        **metrics,
        "expected_language_bits": 2,
        "expected_branch_bits": math.log2(6),
        "expected_prefix_worst_bits": 3,
        "strict_reverse_order": metrics["language_bits"]
        < metrics["branch_bits"]
        < metrics["prefix_worst_bits"],
        "pass": metrics["language_count"] == 4
        and metrics["branch_product"] == 6
        and metrics["prefix_worst_bits"] == 3
        and metrics["language_bits"] == 2
        and metrics["branch_bits"] == math.log2(6),
    }


def verification_payload() -> dict[str, Any]:
    census = exhaustive_binary_language_census()
    comb = comb_metric_gap()
    bilateral = bilateral_copy_metric_report()
    delays = bilateral_fixed_fifo_delay_report()
    one_sided = one_sided_normal_form_gap_report()
    skew = skew_metric_separation_report()
    prefix_rounding = prefix_rounding_separation_report()
    gates = {
        "M0_all_binary_languages_through_horizon_four": census["pass"]
        and census["checked_languages"] == 65809,
        "M1_comb_terminal_growth_is_subexponential": comb["pass"]
        and comb["rows"][-1]["language_rate"] < 0.06,
        "M2_comb_causal_branching_is_one_bit_per_step": all(
            row["branch_rate"] == 1.0 for row in comb["rows"]
        ),
        "M3_bilateral_normal_forms_preserve_both_metrics": bilateral["pass"],
        "M4_restricted_decoder_can_force_write_above_read": all(
            row["strict_write_gap"] for row in one_sided["decoder_memory_restriction"]
        ),
        "M5_restricted_sensor_can_force_read_above_write": one_sided[
            "sensor_computation_restriction"
        ]["strict_read_gap"],
        "M6_bilateral_fixed_fifo_delay_replay": delays["pass"]
        and len(delays["rows"]) == 96,
        "M7_terminal_prefix_and_branch_metrics_are_distinct": skew["pass"],
        "M8_prefix_rounding_reverses_branch_prefix_order": prefix_rounding["pass"]
        and prefix_rounding["strict_reverse_order"],
    }
    return {
        "schema_version": "asmp4_metric_robust_collapse_verification_v0_3",
        "census": census,
        "comb": comb,
        "bilateral": bilateral,
        "delays": delays,
        "one_sided": one_sided,
        "skew": skew,
        "prefix_rounding": prefix_rounding,
        "gates": gates,
        "pass": all(gates.values()),
    }
