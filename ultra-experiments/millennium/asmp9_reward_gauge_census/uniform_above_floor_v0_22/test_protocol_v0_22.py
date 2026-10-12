import json
from fractions import Fraction
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent


def protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_22.json").read_text(encoding="utf-8")
    )


def graph(raw: dict) -> nx.Graph:
    result = nx.Graph()
    result.add_nodes_from(range(raw["node_count"]))
    result.add_edges_from(raw["edges"])
    return result


def test_gate_ids_are_unique_and_total() -> None:
    gates = protocol()["gate_ids"]
    assert len(gates) == 10
    assert len(gates) == len(set(gates))


def test_registered_graphs_are_pairwise_fresh_shaped_blocks() -> None:
    graphs = {
        name: graph(raw)
        for name, raw in protocol()["primary_graphs"].items()
    }
    for item in graphs.values():
        assert nx.is_connected(item)
        assert nx.is_biconnected(item)
        assert not list(nx.bridges(item))
        assert item.number_of_edges() > 9 or item.number_of_nodes() > 6
    names = sorted(graphs)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            assert not nx.is_isomorphic(graphs[left], graphs[right])


def test_registered_graphs_have_no_match_in_sealed_prior_registry() -> None:
    value = protocol()
    registry = json.loads(
        (HERE / value["freshness_rule"]["burned_registry_path"]).read_text(
            encoding="utf-8"
        )
    )
    prior = [
        graph(
            {
                "edges": record["edges"],
                "node_count": record["node_count"],
            }
        )
        for record in registry["records"]
    ]
    assert registry["graph_record_count"] == len(prior)
    for raw in value["primary_graphs"].values():
        candidate = graph(raw)
        assert not any(
            old.number_of_nodes() == candidate.number_of_nodes()
            and old.number_of_edges() == candidate.number_of_edges()
            and nx.is_isomorphic(old, candidate)
            for old in prior
        )


def test_trial_points_are_exactly_on_h_minus_one() -> None:
    for trial_count in protocol()["registered_trial_counts"]:
        z = Fraction(1, 2**trial_count)
        x_value = (1 - 2 * z) / (1 - z)
        y_value = 1 / z
        assert (x_value - 1) * (y_value - 1) == -1
    assert protocol()["registered_trial_counts"] == [2, 3, 5]


def test_claim_boundary_preserves_optimizer_distinction() -> None:
    boundary = protocol()["claim_boundary"]
    assert "does not prove that uniform allocation is optimal" in boundary
    assert "Tutte multiplicativity" in boundary
    assert "even inside one block" in boundary
    assert len(protocol()["complexity_statement"]["forbidden"]) == 4


def test_environment_lock_is_declared_and_complete() -> None:
    value = protocol()
    lock = json.loads(
        (HERE / value["environment_lock_path"]).read_text(
            encoding="utf-8"
        )
    )
    assert set(lock) == {
        "implementation",
        "networkx",
        "platform",
        "python",
    }
