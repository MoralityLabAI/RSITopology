"""Execute one sealed ASMP-9 v0.67 split on a CUDA model.

The runner scores one next-token decision and checkpoints every prompt record.
It performs no sampled generation and owns no persistent conversation cache.
"""

from __future__ import annotations

import argparse
import gc
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("bridge_core_v067", HERE / "bridge_core.py")
assert SPEC and SPEC.loader
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


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
        handle.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def _validate_registration(path: Path) -> tuple[dict, dict, dict]:
    registration = _load(path)
    if registration.get("schema_version") != "asmp9_physical_dynamic_bridge_registration_v0_67":
        raise ValueError("unexpected registration schema")
    if registration.get("outcomes_read") is not False:
        raise ValueError("registration is not prereveal")
    for name in ("protocol", "scenario_manifest"):
        item = registration[name]
        if core.sha256_file(Path(item["path"])) != item["sha256"]:
            raise ValueError(f"registered {name} hash mismatch")
    for item in registration["source_files"]:
        if core.sha256_file(Path(item["path"])) != item["sha256"]:
            raise ValueError(f"registered source hash mismatch: {item['path']}")
    for item in registration["model_files"]:
        if core.sha256_file(Path(item["path"])) != item["sha256"]:
            raise ValueError(f"registered model hash mismatch: {item['path']}")
    if registration["phase"] == "confirmation":
        for name in (
            "construction_records",
            "calibration",
            "construction_analysis_receipt",
        ):
            item = registration[name]
            if core.sha256_file(Path(item["path"])) != item["sha256"]:
                raise ValueError(f"registered {name} hash mismatch")
        construction_receipt = _load(
            Path(registration["construction_analysis_receipt"]["path"])
        )
        if (
            construction_receipt["records"]["sha256"]
            != registration["construction_records"]["sha256"]
            or construction_receipt["calibration"]["sha256"]
            != registration["calibration"]["sha256"]
        ):
            raise ValueError("construction receipt linkage mismatch")
        calibration = _load(Path(registration["calibration"]["path"]))
        frozen_thresholds = {
            key: calibration[key]
            for key in ("numeric_guard", "epsilon_measurement", "epsilon_restore")
        }
        if registration["frozen_thresholds"] != frozen_thresholds:
            raise ValueError("registered confirmation thresholds differ from calibration")
        if registration["frozen_transition_model"] != calibration["transition_model"]:
            raise ValueError("registered transition model differs from calibration")
    protocol = _load(Path(registration["protocol"]["path"]))
    manifest = core.load_manifest(Path(registration["scenario_manifest"]["path"]))
    if protocol["status"] != "registered_prereveal":
        raise ValueError("protocol is not frozen for execution")
    if registration["phase"] not in {"construction", "confirmation"}:
        raise ValueError("invalid registered phase")
    return registration, protocol, manifest


def _load_model(registration: dict, protocol: dict):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("registered model run requires CUDA")
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
    if actual_contract != protocol["model_contract"]["tokenizer_contract"]:
        raise ValueError(
            f"tokenizer contract mismatch: actual={actual_contract}, "
            f"registered={protocol['model_contract']['tokenizer_contract']}"
        )
    tokenizer.padding_side = "left"
    allowance = float(protocol["resource_contract"]["gpu_allowance_mb"])
    total_mb = torch.cuda.get_device_properties(0).total_memory / 1024**2
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


def _render(tokenizer, jobs: list[dict], maximum_tokens: int) -> tuple[list[str], list[int]]:
    texts: list[str] = []
    lengths: list[int] = []
    for job in jobs:
        text = tokenizer.apply_chat_template(
            job["messages"],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        for answer, expected in (("A", 32), ("B", 33)):
            with_answer = tokenizer.encode(text + answer, add_special_tokens=False)
            if (
                with_answer[: len(token_ids)] != token_ids
                or with_answer[len(token_ids) :] != [expected]
            ):
                raise ValueError(
                    f"registered answer boundary changed: {job['record_id']} {answer}"
                )
        if len(token_ids) > maximum_tokens:
            raise ValueError(
                f"prompt exceeds registered token cap: {job['record_id']} "
                f"{len(token_ids)}>{maximum_tokens}"
            )
        texts.append(text)
        lengths.append(len(token_ids))
    return texts, lengths


def run(args: argparse.Namespace) -> None:
    import torch
    import torch.nn.functional as functional

    registration_path = args.registration.resolve()
    registration, protocol, manifest = _validate_registration(registration_path)
    phase = registration["phase"]
    expected_jobs = core.score_jobs(manifest, phase)
    output = args.output_dir.resolve()
    units = output / "work_units"
    units.mkdir(parents=True, exist_ok=True)
    events = output / "events.jsonl"
    summary_path = output / "completion_summary.json"
    expected_by_id = {job["record_id"]: job for job in expected_jobs}
    completed: dict[str, dict] = {}
    for path in units.glob("*.json"):
        value = _load(path)
        record = value["record"]
        record_id = record["record_id"]
        if record_id in completed:
            raise ValueError(f"duplicate resumable record: {record_id}")
        if record_id not in expected_by_id:
            raise ValueError(f"unregistered resumable record: {record_id}")
        core.validate_scored_record(record, expected_by_id[record_id])
        rendered_path = units.parent / "rendered_inputs" / (
            __import__("hashlib").sha256(record_id.encode("utf-8")).hexdigest()
            + ".txt"
        )
        if (
            not rendered_path.exists()
            or core.sha256_file(rendered_path) != record["model_input_sha256"]
        ):
            raise ValueError(f"resumable rendered input mismatch: {record_id}")
        completed[record_id] = record
    expected_ids = set(expected_by_id)
    if set(completed) - expected_ids:
        raise ValueError("output contains unregistered work-unit IDs")

    model = tokenizer = None
    status = "failed"
    abort_reason = None
    peak_cuda_mb = 0.0
    started = time.time()
    try:
        _event(
            events,
            "start",
            registration_sha256=core.sha256_file(registration_path),
            phase=phase,
            already_complete=len(completed),
        )
        pending = [job for job in expected_jobs if job["record_id"] not in completed]
        if pending:
            model, tokenizer = _load_model(registration, protocol)
            device = next(model.parameters()).device
            batch_size = int(protocol["resource_contract"]["batch_size"])
            maximum_tokens = int(protocol["resource_contract"]["max_prompt_tokens"])
            token_a = int(protocol["model_contract"]["tokenizer_contract"]["A"][0])
            token_b = int(protocol["model_contract"]["tokenizer_contract"]["B"][0])
            for offset in range(0, len(pending), batch_size):
                jobs = pending[offset : offset + batch_size]
                texts, prompt_lengths = _render(tokenizer, jobs, maximum_tokens)
                encoded = tokenizer(
                    texts,
                    padding=True,
                    add_special_tokens=False,
                    return_tensors="pt",
                )
                encoded = {key: value.to(device) for key, value in encoded.items()}
                with torch.inference_mode():
                    logits = model(**encoded, use_cache=False).logits[:, -1, :].to(
                        torch.float32
                    )
                    log_probs = functional.log_softmax(logits, dim=-1)
                for index, job in enumerate(jobs):
                    logp_a = float(log_probs[index, token_a].cpu())
                    logp_b = float(log_probs[index, token_b].cpu())
                    record = {
                        **{key: value for key, value in job.items() if key != "messages"},
                        "prompt_token_count": prompt_lengths[index],
                        "logp_a": logp_a,
                        "logp_b": logp_b,
                        "raw_log_odds_a_over_b": logp_a - logp_b,
                        "model_input_sha256": core.sha256_file(
                            _write_prompt_temp(output, job["record_id"], texts[index])
                        ),
                    }
                    unit_path = units / (
                        __import__("hashlib").sha256(
                            job["record_id"].encode("utf-8")
                        ).hexdigest()
                        + ".json"
                    )
                    _write_once_or_equal(
                        unit_path,
                        core.canonical_json_bytes(
                            {
                                "schema_version": "asmp9_dynamic_bridge_work_unit_v0_67",
                                "record": record,
                            }
                        ),
                    )
                    completed[job["record_id"]] = record
                peak_cuda_mb = max(
                    peak_cuda_mb, torch.cuda.max_memory_allocated() / 1024**2
                )
                _event(
                    events,
                    "checkpoint",
                    completed=len(completed),
                    total=len(expected_jobs),
                    peak_cuda_mb=peak_cuda_mb,
                )
                del encoded, logits, log_probs
        if set(completed) != expected_ids:
            raise RuntimeError("run ended without every registered record")
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
            "schema_version": "asmp9_dynamic_bridge_completion_v0_67",
            "phase": phase,
            "status": status,
            "abort_reason": abort_reason,
            "records_completed": len(completed),
            "records_expected": len(expected_jobs),
            "peak_cuda_mb": peak_cuda_mb,
            "elapsed_seconds": time.time() - started,
            "registration_sha256": core.sha256_file(registration_path),
        }
        if status == "completed":
            _write_once_or_equal(summary_path, core.canonical_json_bytes(summary))
        else:
            abort_path = (
                output
                / "abort_receipts"
                / f"abort-{time.time_ns()}.json"
            )
            _write_once_or_equal(abort_path, core.canonical_json_bytes(summary))
        _event(events, "finish", **summary)


def _write_prompt_temp(output: Path, record_id: str, text: str) -> Path:
    """Write the exact rendered input once so its hash is independently replayable."""
    digest = __import__("hashlib").sha256(record_id.encode("utf-8")).hexdigest()
    path = output / "rendered_inputs" / f"{digest}.txt"
    _write_once_or_equal(path, text.encode("utf-8"))
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
