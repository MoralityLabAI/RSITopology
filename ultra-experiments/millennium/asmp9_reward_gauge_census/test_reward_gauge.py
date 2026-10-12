from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import run


HERE = Path(__file__).resolve().parent
PROTOCOL = json.loads((HERE / "protocol_v0_1.json").read_text(encoding="utf-8"))


def test_tree_has_no_cycle_queries() -> None:
    record = run.analyze_graph(4, ((0, 1), (1, 2), (2, 3)))
    assert record["components"] == 1
    assert record["beta_1"] == 0
    assert record["cycle_rows"] == 0
    assert record["full_kernel_dimension"] == record["shaping_dimension"] == 3


def test_triangle_cycle_annihilates_shaping() -> None:
    edges = ((0, 1), (0, 2), (1, 2))
    forest, components = run.spanning_forest(3, edges)
    incidence = run.incidence_matrix(3, edges)
    cycles = run.fundamental_cycle_matrix(3, edges, forest)
    assert components == 1
    assert cycles.shape == (1, 3)
    assert np.all(incidence @ cycles.T == 0)
    assert np.all(cycles @ incidence.T == 0)


def test_square_with_diagonal_has_two_independent_chords() -> None:
    edges = ((0, 1), (0, 3), (1, 2), (1, 3), (2, 3))
    forest, components = run.spanning_forest(4, edges)
    cycles = run.fundamental_cycle_matrix(4, edges, forest)
    incidence = run.incidence_matrix(4, edges)
    assert components == 1
    assert cycles.shape == (2, 5)
    assert np.all(incidence @ cycles.T == 0)


def test_ordinal_counterexample_is_live() -> None:
    record = run.ordinal_counterexample()
    assert record["pass"]
    assert record["same_ordinal_observation"]
    assert record["non_gauge_equivalent"]


def test_small_graph_universe_cardinality_without_full_outcome() -> None:
    observed = sum(1 << len(run.edge_universe(n)) for n in range(2, 5))
    assert observed == 74
