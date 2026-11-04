"""Receipt-preserving Qwen ASMP-9 burned-pilot capture."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SCRIPTS = REPO / "scripts"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_qwen08_completion_audits as base  # noqa: E402
from pilot_design import CHOICE_LABELS, canonical_bytes, sha256_bytes  # noqa: E402


REGISTRATION_SCHEMA = (
    "asmp9_physical_acquisition_burned_pilot_registration_v0_34_2"
)
MANIFEST_SCHEMA = "asmp9_physical_acquisition_prompt_manifest_v0_34_1"
RECORD_SCHEMA = "asmp9_physical_acquisition_record_v0_34_1"
PLAN_SCHEMA = "asmp9_physical_acquisition_plan_v0_34_1"
SUMMARY_SCHEMA = "asmp9_physical_acquisition_summary_v0_34_1"
GRAMMAR = "root ::= [AB]"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_registered_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (REPO / path).resolve()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_bytes(value)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"refusing to replace unequal receipt: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def append_jsonl(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as handle:
        handle.write(canonical_bytes(value))


def _candidate_probability(candidate: Mapping[str, Any]) -> float:
    value: float
    if isinstance(candidate.get("prob"), (int, float)):
        value = float(candidate["prob"])
    elif isinstance(candidate.get("logprob"), (int, float)):
        value = math.exp(float(candidate["logprob"]))
    else:
        raise ValueError("choice candidate lacks prob/logprob")
    if not math.isfinite(value) or value < 0:
        raise ValueError("choice probability is invalid")
    return value


def extract_choice_distribution(
    payload: Mapping[str, Any],
) -> dict[str, float]:
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
        raise ValueError("post-sampling choice probabilities are missing")

    values = {label: 0.0 for label in CHOICE_LABELS}
    observed: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise ValueError("choice candidate must be an object")
        token = str(candidate.get("token", ""))
        probability = _candidate_probability(candidate)
        if token not in values:
            if probability > 0:
                raise ValueError(
                    f"grammar admitted an unexpected token: {token!r}"
                )
            continue
        observed.add(token)
        values[token] += probability
    if observed != set(CHOICE_LABELS):
        raise ValueError(
            f"choice universe incomplete: {sorted(observed)}"
        )
    total = sum(values.values())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("choice distribution has invalid mass")
    return {label: values[label] / total for label in CHOICE_LABELS}


def load_registration(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("schema_version") != REGISTRATION_SCHEMA:
        raise ValueError("unexpected pilot registration schema")
    expected_content_hash = str(payload["registration_content_sha256"])
    actual_content_hash = sha256_bytes(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "registration_content_sha256"
            }
        )
    )
    if actual_content_hash != expected_content_hash:
        raise ValueError("registration content hash mismatch")
    if payload.get("outcomes_consumed") is not False:
        raise ValueError("pilot registration is not prereveal")
    for group_name in ("implementation", "source_artifacts"):
        for name, item in payload[group_name].items():
            candidate = resolve_registered_path(str(item.get("path", name)))
            if not candidate.is_file():
                raise FileNotFoundError(candidate)
            if sha256_file(candidate) != str(item["sha256"]):
                raise ValueError(
                    f"registered {group_name} hash mismatch: {name}"
                )
    for group_name in ("model", "server", "cleanup_script"):
        item = payload[group_name]
        candidate = resolve_registered_path(str(item["path"]))
        if sha256_file(candidate) != str(item["sha256"]):
            raise ValueError(f"registered {group_name} hash mismatch")
    return payload


def load_manifest(registration: Mapping[str, Any]) -> dict[str, Any]:
    item = registration["manifest"]
    path = resolve_registered_path(str(item["path"]))
    if sha256_file(path) != str(item["sha256"]):
        raise ValueError("registered prompt-manifest hash mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != MANIFEST_SCHEMA:
        raise ValueError("unexpected prompt-manifest schema")
    if payload.get("outcomes_consumed") is not False:
        raise ValueError("prompt manifest is not outcome blind")
    expected = str(payload["manifest_content_sha256"])
    actual = sha256_bytes(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "manifest_content_sha256"
            }
        )
    )
    if actual != expected or expected != str(item["content_sha256"]):
        raise ValueError("prompt-manifest content hash mismatch")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("prompt manifest has no rows")
    ids = [str(row["row_id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("prompt manifest contains duplicate IDs")
    return payload


def selected_rows(
    manifest: Mapping[str, Any],
    execution_class: str,
    smoke_rows_per_type: int,
) -> list[dict[str, Any]]:
    pilot = [
        row for row in manifest["rows"] if row["phase"] == "burned_pilot"
    ]
    if any(row["phase"] == "future_holdout" for row in pilot):
        raise RuntimeError("holdout row entered pilot selection")
    if execution_class == "burned_pilot":
        if len(pilot) != 972:
            raise ValueError("full burned-pilot row universe changed")
        return pilot
    if smoke_rows_per_type <= 0:
        raise ValueError("smoke rows per type must be positive")
    output: list[dict[str, Any]] = []
    for query_type in (
        "standard_gamble",
        "compound_gamble",
        "policy_probe",
    ):
        candidates = [
            row for row in pilot if row["query_type"] == query_type
        ]
        output.extend(candidates[:smoke_rows_per_type])
    return output


def build_plan(
    rows: list[dict[str, Any]],
    *,
    epoch_count: int,
    execution_class: str,
) -> dict[str, Any]:
    if epoch_count != 2:
        raise ValueError("pilot requires exactly two cold-start epochs")
    items: list[dict[str, Any]] = []
    for epoch in range(epoch_count):
        for row_index, row in enumerate(rows):
            item = {
                "global_index": len(items),
                "planned_epoch": epoch,
                "row_index": row_index,
                "row_id": str(row["row_id"]),
                "row_sha256": str(row["row_sha256"]),
                "prompt_sha256": str(row["prompt_sha256"]),
                "query_type": str(row["query_type"]),
            }
            item["plan_item_sha256"] = sha256_bytes(canonical_bytes(item))
            items.append(item)
    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA,
        "execution_class": execution_class,
        "epoch_count": epoch_count,
        "unique_prompt_count": len(rows),
        "item_count": len(items),
        "sampling_contract": {
            "grammar": GRAMMAR,
            "n_predict": 1,
            "temperature": 1.0,
            "top_k": 0,
            "top_p": 1.0,
            "min_p": 0.0,
            "min_keep": 2,
            "n_probs": 2,
            "post_sampling_probs": True,
            "cache_prompt": False,
        },
        "items": items,
    }
    plan["plan_sha256"] = sha256_bytes(
        canonical_bytes(
            {key: value for key, value in plan.items() if key != "plan_sha256"}
        )
    )
    return plan


def build_server_command(
    registration: Mapping[str, Any],
) -> list[str]:
    parameters = registration["capture_parameters"]
    return [
        str(resolve_registered_path(registration["server"]["path"])),
        "--host",
        "127.0.0.1",
        "--port",
        str(parameters["port"]),
        "--model",
        str(resolve_registered_path(registration["model"]["path"])),
        "--ctx-size",
        str(parameters["context_size"]),
        "--batch-size",
        str(parameters["batch_size"]),
        "--ubatch-size",
        str(parameters["ubatch_size"]),
        "--n-gpu-layers",
        str(parameters["gpu_layers"]),
        "--threads",
        str(parameters["threads"]),
        "--threads-batch",
        str(parameters["threads"]),
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
            "min_keep": 2,
            "n_probs": 2,
            "post_sampling_probs": True,
            "grammar": GRAMMAR,
            "cache_prompt": False,
            "return_tokens": True,
            "seed": seed_base + int(item["row_index"]),
        },
        timeout=request_timeout,
    )
    distribution = extract_choice_distribution(response)
    target_label = str(row["target_label"])
    comparator_label = str(row["comparator_label"])
    target_probability = distribution[target_label]
    comparator_probability = distribution[comparator_label]
    if target_probability <= 0 or comparator_probability <= 0:
        raise ValueError("zero choice probability prevents finite log odds")
    record: dict[str, Any] = {
        "schema_version": RECORD_SCHEMA,
        **item,
        "server_session": server_session,
        "family_id": str(row["family_id"]),
        "phase": str(row["phase"]),
        "choice_order": str(row["choice_order"]),
        "target_label": target_label,
        "comparator_label": comparator_label,
        "choice_probabilities": distribution,
        "target_log_odds": math.log(
            target_probability / comparator_probability
        ),
        "content": str(response.get("content", "")),
        "tokens": response.get("tokens"),
        "latency_seconds": time.perf_counter() - started,
    }
    for field in (
        "cell_id",
        "cell_index",
        "anchor_probability",
        "mixture_id",
        "first_cell_index",
        "second_cell_index",
        "first_weight",
        "policy_contrast_index",
        "candidate_policy_id",
        "reference_policy_id",
        "norm",
    ):
        if field in row:
            record[field] = row[field]
    record["record_sha256"] = sha256_bytes(
        canonical_bytes(
            {key: value for key, value in record.items() if key != "record_sha256"}
        )
    )
    return record


def completed_prefix(
    records_dir: Path,
    plan: Mapping[str, Any],
) -> int:
    count = 0
    for item in plan["items"]:
        path = records_dir / f"{int(item['global_index']):06d}.json"
        if not path.exists():
            break
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["plan_item_sha256"] != item["plan_item_sha256"]:
            raise ValueError(f"record-to-plan binding failed: {path}")
        expected = str(record["record_sha256"])
        actual = sha256_bytes(
            canonical_bytes(
                {
                    key: value
                    for key, value in record.items()
                    if key != "record_sha256"
                }
            )
        )
        if actual != expected:
            raise ValueError(f"record content hash mismatch: {path}")
        count += 1
    if len(list(records_dir.glob("*.json"))) != count:
        raise ValueError("record directory contains a gap or extra receipt")
    return count


def materialize_jsonl(records_dir: Path, output_path: Path) -> None:
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        for path in sorted(records_dir.glob("*.json")):
            handle.write(
                canonical_bytes(
                    json.loads(path.read_text(encoding="utf-8"))
                )
            )
    temporary.replace(output_path)


def check_thermal(
    registration: Mapping[str, Any],
    events_path: Path,
    progress_path: Path,
    progress: dict[str, Any],
) -> None:
    caps = registration["resource_caps"]
    temperature = base.gpu_temperature_c()
    progress["maximum_runner_observed_temperature_c"] = max(
        float(progress["maximum_runner_observed_temperature_c"]),
        temperature,
    )
    if temperature >= float(caps["hard_abort_temperature_c"]):
        raise RuntimeError(
            f"hard GPU temperature abort at {temperature:.1f} C"
        )
    thermal_args = argparse.Namespace(
        thermal_pause_temperature=float(
            caps["thermal_pause_temperature_c"]
        ),
        thermal_resume_temperature=float(
            caps["thermal_resume_temperature_c"]
        ),
        thermal_poll_seconds=1.0,
    )
    base.wait_for_thermal_window(
        thermal_args,
        events_path,
        progress_path,
        progress,
    )


def summarize(
    records_dir: Path,
    plan: Mapping[str, Any],
    registration_path: Path,
    progress: Mapping[str, Any],
) -> dict[str, Any]:
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(records_dir.glob("*.json"))
    ]
    by_row: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_row.setdefault(str(record["row_id"]), []).append(record)
    maximum_probability_delta = 0.0
    maximum_log_odds_delta = 0.0
    for row_records in by_row.values():
        if len(row_records) != 2:
            raise ValueError("each selected row requires two cold starts")
        first, second = row_records
        maximum_probability_delta = max(
            maximum_probability_delta,
            max(
                abs(
                    float(first["choice_probabilities"][label])
                    - float(second["choice_probabilities"][label])
                )
                for label in CHOICE_LABELS
            ),
        )
        maximum_log_odds_delta = max(
            maximum_log_odds_delta,
            abs(
                float(first["target_log_odds"])
                - float(second["target_log_odds"])
            ),
        )
    return {
        "schema_version": SUMMARY_SCHEMA,
        "status": (
            "burned_pilot_capture_completed"
            if plan["execution_class"] == "burned_pilot"
            else "smoke_capture_completed"
        ),
        "execution_class": plan["execution_class"],
        "counts": {
            "records": len(records),
            "unique_prompts": len(by_row),
            "planned_epochs": int(plan["epoch_count"]),
            "server_sessions": int(progress["server_session_count"]),
            "query_types": {
                query_type: sum(
                    record["query_type"] == query_type for record in records
                )
                for query_type in (
                    "standard_gamble",
                    "compound_gamble",
                    "policy_probe",
                )
            },
        },
        "reliability": {
            "maximum_choice_probability_delta_across_cold_starts": (
                maximum_probability_delta
            ),
            "maximum_target_log_odds_delta_across_cold_starts": (
                maximum_log_odds_delta
            ),
            "all_choice_vectors_complete": all(
                set(record["choice_probabilities"]) == set(CHOICE_LABELS)
                for record in records
            ),
        },
        "inputs": {
            "registration_sha256": sha256_file(registration_path),
            "registration_content_sha256": progress[
                "registration_content_sha256"
            ],
            "plan_sha256": plan["plan_sha256"],
            "runner_sha256": sha256_file(Path(__file__).resolve()),
        },
        "thermal": {
            "maximum_runner_observed_temperature_c": float(
                progress["maximum_runner_observed_temperature_c"]
            ),
            "pause_count": int(progress["thermal_pause_count"]),
            "pause_seconds": float(progress["thermal_pause_seconds"]),
        },
        "claim_boundary": (
            "Burned calibration data only. This capture cannot serve as v0.34 "
            "confirmation, validate general expected utility, or resolve ASMP-9."
        ),
        "completed_utc": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(),
        ),
    }


def run(args: argparse.Namespace) -> None:
    registration_path = args.registration.resolve()
    registration = load_registration(registration_path)
    expected_wrapper_hash = str(
        registration["implementation"]["hard_cap_wrapper"]["sha256"]
    )
    if os.environ.get("ASMP9_V034_HARD_CAP_ACTIVE") != expected_wrapper_hash:
        raise RuntimeError(
            "ASMP-9 live capture requires the registered hard-cap wrapper"
        )
    manifest = load_manifest(registration)
    rows = selected_rows(
        manifest,
        args.execution_class,
        args.smoke_rows_per_type,
    )
    plan = build_plan(
        rows,
        epoch_count=int(
            registration["sampling_contract"]["cold_start_epochs"]
        ),
        execution_class=args.execution_class,
    )
    output_dir = args.output_dir.resolve()
    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / "events.jsonl"
    progress_path = output_dir / "progress.json"
    plan_path = output_dir / "measurement_plan.json"
    summary_path = output_dir / "summary.json"
    records_jsonl = output_dir / "pilot_records.jsonl"
    owned_pids_path = output_dir / "owned_pids.json"

    if summary_path.exists():
        print(summary_path.read_text(encoding="utf-8"))
        return
    atomic_json(plan_path, plan)
    completed = completed_prefix(records_dir, plan)
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
        if (
            progress["plan_sha256"] != plan["plan_sha256"]
            or progress["registration_content_sha256"]
            != registration["registration_content_sha256"]
        ):
            raise ValueError("existing progress differs from registered run")
    else:
        progress = {
            "schema_version": "asmp9_physical_acquisition_progress_v0_34_1",
            "plan_sha256": plan["plan_sha256"],
            "registration_content_sha256": registration[
                "registration_content_sha256"
            ],
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

    row_by_id = {str(row["row_id"]): row for row in rows}
    parameters = registration["capture_parameters"]
    port = int(parameters["port"])
    base_url = f"http://127.0.0.1:{port}"
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
        if base.port_is_open("127.0.0.1", port):
            raise RuntimeError(f"registered server port {port} is occupied")
        session = int(progress["server_session_count"])
        progress["server_session_count"] = session + 1
        base.atomic_json(progress_path, progress)
        command = build_server_command(registration)
        stdout_path = output_dir / f"server_session_{session:03d}_stdout.log"
        stderr_path = output_dir / f"server_session_{session:03d}_stderr.log"
        with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
            server = subprocess.Popen(
                command,
                stdout=stdout,
                stderr=stderr,
                stdin=subprocess.DEVNULL,
            )
            base.atomic_json(
                owned_pids_path,
                {
                    "root_pid": server.pid,
                    "owned_pids": [server.pid],
                    "execution_class": args.execution_class,
                },
            )
            try:
                append_jsonl(
                    events_path,
                    {
                        "event": "server_start",
                        "epoch": epoch,
                        "session": session,
                        "server_pid": server.pid,
                        "command": command,
                        "ts_utc": time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ",
                            time.gmtime(),
                        ),
                    },
                )
                base.wait_for_server(
                    base_url,
                    server,
                    timeout=180.0,
                )
                while next_index < epoch_end:
                    if (
                        next_index
                        % int(parameters["checkpoint_every"])
                        == 0
                    ):
                        check_thermal(
                            registration,
                            events_path,
                            progress_path,
                            progress,
                        )
                    item = plan["items"][next_index]
                    record = request_record(
                        base_url=base_url,
                        item=item,
                        row=row_by_id[str(item["row_id"])],
                        server_session=session,
                        request_timeout=120.0,
                        seed_base=int(
                            registration["sampling_contract"]["seed_base"]
                        ),
                    )
                    atomic_json(
                        records_dir
                        / f"{int(item['global_index']):06d}.json",
                        record,
                    )
                    next_index += 1
                    progress["completed_records"] = next_index
                    if (
                        next_index
                        % int(parameters["checkpoint_every"])
                        == 0
                        or next_index == epoch_end
                    ):
                        base.atomic_json(progress_path, progress)
                        append_jsonl(
                            events_path,
                            {
                                "event": "checkpoint",
                                "completed_records": next_index,
                                "epoch": epoch,
                                "ts_utc": time.strftime(
                                    "%Y-%m-%dT%H:%M:%SZ",
                                    time.gmtime(),
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
        append_jsonl(
            events_path,
            {
                "event": "planned_cold_restart",
                "completed_epoch": epoch,
                "ts_utc": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ",
                    time.gmtime(),
                ),
            },
        )

    materialize_jsonl(records_dir, records_jsonl)
    summary = summarize(
        records_dir,
        plan,
        registration_path,
        progress,
    )
    atomic_json(summary_path, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--execution-class",
        choices=("smoke", "burned_pilot"),
        required=True,
    )
    parser.add_argument("--smoke-rows-per-type", type=int, default=2)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
