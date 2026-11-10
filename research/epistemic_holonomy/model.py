"""Finite graph/Hodge and evidence-provenance synthetic controls.

Graph vertices are *authenticated independent-information states*. An echo
returns to the same state and is represented by a self-loop. The edge weight
is the log-odds increment asserted by a potentially naive inference engine.
Cycle integrals thus detect inconsistency *relative to this marked quotient*.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb, isfinite, log, log2
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class DirectedEdge:
    source: str
    target: str
    log_increment: float
    evidence_id: str


def incidence(nodes: Sequence[str], edges: Sequence[DirectedEdge]) -> np.ndarray:
    if not nodes or len(set(nodes)) != len(nodes):
        raise ValueError("nodes must be nonempty and unique")
    index = {node: k for k, node in enumerate(nodes)}
    B = np.zeros((len(nodes), len(edges)), dtype=float)
    for j, edge in enumerate(edges):
        if edge.source not in index or edge.target not in index:
            raise ValueError("edge endpoint missing from nodes")
        if not isfinite(edge.log_increment):
            raise ValueError("log increments must be finite")
        B[index[edge.source], j] -= 1.0
        B[index[edge.target], j] += 1.0
    return B


def _cycles(nodes: Sequence[str], edges: Sequence[DirectedEdge]) -> tuple[int, list[np.ndarray]]:
    """Deterministic oriented fundamental cycles of a spanning forest."""
    parent = {name: name for name in nodes}
    adjacency: dict[str, list[tuple[str, int, int]]] = {name: [] for name in nodes}

    def find(a: str) -> str:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    non_tree: list[int] = []
    for j, e in enumerate(edges):
        a, b = find(e.source), find(e.target)
        if a == b:
            non_tree.append(j)
        else:
            parent[a] = b
            adjacency[e.source].append((e.target, j, 1))
            adjacency[e.target].append((e.source, j, -1))

    cycles = []
    for j in non_tree:
        edge = edges[j]
        c = np.zeros(len(edges), dtype=float)
        c[j] = 1.0
        # Close the non-tree arc u->v with the tree path v->u.
        start, goal = edge.target, edge.source
        queue = [start]
        visited: dict[str, tuple[str, int, int] | None] = {start: None}
        for node in queue:
            if node == goal:
                break
            for neighbor, k, sign in adjacency[node]:
                if neighbor not in visited:
                    visited[neighbor] = (node, k, sign)
                    queue.append(neighbor)
        if goal not in visited:
            raise AssertionError("forest path missing for cycle")
        current = goal
        while current != start:
            step = visited[current]
            if step is None:
                raise AssertionError("unexpected root")
            predecessor, k, sign = step
            c[k] += sign
            current = predecessor
        cycles.append(c)
    components = len({find(n) for n in nodes})
    assert len(cycles) == len(edges) - len(nodes) + components
    return components, cycles


def hodge_receipt(nodes: Sequence[str], edges: Sequence[DirectedEdge]) -> dict:
    """Project edge cochain onto exact and divergence-free cycle subspaces.

    Least squares fixes the potential only up to a constant on each connected
    component; the gradient, harmonic residual, and cycle integrals are unique.
    """
    B = incidence(nodes, edges)
    w = np.array([edge.log_increment for edge in edges], dtype=float)
    phi = np.linalg.lstsq(B.T, w, rcond=None)[0]
    exact = B.T @ phi
    h = w - exact
    components, cycles = _cycles(nodes, edges)
    cycle_integrals = [float(c @ w) for c in cycles]
    scale = max(1.0, float(np.linalg.norm(w)))
    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "components": components,
        "cycle_rank": len(cycles),
        "cycle_integrals": cycle_integrals,
        "max_abs_cycle_integral": max((abs(x) for x in cycle_integrals), default=0.0),
        "hodge_cycle_l2": float(np.linalg.norm(h)),
        "divergence_linf": float(np.max(np.abs(B @ h))) if len(nodes) else 0.0,
        "is_flat": bool(np.linalg.norm(h) <= 1e-10 * scale),
        "edge_residuals": h.tolist(),
        "edge_exact_increments": exact.tolist(),
    }


def echo_graph(total_signals: int, reliability: float) -> tuple[list[str], list[DirectedEdge]]:
    ell = _log_likelihood_ratio(reliability)
    if total_signals < 1:
        raise ValueError("total_signals must be positive")
    nodes = ["prior", "authenticated-x"]
    edges = [DirectedEdge("prior", "authenticated-x", ell, "original-x")]
    edges += [
        DirectedEdge("authenticated-x", "authenticated-x", ell, "original-x")
        for _ in range(total_signals - 1)
    ]
    return nodes, edges


def corrected_echo_graph(total_signals: int, reliability: float) -> tuple[list[str], list[DirectedEdge]]:
    """Same graph topology as echo_graph; proper duplicate updates carry zero weight."""
    nodes, edges = echo_graph(total_signals, reliability)
    return nodes, [edges[0]] + [
        DirectedEdge(e.source, e.target, 0.0, e.evidence_id) for e in edges[1:]
    ]


def fresh_graph(total_signals: int, reliability: float) -> tuple[list[str], list[DirectedEdge]]:
    ell = _log_likelihood_ratio(reliability)
    if total_signals < 1:
        raise ValueError("total_signals must be positive")
    nodes = [f"observed-{i}" for i in range(total_signals + 1)]
    edges = [
        DirectedEdge(nodes[i], nodes[i + 1], ell, f"independent-{i}")
        for i in range(total_signals)
    ]
    return nodes, edges


def _log_likelihood_ratio(reliability: float) -> float:
    if not 0.5 < reliability < 1.0:
        raise ValueError("reliability must lie strictly between 0.5 and 1")
    return log(reliability / (1.0 - reliability))


def _sigmoid(z: float | np.ndarray) -> float | np.ndarray:
    return np.exp(-np.logaddexp(0.0, -z))


def echo_metrics(total_signals: int, reliability: float = 0.6) -> dict:
    """Exact population metrics for one binary signal echoed N-1 times.

    H is equiprobable, the authentic binary observation X equals H with
    probability reliability, and each echo is a deterministic copy of X.
    The naive observer counts all N copies as conditionally independent.
    """
    nodes, edges = echo_graph(total_signals, reliability)
    ell = _log_likelihood_ratio(reliability)
    z = total_signals * ell
    q = float(_sigmoid(z))
    return {
        "condition": "echo",
        "total_signals": total_signals,
        "distinct_sources": 1,
        "reported_confidence": q,
        "actual_prediction_accuracy": reliability,
        "absolute_calibration_gap": q - reliability,
        "expected_log_loss_nats": float(
            reliability * np.logaddexp(0.0, -z)
            + (1.0 - reliability) * np.logaddexp(0.0, z)
        ),
        "expected_brier": reliability * (1.0 - q) ** 2 + (1.0 - reliability) * q**2,
        "mutual_information_bits": 1.0 + reliability * log2(reliability)
        + (1.0 - reliability) * log2(1.0 - reliability),
        "log_odds_cycle_total": (total_signals - 1) * ell,
        "hodge": hodge_receipt(nodes, edges),
    }


def fresh_metrics(total_signals: int, reliability: float = 0.6) -> dict:
    """Exact population metrics for N genuinely conditionally independent signals."""
    nodes, edges = fresh_graph(total_signals, reliability)
    ell = _log_likelihood_ratio(reliability)
    logloss = brier = accuracy = 0.0
    for k in range(total_signals + 1):
        prob = comb(total_signals, k) * reliability**k * (1.0 - reliability) ** (total_signals - k)
        z = (2 * k - total_signals) * ell
        q = float(_sigmoid(z))
        logloss += prob * float(np.logaddexp(0.0, -z))
        brier += prob * (1.0 - q) ** 2
        accuracy += prob * (1.0 if z > 0 else 0.5 if z == 0 else 0.0)
    return {
        "condition": "independent",
        "total_signals": total_signals,
        "distinct_sources": total_signals,
        "actual_prediction_accuracy": accuracy,
        "expected_log_loss_nats": logloss,
        "expected_brier": brier,
        "population_calibration_gap": 0.0,  # correct generative model
        "hodge": hodge_receipt(nodes, edges),
    }


def paired_trial(total_signals: int, reliability: float = 0.6, *, seed: int = 11, trials: int = 20000) -> dict:
    """Paired seeded simulation; share original signal, resample fresh successors."""
    if trials < 1:
        raise ValueError("trials must be positive")
    ell = _log_likelihood_ratio(reliability)
    if total_signals < 1:
        raise ValueError("total_signals must be positive")
    rng = np.random.default_rng(seed)
    truth = rng.integers(0, 2, size=trials)
    correct = rng.random(trials) < reliability
    original = np.where(correct, truth, 1 - truth)
    additional_correct = rng.random((trials, total_signals - 1)) < reliability
    fresh_sum = (2 * original - 1) + np.sum(
        np.where(additional_correct, 2 * truth[:, None] - 1, 1 - 2 * truth[:, None]), axis=1
    )
    values = {}
    for label, z in (
        ("echo", total_signals * ell * (2 * original - 1)),
        ("independent", ell * fresh_sum),
    ):
        signed_z = np.where(truth == 1, z, -z)
        probability = _sigmoid(z)
        values[label] = {
            "accuracy": float(np.mean(np.where(signed_z > 0, 1.0, np.where(signed_z < 0, 0.0, 0.5)))),
            "log_loss_nats": float(np.mean(np.logaddexp(0.0, -signed_z))),
            "brier": float(np.mean((probability - truth) ** 2)),
        }
    return {"seed": seed, "trials": trials, "total_signals": total_signals, "results": values}
