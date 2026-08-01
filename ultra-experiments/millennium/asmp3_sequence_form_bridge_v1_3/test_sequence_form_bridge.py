from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from sequence_form_bridge import (
    analyze_tree,
    audit_sequence_saddle,
    behavior_from_realization,
    build_result,
    compile_sequence_form,
    concealment_game,
    concealment_row,
    imperfect_recall_fixture,
    matching_game,
    matching_row,
    nested_perfect_recall_game,
    nested_row,
    realization_from_behavior,
    uniform_behavior,
)
from verify_sequence_form_bridge import verify


HERE = Path(__file__).resolve().parent


def test_matching_information_structure_changes_value() -> None:
    revealed = matching_row(hidden=False)
    hidden = matching_row(hidden=True)
    assert revealed["value"] == "-1"
    assert hidden["value"] == "0"
    assert revealed["certified"] and hidden["certified"]


def test_information_set_counts_differ_for_matching() -> None:
    revealed = compile_sequence_form(matching_game(hidden=False))
    hidden = compile_sequence_form(matching_game(hidden=True))
    assert len(revealed.min_form.information_sets) == 2
    assert len(hidden.min_form.information_sets) == 1


def test_imperfect_recall_is_rejected() -> None:
    with pytest.raises(ValueError, match="perfect recall violated"):
        analyze_tree(imperfect_recall_fixture())


def test_behavior_realization_round_trip() -> None:
    compiled = compile_sequence_form(concealment_game(4))
    for form in (compiled.max_form, compiled.min_form):
        behavior = uniform_behavior(form, 4)
        realization = realization_from_behavior(form, behavior)
        recovered = behavior_from_realization(form, realization)
        assert realization_from_behavior(form, recovered) == realization


def test_nested_fixture_has_length_two_sequences() -> None:
    compiled = compile_sequence_form(nested_perfect_recall_game())
    assert max(len(sequence) for sequence in compiled.max_form.sequences) == 2
    row = nested_row()
    assert row["value"] == "1"
    assert row["certified"]


def test_concealment_counts_and_values() -> None:
    for size in range(2, 9):
        row = concealment_row(size)
        assert row["pure_strategies_per_role"] == size**size
        assert row["normal_matrix_entries"] == (size**size) ** 2
        assert row["sequences_per_role"] == 1 + size * size
        assert row["terminal_histories"] == size**3
        assert row["value"] == str(Fraction(size - 1, size))
        assert row["certified"]


def test_small_normal_forms_match_sequence_values() -> None:
    for size in (2, 3):
        row = concealment_row(size)
        assert row["normal_form_audit"] is not None
        assert row["normal_form_audit"]["exact"]
        assert row["normal_form_audit"]["value"] == row["value"]


def test_large_rows_avoid_normal_form_enumeration() -> None:
    for size in range(4, 9):
        row = concealment_row(size)
        assert row["normal_form_audit"] is None
        assert row["audit"]["exact"]


def test_uniform_sequence_saddle_can_be_reaudited() -> None:
    compiled = compile_sequence_form(concealment_game(5))
    x = realization_from_behavior(compiled.max_form, uniform_behavior(compiled.max_form, 5))
    y = realization_from_behavior(compiled.min_form, uniform_behavior(compiled.min_form, 5))
    audit = audit_sequence_saddle(compiled, x, y, Fraction(4, 5))
    assert audit["exact"]
    assert audit["lower_value"] == audit["upper_value"] == "4/5"


def test_all_producer_gates_pass() -> None:
    result = build_result()
    assert result["certified"]
    assert len(result["gates"]) == 8
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 9
    assert all(result["checks"].values())


def test_scope_and_noise_boundary_are_explicit() -> None:
    theorem = (HERE / "SEQUENCE_FORM_THEOREM_v1_3.md").read_text(encoding="utf-8")
    audit = (HERE / "COMPLETION_AUDIT_v1_3.md").read_text(encoding="utf-8")
    assert "perfect-recall sequence saddle" in theorem
    assert "Imperfect-recall firewall" in theorem
    assert "compact robust adaptive-noise controller = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
