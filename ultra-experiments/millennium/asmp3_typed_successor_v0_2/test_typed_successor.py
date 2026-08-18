from __future__ import annotations

import json
from pathlib import Path

from build_release_manifest import verify_manifest
from validate_typed_successor import (
    DRAFT_PATH,
    EXPECTED_JOINT_RISK_CONDITIONS,
    EXPECTED_LAYERS,
    EXPECTED_REFUTE_AXIOMS,
    HERE,
    load_json,
    validate,
)


def draft() -> dict:
    return load_json(DRAFT_PATH)


def witness() -> dict:
    value = draft()
    return load_json((HERE / value["witness_artifact"]).resolve())


def test_draft_is_explicitly_nonnormative() -> None:
    value = draft()
    assert value["status"] == "nonnormative_successor_draft"
    assert value["parent_problem_id"] == "ASMP-3"
    assert value["changes_parent_problem"] is False
    assert "Definition draft only" in value["claim_boundary"]


def test_environment_game_protocol_layers_are_complete() -> None:
    layers = draft()["typed_layers"]
    assert set(layers) == set(EXPECTED_LAYERS)
    for name, expected in EXPECTED_LAYERS.items():
        assert set(layers[name]) == expected
    assert not set(layers["fixed_game"]) & set(layers["protocol"])


def test_fixed_and_admissible_interfaces_have_different_quantifiers() -> None:
    modes = draft()["interface_modes"]
    assert modes["fixed"]["class_name"] == "WV-FIX"
    assert (
        modes["fixed"]["interface_quantifier"]
        == "fixed_before_protocol_algorithms"
    )
    assert modes["existential"]["class_name"] == "WV-ADM"
    assert (
        modes["existential"]["interface_quantifier"]
        == "exists_G_in_declared_Interfaces_E"
    )


def test_refute_adequacy_and_replication_quotient_are_required() -> None:
    value = draft()
    assert set(value["refute_adequacy_axioms"]) == EXPECTED_REFUTE_AXIOMS
    assert (
        value["interface_modes"]["fixed"]["refutation_invariant"]
        == "replication_quotiented_r_E_G"
    )
    assert (
        "effective_best_interface_r_star_E"
        in value["interface_modes"]["existential"][
            "refutation_invariant_options"
        ]
    )


def test_joint_noise_risk_covers_selection_and_adaptivity() -> None:
    noise = draft()["noise_objects"]
    assert noise["single_atom_profile_role"] == "marginal_diagnostic_only"
    assert (
        noise["required_characterization_object"]
        == "joint_transcript_conditional_selected_refutation_risk"
    )
    assert set(noise["conditions_in_scope"]) == (
        EXPECTED_JOINT_RISK_CONDITIONS
    )


def test_successor_poses_both_characterization_targets() -> None:
    assert set(draft()["successor_targets"]) == {
        "characterize_WV_FIX",
        "characterize_WV_ADM",
    }


def test_v0_7_witness_aligns_with_both_typed_branches() -> None:
    value = draft()
    evidence = witness()
    assert evidence["status"] == "exact_quantifier_fork"
    assert evidence["certified"]
    assert all(evidence["gates"].values())
    assert (
        evidence["frozen_encoding_branch"]["asymptotic_gap"]
        == value["interface_modes"]["fixed"]["v0_7_witness_gap"]
        == "(3/5)^d -> 0"
    )
    assert (
        evidence["existential_encoding_branch"]["constant_gap"]
        == value["interface_modes"]["existential"][
            "v0_7_vector_protocol_gap"
        ]
        == "3/5"
    )


def test_markdown_contains_typed_firewall_and_resolution_obligations() -> None:
    text = (
        Path(HERE) / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
    ).read_text(encoding="utf-8")
    assert "This draft does not amend v0.1." in text
    assert "WV-FIX(E,G)" in text
    assert "WV-ADM(E,Interfaces)" in text
    assert "Joint semantic-noise profile" in text
    assert "Resolution obligations" in text


def test_independent_validation_passes() -> None:
    result = validate()
    assert result["check_count"] == len(result["checks"])
    assert result["passed"]
    assert all(result["checks"].values())


def test_release_manifest_matches() -> None:
    assert verify_manifest()
