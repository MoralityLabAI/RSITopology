from __future__ import annotations

import hashlib
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache


@dataclass(frozen=True)
class ChannelTest:
    alternative_probability: Fraction
    false_negative: Fraction
    false_positive: Fraction
    null_probability: Fraction
    samples: int
    threshold: int


@dataclass(frozen=True)
class RuleErrors:
    base: Fraction
    gauge_alias: Fraction
    mechanics_flip: Fraction
    mixture_invalid: Fraction
    reward_flip: Fraction

    @property
    def worst(self) -> Fraction:
        return max(
            self.base,
            self.gauge_alias,
            self.mechanics_flip,
            self.mixture_invalid,
            self.reward_flip,
        )


@dataclass(frozen=True)
class FixedDesignCertificate:
    mechanics: ChannelTest
    mixture: ChannelTest
    return_channel: ChannelTest
    errors: RuleErrors
    total_queries: int


@lru_cache(maxsize=None)
def binomial_tail(
    samples: int,
    threshold: int,
    probability: Fraction,
    upper: bool,
) -> Fraction:
    if samples < 0:
        raise ValueError("samples must be nonnegative")
    if not 0 <= threshold <= samples + 1:
        raise ValueError("threshold is out of range")
    if not 0 <= probability <= 1:
        raise ValueError("probability must lie in [0,1]")
    numerator = probability.numerator
    denominator = probability.denominator
    complement = denominator - numerator
    if samples == 0:
        event = 0 >= threshold if upper else 0 < threshold
        return Fraction(int(event))
    if numerator == 0:
        event = 0 >= threshold if upper else 0 < threshold
        return Fraction(int(event))
    if complement == 0:
        event = samples >= threshold if upper else samples < threshold
        return Fraction(int(event))

    term = complement**samples
    total = 0
    for successes in range(samples + 1):
        event = (
            successes >= threshold
            if upper
            else successes < threshold
        )
        if event:
            total += term
        if successes < samples:
            product = term * (samples - successes) * numerator
            divisor = (successes + 1) * complement
            term, remainder = divmod(product, divisor)
            if remainder:
                raise RuntimeError("binomial recurrence lost integrality")
    return Fraction(total, denominator**samples)


def midpoint_aligned_test(
    null_probability: Fraction,
    alternative_probability: Fraction,
    blocks: int,
) -> ChannelTest:
    if blocks <= 0:
        raise ValueError("blocks must be positive")
    if not 0 <= null_probability < alternative_probability <= 1:
        raise ValueError("ordered Bernoulli probabilities are required")
    midpoint = (null_probability + alternative_probability) / 2
    samples = midpoint.denominator * blocks
    threshold = midpoint.numerator * blocks
    return ChannelTest(
        alternative_probability=alternative_probability,
        false_negative=binomial_tail(
            samples,
            threshold,
            alternative_probability,
            False,
        ),
        false_positive=binomial_tail(
            samples,
            threshold,
            null_probability,
            True,
        ),
        null_probability=null_probability,
        samples=samples,
        threshold=threshold,
    )


def hierarchical_rule_errors(
    return_channel: ChannelTest,
    mechanics: ChannelTest,
    mixture: ChannelTest,
) -> RuleErrors:
    if (
        return_channel.null_probability != Fraction(1, 4)
        or return_channel.alternative_probability != Fraction(3, 4)
        or mechanics.null_probability != Fraction(1, 4)
        or mechanics.alternative_probability != Fraction(3, 4)
        or mixture.null_probability != Fraction(1, 2)
        or mixture.alternative_probability != Fraction(9, 17)
    ):
        raise ValueError("tests do not match the native v0.33 registry")

    alpha_r = return_channel.false_positive
    beta_r = return_channel.false_negative
    alpha_m = mechanics.false_positive
    beta_m = mechanics.false_negative
    alpha_a = mixture.false_positive
    beta_a = mixture.false_negative

    base = alpha_a + (1 - alpha_a) * (
        1 - (1 - alpha_r) * (1 - alpha_m)
    )
    reward_flip = alpha_a + (1 - alpha_a) * beta_r * (1 - alpha_m)
    mechanics_flip = (
        alpha_a + (1 - alpha_a) * beta_m * (1 - alpha_r)
    )
    return RuleErrors(
        base=base,
        gauge_alias=base,
        mechanics_flip=mechanics_flip,
        mixture_invalid=beta_a,
        reward_flip=reward_flip,
    )


def fixed_design(
    return_blocks: int,
    mixture_blocks: int,
) -> FixedDesignCertificate:
    return_test = midpoint_aligned_test(
        Fraction(1, 4),
        Fraction(3, 4),
        return_blocks,
    )
    mechanics_test = midpoint_aligned_test(
        Fraction(1, 4),
        Fraction(3, 4),
        return_blocks,
    )
    mixture_test = midpoint_aligned_test(
        Fraction(1, 2),
        Fraction(9, 17),
        mixture_blocks,
    )
    errors = hierarchical_rule_errors(
        return_test,
        mechanics_test,
        mixture_test,
    )
    return FixedDesignCertificate(
        mechanics=mechanics_test,
        mixture=mixture_test,
        return_channel=return_test,
        errors=errors,
        total_queries=(
            return_test.samples
            + mechanics_test.samples
            + mixture_test.samples
        ),
    )


def conservative_start(delta: Fraction) -> FixedDesignCertificate:
    channel_target = delta / 3
    return_blocks = next(
        blocks
        for blocks in range(1, 10_000)
        if max(
            midpoint_aligned_test(
                Fraction(1, 4),
                Fraction(3, 4),
                blocks,
            ).false_positive,
            midpoint_aligned_test(
                Fraction(1, 4),
                Fraction(3, 4),
                blocks,
            ).false_negative,
        )
        <= channel_target
    )
    mixture_blocks = next(
        blocks
        for blocks in range(1, 10_000)
        if max(
            midpoint_aligned_test(
                Fraction(1, 2),
                Fraction(9, 17),
                blocks,
            ).false_positive,
            midpoint_aligned_test(
                Fraction(1, 2),
                Fraction(9, 17),
                blocks,
            ).false_negative,
        )
        <= channel_target
    )
    return fixed_design(return_blocks, mixture_blocks)


def optimize_midpoint_grid(delta: Fraction) -> FixedDesignCertificate:
    if not 0 < delta < Fraction(1, 2):
        raise ValueError("delta must lie in (0,1/2)")
    initial = conservative_start(delta)
    best = initial
    maximum_total = initial.total_queries
    maximum_return_blocks = (maximum_total - 68) // 4
    maximum_mixture_blocks = (maximum_total - 4) // 68
    return_tests = {
        blocks: midpoint_aligned_test(
            Fraction(1, 4),
            Fraction(3, 4),
            blocks,
        )
        for blocks in range(1, maximum_return_blocks + 1)
    }
    mixture_tests = {
        blocks: midpoint_aligned_test(
            Fraction(1, 2),
            Fraction(9, 17),
            blocks,
        )
        for blocks in range(1, maximum_mixture_blocks + 1)
    }
    for return_blocks, return_test in return_tests.items():
        for mixture_blocks, mixture_test in mixture_tests.items():
            total = 2 * return_test.samples + mixture_test.samples
            if total >= best.total_queries:
                continue
            errors = hierarchical_rule_errors(
                return_test,
                return_test,
                mixture_test,
            )
            if errors.worst <= delta:
                best = FixedDesignCertificate(
                    mechanics=return_test,
                    mixture=mixture_test,
                    return_channel=return_test,
                    errors=errors,
                    total_queries=total,
                )
    return best


def fraction_digest(value: Fraction) -> str:
    encoded = (
        f"{value.numerator}/{value.denominator}"
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def decimal_text(value: Fraction, digits: int = 18) -> str:
    with localcontext() as context:
        context.prec = digits + 8
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
        return format(decimal, f".{digits}f")
