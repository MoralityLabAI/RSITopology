from __future__ import annotations

import hashlib
import itertools
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix


Vector = tuple[int, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def vector_gcd(vector: Sequence[int]) -> int:
    value = 0
    for coordinate in vector:
        value = math.gcd(value, abs(int(coordinate)))
    return value


def first_nonzero_positive(vector: Sequence[int]) -> bool:
    for coordinate in vector:
        if coordinate:
            return coordinate > 0
    raise ValueError("zero vector has no orientation")


def primitive_vectors(
    dimension: int,
    bound: int,
    *,
    canonical_orientation: bool,
) -> list[Vector]:
    if dimension < 1 or bound < 1:
        raise ValueError("dimension and bound must be positive")
    vectors: list[Vector] = []
    for raw in itertools.product(range(-bound, bound + 1), repeat=dimension):
        if not any(raw):
            continue
        if vector_gcd(raw) != 1:
            continue
        if canonical_orientation and not first_nonzero_positive(raw):
            continue
        vectors.append(tuple(int(value) for value in raw))
    return sorted(vectors)


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    return sum(int(a) * int(b) for a, b in zip(left, right))


def possible_signs(score: int, delta: Fraction) -> frozenset[int]:
    if delta < 0:
        raise ValueError("delta must be nonnegative")
    score_q = Fraction(score, 1)
    low = score_q - delta
    high = score_q + delta
    signs: set[int] = set()
    if low < 0:
        signs.add(-1)
    if low <= 0 <= high:
        signs.add(0)
    if high > 0:
        signs.add(1)
    return frozenset(signs)


def robustly_separates(
    query: Vector,
    first: Vector,
    second: Vector,
    delta: Fraction,
) -> bool:
    return possible_signs(dot(query, first), delta).isdisjoint(
        possible_signs(dot(query, second), delta)
    )


@dataclass(frozen=True)
class Coverage:
    candidates: tuple[Vector, ...]
    queries: tuple[Vector, ...]
    pairs: tuple[tuple[int, int], ...]
    covered_pair_indices: tuple[frozenset[int], ...]
    unresolved_pair_indices: tuple[int, ...]

    @property
    def complete(self) -> bool:
        return not self.unresolved_pair_indices


def build_coverage(
    dimension: int,
    reward_bound: int,
    query_width: int,
    delta: Fraction,
) -> Coverage:
    candidates = tuple(
        primitive_vectors(
            dimension, reward_bound, canonical_orientation=False
        )
    )
    queries = tuple(
        primitive_vectors(dimension, query_width, canonical_orientation=True)
    )
    pairs = tuple(itertools.combinations(range(len(candidates)), 2))
    covered: list[frozenset[int]] = []
    union: set[int] = set()
    for query in queries:
        indices = frozenset(
            pair_index
            for pair_index, (left_index, right_index) in enumerate(pairs)
            if robustly_separates(
                query,
                candidates[left_index],
                candidates[right_index],
                delta,
            )
        )
        covered.append(indices)
        union.update(indices)
    unresolved = tuple(sorted(set(range(len(pairs))) - union))
    return Coverage(
        candidates=candidates,
        queries=queries,
        pairs=pairs,
        covered_pair_indices=tuple(covered),
        unresolved_pair_indices=unresolved,
    )


@dataclass(frozen=True)
class SetCoverResult:
    status: str
    objective: int | None
    dual_bound: float | None
    mip_gap: float | None
    selected_query_indices: tuple[int, ...]
    independently_covers_all: bool
    message: str


def solve_minimum_query_cover(
    coverage: Coverage,
    *,
    time_limit_seconds: float,
) -> SetCoverResult:
    if not coverage.complete:
        raise ValueError("set cover is undefined for an incomplete query grammar")
    pair_count = len(coverage.pairs)
    query_count = len(coverage.queries)
    rows: list[int] = []
    columns: list[int] = []
    for query_index, pair_indices in enumerate(coverage.covered_pair_indices):
        for pair_index in pair_indices:
            rows.append(pair_index)
            columns.append(query_index)
    data = np.ones(len(rows), dtype=np.float64)
    matrix = csc_matrix(
        (data, (rows, columns)), shape=(pair_count, query_count)
    )
    constraints = LinearConstraint(
        matrix,
        lb=np.ones(pair_count, dtype=np.float64),
        ub=np.full(pair_count, np.inf, dtype=np.float64),
    )
    result = milp(
        c=np.ones(query_count, dtype=np.float64),
        integrality=np.ones(query_count, dtype=np.int8),
        bounds=Bounds(
            np.zeros(query_count, dtype=np.float64),
            np.ones(query_count, dtype=np.float64),
        ),
        constraints=constraints,
        options={
            "time_limit": float(time_limit_seconds),
            "mip_rel_gap": 0.0,
            "presolve": True,
        },
    )
    if result.x is None:
        return SetCoverResult(
            status="unavailable",
            objective=None,
            dual_bound=getattr(result, "mip_dual_bound", None),
            mip_gap=getattr(result, "mip_gap", None),
            selected_query_indices=(),
            independently_covers_all=False,
            message=str(result.message),
        )
    selected = tuple(
        index for index, value in enumerate(result.x) if value > 0.5
    )
    replayed: set[int] = set()
    for query_index in selected:
        replayed.update(coverage.covered_pair_indices[query_index])
    covers_all = len(replayed) == pair_count
    objective_float = float(result.fun)
    objective = int(round(objective_float))
    dual_bound = float(getattr(result, "mip_dual_bound", math.nan))
    mip_gap = float(getattr(result, "mip_gap", math.nan))
    optimal = (
        int(result.status) == 0
        and abs(objective_float - objective) <= 1e-8
        and abs(dual_bound - objective_float) <= 1e-8
        and abs(mip_gap) <= 1e-12
        and covers_all
    )
    return SetCoverResult(
        status="optimal" if optimal else "invalid_or_nonoptimal",
        objective=objective,
        dual_bound=dual_bound,
        mip_gap=mip_gap,
        selected_query_indices=selected,
        independently_covers_all=covers_all,
        message=str(result.message),
    )


def collision_witness(coverage: Coverage) -> dict[str, object] | None:
    if not coverage.unresolved_pair_indices:
        return None
    pair_index = coverage.unresolved_pair_indices[0]
    left_index, right_index = coverage.pairs[pair_index]
    left = coverage.candidates[left_index]
    right = coverage.candidates[right_index]
    replay = []
    for query in coverage.queries:
        left_signs = sorted(possible_signs(dot(query, left), Fraction(0)))
        right_signs = sorted(possible_signs(dot(query, right), Fraction(0)))
        replay.append(
            {
                "query": list(query),
                "left_score": dot(query, left),
                "right_score": dot(query, right),
                "left_exact_sign": left_signs,
                "right_exact_sign": right_signs,
            }
        )
    return {
        "pair_index": pair_index,
        "left": list(left),
        "right": list(right),
    }


def parse_fraction(value: str | int) -> Fraction:
    if isinstance(value, int):
        return Fraction(value, 1)
    return Fraction(value)


def vector_text(vector: Sequence[int]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"

