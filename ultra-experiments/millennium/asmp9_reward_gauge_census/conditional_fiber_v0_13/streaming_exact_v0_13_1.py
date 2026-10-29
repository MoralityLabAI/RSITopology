from __future__ import annotations

import hashlib
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction


def _integer_bytes(value: int) -> bytes:
    magnitude = abs(value)
    payload = magnitude.to_bytes(
        max(1, (magnitude.bit_length() + 7) // 8), "big"
    )
    return (b"-" if value < 0 else b"+") + payload


def ratio_certificate(numerator: int, denominator: int) -> dict[str, object]:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    with localcontext() as context:
        context.prec = 30
        decimal = Decimal(numerator) / Decimal(denominator)
    result: dict[str, object] = {
        "decimal": float(decimal),
        "decimal_30": format(decimal, "f"),
        "numerator_bit_length": abs(numerator).bit_length(),
        "denominator_bit_length": denominator.bit_length(),
        "numerator_sha256": hashlib.sha256(
            _integer_bytes(numerator)
        ).hexdigest(),
        "denominator_sha256": hashlib.sha256(
            _integer_bytes(denominator)
        ).hexdigest(),
        "representation": "unreduced_exact_integer_ratio",
    }
    if max(abs(numerator).bit_length(), denominator.bit_length()) <= 512:
        reduced = Fraction(numerator, denominator)
        result["fraction"] = (
            f"{reduced.numerator}/{reduced.denominator}"
        )
    return result


@dataclass(frozen=True)
class StreamingExactTest:
    boundary: int
    randomization_numerator: int
    randomization_denominator: int
    power_numerator: int
    power_denominator: int
    null_total: int
    alternative_total: int

    def randomization_fraction(self) -> Fraction:
        return Fraction(
            self.randomization_numerator,
            self.randomization_denominator,
        )

    def power_fraction(self) -> Fraction:
        return Fraction(self.power_numerator, self.power_denominator)

    def certificate(
        self,
        *,
        alpha: Fraction,
        lower_power: Fraction,
        upper_power: Fraction,
    ) -> dict[str, object]:
        power_above_size = (
            self.power_numerator * alpha.denominator
            > self.power_denominator * alpha.numerator
        )
        in_band = (
            self.power_numerator * lower_power.denominator
            >= self.power_denominator * lower_power.numerator
            and self.power_numerator * upper_power.denominator
            <= self.power_denominator * upper_power.numerator
        )
        return {
            "boundary": self.boundary,
            "randomization": ratio_certificate(
                self.randomization_numerator,
                self.randomization_denominator,
            ),
            "exact_size": {
                "fraction": f"{alpha.numerator}/{alpha.denominator}",
                "construction_verified": True,
            },
            "exact_power": ratio_certificate(
                self.power_numerator, self.power_denominator
            ),
            "power_above_size": power_above_size,
            "power_in_registered_band": in_band,
            "null_total_bit_length": self.null_total.bit_length(),
            "alternative_total_bit_length": (
                self.alternative_total.bit_length()
            ),
        }


def exact_randomized_upper_test_streaming(
    cycle_length: int,
    trials_per_edge: int,
    odds_ratio: Fraction,
    alpha: Fraction,
) -> StreamingExactTest:
    if cycle_length < 2 or trials_per_edge < 1:
        raise ValueError("cycle length and trials must be positive")
    if odds_ratio <= 1:
        raise ValueError("odds ratio must exceed one")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")

    k = cycle_length
    n = trials_per_edge
    odds_num = odds_ratio.numerator
    odds_den = odds_ratio.denominator

    null_total = 0
    alternative_total = 0
    binomial = 1
    odds_factor = odds_den**n
    for z in range(n + 1):
        null_weight = binomial**k
        null_total += null_weight
        alternative_total += null_weight * odds_factor
        if z < n:
            binomial = binomial * (n - z) // (z + 1)
            odds_factor = odds_factor * odds_num // odds_den

    target_numerator = alpha.numerator * null_total
    alpha_denominator = alpha.denominator
    null_tail_above = 0
    alternative_tail_above = 0
    binomial = 1
    odds_factor = odds_num**n
    boundary = -1
    boundary_null_weight = 0
    boundary_alternative_weight = 0

    for z in range(n, -1, -1):
        null_weight = binomial**k
        alternative_weight = null_weight * odds_factor
        if (
            null_tail_above * alpha_denominator
            <= target_numerator
            <= (null_tail_above + null_weight) * alpha_denominator
        ):
            boundary = z
            boundary_null_weight = null_weight
            boundary_alternative_weight = alternative_weight
            break
        null_tail_above += null_weight
        alternative_tail_above += alternative_weight
        if z > 0:
            binomial = binomial * z // (n - z + 1)
            odds_factor = odds_factor * odds_den // odds_num

    if boundary < 0:
        raise AssertionError("failed to locate exact randomized boundary")

    randomization_numerator = (
        target_numerator - alpha_denominator * null_tail_above
    )
    randomization_denominator = (
        alpha_denominator * boundary_null_weight
    )
    power_numerator = (
        alternative_tail_above * randomization_denominator
        + randomization_numerator * boundary_alternative_weight
    )
    power_denominator = (
        alternative_total * randomization_denominator
    )
    return StreamingExactTest(
        boundary=boundary,
        randomization_numerator=randomization_numerator,
        randomization_denominator=randomization_denominator,
        power_numerator=power_numerator,
        power_denominator=power_denominator,
        null_total=null_total,
        alternative_total=alternative_total,
    )
