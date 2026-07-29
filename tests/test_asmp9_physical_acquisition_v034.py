from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
HERE = (
    ROOT
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "physical_acquisition_v0_34"
)
V033 = HERE.parent / "decision_quotient_information_v0_33"
for path in (HERE, V033):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import analyze_burned_pilot as analysis  # noqa: E402
import asmp9_native_fixture as native  # noqa: E402
import pilot_design as design  # noqa: E402
import robust_probe_design as robust  # noqa: E402
import run_burned_pilot as runner  # noqa: E402


def test_manifest_is_disjoint_complete_and_hash_bound() -> None:
    manifest = design.build_manifest()
    rows = manifest["rows"]
    assert len(rows) == 1944
    pilot = [row for row in rows if row["phase"] == "burned_pilot"]
    holdout = [row for row in rows if row["phase"] == "future_holdout"]
    assert len(pilot) == len(holdout) == 972
    assert len({row["row_id"] for row in rows}) == len(rows)
    assert len({row["prompt_sha256"] for row in rows}) == len(rows)
    assert {row["query_type"] for row in rows} == {
        "standard_gamble",
        "compound_gamble",
        "policy_probe",
    }
    assert {
        query_type: sum(row["query_type"] == query_type for row in pilot)
        for query_type in (
            "standard_gamble",
            "compound_gamble",
            "policy_probe",
        )
    } == {
        "standard_gamble": 360,
        "compound_gamble": 180,
        "policy_probe": 432,
    }
    for row in rows:
        assert row["target_label"] in {"A", "B"}
        assert row["comparator_label"] in {"A", "B"}
        assert row["target_label"] != row["comparator_label"]
        assert row["row_sha256"] == design.sha256_bytes(
            design.canonical_bytes(
                {
                    key: value
                    for key, value in row.items()
                    if key != "row_sha256"
                }
            )
        )


def test_manifest_uses_exact_preferred_factorized_basis() -> None:
    sources = native.load_native_sources()
    preferred = robust.minimum_linf_factorized_probe_design(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    assert preferred.policy_contrast_basis_indices == (
        design.SELECTED_POLICY_CONTRASTS
    )
    assert preferred.cell_basis_indices == design.SELECTED_CELL_INDICES
    assert preferred.combined_amplification == 8


def test_pilot_selector_never_reads_holdout() -> None:
    manifest = design.build_manifest()
    full = runner.selected_rows(manifest, "burned_pilot", 2)
    smoke = runner.selected_rows(manifest, "smoke", 2)
    assert len(full) == 972
    assert len(smoke) == 6
    assert {row["query_type"] for row in smoke} == {
        "standard_gamble",
        "compound_gamble",
        "policy_probe",
    }
    assert all(row["phase"] == "burned_pilot" for row in (*full, *smoke))


def test_choice_distribution_is_complete_and_fail_closed() -> None:
    payload = {
        "completion_probabilities": [
            {
                "top_probs": [
                    {"token": "A", "prob": 0.3},
                    {"token": "B", "prob": 0.7},
                ]
            }
        ]
    }
    assert runner.extract_choice_distribution(payload) == {
        "A": pytest.approx(0.3),
        "B": pytest.approx(0.7),
    }
    with pytest.raises(ValueError, match="incomplete"):
        runner.extract_choice_distribution(
            {
                "completion_probabilities": [
                    {"top_probs": [{"token": "A", "prob": 1.0}]}
                ]
            }
        )
    with pytest.raises(ValueError, match="unexpected token"):
        runner.extract_choice_distribution(
            {
                "completion_probabilities": [
                    {
                        "top_probs": [
                            {"token": "A", "prob": 0.3},
                            {"token": "B", "prob": 0.6},
                            {"token": "C", "prob": 0.1},
                        ]
                    }
                ]
            }
        )


def test_crossing_interpolates_and_reports_forcing_bounds() -> None:
    result = analysis.crossing(
        [
            (Fraction(1, 6), 2.0),
            (Fraction(1, 3), 1.0),
            (Fraction(1, 2), -1.0),
        ]
    )
    assert result["status"] == "bracketed"
    assert result["estimate"] == pytest.approx(5 / 12)
    assert result["monotonicity_violations"] == 0
    assert analysis.crossing(
        [(Fraction(1, 6), -1.0), (Fraction(1, 2), -2.0)]
    )["status"] == "below_grid"
    assert analysis.crossing(
        [(Fraction(1, 6), 2.0), (Fraction(1, 2), 1.0)]
    )["status"] == "above_grid"


def test_policy_secant_analysis_recovers_linear_fixture() -> None:
    records = []
    for contrast in (0, 1, 2):
        for cell in (0, 1, 2, 4, 5, 7):
            slope = float((contrast + 1) * (cell + 1))
            for norm in (
                Fraction(0),
                Fraction(1, 8),
                Fraction(1, 4),
                Fraction(1, 2),
            ):
                records.append(
                    {
                        "query_type": "policy_probe",
                        "policy_contrast_index": contrast,
                        "cell_index": cell,
                        "family_id": "pilot_direct",
                        "norm": str(norm),
                        "target_log_odds": 0.25 + slope * float(norm),
                    }
                )
    rows, summary = analysis.analyze_policy_probes(records)
    assert len(rows) == 18
    assert summary["probe_count"] == 18
    assert summary["absolute_secant_residual"]["maximum"] < 1e-12
    assert summary["slope_matrix_numerical_rank"] == 1


def test_live_runner_requires_registered_job_wrapper() -> None:
    source = (HERE / "run_burned_pilot.py").read_text(encoding="utf-8")
    wrapper = (
        ROOT / "scripts" / "run_asmp9_v034_jobobject.ps1"
    ).read_text(encoding="utf-8")
    assert "ASMP9_V034_HARD_CAP_ACTIVE" in source
    assert "ASMP9_V034_HARD_CAP_ACTIVE" in wrapper
    assert "ConfigureMemory" in wrapper
    assert "ConfigureCpu" in wrapper
    assert "sustained_io_cap_exceeded" in wrapper
    assert "hard_temperature_abort" in wrapper
    assert "post_run_memory_cleanup.ps1" not in wrapper
    assert "cleanup_script" in wrapper

