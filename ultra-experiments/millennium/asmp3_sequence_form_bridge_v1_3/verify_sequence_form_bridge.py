from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "sequence_form_bridge_v1_3.json"
OUTPUT_PATH = HERE / "artifacts" / "sequence_form_bridge_verification_v1_3.json"


def q(value: str | int) -> Fraction:
    return Fraction(value)


def vector(values: Sequence[str | int]) -> tuple[Fraction, ...]:
    return tuple(q(value) for value in values)


def matrix(values: Sequence[Sequence[str | int]]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(vector(row) for row in values)


def matvec(rows: Sequence[Sequence[Fraction]], values: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return tuple(
        sum((left * right for left, right in zip(row, values)), Fraction(0))
        for row in rows
    )


def transpose_vec(
    rows: Sequence[Sequence[Fraction]], values: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    return tuple(
        sum((values[row] * rows[row][column] for row in range(len(rows))), Fraction(0))
        for column in range(len(rows[0]))
    )


def parse_form(value: dict[str, object]) -> dict[str, object]:
    E = matrix(value["E"])
    e = vector(value["e"])
    names = tuple(value["sequence_names"])
    if (
        len(E) != int(value["constraint_rows"])
        or len(E) != len(e)
        or len(E) != int(value["information_set_count"]) + 1
        or any(len(row) != len(names) for row in E)
        or len(names) != int(value["sequence_count"])
        or not names
        or names[0] != "EMPTY"
    ):
        raise ValueError("invalid realization-form registry")
    return {"E": E, "e": e, "names": names}


def check_realization(form: dict[str, object], realization: Sequence[Fraction]) -> bool:
    return (
        len(realization) == len(form["names"])
        and all(value >= 0 for value in realization)
        and matvec(form["E"], realization) == form["e"]
    )


def check_full_certificate(row: dict[str, object]) -> bool:
    max_form = parse_form(row["max_form"])
    min_form = parse_form(row["min_form"])
    payoff = matrix(row["payoff"])
    audit = row["audit"]
    x = vector(audit["max_realization"])
    y = vector(audit["min_realization"])
    p = vector(audit["min_dual_potentials"])
    qpot = vector(audit["max_dual_potentials"])
    if (
        len(payoff) != len(max_form["names"])
        or any(len(payoff_row) != len(min_form["names"]) for payoff_row in payoff)
        or not check_realization(max_form, x)
        or not check_realization(min_form, y)
    ):
        return False
    min_payoffs = transpose_vec(payoff, x)
    max_payoffs = matvec(payoff, y)
    min_lhs = transpose_vec(min_form["E"], p)
    max_lhs = transpose_vec(max_form["E"], qpot)
    lower = sum((left * right for left, right in zip(min_form["e"], p)), Fraction(0))
    upper = sum((left * right for left, right in zip(max_form["e"], qpot)), Fraction(0))
    pair = sum((x[index] * max_payoffs[index] for index in range(len(x))), Fraction(0))
    value = q(row["value"])
    return (
        vector(audit["min_sequence_payoffs"]) == min_payoffs
        and vector(audit["max_sequence_payoffs"]) == max_payoffs
        and vector(audit["min_dual_lhs"]) == min_lhs
        and vector(audit["max_dual_lhs"]) == max_lhs
        and all(left <= right for left, right in zip(min_lhs, min_payoffs))
        and all(left >= right for left, right in zip(max_lhs, max_payoffs))
        and lower == upper == pair == value
        and q(audit["lower_value"]) == lower
        and q(audit["upper_value"]) == upper
        and q(audit["mixed_pair_value"]) == pair
        and audit["behavior_round_trip_exact"] is True
        and audit["exact"] is True
        and row["certified"] is True
    )


def check_one_level_uniform_form(
    form: dict[str, object], information_count: int, action_count: int
) -> bool:
    names = form["names"]
    if len(names) != 1 + information_count * action_count:
        return False
    root = form["E"][0]
    if root != (Fraction(1),) + (Fraction(0),) * (len(names) - 1):
        return False
    groups: dict[str, list[int]] = {}
    for index, name in enumerate(names[1:], start=1):
        if ">" in name or ":" not in name:
            return False
        information, _ = name.split(":", 1)
        groups.setdefault(information, []).append(index)
    if len(groups) != information_count or any(len(indices) != action_count for indices in groups.values()):
        return False
    expected_rows = {(indices[0], tuple(indices)) for indices in groups.values()}
    seen = set()
    for row in form["E"][1:]:
        if row[0] != -1:
            return False
        positive = tuple(index for index, value in enumerate(row) if value == 1)
        if len(positive) != action_count or any(
            value not in {Fraction(-1), Fraction(0), Fraction(1)} for value in row
        ):
            return False
        seen.add((positive[0], positive))
    return len(seen) == len(expected_rows) and form["e"] == (
        Fraction(1),
    ) + (Fraction(0),) * information_count


def check_concealment_row(row: dict[str, object]) -> bool:
    size = int(row["size"])
    max_form = parse_form(row["max_form"])
    min_form = parse_form(row["min_form"])
    audit = row["audit"]
    x = vector(audit["max_realization"])
    y = vector(audit["min_realization"])
    min_payoffs = vector(audit["min_sequence_payoffs"])
    max_payoffs = vector(audit["max_sequence_payoffs"])
    p = vector(audit["min_dual_potentials"])
    qpot = vector(audit["max_dual_potentials"])
    min_lhs = transpose_vec(min_form["E"], p)
    max_lhs = transpose_vec(max_form["E"], qpot)
    value = Fraction(size - 1, size)
    per_sequence = Fraction(size - 1, size * size)
    expected_realization = (Fraction(1),) + (Fraction(1, size),) * (size * size)
    expected_sequence_payoffs = (Fraction(0),) + (per_sequence,) * (size * size)
    expected_potentials = (value,) + (per_sequence,) * size
    normal = row["normal_form_audit"]
    normal_valid = normal is None or (
        int(normal["pure_strategies_per_role"]) == size**size
        and int(normal["normal_matrix_entries"]) == (size**size) ** 2
        and normal["uniform_column_values"] == [str(value)]
        and normal["uniform_row_values"] == [str(value)]
        and q(normal["value"]) == value
        and normal["exact"] is True
    )
    return (
        check_one_level_uniform_form(max_form, size, size)
        and check_one_level_uniform_form(min_form, size, size)
        and check_realization(max_form, x)
        and check_realization(min_form, y)
        and x == y == expected_realization
        and min_payoffs == max_payoffs == expected_sequence_payoffs
        and p == qpot == expected_potentials
        and vector(audit["min_dual_lhs"]) == min_lhs == expected_sequence_payoffs
        and vector(audit["max_dual_lhs"]) == max_lhs == expected_sequence_payoffs
        and q(audit["lower_value"]) == q(audit["upper_value"]) == value
        and q(audit["mixed_pair_value"]) == q(audit["claimed_value"]) == value
        and int(row["pure_strategies_per_role"]) == size**size
        and int(row["normal_matrix_entries"]) == (size**size) ** 2
        and int(row["sequences_per_role"]) == 1 + size * size
        and int(row["sequence_payoff_entries"]) == (1 + size * size) ** 2
        and int(row["terminal_histories"]) == size**3
        and int(row["compiled_terminal_count"]) == size**3
        and int(row["nonzero_terminal_contributions"]) == size * size * (size - 1)
        and int(row["compiled_nonzero_payoff_contributions"]) == size * size * (size - 1)
        and q(row["value"]) == value
        and normal_valid
        and audit["exact"] is True
        and row["certified"] is True
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    matching = result.get("matching_rows", [])
    concealment = result.get("concealment_rows", [])
    by_id = {row["case_id"]: row for row in matching}
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_sequence_form_bridge_v1_3"
            and result.get("status") == "exact_perfect_recall_sequence_form_bridge"
            and result.get("parent_result") == "ASMP-3-MATRIX-GAME-BRIDGE-v1.2"
            and result.get("certified") is True
            and "imperfect recall" in result.get("claim_boundary", "")
        ),
        "V1_matching_registry_and_values_exact": (
            set(by_id) == {"hidden_matching", "revealed_matching"}
            and q(by_id["hidden_matching"]["value"]) == 0
            and q(by_id["revealed_matching"]["value"]) == -1
        ),
        "V2_matching_sequence_certificates_reconstructed": (
            len(matching) == 2 and all(check_full_certificate(row) for row in matching)
        ),
        "V2b_nested_sequence_certificate_reconstructed": (
            result.get("nested_row", {}).get("max_sequence_depth") == 2
            and q(result["nested_row"]["value"]) == 1
            and check_full_certificate(result["nested_row"])
        ),
        "V3_concealment_registry_complete": (
            [row["size"] for row in concealment] == list(range(2, 9))
        ),
        "V4_all_concealment_certificates_reconstructed": (
            len(concealment) == 7 and all(check_concealment_row(row) for row in concealment)
        ),
        "V5_sequence_compression_counts_exact": all(
            row["pure_strategies_per_role"] == row["size"] ** row["size"]
            and row["sequences_per_role"] == 1 + row["size"] ** 2
            for row in concealment
        ),
        "V6_imperfect_recall_rejection_recorded": (
            result.get("imperfect_recall_rejected") is True
        ),
        "V7_producer_gates_all_true": (
            bool(result.get("gates")) and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_sequence_form_bridge_verification_v1_3",
        "checker": "clean_room_sequence_constraint_and_dual_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker reconstructs the registered one-level signaling "
            "families and matching games; it is not an external review of all "
            "perfect-recall extensive games."
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
        raise SystemExit(f"sequence-form verification failed: {failed}")
    print(
        "ASMP-3 sequence-form independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
