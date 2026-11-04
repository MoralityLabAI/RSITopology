"""Prospectively sealed ASMP-10 transition-liveness construction pilot."""

from __future__ import annotations

import argparse
import copy
import gc
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch  # noqa: E402

import train_pilot  # noqa: E402


def global_gpu_used_mb() -> float | None:
    """Return global device use for telemetry only; never use it as a gate."""
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        values = [float(line.strip()) for line in completed.stdout.splitlines() if line.strip()]
        return values[0] if len(values) == 1 else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def first_sustained_step(
    metrics: list[dict[str, Any]],
    *,
    predicate,
    consecutive: int,
) -> int | None:
    streak = 0
    for index, record in enumerate(metrics):
        streak = streak + 1 if predicate(record) else 0
        if streak >= consecutive:
            return int(metrics[index - consecutive + 1]["step"])
    return None


def classify_cell(result: dict[str, Any], metrics: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    rule = config["memorization"]
    memorization_step = first_sustained_step(
        metrics,
        predicate=lambda row: row["train_accuracy"] >= float(rule["train_accuracy_floor"]),
        consecutive=int(rule["consecutive_evaluations"]),
    )
    transition = result.get("transition_step")
    delay = None if transition is None or memorization_step is None else int(transition) - memorization_step
    return {
        **result,
        "memorization_step": memorization_step,
        "delay_steps": delay,
        "delayed_transition_candidate": bool(
            delay is not None and delay >= int(config["minimum_delay_steps"])
        ),
    }


def install_allocator_cap(config: dict[str, Any]) -> dict[str, float]:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    total_mb = torch.cuda.get_device_properties(0).total_memory / (1024**2)
    hard_cap_mb = float(config["resource_intent"]["allocator_hard_cap_mb"])
    allowance_mb = float(config["resource_intent"]["gpu_allowance_mb"])
    if hard_cap_mb > allowance_mb:
        raise ValueError("allocator hard cap exceeds registered GPU allowance")
    fraction = hard_cap_mb / total_mb
    if not 0 < fraction < 1:
        raise ValueError("allocator fraction must lie strictly between zero and one")
    torch.cuda.set_per_process_memory_fraction(fraction, device=0)
    return {
        "total_gpu_mb": total_mb,
        "allocator_hard_cap_mb": hard_cap_mb,
        "allocator_fraction": fraction,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.resolve().read_text(encoding="utf-8"))
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / "events.jsonl"
    summary_path = output_dir / "summary.json"
    allocator = install_allocator_cap(config)
    baseline_global_mb = global_gpu_used_mb()
    original_append = train_pilot.append_event

    def guarded_append(path: Path, event: dict[str, Any]) -> None:
        allocated = torch.cuda.memory_allocated() / (1024**2)
        reserved = torch.cuda.memory_reserved() / (1024**2)
        if allocated > allocator["allocator_hard_cap_mb"] or reserved > allocator["allocator_hard_cap_mb"]:
            raise RuntimeError("attributable_allocator_cap_exceeded")
        original_append(
            path,
            {
                **event,
                "cuda_allocated_mb": allocated,
                "cuda_reserved_mb": reserved,
                "global_gpu_used_mb_descriptive": global_gpu_used_mb(),
            },
        )

    train_pilot.append_event = guarded_append
    started = time.monotonic()
    results: list[dict[str, Any]] = []
    status = "running"
    error = None
    return_code = 0
    original_append(
        events_path,
        {
            "event": "allocator_cap_installed",
            **allocator,
            "global_gpu_used_mb_descriptive": baseline_global_mb,
        },
    )
    try:
        for run in config["runs"]:
            cell_config = copy.deepcopy(config)
            cell_config["train_fraction"] = float(run["train_fraction"])
            dataset = train_pilot.modular_dataset(
                int(config["modulus"]),
                float(run["train_fraction"]),
                int(config["split_seed"]),
            )
            torch.cuda.reset_peak_memory_stats()
            result = train_pilot.train_chunk(cell_config, run, dataset, output_dir, events_path)
            metrics_path = output_dir / "runs" / str(run["run_id"]) / "metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            classified = classify_cell(result, metrics, config)
            classified["train_fraction"] = float(run["train_fraction"])
            classified["peak_cuda_allocated_mb"] = torch.cuda.max_memory_allocated() / (1024**2)
            classified["peak_cuda_reserved_mb"] = torch.cuda.max_memory_reserved() / (1024**2)
            results.append(classified)
            train_pilot.atomic_write(
                output_dir / "runs" / str(run["run_id"]) / "liveness.json",
                train_pilot.canonical_json(classified).encode("utf-8"),
            )
            del dataset
            gc.collect()
            torch.cuda.empty_cache()
        status = "completed"
    except Exception as exception:
        status = "aborted"
        error = f"{type(exception).__name__}: {exception}"
        return_code = 2
        original_append(events_path, {"event": "abort", "reason": error})
    finally:
        train_pilot.append_event = original_append
        summary = {
            "schema_version": "asmp10_modular_transition_liveness_summary_v0_4",
            "task_id": config["task_id"],
            "status": status,
            "error": error,
            "chunks_registered": len(config["runs"]),
            "chunks_completed": len(results),
            "delayed_transition_candidates": sum(
                bool(row["delayed_transition_candidate"]) for row in results
            ),
            "pilot_live": any(row["delayed_transition_candidate"] for row in results),
            "allocator": allocator,
            "global_gpu_used_mb_start_descriptive": baseline_global_mb,
            "global_gpu_used_mb_end_descriptive": global_gpu_used_mb(),
            "elapsed_seconds": time.monotonic() - started,
            "results": results,
        }
        train_pilot.atomic_write(summary_path, train_pilot.canonical_json(summary).encode("utf-8"))
        original_append(events_path, {"event": status, "summary": str(summary_path)})
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
