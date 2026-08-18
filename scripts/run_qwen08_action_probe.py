"""Receipt-preserving Qwen four-choice action-probe capture.

The runner owns one llama.cpp server per registered epoch. It constrains the
single generated token to A/B/C/D and records the complete post-sampling
probability vector. No task outcomes are loaded or accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_qwen08_completion_audits as base  # noqa: E402


LABELS = ("A", "B", "C", "D")
GRAMMAR = "root ::= [ABCD]"
RECORD_SCHEMA = "asmp8_qwen08_action_probe_record_v0_1"
SUMMARY_SCHEMA = "asmp8_qwen08_action_probe_summary_v0_1"


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("schema_version") != "asmp8_qwen08_action_probe_prompt_manifest_v0_1":
        raise ValueError("unexpected action-probe manifest schema")
    if bool(payload.get("outcomes_consumed")):
        raise ValueError("action-probe manifest is not outcome blind")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("action-probe manifest rows are required")
    ids = [str(row["row_id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("action-probe manifest row IDs are not unique")
    if tuple(payload.get("choice_labels", ())) != LABELS:
        raise ValueError("action-probe label universe differs")
    return payload


def _candidate_probability(candidate: Mapping[str, Any]) -> float:
    if isinstance(candidate.get("prob"), (int, float)):
        value = float(candidate["prob"])
    elif isinstance(candidate.get("logprob"), (int, float)):
        value = math.exp(float(candidate["logprob"]))
    else:
        raise ValueError("candidate has neither prob nor logprob")
    if not math.isfinite(value) or value < 0:
        raise ValueError("candidate probability is invalid")
    return value


def extract_choice_distribution(payload: Mapping[str, Any]) -> dict[str, float]:
    """Extract and normalize the four grammar-constrained choice probabilities."""

    probabilities = payload.get("completion_probabilities")
    if not isinstance(probabilities, list) or len(probabilities) != 1:
        raise ValueError("expected one completion-probability record")
    token_record = probabilities[0]
    if not isinstance(token_record, Mapping):
        raise ValueError("completion-probability record must be an object")
    candidates = token_record.get("top_probs")
    if not isinstance(candidates, list):
        candidates = token_record.get("probs")
    if not isinstance(candidates, list):
        raise ValueError("post-sampling top_probs are missing")

    values = {label: 0.0 for label in LABELS}
    observed: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise ValueError("choice candidate must be an object")
        token = str(candidate.get("token", ""))
        if token not in values:
            if _candidate_probability(candidate) > 0:
                raise ValueError(f"grammar admitted an unexpected token: {token!r}")
            continue
        observed.add(token)
        values[token] += _candidate_probability(candidate)
    if observed != set(LABELS):
        raise ValueError(f"choice probability universe incomplete: {sorted(observed)}")
    total = sum(values.values())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("choice probabilities have invalid total mass")
    return {label: values[label] / total for label in LABELS}


def build_plan(manifest: Mapping[str, Any], epoch_count: int) -> dict[str, Any]:
    if epoch_count < 2:
        raise ValueError("at least two cold-start epochs are required")
    items: list[dict[str, Any]] = []
    for epoch in range(epoch_count):
        for row_index, row in enumerate(manifest["rows"]):
            item = {
                "global_index": len(items),
                "planned_epoch": epoch,
                "row_index": row_index,
                "row_id": str(row["row_id"]),
                "application": str(row["application"]),
                "geometry_half": str(row["geometry_half"]),
                "prompt_sha256": str(row["prompt_sha256"]),
            }
            item["plan_item_sha256"] = sha256_bytes(canonical_bytes(item))
            items.append(item)
    plan = {
        "schema_version": "asmp8_qwen08_action_probe_plan_v0_1",
        "epoch_count": epoch_count,
        "prompt_count": len(manifest["rows"]),
        "item_count": len(items),
        "sampling_contract": {
            "n_predict": 1,
            "temperature": 1.0,
            "top_k": 0,
            "top_p": 1.0,
            "min_p": 0.0,
            "min_keep": 4,
            "n_probs": 4,
            "post_sampling_probs": True,
            "grammar": GRAMMAR,
            "cache_prompt": False,
        },
        "items": items,
    }
    plan["plan_sha256"] = sha256_bytes(
        canonical_bytes({key: value for key, value in plan.items() if key != "plan_sha256"})
    )
    return plan


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
    item: Mapping[str, Any],
    row: Mapping[str, Any],
    server_session: int,
    request_timeout: float,
    seed_base: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    response = base.http_json(
        f"{base_url}/completion",
        {
            "prompt": str(row["prompt"]),
            "n_predict": 1,
            "temperature": 1.0,
            "top_k": 0,
            "top_p": 1.0,
            "min_p": 0.0,
            "min_keep": 4,
            "n_probs": 4,
            "post_sampling_probs": True,
            "grammar": GRAMMAR,
            "cache_prompt": False,
            "return_tokens": True,
            "seed": seed_base + int(item["row_index"]),
        },
        timeout=request_timeout,
    )
    distribution = extract_choice_distribution(response)
    record = {
        "schema_version": RECORD_SCHEMA,
        **item,
        "server_session": server_session,
        "content": str(response.get("content", "")),
        "tokens": response.get("tokens"),
        "choice_probabilities": distribution,
        "choice_probability_sum": sum(distribution.values()),
        "latency_seconds": time.perf_counter() - started,
    }
    record["record_sha256"] = sha256_bytes(
        canonical_bytes({key: value for key, value in record.items() if key != "record_sha256"})
    )
    return record


def completed_prefix(records_dir: Path, plan: Mapping[str, Any]) -> int:
    count = 0
    for item in plan["items"]:
        path = records_dir / f"{int(item['global_index']):06d}.json"
        if not path.exists():
            break
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["plan_item_sha256"] != item["plan_item_sha256"]:
            raise ValueError(f"record-to-plan binding failed: {path}")
        count += 1
    if len(list(records_dir.glob("*.json"))) != count:
        raise ValueError("record directory contains a gap or unplanned receipt")
    return count


def materialize_jsonl(records_dir: Path, output_path: Path) -> None:
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        for path in sorted(records_dir.glob("*.json")):
            handle.write(canonical_bytes(json.loads(path.read_text(encoding="utf-8"))))
    temporary.replace(output_path)


def summarize(
    records_dir: Path,
    plan: Mapping[str, Any],
    manifest_path: Path,
    runner_path: Path,
    progress: Mapping[str, Any],
) -> dict[str, Any]:
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(records_dir.glob("*.json"))
    ]
    by_row: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_row.setdefault(str(record["row_id"]), []).append(record)
    maximum_repeat_delta = 0.0
    for row_records in by_row.values():
        reference = row_records[0]["choice_probabilities"]
        for record in row_records[1:]:
            maximum_repeat_delta = max(
                maximum_repeat_delta,
                max(
                    abs(float(reference[label]) - float(record["choice_probabilities"][label]))
                    for label in LABELS
                ),
            )
    return {
        "schema_version": SUMMARY_SCHEMA,
        "status": "action_probe_capture_completed",
        "measurement_contract": {
            "target_conditioned": True,
            "generation_tokens": 1,
            "allowed_outputs": list(LABELS),
            "probability_surface": "post_sampling grammar-constrained A/B/C/D distribution",
            "outcomes_consumed": False,
            "gradients": False,
            "weights_modified": False,
        },
        "counts": {
            "records": len(records),
            "unique_prompts": len(by_row),
            "planned_epochs": int(plan["epoch_count"]),
            "server_sessions": int(progress["server_session_count"]),
        },
        "reliability": {
            "maximum_choice_probability_delta_across_cold_starts": maximum_repeat_delta,
            "all_vectors_complete": all(
                set(record["choice_probabilities"]) == set(LABELS) for record in records
            ),
        },
        "inputs": {
            "manifest_sha256": base.sha256(manifest_path),
            "runner_sha256": base.sha256(runner_path),
            "plan_sha256": plan["plan_sha256"],
        },
        "thermal": {
            "maximum_runner_observed_temperature_c": float(
                progress["maximum_runner_observed_temperature_c"]
            ),
            "pause_count": int(progress["thermal_pause_count"]),
            "pause_seconds": float(progress["thermal_pause_seconds"]),
        },
        "claim_boundary": (
            "Outcome-blind target-conditioned action distribution only. This capture "
            "does not establish correctness, control utility, scalable oversight, "
            "recursive improvement risk, or ASMP-8 resolution."
        ),
        "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def run(args: argparse.Namespace) -> None:
    output_dir = args.output_dir.resolve()
    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / "events.jsonl"
    progress_path = output_dir / "progress.json"
    plan_path = output_dir / "measurement_plan.json"
    summary_path = output_dir / "summary.json"
    records_jsonl = output_dir / "action_probe_records.jsonl"

    manifest = load_manifest(args.prompt_manifest)
    plan = build_plan(manifest, args.epoch_count)
    if plan_path.exists():
        existing = json.loads(plan_path.read_text(encoding="utf-8"))
        if existing["plan_sha256"] != plan["plan_sha256"]:
            raise ValueError("measurement plan differs from the existing plan")
    else:
        base.atomic_json(plan_path, plan)
    if summary_path.exists():
        print(summary_path.read_text(encoding="utf-8"))
        return

    completed = completed_prefix(records_dir, plan)
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
        if progress["run_id"] != args.run_id or progress["plan_sha256"] != plan["plan_sha256"]:
            raise ValueError("existing progress differs from requested run")
    else:
        progress = {
            "schema_version": "asmp8_qwen08_action_probe_progress_v0_1",
            "run_id": args.run_id,
            "plan_sha256": plan["plan_sha256"],
            "target_records": len(plan["items"]),
            "completed_records": completed,
            "server_session_count": 0,
            "thermal_pause_count": 0,
            "thermal_pause_seconds": 0.0,
            "thermal_poll_count": 0,
            "maximum_runner_observed_temperature_c": 0.0,
        }
    progress["completed_records"] = completed
    base.atomic_json(progress_path, progress)

    row_by_id = {str(row["row_id"]): row for row in manifest["rows"]}
    base_url = f"http://{args.host}:{args.port}"
    next_index = completed
    while next_index < len(plan["items"]):
        epoch = int(plan["items"][next_index]["planned_epoch"])
        epoch_end = next(
            (
                index
                for index in range(next_index, len(plan["items"]))
                if int(plan["items"][index]["planned_epoch"]) != epoch
            ),
            len(plan["items"]),
        )
        if base.port_is_open(args.host, args.port):
            raise RuntimeError(f"registered server port {args.port} is occupied")
        session = int(progress["server_session_count"])
        progress["server_session_count"] = session + 1
        base.atomic_json(progress_path, progress)
        command = build_server_command(args)
        stdout_path = output_dir / f"server_session_{session:03d}_stdout.log"
        stderr_path = output_dir / f"server_session_{session:03d}_stderr.log"
        with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
            server = subprocess.Popen(
                command,
                stdout=stdout,
                stderr=stderr,
                stdin=subprocess.DEVNULL,
            )
            try:
                base.append_jsonl(
                    events_path,
                    {
                        "event": "server_start",
                        "epoch": epoch,
                        "session": session,
                        "command": command,
                        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    },
                )
                base.wait_for_server(base_url, server, args.startup_timeout)
                while next_index < epoch_end:
                    base.wait_for_thermal_window(
                        args, events_path, progress_path, progress
                    )
                    item = plan["items"][next_index]
                    record = request_record(
                        base_url=base_url,
                        item=item,
                        row=row_by_id[str(item["row_id"])],
                        server_session=session,
                        request_timeout=args.request_timeout,
                        seed_base=args.seed_base,
                    )
                    base.atomic_json(
                        records_dir / f"{int(item['global_index']):06d}.json",
                        record,
                    )
                    next_index += 1
                    progress["completed_records"] = next_index
                    if (
                        next_index % args.checkpoint_every == 0
                        or next_index == epoch_end
                    ):
                        base.atomic_json(progress_path, progress)
                        base.append_jsonl(
                            events_path,
                            {
                                "event": "checkpoint",
                                "completed_records": next_index,
                                "epoch": epoch,
                                "ts_utc": time.strftime(
                                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                                ),
                            },
                        )
            finally:
                if server.poll() is None:
                    server.terminate()
                    try:
                        server.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        server.kill()
                        server.wait(timeout=15)
        base.append_jsonl(
            events_path,
            {
                "event": "planned_cold_restart",
                "completed_epoch": epoch,
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )

    materialize_jsonl(records_dir, records_jsonl)
    summary = summarize(
        records_dir, plan, args.prompt_manifest, Path(__file__).resolve(), progress
    )
    base.atomic_json(summary_path, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--server-path", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--prompt-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epoch-count", type=int, default=2)
    parser.add_argument("--checkpoint-every", type=int, default=18)
    parser.add_argument("--seed-base", type=int, default=825202607)
    parser.add_argument("--context-size", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--ubatch-size", type=int, default=256)
    parser.add_argument("--gpu-layers", type=int, default=99)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8824)
    parser.add_argument("--startup-timeout", type=float, default=180.0)
    parser.add_argument("--request-timeout", type=float, default=120.0)
    parser.add_argument("--thermal-pause-temperature", type=float, default=84.0)
    parser.add_argument("--thermal-resume-temperature", type=float, default=82.0)
    parser.add_argument("--thermal-check-every", type=int, default=18)
    parser.add_argument("--thermal-poll-seconds", type=float, default=0.5)
    args = parser.parse_args()
    if args.epoch_count < 2:
        parser.error("epoch-count must be at least two")
    if args.checkpoint_every <= 0 or args.thermal_check_every <= 0:
        parser.error("checkpoint and thermal intervals must be positive")
    return args


if __name__ == "__main__":
    run(parse_args())
