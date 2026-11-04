from __future__ import annotations

import pytest

from experiment import (
    cycle_graph,
    graph_metadata,
    named_graphs,
    run_floor_control,
    run_forest_control,
    run_graph_cells,
)


@pytest.mark.parametrize("length", (3, 4, 6, 8))
def test_cycle_metadata(length: int) -> None:
    vertex_count, edges = cycle_graph(length)
    metadata = graph_metadata(vertex_count, edges)
    assert metadata["beta_1"] == 1
    assert metadata["cycle_lengths"] == [length]


def test_named_multicycle_graphs_have_expected_beta() -> None:
    graphs = named_graphs()
    assert graph_metadata(*graphs["theta_4"])["beta_1"] == 2
    assert graph_metadata(*graphs["complete_5"])["beta_1"] == 6


def test_small_graph_cell_preserves_mirror_and_theorem() -> None:
    vertex_count, edges = cycle_graph(3)
    result = run_graph_cells(
        graph_name="test",
        vertex_count=vertex_count,
        edges=edges,
        seed=1,
        replicates=32,
        multipliers=(1.0,),
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
        planted_circulation=1.2,
    )
    cell = result["cells"][0]
    assert cell["mirror_status_match"]
    assert not any(cell["unsafe_on_event_counts"].values())


def test_forest_control_never_passes_vacuously() -> None:
    result = run_forest_control(
        replicates=32,
        samples_per_edge=1000,
        seed=2,
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
    )
    assert result["status_counts"] == {"unavailable_no_cycles": 32}


def test_floor_control_is_unavailable_on_simultaneous_event() -> None:
    result = run_floor_control(
        replicates=32,
        samples_per_edge=10000,
        seed=3,
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
    )
    assert result["nonunavailable_on_event"] == 0
