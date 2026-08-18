"""Bounded, checkpointed throughput sample for Qwen 0.8B activation audits."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import time
from typing import Any, Iterable


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(_canonical_bytes(value))
    temporary.replace(path)


def _append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(_canonical_bytes(value).decode("utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _percentile(values: list[float], probability: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _load_prompts(path: Path, count: int) -> tuple[list[str], int]:
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = manifest.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("prompt manifest has no rows")
    source = [str(row["prompt"]) for row in rows]
    prompts = [source[index % len(source)] for index in range(count)]
    return prompts, len(source)


def _batches(items: list[str], size: int) -> Iterable[tuple[int, list[str]]]:
    for start in range(0, len(items), size):
        yield start, items[start : start + size]


def _load_model(model_path: Path, gpu_allowance_mb: float, load_mode: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for this registered sample")
    total_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
    torch.cuda.set_per_process_memory_fraction(min(0.99, gpu_allowance_mb / total_mb), device=0)
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        local_files_only=True,
        trust_remote_code=True,
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    kwargs = {
        "local_files_only": True,
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "device_map": {"": "cuda:0"},
    }
    if load_mode == "nf4":
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
    elif load_mode == "fp16":
        kwargs["dtype"] = torch.float16
    else:
        raise ValueError(f"unsupported load mode: {load_mode}")
    import transformers.modeling_utils as modeling_utils

    original_warmup = modeling_utils.caching_allocator_warmup
    modeling_utils.caching_allocator_warmup = lambda *_args, **_kwargs: None
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path, **kwargs)
    finally:
        modeling_utils.caching_allocator_warmup = original_warmup
    model.eval()
    return model, tokenizer


def _score_batch(model: Any, tokenizer: Any, prompts: list[str], max_length: int) -> tuple[int, float]:
    import torch

    tokens = tokenizer(
        prompts,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )
    input_tokens = int(tokens["attention_mask"].sum().item())
    tokens = {name: value.to("cuda:0") for name, value in tokens.items()}
    with torch.inference_mode():
        output = model.model(**tokens, use_cache=False, return_dict=True)
        hidden = output.last_hidden_state
        last_indices = tokens["attention_mask"].sum(dim=1) - 1
        final_hidden = hidden[torch.arange(hidden.shape[0], device=hidden.device), last_indices]
        # Frozen, inexpensive audit statistic: RMS of the final-token residual state.
        score = float(final_hidden.float().square().mean(dim=1).mean().item())
    del output, hidden, final_hidden, tokens
    return input_tokens, score


def benchmark(args: argparse.Namespace) -> None:
    import torch
    import transformers

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    events_path = output / "events.jsonl"
    progress_path = output / "progress.json"
    summary_path = output / "summary.json"
    if summary_path.exists():
        print(summary_path.read_text(encoding="utf-8"))
        return
    prompts, unique_prompt_count = _load_prompts(args.prompt_manifest, args.sample_count)
    warmup_prompts = prompts[: min(args.warmup_count, len(prompts))]
    measured_prompts = prompts
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _append_jsonl(
        events_path,
        {
            "event": "start",
            "started_utc": started_utc,
            "sample_count": len(measured_prompts),
            "batch_size": args.batch_size,
        },
    )
    load_started = time.perf_counter()
    model, tokenizer = _load_model(args.model_path, args.gpu_allowance_mb, args.load_mode)
    torch.cuda.synchronize()
    model_load_seconds = time.perf_counter() - load_started
    _append_jsonl(events_path, {"event": "model_loaded", "seconds": model_load_seconds})

    warmup_started = time.perf_counter()
    warmup_tokens = 0
    for _, batch in _batches(warmup_prompts, args.batch_size):
        tokens, _ = _score_batch(model, tokenizer, batch, args.max_length)
        warmup_tokens += tokens
    torch.cuda.synchronize()
    warmup_seconds = time.perf_counter() - warmup_started
    _append_jsonl(
        events_path,
        {"event": "warmup_complete", "seconds": warmup_seconds, "audits": len(warmup_prompts)},
    )

    latencies: list[float] = []
    token_counts: list[int] = []
    scalar_checksum = 0.0
    completed = 0
    chunks_completed = 0
    measured_started = time.perf_counter()
    for start, batch in _batches(measured_prompts, args.batch_size):
        torch.cuda.synchronize()
        batch_started = time.perf_counter()
        input_tokens, score = _score_batch(model, tokenizer, batch, args.max_length)
        torch.cuda.synchronize()
        batch_seconds = time.perf_counter() - batch_started
        latencies.append(batch_seconds)
        token_counts.append(input_tokens)
        scalar_checksum += score * len(batch)
        completed += len(batch)
        if completed % args.checkpoint_every == 0 or completed == len(measured_prompts):
            chunks_completed += 1
            elapsed = time.perf_counter() - measured_started
            progress = {
                "schema_version": "asmp8_qwen08_audit_throughput_progress_v0_1",
                "completed_audits": completed,
                "chunks_completed": chunks_completed,
                "elapsed_seconds": elapsed,
                "audits_per_second": completed / elapsed,
                "input_tokens": sum(token_counts),
                "scalar_checksum": scalar_checksum,
            }
            _atomic_json(progress_path, progress)
            _append_jsonl(events_path, {"event": "checkpoint", **progress})
    measured_seconds = time.perf_counter() - measured_started

    audits_per_second = completed / measured_seconds
    input_tokens = sum(token_counts)
    etas = {
        str(target): {
            "steady_state_seconds": target / audits_per_second,
            "cold_start_seconds": model_load_seconds + warmup_seconds + target / audits_per_second,
        }
        for target in (31, 64, 8192, 524288)
    }
    summary = {
        "schema_version": "asmp8_qwen08_audit_throughput_summary_v0_1",
        "status": "completed",
        "measurement_contract": {
            "unit": "one Qwen 0.8B forward pass plus final-token residual RMS reduction",
            "generation": False,
            "gradients": False,
            "weights_modified": False,
            "human_label_throughput": False,
            "batch_size": args.batch_size,
            "max_length": args.max_length,
            "load_mode": args.load_mode,
            "precision": (
                "NF4 double-quantization with float16 compute"
                if args.load_mode == "nf4"
                else "float16 weights and compute"
            ),
        },
        "inputs": {
            "model_path": str(args.model_path.resolve()),
            "prompt_manifest": str(args.prompt_manifest.resolve()),
            "prompt_manifest_sha256": _sha256(args.prompt_manifest),
            "unique_manifest_prompts": unique_prompt_count,
            "sample_count": completed,
            "warmup_count": len(warmup_prompts),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "cuda_device": torch.cuda.get_device_name(0),
            "pid": os.getpid(),
        },
        "timing": {
            "model_load_seconds": model_load_seconds,
            "warmup_seconds": warmup_seconds,
            "measured_seconds": measured_seconds,
            "audits_per_second": audits_per_second,
            "input_tokens_per_second": input_tokens / measured_seconds,
            "batch_latency_seconds": {
                "mean": statistics.fmean(latencies),
                "p50": _percentile(latencies, 0.50),
                "p90": _percentile(latencies, 0.90),
                "p95": _percentile(latencies, 0.95),
                "p99": _percentile(latencies, 0.99),
            },
        },
        "counts": {
            "audits_completed": completed,
            "input_tokens": input_tokens,
            "batches": len(latencies),
            "chunks_completed": chunks_completed,
        },
        "eta": etas,
        "scalar_checksum": scalar_checksum,
        "started_utc": started_utc,
        "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _atomic_json(summary_path, summary)
    _append_jsonl(events_path, {"event": "complete", "summary_sha256": _sha256(summary_path)})
    print(json.dumps(summary, indent=2, sort_keys=True))

    del model, tokenizer, prompts, measured_prompts, warmup_prompts
    gc.collect()
    torch.cuda.synchronize()
    torch.cuda.empty_cache()
    if hasattr(torch.cuda, "ipc_collect"):
        torch.cuda.ipc_collect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--prompt-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample-count", type=int, default=1000)
    parser.add_argument("--warmup-count", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--checkpoint-every", type=int, default=100)
    parser.add_argument("--gpu-allowance-mb", type=float, default=3440.0)
    parser.add_argument("--load-mode", choices=("nf4", "fp16"), default="nf4")
    args = parser.parse_args()
    if args.sample_count <= 0 or args.warmup_count < 0 or args.batch_size <= 0:
        parser.error("sample, warmup, and batch sizes are invalid")
    if args.checkpoint_every <= 0 or args.sample_count % args.checkpoint_every:
        parser.error("sample-count must be divisible by checkpoint-every")
    if args.checkpoint_every % args.batch_size:
        parser.error("checkpoint-every must be divisible by batch-size")
    return args


if __name__ == "__main__":
    benchmark(parse_args())
