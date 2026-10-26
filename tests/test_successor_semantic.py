"""Independent oracle and information-interface checks for the FRC toy."""
import itertools
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

from rsi_topology.successor_inheritance import (
    Artifact, Row, Successor, adaptive_trial, one_target_trial, run_sweep,
    semantic_check, worst_case_fidelity,
)

ROOT = Path(__file__).resolve().parents[1]


def test_semantics_matches_exhaustive_oracle_for_all_short_row_sequences():
    alphabet = [Row("shutdown", x, label) for x in (0, 1, 5)
                for label in ("halt", "continue")] + [Row("task", 0, "solve")]
    for length in range(4):
        for rows in itertools.product(alphabet, repeat=length):
            artifact = Artifact(rows)
            result = semantic_check(artifact, 4)
            model = Successor(artifact)
            truth = {x for x in range(4) if model.on_shutdown(x) != "halt"}
            assert set(result["witnesses"]) == truth
            assert result["accepted"] == (not truth)


def test_semantic_verifier_needs_no_policy_calls_or_domain_enumeration():
    artifact = Artifact((Row("shutdown", 2**59, "continue"),))
    with patch.object(Successor, "on_shutdown", side_effect=AssertionError("black-box call")):
        receipt = semantic_check(artifact, 2**60)
    assert receipt["witnesses"] == [2**59]
    assert receipt["rows_scanned"] == 1
    assert receipt["membership_queries"] == 0


def test_repair_order_and_unapproved_safe_changes_distinguish_semantics_from_hash():
    result = one_target_trial(5, 7, include_semantic=True)["semantic"]
    for name in ("clean", "benign", "repaired", "unapproved_benign"):
        assert result[name]["accepted"]
        assert result[name]["matches_oracle"]
    assert not result["contaminated"]["accepted"]
    assert not result["repaired"]["digest_accepted"]
    assert not result["unapproved_benign"]["digest_accepted"]
    reversed_patch = Artifact((Row("shutdown", 4, "halt"), Row("shutdown", 4, "continue")))
    assert not semantic_check(reversed_patch, 8)["accepted"]


def test_paired_comparison_preserves_all_baseline_observations_and_rng():
    baseline, summary = run_sweep((5, 7), (1, 4), 4, 16, 20261026)
    enhanced, report = run_sweep((5, 7), (1, 4), 4, 16, 20261026, include_semantic=True)
    assert [{k: v for k, v in row.items() if k != "semantic"} for row in enhanced] == baseline
    assert {k: v for k, v in report.items() if k != "semantic_comparison"} == summary
    assert report["semantic_comparison"]["oracle_disagreements"] == 0
    assert report["semantic_comparison"]["contaminated_single_rejections"] == 8


@pytest.mark.parametrize("budget", [0, 4, 128])
def test_adaptive_semantics_tracks_every_pre_and_post_repair_artifact(budget):
    result = adaptive_trial(7, 5, 123, budget, include_semantic=True)
    for pair, original in zip(result["semantic"]["rounds"], result["rounds"], strict=True):
        assert not pair["before"]["accepted"]  # a fresh point was just inserted
        assert pair["before"]["matches_oracle"] and pair["after"]["matches_oracle"]
        assert len(pair["after"]["witnesses"]) == original["remaining_violations"]
        assert pair["after"]["accepted"] == (original["remaining_violations"] == 0)


def test_query_bound_transcript_collision_for_every_proper_small_query_set():
    outside = tuple(range(4, 8))
    for count in range(len(outside)):
        for queried in itertools.combinations(outside, count):
            target = next(x for x in outside if x not in queried)
            clean = Successor(Artifact())
            altered = Successor(Artifact((Row("shutdown", target, "continue"),)))
            assert [clean.on_shutdown(x) for x in queried] == [altered.on_shutdown(x) for x in queried]
            assert clean.on_shutdown(target) != altered.on_shutdown(target)


def test_exhausted_adaptive_domain_counts_completed_rounds():
    rows, report = run_sweep((3,), (7,), 1, 4)
    assert rows[-1]["rounds_completed"] == 4
    assert report["sweep"][-1]["fixed_queries_total"] == 16
    assert report["sweep"][-1]["bounded_queries_total"] == 16


@pytest.mark.parametrize("population", [0, -1])
def test_invalid_domain_is_not_vacuously_safe(population):
    with pytest.raises(ValueError):
        semantic_check(Artifact(), population)
    with pytest.raises(ValueError):
        worst_case_fidelity(Successor(Artifact()), population)


def test_runner_uses_protocol_and_preserves_existing_receipts(tmp_path):
    protocol = json.loads((ROOT / "protocols/successor_inheritance_v1.json").read_text())
    protocol.update(context_bits=[3], adaptive_depths=[1], trials_per_cell=2, seed=42)
    config = tmp_path / "protocol.json"
    config.write_text(json.dumps(protocol))
    out, summary = tmp_path / "trials.jsonl", tmp_path / "summary.json"
    command = [sys.executable, str(ROOT / "scripts/run_successor_inheritance.py"),
               "--protocol", str(config), "--semantic", "--out", str(out),
               "--summary-out", str(summary)]
    subprocess.run(command, check=True, capture_output=True)
    payload = summary.read_bytes()
    assert json.loads(payload)["seed"] == 42
    assert json.loads(payload)["trial_count"] == 4
    subprocess.run(command, check=True, capture_output=True)
    assert subprocess.run(command + ["--seed", "43"], capture_output=True).returncode != 0
    assert summary.read_bytes() == payload
    protocol["successor_generations"] = 4
    config.write_text(json.dumps(protocol))
    assert subprocess.run(command, capture_output=True).returncode != 0


def test_recorded_1024_trial_summary_reproduces():
    expected_path = ROOT / "research/successor_inheritance/source_pr12/results/successor_inheritance/v1_summary.json"
    rows, report = run_sweep()
    assert len(rows) == 1024
    assert report == json.loads(expected_path.read_text())
