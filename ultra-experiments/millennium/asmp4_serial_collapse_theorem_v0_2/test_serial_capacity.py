from __future__ import annotations

import math
import importlib.util
from fractions import Fraction
from pathlib import Path

from serial_capacity import (
    actuator_mode_side_information_replay,
    boundary_fixture_report,
    diagonal_box_exact_transcript_count,
    exhaustive_one_step_census,
    fixed_fifo_delay_relay_report,
    minimum_action_transcripts,
    mode_switching_plant,
    restricted_authority_plant,
    scalar_exact_rate,
    scalar_exact_transcript_count,
    shear_exact_transcript_count,
    uncertainty_timing_plant,
    verification_payload,
)


def test_exhaustive_one_step_serial_region_is_the_predicted_diagonal_quadrant():
    census = exhaustive_one_step_census()
    assert census["plant_observation_pairs"] == 162
    assert census["budget_cells"] == 648
    assert census["minimum_transcript_histogram"] == {
        "1": 112,
        "2": 8,
        "infeasible": 42,
    }
    assert census["mismatch_count"] == 0
    assert census["pass"] is True


def test_mode_switching_requires_every_binary_action_word():
    plant = mode_switching_plant()
    for horizon in range(1, 5):
        result = minimum_action_transcripts(plant, horizon)
        assert result["feasible"] is True
        assert result["minimum_action_transcript_count"] == 2**horizon


def test_actuator_local_mode_side_information_collapses_write_language():
    for horizon in range(1, 5):
        replay = actuator_mode_side_information_replay(horizon)
        assert replay == {"safe": True, "write_transcript_count": 1}


def test_partial_observation_and_unseen_current_uncertainty_are_kill_cases():
    for horizon in range(1, 5):
        assert (
            minimum_action_transcripts(
                mode_switching_plant(partial_observation=True), horizon
            )["feasible"]
            is False
        )
    assert (
        minimum_action_transcripts(uncertainty_timing_plant(), 1)["feasible"] is False
    )


def test_full_information_cannot_repair_insufficient_control_authority():
    assert minimum_action_transcripts(mode_switching_plant(), 1)["feasible"] is True
    assert (
        minimum_action_transcripts(restricted_authority_plant(), 1)["feasible"] is False
    )


def test_scalar_formula_has_exact_initial_margin_correction():
    assert [
        scalar_exact_transcript_count(2, Fraction(1, 4), 1, horizon)
        for horizon in range(1, 7)
    ] == [1, 1, 2, 4, 8, 16]
    assert scalar_exact_rate(2, Fraction(1, 4), 1, 2) == 0.0
    assert scalar_exact_rate(2, Fraction(1, 4), 1, 6) == math.log2(16) / 6
    assert scalar_exact_rate(2, 1, 1, 20) == 1.0


def test_diagonal_box_formula_recovers_sum_of_positive_exponents():
    counts = [
        diagonal_box_exact_transcript_count(
            (2, 3, Fraction(1, 2)),
            (Fraction(1, 4), Fraction(1, 9), 1),
            (1, 1, 1),
            horizon,
        )
        for horizon in range(1, 5)
    ]
    assert counts == [1, 1, 6, 36]
    asymptotic_rate = (
        math.log2(
            diagonal_box_exact_transcript_count(
                (2, 3, Fraction(1, 2)), (1, 1, 1), (1, 1, 1), 20
            )
        )
        / 20
    )
    assert asymptotic_rate == math.log2(6)


def test_nonhyperbolic_shear_has_zero_asymptotic_but_unbounded_finite_cost():
    counts = [
        shear_exact_transcript_count(Fraction(1, 2), 1, horizon)
        for horizon in range(1, 101)
    ]
    assert counts[:4] == [1, 1, 2, 2]
    assert counts[-1] == 50
    assert math.log2(counts[-1]) / 100 < 0.06


def test_fixed_fifo_delay_preserves_relay_languages_after_fixed_warmup():
    report = fixed_fifo_delay_relay_report()
    assert report["pass"] is True
    assert len(report["rows"]) == 24
    assert all(row["languages_match"] for row in report["rows"])


def test_boundary_report_and_all_verification_gates_pass():
    report = boundary_fixture_report()
    assert report["unseen_current_disturbance_feasible"] is False
    payload = verification_payload()
    assert payload["pass"] is True
    assert all(payload["gates"].values())


def test_independent_verifier_passes():
    path = Path(__file__).with_name("verify_theorem.py")
    spec = importlib.util.spec_from_file_location("asmp4_independent_verifier", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.verify()
    assert result["pass"] is True
    assert all(result["checks"].values())
