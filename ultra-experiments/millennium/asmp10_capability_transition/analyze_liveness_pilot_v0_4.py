"""Independently validate and summarize the completed ASMP-10 v0.4 pilot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ARTIFACTS = HERE / "pilot_artifacts_v0_4"


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def first_sustained_step(
    metrics: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool], consecutive: int
) -> int | None:
    streak = 0
    for index, row in enumerate(metrics):
        streak = streak + 1 if predicate(row) else 0
        if streak >= consecutive:
            return int(metrics[index - consecutive + 1]["step"])
    return None


def terminal_stable_step(
    metrics: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool], minimum_tail: int
) -> int | None:
    for index, row in enumerate(metrics):
        tail = metrics[index:]
        if len(tail) >= minimum_tail and all(predicate(item) for item in tail):
            return int(row["step"])
    return None


def event_rows() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (ARTIFACTS / "events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def manifest_files() -> list[Path]:
    fixed = [
        HERE / ".gitattributes",
        HERE / "README.md",
        HERE / "LIVENESS_PILOT_PLAN_v0_4.md",
        HERE / "LIVENESS_PILOT_RESULT_v0_4.md",
        HERE / "PREDICTOR_PROTOCOL_DRAFT_v0_5.md",
        HERE / "analyze_liveness_pilot_v0_4.py",
        HERE / "test_analyze_liveness_pilot_v0_4.py",
        HERE / "pilot_liveness_config_v0_4.json",
        HERE / "pilot_liveness_authorization_v0_4.json",
        HERE / "pilot_liveness_continuation_authorization_v0_4a.json",
        HERE / "pilot_liveness_continuation_authorization_v0_4b.json",
        HERE / "pilot_liveness_continuation_authorization_v0_4c.json",
        HERE / "pilot_liveness_continuation_authorization_v0_4d.json",
        HERE / "train_pilot.py",
        HERE / "train_liveness_pilot_v0_4.py",
        HERE / "resume_liveness_pilot_v0_4b.py",
        HERE / "resume_liveness_pilot_v0_4c.py",
        ARTIFACTS / "summary.json",
        ARTIFACTS / "events.jsonl",
    ]
    run_files: list[Path] = []
    for run_dir in sorted((ARTIFACTS / "runs").iterdir()):
        run_files.extend(run_dir / name for name in ("completed.json", "liveness.json", "metrics.json"))
    wrapper_files: list[Path] = []
    for wrapper in sorted(HERE.glob("pilot_wrapper_v0_4*")):
        wrapper_files.extend(sorted(path for path in wrapper.iterdir() if path.is_file()))
    return fixed + run_files + wrapper_files


def main() -> int:
    config = load_json(HERE / "pilot_liveness_config_v0_4.json")
    summary = load_json(ARTIFACTS / "summary.json")
    assert summary["status"] == "completed"
    assert summary["chunks_completed"] == summary["chunks_registered"] == 6
    events = event_rows()
    rows = []
    for registered in config["runs"]:
        run_id = registered["run_id"]
        run_dir = ARTIFACTS / "runs" / run_id
        completed = load_json(run_dir / "completed.json")
        liveness = load_json(run_dir / "liveness.json")
        metrics = load_json(run_dir / "metrics.json")
        assert completed["status"] == "completed"
        assert completed["steps_completed"] == config["steps"] == metrics[-1]["step"]
        assert len(metrics) == 151
        transition_rule = config["transition"]
        qualifies = lambda row: (
            row["test_accuracy"] >= transition_rule["test_accuracy_floor"]
            and row["test_loss"] <= transition_rule["test_loss_ceiling"]
        )
        memory_rule = config["memorization"]
        memorizes = lambda row: row["train_accuracy"] >= memory_rule["train_accuracy_floor"]
        transition = first_sustained_step(
            metrics, qualifies, int(transition_rule["consecutive_evaluations"])
        )
        memorization = first_sustained_step(
            metrics, memorizes, int(memory_rule["consecutive_evaluations"])
        )
        assert transition == completed["transition_step"] == liveness["transition_step"]
        assert memorization == liveness["memorization_step"]
        delay = None if transition is None else transition - memorization
        assert delay == liveness["delay_steps"]
        after = [] if transition is None else [row for row in metrics if row["step"] >= transition]
        failures = [int(row["step"]) for row in after if not qualifies(row)]
        own_events = [row for row in events if row.get("run_id") == run_id]
        rows.append(
            {
                "run_id": run_id,
                "train_fraction": registered["train_fraction"],
                "weight_decay": registered["weight_decay"],
                "memorization_step": memorization,
                "first_sustained_transition_step": transition,
                "delay_steps": delay,
                "delayed_transition_candidate": liveness["delayed_transition_candidate"],
                "post_transition_failure_count": len(failures),
                "last_post_transition_failure_step": failures[-1] if failures else None,
                "terminal_stable_step_min_20_evals": terminal_stable_step(metrics, qualifies, 20),
                "final_train_accuracy": metrics[-1]["train_accuracy"],
                "final_test_accuracy": metrics[-1]["test_accuracy"],
                "final_test_loss": metrics[-1]["test_loss"],
                "early_geometry": completed["geometry"],
                "peak_cuda_allocated_mb_from_events": max(
                    (float(row.get("cuda_allocated_mb", 0.0)) for row in own_events), default=0.0
                ),
                "peak_cuda_reserved_mb_from_events": max(
                    (float(row.get("cuda_reserved_mb", 0.0)) for row in own_events), default=0.0
                ),
            }
        )
    delayed = sum(row["delayed_transition_candidate"] for row in rows)
    wrapper_records = []
    for wrapper in sorted(HERE.glob("pilot_wrapper_v0_4*")):
        record = load_json(wrapper / "wrapper_summary.json")
        wrapper_records.append(
            {
                "segment": wrapper.name,
                "status": record["status"],
                "abort_reason": record["abort_reason"],
                "elapsed_seconds": record["elapsed_seconds"],
                "peak_ram_mb": record["peak_ram_mb"],
                "peak_io_mb_s": record["peak_io_mb_s"],
                "cleanup_passed": record["cleanup_passed"],
            }
        )
    assert all(row["cleanup_passed"] for row in wrapper_records)
    result = {
        "schema_version": "asmp10_liveness_pilot_analysis_v0_4",
        "status": "validated_complete",
        "registered_cells": len(rows),
        "delayed_transition_candidates": delayed,
        "pilot_live": delayed >= 1,
        "frozen_branch_action": (
            "draft_disjoint_seed_predictor_protocol_do_not_run"
            if delayed >= 2
            else "fresh_seed_confirmation_required" if delayed == 1 else "stop_no_live_cell"
        ),
        "terminal_stability_is_posthoc_diagnostic": True,
        "rows": rows,
        "wrapper_segments": wrapper_records,
        "resource_summary": {
            "peak_host_ram_mb": max(row["peak_ram_mb"] for row in wrapper_records),
            "peak_io_mb_s": max(row["peak_io_mb_s"] for row in wrapper_records),
            "peak_cuda_allocated_mb_from_events": max(
                row["peak_cuda_allocated_mb_from_events"] for row in rows
            ),
            "peak_cuda_reserved_mb_from_events": max(
                row["peak_cuda_reserved_mb_from_events"] for row in rows
            ),
        },
    }
    analysis_path = ARTIFACTS / "analysis_v0_4.json"
    analysis_path.write_text(canonical_json(result), encoding="utf-8", newline="\n")
    manifest = {
        path.resolve().relative_to(REPO).as_posix(): sha256(path)
        for path in manifest_files()
    }
    receipt = {
        "schema_version": "asmp10_liveness_pilot_receipt_v0_4",
        "analysis_sha256": sha256(analysis_path),
        "manifest": manifest,
        "manifest_file_count": len(manifest),
        "verification": {
            "all_six_terminal_records_recomputed": True,
            "registered_transition_steps_match": True,
            "registered_memorization_steps_match": True,
            "all_wrapper_cleanup_receipts_pass": True,
            "ignored_checkpoints_excluded_from_release_manifest": True
        }
    }
    (ARTIFACTS / "receipt_v0_4.json").write_text(
        canonical_json(receipt), encoding="utf-8", newline="\n"
    )
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
