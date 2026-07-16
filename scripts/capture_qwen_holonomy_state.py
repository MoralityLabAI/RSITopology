"""Capture one frozen Qwen3.5-0.8B model state under a sealed authorization.

This program performs forward passes only and writes one resumable activation
chunk per site, context shard, and geometry half.  It must run inside the
registered hard-cap wrapper; direct invocation without its authorization is
fail-closed.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Mapping

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import (
    canonical_json_bytes,
    prompt_rows_for_chunk,
    runtime_environment,
    sha256_file,
    validate_prompt_manifest,
    write_once_or_equal,
)
from rsi_topology.qwen_state_capture import (
    STATE_CAPTURE_SCHEMA,
    development_state,
    load_causal_protocol,
    resolve_unique_module,
    state_capture_chunk_id,
    validate_development_files,
)


def _event(path: Path, event: str, **fields: Any) -> None:
    row = {"time_unix": time.time(), "event": event, **fields}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    temporary.replace(path)


def _validate_authorization(
    value: Mapping[str, Any],
    *,
    args: argparse.Namespace,
) -> None:
    if value.get("schema_version") != "qwen_holonomy_state_capture_authorization_v0_1":
        raise ValueError("invalid state-capture authorization schema")
    if value.get("status") != "authorized_for_qwen_holonomy_state_capture":
        raise ValueError("state capture is not authorized")
    if value.get("protocol_sha256") != sha256_file(args.protocol):
        raise ValueError("authorization does not bind protocol bytes")
    if value.get("geometry_manifest_sha256") != sha256_file(args.geometry_manifest):
        raise ValueError("authorization does not bind geometry manifest bytes")
    if value.get("state_id") != args.state_id:
        raise ValueError("authorization state differs")
    if value.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap wrapper validation is not passed")
    if value.get("caps_confirmed_by_user") is not True:
        raise ValueError("resource caps were not explicitly confirmed")
    caps = value.get("resource_caps")
    if not isinstance(caps, Mapping):
        raise ValueError("authorization has no resource caps")
    for key in (
        "memory_mb",
        "cpu_percent",
        "io_mb_s",
        "timeout_seconds",
        "gpu_allowance_mb",
        "checkpoint_every_seconds",
    ):
        if float(caps.get(key, 0)) <= 0:
            raise ValueError(f"invalid resource cap: {key}")
    if int(caps.get("swap_bytes", -1)) != 0:
        raise ValueError("state capture requires zero registered swap")
    parameters = value.get("capture_parameters")
    if not isinstance(parameters, Mapping):
        raise ValueError("authorization has no capture parameters")
    if Path(str(parameters.get("output_dir", ""))).resolve() != args.output_dir.resolve():
        raise ValueError("authorized output directory differs")
    if int(parameters.get("batch_size", 0)) != args.batch_size:
        raise ValueError("authorized batch size differs")
    if parameters.get("quantization") != args.quantization:
        raise ValueError("authorized quantization differs")
    if value.get("environment_lock") != runtime_environment():
        raise ValueError("runtime environment differs from authorization")
    for name in ("hard_cap_wrapper", "cleanup_script"):
        item = value.get(name)
        if not isinstance(item, Mapping):
            raise ValueError(f"authorization has no {name}")
        path = Path(str(item.get("path", "")))
        if not path.is_file() or sha256_file(path) != item.get("sha256"):
            raise ValueError(f"authorized {name} is missing or changed")
    sources = value.get("source_paths")
    hashes = value.get("source_sha256")
    if not isinstance(sources, Mapping) or not isinstance(hashes, Mapping):
        raise ValueError("authorization source universe is absent")
    if set(sources) != set(hashes):
        raise ValueError("authorization source universe is incomplete")
    for name, raw_path in sources.items():
        path = Path(str(raw_path))
        if not path.is_file() or sha256_file(path) != hashes[name]:
            raise ValueError(f"authorized source changed: {name}")


def _load_model(
    *, protocol: Mapping[str, Any], state_id: str, quantization: str, gpu_mb: float
) -> tuple[Any, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_info = protocol["development_model"]
    model_path = Path(model_info["local_path"])
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, local_files_only=True, trust_remote_code=True
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    if not torch.cuda.is_available():
        raise RuntimeError("registered development capture requires CUDA")
    total_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
    fraction = min(0.99, float(gpu_mb) / total_mb)
    torch.cuda.set_per_process_memory_fraction(fraction, device=0)
    load_kwargs: dict[str, Any] = {
        "local_files_only": True,
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "device_map": {"": "cuda:0"},
    }
    if quantization == "4bit":
        from transformers import BitsAndBytesConfig

        load_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
    elif quantization == "float16":
        load_kwargs["torch_dtype"] = torch.float16
    else:
        raise ValueError("quantization must be 4bit or float16")
    model = AutoModelForCausalLM.from_pretrained(model_path, **load_kwargs)
    state = development_state(protocol, state_id)
    if state["kind"] == "peft_adapter":
        from peft import PeftModel

        model = PeftModel.from_pretrained(
            model,
            state["path"],
            adapter_name=state_id,
            is_trainable=False,
        )
    model.eval()
    return model, tokenizer


def capture(args: argparse.Namespace) -> None:
    import torch

    protocol = load_causal_protocol(args.protocol)
    manifest = json.loads(args.geometry_manifest.read_text(encoding="utf-8"))
    validate_prompt_manifest(manifest)
    authorization = json.loads(args.authorization.read_text(encoding="utf-8"))
    _validate_authorization(authorization, args=args)
    model_hashes = validate_development_files(protocol, args.state_id)

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    events = output / "events.jsonl"
    progress_path = output / "capture_progress.json"
    summary_path = output / "summary.json"
    index_path = output / "state_capture_index.json"
    run_id = str(authorization["run_id"])
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
        if progress.get("run_id") != run_id or progress.get("state_id") != args.state_id:
            raise ValueError("existing progress belongs to another run or state")
    else:
        progress = {
            "schema_version": "qwen_holonomy_state_capture_progress_v0_1",
            "run_id": run_id,
            "state_id": args.state_id,
            "chunks": [],
        }
    completed = {row["chunk_id"]: row for row in progress["chunks"]}
    chunks = list(progress["chunks"])
    model = None
    tokenizer = None
    handles: list[Any] = []
    status = "failed"
    abort_reason = None
    peak_cuda_mb = 0.0
    started = time.time()
    try:
        _event(events, "start", run_id=run_id, state_id=args.state_id)
        model, tokenizer = _load_model(
            protocol=protocol,
            state_id=args.state_id,
            quantization=args.quantization,
            gpu_mb=float(authorization["resource_caps"]["gpu_allowance_mb"]),
        )
        sites = tuple(protocol["development_model"]["activation_sites"])
        captures: dict[str, list[np.ndarray]] = {site: [] for site in sites}
        current_indices = None

        def make_hook(site: str):
            def hook(_module, _inputs, output_value):
                nonlocal current_indices
                tensor = output_value[0] if isinstance(output_value, tuple) else output_value
                if current_indices is None or tensor.ndim != 3:
                    raise RuntimeError(f"unexpected hooked output at {site}")
                rows = torch.arange(tensor.shape[0], device=tensor.device)
                selected = tensor[rows, current_indices]
                captures[site].append(
                    selected.detach().to(torch.float32).cpu().numpy()
                )

            return hook

        for site in sites:
            module = resolve_unique_module(model, site)
            handles.append(module.register_forward_hook(make_hook(site)))

        checkpoint_seconds = float(
            authorization["resource_caps"]["checkpoint_every_seconds"]
        )
        last_checkpoint = time.time()
        timeout = float(authorization["resource_caps"]["timeout_seconds"])
        for shard_index in range(int(manifest["context_shards"])):
            shard = f"shard-{shard_index:02d}"
            for half in manifest["halves"]:
                if time.time() - started > timeout:
                    raise TimeoutError("registered state-capture timeout")
                rows = prompt_rows_for_chunk(
                    manifest, context_shard=shard, half=half
                )
                required = {
                    state_capture_chunk_id(args.state_id, site, shard, half)
                    for site in sites
                }
                if required <= set(completed):
                    _event(events, "chunk_group_skipped", shard=shard, half=half)
                    continue
                for values in captures.values():
                    values.clear()
                for start in range(0, len(rows), args.batch_size):
                    batch = rows[start : start + args.batch_size]
                    encoded = tokenizer(
                        [row["prompt"] for row in batch],
                        padding=True,
                        return_tensors="pt",
                    )
                    encoded = {
                        key: value.to(next(model.parameters()).device)
                        for key, value in encoded.items()
                    }
                    current_indices = encoded["attention_mask"].sum(dim=1) - 1
                    with torch.inference_mode():
                        model(**encoded, use_cache=False)
                    peak_cuda_mb = max(
                        peak_cuda_mb,
                        torch.cuda.max_memory_allocated() / (1024 * 1024),
                    )
                    del encoded
                current_indices = None
                prompt_ids = [row["prompt_id"] for row in rows]
                for site in sites:
                    values = np.concatenate(captures[site], axis=0).astype(
                        np.float32, copy=False
                    )
                    if values.ndim != 2 or len(values) != len(rows):
                        raise RuntimeError(f"state-capture shape failure at {site}")
                    if not np.all(np.isfinite(values)):
                        raise RuntimeError(f"state-capture finiteness failure at {site}")
                    relative = (
                        Path("chunks")
                        / args.state_id
                        / site.replace(".", "__")
                        / f"{shard}--{half}.npz"
                    )
                    target = output / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    np.savez(target, activations=values)
                    row = {
                        "chunk_id": state_capture_chunk_id(
                            args.state_id, site, shard, half
                        ),
                        "state_id": args.state_id,
                        "site_id": site,
                        "context_shard": shard,
                        "half": half,
                        "path": relative.as_posix(),
                        "sha256": sha256_file(target),
                        "prompt_ids": prompt_ids,
                        "row_count": len(values),
                        "ambient_dimension": int(values.shape[1]),
                        "dtype": str(values.dtype),
                    }
                    if row["chunk_id"] not in completed:
                        chunks.append(row)
                        completed[row["chunk_id"]] = row
                progress["chunks"] = sorted(chunks, key=lambda row: row["chunk_id"])
                _atomic_json(progress_path, progress)
                _event(
                    events,
                    "checkpoint",
                    shard=shard,
                    half=half,
                    chunk_count=len(chunks),
                    elapsed_seconds=time.time() - started,
                )
                if time.time() - last_checkpoint >= checkpoint_seconds:
                    last_checkpoint = time.time()
        index = {
            "schema_version": STATE_CAPTURE_SCHEMA,
            "run_id": run_id,
            "state_id": args.state_id,
            "protocol_sha256": sha256_file(args.protocol),
            "geometry_manifest_sha256": sha256_file(args.geometry_manifest),
            "authorization_sha256": sha256_file(args.authorization),
            "quantization": args.quantization,
            "model_file_sha256": model_hashes,
            "chunks": sorted(chunks, key=lambda row: row["chunk_id"]),
        }
        write_once_or_equal(index_path, canonical_json_bytes(index))
        status = "completed"
    except TimeoutError as error:
        status = "aborted"
        abort_reason = str(error)
        raise
    finally:
        for handle in handles:
            handle.remove()
        handles.clear()
        model = None
        tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
        summary = {
            "schema_version": "qwen_holonomy_state_capture_summary_v0_1",
            "run_id": run_id,
            "state_id": args.state_id,
            "status": status,
            "abort_reason": abort_reason,
            "chunks_completed": len(chunks),
            "peak_cuda_mb": peak_cuda_mb,
            "elapsed_seconds": time.time() - started,
            "explicit_model_cleanup": True,
        }
        _atomic_json(summary_path, summary)
        _event(events, status, **summary)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--geometry-manifest", type=Path, required=True)
    value.add_argument("--authorization", type=Path, required=True)
    value.add_argument("--state-id", required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    value.add_argument("--batch-size", type=int, default=4)
    value.add_argument("--quantization", choices=("4bit", "float16"), default="4bit")
    return value


if __name__ == "__main__":
    capture(parser().parse_args())
