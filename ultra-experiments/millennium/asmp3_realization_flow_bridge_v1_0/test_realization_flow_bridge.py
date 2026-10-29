from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from realization_flow_bridge import (
    ControlledDAG,
    adaptive_graph,
    adaptive_row,
    audit_occupancy,
    band_graph,
    band_row,
    build_result,
    deterministic_policies,
    occupancy_from_policy,
    policy_from_occupancy,
    reconstruction_audit,
    uniform_policy,
)
from verify_realization_flow_bridge import verify


HERE = Path(__file__).resolve().parent


def test_band_graph_is_normalized_and_acyclic() -> None:
    for count in range(1, 9):
        graph = band_graph(count, Fraction(4, 5), Fraction(9, 10))
        graph.validate()
        assert sum(graph.initial.values(), Fraction(0)) == 1


def test_cycle_is_rejected() -> None:
    graph = ControlledDAG(
        states=("a", "b"),
        terminals=("z",),
        actions={"a": ("go",), "b": ("back",)},
        transitions={
            ("a", "go"): {"b": Fraction(1)},
            ("b", "back"): {"a": Fraction(1)},
        },
        initial={"a": Fraction(1)},
    )
    with pytest.raises(ValueError, match="not acyclic"):
        graph.validate()


def test_policy_to_flow_to_policy_is_exact() -> None:
    graph = band_graph(5, Fraction(4, 5), Fraction(9, 10))
    policy = uniform_policy(graph, Fraction(2, 5))
    occupancy, terminal = occupancy_from_policy(graph, policy)
    audit = audit_occupancy(graph, occupancy)
    recovered = policy_from_occupancy(graph, occupancy)
    recovered_occupancy, recovered_terminal = occupancy_from_policy(graph, recovered)
    assert audit["valid"]
    assert recovered_occupancy == occupancy
    assert recovered_terminal == terminal


def test_invalid_flow_is_rejected() -> None:
    graph = band_graph(2, Fraction(4, 5), Fraction(9, 10))
    occupancy, _ = occupancy_from_policy(graph, uniform_policy(graph, Fraction(0)))
    occupancy[("s0", "low")] += Fraction(1, 10)
    assert not audit_occupancy(graph, occupancy)["valid"]
    with pytest.raises(ValueError, match="does not satisfy"):
        policy_from_occupancy(graph, occupancy)


def test_pure_policy_count_is_exponential() -> None:
    for count in range(1, 9):
        graph = band_graph(count, Fraction(4, 5), Fraction(9, 10))
        assert len(deterministic_policies(graph)) == 1 << count


def test_band_rows_have_linear_flow_size_and_constant_gap() -> None:
    for count in range(1, 13):
        row = band_row(count)
        assert row["pure_policy_count_per_class"] == 1 << count
        assert row["flow_variable_count_per_class"] == 2 * count
        assert row["flow_equality_count_per_class"] == count
        assert row["exact_gap"] == "3/5"
        assert row["certified"]


def test_enumerated_band_extrema_match() -> None:
    for count in range(1, 9):
        row = band_row(count)
        assert row["enumerated_honest_extrema"] == ["4/5", "9/10"]
        assert row["enumerated_false_extrema"] == ["1/10", "1/5"]


def test_adaptive_graph_reconstruction_and_registry() -> None:
    graph = adaptive_graph()
    graph.validate()
    row = adaptive_row()
    assert row["audit"]["reconstruction_exact"]
    assert row["pure_policy_count"] == 8
    assert row["distinct_pure_terminal_law_count"] == 4


def test_reconstruction_audit_handles_unreachable_states() -> None:
    graph = adaptive_graph()
    policy = {
        "root": {"A": Fraction(1), "B": Fraction(0)},
        "left": {"yes": Fraction(1), "no": Fraction(0)},
        "right": {"yes": Fraction(0), "no": Fraction(1)},
    }
    assert reconstruction_audit(graph, policy)["reconstruction_exact"]


def test_all_producer_gates_pass() -> None:
    result = build_result()
    assert result["certified"]
    assert len(result["gates"]) == 7
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 7
    assert all(result["checks"].values())


def test_theorem_and_multi_role_boundary_are_explicit() -> None:
    theorem = (HERE / "REALIZATION_FLOW_THEOREM_v1_0.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v1_0.md").read_text(encoding="utf-8")
    normalized = " ".join(theorem.split()).lower()
    assert "policy-flow equivalence" in theorem
    assert "Extended polyhedral formulation" in theorem
    assert "multiple independently strategic roles" in normalized
    assert "two independently strategic advocates = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
