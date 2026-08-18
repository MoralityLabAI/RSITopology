from __future__ import annotations

from fractions import Fraction
from itertools import combinations

import pytest

from context_gluing import (
    ContextGraph,
    cycle_circulations,
    fundamental_cycle_basis,
    global_flow,
    has_shared_scalar,
    is_locally_scalar,
    local_flow,
    minimal_parallel_edge_witness,
    minimum_mixed_checks,
    matrix_rank,
    mixed_cycle_basis,
    non_gluing_witness,
    obstruction_dimensions,
    shared_scalar_status,
    incidence_matrix,
)


def test_two_items_two_contexts_is_minimal_non_gluing_witness() -> None:
    witness = minimal_parallel_edge_witness()
    assert witness["locally_scalar"]
    assert not witness["shared_scalar"]
    assert witness["dimensions"]["mixed_cycle_rank"] == 1
    cycles = mixed_cycle_basis(witness["item_count"], witness["contexts"])
    assert len(cycles) == 1
    assert cycle_circulations(witness["flow"], cycles) in {
        (Fraction(1),),
        (Fraction(-1),),
    }
    assert (
        shared_scalar_status(
            witness["item_count"], witness["contexts"], witness["flow"]
        )["status"]
        == "shared_scalar_refuted"
    )


def test_one_context_has_no_mixed_obstruction() -> None:
    contexts = (ContextGraph("c0", ((0, 1), (1, 2), (0, 2))),)
    dimensions = obstruction_dimensions(3, contexts)
    assert dimensions["local_cycle_rank"] == 1
    assert dimensions["union_cycle_rank"] == 1
    assert dimensions["mixed_cycle_rank"] == 0
    assert non_gluing_witness(3, contexts) is None
    flow = global_flow(3, contexts, (0, 1, 2))
    assert (
        shared_scalar_status(3, contexts, flow)["status"]
        == "shared_scalar_forced_by_design"
    )


def test_two_context_trees_can_form_one_mixed_cycle() -> None:
    contexts = (
        ContextGraph("c0", ((0, 1), (1, 2))),
        ContextGraph("c1", ((0, 2),)),
    )
    dimensions = obstruction_dimensions(3, contexts)
    assert dimensions["local_cycle_rank"] == 0
    assert dimensions["union_cycle_rank"] == 1
    assert dimensions["mixed_cycle_rank"] == 1
    witness = non_gluing_witness(3, contexts)
    assert witness is not None
    assert is_locally_scalar(3, contexts, witness)
    assert not has_shared_scalar(3, contexts, witness)


def test_global_utility_always_glues() -> None:
    contexts = (
        ContextGraph("c0", ((0, 1), (1, 2))),
        ContextGraph("c1", ((0, 2), (2, 3))),
    )
    flow = global_flow(4, contexts, (0, 1, -2, 4))
    assert is_locally_scalar(4, contexts, flow)
    assert has_shared_scalar(4, contexts, flow)
    assert shared_scalar_status(4, contexts, flow)["status"] == "shared_scalar_verified"


def test_context_local_utility_can_fail_to_glue() -> None:
    contexts = (
        ContextGraph("c0", ((0, 1),)),
        ContextGraph("c1", ((0, 1),)),
    )
    flow = local_flow(2, contexts, ((0, 1), (0, 2)))
    assert flow == (Fraction(1), Fraction(2))
    assert is_locally_scalar(2, contexts, flow)
    assert not has_shared_scalar(2, contexts, flow)


def test_local_cycle_failure_precedes_gluing_decision() -> None:
    contexts = (ContextGraph("c0", ((0, 1), (1, 2), (0, 2))),)
    inconsistent = (Fraction(1), Fraction(1), Fraction(1))
    assert not is_locally_scalar(3, contexts, inconsistent)
    assert (
        shared_scalar_status(3, contexts, inconsistent)["status"]
        == "local_scalar_failed"
    )


@pytest.mark.parametrize("item_count", (2, 3, 4))
def test_rank_and_cycle_formulas_match_all_two_context_graph_pairs(
    item_count: int,
) -> None:
    universe = tuple(combinations(range(item_count), 2))
    graphs = [
        tuple(edge for index, edge in enumerate(universe) if mask & (1 << index))
        for mask in range(1 << len(universe))
    ]
    for left in graphs:
        for right in graphs:
            contexts = (
                ContextGraph("left", left),
                ContextGraph("right", right),
            )
            dimensions = obstruction_dimensions(item_count, contexts)
            assert dimensions["rank_difference"] == dimensions["mixed_cycle_rank"]
            assert minimum_mixed_checks(item_count, contexts) >= 0
            assert (
                len(mixed_cycle_basis(item_count, contexts))
                == (dimensions["mixed_cycle_rank"])
            )
            witness = non_gluing_witness(item_count, contexts)
            assert (witness is not None) == (dimensions["mixed_cycle_rank"] > 0)


def test_invalid_duplicate_context_name_rejected() -> None:
    contexts = (
        ContextGraph("same", ((0, 1),)),
        ContextGraph("same", ((0, 1),)),
    )
    with pytest.raises(ValueError, match="names"):
        obstruction_dimensions(2, contexts)


@pytest.mark.parametrize("item_count", (2, 3, 4))
def test_fundamental_cycles_are_independent_incidence_null_vectors(
    item_count: int,
) -> None:
    universe = tuple(combinations(range(item_count), 2))
    for mask in range(1 << len(universe)):
        edges = tuple(
            edge for index, edge in enumerate(universe) if mask & (1 << index)
        )
        cycles = fundamental_cycle_basis(item_count, edges)
        assert matrix_rank(cycles) == len(cycles)
        incidence = incidence_matrix(item_count, edges)
        for cycle in cycles:
            boundary = tuple(
                sum(cycle[edge] * incidence[edge][item] for edge in range(len(edges)))
                for item in range(item_count)
            )
            assert all(value == 0 for value in boundary)


def test_cycle_flow_dimension_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="dimensions"):
        cycle_circulations((1, 2), ((1,),))
