from __future__ import annotations

import sys
from fractions import Fraction
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
V13 = HERE.parent / "asmp3_sequence_form_bridge_v1_3"
if str(V13) not in sys.path:
    sys.path.insert(0, str(V13))

from sequence_form_bridge import (  # noqa: E402
    ExtensiveGame,
    Q,
    audit_sequence_saddle,
    compile_sequence_form,
    qstr,
    realization_from_behavior,
)


def budget_noise_game(depth: int, budget: int) -> ExtensiveGame:
    if depth < 1 or budget < 0 or budget > depth:
        raise ValueError("invalid depth/budget")
    nodes: dict[str, dict[str, object]] = {
        "truth": {"kind": "chance", "transitions": {}}
    }
    nodes["truth"]["transitions"] = {
        "truth_0": (Q(1, 2), "noise_t0_hEMPTY"),
        "truth_1": (Q(1, 2), "noise_t1_hEMPTY"),
    }

    def add_noise_path(truth: int, history: str, flips: int) -> str:
        if len(history) == depth:
            guess_node = f"guess_t{truth}_h{history}"
            information_set = f"GUESS_{history}"
            actions = {}
            for guess in (0, 1):
                terminal = f"terminal_t{truth}_h{history}_g{guess}"
                actions[f"guess_{guess}"] = terminal
                nodes[terminal] = {
                    "kind": "terminal",
                    "payoff": Q(1) if guess == truth else Q(-1),
                }
            nodes[guess_node] = {
                "kind": "player",
                "player": "max",
                "information_set": information_set,
                "actions": actions,
            }
            return guess_node

        node_id = f"noise_t{truth}_h{history or 'EMPTY'}"
        actions = {}
        for response in (0, 1):
            next_flips = flips + int(response != truth)
            if next_flips <= budget:
                next_history = history + str(response)
                actions[f"emit_{response}"] = add_noise_path(
                    truth, next_history, next_flips
                )
        nodes[node_id] = {
            "kind": "player",
            "player": "min",
            "information_set": f"NOISE_T{truth}_H{history or 'EMPTY'}",
            "actions": actions,
        }
        return node_id

    add_noise_path(0, "", 0)
    add_noise_path(1, "", 0)
    return ExtensiveGame("truth", nodes)


def max_behavior(compiled, depth: int, separable: bool) -> dict[str, dict[str, Q]]:
    behavior = {}
    for information_set in compiled.max_form.information_sets:
        history = information_set.removeprefix("GUESS_")
        actions = compiled.max_form.actions[information_set]
        if not separable:
            behavior[information_set] = {action: Q(1, 2) for action in actions}
            continue
        ones = history.count("1")
        guess = 1 if 2 * ones > depth else 0
        behavior[information_set] = {
            action: Q(1) if action == f"guess_{guess}" else Q(0)
            for action in actions
        }
    return behavior


def common_transcript(depth: int, budget: int) -> str:
    if 2 * budget < depth:
        raise ValueError("response languages do not overlap")
    ones = depth - budget
    return "1" * ones + "0" * (depth - ones)


def min_behavior(
    compiled,
    depth: int,
    budget: int,
    separable: bool,
) -> tuple[dict[str, dict[str, Q]], str | None]:
    target = None if separable else common_transcript(depth, budget)
    behavior = {}
    for information_set in compiled.min_form.information_sets:
        prefix = information_set.split("_H", 1)[1]
        history = "" if prefix == "EMPTY" else prefix
        truth = int(information_set.split("_T", 1)[1][0])
        actions = compiled.min_form.actions[information_set]
        desired_response = truth if separable else int(target[len(history)])
        desired_action = f"emit_{desired_response}"
        selected = desired_action if desired_action in actions else actions[0]
        behavior[information_set] = {
            action: Q(1) if action == selected else Q(0) for action in actions
        }
    return behavior, target


def response_languages(depth: int, budget: int) -> tuple[set[str], set[str]]:
    all_words = {format(value, f"0{depth}b") for value in range(1 << depth)}
    truth_zero = {word for word in all_words if word.count("1") <= budget}
    truth_one = {word for word in all_words if word.count("0") <= budget}
    return truth_zero, truth_one


def case_row(depth: int, budget: int) -> dict[str, object]:
    game = budget_noise_game(depth, budget)
    compiled = compile_sequence_form(game)
    truth_zero, truth_one = response_languages(depth, budget)
    overlap = truth_zero & truth_one
    separable = 2 * budget < depth
    value = Q(1) if separable else Q(0)
    max_policy = max_behavior(compiled, depth, separable)
    min_policy, target = min_behavior(compiled, depth, budget, separable)
    max_realization = realization_from_behavior(compiled.max_form, max_policy)
    min_realization = realization_from_behavior(compiled.min_form, min_policy)
    audit = audit_sequence_saddle(
        compiled, max_realization, min_realization, value
    )
    majority_correct = all(
        (2 * word.count("1") > depth) is False for word in truth_zero
    ) and all((2 * word.count("1") > depth) is True for word in truth_one)
    target_valid = target is None or (
        target in truth_zero and target in truth_one
    )
    return {
        "depth": depth,
        "flip_budget": budget,
        "phase": "separable" if separable else "overlap",
        "criterion": "2b<d" if separable else "2b>=d",
        "truth_zero_language_size": len(truth_zero),
        "truth_one_language_size": len(truth_one),
        "language_size_formula": sum(comb(depth, index) for index in range(budget + 1)),
        "overlap_size": len(overlap),
        "overlap_weight_formula": sum(
            comb(depth, weight)
            for weight in range(max(0, depth - budget), min(depth, budget) + 1)
        ),
        "common_transcript": target,
        "majority_correct_on_both_languages": majority_correct,
        "common_transcript_valid": target_valid,
        "game_node_count": len(game.nodes),
        "terminal_histories": compiled.terminal_count,
        "max_information_sets": len(compiled.max_form.information_sets),
        "min_information_sets": len(compiled.min_form.information_sets),
        "max_sequences": len(compiled.max_form.sequences),
        "min_sequences": len(compiled.min_form.sequences),
        "value": qstr(value),
        "audit": audit,
        "certified": (
            audit["exact"]
            and len(truth_zero) == len(truth_one)
            == sum(comb(depth, index) for index in range(budget + 1))
            and len(overlap)
            == sum(
                comb(depth, weight)
                for weight in range(max(0, depth - budget), min(depth, budget) + 1)
            )
            and ((separable and majority_correct and not overlap) or (not separable and target_valid and bool(overlap)))
        ),
    }


def build_result() -> dict[str, object]:
    rows = [
        case_row(depth, budget)
        for depth in range(1, 7)
        for budget in range(depth + 1)
    ]
    gates = {
        "N0_registry_complete": len(rows) == sum(depth + 1 for depth in range(1, 7)),
        "N1_all_sequence_saddles_exact": all(row["audit"]["exact"] for row in rows),
        "N2_language_counts_match_binomial_formula": all(
            row["truth_zero_language_size"]
            == row["truth_one_language_size"]
            == row["language_size_formula"]
            for row in rows
        ),
        "N3_overlap_counts_match_weight_formula": all(
            row["overlap_size"] == row["overlap_weight_formula"] for row in rows
        ),
        "N4_separable_phase_has_value_one": all(
            row["phase"] != "separable"
            or (row["value"] == "1" and row["majority_correct_on_both_languages"])
            for row in rows
        ),
        "N5_overlap_phase_has_value_zero": all(
            row["phase"] != "overlap"
            or (row["value"] == "0" and row["common_transcript_valid"])
            for row in rows
        ),
        "N6_all_rows_certified": all(row["certified"] for row in rows),
    }
    return {
        "schema_version": "asmp3_adaptive_noise_sequence_v1_4",
        "experiment_id": "ASMP-3-ADAPTIVE-NOISE-SEQUENCE-v1.4",
        "status": "exact_joint_noise_budget_phase",
        "parent_result": "ASMP-3-SEQUENCE-FORM-BRIDGE-v1.3",
        "theorem": {
            "game": (
                "uniform hidden truth, d observed responses, adversarial noise "
                "with a global budget b, then a history-information-set guess"
            ),
            "separable_phase": "2b<d gives exact value 1 by majority",
            "overlap_phase": (
                "2b>=d gives exact value 0 by a common transcript and uniform guessing"
            ),
            "joint_object": (
                "intersection of complete response-history languages, not a "
                "single-response marginal accuracy"
            ),
        },
        "case_rows": rows,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "Noise is a registered zero-sum minimizing controller that knows "
            "truth and response history and is constrained by one global flip "
            "budget. Other information, stochastic, or independence restrictions "
            "define different noise classes."
        ),
    }
