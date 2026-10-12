"""Capture one fresh Qwen0.8B precision/context arm under a hard cap.

The script is intentionally separate from Stage B: Stage-B code and receipts
remain immutable inputs, while this command has its own authorization schema,
fresh prompt manifest, and state-capture index.
"""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
import sys
import time
from typing import Any, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import (  # noqa: E402
    canonical_json_bytes,
    prompt_rows_for_chunk,
    runtime_environment,
    sha256_file,
    write_once_or_equal,
)
from rsi_topology.qwen_precision_context import (  # noqa: E402
    PROTOCOL_ID,
    load_protocol,
    validate_manifest,
)
from rsi_topology.qwen_state_capture import (  # noqa: E402
    STATE_CAPTURE_SCHEMA,
    development_state,
    load_causal_protocol,
    resolve_unique_module,
    state_capture_chunk_id,
    validate_development_files,
)


# Reuse the wrapper's state-capture schema while binding this experiment's
# distinct protocol, source universe, prompt-separation receipt, and command.
AUTH_SCHEMA = "qwen_holonomy_state_capture_authorization_v0_1"


def _event(path: Path, event: str, **fields: Any) -> None:
    row = {"time_unix": time.time(), "event": event, **fields}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    temporary.replace(path)


def _validate_authorization(value: Mapping[str, Any], args: argparse.Namespace) -> None:
    if value.get("schema_version") != AUTH_SCHEMA:
        raise ValueError("invalid precision/context capture authorization")
    if value.get("status") != "authorized_for_capture":
        raise ValueError("capture authorization is not active")
    if value.get("scientific_protocol_sha256") != sha256_file(args.scientific_protocol):
        raise ValueError("authorization does not bind scientific protocol")
    if value.get("causal_protocol_sha256") != sha256_file(args.causal_protocol):
        raise ValueError("authorization does not bind causal protocol")
    if value.get("prompt_manifest_sha256") != sha256_file(args.geometry_manifest):
        raise ValueError("authorization does not bind prompt manifest")
    if value.get("state") != args.state or value.get("precision") != args.precision:
        raise ValueError("authorization state or precision differs")
    if Path(str(value.get("output_dir", ""))).resolve() != args.output_dir.resolve():
        raise ValueError("authorization output directory differs")
    if int(value.get("batch_size", 0)) != args.batch_size:
        raise ValueError("authorization batch size differs")
    if value.get("environment_lock") != runtime_environment():
        raise ValueError("runtime environment differs from authorization")
    if value.get("caps_confirmed_by_user") is not True:
        raise ValueError("resource caps were not explicitly confirmed")
    if value.get("resource_caps", {}).get("swap_bytes") != 0:
        raise ValueError("authorization permits swap")
    for field in ("memory_mb", "cpu_percent", "io_mb_s", "timeout_seconds", "gpu_allowance_mb"):
        if float(value.get("resource_caps", {}).get(field, 0)) <= 0:
            raise ValueError(f"invalid resource cap: {field}")
    for item_name in ("hard_cap_wrapper", "cleanup_script"):
        item = value.get(item_name)
        if not isinstance(item, Mapping):
            raise ValueError(f"authorization lacks {item_name}")
        path = Path(str(item.get("path", "")))
        if not path.is_file() or sha256_file(path) != item.get("sha256"):
            raise ValueError(f"authorized {item_name} changed")
    validation_item = value.get("hard_cap_validation_receipt")
    if not isinstance(validation_item, Mapping):
        raise ValueError("authorization lacks hard-cap validation receipt")
    validation_path = Path(str(validation_item.get("path", "")))
    if not validation_path.is_file() or sha256_file(validation_path) != validation_item.get("sha256"):
        raise ValueError("hard-cap validation receipt changed")
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    if validation.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation receipt is not a pass")
    if validation.get("wrapper", {}).get("sha256") != value["hard_cap_wrapper"]["sha256"]:
        raise ValueError("hard-cap validation does not bind wrapper")
    if validation.get("cleanup", {}).get("sha256") != value["cleanup_script"]["sha256"]:
        raise ValueError("hard-cap validation does not bind cleanup")
    separation_item = value.get("prompt_separation_receipt")
    pair_item = value.get("precision_pair_receipt")
    for name, item in (("separation", separation_item), ("precision pair", pair_item)):
        if not isinstance(item, Mapping):
            raise ValueError(f"authorization lacks {name} receipt")
        path = Path(str(item.get("path", "")))
        if not path.is_file() or sha256_file(path) != item.get("sha256"):
            raise ValueError(f"authorized {name} receipt changed")
    if json.loads(Path(str(separation_item["path"])).read_text(encoding="utf-8-sig")).get("passed") is not True:
        raise ValueError("prompt separation receipt is not a pass")
    if json.loads(Path(str(pair_item["path"])).read_text(encoding="utf-8-sig")).get("identical_except_runtime_precision") is not True:
        raise ValueError("precision pair receipt is not a pass")
    sources = value.get("source_paths")
    hashes = value.get("source_sha256")
    if not isinstance(sources, Mapping) or not isinstance(hashes, Mapping) or set(sources) != set(hashes):
        raise ValueError("authorization source universe is incomplete")
    for name, raw in sources.items():
        path = Path(str(raw))
        if not path.is_file() or sha256_file(path) != hashes[name]:
            raise ValueError(f"authorized source changed: {name}")


def _load_model(*, causal_protocol: Mapping[str, Any], state: str, precision: str, gpu_mb: float) -> tuple[Any, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_info = causal_protocol["development_model"]
    model_path = Path(model_info["local_path"])
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    if not torch.cuda.is_available():
        raise RuntimeError("registered Qwen capture requires CUDA")
    total_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
    torch.cuda.set_per_process_memory_fraction(min(0.99, gpu_mb / total_mb), device=0)
    kwargs: dict[str, Any] = {
        "local_files_only": True,
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "device_map": {"": "cuda:0"},
    }
    if precision == "4bit":
        from transformers import BitsAndBytesConfig

        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
    elif precision == "float16":
        kwargs["torch_dtype"] = torch.float16
    else:
        raise ValueError("precision must be 4bit or float16")
    import transformers.modeling_utils as modeling_utils

    original_warmup = modeling_utils.caching_allocator_warmup
    if model_info.get("loader", {}).get("disable_transformers_caching_allocator_warmup", False):
        modeling_utils.caching_allocator_warmup = lambda *_args, **_kwargs: None
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path, **kwargs)
    finally:
        modeling_utils.caching_allocator_warmup = original_warmup
    state_info = development_state(causal_protocol, state)
    if state_info["kind"] == "peft_adapter":
        from peft import PeftModel

        model = PeftModel.from_pretrained(
            model, state_info["path"], adapter_name=state, is_trainable=False
        )
    model.eval()
    return model, tokenizer


def capture(args: argparse.Namespace) -> None:
    import torch

    scientific = load_protocol(args.scientific_protocol)
    causal = load_causal_protocol(args.causal_protocol)
    manifest = json.loads(args.geometry_manifest.read_text(encoding="utf-8-sig"))
    validate_manifest(manifest, protocol_path=args.scientific_protocol)
    authorization = json.loads(args.authorization.read_text(encoding="utf-8-sig"))
    _validate_authorization(authorization, args)
    if args.state not in scientific["model_lock"]["states"]:
        raise ValueError("state is not registered")
    if args.precision not in ("4bit", "float16"):
        raise ValueError("precision is not registered")
    model_hashes = validate_development_files(causal, args.state)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    events = output / "events.jsonl"
    progress_path = output / "capture_progress.json"
    index_path = output / "state_capture_index.json"
    run_id = str(authorization["run_id"])
    if index_path.exists():
        existing = json.loads(index_path.read_text(encoding="utf-8-sig"))
        if existing.get("authorization_sha256") == sha256_file(args.authorization):
            print(json.dumps({"status": "already_complete", "index": str(index_path)}, sort_keys=True))
            return
        raise FileExistsError("capture index exists for another authorization")
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8-sig"))
        if progress.get("run_id") != run_id:
            raise ValueError("existing capture progress belongs to another run")
    else:
        progress = {"run_id": run_id, "completed": {}}
        _atomic_json(progress_path, progress)

    model = tokenizer = None
    hooks = []
    started = time.time()
    peak_cuda_mb = 0.0
    status = "failed"
    abort_reason: str | None = None
    try:
        _event(events, "start", run_id=run_id, state=args.state, precision=args.precision)
        model, tokenizer = _load_model(
            causal_protocol=causal,
            state=args.state,
            precision=args.precision,
            gpu_mb=float(authorization["resource_caps"]["gpu_allowance_mb"]),
        )
        sites = tuple(map(str, scientific["sites"]))
        captures: dict[str, list[np.ndarray]] = {site: [] for site in sites}
        current_indices: Any = None

        def make_hook(site: str):
            def hook(_module: Any, _inputs: Any, output_value: Any) -> None:
                nonlocal current_indices
                tensor = output_value[0] if isinstance(output_value, tuple) else output_value
                if current_indices is None or tensor.ndim != 3:
                    raise RuntimeError(f"unexpected activation rank at {site}")
                rows = torch.arange(tensor.shape[0], device=tensor.device)
                captures[site].append(
                    tensor[rows, current_indices].detach().float().cpu().numpy()
                )
            return hook

        for site in sites:
            hooks.append(resolve_unique_module(model, site).register_forward_hook(make_hook(site)))
        for shard_index in range(int(manifest["context_shards"])):
            shard = f"shard-{shard_index:02d}"
            for half in ("construction", "geometry_validation"):
                if time.time() - started > float(authorization["resource_caps"]["timeout_seconds"]):
                    raise TimeoutError("registered capture timeout")
                chunk_ids = {site: state_capture_chunk_id(args.state, site, shard, half) for site in sites}
                if all(progress["completed"].get(chunk_ids[site]) for site in sites):
                    for site in sites:
                        item = progress["completed"][chunk_ids[site]]
                        existing_path = (output / str(item["path"])).resolve()
                        if (
                            not existing_path.is_file()
                            or sha256_file(existing_path) != item["sha256"]
                        ):
                            raise ValueError("completed capture chunk changed before resume")
                    _event(events, "chunk_group_skipped", shard=shard, half=half)
                    continue
                rows = prompt_rows_for_chunk(manifest, context_shard=shard, half=half)
                for values in captures.values():
                    values.clear()
                for start in range(0, len(rows), args.batch_size):
                    batch = rows[start : start + args.batch_size]
                    encoded = tokenizer(
                        [str(row["prompt"]) for row in batch],
                        return_tensors="pt", padding=True, truncation=False,
                    )
                    encoded = {key: value.to(next(model.parameters()).device) for key, value in encoded.items()}
                    current_indices = encoded["attention_mask"].sum(dim=1) - 1
                    with torch.inference_mode():
                        model(**encoded, use_cache=False)
                    peak_cuda_mb = max(
                        peak_cuda_mb,
                        float(torch.cuda.max_memory_allocated() / (1024 * 1024)),
                    )
                current_indices = None
                prompt_ids = [str(row["prompt_id"]) for row in rows]
                for site in sites:
                    values = np.concatenate(captures[site], axis=0).astype(np.float32, copy=False)
                    if values.shape[0] != len(prompt_ids) or values.ndim != 2 or not np.all(np.isfinite(values)):
                        raise RuntimeError(f"invalid activation capture at {site}")
                    chunk_path = output / "chunks" / args.state / site.replace(".", "__") / f"{shard}--{half}.npz"
                    chunk_path.parent.mkdir(parents=True, exist_ok=True)
                    if not chunk_path.exists():
                        np.savez_compressed(chunk_path, activations=values)
                    progress["completed"][chunk_ids[site]] = {
                        "path": str(chunk_path.relative_to(output)),
                        "sha256": sha256_file(chunk_path),
                        "row_count": int(values.shape[0]),
                        "ambient_dimension": int(values.shape[1]),
                        "prompt_ids": prompt_ids,
                    }
                _atomic_json(progress_path, progress)
                _event(
                    events,
                    "checkpoint",
                    shard=shard,
                    half=half,
                    chunk_groups_completed=len(progress["completed"]) // len(sites),
                    elapsed_seconds=time.time() - started,
                )
        chunks = []
        for site in sites:
            for shard_index in range(int(manifest["context_shards"])):
                for half in ("construction", "geometry_validation"):
                    shard = f"shard-{shard_index:02d}"
                    chunk_id = state_capture_chunk_id(args.state, site, shard, half)
                    item = progress["completed"].get(chunk_id)
                    if not item:
                        raise RuntimeError("capture progress incomplete")
                    chunk_path = (output / str(item["path"])).resolve()
                    if not chunk_path.is_file() or sha256_file(chunk_path) != item["sha256"]:
                        raise RuntimeError("capture chunk changed before index sealing")
                    chunks.append({
                        "chunk_id": chunk_id,
                        "state_id": args.state,
                        "site_id": site,
                        "context_shard": shard,
                        "half": half,
                        "path": item["path"],
                        "sha256": item["sha256"],
                        "prompt_ids": item["prompt_ids"],
                        "row_count": item["row_count"],
                        "ambient_dimension": item["ambient_dimension"],
                        "dtype": "float32",
                    })
        index = {
            "schema_version": STATE_CAPTURE_SCHEMA,
            "run_id": run_id,
            "state_id": args.state,
            "quantization": args.precision,
            "protocol_sha256": sha256_file(args.causal_protocol),
            "geometry_manifest_sha256": sha256_file(args.geometry_manifest),
            "scientific_protocol": {"protocol_id": PROTOCOL_ID, "path": str(args.scientific_protocol.resolve()), "sha256": sha256_file(args.scientific_protocol)},
            "authorization_sha256": sha256_file(args.authorization),
            "model_file_sha256": model_hashes,
            "outcomes_read": False,
            "outcomes_consumed": False,
            "generation": False,
            "gradients": False,
            "weight_mutation": False,
            "chunks": chunks,
        }
        write_once_or_equal(index_path, canonical_json_bytes(index))
        _event(events, "completed", chunks=len(chunks))
        status = "completed"
        print(json.dumps({"status": "completed", "index": str(index_path), "chunk_count": len(chunks)}, sort_keys=True))
    except Exception as error:
        abort_reason = f"{type(error).__name__}:{error}"
        _event(events, "failed", reason=abort_reason)
        raise
    finally:
        for handle in hooks:
            handle.remove()
        del model, tokenizer
        gc.collect()
        if torch.cuda.is_available():
            try:
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            except Exception:
                pass
        _atomic_json(
            output / "summary.json",
            {
                "schema_version": "qwen08_l19_precision_context_capture_summary_v0_1",
                "run_id": run_id,
                "state": args.state,
                "precision": args.precision,
                "status": status,
                "abort_reason": abort_reason,
                "elapsed_seconds": time.time() - started,
                "peak_cuda_mb": peak_cuda_mb,
                "explicit_cuda_cleanup": True,
                "chunks_completed": len(progress.get("completed", {})),
            },
        )


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--causal-protocol", type=Path, default=ROOT / "protocols" / "qwen_holonomy_causal_transfer_v0_1.json")
    value.add_argument("--scientific-protocol", type=Path, default=ROOT / "protocols" / "qwen08_l19_precision_context_v0_1.json")
    value.add_argument("--geometry-manifest", type=Path, required=True)
    value.add_argument("--authorization", type=Path, required=True)
    value.add_argument("--state", choices=("base", "naive_qlora"), required=True)
    value.add_argument("--precision", choices=("4bit", "float16"), required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    value.add_argument("--batch-size", type=int, required=True)
    return value


if __name__ == "__main__":
    capture(parser().parse_args())
