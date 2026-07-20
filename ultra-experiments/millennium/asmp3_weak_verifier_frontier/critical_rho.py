from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from frontier import ERROR_LIMIT, RHO_GRID, majority_error


# Coefficients in ascending order. For q=9, one family, mu=1/5:
# majority_error(rho) - 1/20 = -9*P(rho)/D(rho), where D(rho)>0 on [0,1].
THRESHOLD_POLYNOMIAL = (
    Fraction(5281),
    Fraction(40728),
    Fraction(-1046494),
    Fraction(-15144160),
    Fraction(-67432815),
    Fraction(-110905976),
    Fraction(-39111828),
    Fraction(23595264),
)

LOWER = Fraction(59108062397, 10**12)
UPPER = Fraction(59108062398, 10**12)


def trim(poly: Iterable[Fraction]) -> tuple[Fraction, ...]:
    values = list(poly)
    while values and values[-1] == 0:
        values.pop()
    return tuple(values)


def evaluate(poly: Iterable[Fraction], x: Fraction) -> Fraction:
    value = Fraction(0)
    for coefficient in reversed(tuple(poly)):
        value = value * x + coefficient
    return value


def derivative(poly: Iterable[Fraction]) -> tuple[Fraction, ...]:
    values = tuple(poly)
    return trim(Fraction(i) * values[i] for i in range(1, len(values)))


def polynomial_remainder(
    dividend: Iterable[Fraction], divisor: Iterable[Fraction]
) -> tuple[Fraction, ...]:
    left = list(trim(dividend))
    right = trim(divisor)
    if not right:
        raise ZeroDivisionError("zero polynomial")
    while len(left) >= len(right) and left:
        factor = left[-1] / right[-1]
        shift = len(left) - len(right)
        for i, coefficient in enumerate(right):
            left[i + shift] -= factor * coefficient
        left = list(trim(left))
    return tuple(left)


def sturm_sequence(poly: Iterable[Fraction]) -> tuple[tuple[Fraction, ...], ...]:
    first = trim(poly)
    second = derivative(first)
    sequence = [first, second]
    while sequence[-1]:
        remainder = polynomial_remainder(sequence[-2], sequence[-1])
        if not remainder:
            break
        sequence.append(tuple(-x for x in remainder))
    return tuple(sequence)


def sign_variations(sequence: Iterable[Iterable[Fraction]], x: Fraction) -> int:
    signs: list[int] = []
    for poly in sequence:
        value = evaluate(poly, x)
        if value:
            signs.append(1 if value > 0 else -1)
    return sum(a != b for a, b in zip(signs, signs[1:]))


def root_count(poly: Iterable[Fraction], lower: Fraction, upper: Fraction) -> int:
    sequence = sturm_sequence(poly)
    return sign_variations(sequence, lower) - sign_variations(sequence, upper)


def threshold_denominator(rho: Fraction) -> Fraction:
    value = Fraction(1562500)
    for scale in (1, 2, 3, 5, 6, 7):
        value *= scale * rho + 1
    return value


def polynomial_residual(rho: Fraction) -> Fraction:
    return -9 * evaluate(THRESHOLD_POLYNOMIAL, rho) / threshold_denominator(rho)


def verify_identity() -> bool:
    points = tuple(RHO_GRID) + (LOWER, UPPER)
    return all(
        majority_error(9, 1, rho) - ERROR_LIMIT == polynomial_residual(rho)
        for rho in points
    )


def characterization() -> dict[str, object]:
    roots_unit = root_count(THRESHOLD_POLYNOMIAL, Fraction(0), Fraction(1))
    roots_bracket = root_count(THRESHOLD_POLYNOMIAL, LOWER, UPPER)
    lower_value = evaluate(THRESHOLD_POLYNOMIAL, LOWER)
    upper_value = evaluate(THRESHOLD_POLYNOMIAL, UPPER)
    identity = verify_identity()
    certified = (
        identity
        and roots_unit == 1
        and roots_bracket == 1
        and lower_value > 0
        and upper_value < 0
    )
    return {
        "configuration": {
            "q": 9,
            "families": 1,
            "marginal_error": "1/5",
            "fp_fn_limit": "1/20",
            "model": "single-family beta-binomial exchangeable errors",
        },
        "threshold_polynomial_coefficients_ascending": [
            str(x) for x in THRESHOLD_POLYNOMIAL
        ],
        "critical_rho": {
            "definition": "unique root of the threshold polynomial in [0,1]",
            "lower": str(LOWER),
            "upper": str(UPPER),
            "lower_decimal": float(LOWER),
            "upper_decimal": float(UPPER),
            "interval_width": str(UPPER - LOWER),
            "pass_for": "rho at or below the critical value",
            "fail_for": "rho above the critical value",
        },
        "certificates": {
            "exact_residual_identity": identity,
            "roots_in_unit_interval": roots_unit,
            "roots_in_isolating_interval": roots_bracket,
            "lower_polynomial_sign": 1 if lower_value > 0 else -1,
            "upper_polynomial_sign": 1 if upper_value > 0 else -1,
        },
        "certified": certified,
        "claim_boundary": (
            "Post-result exact characterization of one frozen beta-binomial cell; "
            "not a preregistered scientific outcome or a real-verifier estimate."
        ),
    }


def main() -> None:
    output = Path(__file__).resolve().parent / "critical_rho_v0_1_1.json"
    payload = characterization()
    if not payload["certified"]:
        raise RuntimeError("critical-rho characterization failed")
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

