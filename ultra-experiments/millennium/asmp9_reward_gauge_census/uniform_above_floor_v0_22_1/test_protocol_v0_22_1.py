import hashlib
import json
from fractions import Fraction
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_22_1.json").read_text(encoding="utf-8")
    )


def graph(raw: dict) -> nx.Graph:
    result = nx.Graph()
    result.add_nodes_from(range(raw["node_count"]))
    result.add_edges_from(raw["edges"])
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_amendment_is_narrow_and_predecessor_is_bound() -> None:
    value = protocol()
    assert value["amends"] == "ASMP-9-UNIFORM-ABOVE-FLOOR-v0.22"
    assert "Mechanical successor only" in value["amendment_scope"]
    record = value["predecessor_record"]
    assert record["expected_gate_passes"][
        "G8_complexity_attribution"
    ] is False
    assert sum(record["expected_gate_passes"].values()) == 9
    for kind in (
        "registration",
        "result",
        "run_receipt",
        "independent_verification",
    ):
        path = (HERE / record[f"{kind}_path"]).resolve()
        assert sha256(path) == record[f"{kind}_sha256"]


def test_gate_ids_are_unique_and_total() -> None:
    gates = protocol()["gate_ids"]
    assert len(gates) == 10
    assert len(gates) == len(set(gates))


def test_structured_claim_lists_are_exact() -> None:
    statement = protocol()["complexity_statement"]
    assert statement["allowed"] == [
        "For every fixed r>=2, exact evaluation of the declared uniform "
        "allocation on finite simple biconnected blocks is #P-hard under "
        "polynomial-time Turing reductions, by Tutte block "
        "multiplicativity and explicit bridge factors.",
        "For fixed r, the common-denominator microtrial numerator is "
        "#P-complete under polynomial-time Turing reductions.",
        "The r=2 minimal uniform above-floor cell evaluates T_G(2/3,4) "
        "times a known nonzero rational prefactor.",
    ]
    assert statement["forbidden"] == [
        "Maximin allocation is #P-hard.",
        "Uniform allocation is optimal on arbitrary biconnected blocks.",
        "Nonuniform counts or arbitrary endpoint probabilities are "
        "classified.",
        "The Backman formula or the Tutte hard curve is new.",
    ]


def test_registered_graphs_are_fresh_biconnected_blocks() -> None:
    value = protocol()
    candidates = {
        name: graph(raw)
        for name, raw in value["primary_graphs"].items()
    }
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
    for candidate in candidates.values():
        assert nx.is_biconnected(candidate)
        assert not list(nx.bridges(candidate))
        assert (
            candidate.number_of_nodes() > 6
            or candidate.number_of_edges() > 9
        )
        assert not any(
            old.number_of_nodes() == candidate.number_of_nodes()
            and old.number_of_edges() == candidate.number_of_edges()
            and nx.is_isomorphic(old, candidate)
            for old in prior
        )
    names = sorted(candidates)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            assert not nx.is_isomorphic(
                candidates[left], candidates[right]
            )


def test_registered_points_are_nonexceptional_h_minus_one() -> None:
    for trial_count in protocol()["registered_trial_counts"]:
        z = Fraction(1, 2**trial_count)
        x_value = (1 - 2 * z) / (1 - z)
        y_value = 1 / z
        assert (x_value - 1) * (y_value - 1) == -1
        assert 0 < x_value < 1 < y_value
    assert protocol()["registered_trial_counts"] == [2, 3, 5]


def test_environment_lock_is_complete() -> None:
    lock = json.loads(
        (HERE / protocol()["environment_lock_path"]).read_text(
            encoding="utf-8"
        )
    )
    assert set(lock) == {
        "implementation",
        "networkx",
        "platform",
        "python",
    }
