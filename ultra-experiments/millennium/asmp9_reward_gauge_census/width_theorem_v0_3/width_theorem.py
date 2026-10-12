from __future__ import annotations

import itertools
import math
from collections.abc import Sequence


Vector = tuple[int, ...]


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


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(int(a) * int(b) for a, b in zip(left, right))


def sharp_width(bound: int) -> int:
    if bound < 1:
        raise ValueError("bound must be positive")
    return 2 if bound == 1 else 2 * bound - 1


def _equal_extreme_separator(
    bound: int, common_sign: int, other_u: int, other_v: int
) -> tuple[int, int]:
    # Returns (coefficient on common +/-B coordinate, coefficient on other).
    if other_u == other_v:
        raise ValueError("other coordinates must differ")
    swapped = other_u < other_v
    b, d = (other_v, other_u) if swapped else (other_u, other_v)
    h = b - d
    if h >= 2:
        other_coefficient = bound
        common_coefficient_transformed = -d - 1
    else:
        if h != 1:
            raise AssertionError("positive integer difference expected")
        other_coefficient = bound + 1
        common_coefficient_transformed = -b if b >= 1 else 1 - b
    common_coefficient = common_sign * common_coefficient_transformed
    pair = (common_coefficient, other_coefficient)
    if swapped:
        # The construction now makes v positive and u negative, which is fine.
        return pair
    return pair


def construct_separator(first: Vector, second: Vector, bound: int) -> Vector:
    if len(first) != len(second):
        raise ValueError("dimension mismatch")
    if first == second:
        raise ValueError("identical rays cannot be separated")
    dimension = len(first)
    if dimension < 2:
        raise ValueError("the sharp theorem is stated for dimension >= 2")
    if max(map(abs, first + second)) > bound:
        raise ValueError("vector exceeds registered bound")
    if vector_gcd(first) != 1 or vector_gcd(second) != 1:
        raise ValueError("primitive representatives required")

    for index, value in enumerate(first):
        if second[index] != -value:
            break
    else:
        coordinate = next(i for i, value in enumerate(first) if value)
        query = [0] * dimension
        query[coordinate] = 1 if first[coordinate] > 0 else -1
        return tuple(query)

    selected = None
    for i in range(dimension):
        for j in range(i + 1, dimension):
            determinant = first[i] * second[j] - first[j] * second[i]
            if determinant:
                selected = (i, j, determinant)
                break
        if selected:
            break
    if selected is None:
        raise AssertionError("distinct primitive dependent rays must be antipodal")

    i, j, determinant = selected
    a, b = first[i], first[j]
    c, d = second[i], second[j]
    sign = 1 if determinant > 0 else -1
    x = sign * (d + b)
    y = sign * (-c - a)
    target = sharp_width(bound)

    if max(abs(x), abs(y)) > target:
        if abs(a + c) == 2 * bound:
            common_sign = 1 if a > 0 else -1
            x, y = _equal_extreme_separator(
                bound, common_sign, b, d
            )
        elif abs(b + d) == 2 * bound:
            common_sign = 1 if b > 0 else -1
            y, x = _equal_extreme_separator(
                bound, common_sign, a, c
            )
        else:
            raise AssertionError("only an equal extreme can attain width 2B")

    query = [0] * dimension
    query[i] = x
    query[j] = y
    reduced = primitive(query)
    first_score = dot(reduced, first)
    second_score = dot(reduced, second)
    if first_score * second_score >= 0:
        raise AssertionError(
            f"construction failed: {first=} {second=} {reduced=} "
            f"{first_score=} {second_score=}"
        )
    if max(map(abs, reduced)) > target:
        raise AssertionError("constructed query exceeds sharp width")
    return reduced


def lower_witness(dimension: int, bound: int) -> tuple[Vector, Vector]:
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    if bound == 1:
        first = (1, 0)
        second = (1, 1)
    else:
        first = (bound, bound - 1)
        second = (bound - 1, bound - 2)
    padding = (0,) * (dimension - 2)
    return first + padding, second + padding


def any_separator_below_sharp_width(dimension: int, bound: int) -> bool:
    first, second = lower_witness(dimension, bound)
    limit = sharp_width(bound) - 1
    for query in itertools.product(range(-limit, limit + 1), repeat=dimension):
        if not any(query):
            continue
        if dot(query, first) * dot(query, second) < 0:
            return True
    return False

