"""Hard-cap-only task-aligned Qwen activation capture for controller meshes."""

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

from rsi_topology.godel_capture import canonical_json_bytes, runtime_environment, sha256_file, write_once_or_equal
from rsi_topology.qwen_controller_task_capture import (
    AUTH_SCHEMA,
    AUTH_STATUS,
    INDEX_SCHEMA,
    chunk_id,
    load_protocol,
    validate_capture_index,
    validate_prompt_manifest,
)
from rsi_topology.qwen_state_capture import load_causal_protocol, validate_development_files


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    temporary.replace(path)


def _validate_authorization(
    value: Mapping[str, Any],
    *,
    args: argparse.Namespace,
    protocol: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> None:
    if value.get("schema_version") != AUTH_SCHEMA or value.get("status") != AUTH_STATUS:
        raise ValueError("controller-task capture is not authorized")
    if value.get("caps_confirmed_by_user") is not True:
        raise ValueError("resource caps were not explicitly confirmed")
    if value.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation is not a pass")
    if value.get("protocol_sha256") != sha256_file(args.protocol):
        raise ValueError("authorization protocol binding differs")
    if value.get("prompt_manifest_sha256") != sha256_file(args.prompt_manifest):
        raise ValueError("authorization prompt-manifest binding differs")
    if value.get("prompt_manifest_semantic_sha256") != manifest.get("manifest_semantic_sha256"):
        raise ValueError("authorization prompt semantic binding differs")
    if value.get("environment_lock") != runtime_environment():
        raise ValueError("runtime environment differs from authorization")
    expected_caps = protocol["resource_contract"]
    caps = value.get("resource_caps")
    if not isinstance(caps, Mapping):
        raise ValueError("authorization resource caps are absent")
    for name in (
        "memory_mb",
        "host_reserve_mb",
        "minimum_free_memory_mb",
        "cpu_percent",
        "io_mb_s",
        "timeout_seconds",
        "gpu_allowance_mb",
        "checkpoint_every_seconds",
        "swap_bytes",
    ):
        if float(caps.get(name, -1)) != float(expected_caps[name]):
            raise ValueError(f"authorization cap differs: {name}")
    parameters = value.get("capture_parameters")
    if not isinstance(parameters, Mapping):
        raise ValueError("authorization capture parameters are absent")
    if Path(str(parameters.get("output_dir", ""))).resolve() != args.output_dir.resolve():
        raise ValueError("authorized output directory differs")
    if int(parameters.get("batch_size", 0)) != args.batch_size:
        raise ValueError("authorized batch size differs")
    if args.batch_size != int(expected_caps["batch_size"]):
        raise ValueError("runtime batch size differs from protocol")
    for name in ("hard_cap_wrapper", "cleanup_script", "hard_cap_validation_receipt"):
        item = value.get(name)
        if not isinstance(item, Mapping):
            raise ValueError(f"authorization lacks {name}")
        path = Path(str(item.get("path", "")))
        if not path.is_file() or sha256_file(path) != item.get("sha256"):
            raise ValueError(f"authorized {name} is missing or changed")
    sources = value.get("source_paths")
    hashes = value.get("source_sha256")
    if not isinstance(sources, Mapping) or not isinstance(hashes, Mapping) or set(sources) != set(hashes):
        raise ValueError("authorization source universe is incomplete")
    for name, raw_path in sources.items():
        path = Path(str(raw_path))
        if not path.is_file() or sha256_file(path) != hashes[name]:
            raise ValueError(f"authorized source changed: {name}")


def _load_model(parent_protocol: Mapping[str, Any], gpu_mb: float):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    model_info = parent_protocol["development_model"]
    model_path = Path(model_info["local_path"])
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    if not torch.cuda.is_available():
        raise RuntimeError("registered controller-task capture requires CUDA")
    total_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
    torch.cuda.set_per_process_memory_fraction(min(0.99, float(gpu_mb) / total_mb), device=0)
    kwargs: dict[str, Any] = {
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

    disable_warmup = bool(model_info.get("loader", {}).get("disable_transformers_caching_allocator_warmup", False))
    original = modeling_utils.caching_allocator_warmup
    if disable_warmup:
        modeling_utils.caching_allocator_warmup = lambda *_args, **_kwargs: None
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path, **kwargs)
    finally:
        modeling_utils.caching_allocator_warmup = original
    model.eval()
    return model, tokenizer


def _resolve_module(model: Any, path: str) -> Any:
    current = model
    for token in path.split("."):
        current = current[int(token)] if token.isdigit() else getattr(current, token)
    return current


def _existing_chunks(output: Path, progress: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    completed = {}
    for row in progress.get("chunks", ()):
        path = output / str(row.get("path", ""))
        if not path.is_file() or sha256_file(path) != row.get("sha256"):
            raise ValueError("existing capture progress references a missing or changed chunk")
        completed[str(row["chunk_id"])] = dict(row)
    return completed


def capture(args: argparse.Namespace) -> None:
    import torch

    protocol = load_protocol(args.protocol)
    manifest = _load(args.prompt_manifest)
    validate_prompt_manifest(manifest, protocol=protocol)
    authorization = _load(args.authorization)
    _validate_authorization(authorization, args=args, protocol=protocol, manifest=manifest)
    parent_path = ROOT / protocol["parent_model_protocol"]["path"]
    if sha256_file(parent_path) != protocol["parent_model_protocol"]["sha256"]:
        raise ValueError("parent model protocol hash mismatch")
    parent = load_causal_protocol(parent_path)
    model_hashes = validate_development_files(parent, "base")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    progress_path = output / "capture_progress.json"
    index_path = output / "state_capture_index.json"
    if index_path.exists():
        existing_index = _load(index_path)
        validate_capture_index(existing_index, protocol=protocol, manifest=manifest, index_path=index_path)
        print(json.dumps(existing_index, indent=2, sort_keys=True))
        return
    progress = _load(progress_path) if progress_path.exists() else {"schema_version": "qwen08_controller_task_capture_progress_v0_1", "run_id": authorization["run_id"], "chunks": []}
    if progress.get("run_id") != authorization["run_id"]:
        raise ValueError("existing progress belongs to another run")
    completed = _existing_chunks(output, progress)
    rows_by_cell: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for application in protocol["controller_study"]["applications"]:
        for half in protocol["controller_study"]["halves"]:
            rows_by_cell[(application, half)] = sorted(
                [row for row in manifest["rows"] if row["application"] == application and row["geometry_half"] == half],
                key=lambda row: str(row["row_id"]),
            )
    sites = list(map(str, protocol["capture_contract"]["sites"]))
    pending = [cell for cell in rows_by_cell if any(chunk_id(cell[0], cell[1], site) not in completed for site in sites)]
    if pending:
        model, tokenizer = _load_model(parent, float(protocol["resource_contract"]["gpu_allowance_mb"]))
        base_model = model.model
        captured: dict[str, Tensor] = {}
        hooks = []

        def hook_for(site: str):
            def receive(_module, _inputs, value):
                hidden = value[0] if isinstance(value, tuple) else value
                captured[site] = hidden.detach()
            return receive

        for site in sites:
            hooks.append(_resolve_module(model, site).register_forward_hook(hook_for(site)))
        try:
            for application, half in pending:
                rows = rows_by_cell[(application, half)]
                site_values = {site: [] for site in sites}
                for start in range(0, len(rows), args.batch_size):
                    batch = rows[start : start + args.batch_size]
                    tokens = tokenizer(
                        [str(row["prompt"]) for row in batch],
                        padding=True,
                        truncation=True,
                        max_length=int(protocol["capture_contract"]["maximum_input_tokens"]),
                        return_tensors="pt",
                    )
                    tokens = {name: value.to("cuda:0") for name, value in tokens.items()}
                    captured.clear()
                    with torch.inference_mode():
                        base_model(**tokens, use_cache=False, return_dict=True)
                    if set(captured) != set(sites):
                        raise RuntimeError("not every registered activation hook fired")
                    final = tokens["attention_mask"].sum(dim=1).long() - 1
                    batch_indices = torch.arange(len(batch), device=final.device)
                    for site in sites:
                        selected = captured[site][batch_indices, final]
                        site_values[site].append(selected.float().cpu().numpy())
                    del tokens
                row_ids = [str(row["row_id"]) for row in rows]
                for site in sites:
                    identifier = chunk_id(application, half, site)
                    if identifier in completed:
                        continue
                    values = np.concatenate(site_values[site], axis=0).astype(np.float32, copy=False)
                    relative = Path("chunks") / f"{identifier}.npz"
                    path = output / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("xb") as handle:
                        np.savez_compressed(handle, activations=values)
                    record = {
                        "chunk_id": identifier,
                        "application": application,
                        "geometry_half": half,
                        "site": site,
                        "path": relative.as_posix(),
                        "sha256": sha256_file(path),
                        "row_ids": row_ids,
                        "row_count": len(row_ids),
                        "ambient_dimension": int(values.shape[1]),
                        "dtype": "float32",
                    }
                    progress["chunks"].append(record)
                    completed[identifier] = record
                    _atomic_json(progress_path, progress)
        finally:
            for handle in hooks:
                handle.remove()
            del base_model, model
            gc.collect()
            torch.cuda.empty_cache()
    chunks = sorted(completed.values(), key=lambda row: str(row["chunk_id"]))
    index: dict[str, Any] = {
        "schema_version": INDEX_SCHEMA,
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256_file(args.protocol),
        "study_config_sha256": protocol["controller_study"]["config_sha256"],
        "prompt_manifest_sha256": sha256_file(args.prompt_manifest),
        "prompt_manifest_semantic_sha256": manifest["manifest_semantic_sha256"],
        "authorization_sha256": sha256_file(args.authorization),
        "model_id": protocol["capture_contract"]["model_id"],
        "model_hashes": model_hashes,
        "quantization": protocol["capture_contract"]["quantization"],
        "token_position": protocol["capture_contract"]["token_position"],
        "chunks": chunks,
        "completed_unix": time.time(),
        "outcomes_consumed": False,
        "generation": False,
        "logits_materialized": False,
        "gradients": False,
        "weight_mutation": False,
    }
    write_once_or_equal(index_path, canonical_json_bytes(index))
    validate_capture_index(index, protocol=protocol, manifest=manifest, index_path=index_path)
    print(json.dumps(index, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--protocol", type=Path, default=ROOT / "protocols" / "qwen08_controller_task_capture_v0_1.json")
    value.add_argument("--prompt-manifest", type=Path, required=True)
    value.add_argument("--authorization", type=Path, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    value.add_argument("--batch-size", type=int, default=4)
    return value


if __name__ == "__main__":
    capture(parser().parse_args())
