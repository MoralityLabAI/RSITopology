from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence


Q = Fraction
Vector = tuple[Q, ...]
Matrix = tuple[Vector, ...]


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def qvector(values: Iterable[Q]) -> list[str]:
    return [qstr(value) for value in values]


@dataclass(frozen=True)
class MatrixGame:
    payoff: Matrix

    @property
    def row_count(self) -> int:
        return len(self.payoff)

    @property
    def column_count(self) -> int:
        return len(self.payoff[0])

    def validate(self) -> None:
        if not self.payoff or not self.payoff[0]:
            raise ValueError("payoff matrix must be nonempty")
        width = len(self.payoff[0])
        if any(len(row) != width for row in self.payoff):
            raise ValueError("payoff matrix is ragged")


def validate_distribution(values: Sequence[Q], size: int, name: str) -> None:
    if len(values) != size:
        raise ValueError(f"{name} distribution has the wrong size")
    if any(value < 0 for value in values):
        raise ValueError(f"{name} distribution is negative")
    if sum(values, Q(0)) != 1:
        raise ValueError(f"{name} distribution does not sum to one")


def column_payoffs(game: MatrixGame, max_mix: Sequence[Q]) -> Vector:
    game.validate()
    validate_distribution(max_mix, game.row_count, "max")
    return tuple(
        sum(
            (max_mix[row] * game.payoff[row][column] for row in range(game.row_count)),
            Q(0),
        )
        for column in range(game.column_count)
    )


def row_payoffs(game: MatrixGame, min_mix: Sequence[Q]) -> Vector:
    game.validate()
    validate_distribution(min_mix, game.column_count, "min")
    return tuple(
        sum(
            (game.payoff[row][column] * min_mix[column] for column in range(game.column_count)),
            Q(0),
        )
        for row in range(game.row_count)
    )


def audit_saddle_certificate(
    game: MatrixGame,
    max_mix: Sequence[Q],
    min_mix: Sequence[Q],
    claimed_value: Q,
) -> dict[str, object]:
    columns = column_payoffs(game, max_mix)
    rows = row_payoffs(game, min_mix)
    lower_bound = min(columns)
    upper_bound = max(rows)
    expected = sum(
        (
            max_mix[row] * game.payoff[row][column] * min_mix[column]
            for row in range(game.row_count)
            for column in range(game.column_count)
        ),
        Q(0),
    )
    lower_valid = lower_bound >= claimed_value
    upper_valid = upper_bound <= claimed_value
    exact = lower_valid and upper_valid and expected == claimed_value
    return {
        "max_mix": qvector(max_mix),
        "min_mix": qvector(min_mix),
        "column_payoffs_against_max_mix": qvector(columns),
        "row_payoffs_against_min_mix": qvector(rows),
        "lower_bound": qstr(lower_bound),
        "upper_bound": qstr(upper_bound),
        "mixed_pair_payoff": qstr(expected),
        "claimed_value": qstr(claimed_value),
        "lower_certificate_valid": lower_valid,
        "upper_certificate_valid": upper_valid,
        "exact": exact,
    }


def serialize_game(game: MatrixGame) -> dict[str, object]:
    return {
        "rows": game.row_count,
        "columns": game.column_count,
        "payoff": [qvector(row) for row in game.payoff],
    }


def explicit_rows() -> list[dict[str, object]]:
    fixtures = (
        (
            "matching_pennies",
            MatrixGame(((Q(1), Q(-1)), (Q(-1), Q(1)))),
            (Q(1, 2), Q(1, 2)),
            (Q(1, 2), Q(1, 2)),
            Q(0),
            "hidden simultaneous mixing raises the pure maximin from -1 to 0",
        ),
        (
            "rock_paper_scissors",
            MatrixGame(
                (
                    (Q(0), Q(-1), Q(1)),
                    (Q(1), Q(0), Q(-1)),
                    (Q(-1), Q(1), Q(0)),
                )
            ),
            (Q(1, 3),) * 3,
            (Q(1, 3),) * 3,
            Q(0),
            "three-action cyclic hidden strategies require full mixing",
        ),
        (
            "biased_oversight",
            MatrixGame(
                (
                    (Q(4, 5), Q(1, 5)),
                    (Q(2, 5), Q(3, 5)),
                )
            ),
            (Q(1, 4), Q(3, 4)),
            (Q(1, 2), Q(1, 2)),
            Q(1, 2),
            "nonuniform verifier mixing equalizes two hidden attacks",
        ),
    )
    rows = []
    for case_id, game, max_mix, min_mix, value, interpretation in fixtures:
        audit = audit_saddle_certificate(game, max_mix, min_mix, value)
        pure_maximin = max(min(row) for row in game.payoff)
        pure_minimax = min(
            max(game.payoff[row][column] for row in range(game.row_count))
            for column in range(game.column_count)
        )
        rows.append(
            {
                "case_id": case_id,
                "game": serialize_game(game),
                "certificate": audit,
                "pure_maximin": qstr(pure_maximin),
                "pure_minimax": qstr(pure_minimax),
                "interpretation": interpretation,
                "certified": audit["exact"],
            }
        )
    return rows


def identity_game(size: int) -> MatrixGame:
    if size < 1:
        raise ValueError("identity game size must be positive")
    return MatrixGame(
        tuple(
            tuple(Q(1) if row == column else Q(0) for column in range(size))
            for row in range(size)
        )
    )


def identity_row(size: int) -> dict[str, object]:
    game = identity_game(size)
    uniform = (Q(1, size),) * size
    value = Q(1, size)
    audit = audit_saddle_certificate(game, uniform, uniform, value)
    return {
        "size": size,
        "row_actions": size,
        "hidden_attack_actions": size,
        "matrix_entries": size * size,
        "pure_maximin": "1" if size == 1 else "0",
        "mixed_value": qstr(value),
        "certificate": audit,
        "certified": audit["exact"],
    }


def duplicate_actions(
    game: MatrixGame, row_copies: int, column_copies: int
) -> MatrixGame:
    if row_copies < 1 or column_copies < 1:
        raise ValueError("copy counts must be positive")
    return MatrixGame(
        tuple(
            tuple(
                game.payoff[row][column]
                for column in range(game.column_count)
                for _ in range(column_copies)
            )
            for row in range(game.row_count)
            for _ in range(row_copies)
        )
    )


def alias_row(copy_count: int) -> dict[str, object]:
    base = MatrixGame(
        (
            (Q(4, 5), Q(1, 5)),
            (Q(2, 5), Q(3, 5)),
        )
    )
    expanded = duplicate_actions(base, copy_count, copy_count)
    base_max = (Q(1, 4), Q(3, 4))
    base_min = (Q(1, 2), Q(1, 2))
    max_mix = tuple(
        probability / copy_count
        for probability in base_max
        for _ in range(copy_count)
    )
    min_mix = tuple(
        probability / copy_count
        for probability in base_min
        for _ in range(copy_count)
    )
    audit = audit_saddle_certificate(expanded, max_mix, min_mix, Q(1, 2))
    return {
        "copy_count_per_action": copy_count,
        "raw_rows": expanded.row_count,
        "raw_columns": expanded.column_count,
        "quotient_rows": 2,
        "quotient_columns": 2,
        "value": "1/2",
        "game": serialize_game(expanded),
        "certificate": audit,
        "certified": audit["exact"],
    }


def build_result() -> dict[str, object]:
    explicit = explicit_rows()
    identity = [identity_row(size) for size in range(1, 13)]
    aliases = [alias_row(copies) for copies in range(1, 7)]
    by_id = {row["case_id"]: row for row in explicit}
    gates = {
        "M0_all_explicit_saddles_exact": all(row["certified"] for row in explicit),
        "M1_matching_mixed_value_zero": (
            by_id["matching_pennies"]["certificate"]["claimed_value"] == "0"
            and by_id["matching_pennies"]["pure_maximin"] == "-1"
        ),
        "M2_biased_nonuniform_saddle_exact": (
            by_id["biased_oversight"]["certificate"]["max_mix"]
            == ["1/4", "3/4"]
            and by_id["biased_oversight"]["certificate"]["claimed_value"] == "1/2"
        ),
        "I0_identity_values_are_one_over_size": all(
            row["mixed_value"] == qstr(Q(1, row["size"])) for row in identity
        ),
        "I1_all_identity_saddles_exact": all(row["certified"] for row in identity),
        "A0_action_aliases_preserve_value": all(
            row["certified"] and row["value"] == "1/2" for row in aliases
        ),
    }
    return {
        "schema_version": "asmp3_matrix_game_bridge_v1_2",
        "experiment_id": "ASMP-3-MATRIX-GAME-BRIDGE-v1.2",
        "status": "exact_simultaneous_hidden_action_bridge",
        "parent_result": "ASMP-3-TWO-ROLE-BACKWARD-BRIDGE-v1.1",
        "theorem": {
            "input": "finite rational zero-sum simultaneous-action payoff matrix",
            "max_lp": "maximize v with x in simplex and A^T x >= v 1",
            "min_lp": "minimize w with y in simplex and A y <= w 1",
            "certificate": "matching rational max lower and min upper strategies",
            "consequence": (
                "hidden mixed strategies are handled exactly without revealing "
                "their actions or imposing a sequential order"
            ),
        },
        "explicit_rows": explicit,
        "identity_rows": identity,
        "alias_rows": aliases,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The normal-form matrix must be explicitly supplied. A compact "
            "extensive-form game can have exponentially many pure strategies; "
            "perfect-recall sequence form is still required to avoid that expansion."
        ),
    }
