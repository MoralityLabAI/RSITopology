from __future__ import annotations

import bisect
import itertools
import math
from fractions import Fraction
from functools import lru_cache
from typing import Sequence


Vector = tuple[int, ...]


def sign(value: int) -> int:
    return (value > 0) - (value < 0)


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(int(a) * int(b) for a, b in zip(left, right))


def vector_gcd(vector: Sequence[int]) -> int:
    value = 0
    for coordinate in vector:
        value = math.gcd(value, abs(int(coordinate)))
    return value


def primitive(vector: Sequence[int]) -> Vector:
    divisor = vector_gcd(vector)
    if divisor == 0:
        raise ValueError("zero vector")
    return tuple(int(value) // divisor for value in vector)


def primitive_rays(dimension: int, bound: int) -> list[Vector]:
    return [
        tuple(raw)
        for raw in itertools.product(
            range(-bound, bound + 1), repeat=dimension
        )
        if any(raw) and vector_gcd(raw) == 1
    ]


def sharp_zero_width(bound: int) -> int:
    if bound < 1:
        raise ValueError("bound must be positive")
    return 1 if bound <= 2 else bound - 1


@lru_cache(maxsize=None)
def farey_fractions(order: int) -> tuple[Fraction, ...]:
    if order < 1:
        raise ValueError("Farey order must be positive")
    values = {
        Fraction(numerator, denominator)
        for denominator in range(1, order + 1)
        for numerator in range(0, denominator + 1)
        if math.gcd(numerator, denominator) == 1
    }
    return tuple(sorted(values))


def _threshold_between(
    first: Fraction, second: Fraction, order: int
) -> Fraction:
    if first == second:
        raise ValueError("ratios must differ")
    low, high = sorted((first, second))
    sequence = farey_fractions(order)
    index = bisect.bisect_left(sequence, low)
    if index == len(sequence):
        raise AssertionError("no Farey threshold found")
    threshold = sequence[index]
    if threshold > high:
        raise AssertionError(
            f"Farey cell contains two target ratios: {low}, {high}"
        )
    return threshold


def construct_exact_separator(
    first: Vector, second: Vector, bound: int
) -> Vector:
    if len(first) != len(second) or len(first) < 2:
        raise ValueError("matching dimension >=2 required")
    if first == second:
        raise ValueError("identical rays cannot be separated")
    if vector_gcd(first) != 1 or vector_gcd(second) != 1:
        raise ValueError("primitive representatives required")
    if max(map(abs, first + second)) > bound:
        raise ValueError("ray exceeds bound")

    first_signs = tuple(sign(value) for value in first)
    second_signs = tuple(sign(value) for value in second)
    for index, (left_sign, right_sign) in enumerate(
        zip(first_signs, second_signs)
    ):
        if left_sign != right_sign:
            query = [0] * len(first)
            query[index] = 1
            return tuple(query)

    reference = next(index for index, value in enumerate(first) if value)
    differing = None
    for index in range(len(first)):
        if (
            abs(first[index]) * abs(second[reference])
            != abs(second[index]) * abs(first[reference])
        ):
            differing = index
            break
    if differing is None:
        raise AssertionError("same signs and ratios imply identical primitive ray")

    i, k = differing, reference
    ratio_first = Fraction(abs(first[i]), abs(first[k]))
    ratio_second = Fraction(abs(second[i]), abs(second[k]))
    if (ratio_first <= 1 < ratio_second) or (
        ratio_second <= 1 < ratio_first
    ):
        threshold = Fraction(1, 1)
    else:
        if ratio_first > 1 and ratio_second > 1:
            i, k = k, i
            ratio_first = 1 / ratio_first
            ratio_second = 1 / ratio_second
        threshold = _threshold_between(
            ratio_first, ratio_second, max(1, bound - 1)
        )

    query = [0] * len(first)
    query[i] = threshold.denominator * sign(first[i])
    query[k] = -threshold.numerator * sign(first[k])
    reduced = primitive(query)
    if sign(dot(reduced, first)) == sign(dot(reduced, second)):
        raise AssertionError(
            f"construction failed: {first=}, {second=}, {reduced=}"
        )
    if max(map(abs, reduced)) > sharp_zero_width(bound):
        raise AssertionError("constructed query exceeds sharp zero width")
    return reduced


def lower_witness(dimension: int, bound: int) -> tuple[Vector, Vector]:
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    if bound <= 2:
        first, second = (1, 0), (0, 1)
    else:
        first = (bound, bound - 1)
        second = (bound - 1, bound - 2)
    padding = (0,) * (dimension - 2)
    return first + padding, second + padding


def narrower_exact_separator_exists(dimension: int, bound: int) -> bool:
    limit = sharp_zero_width(bound) - 1
    if limit == 0:
        return False
    first, second = lower_witness(dimension, bound)
    for query in itertools.product(range(-limit, limit + 1), repeat=dimension):
        if not any(query):
            continue
        if sign(dot(query, first)) != sign(dot(query, second)):
            return True
    return False

