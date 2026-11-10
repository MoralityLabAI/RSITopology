"""Analytic and synthetic checks for EH-01."""

from math import isclose, log

import numpy as np
import pytest

from research.epistemic_holonomy.model import (
    DirectedEdge,
    echo_graph,
    corrected_echo_graph,
    echo_metrics,
    fresh_metrics,
    hodge_receipt,
    incidence,
    paired_trial,
)


def test_gradient_is_flat_and_cycle_basis_is_complete():
    nodes = ["a", "b", "c", "d"]
    edges = [
        DirectedEdge("a", "b", 0, "ab"),
        DirectedEdge("b", "c", 0, "bc"),
        DirectedEdge("a", "c", 0, "ac"),
        DirectedEdge("c", "d", 0, "cd"),
        DirectedEdge("d", "a", 0, "da"),
    ]
    B = incidence(nodes, edges)
    phi = np.array([2.0, 3.0, -1.0, 4.0])
    w = B.T @ phi
    weighted = [DirectedEdge(e.source, e.target, float(w[j]), e.evidence_id) for j, e in enumerate(edges)]
    result = hodge_receipt(nodes, weighted)
    assert result["cycle_rank"] == 2
    assert result["is_flat"]
    assert result["hodge_cycle_l2"] < 1e-12
    assert result["max_abs_cycle_integral"] < 1e-12


def test_nonflat_triangle_gauge_invariance():
    nodes = ["a", "b", "c"]
    edges = [
        DirectedEdge("a", "b", 1.0, "ab"),
        DirectedEdge("b", "c", 1.0, "bc"),
        DirectedEdge("a", "c", 1.0, "ac"),
    ]
    original = hodge_receipt(nodes, edges)
    B = incidence(nodes, edges)
    potential = np.array([1.0, -3.0, 5.0])
    shifted = B.T @ potential
    gauged = [DirectedEdge(e.source, e.target, e.log_increment + shifted[j], e.evidence_id) for j, e in enumerate(edges)]
    transformed = hodge_receipt(nodes, gauged)
    assert original["cycle_rank"] == 1
    assert not original["is_flat"]
    assert original["cycle_integrals"] == pytest.approx([-1.0])
    assert transformed["cycle_integrals"] == pytest.approx(original["cycle_integrals"])
    assert transformed["edge_residuals"] == pytest.approx(original["edge_residuals"])
    assert original["divergence_linf"] < 1e-12


def test_disconnected_self_loops_and_parallel_edges():
    nodes = ["a", "b", "c"]
    edges = [
        DirectedEdge("a", "a", 0.5, "echo"),
        DirectedEdge("b", "c", 0.1, "fresh"),
        DirectedEdge("b", "c", 0.2, "second"),
    ]
    receipt = hodge_receipt(nodes, edges)
    assert receipt["components"] == 2
    assert receipt["cycle_rank"] == 2
    assert sorted(abs(x) for x in receipt["cycle_integrals"]) == pytest.approx([0.1, 0.5])


def test_echo_calibration_information_and_cycle_count():
    one = echo_metrics(1)
    ten = echo_metrics(10)
    assert ten["reported_confidence"] == pytest.approx(0.982954072, abs=1e-9)
    assert ten["actual_prediction_accuracy"] == 0.6
    assert ten["distinct_sources"] == 1
    assert ten["mutual_information_bits"] == pytest.approx(one["mutual_information_bits"])
    assert ten["mutual_information_bits"] == pytest.approx(0.0290494055, abs=1e-9)
    assert ten["log_odds_cycle_total"] == pytest.approx(9 * log(1.5))
    assert ten["hodge"]["cycle_rank"] == 9
    assert ten["hodge"]["max_abs_cycle_integral"] == pytest.approx(log(1.5))
    assert ten["expected_log_loss_nats"] > one["expected_log_loss_nats"]


def test_fresh_chain_is_flat_and_improves_prediction():
    echo = echo_metrics(10)
    independent = fresh_metrics(10)
    assert independent["hodge"]["is_flat"]
    assert independent["hodge"]["cycle_rank"] == 0
    assert independent["distinct_sources"] == 10
    assert independent["expected_log_loss_nats"] < echo["expected_log_loss_nats"]
    assert independent["expected_brier"] < echo["expected_brier"]


def test_seeded_replay_matches_exact_averages():
    trial = paired_trial(10, seed=11, trials=50000)["results"]
    assert trial["echo"]["accuracy"] == pytest.approx(0.6, abs=0.01)
    assert trial["echo"]["log_loss_nats"] == pytest.approx(echo_metrics(10)["expected_log_loss_nats"], abs=0.04)
    assert trial["independent"]["log_loss_nats"] == pytest.approx(fresh_metrics(10)["expected_log_loss_nats"], abs=0.02)


def test_input_contracts_and_numerical_stability():
    with pytest.raises(ValueError):
        echo_graph(0, 0.6)
    with pytest.raises(ValueError):
        echo_metrics(2, 0.5)
    with pytest.raises(ValueError):
        hodge_receipt(["a", "a"], [])
    with pytest.raises(ValueError):
        hodge_receipt(["a"], [DirectedEdge("a", "b", 1.0, "x")])
    assert isclose(echo_metrics(256)["reported_confidence"], 1.0)
    assert np.isfinite(echo_metrics(256)["expected_log_loss_nats"])


def test_externally_opposite_worlds_are_indistinguishable():
    # Both worlds emit the same transcript law: P(T=0)=P(T=1)=1/2.
    for predictions in ((0, 0), (0, 1), (1, 0), (1, 1)):
        world0 = sum(0.5 * (predictions[t] == 0) for t in (0, 1))
        world1 = sum(0.5 * (predictions[t] == 1) for t in (0, 1))
        assert (world0 + world1) / 2 == 0.5


def test_matched_graph_provenance_correction():
    naive = hodge_receipt(*echo_graph(10, 0.6))
    corrected = hodge_receipt(*corrected_echo_graph(10, 0.6))
    assert naive["nodes"] == corrected["nodes"]
    assert naive["edges"] == corrected["edges"]
    assert naive["cycle_rank"] == corrected["cycle_rank"] == 9
    assert not naive["is_flat"]
    assert corrected["is_flat"]
    assert corrected["max_abs_cycle_integral"] == 0.0
