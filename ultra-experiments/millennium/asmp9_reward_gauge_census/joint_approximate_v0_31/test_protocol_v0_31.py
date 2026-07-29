import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def test_protocol_is_complete_and_cpu_only():
    protocol = json.loads(
        (HERE / "protocol_v0_31.json").read_text(encoding="utf-8")
    )
    assert protocol["protocol_id"] == "ASMP-9-JOINT-APPROXIMATE-v0.31"
    assert protocol["version"] == "0.31"
    assert not protocol["resource_caps"]["gpu_allowed"]
    assert protocol["resource_caps"]["wall_seconds"] == 30
    assert len(protocol["gates"]) == 12
    assert set(protocol["gates"]) == {
        f"G{index}_{name}"
        for index, name in (
            (0, "registration_binding"),
            (1, "context_projection"),
            (2, "joint_source_coverage"),
            (3, "mechanical_contraction"),
            (4, "semantic_incidence"),
            (5, "support_sharpness"),
            (6, "policy_handoff"),
            (7, "source_ablation"),
            (8, "shape_advantage"),
            (9, "context_rank_no_go"),
            (10, "prior_art_and_claim_boundary"),
            (11, "resource_and_scope"),
        )
    }


def test_primary_fixture_respects_declared_source_bounds():
    protocol = json.loads(
        (HERE / "protocol_v0_31.json").read_text(encoding="utf-8")
    )
    fixture = protocol["primary_fixture"]
    for row, bound in zip(
        fixture["mechanical_delta"],
        fixture["mechanical_row_l1_widths"],
    ):
        assert sum(abs(Fraction(value)) for value in row) <= Fraction(bound)
    for values, widths in (
        (fixture["localization_error"], fixture["localization_widths"]),
        (
            fixture["midpoint_residual"],
            fixture["midpoint_residual_widths"],
        ),
        (fixture["semantic_residual"], fixture["semantic_cell_widths"]),
    ):
        assert all(
            abs(Fraction(value)) <= Fraction(width)
            for value, width in zip(values, widths)
        )


def test_claim_boundary_and_prior_art_are_explicit():
    protocol = json.loads(
        (HERE / "protocol_v0_31.json").read_text(encoding="utf-8")
    )
    excluded = " ".join(protocol["claim_boundary"]["excludes"]).lower()
    assert "resolution of asmp-9" in excluded
    prior = (HERE / "PRIOR_ART_GATE_v0_31.md").read_text(encoding="utf-8")
    theorem = (HERE / "THEOREM_DRAFT_v0_31.md").read_text(encoding="utf-8")
    for token in (
        "Frisch",
        "El Ghaoui",
        "set-membership",
        "support function",
        "Abbeel",
        "Iyengar",
        "Nilim",
        "Novelty is not claimed",
    ):
        assert token.lower() in (prior + theorem).lower()
