from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def test_protocol_has_total_gate_and_claim_boundary() -> None:
    protocol = json.loads((HERE / "protocol_v0_32.json").read_text())
    assert protocol["protocol_id"] == "ASMP-9-BEHAVIORAL-RECTANGLE-v0.32"
    assert set(protocol["gates"]) == {
        "G0_registration_binding",
        "G1_population_acquisition",
        "G2_rectangle_algebra",
        "G3_complete_coverage",
        "G4_shared_uncertainty_geometry",
        "G5_three_state_semantics",
        "G6_mixture_affinity_liveness",
        "G7_access_no_go",
        "G8_finite_sample",
        "G9_v031_handoff",
        "G10_prior_art_and_claim_boundary",
        "G11_resource_and_scope",
    }
    assert "resolution of ASMP-9" in protocol["claim_boundary"]["excludes"]
    assert protocol["resource_caps"]["gpu_allowed"] is False


def test_protocol_fixes_binary_and_statistical_units() -> None:
    protocol = json.loads((HERE / "protocol_v0_32.json").read_text())
    primary = protocol["primary_fixture"]
    assert primary["row_count"] * primary["column_count"] == 12
    assert primary["bisection_depth"] == 4
    finite = protocol["finite_sample"]
    assert finite == {
        "correct_probability_floor": "3/4",
        "family_error": "1/100",
        "population_query_count": 48,
        "registered_minimum_odd_repeats": 43,
    }


def test_prior_art_and_scope_tokens_are_present() -> None:
    prior = (HERE / "PRIOR_ART_GATE_v0_32.md").read_text(encoding="utf-8")
    theorem = (HERE / "THEOREM_DRAFT_v0_32.md").read_text(encoding="utf-8")
    for token in ("Herstein", "Luce", "Torrance", "Wakker", "Chen"):
        assert token in prior
    for token in (
        "does not",
        "expected utility",
        "context-varying anchors",
        "ASMP-9",
    ):
        assert token in theorem


def test_registration_seals_every_prereveal_source() -> None:
    source = (HERE / "register_v0_32.py").read_text(encoding="utf-8")
    for name in (
        "DEVELOPMENT_NOTE_v0_32.md",
        "PRIOR_ART_GATE_v0_32.md",
        "README.md",
        "THEOREM_DRAFT_v0_32.md",
        "__init__.py",
        "behavioral_rectangle.py",
        "environment_lock_v0_32.json",
        "protocol_v0_32.json",
        "register_v0_32.py",
        "run_verification_v0_32.py",
        "test_behavioral_rectangle.py",
        "test_protocol_v0_32.py",
        "verify_result_v0_32.py",
    ):
        assert f'"{name}"' in source


def test_windows_resource_helper_declares_native_types() -> None:
    source = (HERE / "run_verification_v0_32.py").read_text(encoding="utf-8")
    assert "GetCurrentProcess.restype = wintypes.HANDLE" in source
    assert "GetProcessMemoryInfo.argtypes" in source
