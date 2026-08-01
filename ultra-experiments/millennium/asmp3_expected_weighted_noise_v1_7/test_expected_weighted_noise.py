from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from expected_weighted_noise import (
    build_result,
    compositions,
    exact_value,
    expected_row,
    grid_exhaustion,
    word_scores,
)
from verify_expected_weighted_noise import verify


Q = Fraction
HERE = Path(__file__).resolve().parent


def test_invalid_costs_and_budgets_are_rejected() -> None:
    for costs, budget in (((), Q(0)), ((1, 0), Q(0)), ((1, 2), Q(-1)), ((1, 2), Q(4))):
        with pytest.raises(ValueError):
            expected_row(costs, budget)
    with pytest.raises(ValueError):
        exact_value(0, Q(0))


def test_closed_form_supports_fractional_budgets() -> None:
    assert exact_value(8, Q(3, 2)) == Q(5, 8)
    assert exact_value(8, Q(4)) == 0
    assert exact_value(8, Q(7)) == 0


def test_endpoint_mixture_is_feasible_and_matches_value() -> None:
    for costs in ((1,), (1, 3), (2, 2, 5), (1, 2, 4, 8)):
        total = sum(costs)
        for twice_budget in range(2 * total + 1):
            budget = Q(twice_budget, 2)
            row = expected_row(costs, budget)
            assert Q(row["endpoint_expected_flip_cost_each_truth"]) <= budget
            assert Q(row["endpoint_total_variation"]) == Q(row["value"])
            assert row["certified"]


def test_linear_verifier_certificate_matches_positive_phase() -> None:
    for total in range(1, 17):
        for twice_budget in range(2 * total + 1):
            budget = Q(twice_budget, 2)
            row = expected_row((total,), budget)
            linear = Q(1) - 2 * budget / total
            assert Q(row["dual_expectation_gap_lower_bound"]) == max(Q(0), linear)
            assert (row["phase"] == "positive_advantage") == (linear > 0)


def test_value_depends_only_on_total_cost() -> None:
    families = ((1, 1, 4, 4), (2, 2, 2, 4), (1, 2, 3, 4))
    for twice_budget in range(21):
        budget = Q(twice_budget, 2)
        values = {expected_row(costs, budget)["value"] for costs in families}
        assert len(values) == 1


def test_hard_and_expected_constraints_strictly_separate() -> None:
    row = expected_row((2, 2, 2, 4), 5)
    assert row["value"] == "0"
    result = build_result()
    witness = next(
        item
        for item in result["strict_hard_expected_separations"]
        if item["costs"] == [2, 2, 2, 4] and item["budget"] == 5
    )
    assert witness == {
        "costs": [2, 2, 2, 4],
        "budget": 5,
        "hard_value": "1",
        "expected_value": "0",
    }


def test_composition_enumerator_is_complete() -> None:
    rows = compositions(4, 3)
    assert len(rows) == 15
    assert len(set(rows)) == 15
    assert all(sum(row) == 4 and min(row) >= 0 for row in rows)


def test_word_scores_cover_weighted_endpoints() -> None:
    values = word_scores((1, 3, 7))
    assert len(values) == 8
    assert values[0] == 0
    assert values[-1] == 11
    assert set(values) == {0, 1, 3, 4, 7, 8, 10, 11}


def test_small_distribution_grid_matches_closed_form() -> None:
    grid = grid_exhaustion()
    assert grid["case_count"] == 39
    assert grid["distribution_pairs_checked"] == 35808
    assert grid["all_grid_optima_match"]
    assert all(row["matches"] for row in grid["rows"])


def test_parent_registry_and_all_gates_pass() -> None:
    result = build_result()
    assert len(result["expected_rows"]) == 2729
    assert len(result["strict_hard_expected_separations"]) == 1139
    assert result["certified"]
    assert len(result["gates"]) == 9
    assert all(result["gates"].values())


def test_large_binary_cost_certificate_is_constant_size() -> None:
    witness = build_result()["large_succinct_witness"]
    assert witness["total_cost"] == (1 << 32) - 1
    assert witness["value"] == "1/3"
    assert witness["response_words_enumerated"] == 0


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_noise_quantifier_and_remaining_scope_are_explicit() -> None:
    theorem = (HERE / "EXPECTED_WEIGHTED_NOISE_THEOREM_v1_7.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v1_7.md").read_text(encoding="utf-8")
    assert "Noise-class firewall" in theorem
    assert "grid is not used to" in theorem
    assert "honest-prover computation characterization = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
