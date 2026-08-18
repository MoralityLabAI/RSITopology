from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from polyhedral_tv_frontier import (
    audit_polyhedral_certificate,
    build_result,
    dual_linear_combination,
    fixture_rows,
    law_polytope,
    total_variation,
)
from verify_polyhedral_tv_frontier import verify


HERE = Path(__file__).resolve().parent


def test_law_polytope_enforces_simplex() -> None:
    polytope = law_polytope(3)
    assert polytope.contains((Fraction(1, 3),) * 3)
    assert polytope.contains((Fraction(1), Fraction(0), Fraction(0)))
    assert not polytope.contains((Fraction(1), Fraction(1), Fraction(-1)))
    assert not polytope.contains((Fraction(1), Fraction(1), Fraction(0)))


def test_dual_rejects_negative_inequality_multiplier() -> None:
    polytope = law_polytope(2)
    with pytest.raises(ValueError, match="must be nonnegative"):
        dual_linear_combination(
            polytope,
            (Fraction(-1), Fraction(0)),
            (Fraction(0),),
        )


def test_total_variation_is_exact() -> None:
    assert total_variation(
        (Fraction(4, 5), Fraction(1, 5)),
        (Fraction(1, 5), Fraction(4, 5)),
    ) == Fraction(3, 5)
    assert total_variation(
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(1, 2)),
    ) == 0


def test_all_fixture_certificates_are_exact() -> None:
    rows = fixture_rows()
    assert len(rows) == 3
    assert all(row["audit"]["exact"] for row in rows)
    assert all(
        row["audit"]["honest_minimum_dual"]["valid"]
        and row["audit"]["false_maximum_dual"]["valid"]
        for row in rows
    )


def test_interval_noise_band_has_constant_gap() -> None:
    row = {row["case_id"]: row for row in fixture_rows()}[
        "interval_noise_bands"
    ]
    assert row["audit"]["lower_gap"] == "3/5"
    assert row["audit"]["upper_tv_witness"] == "3/5"


def test_polyhedral_collision_has_zero_gap() -> None:
    row = {row["case_id"]: row for row in fixture_rows()}[
        "polyhedral_hull_collision"
    ]
    assert row["audit"]["claimed_gap"] == "0"
    assert row["audit"]["exact"]


def test_joint_event_band_has_equal_marginal_witnesses() -> None:
    row = {row["case_id"]: row for row in fixture_rows()}[
        "joint_event_robust_bands"
    ]
    witness = row["equal_marginal_witness"]
    honest = [Fraction(value) for value in witness["honest"]]
    false = [Fraction(value) for value in witness["false"]]
    for indices in ((2, 3), (1, 3)):
        assert sum(honest[index] for index in indices) == Fraction(1, 2)
        assert sum(false[index] for index in indices) == Fraction(1, 2)
    assert row["audit"]["claimed_gap"] == "3/5"


def test_shape_mismatch_is_rejected() -> None:
    honest = law_polytope(2)
    false = law_polytope(3)
    with pytest.raises(ValueError, match="alphabets differ"):
        audit_polyhedral_certificate(
            honest,
            false,
            (Fraction(0), Fraction(0)),
            Fraction(0),
            Fraction(0),
            (Fraction(0), Fraction(0)),
            (Fraction(0),),
            (Fraction(0), Fraction(0), Fraction(0)),
            (Fraction(0),),
            (Fraction(1), Fraction(0)),
            (Fraction(1), Fraction(0), Fraction(0)),
            Fraction(0),
        )


def test_all_producer_gates_pass() -> None:
    result = build_result()
    assert result["certified"]
    assert len(result["gates"]) == 6
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_theorem_keeps_representation_boundary_explicit() -> None:
    theorem = (HERE / "POLYHEDRAL_TV_FRONTIER_THEOREM_v0_9.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v0_9.md").read_text(encoding="utf-8")
    normalized = " ".join(theorem.split())
    assert "distance_TV(P,Q)" in theorem
    assert "Constructive verifier LP" in theorem
    assert "conditional on representation" in normalized
    assert "sequence-form/realization-plan bridge = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
