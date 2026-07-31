import json
from fractions import Fraction
from pathlib import Path

from selection_barrier import (
    ATOM_GRID,
    ERROR_LIMIT,
    build_result,
    deterministic_worst_case_false_accept,
    exhaustive_formula_check,
    miss_probability_without_replacement,
    polylog_calibration_budget,
    randomized_minimax_false_accept,
    required_distinct_calibration,
    selected_blind_spot_majority_false_accept,
)


def test_exhaustive_small_universes_match_hypergeometric_formula() -> None:
    assert exhaustive_formula_check()


def test_one_blind_spot_has_sharp_randomized_minimax_value() -> None:
    for atom_count in range(1, 65):
        for calibration_count in range(atom_count + 1):
            expected = Fraction(atom_count - calibration_count, atom_count)
            assert (
                miss_probability_without_replacement(
                    atom_count,
                    calibration_count,
                    1,
                )
                == expected
            )
            assert (
                randomized_minimax_false_accept(
                    atom_count,
                    calibration_count,
                )
                == expected
            )


def test_fixed_calibration_is_unit_worst_case_until_exhaustive() -> None:
    for atom_count in range(1, 65):
        for calibration_count in range(atom_count):
            assert (
                deterministic_worst_case_false_accept(
                    atom_count,
                    calibration_count,
                )
                == 1
            )
        assert deterministic_worst_case_false_accept(atom_count, atom_count) == 0


def test_five_percent_uniform_gate_requires_95_percent_coverage() -> None:
    for atom_count in ATOM_GRID:
        required = required_distinct_calibration(atom_count, ERROR_LIMIT)
        assert randomized_minimax_false_accept(atom_count, required) <= ERROR_LIMIT
        if required:
            assert (
                randomized_minimax_false_accept(atom_count, required - 1)
                > ERROR_LIMIT
            )
        assert required >= Fraction(19, 20) * atom_count


def test_round_robin_polylog_scale_fails_every_registered_size() -> None:
    for atom_count in ATOM_GRID:
        calibration_count = polylog_calibration_budget(atom_count)
        assert (
            randomized_minimax_false_accept(atom_count, calibration_count)
            > ERROR_LIMIT
        )


def test_repetition_cannot_repair_a_deterministic_selected_blind_spot() -> None:
    for query_count in (1, 3, 5, 7, 9, 101):
        assert selected_blind_spot_majority_false_accept(query_count) == 1


def test_result_certificate_passes() -> None:
    result = build_result()
    assert result["certified"]
    assert all(result["gates"].values())


def test_emitted_certificate_matches_exact_builder() -> None:
    artifact = Path(__file__).resolve().parent / "selection_barrier_v0_2.json"
    assert json.loads(artifact.read_text(encoding="utf-8")) == build_result()
