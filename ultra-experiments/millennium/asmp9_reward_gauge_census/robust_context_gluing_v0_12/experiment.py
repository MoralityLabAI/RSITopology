"""Fresh-cell experiment for ASMP-9 robust context gluing v0.12."""

from __future__ import annotations

import random
from collections import Counter
from itertools import combinations
from typing import Any

import numpy as np

from exact_certificate import smallest_conditioning_witness
from robust_gluing import (
    arbitrary_query_bound,
    cycle_design_census,
    decompose,
    local_global_incidence,
    quotient_basis,
    simple_cycle_vectors,
)


def edge_universe(item_count: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations(range(item_count), 2))


def random_fixed_edge_contexts(
    item_count: int,
    context_count: int,
    edges_per_context: int,
    rng: random.Random,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    universe = edge_universe(item_count)
    if not 0 <= edges_per_context <= len(universe):
        raise ValueError("invalid fixed edge count")
    return tuple(
        tuple(sorted(rng.sample(universe, edges_per_context)))
        for _ in range(context_count)
    )


def run_exact_witness() -> dict[str, object]:
    result = smallest_conditioning_witness()
    expected = {
        "item_count": 4,
        "context_count": 2,
        "edge_count": 6,
        "local_rank": 5,
        "shared_rank": 3,
        "obstruction_dimension": 2,
        "short_total_support": 6,
        "short_normalized_gram": (("2/3", "0"), ("0", "2/3")),
        "short_sigma_min_squared": "2/3",
        "short_amplification_squared": "3/2",
        "robust_total_support": 8,
        "robust_normalized_gram": (("1", "0"), ("0", "1")),
        "robust_sigma_min_squared": "1",
        "robust_amplification_squared": "1",
    }
    return {
        "certificate": result,
        "expected": expected,
        "exact_match": result == expected,
    }


def run_fresh_cells(spec: dict[str, Any]) -> dict[str, Any]:
    seed = int(spec["seed"])
    count = int(spec["count"])
    item_count = int(spec["item_count"])
    context_count = int(spec["context_count"])
    edges_per_context = int(spec["edges_per_context"])
    tolerance = float(spec["tolerance"])
    rng = random.Random(seed)

    dimension_distribution: Counter[int] = Counter()
    pythagorean_mismatch_count = 0
    dimension_mismatch_count = 0
    shared_control_mismatch_count = 0
    local_projection_mismatch_count = 0
    radius_optimality_mismatch_count = 0
    underquery_mismatch_count = 0
    orthonormal_mismatch_count = 0
    normalized_bound_mismatch_count = 0
    cycle_basis_mismatch_count = 0
    shortest_suboptimal_count = 0
    locally_scalar_gluing_positive_count = 0
    maximum_amplification_ratio = 1.0

    for _ in range(count):
        contexts = random_fixed_edge_contexts(
            item_count, context_count, edges_per_context, rng
        )
        local, shared, labelled = local_global_incidence(
            item_count, contexts
        )
        quotient = quotient_basis(local, shared)
        dimension = quotient.shape[1]
        expected_dimension = int(
            np.linalg.matrix_rank(local) - np.linalg.matrix_rank(shared)
        )
        dimension_mismatch_count += int(dimension != expected_dimension)
        dimension_distribution[dimension] += 1

        shared_utility = np.array(
            [rng.randint(-7, 7) for _ in range(item_count)], dtype=float
        )
        shared_flow = shared @ shared_utility
        shared_result = decompose(local, shared, shared_flow)
        shared_control_mismatch_count += int(
            max(
                shared_result.rho_local,
                shared_result.rho_glue,
                shared_result.rho_total,
            )
            > tolerance
        )

        local_utility = np.array(
            [
                rng.randint(-7, 7)
                for _ in range(item_count * context_count)
            ],
            dtype=float,
        )
        local_flow = local @ local_utility
        local_result = decompose(local, shared, local_flow)
        local_projection_mismatch_count += int(
            local_result.rho_local > tolerance
        )
        locally_scalar_gluing_positive_count += int(
            local_result.rho_glue > tolerance
        )

        arbitrary = np.array(
            [rng.randint(-11, 11) for _ in range(len(labelled))],
            dtype=float,
        )
        result = decompose(local, shared, arbitrary)
        pythagorean_mismatch_count += int(
            result.pythagorean_residual > tolerance
        )
        least_squares = np.linalg.lstsq(shared, arbitrary, rcond=None)[0]
        direct_radius = float(
            np.linalg.norm(arbitrary - shared @ least_squares)
        )
        radius_optimality_mismatch_count += int(
            abs(direct_radius - result.rho_total) > tolerance
        )

        under_rows = max(0, dimension - 1)
        under_design = np.eye(dimension, dtype=float)[:under_rows]
        under_bound = arbitrary_query_bound(under_design)
        underquery_mismatch_count += int(
            under_bound["rank"] >= dimension
            or under_bound["sigma_min"] != 0.0
        )

        orthonormal = arbitrary_query_bound(np.eye(dimension, dtype=float))
        orthonormal_mismatch_count += int(
            abs(float(orthonormal["sigma_min"]) - 1.0) > tolerance
            or abs(float(orthonormal["amplification"]) - 1.0) > tolerance
        )

        random_design = np.array(
            [
                [rng.gauss(0.0, 1.0) for _ in range(dimension)]
                for _ in range(dimension)
            ],
            dtype=float,
        )
        row_norms = np.linalg.norm(random_design, axis=1)
        random_design = random_design / row_norms[:, None]
        normalized_bound = arbitrary_query_bound(random_design)
        normalized_bound_mismatch_count += int(
            float(normalized_bound["sigma_min"]) > 1.0 + tolerance
        )

        cycles = simple_cycle_vectors(item_count, labelled)
        census = cycle_design_census(cycles, quotient)
        cycle_basis_mismatch_count += int(
            census.obstruction_dimension != dimension
            or census.e_optimal is None
            or census.shortest_best is None
            or census.spanning_design_count == 0
        )
        if census.e_optimal is not None and census.shortest_best is not None:
            ratio = (
                census.shortest_best.amplification
                / census.e_optimal.amplification
            )
            maximum_amplification_ratio = max(
                maximum_amplification_ratio, ratio
            )
            shortest_suboptimal_count += int(ratio > 1.0 + tolerance)

    return {
        **spec,
        "actual_count": count,
        "dimension_distribution": dict(
            sorted(dimension_distribution.items())
        ),
        "pythagorean_mismatch_count": pythagorean_mismatch_count,
        "dimension_mismatch_count": dimension_mismatch_count,
        "shared_control_mismatch_count": shared_control_mismatch_count,
        "local_projection_mismatch_count": local_projection_mismatch_count,
        "radius_optimality_mismatch_count": (
            radius_optimality_mismatch_count
        ),
        "underquery_mismatch_count": underquery_mismatch_count,
        "orthonormal_mismatch_count": orthonormal_mismatch_count,
        "normalized_bound_mismatch_count": normalized_bound_mismatch_count,
        "cycle_basis_mismatch_count": cycle_basis_mismatch_count,
        "shortest_suboptimal_count": shortest_suboptimal_count,
        "locally_scalar_gluing_positive_count": (
            locally_scalar_gluing_positive_count
        ),
        "maximum_amplification_ratio": maximum_amplification_ratio,
    }
