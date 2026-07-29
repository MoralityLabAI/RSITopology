"""Exact development helpers for the ASMP-9 v0.62 modulus slice."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations
from typing import Mapping, Sequence


Q = Fraction
ALTERNATIVES = ("a", "b", "c")
RANKINGS = tuple(permutations(ALTERNATIVES))
MENUS = (
    ("a", "b"),
    ("a", "c"),
    ("b", "c"),
    ("a", "b", "c"),
)
Kernel = dict[tuple[tuple[str, ...], str], Fraction]


def _validate_gamma(gamma: Fraction) -> Fraction:
    gamma = Q(gamma)
    if not 0 < gamma <= Q(1, 125):
        raise ValueError("gamma must lie in (0,1/125]")
    return gamma


def kernel_with_full(full: Sequence[Fraction]) -> Kernel:
    full = tuple(Q(value) for value in full)
    if len(full) != 3 or min(full) <= 0 or sum(full, Q(0)) != 1:
        raise ValueError("full-menu vector must be a positive distribution")
    kernel = {
        (("a", "b"), "a"): Q(2, 5),
        (("a", "b"), "b"): Q(3, 5),
        (("a", "c"), "a"): Q(3, 5),
        (("a", "c"), "c"): Q(2, 5),
        (("b", "c"), "b"): Q(3, 5),
        (("b", "c"), "c"): Q(2, 5),
    }
    for item, probability in zip(ALTERNATIVES, full):
        kernel[(ALTERNATIVES, item)] = probability
    return kernel


def rum_point(gamma: Fraction, t: Fraction) -> Kernel:
    gamma = _validate_gamma(gamma)
    t = Q(t)
    if not 0 <= t <= gamma / 2:
        raise ValueError("RUM segment requires 0 <= t <= gamma/2")
    return kernel_with_full((Q(2, 5), Q(2, 5) - t, Q(1, 5) + t))


def nonrum_point(gamma: Fraction, s: Fraction) -> Kernel:
    gamma = _validate_gamma(gamma)
    s = Q(s)
    if not gamma <= s <= 2 * gamma:
        raise ValueError("non-RUM segment requires gamma <= s <= 2 gamma")
    return kernel_with_full((Q(2, 5) + s, Q(2, 5) - s, Q(1, 5)))


def rum_ranking_weights(t: Fraction) -> tuple[Fraction, ...]:
    t = Q(t)
    if not 0 <= t <= Q(1, 5):
        raise ValueError("ranking weights require 0 <= t <= 1/5")
    return (
        Q(1, 5) + t,
        Q(1, 5) - t,
        Q(1, 5),
        Q(1, 5) - t,
        Q(0),
        Q(1, 5) + t,
    )


def kernel_from_ranking_weights(weights: Sequence[Fraction]) -> Kernel:
    weights = tuple(Q(value) for value in weights)
    if len(weights) != len(RANKINGS) or min(weights) < 0:
        raise ValueError("invalid ranking weights")
    if sum(weights, Q(0)) != 1:
        raise ValueError("ranking weights must sum to one")
    return {
        (menu, item): sum(
            weight
            for ranking, weight in zip(RANKINGS, weights)
            if next(value for value in ranking if value in menu) == item
        )
        for menu in MENUS
        for item in menu
    }


def menu_l1(left: Mapping, right: Mapping, menu: tuple[str, ...]) -> Fraction:
    return sum(abs(left[(menu, item)] - right[(menu, item)]) for item in menu)


def kernel_l1(left: Mapping, right: Mapping) -> Fraction:
    return max(menu_l1(left, right, menu) for menu in MENUS)


def kernel_tv(left: Mapping, right: Mapping) -> Fraction:
    return kernel_l1(left, right) / 2


def symmetric_ratio(left: Mapping, right: Mapping) -> Fraction:
    return max(
        max(left[(menu, item)] / right[(menu, item)],
            right[(menu, item)] / left[(menu, item)])
        for menu in MENUS
        for item in menu
    )


def regularity_gap(kernel: Mapping) -> Fraction:
    return kernel[(ALTERNATIVES, "a")] - kernel[(("a", "b"), "a")]


def luce_cycle_defect(kernel: Mapping) -> Fraction:
    left = (
        kernel[(("a", "b"), "a")]
        * kernel[(("b", "c"), "b")]
        * kernel[(("a", "c"), "c")]
    )
    right = (
        kernel[(("a", "b"), "b")]
        * kernel[(("b", "c"), "c")]
        * kernel[(("a", "c"), "a")]
    )
    return abs(left - right)


def delta_modulus(gamma: Fraction) -> Fraction:
    return _validate_gamma(gamma)


def lambda_modulus(gamma: Fraction) -> Fraction:
    gamma = _validate_gamma(gamma)
    return 1 + Q(5, 2) * gamma


def huber_threshold(gamma: Fraction) -> Fraction:
    gamma = delta_modulus(gamma)
    return gamma / (1 + gamma)


def primal_parameters(gamma: Fraction) -> tuple[Fraction, Fraction]:
    gamma = _validate_gamma(gamma)
    return Q(5, 2) * gamma * gamma, gamma


def common_huber_observation(
    left: Mapping,
    right: Mapping,
    epsilon: Fraction,
) -> Kernel:
    epsilon = Q(epsilon)
    observed = {}
    for menu in MENUS:
        mandatory = [
            (1 - epsilon) * max(left[(menu, item)], right[(menu, item)])
            for item in menu
        ]
        mandatory[0] += 1 - sum(mandatory, Q(0))
        for item, value in zip(menu, mandatory):
            observed[(menu, item)] = value
    return observed


def common_recording_observation(
    left: Mapping,
    right: Mapping,
    lower: Fraction,
    upper: Fraction,
) -> tuple[Kernel, Kernel, Kernel]:
    lower = Q(lower)
    upper = Q(upper)
    if not 0 < lower <= upper <= 1:
        raise ValueError("invalid recording interval")
    joint = {}
    left_recording = {}
    right_recording = {}
    for menu in MENUS:
        for item in menu:
            key = (menu, item)
            mass = max(lower * left[key], lower * right[key])
            joint[key] = mass
            left_recording[key] = mass / left[key]
            right_recording[key] = mass / right[key]
            if not (
                lower <= left_recording[key] <= upper
                and lower <= right_recording[key] <= upper
            ):
                raise ValueError("recording neighborhoods do not overlap")
        if sum(joint[(menu, item)] for item in menu) > 1:
            raise AssertionError("recorded mass exceeds one")
    return joint, left_recording, right_recording

