from fractions import Fraction

from block_factorization import (
    PreparedGraph,
    all_statuses,
    availability,
    biconnected_edge_blocks,
    block_product_availability,
    blockwise_available,
    direct_available,
)


TWO_DIAMONDS = (
    (0, 1),
    (1, 2),
    (2, 0),
    (0, 3),
    (3, 2),
    (0, 4),
    (4, 5),
    (5, 0),
    (0, 6),
    (6, 5),
)

CENTRAL_CYCLE_WITH_TWO_ATTACHMENTS = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (0, 4),
    (4, 5),
    (5, 0),
    (2, 6),
    (6, 7),
    (7, 2),
)

TWO_CYCLES_WITH_BRIDGE = (
    (0, 1),
    (1, 2),
    (2, 0),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 3),
)

THETA = (
    (0, 2),
    (2, 1),
    (0, 3),
    (3, 1),
    (0, 4),
    (4, 1),
)


def test_two_diamond_blocks_are_exact() -> None:
    assert biconnected_edge_blocks(7, TWO_DIAMONDS) == (
        (0, 1, 2, 3, 4),
        (5, 6, 7, 8, 9),
    )


def test_exhaustive_status_equivalence_on_two_diamonds() -> None:
    prepared = PreparedGraph.build(7, TWO_DIAMONDS)
    for statuses in all_statuses(len(TWO_DIAMONDS)):
        assert prepared.direct_available(
            statuses
        ) == prepared.blockwise_available(statuses)


def test_exact_probability_factorization() -> None:
    counts = (1, 2, 3, 2, 1, 2, 1, 3, 2, 1)
    epsilon = Fraction(3, 11)
    labels = (0, 1, 0, 1, 1, 0, 0, 1, 0, 1)
    probabilities = tuple(
        epsilon if label == 0 else 1 - epsilon for label in labels
    )
    direct = availability(
        7,
        TWO_DIAMONDS,
        counts,
        probabilities,
        blockwise=False,
    )
    decomposed = block_product_availability(
        7, TWO_DIAMONDS, counts, probabilities
    )
    assert direct == decomposed


def test_bridge_is_a_singleton_block_and_irrelevant() -> None:
    triangle_bridge = ((0, 1), (1, 2), (2, 0), (0, 3))
    assert biconnected_edge_blocks(4, triangle_bridge) == (
        (0, 1, 2),
        (3,),
    )
    for statuses in all_statuses(4):
        assert direct_available(
            4, triangle_bridge, statuses
        ) == blockwise_available(4, triangle_bridge, statuses)


def test_multiple_articulation_vertices_cannot_supply_a_shortcut() -> None:
    assert biconnected_edge_blocks(
        8, CENTRAL_CYCLE_WITH_TWO_ATTACHMENTS
    ) == (
        (0, 1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
    )
    prepared = PreparedGraph.build(
        8, CENTRAL_CYCLE_WITH_TWO_ATTACHMENTS
    )
    for statuses in all_statuses(
        len(CENTRAL_CYCLE_WITH_TWO_ATTACHMENTS)
    ):
        assert prepared.direct_available(
            statuses
        ) == prepared.blockwise_available(statuses)


def test_bridge_between_cyclic_components_never_changes_liveness() -> None:
    assert biconnected_edge_blocks(6, TWO_CYCLES_WITH_BRIDGE) == (
        (0, 1, 2),
        (3,),
        (4, 5, 6),
    )
    prepared = PreparedGraph.build(6, TWO_CYCLES_WITH_BRIDGE)
    by_nonbridge_status: dict[tuple[int, ...], bool] = {}
    for statuses in all_statuses(len(TWO_CYCLES_WITH_BRIDGE)):
        direct = prepared.direct_available(statuses)
        assert direct == prepared.blockwise_available(statuses)
        nonbridge_status = statuses[:3] + statuses[4:]
        previous = by_nonbridge_status.setdefault(
            nonbridge_status, direct
        )
        assert previous == direct


def test_one_overlapping_cycle_block_gets_no_false_decomposition() -> None:
    assert biconnected_edge_blocks(5, THETA) == (
        tuple(range(len(THETA))),
    )
