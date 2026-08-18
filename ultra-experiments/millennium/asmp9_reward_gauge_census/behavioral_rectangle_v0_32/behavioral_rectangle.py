from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb
from typing import Iterable, Sequence


Rational = Fraction


def _fraction(value: int | str | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


@dataclass(frozen=True)
class GambleInterval:
    lower: Fraction
    upper: Fraction
    estimate: Fraction
    query_count: int
    responses: tuple[int, ...]

    @property
    def radius(self) -> Fraction:
        return (self.upper - self.lower) / 2


@dataclass(frozen=True)
class ResidualRow:
    row: int
    column: int
    estimate: Fraction
    support: Fraction
    lower_abs: Fraction
    upper_abs: Fraction
    decision: str


@dataclass(frozen=True)
class RectangleCertificate:
    rows: int
    columns: int
    tolerance: Fraction
    decision: str
    residuals: tuple[ResidualRow, ...]


@dataclass(frozen=True)
class MixtureAudit:
    residual: Fraction
    support: Fraction
    lower_abs: Fraction
    upper_abs: Fraction
    tolerance: Fraction
    decision: str


def standard_gamble_response(
    value: int | str | Fraction,
    best_probability: int | str | Fraction,
) -> int:
    """Binary population threshold with equality assigned to the lower branch."""

    value_f = _fraction(value)
    probability_f = _fraction(best_probability)
    if not 0 <= value_f <= 1:
        raise ValueError("value must lie in [0,1]")
    if not 0 <= probability_f <= 1:
        raise ValueError("best_probability must lie in [0,1]")
    return 1 if value_f > probability_f else -1


def bisect_standard_gamble(
    value: int | str | Fraction,
    depth: int,
) -> GambleInterval:
    """Localize one normalized value using exact standard-gamble signs."""

    if depth < 0:
        raise ValueError("depth must be nonnegative")
    value_f = _fraction(value)
    if not 0 <= value_f <= 1:
        raise ValueError("value must lie in [0,1]")

    lower = Fraction(0)
    upper = Fraction(1)
    responses: list[int] = []
    for _ in range(depth):
        midpoint = (lower + upper) / 2
        response = standard_gamble_response(value_f, midpoint)
        responses.append(response)
        if response > 0:
            lower = midpoint
        elif response < 0:
            upper = midpoint
        else:  # pragma: no cover - the binary helper has only two outputs
            raise AssertionError("unreachable binary response")
    return GambleInterval(
        lower=lower,
        upper=upper,
        estimate=(lower + upper) / 2,
        query_count=len(responses),
        responses=tuple(responses),
    )


def acquire_rectangle(
    values: Sequence[Sequence[int | str | Fraction]],
    depth: int,
) -> tuple[tuple[GambleInterval, ...], ...]:
    rows = _rectangular(values)
    return tuple(
        tuple(bisect_standard_gamble(value, depth) for value in row)
        for row in rows
    )


def _rectangular(
    values: Sequence[Sequence[int | str | Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    if not values or not values[0]:
        raise ValueError("rectangle must be nonempty")
    columns = len(values[0])
    if any(len(row) != columns for row in values):
        raise ValueError("ragged rectangle")
    return tuple(tuple(_fraction(value) for value in row) for row in values)


def flatten(
    values: Sequence[Sequence[int | str | Fraction]],
) -> tuple[Fraction, ...]:
    rows = _rectangular(values)
    return tuple(value for row in rows for value in row)


def cross_difference_matrix(
    row_count: int,
    column_count: int,
) -> tuple[tuple[Fraction, ...], ...]:
    """Return the anchored rectangle interaction operator."""

    if row_count < 2 or column_count < 2:
        raise ValueError("at least two rows and columns are required")
    width = row_count * column_count
    result: list[tuple[Fraction, ...]] = []
    for row in range(1, row_count):
        for column in range(1, column_count):
            vector = [Fraction(0) for _ in range(width)]
            vector[row * column_count + column] = 1
            vector[row * column_count] = -1
            vector[column] = -1
            vector[0] = 1
            result.append(tuple(vector))
    return tuple(result)


def _matvec(
    matrix: Sequence[Sequence[Fraction]],
    vector: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    if matrix and any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix/vector shape mismatch")
    return tuple(
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    )


def rational_rank(matrix: Sequence[Sequence[int | str | Fraction]]) -> int:
    rows = [list(map(_fraction, row)) for row in matrix]
    if not rows:
        return 0
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (
                candidate
                for candidate in range(pivot_row, len(rows))
                if rows[candidate][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for candidate in range(len(rows)):
            if candidate == pivot_row:
                continue
            factor = rows[candidate][column]
            if factor:
                rows[candidate] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(
                        rows[candidate], rows[pivot_row]
                    )
                ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def interaction_residuals(
    values: Sequence[Sequence[int | str | Fraction]],
) -> tuple[Fraction, ...]:
    rows = _rectangular(values)
    matrix = cross_difference_matrix(len(rows), len(rows[0]))
    return _matvec(matrix, flatten(rows))


def additive_decomposition(
    values: Sequence[Sequence[int | str | Fraction]],
) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...], Fraction] | None:
    """Return row effects, column effects, constant iff the table is additive."""

    rows = _rectangular(values)
    if len(rows) < 2 or len(rows[0]) < 2:
        raise ValueError("at least two rows and columns are required")
    if any(residual != 0 for residual in interaction_residuals(rows)):
        return None
    constant = rows[0][0]
    row_effects = tuple(row[0] - constant for row in rows)
    column_effects = tuple(value - constant for value in rows[0])
    return row_effects, column_effects, constant


def box_support(
    linear_map: Sequence[Sequence[Fraction]],
    widths: Sequence[int | str | Fraction],
    direction: Sequence[int | str | Fraction],
) -> Fraction:
    """Exact support of linear_map Box(widths) in one output direction."""

    if len(linear_map) != len(direction):
        raise ValueError("direction dimension mismatch")
    widths_f = tuple(_fraction(value) for value in widths)
    if any(value < 0 for value in widths_f):
        raise ValueError("widths must be nonnegative")
    if linear_map and any(len(row) != len(widths_f) for row in linear_map):
        raise ValueError("linear-map width mismatch")
    direction_f = tuple(_fraction(value) for value in direction)
    pulled_back = [
        sum(
            (
                direction_f[row] * linear_map[row][column]
                for row in range(len(linear_map))
            ),
            Fraction(0),
        )
        for column in range(len(widths_f))
    ]
    return sum(
        (width * abs(coefficient) for width, coefficient in zip(widths_f, pulled_back)),
        Fraction(0),
    )


def certify_rectangle(
    estimates: Sequence[Sequence[int | str | Fraction]],
    widths: Sequence[Sequence[int | str | Fraction]],
    tolerance: int | str | Fraction,
) -> RectangleCertificate:
    estimates_f = _rectangular(estimates)
    widths_f = _rectangular(widths)
    if (len(estimates_f), len(estimates_f[0])) != (
        len(widths_f),
        len(widths_f[0]),
    ):
        raise ValueError("estimate/width shape mismatch")
    if any(value < 0 for row in widths_f for value in row):
        raise ValueError("widths must be nonnegative")
    tolerance_f = _fraction(tolerance)
    if tolerance_f < 0:
        raise ValueError("tolerance must be nonnegative")

    row_count = len(estimates_f)
    column_count = len(estimates_f[0])
    matrix = cross_difference_matrix(row_count, column_count)
    residual_estimates = _matvec(matrix, flatten(estimates_f))
    flat_widths = flatten(widths_f)

    rows: list[ResidualRow] = []
    decisions: list[str] = []
    index = 0
    for row in range(1, row_count):
        for column in range(1, column_count):
            direction = [
                Fraction(1 if candidate == index else 0)
                for candidate in range(len(matrix))
            ]
            support = box_support(matrix, flat_widths, direction)
            estimate = residual_estimates[index]
            lower_abs = max(Fraction(0), abs(estimate) - support)
            upper_abs = abs(estimate) + support
            if upper_abs <= tolerance_f:
                decision = "approximately_additive_certified"
            elif lower_abs > tolerance_f:
                decision = "interaction_certified"
            else:
                decision = "inconclusive"
            rows.append(
                ResidualRow(
                    row=row,
                    column=column,
                    estimate=estimate,
                    support=support,
                    lower_abs=lower_abs,
                    upper_abs=upper_abs,
                    decision=decision,
                )
            )
            decisions.append(decision)
            index += 1

    if "interaction_certified" in decisions:
        overall = "interaction_certified"
    elif all(item == "approximately_additive_certified" for item in decisions):
        overall = "approximately_additive_certified"
    else:
        overall = "inconclusive"
    return RectangleCertificate(
        rows=row_count,
        columns=column_count,
        tolerance=tolerance_f,
        decision=overall,
        residuals=tuple(rows),
    )


def audit_mixture_affinity(
    first_estimate: int | str | Fraction,
    second_estimate: int | str | Fraction,
    mixture_estimate: int | str | Fraction,
    first_weight: int | str | Fraction,
    first_width: int | str | Fraction,
    second_width: int | str | Fraction,
    mixture_width: int | str | Fraction,
    tolerance: int | str | Fraction,
) -> MixtureAudit:
    """Audit one registered compound lottery against affine mixture utility."""

    weight = _fraction(first_weight)
    if not 0 <= weight <= 1:
        raise ValueError("first_weight must lie in [0,1]")
    widths = tuple(
        _fraction(value)
        for value in (first_width, second_width, mixture_width)
    )
    if any(value < 0 for value in widths):
        raise ValueError("widths must be nonnegative")
    tolerance_f = _fraction(tolerance)
    if tolerance_f < 0:
        raise ValueError("tolerance must be nonnegative")
    residual = (
        _fraction(mixture_estimate)
        - weight * _fraction(first_estimate)
        - (1 - weight) * _fraction(second_estimate)
    )
    support = widths[2] + weight * widths[0] + (1 - weight) * widths[1]
    lower_abs = max(Fraction(0), abs(residual) - support)
    upper_abs = abs(residual) + support
    if upper_abs <= tolerance_f:
        decision = "mixture_affinity_certified"
    elif lower_abs > tolerance_f:
        decision = "mixture_affinity_rejected"
    else:
        decision = "inconclusive"
    return MixtureAudit(
        residual=residual,
        support=support,
        lower_abs=lower_abs,
        upper_abs=upper_abs,
        tolerance=tolerance_f,
        decision=decision,
    )


def row_local_coordinates(
    values: Sequence[Sequence[int | str | Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    """Normalize each row by its own endpoints."""

    rows = _rectangular(values)
    normalized: list[tuple[Fraction, ...]] = []
    for row in rows:
        low = row[0]
        high = row[-1]
        if high == low:
            raise ValueError("row endpoints must be distinct")
        normalized.append(tuple((value - low) / (high - low) for value in row))
    return tuple(normalized)


def omission_witness(
    row_count: int,
    column_count: int,
    omitted_index: int,
    amplitude: int | str | Fraction = 1,
) -> tuple[tuple[Fraction, ...], ...]:
    """Perturb one omitted cell of an otherwise additive zero table."""

    size = row_count * column_count
    if row_count < 2 or column_count < 2:
        raise ValueError("at least two rows and columns are required")
    if not 0 <= omitted_index < size:
        raise IndexError(omitted_index)
    values = [Fraction(0) for _ in range(size)]
    values[omitted_index] = _fraction(amplitude)
    return tuple(
        tuple(values[row * column_count : (row + 1) * column_count])
        for row in range(row_count)
    )


def majority_error_probability(
    repeats: int,
    correct_probability: int | str | Fraction,
) -> Fraction:
    """Exact majority-vote error for an odd number of Bernoulli trials."""

    probability = _fraction(correct_probability)
    if repeats <= 0 or repeats % 2 == 0:
        raise ValueError("repeats must be positive and odd")
    if not Fraction(1, 2) < probability <= 1:
        raise ValueError("correct_probability must lie in (1/2,1]")
    failures = Fraction(0)
    for correct in range((repeats - 1) // 2 + 1):
        failures += (
            comb(repeats, correct)
            * probability**correct
            * (1 - probability) ** (repeats - correct)
        )
    return failures


def minimum_odd_repeats(
    query_count: int,
    correct_probability: int | str | Fraction,
    family_error: int | str | Fraction,
    maximum: int = 100_001,
) -> int:
    """Smallest odd repeat count passing an exact union-bound gate."""

    if query_count <= 0:
        raise ValueError("query_count must be positive")
    family_error_f = _fraction(family_error)
    if not 0 < family_error_f < 1:
        raise ValueError("family_error must lie in (0,1)")
    probability = _fraction(correct_probability)
    if not Fraction(1, 2) < probability <= 1:
        raise ValueError("no finite guarantee at or below chance")
    for repeats in range(1, maximum + 1, 2):
        if (
            query_count
            * majority_error_probability(repeats, probability)
            <= family_error_f
        ):
            return repeats
    raise RuntimeError("repeat bound not found within maximum")


def centered_dyadic_grid(depth: int) -> tuple[Fraction, ...]:
    if depth <= 0:
        raise ValueError("depth must be positive")
    denominator = 2 ** (depth + 1)
    return tuple(Fraction(2 * index + 1, denominator) for index in range(2**depth))


def all_strictly_increasing(values: Iterable[Fraction]) -> bool:
    sequence = tuple(values)
    return all(left < right for left, right in zip(sequence, sequence[1:]))
