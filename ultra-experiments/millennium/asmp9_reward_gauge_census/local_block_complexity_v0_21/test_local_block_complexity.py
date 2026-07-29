import itertools
from fractions import Fraction

import pytest

from local_block_complexity import (
    asmp_count_floor_availability,
    asmp_count_floor_numerator,
    biconnected_edge_blocks,
    count_floor_allocation,
    count_totally_cyclic_orientations,
    tutte_02_block_product,
    tutte_02_deletion_contraction,
)


TRIANGLE = ((0, 1), (1, 2), (2, 0))
DIAMOND = ((0, 1), (1, 2), (2, 0), (0, 3), (3, 2))
THETA = (
    (0, 2),
    (2, 1),
    (0, 3),
    (3, 1),
    (0, 4),
    (4, 1),
)
K4 = tuple(itertools.combinations(range(4), 2))


def test_classical_counts_on_burned_graphs() -> None:
    assert tutte_02_deletion_contraction(3, TRIANGLE) == 2
    assert count_totally_cyclic_orientations(3, TRIANGLE) == 2
    assert tutte_02_deletion_contraction(4, K4) == 24


@pytest.mark.parametrize(
    ("node_count", "edges"),
    [(3, TRIANGLE), (4, DIAMOND), (5, THETA), (4, K4)],
)
def test_three_boundary_evaluators_agree_on_burned_blocks(
    node_count: int, edges: tuple[tuple[int, int], ...]
) -> None:
    tutte = tutte_02_deletion_contraction(node_count, edges)
    exhaustive = count_totally_cyclic_orientations(node_count, edges)
    asmp = asmp_count_floor_numerator(node_count, edges)
    assert tutte == exhaustive == asmp
    assert asmp_count_floor_availability(
        node_count, edges
    ) == Fraction(asmp, 2 ** len(edges))


def test_all_simple_graphs_on_five_vertices() -> None:
    universe = tuple(itertools.combinations(range(5), 2))
    for mask in range(1 << len(universe)):
        edges = tuple(
            edge
            for index, edge in enumerate(universe)
            if mask & (1 << index)
        )
        assert tutte_02_deletion_contraction(
            5, edges
        ) == count_totally_cyclic_orientations(5, edges)


def test_bridge_distinction_is_explicit() -> None:
    triangle_with_leaf = TRIANGLE + ((0, 3),)
    assert tutte_02_deletion_contraction(4, triangle_with_leaf) == 0
    assert count_totally_cyclic_orientations(
        4, triangle_with_leaf
    ) == 0
    # ASMP quotient liveness ignores the original bridge.  The bridge has two
    # free orientations, so four of the sixteen total orientations survive.
    assert asmp_count_floor_numerator(4, triangle_with_leaf) == 4
    assert asmp_count_floor_availability(
        4, triangle_with_leaf
    ).numerator == 1
    assert asmp_count_floor_availability(
        4, triangle_with_leaf
    ).denominator == 4


def test_block_product_on_burned_one_point_union() -> None:
    two_triangles = TRIANGLE + ((0, 3), (3, 4), (4, 0))
    assert biconnected_edge_blocks(5, two_triangles) == (
        (0, 1, 2),
        (3, 4, 5),
    )
    assert tutte_02_deletion_contraction(5, two_triangles) == 4
    assert tutte_02_block_product(5, two_triangles) == 4


def test_count_floor_is_the_only_unique_positive_allocation() -> None:
    assert count_floor_allocation(6, 6) == (1, 1, 1, 1, 1, 1)
    with pytest.raises(ValueError, match="infeasible"):
        count_floor_allocation(6, 5)
    with pytest.raises(ValueError, match="not unique"):
        count_floor_allocation(6, 7)
