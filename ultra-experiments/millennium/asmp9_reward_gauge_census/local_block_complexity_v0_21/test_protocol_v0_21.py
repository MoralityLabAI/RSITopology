import json
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent


def load_protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_21.json").read_text(encoding="utf-8")
    )


def graph_from_raw(raw: dict) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(raw["node_count"]))
    graph.add_edges_from(raw["edges"])
    return graph


def test_gate_ids_are_total_and_unique() -> None:
    gates = load_protocol()["gate_ids"]
    assert len(gates) == 10
    assert len(gates) == len(set(gates))
    assert gates[0] == "G0_registration_binding"
    assert gates[-1] == "G9_resource_and_scope"


def test_primary_graphs_are_pairwise_nonisomorphic_blocks() -> None:
    graphs = {
        name: graph_from_raw(raw)
        for name, raw in load_protocol()["primary_graphs"].items()
    }
    for graph in graphs.values():
        assert nx.is_connected(graph)
        assert nx.is_biconnected(graph)
    names = sorted(graphs)
    for left_index, left in enumerate(names):
        for right in names[left_index + 1 :]:
            assert not nx.is_isomorphic(graphs[left], graphs[right])


def test_control_structures_match_registration() -> None:
    controls = load_protocol()["controls"]
    bridge = graph_from_raw(controls["bridge_scope"])
    assert len(list(nx.bridges(bridge))) == 1
    product = graph_from_raw(controls["block_product"])
    blocks = list(nx.biconnected_component_edges(product))
    assert sum(len(block) > 1 for block in blocks) == 2


def test_prior_art_and_forbidden_claims_are_explicit() -> None:
    protocol = load_protocol()
    assert len(protocol["prior_art"]) == 3
    assert len(protocol["complexity_statement"]["allowed"]) == 3
    assert len(protocol["complexity_statement"]["forbidden"]) == 4
    assert "does not classify optimizer search" in protocol[
        "claim_boundary"
    ]

