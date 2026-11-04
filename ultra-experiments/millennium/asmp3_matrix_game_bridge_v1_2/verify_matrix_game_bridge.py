from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "matrix_game_bridge_v1_2.json"
OUTPUT_PATH = HERE / "artifacts" / "matrix_game_bridge_verification_v1_2.json"


def q(value: str | int) -> Fraction:
    return Fraction(value)


def vector(values: Sequence[str | int]) -> tuple[Fraction, ...]:
    return tuple(q(value) for value in values)


def parse_game(value: dict[str, object]) -> tuple[tuple[Fraction, ...], ...]:
    matrix = tuple(vector(row) for row in value["payoff"])
    if (
        not matrix
        or any(len(row) != len(matrix[0]) for row in matrix)
        or len(matrix) != int(value["rows"])
        or len(matrix[0]) != int(value["columns"])
    ):
        raise ValueError("invalid matrix registry")
    return matrix


def check_distribution(values: Sequence[Fraction], size: int) -> bool:
    return (
        len(values) == size
        and all(value >= 0 for value in values)
        and sum(values, Fraction(0)) == 1
    )


def check_certificate(
    matrix: tuple[tuple[Fraction, ...], ...], certificate: dict[str, object]
) -> bool:
    rows = len(matrix)
    columns = len(matrix[0])
    max_mix = vector(certificate["max_mix"])
    min_mix = vector(certificate["min_mix"])
    value = q(certificate["claimed_value"])
    if not check_distribution(max_mix, rows) or not check_distribution(min_mix, columns):
        return False
    column_values = tuple(
        sum((max_mix[row] * matrix[row][column] for row in range(rows)), Fraction(0))
        for column in range(columns)
    )
    row_values = tuple(
        sum((matrix[row][column] * min_mix[column] for column in range(columns)), Fraction(0))
        for row in range(rows)
    )
    pair_value = sum(
        (
            max_mix[row] * matrix[row][column] * min_mix[column]
            for row in range(rows)
            for column in range(columns)
        ),
        Fraction(0),
    )
    return (
        vector(certificate["column_payoffs_against_max_mix"]) == column_values
        and vector(certificate["row_payoffs_against_min_mix"]) == row_values
        and q(certificate["lower_bound"]) == min(column_values) >= value
        and q(certificate["upper_bound"]) == max(row_values) <= value
        and q(certificate["mixed_pair_payoff"]) == pair_value == value
        and certificate["lower_certificate_valid"] is True
        and certificate["upper_certificate_valid"] is True
        and certificate["exact"] is True
    )


def check_explicit_rows(rows: Sequence[dict[str, object]]) -> bool:
    expected = {
        "matching_pennies": (
            ((Fraction(1), Fraction(-1)), (Fraction(-1), Fraction(1))),
            Fraction(0),
        ),
        "rock_paper_scissors": (
            (
                (Fraction(0), Fraction(-1), Fraction(1)),
                (Fraction(1), Fraction(0), Fraction(-1)),
                (Fraction(-1), Fraction(1), Fraction(0)),
            ),
            Fraction(0),
        ),
        "biased_oversight": (
            (
                (Fraction(4, 5), Fraction(1, 5)),
                (Fraction(2, 5), Fraction(3, 5)),
            ),
            Fraction(1, 2),
        ),
    }
    if {row["case_id"] for row in rows} != set(expected):
        return False
    for row in rows:
        matrix = parse_game(row["game"])
        expected_matrix, expected_value = expected[row["case_id"]]
        if matrix != expected_matrix:
            return False
        if q(row["certificate"]["claimed_value"]) != expected_value:
            return False
        if not check_certificate(matrix, row["certificate"]) or row["certified"] is not True:
            return False
    return True


def check_identity_row(row: dict[str, object]) -> bool:
    size = int(row["size"])
    matrix = tuple(
        tuple(Fraction(1) if i == j else Fraction(0) for j in range(size))
        for i in range(size)
    )
    return (
        int(row["row_actions"]) == size
        and int(row["hidden_attack_actions"]) == size
        and int(row["matrix_entries"]) == size * size
        and q(row["pure_maximin"]) == (1 if size == 1 else 0)
        and q(row["mixed_value"]) == Fraction(1, size)
        and check_certificate(matrix, row["certificate"])
        and row["certified"] is True
    )


def check_alias_row(row: dict[str, object]) -> bool:
    copies = int(row["copy_count_per_action"])
    matrix = parse_game(row["game"])
    base = (
        (Fraction(4, 5), Fraction(1, 5)),
        (Fraction(2, 5), Fraction(3, 5)),
    )
    expected = tuple(
        tuple(base[i // copies][j // copies] for j in range(2 * copies))
        for i in range(2 * copies)
    )
    return (
        matrix == expected
        and int(row["raw_rows"]) == int(row["raw_columns"]) == 2 * copies
        and int(row["quotient_rows"]) == int(row["quotient_columns"]) == 2
        and q(row["value"]) == Fraction(1, 2)
        and check_certificate(matrix, row["certificate"])
        and row["certified"] is True
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    explicit = result.get("explicit_rows", [])
    identity = result.get("identity_rows", [])
    aliases = result.get("alias_rows", [])
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_matrix_game_bridge_v1_2"
            and result.get("status") == "exact_simultaneous_hidden_action_bridge"
            and result.get("parent_result") == "ASMP-3-TWO-ROLE-BACKWARD-BRIDGE-v1.1"
            and result.get("certified") is True
            and "perfect-recall sequence form" in result.get("claim_boundary", "")
        ),
        "V1_explicit_saddles_reconstructed": check_explicit_rows(explicit),
        "V2_identity_registry_complete": (
            [row["size"] for row in identity] == list(range(1, 13))
        ),
        "V3_identity_saddles_reconstructed": (
            len(identity) == 12 and all(check_identity_row(row) for row in identity)
        ),
        "V4_identity_values_decay_as_one_over_size": all(
            q(row["mixed_value"]) == Fraction(1, row["size"]) for row in identity
        ),
        "V5_alias_registry_complete": (
            [row["copy_count_per_action"] for row in aliases] == list(range(1, 7))
        ),
        "V6_alias_saddles_reconstructed": (
            len(aliases) == 6 and all(check_alias_row(row) for row in aliases)
        ),
        "V7_producer_gates_all_true": (
            bool(result.get("gates")) and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_matrix_game_bridge_verification_v1_2",
        "checker": "clean_room_primal_dual_matrix_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates supplied normal-form matrices and rational "
            "saddles; it does not construct a compact sequence form."
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
        raise SystemExit(f"matrix-game bridge verification failed: {failed}")
    print(
        "ASMP-3 matrix-game independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
