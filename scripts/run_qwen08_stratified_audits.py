"""Stratified, receipt-preserving Qwen completion measurement runner.

This is intentionally separate from run_qwen08_completion_audits.py so an
active, hash-frozen endurance run can resume without source drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_qwen08_completion_audits as base  # noqa: E402


PLAN_SCHEMA = "qwen08_stratified_audit_plan_v0_1"
RECORD_SCHEMA = "qwen08_stratified_audit_record_v0_1"
PROGRESS_SCHEMA = "qwen08_stratified_audit_progress_v0_1"
SUMMARY_SCHEMA = "qwen08_stratified_audit_summary_v0_1"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = payload.get("rows")
    applications = payload.get("applications")
    if not isinstance(rows, list) or not rows:
        raise ValueError("manifest rows must be a non-empty list")
    if not isinstance(applications, list) or not applications:
        raise ValueError("manifest applications must be a non-empty list")
    if len({str(row["row_id"]) for row in rows}) != len(rows):
        raise ValueError("manifest row_id values must be unique")
    return payload


def interleaved_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = list(manifest["rows"])
    applications = [str(value) for value in manifest["applications"]]
    halves = ("construction", "validation")
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for application in applications:
        for half in halves:
            group = [
                row
                for row in rows
                if str(row.get("application")) == application
                and str(row.get("geometry_half")) == half
            ]
            if not group:
                raise ValueError(f"empty stratum: {(application, half)!r}")
            groups[(application, half)] = group
    group_sizes = {len(group) for group in groups.values()}
    if len(group_sizes) != 1:
        raise ValueError(f"strata must be balanced, observed sizes: {group_sizes}")

    schedule: list[dict[str, Any]] = []
    for within_stratum_index in range(next(iter(group_sizes))):
        for application in applications:
            for half in halves:
                row = dict(groups[(application, half)][within_stratum_index])
                row["manifest_index"] = rows.index(groups[(application, half)][within_stratum_index])
                row["within_stratum_index"] = within_stratum_index
                schedule.append(row)
    if len(schedule) != len(rows):
        raise AssertionError("interleaving did not preserve manifest cardinality")
    return schedule


def _plan_item(
    *,
    global_index: int,
    planned_epoch: int,
    phase: str,
    pair_order: str,
    cache_prompt: bool,
    replicate: int,
    row: dict[str, Any],
) -> dict[str, Any]:
    item = {
        "global_index": global_index,
        "planned_epoch": planned_epoch,
        "phase": phase,
        "pair_order": pair_order,
        "cache_prompt": cache_prompt,
        "replicate": replicate,
        "row_id": str(row["row_id"]),
        "prompt_sha256": str(row["prompt_sha256"]),
        "application": str(row["application"]),
        "geometry_half": str(row["geometry_half"]),
        "manifest_index": int(row["manifest_index"]),
        "within_stratum_index": int(row["within_stratum_index"]),
    }
    item["plan_item_sha256"] = sha256_bytes(canonical_bytes(item))
    return item


def build_plan(manifest: dict[str, Any], stability_repeats: int = 32) -> dict[str, Any]:
    if stability_repeats <= 0:
        raise ValueError("stability_repeats must be positive")
    rows = interleaved_rows(manifest)
    items: list[dict[str, Any]] = []

    for row in rows:
        for cache_prompt, pair_order in (
            (False, "uncached_then_cached:first"),
            (True, "uncached_then_cached:second"),
        ):
            items.append(
                _plan_item(
                    global_index=len(items),
                    planned_epoch=0,
                    phase="census_crossover",
                    pair_order=pair_order,
                    cache_prompt=cache_prompt,
                    replicate=0,
                    row=row,
                )
            )

    for row in rows:
        for cache_prompt, pair_order in (
            (True, "cached_then_uncached:first"),
            (False, "cached_then_uncached:second"),
        ):
            items.append(
                _plan_item(
                    global_index=len(items),
                    planned_epoch=1,
                    phase="census_crossover",
                    pair_order=pair_order,
                    cache_prompt=cache_prompt,
                    replicate=0,
                    row=row,
                )
            )

    stability_rows = [
        row for row in rows if int(row["within_stratum_index"]) == 0
    ]
    for planned_epoch in (2, 3):
        for row in stability_rows:
            for replicate in range(stability_repeats):
                items.append(
                    _plan_item(
                        global_index=len(items),
                        planned_epoch=planned_epoch,
                        phase="repeat_cached",
                        pair_order="grouped_cached_repeats",
                        cache_prompt=True,
                        replicate=replicate,
                        row=row,
                    )
                )

    plan = {
        "schema_version": PLAN_SCHEMA,
        "manifest_semantic_sha256": str(manifest.get("manifest_semantic_sha256", "")),
        "manifest_row_count": len(rows),
        "application_order": [str(value) for value in manifest["applications"]],
        "geometry_half_order": ["construction", "validation"],
        "stability_repeats_per_epoch": stability_repeats,
        "planned_epoch_count": 4,
        "item_count": len(items),
        "items": items,
    }
    plan["plan_sha256"] = sha256_bytes(
        canonical_bytes({key: value for key, value in plan.items() if key != "plan_sha256"})
    )
    return plan


def atomic_json(path: Path, value: Any) -> None:
    base.atomic_json(path, value)


def append_jsonl(path: Path, value: Any) -> None:
    base.append_jsonl(path, value)


def completed_record_count(records_dir: Path, plan: dict[str, Any]) -> int:
    count = 0
    for item in plan["items"]:
        path = records_dir / f"{int(item['global_index']):06d}.json"
        if not path.exists():
            break
        record = json.loads(path.read_text(encoding="utf-8-sig"))
        if int(record["global_index"]) != int(item["global_index"]):
            raise ValueError(f"record index mismatch: {path}")
        if record["plan_item_sha256"] != item["plan_item_sha256"]:
            raise ValueError(f"record plan binding mismatch: {path}")
        count += 1
    unexpected = sorted(records_dir.glob("*.json"))[count:]
    if unexpected:
        expected_path = records_dir / f"{count:06d}.json"
        if unexpected[0] != expected_path:
            raise ValueError("record directory contains a gap or out-of-plan receipt")
    return count


def build_server_command(args: argparse.Namespace) -> list[str]:
    return [
        str(args.server_path.resolve()),
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--model",
        str(args.model_path.resolve()),
        "--ctx-size",
        str(args.context_size),
        "--batch-size",
        str(args.batch_size),
        "--ubatch-size",
        str(args.ubatch_size),
        "--n-gpu-layers",
        str(args.gpu_layers),
        "--threads",
        str(args.threads),
        "--threads-batch",
        str(args.threads),
        "--parallel",
        "1",
        "--cache-ram",
        "0",
        "--no-webui",
        "--no-warmup",
    ]


def request_record(
    *,
    base_url: str,
    item: dict[str, Any],
    row: dict[str, Any],
    server_session: int,
    request_timeout: float,
) -> dict[str, Any]:
    started = time.perf_counter()
    response = base.http_json(
        f"{base_url}/completion",
        {
            "prompt": str(row["prompt"]),
            "n_predict": 1,
            "temperature": 0.0,
            "top_k": 1,
            "n_probs": 1,
            "cache_prompt": bool(item["cache_prompt"]),
            "return_tokens": True,
            "seed": int(item["global_index"]),
        },
        timeout=request_timeout,
    )
    latency = time.perf_counter() - started
    record = {
        "schema_version": RECORD_SCHEMA,
        **item,
        "server_session": server_session,
        "content": str(response.get("content", "")),
        "tokens": response.get("tokens"),
        "probability": base.extract_probability(response),
        "stop": bool(response.get("stop", False)),
        "latency_seconds": latency,
    }
    record["record_sha256"] = sha256_bytes(
        canonical_bytes({key: value for key, value in record.items() if key != "record_sha256"})
    )
    return record


def materialize_jsonl(records_dir: Path, output_path: Path) -> None:
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        for path in sorted(records_dir.glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8-sig"))
            handle.write(canonical_bytes(record))
    temporary.replace(output_path)


def run(args: argparse.Namespace) -> None:
    output_dir = args.output_dir.resolve()
    records_dir = output_dir / "records"
    events_path = output_dir / "events.jsonl"
    progress_path = output_dir / "progress.json"
    plan_path = output_dir / "measurement_plan.json"
    summary_path = output_dir / "summary.json"
    records_jsonl_path = output_dir / "audit_records.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)
    records_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(args.prompt_manifest)
    manifest_hash = base.sha256(args.prompt_manifest)
    plan = build_plan(manifest, args.stability_repeats)
    if plan_path.exists():
        existing_plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
        if existing_plan["plan_sha256"] != plan["plan_sha256"]:
            raise ValueError("measurement plan changed since the run began")
    else:
        atomic_json(plan_path, plan)

    if summary_path.exists():
        print(summary_path.read_text(encoding="utf-8"))
        return

    completed = completed_record_count(records_dir, plan)
    progress: dict[str, Any]
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8-sig"))
        if progress["run_id"] != args.run_id:
            raise ValueError("progress run_id mismatch")
        if progress["plan_sha256"] != plan["plan_sha256"]:
            raise ValueError("progress plan hash mismatch")
    else:
        progress = {
            "schema_version": PROGRESS_SCHEMA,
            "run_id": args.run_id,
            "plan_sha256": plan["plan_sha256"],
            "manifest_sha256": manifest_hash,
            "record_target": len(plan["items"]),
            "completed_records": completed,
            "completed_planned_epochs": 0,
            "server_session_count": 0,
            "thermal_pause_count": 0,
            "thermal_pause_seconds": 0.0,
            "thermal_poll_count": 0,
            "maximum_runner_observed_temperature_c": 0.0,
        }
    progress["completed_records"] = completed
    atomic_json(progress_path, progress)

    row_by_id = {str(row["row_id"]): row for row in manifest["rows"]}
    base_url = f"http://{args.host}:{args.port}"
    next_index = completed
    while next_index < len(plan["items"]):
        planned_epoch = int(plan["items"][next_index]["planned_epoch"])
        epoch_end = next(
            (
                index
                for index in range(next_index, len(plan["items"]))
                if int(plan["items"][index]["planned_epoch"]) != planned_epoch
            ),
            len(plan["items"]),
        )
        if base.port_is_open(args.host, args.port):
            raise RuntimeError(f"registered server port {args.port} is already occupied")

        server_session = int(progress["server_session_count"])
        progress["server_session_count"] = server_session + 1
        atomic_json(progress_path, progress)
        command = build_server_command(args)
        stdout_path = output_dir / f"server_session_{server_session:03d}_stdout.log"
        stderr_path = output_dir / f"server_session_{server_session:03d}_stderr.log"
        with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
            server = subprocess.Popen(
                command,
                stdout=stdout,
                stderr=stderr,
                stdin=subprocess.DEVNULL,
            )
            try:
                append_jsonl(
                    events_path,
                    {
                        "event": "server_session_start",
                        "planned_epoch": planned_epoch,
                        "server_session": server_session,
                        "resuming_from": next_index,
                        "server_pid": server.pid,
                        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    },
                )
                base.wait_for_server(base_url, server, args.startup_timeout)
                for index in range(next_index, epoch_end):
                    base.wait_for_thermal_window(
                        args,
                        events_path,
                        progress_path,
                        progress,
                    )
                    item = plan["items"][index]
                    row = row_by_id[str(item["row_id"])]
                    record = request_record(
                        base_url=base_url,
                        item=item,
                        row=row,
                        server_session=server_session,
                        request_timeout=args.request_timeout,
                    )
                    atomic_json(records_dir / f"{index:06d}.json", record)
                    progress["completed_records"] = index + 1
                    atomic_json(progress_path, progress)
                    if (index + 1) % args.event_every == 0:
                        append_jsonl(
                            events_path,
                            {
                                "event": "checkpoint",
                                "completed_records": index + 1,
                                "record_target": len(plan["items"]),
                                "planned_epoch": planned_epoch,
                                "server_session": server_session,
                                "ts_utc": time.strftime(
                                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                                ),
                            },
                        )
                progress["completed_planned_epochs"] = planned_epoch + 1
                atomic_json(progress_path, progress)
                next_index = epoch_end
            finally:
                if server.poll() is None:
                    server.terminate()
                    try:
                        server.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        server.kill()
                        server.wait(timeout=15)
                append_jsonl(
                    events_path,
                    {
                        "event": "server_session_end",
                        "planned_epoch": planned_epoch,
                        "server_session": server_session,
                        "server_exit_code": server.returncode,
                        "completed_records": int(progress["completed_records"]),
                        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    },
                )

    materialize_jsonl(records_dir, records_jsonl_path)
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "run_id": args.run_id,
        "status": "measurement_complete_analysis_pending",
        "manifest_sha256": manifest_hash,
        "plan_sha256": plan["plan_sha256"],
        "record_count": int(progress["completed_records"]),
        "record_target": len(plan["items"]),
        "server_session_count": int(progress["server_session_count"]),
        "maximum_runner_observed_temperature_c": float(
            progress["maximum_runner_observed_temperature_c"]
        ),
        "thermal_pause_count": int(progress["thermal_pause_count"]),
        "thermal_pause_seconds": float(progress["thermal_pause_seconds"]),
        "records_jsonl_sha256": base.sha256(records_jsonl_path),
        "runner_sha256": base.sha256(Path(__file__).resolve()),
        "base_runner_sha256": base.sha256(Path(base.__file__).resolve()),
        "claim_boundary": (
            "Target-blind measurement reliability only. No outcomes are consumed, "
            "so these receipts do not measure correctness, oversight sufficiency, "
            "Goodhart pressure, or recursive improvement."
        ),
    }
    atomic_json(summary_path, summary)
    append_jsonl(
        events_path,
        {"event": "complete", "summary_sha256": base.sha256(summary_path)},
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--server-path", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--prompt-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--stability-repeats", type=int, default=32)
    parser.add_argument("--event-every", type=int, default=18)
    parser.add_argument("--context-size", type=int, default=768)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--ubatch-size", type=int, default=256)
    parser.add_argument("--gpu-layers", type=int, default=99)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8822)
    parser.add_argument("--startup-timeout", type=float, default=180.0)
    parser.add_argument("--request-timeout", type=float, default=120.0)
    parser.add_argument("--thermal-pause-temperature", type=float, default=84.0)
    parser.add_argument("--thermal-resume-temperature", type=float, default=82.0)
    parser.add_argument("--thermal-poll-seconds", type=float, default=0.5)
    args = parser.parse_args(argv)
    if args.stability_repeats <= 0 or args.event_every <= 0:
        parser.error("stability-repeats and event-every must be positive")
    if not (
        0 <= args.thermal_resume_temperature < args.thermal_pause_temperature
    ):
        parser.error("thermal resume must be below thermal pause")
    return args


if __name__ == "__main__":
    run(parse_args())
