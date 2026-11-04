"""Small-registry information-design calculations for ASMP-9 v0.5.

The LP maximizes the minimum pairwise Bhattacharyya information accumulated per
query by a randomized nonadaptive design. It is a development diagnostic, not
the adaptive theorem and not a registered result.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linprog

from finite_sample import Vector, latent_sign, primitive_rays


def response_probability(latent: int, eta: float) -> float:
    if latent not in (-1, 0, 1):
        raise ValueError("latent must be -1, 0, or 1")
    if not (0.0 <= eta < 0.5):
        raise ValueError("eta must lie in [0,1/2)")
    return {-1: eta, 0: 0.5, 1: 1.0 - eta}[latent]


def bhattacharyya_information(
    left_latent: int, right_latent: int, eta: float
) -> float:
    left = response_probability(left_latent, eta)
    right = response_probability(right_latent, eta)
    coefficient = math.sqrt(left * right) + math.sqrt(
        (1.0 - left) * (1.0 - right)
    )
    if coefficient == 0.0:
        return math.inf
    return -math.log(coefficient)


def unique_signature_queries(
    hypotheses: Sequence[Vector], width: int
) -> tuple[list[Vector], np.ndarray]:
    """Return one primitive query per distinct signature up to global negation."""
    if width < 1:
        raise ValueError("width must be positive")
    dimension = len(hypotheses[0])
    representatives: dict[tuple[int, ...], Vector] = {}
    for query in primitive_rays(dimension, width):
        signature = tuple(latent_sign(vector, query) for vector in hypotheses)
        negated = tuple(-value for value in signature)
        key = min(signature, negated)
        representatives.setdefault(key, query)
    keys = sorted(representatives)
    queries = [representatives[key] for key in keys]
    signatures = np.asarray(keys, dtype=np.int8).T
    return queries, signatures


@dataclass(frozen=True)
class DesignResult:
    dimension: int
    bound: int
    width: int
    eta: float
    hypothesis_count: int
    query_class_count: int
    pair_count: int
    minimum_information: float
    support_size: int
    status: str


def solve_information_design(
    dimension: int, bound: int, width: int, eta: float
) -> DesignResult:
    hypotheses = primitive_rays(dimension, bound)
    _, signatures = unique_signature_queries(hypotheses, width)
    pairs = list(itertools.combinations(range(len(hypotheses)), 2))
    query_count = signatures.shape[1]
    information = np.empty((len(pairs), query_count), dtype=np.float64)
    lookup = {
        (left, right): bhattacharyya_information(left, right, eta)
        for left in (-1, 0, 1)
        for right in (-1, 0, 1)
    }
    for pair_index, (left, right) in enumerate(pairs):
        information[pair_index] = [
            lookup[(int(a), int(b))]
            for a, b in zip(signatures[left], signatures[right])
        ]

    # Variables are query probabilities followed by the minimum information t.
    objective = np.zeros(query_count + 1)
    objective[-1] = -1.0
    constraints = np.hstack(
        [-information, np.ones((len(pairs), 1), dtype=np.float64)]
    )
    result = linprog(
        objective,
        A_ub=constraints,
        b_ub=np.zeros(len(pairs)),
        A_eq=np.asarray([[1.0] * query_count + [0.0]]),
        b_eq=np.asarray([1.0]),
        bounds=[(0.0, 1.0)] * query_count + [(0.0, None)],
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    weights = result.x[:-1]
    return DesignResult(
        dimension=dimension,
        bound=bound,
        width=width,
        eta=eta,
        hypothesis_count=len(hypotheses),
        query_class_count=query_count,
        pair_count=len(pairs),
        minimum_information=float(result.x[-1]),
        support_size=int(np.count_nonzero(weights > 1e-10)),
        status="positive" if result.x[-1] > 1e-10 else "zero",
    )


def mle_union_bound_samples(
    hypothesis_count: int,
    minimum_information: float,
    alpha: float,
) -> float:
    """Continuous-allocation ML union-bound sample count (no rounding term)."""
    if not (0.0 < alpha < 0.5):
        raise ValueError("alpha must lie in (0,1/2)")
    if minimum_information <= 0.0:
        return math.inf
    return math.log((hypothesis_count - 1) / alpha) / minimum_information
