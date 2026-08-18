"""Exact unknown-link constructions for the ASMP-9 v0.8 development seed."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Sequence


ProbabilityLink = Callable[[Fraction], Fraction]


def rational_symmetric_link(value: Fraction) -> Fraction:
    """Strictly increasing symmetric link with rational values on Q."""
    value = Fraction(value)
    if value < 0:
        return 1 - rational_symmetric_link(-value)
    return Fraction(1, 2) + value / (2 * (1 + value))


def inverse_rational_symmetric_link(probability: Fraction) -> Fraction:
    probability = Fraction(probability)
    if not Fraction(0) < probability < Fraction(1):
        raise ValueError("probability must lie strictly between zero and one")
    if probability < Fraction(1, 2):
        return -inverse_rational_symmetric_link(1 - probability)
    contrast = 2 * probability - 1
    if contrast == 1:
        raise ValueError("probability one has no finite inverse")
    return contrast / (1 - contrast)


@dataclass(frozen=True)
class PiecewiseSymmetricLink:
    """Exact piecewise-linear positive branch with a rational monotone tail."""

    knots: tuple[tuple[Fraction, Fraction], ...]

    def __post_init__(self) -> None:
        if not self.knots or self.knots[0] != (Fraction(0), Fraction(1, 2)):
            raise ValueError("knots must begin at (0,1/2)")
        for (left_x, left_y), (right_x, right_y) in zip(
            self.knots, self.knots[1:]
        ):
            if not left_x < right_x or not left_y < right_y:
                raise ValueError("knots must be strictly increasing")
        if not self.knots[-1][1] < 1:
            raise ValueError("final probability must be below one")

    def __call__(self, value: Fraction) -> Fraction:
        value = Fraction(value)
        if value < 0:
            return 1 - self(-value)
        for (left_x, left_y), (right_x, right_y) in zip(
            self.knots, self.knots[1:]
        ):
            if value <= right_x:
                fraction = (value - left_x) / (right_x - left_x)
                return left_y + fraction * (right_y - left_y)
        last_x, last_y = self.knots[-1]
        offset = value - last_x
        return last_y + (1 - last_y) * offset / (1 + offset)


def complete_pairwise_law(
    utility: Sequence[Fraction], link: ProbabilityLink
) -> dict[tuple[int, int], Fraction]:
    values = tuple(map(Fraction, utility))
    return {
        (left, right): link(values[right] - values[left])
        for left in range(len(values))
        for right in range(left + 1, len(values))
    }


def temperature_law(
    utility: Sequence[Fraction],
    beta: Fraction,
    link: ProbabilityLink = rational_symmetric_link,
) -> dict[tuple[int, int], Fraction]:
    beta = Fraction(beta)
    if beta <= 0:
        raise ValueError("beta must be positive")
    values = tuple(map(Fraction, utility))
    return {
        (left, right): link(beta * (values[right] - values[left]))
        for left in range(len(values))
        for right in range(left + 1, len(values))
    }


def recover_scaled_utility(
    item_count: int,
    law: dict[tuple[int, int], Fraction],
    inverse_link: Callable[[Fraction], Fraction] = inverse_rational_symmetric_link,
) -> tuple[Fraction, ...]:
    """Recover beta*(u-u_0) from a complete known-link law."""
    recovered = [Fraction(0)]
    for item in range(1, item_count):
        recovered.append(inverse_link(law[(0, item)]))
    for (left, right), probability in law.items():
        expected = recovered[right] - recovered[left]
        if inverse_link(probability) != expected:
            raise ValueError("response law is not scalar coherent")
    return tuple(recovered)


def positive_affine_equivalent(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> bool:
    left = tuple(map(Fraction, left))
    right = tuple(map(Fraction, right))
    if len(left) != len(right):
        return False
    anchor = next(
        (
            (i, j)
            for i in range(len(left))
            for j in range(i + 1, len(left))
            if left[i] != left[j]
        ),
        None,
    )
    if anchor is None:
        return len(set(right)) == 1
    i, j = anchor
    scale = (right[j] - right[i]) / (left[j] - left[i])
    if scale <= 0:
        return False
    shift = right[i] - scale * left[i]
    return all(r == scale * l + shift for l, r in zip(left, right))


def _compare(left: Fraction, right: Fraction) -> int:
    return (left > right) - (left < right)


def same_labeled_difference_order(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> bool:
    return labeled_difference_order_key(left) == labeled_difference_order_key(
        right
    )


def labeled_difference_order_key(
    utility: Sequence[Fraction],
) -> tuple[int, ...]:
    """Canonical weak-order key for every labelled oriented difference."""
    values = tuple(map(Fraction, utility))
    pairs = [
        (source, target)
        for source in range(len(values))
        for target in range(len(values))
        if source != target
    ]
    differences = {
        pair: values[pair[1]] - values[pair[0]] for pair in pairs
    }
    return tuple(
        _compare(differences[a], differences[b])
        for a in pairs
        for b in pairs
    )


def _same_labeled_difference_order_direct(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> bool:
    """Reference implementation retained for exact test cross-checks."""
    left = tuple(map(Fraction, left))
    right = tuple(map(Fraction, right))
    if len(left) != len(right):
        return False
    pairs = [
        (source, target)
        for source in range(len(left))
        for target in range(len(left))
        if source != target
    ]
    left_differences = {
        pair: left[pair[1]] - left[pair[0]] for pair in pairs
    }
    right_differences = {
        pair: right[pair[1]] - right[pair[0]] for pair in pairs
    }
    return all(
        _compare(left_differences[a], left_differences[b])
        == _compare(right_differences[a], right_differences[b])
        for a in pairs
        for b in pairs
    )


def interpolated_matching_link(
    source_utility: Sequence[Fraction],
    target_utility: Sequence[Fraction],
    source_link: ProbabilityLink = rational_symmetric_link,
) -> PiecewiseSymmetricLink:
    """Build F' so (source,F) and (target,F') agree on all item pairs."""
    source = tuple(map(Fraction, source_utility))
    target = tuple(map(Fraction, target_utility))
    if not same_labeled_difference_order(source, target):
        raise ValueError("utility vectors do not share labelled difference order")
    mapping: dict[Fraction, Fraction] = {}
    for left in range(len(source)):
        for right in range(len(source)):
            target_gap = target[right] - target[left]
            source_gap = source[right] - source[left]
            if target_gap <= 0:
                continue
            probability = source_link(source_gap)
            if target_gap in mapping and mapping[target_gap] != probability:
                raise ValueError("target gap has inconsistent source images")
            mapping[target_gap] = probability
    knots = ((Fraction(0), Fraction(1, 2)),) + tuple(sorted(mapping.items()))
    return PiecewiseSymmetricLink(knots)


def explicit_counterexample() -> dict[str, object]:
    source = tuple(map(Fraction, (0, 1, 3)))
    target = tuple(map(Fraction, (0, 1, 4)))
    target_link = interpolated_matching_link(source, target)
    source_law = complete_pairwise_law(source, rational_symmetric_link)
    target_law = complete_pairwise_law(target, target_link)
    return {
        "source_utility": source,
        "target_utility": target,
        "source_law": source_law,
        "target_law": target_law,
        "same_law": source_law == target_law,
        "positive_affine_equivalent": positive_affine_equivalent(source, target),
        "same_difference_order": same_labeled_difference_order(source, target),
        "target_link": target_link,
    }
