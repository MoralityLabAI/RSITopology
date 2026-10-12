"""Development tests for the ASMP-9 v0.24 marginal reduction."""

from __future__ import annotations

from fractions import Fraction

import pytest

from marginal_oracle import (
    availability_polynomial_from_marginal_oracle,
    availability_polynomial_from_uniform_ratios,
    exact_availability,
    floor_availability_from_polynomial,
    one_edge_marginal_ratio,
    polynomial_evaluate,
    telescoped_uniform_ratio,
    uniform_ratio_sequence,
)


GRAPH_CELLS = (
    (
        "triangle",
        3,
        ((0, 1), (1, 2), (0, 2)),
    ),
    (
        "diamond",
        4,
        ((0, 1), (1, 2), (2, 0), (0, 3), (3, 2)),
    ),
    (
        "k4",
        4,
        ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)),
    ),
)


@pytest.mark.parametrize("_name,node_count,edges", GRAPH_CELLS)
def test_uniform_ratios_recover_floor_and_out_of_grid_value(
    _name: str, node_count: int, edges: tuple[tuple[int, int], ...]
) -> None:
    ratios = uniform_ratio_sequence(node_count, edges)
    polynomial = availability_polynomial_from_uniform_ratios(ratios)

    assert len(polynomial) == len(edges) + 1
    assert polynomial[0] == 1
    assert floor_availability_from_polynomial(polynomial) == (
        exact_availability(node_count, edges, (1,) * len(edges))
    )

    held_out_count = len(edges) + 2
    held_out_point = Fraction(1, 2**held_out_count)
    assert polynomial_evaluate(polynomial, held_out_point) == (
        exact_availability(
            node_count, edges, (held_out_count,) * len(edges)
        )
    )


@pytest.mark.parametrize("_name,node_count,edges", GRAPH_CELLS)
def test_local_marginals_telescope_to_uniform_ratios(
    _name: str, node_count: int, edges: tuple[tuple[int, int], ...]
) -> None:
    direct = uniform_ratio_sequence(node_count, edges)
    telescoped = tuple(
        telescoped_uniform_ratio(node_count, edges, trial_count)
        for trial_count in range(1, len(edges) + 1)
    )
    assert telescoped == direct


@pytest.mark.parametrize("_name,node_count,edges", GRAPH_CELLS)
def test_m_squared_local_calls_recover_full_curve(
    _name: str, node_count: int, edges: tuple[tuple[int, int], ...]
) -> None:
    calls: list[tuple[tuple[int, ...], int]] = []

    def oracle(counts: tuple[int, ...], edge_index: int) -> Fraction:
        calls.append((tuple(counts), edge_index))
        return one_edge_marginal_ratio(
            node_count, edges, counts, edge_index
        )

    polynomial = availability_polynomial_from_marginal_oracle(
        node_count, edges, oracle
    )
    assert len(calls) == len(edges) ** 2
    assert floor_availability_from_polynomial(polynomial) == (
        exact_availability(node_count, edges, (1,) * len(edges))
    )


def test_rejects_nonpositive_ratio() -> None:
    with pytest.raises(ValueError, match="positive"):
        availability_polynomial_from_uniform_ratios((Fraction(0),))

