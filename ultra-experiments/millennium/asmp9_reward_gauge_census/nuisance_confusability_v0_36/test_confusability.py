from __future__ import annotations

from itertools import product
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from confusability import (
    all_tables,
    confusability_relation,
    decision_identifiable,
    decoder_exists,
    is_equivalence_relation,
    is_reflexive,
    is_symmetric,
    is_transitive,
    mirrored_threshold_tables,
    relation_edge_bits,
    relation_subset,
    set_equality_relation,
    signatures,
)


def test_mirrored_threshold_one_query_is_nontransitive_path() -> None:
    q0, q1 = mirrored_threshold_tables()
    for table in (q0, q1):
        observation_sets = signatures(
            (table,), 3, 2, nuisance_mode="shared"
        )
        relation = confusability_relation(observation_sets)
        assert is_reflexive(relation)
        assert is_symmetric(relation)
        assert not is_transitive(relation)
        assert relation_edge_bits(relation) == "101"
        assert is_equivalence_relation(
            set_equality_relation(observation_sets)
        )


def test_decision_criterion_matches_direct_fibers_on_witness() -> None:
    q0, _ = mirrored_threshold_tables()
    observation_sets = signatures((q0,), 3, 2, nuisance_mode="shared")
    relation = confusability_relation(observation_sets)
    for decisions in product(range(3), repeat=3):
        assert decision_identifiable(relation, decisions) == decoder_exists(
            observation_sets, decisions
        )


def test_joint_shared_witness_identifies_but_reset_does_not() -> None:
    tables = mirrored_threshold_tables()
    shared_sets = signatures(tables, 3, 2, nuisance_mode="shared")
    reset_sets = signatures(tables, 3, 2, nuisance_mode="reset")
    shared_relation = confusability_relation(shared_sets)
    reset_relation = confusability_relation(reset_sets)
    assert shared_sets == (
        frozenset({(0, 0)}),
        frozenset({(0, 1), (1, 0)}),
        frozenset({(1, 1)}),
    )
    assert decision_identifiable(shared_relation, (0, 1, 2))
    assert not decision_identifiable(reset_relation, (0, 1, 2))
    assert relation_subset(shared_relation, reset_relation)


def test_adding_shared_query_only_removes_edges_on_witness() -> None:
    q0, q1 = mirrored_threshold_tables()
    first = confusability_relation(
        signatures((q0,), 3, 2, nuisance_mode="shared")
    )
    second = confusability_relation(
        signatures((q1,), 3, 2, nuisance_mode="shared")
    )
    joint = confusability_relation(
        signatures((q0, q1), 3, 2, nuisance_mode="shared")
    )
    assert relation_subset(joint, first)
    assert relation_subset(joint, second)


def test_registered_table_cardinalities_are_exact() -> None:
    assert len(tuple(all_tables(3, 2, 2))) == 64
    assert len(tuple(all_tables(2, 2, 2))) == 16
    assert len(tuple(all_tables(3, 1, 2))) == 8
    assert len(tuple(all_tables(3, 2, 1))) == 1


def test_invalid_modes_and_cardinalities_fail_closed() -> None:
    q0, _ = mirrored_threshold_tables()
    try:
        signatures((q0,), 3, 2, nuisance_mode="unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown nuisance mode did not fail")
    try:
        tuple(all_tables(0, 2, 2))
    except ValueError:
        pass
    else:
        raise AssertionError("zero cardinality did not fail")


def test_protocol_preserves_claim_boundary_and_frozen_counts() -> None:
    import json

    protocol = json.loads(
        (HERE / "PROTOCOL_v0_36.json").read_text(encoding="utf-8")
    )
    assert protocol["status"] == "prospective_protocol_not_run"
    assert protocol["outcomes_consumed"] is False
    assert protocol["enumeration"]["one_query_primary"]["tables"] == 64
    assert (
        protocol["enumeration"]["two_query_primary"][
            "ordered_table_pairs"
        ]
        == 4096
    )
    assert [gate["gate"] for gate in protocol["fixed_gates"]] == [
        "N0",
        "M0",
        "D0",
        "Q0",
        "W0",
    ]
    assert "does not" in protocol["claim_boundary"]


def test_verifier_is_import_independent() -> None:
    source = (HERE / "verify_result.py").read_text(encoding="utf-8")
    assert "from confusability" not in source
    assert "from run_census" not in source
