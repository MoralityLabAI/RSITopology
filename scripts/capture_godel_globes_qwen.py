"""Outcome-free Qwen activation capture for the registered Godel grid.

This entry point must run inside an independently validated hard-cap wrapper.
It refuses to start without a run authorization that binds the protocol,
prompt manifest, explicit resource caps, and cleanup path.  It performs forward
passes only: no generation, gradients, scoring, intervention, or weight write.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import (
    CAPTURE_SCHEMA,
    canonical_json_bytes,
    canonical_json_sha256,
    capture_chunk_id,
    load_protocol,
    prompt_rows_for_chunk,
    runtime_environment,
    sha256_file,
    validate_prompt_manifest,
    write_once_or_equal,
)


def _event(path: Path, event: str, **fields: Any) -> None:
    payload = {"time_unix": time.time(), "event": event, **fields}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")


def _validate_authorization(
    value: Mapping[str, Any],
    *,
    protocol_path: Path,
    manifest_path: Path,
    output_dir: Path,
    device: str,
    batch_size: int,
) -> None:
    if value.get("status") != "authorized_for_godel_capture":
        raise ValueError("capture authorization status is not launch-authorized")
    if value.get("protocol_sha256") != sha256_file(protocol_path):
        raise ValueError("capture authorization does not bind the protocol")
    if value.get("prompt_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("capture authorization does not bind the prompt manifest bytes")
    if value.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap wrapper has not passed validation")
    if value.get("caps_confirmed_by_user") is not True:
        raise ValueError("resource caps have not been explicitly confirmed")
    caps = value.get("resource_caps")
    if not isinstance(caps, Mapping):
        raise ValueError("capture authorization lacks resource_caps")
    positive = (
        "memory_mb",
        "cpu_percent",
        "io_mb_s",
        "timeout_seconds",
        "gpu_allowance_mb",
        "checkpoint_every_seconds",
    )
    if any(float(caps.get(name, 0)) <= 0 for name in positive):
        raise ValueError("all registered resource caps must be explicit and positive")
    if int(caps.get("swap_bytes", -1)) != 0:
        raise ValueError("Godel capture requires zero registered swap")
    for name in ("hard_cap_wrapper", "cleanup_script"):
        artifact = value.get(name)
        if not isinstance(artifact, Mapping):
            raise ValueError(f"authorization lacks {name}")
        path = Path(str(artifact.get("path", "")))
        if not path.is_file() or sha256_file(path) != artifact.get("sha256"):
            raise ValueError(f"authorization {name} is missing or changed")
    validation_artifact = value.get("hard_cap_validation_receipt")
    if not isinstance(validation_artifact, Mapping):
        raise ValueError("authorization lacks hard_cap_validation_receipt")
    validation_path = Path(str(validation_artifact.get("path", "")))
    if (
        not validation_path.is_file()
        or sha256_file(validation_path) != validation_artifact.get("sha256")
    ):
        raise ValueError("authorization hard-cap validation receipt is missing or changed")
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    if (
        validation.get("schema_version")
        != "qwen_holonomy_hard_cap_validation_v0_1"
        or validation.get("hard_cap_validation_status") != "passed"
    ):
        raise ValueError("hard-cap validation receipt is not a registered pass")
    if validation.get("wrapper", {}).get("sha256") != value["hard_cap_wrapper"]["sha256"]:
        raise ValueError("hard-cap validation receipt does not bind authorized wrapper")
    if validation.get("cleanup", {}).get("sha256") != value["cleanup_script"]["sha256"]:
        raise ValueError("hard-cap validation receipt does not bind authorized cleanup")
    if value.get("environment_lock") != runtime_environment():
        raise ValueError("runtime environment differs from the sealed capture environment")
    paths = value.get("source_paths")
    hashes = value.get("source_sha256")
    if not isinstance(paths, Mapping) or not isinstance(hashes, Mapping) or set(paths) != set(hashes):
        raise ValueError("authorization source universe is incomplete")
    for name, source_path in paths.items():
        path = Path(str(source_path))
        if not path.is_file() or sha256_file(path) != hashes[name]:
            raise ValueError(f"authorized source changed: {name}")
    parameters = value.get("capture_parameters")
    if not isinstance(parameters, Mapping):
        raise ValueError("authorization lacks capture_parameters")
    if Path(str(parameters.get("output_dir", ""))).resolve() != output_dir.resolve():
        raise ValueError("capture output directory differs from authorization")
    if parameters.get("device") != device or int(parameters.get("batch_size", 0)) != batch_size:
        raise ValueError("capture device or batch size differs from authorization")


def _resolve_module(model: Any, path: str) -> Any:
    value = model
    tokens = path.split(".")
    # The frozen site names use the CausalLM wrapper's ``model.layers``
    # namespace.  The live capture deliberately loads the corresponding base
    # transformer because logits are prohibited and the LM head is not on any
    # registered causal path.  Strip only that wrapper prefix; the remaining
    # module identity is byte-for-byte the same checkpoint object.
    if tokens and tokens[0] == "model" and not hasattr(value, "model"):
        tokens = tokens[1:]
    for token in tokens:
        if token.isdigit():
            value = value[int(token)]
        else:
            value = getattr(value, token)
    return value


def _promote_floating_state_to_float32(model: Any, torch: Any) -> None:
    """Promote native-bf16 checkpoint state one tensor at a time.

    The locked safetensors are stored as bf16.  Direct float32 conversion in
    the Windows Transformers loader crashes inside torch_cpu.dll on this host.
    Incremental promotion produces the same representable float32 values while
    avoiding a second model-sized conversion allocation.
    """

    with torch.no_grad():
        for parameter in model.parameters():
            if parameter.is_floating_point() and parameter.dtype != torch.float32:
                parameter.data = parameter.data.to(dtype=torch.float32)
        for buffer in model.buffers():
            if buffer.is_floating_point() and buffer.dtype != torch.float32:
                buffer.data = buffer.data.to(dtype=torch.float32)


def _extract_base_transformer(wrapper_model: Any) -> Any:
    """Detach the registered base transformer from a CausalLM loader shell."""

    base_model = wrapper_model.model
    wrapper_model.model = None
    wrapper_model.lm_head = None
    return base_model


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    temporary.replace(path)


def _load_progress(path: Path, *, run_id: str) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "godel_capture_progress_v0_1", "run_id": run_id, "chunks": []}
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("run_id") != run_id:
        raise ValueError("existing capture progress belongs to another run")
    return value


def _partial_group_paths(
    output: Path, *, runtime: str, shard: str, half: str
) -> tuple[Path, Path]:
    root = output / "partials" / runtime / shard
    return root / f"{half}.npz", root / f"{half}.json"


def _write_partial_group(
    output: Path,
    *,
    runtime: str,
    shard: str,
    half: str,
    sites: list[str],
    prompt_ids: list[str],
    captured: Mapping[str, list[np.ndarray]],
) -> tuple[Path, Path]:
    """Write an atomic, hash-bound partial shard/half checkpoint."""

    data_path, metadata_path = _partial_group_paths(
        output, runtime=runtime, shard=shard, half=half
    )
    data_path.parent.mkdir(parents=True, exist_ok=True)
    arrays: dict[str, np.ndarray] = {}
    site_keys: dict[str, str] = {}
    for index, site in enumerate(sites):
        key = f"site_{index:03d}"
        values = np.concatenate(captured[site], axis=0).astype(np.float32, copy=False)
        if len(values) != len(prompt_ids) or not np.all(np.isfinite(values)):
            raise RuntimeError(f"partial checkpoint row/finiteness failure at {site}")
        arrays[key] = values
        site_keys[site] = key
    temporary = data_path.with_suffix(data_path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez(handle, **arrays)
    temporary.replace(data_path)
    metadata = {
        "schema_version": "godel_capture_partial_group_v0_1",
        "runtime_precision": runtime,
        "context_shard": shard,
        "half": half,
        "prompt_ids": prompt_ids,
        "row_count": len(prompt_ids),
        "site_keys": site_keys,
        "data_sha256": sha256_file(data_path),
    }
    _atomic_json(metadata_path, metadata)
    return data_path, metadata_path


def _load_partial_group(
    output: Path,
    *,
    runtime: str,
    shard: str,
    half: str,
    sites: list[str],
    expected_prompt_ids: list[str],
) -> tuple[int, dict[str, np.ndarray]]:
    data_path, metadata_path = _partial_group_paths(
        output, runtime=runtime, shard=shard, half=half
    )
    if not data_path.exists() and not metadata_path.exists():
        return 0, {}
    if not data_path.is_file() or not metadata_path.is_file():
        raise ValueError("partial checkpoint is incomplete")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("schema_version") != "godel_capture_partial_group_v0_1":
        raise ValueError("partial checkpoint schema mismatch")
    expected_identity = {
        "runtime_precision": runtime,
        "context_shard": shard,
        "half": half,
    }
    if any(metadata.get(name) != value for name, value in expected_identity.items()):
        raise ValueError("partial checkpoint identity mismatch")
    prompt_ids = metadata.get("prompt_ids")
    if (
        not isinstance(prompt_ids, list)
        or prompt_ids != expected_prompt_ids[: len(prompt_ids)]
        or int(metadata.get("row_count", -1)) != len(prompt_ids)
    ):
        raise ValueError("partial checkpoint prompt prefix mismatch")
    if metadata.get("data_sha256") != sha256_file(data_path):
        raise ValueError("partial checkpoint data hash mismatch")
    site_keys = metadata.get("site_keys")
    if not isinstance(site_keys, Mapping) or set(site_keys) != set(sites):
        raise ValueError("partial checkpoint site universe mismatch")
    restored: dict[str, np.ndarray] = {}
    with np.load(data_path, allow_pickle=False) as archive:
        if set(archive.files) != set(site_keys.values()):
            raise ValueError("partial checkpoint array universe mismatch")
        for site in sites:
            values = np.asarray(archive[str(site_keys[site])], dtype=np.float32)
            if len(values) != len(prompt_ids) or not np.all(np.isfinite(values)):
                raise ValueError(f"partial checkpoint values invalid at {site}")
            restored[site] = values
    return len(prompt_ids), restored


def _remove_partial_group(
    output: Path, *, runtime: str, shard: str, half: str
) -> None:
    data_path, metadata_path = _partial_group_paths(
        output, runtime=runtime, shard=shard, half=half
    )
    for path in (metadata_path, data_path):
        if path.exists():
            path.unlink()


def capture(args: argparse.Namespace) -> None:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as error:  # pragma: no cover - optional live dependency
        raise RuntimeError("live capture requires torch and transformers") from error

    protocol_path = args.protocol.resolve()
    manifest_path = args.prompt_manifest.resolve()
    protocol = load_protocol(protocol_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_prompt_manifest(manifest)
    authorization = json.loads(args.authorization.read_text(encoding="utf-8"))
    _validate_authorization(
        authorization,
        protocol_path=protocol_path,
        manifest_path=manifest_path,
        output_dir=args.output_dir,
        device=args.device,
        batch_size=args.batch_size,
    )
    model_path = Path(protocol["model_lock"]["local_path"])
    for name, expected in protocol["model_lock"]["files"].items():
        target = model_path / name
        if not target.is_file() or sha256_file(target) != expected:
            raise ValueError(f"model lock mismatch: {name}")
    if args.batch_size < 1:
        raise ValueError("batch_size must be positive")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    events = output / "events.jsonl"
    summary_path = output / "summary.json"
    progress_path = output / "capture_progress.json"
    run_id = str(authorization["run_id"])
    checkpoint_every_seconds = float(
        authorization["resource_caps"]["checkpoint_every_seconds"]
    )
    progress = _load_progress(progress_path, run_id=run_id)
    completed = {item["chunk_id"]: item for item in progress["chunks"]}
    tokenizer = None
    model = None
    handles = []
    chunks = list(progress["chunks"])
    started = time.time()
    status = "failed"
    abort_reason = None
    loaded_runtime = None
    peak_cuda_mb = 0.0
    try:
        _event(events, "start", run_id=run_id, batch_size=args.batch_size)
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        for runtime in protocol["runtime_precisions"]:
            loaded_runtime = runtime
            dtype = torch.float32 if runtime == "full_float32" else torch.bfloat16
            _event(events, "runtime_load_start", runtime=runtime)
            # The Windows AutoModel loader crashes while reconciling this
            # CausalLM-authored checkpoint. Use the checkpoint's native loader
            # at stored bf16, then detach the base and discard the wrapper/head
            # before promotion or any forward pass. No logits are materialized.
            wrapper_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                local_files_only=True,
                dtype=torch.bfloat16,
                low_cpu_mem_usage=True,
            )
            _event(events, "runtime_wrapper_loaded", runtime=runtime)
            model = _extract_base_transformer(wrapper_model).to(args.device)
            del wrapper_model
            gc.collect()
            _event(events, "runtime_base_extracted", runtime=runtime)
            if dtype == torch.float32:
                _event(events, "runtime_promotion_start", runtime=runtime)
                _promote_floating_state_to_float32(model, torch)
                _event(events, "runtime_promotion_completed", runtime=runtime)
            model.eval()
            _event(events, "runtime_loaded", runtime=runtime)
            captured: dict[str, list[np.ndarray]] = {
                site: [] for site in protocol["candidate_sites"]
            }
            current_indices = None

            def make_hook(site: str):
                def hook(_module, _inputs, output_value):
                    nonlocal current_indices
                    tensor = output_value[0] if isinstance(output_value, tuple) else output_value
                    if current_indices is None or tensor.ndim != 3:
                        raise RuntimeError(f"unexpected hooked output at {site}")
                    batch_indices = torch.arange(tensor.shape[0], device=tensor.device)
                    selected = tensor[batch_indices, current_indices]
                    captured[site].append(selected.detach().to(torch.float32).cpu().numpy())
                return hook

            for site in protocol["candidate_sites"]:
                handles.append(_resolve_module(model, site).register_forward_hook(make_hook(site)))

            for shard_index in range(int(manifest["context_shards"])):
                shard = f"shard-{shard_index:02d}"
                for half in manifest["halves"]:
                    rows = prompt_rows_for_chunk(manifest, context_shard=shard, half=half)
                    required_ids = {
                        capture_chunk_id(runtime, site, shard, half)
                        for site in protocol["candidate_sites"]
                    }
                    if required_ids <= set(completed):
                        _remove_partial_group(
                            output, runtime=runtime, shard=shard, half=half
                        )
                        _event(events, "chunk_group_skipped", runtime=runtime, shard=shard, half=half)
                        continue
                    for site in captured:
                        captured[site].clear()
                    prompt_ids = [item["prompt_id"] for item in rows]
                    partial_count, restored = _load_partial_group(
                        output,
                        runtime=runtime,
                        shard=shard,
                        half=half,
                        sites=list(protocol["candidate_sites"]),
                        expected_prompt_ids=prompt_ids,
                    )
                    if partial_count:
                        for site, values in restored.items():
                            captured[site].append(values)
                        _event(
                            events,
                            "partial_checkpoint_restored",
                            runtime=runtime,
                            shard=shard,
                            half=half,
                            row_count=partial_count,
                        )
                    last_partial_checkpoint = time.monotonic()
                    for start in range(partial_count, len(rows), args.batch_size):
                        batch = rows[start : start + args.batch_size]
                        encoded = tokenizer(
                            [item["prompt"] for item in batch],
                            padding=True,
                            return_tensors="pt",
                        )
                        encoded = {key: value.to(args.device) for key, value in encoded.items()}
                        current_indices = encoded["attention_mask"].sum(dim=1) - 1
                        with torch.inference_mode():
                            model(**encoded, use_cache=False)
                        if torch.cuda.is_available():
                            peak_cuda_mb = max(
                                peak_cuda_mb,
                                torch.cuda.max_memory_allocated() / (1024 * 1024),
                            )
                        del encoded
                        processed = start + len(batch)
                        if (
                            time.monotonic() - last_partial_checkpoint
                            >= checkpoint_every_seconds
                            and processed < len(rows)
                        ):
                            _write_partial_group(
                                output,
                                runtime=runtime,
                                shard=shard,
                                half=half,
                                sites=list(protocol["candidate_sites"]),
                                prompt_ids=prompt_ids[:processed],
                                captured=captured,
                            )
                            last_partial_checkpoint = time.monotonic()
                            _event(
                                events,
                                "partial_checkpoint",
                                runtime=runtime,
                                shard=shard,
                                half=half,
                                row_count=processed,
                            )
                    current_indices = None
                    for site in protocol["candidate_sites"]:
                        values = np.concatenate(captured[site], axis=0).astype(np.float32, copy=False)
                        if len(values) != len(rows) or not np.all(np.isfinite(values)):
                            raise RuntimeError(f"capture row/finiteness failure at {site}")
                        chunk_id = capture_chunk_id(runtime, site, shard, half)
                        relative = (
                            Path("chunks")
                            / runtime
                            / site.replace(".", "__")
                            / f"{shard}--{half}.npz"
                        )
                        target = output / relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        np.savez(target, activations=values)
                        entry = {
                            "chunk_id": chunk_id,
                            "runtime_precision": runtime,
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
                        if chunk_id not in completed:
                            chunks.append(entry)
                            completed[chunk_id] = entry
                    progress = {
                        "schema_version": "godel_capture_progress_v0_1",
                        "run_id": run_id,
                        "chunks": sorted(chunks, key=lambda item: item["chunk_id"]),
                        "last_completed_group": {
                            "runtime": runtime,
                            "context_shard": shard,
                            "half": half,
                        },
                    }
                    _atomic_json(progress_path, progress)
                    _remove_partial_group(
                        output, runtime=runtime, shard=shard, half=half
                    )
                    _event(events, "checkpoint", runtime=runtime, shard=shard, half=half, chunk_count=len(chunks))

            for handle in handles:
                handle.remove()
            handles.clear()
            del model
            model = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
                if hasattr(torch.cuda, "ipc_collect"):
                    torch.cuda.ipc_collect()
            _event(events, "runtime_released", runtime=runtime)

        index = {
            "schema_version": CAPTURE_SCHEMA,
            "protocol_id": protocol["protocol_id"],
            "protocol_sha256": canonical_json_sha256(protocol),
            "protocol_file_sha256": sha256_file(protocol_path),
            "prompt_manifest_sha256": sha256_file(manifest_path),
            "capture_kind": "real_model_target_blind",
            "run_id": run_id,
            "authorization_sha256": sha256_file(args.authorization),
            "outcomes_read": False,
            "weight_mutation": False,
            "generation_performed": False,
            "final_nonpadding_prompt_token": True,
            "attention_masked_padding": True,
            "runtime_precisions": list(protocol["runtime_precisions"]),
            "candidate_sites": list(protocol["candidate_sites"]),
            "chunks": sorted(chunks, key=lambda item: item["chunk_id"]),
        }
        # The analyzer binds canonical manifest content; store both byte and
        # canonical hashes so external authorizations can bind exact bytes.
        index["prompt_manifest_sha256"] = canonical_json_sha256(manifest)
        index["prompt_manifest_file_sha256"] = sha256_file(manifest_path)
        write_once_or_equal(output / "capture_index.json", canonical_json_bytes(index))
        status = "completed"
    except Exception as error:
        abort_reason = f"{type(error).__name__}:{error}"
        _event(events, "abort", reason=abort_reason, loaded_runtime=loaded_runtime)
        raise
    finally:
        for handle in handles:
            handle.remove()
        handles.clear()
        if model is not None:
            del model
        if tokenizer is not None:
            del tokenizer
        gc.collect()
        if "torch" in locals() and torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
        summary = {
            "schema_version": "godel_capture_summary_v0_1",
            "run_id": run_id,
            "status": status,
            "abort_reason": abort_reason,
            "elapsed_seconds": time.time() - started,
            "chunks_completed": len(chunks),
            "peak_cuda_allocated_mb": peak_cuda_mb,
            "owned_process_cleanup": "delegated_to_registered_outer_wrapper",
            "model_objects_released": True,
            "cuda_cache_released": True,
        }
        _atomic_json(summary_path, summary)
        _event(events, "finish", status=status, summary=str(summary_path))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--prompt-manifest", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=8)
    capture(parser.parse_args())


if __name__ == "__main__":
    main()
