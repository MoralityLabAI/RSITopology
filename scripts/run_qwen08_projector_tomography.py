"""Run the sealed four-projector Boolean intervention cube on Qwen-0.8B."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _event(path: Path, event: str, **fields: Any) -> None:
    value = {"ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **fields}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")


def _validate(registration: dict, registration_path: Path) -> tuple[dict, list[dict], np.lib.npyio.NpzFile]:
    for field in ("protocol", "prompt_manifest", "capture_index", "certificate_file", "analysis_result", "sealed_projectors", "sealed_evaluation_prompts"):
        item = registration[field]
        if sha256_file(item["path"]) != item["sha256"]:
            raise ValueError(f"sealed input hash mismatch: {field}")
    protocol = _load(Path(registration["protocol"]["path"]))
    prompts = _load(Path(registration["sealed_evaluation_prompts"]["path"]))["rows"]
    projectors = np.load(Path(registration["sealed_projectors"]["path"]))
    if registration["outcomes_read"] is not False:
        raise ValueError("registration is not prereveal")
    return protocol, prompts, projectors


def _load_model(protocol: dict):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    model_info = protocol["model"]
    model_path = Path(model_info["local_path"])
    if sha256_file(model_path / "model.safetensors-00001-of-00001.safetensors") != model_info["model_file_sha256"]:
        raise ValueError("model hash mismatch")
    if not torch.cuda.is_available():
        raise RuntimeError("registered run requires CUDA")
    allowance = float(protocol["resource_contract"]["gpu_allowance_mb"])
    total = torch.cuda.get_device_properties(0).total_memory / 1024**2
    torch.cuda.set_per_process_memory_fraction(min(0.99, allowance / total), 0)
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    kwargs = {
        "local_files_only": True,
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "device_map": {"": "cuda:0"},
        "quantization_config": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        ),
    }
    import transformers.modeling_utils as modeling_utils

    old_warmup = modeling_utils.caching_allocator_warmup
    if model_info.get("disable_transformers_caching_allocator_warmup"):
        modeling_utils.caching_allocator_warmup = lambda *_args, **_kwargs: None
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path, **kwargs)
    finally:
        modeling_utils.caching_allocator_warmup = old_warmup
    model.eval()
    return model, tokenizer


def _module(model, site: str):
    matches = [module for name, module in model.named_modules() if name == site]
    if len(matches) != 1:
        raise ValueError(f"site did not resolve uniquely: {site}")
    return matches[0]


def run(args: argparse.Namespace) -> None:
    import torch
    import torch.nn.functional as F

    registration_path = args.registration.resolve()
    registration = _load(registration_path)
    protocol, prompts, projectors = _validate(registration, registration_path)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    events = output / "events.jsonl"
    summary_path = output / "summary.json"
    completed = {path.stem for path in (output / "work_units").glob("*.json")} if (output / "work_units").exists() else set()
    (output / "work_units").mkdir(exist_ok=True)
    model = tokenizer = None
    handles: list[Any] = []
    current_prompt_indices = None
    current_active: set[int] = set()
    current_directions = None
    status, abort_reason = "failed", None
    peak_cuda_mb = 0.0
    start_time = time.time()
    try:
        _event(events, "start", run_id=registration["run_id"], registration_sha256=sha256_file(registration_path))
        model, tokenizer = _load_model(protocol)
        device = next(model.parameters()).device
        selected = torch.tensor(projectors["selected"], device=device, dtype=torch.float32)
        random_dirs = torch.tensor(projectors["matched_random"], device=device, dtype=torch.float32)
        centers = torch.tensor(projectors["centers"], device=device, dtype=torch.float32)
        alpha = float(protocol["intervention"]["alpha"])

        def make_hook(index: int):
            def hook(_module, _inputs, output_value):
                if index not in current_active:
                    return output_value
                tensor = output_value[0] if isinstance(output_value, tuple) else output_value
                rows = torch.arange(tensor.shape[0], device=tensor.device)
                modified = tensor.clone()
                h = modified[rows, current_prompt_indices].to(torch.float32)
                direction = current_directions[index]
                delta = torch.sum((h - centers[index]) * direction, dim=-1, keepdim=True) * direction
                modified[rows, current_prompt_indices] = (h - alpha * delta).to(modified.dtype)
                if isinstance(output_value, tuple):
                    return (modified,) + output_value[1:]
                return modified
            return hook

        for index, site in enumerate(protocol["source_geometry"]["site_ids"]):
            handles.append(_module(model, site).register_forward_hook(make_hook(index)))

        for arm, directions in (("selected", selected), ("matched_random", random_dirs)):
            current_directions = directions
            for mask in range(16):
                unit_id = f"{arm}--{mask:02d}"
                if unit_id in completed:
                    _event(events, "work_unit_skipped", unit_id=unit_id)
                    continue
                current_active = {i for i in range(4) if (mask >> i) & 1}
                records = []
                for offset in range(0, len(prompts), args.batch_size):
                    batch = prompts[offset : offset + args.batch_size]
                    texts = [row["prompt"] for row in batch]
                    suffixes = ["\nANSWER=" + row["expected_answer"] for row in batch]
                    full_texts = [prompt + suffix for prompt, suffix in zip(texts, suffixes)]
                    prompt_tokens = tokenizer(texts, padding=False, add_special_tokens=True)["input_ids"]
                    encoded = tokenizer(full_texts, padding=True, return_tensors="pt")
                    full_unpadded = tokenizer(full_texts, padding=False, add_special_tokens=True)["input_ids"]
                    if any(full[: len(prompt)] != prompt for full, prompt in zip(full_unpadded, prompt_tokens)):
                        raise ValueError("completion boundary changed the registered prompt tokenization")
                    encoded = {key: value.to(device) for key, value in encoded.items()}
                    current_prompt_indices = torch.tensor([len(ids) - 1 for ids in prompt_tokens], device=device)
                    with torch.inference_mode():
                        logits = model(**encoded, use_cache=False).logits
                        log_probs = F.log_softmax(logits.to(torch.float32), dim=-1)
                    for row_index, row in enumerate(batch):
                        prompt_length = len(prompt_tokens[row_index])
                        full_length = int(encoded["attention_mask"][row_index].sum().item())
                        labels = encoded["input_ids"][row_index, prompt_length:full_length]
                        positions = torch.arange(prompt_length - 1, full_length - 1, device=device)
                        token_log_probs = log_probs[row_index, positions, labels]
                        records.append(
                            {
                                "prompt_id": row["prompt_id"],
                                "subcondition_id": row["subcondition_id"],
                                "arm": arm,
                                "mask": mask,
                                "bits": [(mask >> i) & 1 for i in range(4)],
                                "mean_log_probability": float(token_log_probs.mean().cpu()),
                                "completion_token_count": int(len(labels)),
                            }
                        )
                    peak_cuda_mb = max(peak_cuda_mb, torch.cuda.max_memory_allocated() / 1024**2)
                    del encoded, logits, log_probs
                unit_path = output / "work_units" / f"{unit_id}.json"
                write_once_or_equal(unit_path, canonical_json_bytes({"unit_id": unit_id, "records": records}))
                _event(events, "checkpoint", unit_id=unit_id, records=len(records), elapsed_seconds=time.time() - start_time)
        # Frozen numerical replay: baseline once more after all interventions.
        current_active = set()
        current_directions = selected
        replay = []
        for offset in range(0, len(prompts), args.batch_size):
            batch = prompts[offset : offset + args.batch_size]
            texts = [row["prompt"] for row in batch]
            full_texts = [row["prompt"] + "\nANSWER=" + row["expected_answer"] for row in batch]
            prompt_tokens = tokenizer(texts, padding=False, add_special_tokens=True)["input_ids"]
            encoded = tokenizer(full_texts, padding=True, return_tensors="pt")
            full_unpadded = tokenizer(full_texts, padding=False, add_special_tokens=True)["input_ids"]
            if any(full[: len(prompt)] != prompt for full, prompt in zip(full_unpadded, prompt_tokens)):
                raise ValueError("completion boundary changed the registered prompt tokenization")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            current_prompt_indices = torch.tensor([len(ids) - 1 for ids in prompt_tokens], device=device)
            with torch.inference_mode():
                log_probs = F.log_softmax(model(**encoded, use_cache=False).logits.to(torch.float32), dim=-1)
            for row_index, row in enumerate(batch):
                start = len(prompt_tokens[row_index])
                end = int(encoded["attention_mask"][row_index].sum().item())
                labels = encoded["input_ids"][row_index, start:end]
                positions = torch.arange(start - 1, end - 1, device=device)
                replay.append({"prompt_id": row["prompt_id"], "mean_log_probability": float(log_probs[row_index, positions, labels].mean().cpu())})
        write_once_or_equal(output / "baseline_replay.json", canonical_json_bytes({"records": replay}))
        status = "completed"
    except Exception as error:
        abort_reason = f"{type(error).__name__}:{error}"
        _event(events, "error", reason=abort_reason)
        raise
    finally:
        for handle in handles:
            handle.remove()
        handles.clear()
        current_prompt_indices = None
        current_directions = None
        model = None
        tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
        summary = {
            "schema_version": "qwen08_projector_tomography_summary_v0_1",
            "run_id": registration["run_id"],
            "status": status,
            "abort_reason": abort_reason,
            "work_units_completed": len(list((output / "work_units").glob("*.json"))),
            "peak_cuda_mb": peak_cuda_mb,
            "elapsed_seconds": time.time() - start_time,
            "registration_sha256": sha256_file(registration_path),
        }
        summary_path.write_bytes(canonical_json_bytes(summary))
        _event(events, "finish", **summary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
