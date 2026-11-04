"""Finite-sample ASMP-9 reward-ray identification utilities.

Development code for v0.5. This module is intentionally dependency-light and
does not constitute a registered result.
"""

from __future__ import annotations

import itertools
import math
import random
from fractions import Fraction
from functools import reduce
from math import gcd
from typing import Iterable, Sequence


Vector = tuple[int, ...]


def sign(value: int) -> int:
    return (value > 0) - (value < 0)


def vector_gcd(values: Iterable[int]) -> int:
    return reduce(gcd, (abs(v) for v in values), 0)


def primitive_rays(dimension: int, bound: int) -> list[Vector]:
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    if bound < 1:
        raise ValueError("bound must be positive")
    rays: list[Vector] = []
    for vector in itertools.product(range(-bound, bound + 1), repeat=dimension):
        if any(vector) and vector_gcd(vector) == 1:
            rays.append(tuple(vector))
    return rays


def primitive_ray_count(dimension: int, bound: int) -> int:
    """Count oriented primitive rays without materializing the box."""
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    if bound < 1:
        raise ValueError("bound must be positive")

    def mobius(n: int) -> int:
        factors = 0
        remaining = n
        prime = 2
        while prime * prime <= remaining:
            if remaining % prime == 0:
                remaining //= prime
                factors += 1
                if remaining % prime == 0:
                    return 0
                while remaining % prime == 0:
                    remaining //= prime
            prime += 1
        if remaining > 1:
            factors += 1
        return -1 if factors % 2 else 1

    total = 0
    for scale in range(1, bound + 1):
        mu = mobius(scale)
        if mu:
            radius = bound // scale
            total += mu * ((2 * radius + 1) ** dimension - 1)
    return total


def theorem_width(bound: int) -> int:
    if bound < 1:
        raise ValueError("bound must be positive")
    return 1 if bound <= 2 else bound - 1


def farey_sequence(order: int) -> list[Fraction]:
    if order < 1:
        raise ValueError("order must be positive")
    sequence = [Fraction(0, 1)]
    a, b, c, d = 0, 1, 1, order
    while c <= order:
        sequence.append(Fraction(c, d))
        k = (order + b) // d
        a, b, c, d = c, d, k * c - a, k * d - b
    return sequence


def bounded_unit_ratios(bound: int) -> list[Fraction]:
    values = {
        Fraction(numerator, denominator)
        for numerator in range(1, bound + 1)
        for denominator in range(1, bound + 1)
        if numerator <= denominator
    }
    return sorted(values)


def logical_query_bound(dimension: int, bound: int) -> int:
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    farey_count = len(farey_sequence(max(1, bound - 1)))
    return dimension + (dimension - 1) * (
        2 + math.ceil(math.log2(farey_count))
    )


def repetitions_required(
    eta: float, alpha: float, logical_queries: int
) -> int:
    if not (0.0 <= eta < 0.5):
        raise ValueError("eta must lie in [0, 1/2)")
    if not (0.0 < alpha < 0.5):
        raise ValueError("alpha must lie in (0, 1/2)")
    if logical_queries < 1:
        raise ValueError("logical_queries must be positive")
    channel_gap = 1.0 - 2.0 * eta
    return math.ceil(
        8.0
        / (channel_gap * channel_gap)
        * math.log(2.0 * logical_queries / alpha)
    )


def binary_entropy(probability: float) -> float:
    if not (0.0 <= probability <= 1.0):
        raise ValueError("probability must lie in [0,1]")
    if probability in (0.0, 1.0):
        return 0.0
    return -probability * math.log2(probability) - (
        1.0 - probability
    ) * math.log2(1.0 - probability)


def channel_capacity(eta: float) -> float:
    if not (0.0 <= eta <= 0.5):
        raise ValueError("eta must lie in [0,1/2]")
    return 1.0 - binary_entropy(eta)


def fano_fixed_budget_lower_bound(
    dimension: int, bound: int, eta: float, alpha: float
) -> float:
    if not (0.0 < alpha < 0.5):
        raise ValueError("alpha must lie in (0,1/2)")
    capacity = channel_capacity(eta)
    if capacity == 0.0:
        return math.inf
    hypotheses = primitive_ray_count(dimension, bound)
    numerator = (
        (1.0 - alpha) * math.log2(hypotheses) - binary_entropy(alpha)
    )
    return max(0.0, numerator / capacity)


def bernoulli_kl(left: float, right: float) -> float:
    if not (0.0 <= left <= 1.0 and 0.0 <= right <= 1.0):
        raise ValueError("Bernoulli probabilities must lie in [0,1]")
    total = 0.0
    if left > 0.0:
        if right == 0.0:
            return math.inf
        total += left * math.log(left / right)
    if left < 1.0:
        if right == 1.0:
            return math.inf
        total += (1.0 - left) * math.log(
            (1.0 - left) / (1.0 - right)
        )
    return total


def tie_strict_max_kl(eta: float) -> float:
    if not (0.0 < eta < 0.5):
        raise ValueError("eta must lie in (0,1/2)")
    return max(bernoulli_kl(0.5, eta), bernoulli_kl(eta, 0.5))


def nonadaptive_farey_lower_bound(
    bound: int, eta: float, alpha: float
) -> float:
    """Two-dimensional critical-width lower bound in binary responses."""
    if bound < 3:
        raise ValueError("bound must be at least three")
    if not (0.0 < alpha < 0.25):
        raise ValueError("alpha must lie in (0,1/4)")
    edge_count = len(farey_sequence(bound)) - 1
    return (
        edge_count
        / (2.0 * tie_strict_max_kl(eta))
        * math.log(1.0 / (4.0 * alpha))
    )


def farey_adjacency_audit(bound: int) -> dict[str, int | bool]:
    """Verify the critical-width endpoint-incidence argument exactly."""
    if bound < 3:
        raise ValueError("bound must be at least three")
    candidates = farey_sequence(bound)
    admissible = farey_sequence(bound - 1)
    admissible_set = set(admissible)
    maximum_separators = 0
    incidence_total = 0
    for left, right in itertools.pairwise(candidates):
        separators = [
            threshold
            for threshold in admissible
            if sign(left - threshold) != sign(right - threshold)
        ]
        expected = [
            endpoint
            for endpoint in (left, right)
            if endpoint in admissible_set
        ]
        if separators != expected:
            return {
                "bound": bound,
                "edge_count": len(candidates) - 1,
                "admissible_threshold_count": len(admissible),
                "maximum_edge_separators": max(
                    maximum_separators, len(separators)
                ),
                "incidence_total": incidence_total + len(separators),
                "valid": False,
            }
        maximum_separators = max(maximum_separators, len(separators))
        incidence_total += len(separators)
    return {
        "bound": bound,
        "edge_count": len(candidates) - 1,
        "admissible_threshold_count": len(admissible),
        "maximum_edge_separators": maximum_separators,
        "incidence_total": incidence_total,
        "valid": incidence_total <= 2 * len(admissible),
    }


def latent_sign(vector: Sequence[int], query: Sequence[int]) -> int:
    if len(vector) != len(query):
        raise ValueError("dimension mismatch")
    return sign(sum(a * b for a, b in zip(vector, query)))


def noisy_response(
    latent: int, eta: float, rng: random.Random
) -> int:
    if latent not in (-1, 0, 1):
        raise ValueError("latent sign must be -1, 0, or 1")
    if not (0.0 <= eta < 0.5):
        raise ValueError("eta must lie in [0,1/2)")
    probability = {-1: eta, 0: 0.5, 1: 1.0 - eta}[latent]
    return int(rng.random() < probability)


def classify_repeated(
    vector: Sequence[int],
    query: Sequence[int],
    eta: float,
    repetitions: int,
    rng: random.Random,
) -> int:
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    latent = latent_sign(vector, query)
    mean = sum(
        noisy_response(latent, eta, rng) for _ in range(repetitions)
    ) / repetitions
    lower = (eta + 0.5) / 2.0
    upper = (0.5 + (1.0 - eta)) / 2.0
    if mean < lower:
        return -1
    if mean > upper:
        return 1
    return 0


def _comparison_query(
    dimension: int,
    numerator_index: int,
    denominator_index: int,
    threshold: Fraction,
    coordinate_signs: Sequence[int],
) -> Vector:
    query = [0] * dimension
    query[numerator_index] = threshold.denominator * coordinate_signs[
        numerator_index
    ]
    query[denominator_index] = -threshold.numerator * coordinate_signs[
        denominator_index
    ]
    common = vector_gcd(query)
    if common > 1:
        query = [value // common for value in query]
    return tuple(query)


def _reconstruct_from_ratios(
    signs: Sequence[int], ratios: Sequence[Fraction | None], reference: int
) -> Vector:
    denominators = [
        ratio.denominator for ratio in ratios if ratio is not None
    ]
    scale = 1
    for denominator in denominators:
        scale = math.lcm(scale, denominator)
    magnitudes = [
        0 if ratio is None else ratio.numerator * (scale // ratio.denominator)
        for ratio in ratios
    ]
    if magnitudes[reference] == 0:
        raise AssertionError("reference coordinate vanished")
    common = vector_gcd(magnitudes)
    magnitudes = [value // common for value in magnitudes]
    return tuple(
        sign_value * magnitude
        for sign_value, magnitude in zip(signs, magnitudes)
    )


def identify_ray(
    vector: Sequence[int],
    bound: int,
    *,
    eta: float = 0.0,
    alpha: float = 0.01,
    seed: int = 0,
    force_repetitions: int | None = None,
    exact_oracle: bool = False,
) -> tuple[Vector | None, int, int]:
    """Identify one ray and return (estimate, response count, max width).

    The default uses repeated ternary-sign classification. Setting eta=0 still
    requires sampling because a latent tie emits a fair binary response.
    `exact_oracle=True` is a deterministic constructor check; its response
    count is the number of logical queries, not binary channel samples.
    """
    dimension = len(vector)
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    if max(abs(value) for value in vector) > bound:
        raise ValueError("vector exceeds bound")
    if vector_gcd(vector) != 1:
        raise ValueError("vector must be primitive")
    rng = random.Random(seed)
    k_bound = logical_query_bound(dimension, bound)
    repetitions = 1 if exact_oracle else (
        force_repetitions
        if force_repetitions is not None
        else repetitions_required(eta, alpha, k_bound)
    )
    if repetitions < 1:
        raise ValueError("force_repetitions must be positive")

    sample_count = 0
    max_width = 0

    def ask(query: Vector) -> int:
        nonlocal sample_count, max_width
        max_width = max(max_width, max(abs(value) for value in query))
        sample_count += repetitions
        if exact_oracle:
            return latent_sign(vector, query)
        return classify_repeated(vector, query, eta, repetitions, rng)

    coordinate_signs: list[int] = []
    for index in range(dimension):
        query = tuple(1 if j == index else 0 for j in range(dimension))
        coordinate_signs.append(ask(query))

    nonzero = [index for index, value in enumerate(coordinate_signs) if value]
    if not nonzero:
        return None, sample_count, max_width
    reference = nonzero[0]
    ratios: list[Fraction | None] = [None] * dimension
    ratios[reference] = Fraction(1, 1)
    farey = farey_sequence(max(1, bound - 1))
    candidates = bounded_unit_ratios(bound)

    for index in nonzero[1:]:
        one_query = _comparison_query(
            dimension,
            index,
            reference,
            Fraction(1, 1),
            coordinate_signs,
        )
        orientation = ask(one_query)
        if orientation == 0:
            ratios[index] = Fraction(1, 1)
            continue

        numerator_index, denominator_index = (
            (index, reference) if orientation < 0 else (reference, index)
        )
        low = 0
        high = len(farey) - 1
        exact: Fraction | None = None
        while low <= high:
            middle = (low + high) // 2
            threshold = farey[middle]
            query = _comparison_query(
                dimension,
                numerator_index,
                denominator_index,
                threshold,
                coordinate_signs,
            )
            answer = ask(query)
            if answer == 0:
                exact = threshold
                break
            if answer < 0:
                high = middle - 1
            else:
                low = middle + 1

        if exact is None:
            left = farey[max(0, high)]
            right = farey[min(len(farey) - 1, low)]
            inside = [value for value in candidates if left < value < right]
            if len(inside) != 1:
                return None, sample_count, max_width
            exact = inside[0]

        if exact == 0:
            return None, sample_count, max_width
        ratio = exact if orientation < 0 else 1 / exact
        ratios[index] = ratio

    estimate = _reconstruct_from_ratios(
        coordinate_signs, ratios, reference
    )
    if max(abs(value) for value in estimate) > bound:
        return None, sample_count, max_width
    return estimate, sample_count, max_width


def full_signature(vector: Sequence[int], width: int) -> tuple[int, ...]:
    dimension = len(vector)
    queries = primitive_rays(dimension, width)
    return tuple(latent_sign(vector, query) for query in queries)
