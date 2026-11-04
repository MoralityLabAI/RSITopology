from __future__ import annotations

import json

import pytest

from standard_encoding_transfer import (
    ARTIFACT_PATH,
    ENCODINGS,
    build_artifact,
    canonical_admissibility_rows,
    compile_family,
    coupling_fixture_rows,
    decode_family,
    encoding_fixture_rows,
    parent_resolution_audit,
    quantifier_mode_transfer_audit,
    source_resolution_audit,
    transfer_theorem_audit,
)
from verify_standard_encoding_transfer import verify


def test_source_registers_standard_encodings_and_full_set_undecidability_route() -> None:
    audit = source_resolution_audit()
    assert audit["certified"]
    assert all(audit["source_markers"].values())


def test_all_canonical_fields_are_preserved() -> None:
    rows = canonical_admissibility_rows()
    assert len(rows) == 16
    assert all(row["preserved"] for row in rows)


@pytest.mark.parametrize("encoding", ENCODINGS)
def test_each_standard_encoding_compiles_and_decodes(encoding: str) -> None:
    description = compile_family(encoding, 41)
    decoded = decode_family(description)
    assert decoded["machine_index"] == 41
    assert decoded["strict_fixed_interface"]
    assert decoded["bounded_simulation"]


def test_invalid_or_noncanonical_descriptions_are_rejected() -> None:
    with pytest.raises(ValueError):
        compile_family("not_an_encoding", 0)
    malformed = compile_family("json_ast", 7)
    malformed["relation"] = "constant_zero"
    with pytest.raises(ValueError):
        decode_family(malformed)


def test_all_encoding_fixture_rows_preserve_semantics() -> None:
    rows = encoding_fixture_rows()
    assert len(rows) == 720
    assert all(row["representation_preserves_semantics"] for row in rows)


def test_nonhalting_fixture_is_positive_in_every_encoding() -> None:
    rows = [row for row in encoding_fixture_rows() if row["machine_fixture"] == "NEVER"]
    assert len(rows) == 120
    assert all(row["membership"] and row["exact_gap"] == "3/5" for row in rows)


def test_halting_fixture_tails_are_zero_in_every_encoding() -> None:
    for row in encoding_fixture_rows():
        if row["machine_fixture"] == "NEVER":
            continue
        halt_time = int(row["machine_fixture"].split("_")[-1])
        if halt_time <= row["depth"]:
            assert row["exact_gap"] == "0"
            assert not row["membership"]


def test_transfer_targets_full_decision_set() -> None:
    audit = transfer_theorem_audit()
    assert audit["certified"]
    assert audit["full_decision_set"]["reduction_target"].startswith("the full set")
    assert all(audit["proof_obligations"].values())


def test_interactive_inactive_coupling_survives_all_fixtures() -> None:
    rows = coupling_fixture_rows()
    assert len(rows) == 2560
    assert all(row["all_transcript_prefixes_identical"] for row in rows)
    assert all(row["verifier_decisions_identical"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_quantifier_mode_transfer_covers_FIX_and_ADM() -> None:
    audit = quantifier_mode_transfer_audit()
    assert audit["certified"]
    assert set(audit["modes"]) == {"FIX", "ADM_singleton", "ADM_broad"}
    assert set(audit["full_decision_sets"]) == {"FIX", "ADM"}
    assert set(audit["effective_compilers"]) == {"FIX", "ADM_singleton", "ADM_broad"}
    assert all(audit["proof_obligations"].values())


def test_representation_evasion_requires_a_changed_or_nonstandard_problem() -> None:
    cases = transfer_theorem_audit()["representation_evasion"]
    assert len(cases) == 4
    assert "new restricted problem" in cases["exclude_compiler_image"]
    assert "not a standard effective encoding" in cases["use_noncomputable_translation"]


def test_parent_disposition_retains_external_gate() -> None:
    audit = parent_resolution_audit()
    assert audit["source_resolution_rule_satisfied_under_ordinary_standard_encoding_reading"]
    assert audit["prize_grade_acceptance"] is False
    assert audit["external_expert_reproductions"] == "0/2"


def test_all_ten_producer_gates_pass() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["gates"]) == 12
    assert all(artifact["gates"].values())


def test_written_artifact_and_clean_room_verifier_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 12
