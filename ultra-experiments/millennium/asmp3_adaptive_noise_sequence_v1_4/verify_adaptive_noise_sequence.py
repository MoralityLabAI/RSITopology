from __future__ import annotations

import json
from fractions import Fraction
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "adaptive_noise_sequence_v1_4.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "adaptive_noise_sequence_verification_v1_4.json"
)


def q(value: str | int) -> Fraction:
    return Fraction(value)


def languages(depth: int, budget: int) -> tuple[set[str], set[str]]:
    words = {format(value, f"0{depth}b") for value in range(1 << depth)}
    return (
        {word for word in words if word.count("1") <= budget},
        {word for word in words if word.count("0") <= budget},
    )


def prefix_count(depth: int, budget: int) -> int:
    return sum(
        sum(comb(length, flips) for flips in range(min(budget, length) + 1))
        for length in range(depth)
    )


def edge_count(depth: int, budget: int) -> int:
    return sum(
        sum(comb(length, flips) for flips in range(min(budget, length) + 1))
        for length in range(1, depth + 1)
    )


def check_row(row: dict[str, object]) -> bool:
    depth = int(row["depth"])
    budget = int(row["flip_budget"])
    zero, one = languages(depth, budget)
    overlap = zero & one
    union = zero | one
    separable = 2 * budget < depth
    language_formula = sum(comb(depth, index) for index in range(budget + 1))
    overlap_formula = sum(
        comb(depth, weight)
        for weight in range(max(0, depth - budget), min(depth, budget) + 1)
    )
    min_infos = 2 * prefix_count(depth, budget)
    min_sequences = 1 + 2 * edge_count(depth, budget)
    max_infos = len(union)
    max_sequences = 1 + 2 * max_infos
    terminals = 4 * language_formula
    nodes = 1 + min_infos + 2 * language_formula + terminals
    majority_correct = all(2 * word.count("1") < depth for word in zero) and all(
        2 * word.count("1") > depth for word in one
    )
    target = row["common_transcript"]
    target_valid = target is None or target in overlap
    audit = row["audit"]
    expected_value = Fraction(1) if separable else Fraction(0)
    return (
        row["phase"] == ("separable" if separable else "overlap")
        and row["criterion"] == ("2b<d" if separable else "2b>=d")
        and int(row["truth_zero_language_size"]) == len(zero) == language_formula
        and int(row["truth_one_language_size"]) == len(one) == language_formula
        and int(row["language_size_formula"]) == language_formula
        and int(row["overlap_size"]) == len(overlap) == overlap_formula
        and int(row["overlap_weight_formula"]) == overlap_formula
        and row["majority_correct_on_both_languages"] is majority_correct
        and row["common_transcript_valid"] is target_valid
        and (separable and target is None and not overlap or not separable and target_valid and bool(overlap))
        and int(row["min_information_sets"]) == min_infos
        and int(row["min_sequences"]) == min_sequences
        and int(row["max_information_sets"]) == max_infos
        and int(row["max_sequences"]) == max_sequences
        and int(row["terminal_histories"]) == terminals
        and int(row["game_node_count"]) == nodes
        and q(row["value"]) == expected_value
        and q(audit["claimed_value"]) == expected_value
        and q(audit["lower_value"]) == expected_value
        and q(audit["upper_value"]) == expected_value
        and q(audit["mixed_pair_value"]) == expected_value
        and audit["max_realization_feasible"] is True
        and audit["min_realization_feasible"] is True
        and audit["lower_constraint_valid"] is True
        and audit["upper_constraint_valid"] is True
        and audit["behavior_round_trip_exact"] is True
        and audit["exact"] is True
        and row["certified"] is True
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    rows = result.get("case_rows", [])
    expected_registry = [
        (depth, budget)
        for depth in range(1, 7)
        for budget in range(depth + 1)
    ]
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_adaptive_noise_sequence_v1_4"
            and result.get("status") == "exact_joint_noise_budget_phase"
            and result.get("parent_result") == "ASMP-3-SEQUENCE-FORM-BRIDGE-v1.3"
            and result.get("certified") is True
            and "global flip budget" in result.get("claim_boundary", "")
        ),
        "V1_case_registry_complete": (
            [(row["depth"], row["flip_budget"]) for row in rows]
            == expected_registry
        ),
        "V2_all_language_and_sequence_certificates_reconstructed": (
            len(rows) == len(expected_registry) and all(check_row(row) for row in rows)
        ),
        "V3_phase_boundary_exact": all(
            (row["phase"] == "separable") == (2 * row["flip_budget"] < row["depth"])
            for row in rows
        ),
        "V4_separable_values_one": all(
            row["phase"] != "separable" or row["value"] == "1" for row in rows
        ),
        "V5_overlap_values_zero": all(
            row["phase"] != "overlap" or row["value"] == "0" for row in rows
        ),
        "V6_producer_gates_all_true": (
            bool(result.get("gates")) and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_adaptive_noise_sequence_verification_v1_4",
        "checker": "clean_room_response_language_and_phase_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates the registered adversarial flip-budget "
            "controller; it does not generalize the phase boundary to other "
            "noise information or independence classes."
        ),
    }


def main() -> None:
    result = verify()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["passed"]:
        failed = [name for name, passed in result["checks"].items() if not passed]
        raise SystemExit(f"adaptive-noise verification failed: {failed}")
    print(
        "ASMP-3 adaptive-noise independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
