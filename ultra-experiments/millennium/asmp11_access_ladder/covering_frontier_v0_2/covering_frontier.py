"""Solver-certified covering designs plus exact finite-sample power."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import ceil, comb
from typing import Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix


@dataclass(frozen=True)
class CoveringSolution:
    n: int
    block_size: int
    support_size: int
    optimum: int
    selected_blocks: tuple[tuple[int, ...], ...]
    solver_status: int
    solver_message: str
    mip_gap: float
    mip_dual_bound: float
    mip_node_count: int
    counting_lower_bound: int
    schoenheim_lower_bound: int


@dataclass(frozen=True)
class ExactTestDesign:
    query_count: int
    samples_per_query: int
    cutoff: int
    null_tail: Fraction
    familywise_error_upper: Fraction
    signal_power_lower: Fraction

    @property
    def total_samples(self) -> int:
        return self.query_count * self.samples_per_query


def subsets(n: int, size: int) -> tuple[tuple[int, ...], ...]:
    return tuple(combinations(range(n), size))


def counting_lower_bound(n: int, block_size: int, support_size: int) -> int:
    return ceil(comb(n, support_size) / comb(block_size, support_size))


def schoenheim_lower_bound(n: int, block_size: int, support_size: int) -> int:
    """Recursive Schoenheim lower bound L(n, block_size, support_size)."""

    if support_size == 0:
        return 1
    return ceil(
        n
        * schoenheim_lower_bound(n - 1, block_size - 1, support_size - 1)
        / block_size
    )


def incidence_matrix(
    n: int, block_size: int, support_size: int
) -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[int, ...], ...], csc_matrix]:
    if not 0 < support_size <= block_size <= n:
        raise ValueError("require 0 < support_size <= block_size <= n")
    supports = subsets(n, support_size)
    blocks = subsets(n, block_size)
    support_index = {support: index for index, support in enumerate(supports)}
    rows: list[int] = []
    cols: list[int] = []
    for column, block in enumerate(blocks):
        for support in combinations(block, support_size):
            rows.append(support_index[tuple(support)])
            cols.append(column)
    data = np.ones(len(rows), dtype=float)
    matrix = csc_matrix((data, (rows, cols)), shape=(len(supports), len(blocks)))
    return supports, blocks, matrix


def verify_cover(
    n: int,
    block_size: int,
    support_size: int,
    selected_blocks: Sequence[Sequence[int]],
) -> bool:
    covered = set()
    for block in selected_blocks:
        if len(block) != block_size or len(set(block)) != block_size:
            return False
        if any(point < 0 or point >= n for point in block):
            return False
        covered.update(combinations(sorted(block), support_size))
    return len(covered) == comb(n, support_size)


def solve_covering(
    n: int,
    block_size: int,
    support_size: int,
    *,
    time_limit_seconds: float = 120.0,
) -> CoveringSolution:
    supports, blocks, matrix = incidence_matrix(n, block_size, support_size)
    variables = len(blocks)
    constraint = LinearConstraint(
        matrix,
        lb=np.ones(len(supports), dtype=float),
        ub=np.full(len(supports), np.inf, dtype=float),
    )
    result = milp(
        c=np.ones(variables, dtype=float),
        integrality=np.ones(variables, dtype=int),
        bounds=Bounds(np.zeros(variables), np.ones(variables)),
        constraints=constraint,
        options={"time_limit": time_limit_seconds, "mip_rel_gap": 0.0},
    )
    if result.status != 0 or result.x is None:
        raise RuntimeError(
            f"covering solver did not certify optimum for ({n},{block_size},{support_size}): "
            f"status={result.status} message={result.message}"
        )
    selected_indices = tuple(index for index, value in enumerate(result.x) if value > 0.5)
    selected = tuple(blocks[index] for index in selected_indices)
    optimum = len(selected)
    if not verify_cover(n, block_size, support_size, selected):
        raise AssertionError("solver witness does not cover every support")
    if abs(float(result.fun) - optimum) > 1e-7:
        raise AssertionError("rounded witness size disagrees with solver objective")
    return CoveringSolution(
        n=n,
        block_size=block_size,
        support_size=support_size,
        optimum=optimum,
        selected_blocks=selected,
        solver_status=int(result.status),
        solver_message=str(result.message),
        mip_gap=float(getattr(result, "mip_gap", 0.0)),
        mip_dual_bound=float(getattr(result, "mip_dual_bound", result.fun)),
        mip_node_count=int(getattr(result, "mip_node_count", 0)),
        counting_lower_bound=counting_lower_bound(n, block_size, support_size),
        schoenheim_lower_bound=schoenheim_lower_bound(n, block_size, support_size),
    )


def two_sided_binomial_tail(samples: int, cutoff: int, plus_probability: Fraction) -> Fraction:
    if samples < 1:
        raise ValueError("samples must be positive")
    if cutoff < 0:
        return Fraction(0)
    if 2 * cutoff >= samples:
        return Fraction(1)
    a = plus_probability.numerator
    b = plus_probability.denominator
    minus = b - a
    numerator = sum(
        comb(samples, x) * a**x * minus ** (samples - x)
        for x in range(cutoff + 1)
    )
    numerator += sum(
        comb(samples, x) * a**x * minus ** (samples - x)
        for x in range(samples - cutoff, samples + 1)
    )
    return Fraction(numerator, b**samples)


def most_permissive_cutoff(samples: int, query_count: int, alpha: Fraction) -> int | None:
    accepted = None
    for cutoff in range((samples - 1) // 2 + 1):
        tail = two_sided_binomial_tail(samples, cutoff, Fraction(1, 2))
        if query_count * tail <= alpha:
            accepted = cutoff
        else:
            break
    return accepted


def find_exact_design(
    query_count: int,
    flip_rate: Fraction,
    alpha: Fraction,
    target_power: Fraction,
    sample_cap: int,
) -> ExactTestDesign | None:
    if query_count < 1:
        raise ValueError("query_count must be positive")
    signal_probability = Fraction(1) - flip_rate
    for samples in range(1, sample_cap + 1):
        cutoff = most_permissive_cutoff(samples, query_count, alpha)
        if cutoff is None:
            continue
        null_tail = two_sided_binomial_tail(samples, cutoff, Fraction(1, 2))
        power = two_sided_binomial_tail(samples, cutoff, signal_probability)
        if power >= target_power:
            return ExactTestDesign(
                query_count=query_count,
                samples_per_query=samples,
                cutoff=cutoff,
                null_tail=null_tail,
                familywise_error_upper=query_count * null_tail,
                signal_power_lower=power,
            )
    return None


def worst_case_adaptive_covering_lemma_holds(
    n: int,
    block_size: int,
    support_size: int,
    all_negative_blocks: Sequence[Sequence[int]],
) -> bool:
    """A clean/planted separator needs a cover along its all-negative path."""

    return verify_cover(n, block_size, support_size, all_negative_blocks)
