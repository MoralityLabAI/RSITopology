from fractions import Fraction as Q
from itertools import permutations
import json
from pathlib import Path

import pytest

from reference_weight import (
    minimal_reference_switch_witness,
    minimax_regret_certificate,
    ordering_cost,
    ordering_weight_region,
    robust_chain_certificate,
    weight_region_contains,
)


HERE = Path(__file__).resolve().parent
V048 = HERE.parent / "ordering_modulus_v0_48"


def exhaustive_common(bound_tables, vertices):
    width = len(vertices[0])
    orders = tuple(permutations(range(width)))
    result = set(orders)
    for table in bound_tables:
        for vertex in vertices:
            rows = {
                order: ordering_cost(order, table, vertex)
                for order in orders
            }
            optimum = min(rows.values())
            result.intersection_update(
                order for order, value in rows.items()
                if value == optimum
            )
    return result


def test_robust_chain_matches_exhaustive_scenarios():
    tables = (
        (Q(0), Q(0), Q(1), Q(1), Q(0), Q(1), Q(1), Q(2)),
        (Q(0), Q(1), Q(0), Q(1), Q(0), Q(1), Q(2), Q(2)),
    )
    vertices = (
        (Q(1, 2), Q(1, 3), Q(1, 6)),
        (Q(1, 6), Q(1, 3), Q(1, 2)),
    )
    exact = exhaustive_common(tables, vertices)
    certificate = robust_chain_certificate(tables, vertices)
    assert certificate.robust_optimizer_count == len(exact)
    assert certificate.robust_optimizer_exists == bool(exact)
    if exact:
        assert certificate.lexicographic_robust_order == min(exact)


def test_vertex_pass_implies_every_registered_convex_combination():
    bounds = (Q(0), Q(0), Q(1), Q(1))
    ordering = (0, 1)
    region = ordering_weight_region(ordering, (bounds,))
    vertices = (
        (Q(3, 4), Q(1, 4)),
        (Q(2, 3), Q(1, 3)),
    )
    assert all(weight_region_contains(region, row) for row in vertices)
    for numerator in range(11):
        coefficient = Q(numerator, 10)
        point = tuple(
            coefficient * vertices[0][index]
            + (1 - coefficient) * vertices[1][index]
            for index in range(2)
        )
        assert weight_region_contains(region, point)


def test_minimal_reference_switch_has_no_robust_order():
    witness = minimal_reference_switch_witness()
    assert witness["bounds"] == (Q(0), Q(0), Q(0), Q(1))
    assert witness["robust_optimizer_count"] == 0
    assert witness["boundary"]
    assert witness["minimax_regret"] == Q(1, 2)
    assert witness["minimax_optimizer_count"] == 2


def test_switch_witness_is_a_valid_buehler_table():
    # One parameter with risk one, row (1/2,1/2), alpha=3/5.
    # Neither singleton exceeds alpha; the full set does.
    probabilities = (Q(1, 2), Q(1, 2))
    alpha = Q(3, 5)
    table = []
    for mask in range(4):
        mass = sum(
            probabilities[index]
            for index in range(2)
            if mask & (1 << index)
        )
        table.append(Q(1) if mass > alpha else Q(0))
    assert tuple(table) == (Q(0), Q(0), Q(0), Q(1))


def test_weight_regions_split_at_the_reference_simplex_midpoint():
    bounds = (Q(0), Q(0), Q(0), Q(1))
    first = ordering_weight_region((0, 1), (bounds,))
    second = ordering_weight_region((1, 0), (bounds,))
    assert weight_region_contains(first, (Q(3, 4), Q(1, 4)))
    assert not weight_region_contains(second, (Q(3, 4), Q(1, 4)))
    assert weight_region_contains(second, (Q(1, 4), Q(3, 4)))
    assert not weight_region_contains(first, (Q(1, 4), Q(3, 4)))
    assert weight_region_contains(first, (Q(1, 2), Q(1, 2)))
    assert weight_region_contains(second, (Q(1, 2), Q(1, 2)))


def test_minimax_regret_zero_iff_robust_chain_exists_on_small_fixture():
    tables = (
        (Q(0), Q(0), Q(1), Q(1)),
        (Q(0), Q(0), Q(2), Q(2)),
    )
    vertices = (
        (Q(3, 4), Q(1, 4)),
        (Q(2, 3), Q(1, 3)),
    )
    robust = robust_chain_certificate(tables, vertices)
    regret = minimax_regret_certificate(tables, vertices)
    assert robust.robust_optimizer_exists
    assert regret.optimum == 0


def test_v048_common_count_recovered_for_singleton_reference_family():
    subset = json.loads(
        (
            V048
            / "artifacts_v0_48"
            / "subset_bounds_v0_48.json"
        ).read_text(encoding="utf-8")
    )
    result = json.loads(
        (
            V048
            / "artifacts_v0_48"
            / "result_v0_48.json"
        ).read_text(encoding="utf-8")
    )
    weights = tuple(
        Q(value)
        for value in result["scientific"]["primary"][
            "reference_weights"
        ]
    )
    certificate = robust_chain_certificate(
        (
            tuple(Q(value) for value in subset["classification"]),
            tuple(Q(value) for value in subset["root_group"]),
        ),
        (weights,),
    )
    assert certificate.robust_optimizer_count == 1_451_520
    assert certificate.robust_optimizer_exists


def test_reference_vertices_must_stay_inside_positive_simplex():
    bounds = ((Q(0), Q(0), Q(0), Q(1)),)
    with pytest.raises(ValueError, match="strictly positive"):
        robust_chain_certificate(bounds, ((Q(1), Q(0)),))
    with pytest.raises(ValueError, match="sum to one"):
        robust_chain_certificate(bounds, ((Q(2, 3), Q(2, 3)),))
