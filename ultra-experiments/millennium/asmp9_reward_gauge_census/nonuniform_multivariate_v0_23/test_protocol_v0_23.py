import hashlib
import json
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent


def load_protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_23.json").read_text(encoding="utf-8")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph(raw: dict) -> nx.Graph:
    value = nx.Graph()
    value.add_nodes_from(range(raw["node_count"]))
    value.add_edges_from(raw["edges"])
    return value


def test_protocol_identity_and_gate_universe() -> None:
    protocol = load_protocol()
    assert protocol["protocol_id"] == (
        "ASMP-9-NONUNIFORM-MULTIVARIATE-v0.23"
    )
    gates = protocol["gate_ids"]
    assert len(gates) == 11
    assert len(set(gates)) == 11
    assert gates[0] == "G0_registration_binding"
    assert gates[-1] == "G10_resource_and_scope"


def test_fresh_graph_is_biconnected_and_not_in_registry() -> None:
    protocol = load_protocol()
    candidate = graph(protocol["fresh_validation"]["graph"])
    assert nx.is_biconnected(candidate)
    assert not list(nx.bridges(candidate))
    registry_path = (
        HERE / protocol["freshness_rule"]["burned_registry_path"]
    ).resolve()
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for record in registry["records"]:
        old = graph(record)
        assert not (
            len(old) == len(candidate)
            and old.number_of_edges() == candidate.number_of_edges()
            and nx.is_isomorphic(old, candidate)
        )


def test_fresh_counts_are_total_and_nonuniform() -> None:
    protocol = load_protocol()
    edge_count = len(
        protocol["fresh_validation"]["graph"]["edges"]
    )
    counts = protocol["fresh_validation"]["counts"]
    assert len(counts) == 3
    for vector in counts.values():
        assert len(vector) == edge_count
        assert min(vector) >= 1
        assert len(set(vector)) >= 5


def test_k4_family_is_fixed_total_and_has_fresh_checks() -> None:
    value = load_protocol()["k4_family"]
    assert value["edge_order"] == ["01", "02", "03", "12", "13", "23"]
    assert value["trap_pattern"] == [
        "s-1",
        "s",
        "s+1",
        "s+1",
        "s",
        "s-1",
    ]
    assert value["balanced_pattern"] == ["s"] * 6
    assert value["fresh_numeric_checks"] == [9, 11, 17]


def test_claim_boundary_is_structured_and_conservative() -> None:
    protocol = load_protocol()
    allowed = protocol["structured_claims"]["allowed"]
    forbidden = protocol["structured_claims"]["forbidden"]
    assert len(allowed) == 4
    assert len(forbidden) == 6
    assert any("prior-art-derived" in claim for claim in allowed)
    assert "ASMP-9 is resolved." in forbidden
    assert any("NP-hard" in claim for claim in forbidden)
    assert "does not classify the global maximin optimizer" in protocol[
        "claim_boundary"
    ]


def test_environment_lock_matches_current_required_schema() -> None:
    lock = json.loads(
        (HERE / load_protocol()["environment_lock_path"]).read_text(
            encoding="utf-8"
        )
    )
    assert set(lock) == {
        "implementation",
        "networkx",
        "platform",
        "python",
    }


def test_prior_art_and_development_are_explicitly_separate() -> None:
    prior = (HERE / "PRIOR_ART_GATE_v0_23.md").read_text(
        encoding="utf-8"
    )
    development = (HERE / "DEVELOPMENT_NOTE_v0_23.md").read_text(
        encoding="utf-8"
    )
    assert "arXiv:math/0503607" in prior
    assert "arXiv:1408.3962" in prior
    assert "arXiv:2105.14228" in prior
    assert "outcome-bearing development record" in development
    assert "None of the graphs" in development


def test_resource_caps_are_cpu_only_and_bounded() -> None:
    caps = load_protocol()["resource_caps"]
    assert caps == {
        "gpu_allowed": False,
        "peak_resident_bytes": 1073741824,
        "wall_seconds": 180,
    }
