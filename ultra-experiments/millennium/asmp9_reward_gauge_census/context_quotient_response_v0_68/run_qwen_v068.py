"""Run one sealed ASMP-9 v0.68 split as singleton CUDA forwards.

The runner checkpoints every score record, owns no persistent conversation
state, performs no sampled generation, and explicitly releases CUDA state.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
from pathlib import Path
import time
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "asmp9_successor_design_v068", HERE / "successor_design.py"
)
assert SPEC and SPEC.loader
design = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(design)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_once_or_equal(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _event(path: Path, event: str, **fields: Any) -> None:
    value = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        **fields,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
        )
        handle.flush()


def _actual_environment() -> dict:
    return {
        "python": platform.python_version(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("torch", "transformers", "accelerate", "safetensors")
        },
    }


def validate_scored_record(record: Mapping, job: Mapping) -> None:
    for field in (
        "schema_version",
        "record_id",
        "semantic_id",
        "repeat_index",
        "scenario_id",
        "family",
        "split",
        "arm",
        "target",
        "display_order",
        "messages_sha256",
    ):
        if record.get(field) != job.get(field):
            raise ValueError(
                f"record differs from job: {job['record_id']} {field}"
            )
    for field in (
        "prompt_token_count",
        "logp_a",
        "logp_b",
        "raw_log_odds_a_over_b",
        "model_input_sha256",
    ):
        if field not in record:
            raise ValueError(f"record lacks {field}: {job['record_id']}")
    values = [
        float(record["logp_a"]),
        float(record["logp_b"]),
        float(record["raw_log_odds_a_over_b"]),
    ]
    if not all(__import__("math").isfinite(value) for value in values):
        raise ValueError(f"nonfinite score: {job['record_id']}")
    if values[2] != values[0] - values[1]:
        raise ValueError(f"log-odds arithmetic mismatch: {job['record_id']}")
    if int(record["prompt_token_count"]) <= 0:
        raise ValueError(f"invalid prompt length: {job['record_id']}")


def _validate_registration(path: Path) -> tuple[dict, dict, dict]:
    registration = _load(path)
    if (
        registration.get("schema_version")
        != "asmp9_context_quotient_execution_registration_v0_68_1"
    ):
        raise ValueError("unexpected registration schema")
    if registration.get("status") != "registered_prereveal":
        raise ValueError("registration is not prereveal")
    if registration.get("outcomes_read") is not False:
        raise ValueError("registration records prior outcome access")
    if registration.get("phase") not in {"construction", "confirmation"}:
        raise ValueError("invalid phase")
    for name in (
        "protocol",
        "protocol_amendment",
        "scenario_manifest",
        "prereveal_validation",
    ):
        item = registration[name]
        if sha256(Path(item["path"])) != item["sha256"]:
            raise ValueError(f"registered {name} hash mismatch")
    for collection in ("source_files", "model_files"):
        for item in registration[collection]:
            if sha256(Path(item["path"])) != item["sha256"]:
                raise ValueError(
                    f"registered {collection} mismatch: {item['path']}"
                )
    prereveal = _load(Path(registration["prereveal_validation"]["path"]))
    if (
        prereveal.get("status") != "passed"
        or prereveal.get("outcomes_read") is not False
        or prereveal.get("validation", {}).get(
            "synthetic_common_mode_removed"
        )
        is not True
        or prereveal.get("validation", {}).get(
            "synthetic_arm_by_order_interaction_retained"
        )
        is not True
    ):
        raise ValueError("prereveal instrument controls did not pass")
    if _actual_environment() != registration["environment"]:
        raise ValueError("runtime environment differs from registration")
    protocol = _load(Path(registration["protocol"]["path"]))
    manifest = design.load_manifest(
        Path(registration["scenario_manifest"]["path"])
    )
    jobs = design.score_jobs(manifest, registration["phase"])
    if (
        hashlib.sha256(design.canonical_json_bytes(jobs)).hexdigest()
        != registration["job_list_sha256"]
    ):
        raise ValueError("registered job-list hash mismatch")
    caps = registration["resource_contract"]
    if int(caps["batch_size"]) != 1 or int(caps["swap_bytes"]) != 0:
        raise ValueError("singleton or zero-swap contract changed")
    if registration["phase"] == "confirmation":
        decision = registration["construction_decision"]
        if sha256(Path(decision["path"])) != decision["sha256"]:
            raise ValueError("construction decision hash mismatch")
        decision_value = _load(Path(decision["path"]))
        if not decision_value.get("local_confirmation_authorized", False):
            raise ValueError("construction did not authorize confirmation")
    return registration, protocol, manifest


def _load_model(registration: dict):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("registered run requires CUDA")
    model_path = Path(registration["model_path"])
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, local_files_only=True, trust_remote_code=True
    )
    actual_contract = {
        "A": tokenizer.encode("A", add_special_tokens=False),
        "B": tokenizer.encode("B", add_special_tokens=False),
        "vocabulary_size": len(tokenizer),
        "eos_token_id": tokenizer.eos_token_id,
        "pad_token_id": tokenizer.pad_token_id,
    }
    if actual_contract != registration["tokenizer_contract"]:
        raise ValueError("tokenizer contract mismatch")
    total_mb = torch.cuda.get_device_properties(0).total_memory / 1024**2
    allowance = float(registration["resource_contract"]["gpu_allowance_mb"])
    torch.cuda.set_per_process_memory_fraction(min(0.99, allowance / total_mb), 0)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        local_files_only=True,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        device_map={"": "cuda:0"},
        torch_dtype=torch.float16,
    )
    model.eval()
    return model, tokenizer


def _render_one(tokenizer, job: Mapping, maximum_tokens: int) -> tuple[str, int]:
    text = tokenizer.apply_chat_template(
        job["messages"],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    for answer, expected in (("A", 32), ("B", 33)):
        combined = tokenizer.encode(text + answer, add_special_tokens=False)
        if (
            combined[: len(token_ids)] != token_ids
            or combined[len(token_ids) :] != [expected]
        ):
            raise ValueError(
                f"answer boundary changed: {job['record_id']} {answer}"
            )
    if len(token_ids) > maximum_tokens:
        raise ValueError(
            f"prompt exceeds cap: {job['record_id']} "
            f"{len(token_ids)}>{maximum_tokens}"
        )
    return text, len(token_ids)


def _rendered_path(output: Path, record_id: str) -> Path:
    digest = hashlib.sha256(record_id.encode("utf-8")).hexdigest()
    return output / "rendered_inputs" / f"{digest}.txt"


def run(args: argparse.Namespace) -> None:
    import torch
    import torch.nn.functional as functional

    registration_path = args.registration.resolve()
    registration, _, manifest = _validate_registration(registration_path)
    phase = registration["phase"]
    jobs = design.score_jobs(manifest, phase)
    expected = {job["record_id"]: job for job in jobs}
    output = args.output_dir.resolve()
    units = output / "work_units"
    units.mkdir(parents=True, exist_ok=True)
    events = output / "events.jsonl"
    completed: dict[str, dict] = {}
    for unit_path in units.glob("*.json"):
        record = _load(unit_path)["record"]
        record_id = str(record["record_id"])
        if record_id in completed or record_id not in expected:
            raise ValueError(f"invalid resumable record: {record_id}")
        validate_scored_record(record, expected[record_id])
        rendered = _rendered_path(output, record_id)
        if (
            not rendered.exists()
            or sha256(rendered) != record["model_input_sha256"]
        ):
            raise ValueError(f"rendered-input mismatch: {record_id}")
        completed[record_id] = record

    model = tokenizer = None
    status = "failed"
    abort_reason = None
    peak_cuda_mb = 0.0
    started = time.time()
    try:
        _event(
            events,
            "start",
            registration_sha256=sha256(registration_path),
            phase=phase,
            already_complete=len(completed),
        )
        pending = [job for job in jobs if job["record_id"] not in completed]
        if pending:
            model, tokenizer = _load_model(registration)
            device = next(model.parameters()).device
            token_a = int(registration["tokenizer_contract"]["A"][0])
            token_b = int(registration["tokenizer_contract"]["B"][0])
            maximum_tokens = int(
                registration["resource_contract"]["max_prompt_tokens"]
            )
            for job in pending:
                text, prompt_length = _render_one(
                    tokenizer, job, maximum_tokens
                )
                encoded = tokenizer(
                    text,
                    add_special_tokens=False,
                    return_tensors="pt",
                )
                encoded = {
                    key: value.to(device) for key, value in encoded.items()
                }
                with torch.inference_mode():
                    logits = model(
                        **encoded, use_cache=False
                    ).logits[:, -1, :].to(torch.float32)
                    log_probs = functional.log_softmax(logits, dim=-1)
                logp_a = float(log_probs[0, token_a].cpu())
                logp_b = float(log_probs[0, token_b].cpu())
                rendered = _rendered_path(output, job["record_id"])
                _write_once_or_equal(rendered, text.encode("utf-8"))
                record = {
                    **{
                        key: value
                        for key, value in job.items()
                        if key != "messages"
                    },
                    "prompt_token_count": prompt_length,
                    "logp_a": logp_a,
                    "logp_b": logp_b,
                    "raw_log_odds_a_over_b": logp_a - logp_b,
                    "model_input_sha256": sha256(rendered),
                }
                validate_scored_record(record, job)
                unit_path = units / (
                    hashlib.sha256(
                        job["record_id"].encode("utf-8")
                    ).hexdigest()
                    + ".json"
                )
                _write_once_or_equal(
                    unit_path,
                    design.canonical_json_bytes(
                        {
                            "schema_version": (
                                "asmp9_context_quotient_work_unit_v0_68_1"
                            ),
                            "record": record,
                        }
                    ),
                )
                completed[job["record_id"]] = record
                peak_cuda_mb = max(
                    peak_cuda_mb,
                    torch.cuda.max_memory_allocated() / 1024**2,
                )
                _event(
                    events,
                    "checkpoint",
                    completed=len(completed),
                    total=len(jobs),
                    peak_cuda_mb=peak_cuda_mb,
                )
                del encoded, logits, log_probs
        if set(completed) != set(expected):
            raise RuntimeError("not every registered record completed")
        status = "completed"
    except Exception as error:
        abort_reason = f"{type(error).__name__}:{error}"
        _event(events, "error", reason=abort_reason)
        raise
    finally:
        model = None
        tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
        summary = {
            "schema_version": "asmp9_context_quotient_completion_v0_68_1",
            "phase": phase,
            "status": status,
            "abort_reason": abort_reason,
            "records_completed": len(completed),
            "records_expected": len(jobs),
            "peak_cuda_mb": peak_cuda_mb,
            "elapsed_seconds": time.time() - started,
            "registration_sha256": sha256(registration_path),
        }
        if status == "completed":
            _write_once_or_equal(
                output / "completion_summary.json",
                design.canonical_json_bytes(summary),
            )
        else:
            _write_once_or_equal(
                output
                / "abort_receipts"
                / f"abort-{time.time_ns()}.json",
                design.canonical_json_bytes(summary),
            )
        _event(events, "finish", **summary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
