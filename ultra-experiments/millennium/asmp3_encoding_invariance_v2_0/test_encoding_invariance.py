from __future__ import annotations

from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from encoding_invariance import (
    alias_map,
    build_result,
    canonical_witnesses,
    exhaustive_alias_audit,
    exhaustive_raw_minimum,
    make_task,
    parity_macro_row,
    quotient_dimension,
    transcript_minima,
    transport_registry,
    transport_task,
)
from verify_encoding_invariance import verify


HERE = Path(__file__).resolve().parent


def test_invalid_tasks_and_aliases_are_rejected() -> None:
    for count, levels in ((0, (1,)), (3, ()), (3, (0,)), (3, (4,))):
        with pytest.raises(ValueError):
            make_task(count, levels)
    with pytest.raises(ValueError):
        alias_map((1, 0))
    with pytest.raises(ValueError):
        parity_macro_row(1)


def test_quotient_dimension_is_maximum_transcript_minimum() -> None:
    task = make_task(6, (1, 3, 5))
    assert transcript_minima(task) == {"tau_0": 1, "tau_1": 3, "tau_2": 5}
    assert quotient_dimension(task) == 5


def test_bijective_transport_preserves_dimension_and_witnesses() -> None:
    source = make_task(5, (2, 4))
    class_map = {item: (item + 2) % 5 for item in range(5)}
    transcript_map = {"tau_0": "right", "tau_1": "left"}
    encoded = transport_task(source, class_map, transcript_map)
    assert quotient_dimension(encoded) == quotient_dimension(source) == 4
    for transcript, witness in canonical_witnesses(source).items():
        transported = frozenset(class_map[item] for item in witness)
        assert transported in encoded[transcript_map[transcript]]


def test_nonbijective_transport_is_rejected() -> None:
    source = make_task(3, (2,))
    with pytest.raises(ValueError, match="class transport"):
        transport_task(source, {0: 0, 1: 0, 2: 1}, {"tau_0": "encoded"})
    with pytest.raises(ValueError, match="transcript transport"):
        transport_task(source, {0: 0, 1: 1, 2: 2}, {})


def test_alias_projection_preserves_minimum_witness_size() -> None:
    task = make_task(4, (3,))
    aliases = alias_map((1, 2, 3, 1))
    assert exhaustive_raw_minimum(task["tau_0"], aliases) == 3


def test_all_small_alias_expansions_are_exhaustive() -> None:
    rows = exhaustive_alias_audit()
    assert len(rows) == 14
    assert all(row["raw_minimum"] == row["quotient_minimum"] for row in rows)
    assert all(row["matches"] for row in rows)


def test_transport_registry_is_complete_and_invariant() -> None:
    rows = transport_registry()
    assert len(rows) == 27
    assert all(row["source_dimension"] == row["encoded_dimension"] for row in rows)
    assert all(row["canonical_witness_transport_holds"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_parity_macro_requires_every_primitive_query() -> None:
    for bit_count in range(4, 13):
        row = parity_macro_row(bit_count)
        assert row["ambiguous_partial_assignments_checked"] == 3**bit_count - 2**bit_count
        assert row["every_nonterminal_partial_assignment_ambiguous"]
        assert row["pivotal_bits"] == bit_count
        assert row["exact_deterministic_query_complexity"] == bit_count


def test_macro_dimension_drop_is_not_benign_or_locally_affordable() -> None:
    for bit_count in range(4, 13):
        row = parity_macro_row(bit_count)
        assert row["base_refutation_dimension"] == bit_count
        assert row["macro_refutation_dimension"] == 1
        assert not row["semantic_class_bijection_exists"]
        assert not row["macro_within_declared_budget"]
        assert not row["benign_encoding"]


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["transport_rows"]) == 27
    assert len(result["exhaustive_alias_rows"]) == 14
    assert len(result["parity_macro_rows"]) == 9
    assert result["certified"]
    assert len(result["gates"]) == 10
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_resource_and_asymptotic_boundaries_are_explicit() -> None:
    theorem = (HERE / "ENCODING_INVARIANCE_THEOREM_v2_0.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v2_0.md").read_text(encoding="utf-8")
    assert "Resource-preserving encoding rule" in theorem
    assert "deterministic exact evaluation" in theorem
    assert "uniform asymptotic encoding maps" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
