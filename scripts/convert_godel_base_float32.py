"""Convert the locked Qwen base checkpoint to one-tensor float32 safetensors.

The converter deliberately avoids both PyTorch and memory mapping.  On Windows,
mapping a multi-gigabyte safetensors shard consumes Job Object commit even when
only one tensor is requested, while PyTorch may retain the source allocation
after dtype promotion.  Parsing offsets and widening bounded byte chunks keeps
the conversion job's resident and committed memory independent of shard size.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import time

import numpy as np


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_safetensors_header(handle: object) -> tuple[int, dict[str, object]]:
    prefix = handle.read(8)
    if len(prefix) != 8:
        raise ValueError("truncated safetensors header length")
    header_length = struct.unpack("<Q", prefix)[0]
    header_bytes = handle.read(header_length)
    if len(header_bytes) != header_length:
        raise ValueError("truncated safetensors header")
    header = json.loads(header_bytes.decode("utf-8"))
    if not isinstance(header, dict):
        raise ValueError("safetensors header must be an object")
    return 8 + header_length, header


def _float32_safetensors_header(
    tensor_name: str, shape: list[int], byte_count: int
) -> bytes:
    value = {
        tensor_name: {
            "dtype": "F32",
            "shape": shape,
            "data_offsets": [0, byte_count],
        }
    }
    raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
    raw += b" " * ((-len(raw)) % 8)
    return struct.pack("<Q", len(raw)) + raw


def _widen_chunk(raw: bytes, source_dtype: str) -> bytes:
    if source_dtype == "BF16":
        if len(raw) % 2:
            raise ValueError("BF16 tensor byte count is not element-aligned")
        words = np.frombuffer(raw, dtype="<u2")
        return (words.astype("<u4") << np.uint32(16)).view("<f4").tobytes()
    if source_dtype == "F16":
        if len(raw) % 2:
            raise ValueError("F16 tensor byte count is not element-aligned")
        return np.frombuffer(raw, dtype="<f2").astype("<f4").tobytes()
    if source_dtype == "F32":
        if len(raw) % 4:
            raise ValueError("F32 tensor byte count is not element-aligned")
        return raw
    raise ValueError(f"unsupported checkpoint tensor dtype: {source_dtype}")


def _write_float32_tensor(
    *,
    shard_handle: object,
    data_start: int,
    tensor_name: str,
    tensor_metadata: dict[str, object],
    temporary: Path,
    chunk_bytes: int = 8 * 1024 * 1024,
) -> tuple[str, list[int]]:
    source_dtype = str(tensor_metadata.get("dtype"))
    shape = [int(value) for value in tensor_metadata.get("shape", [])]
    offsets = tensor_metadata.get("data_offsets")
    if not isinstance(offsets, list) or len(offsets) != 2:
        raise ValueError(f"invalid data offsets for {tensor_name}")
    start, end = (int(offsets[0]), int(offsets[1]))
    if start < 0 or end < start:
        raise ValueError(f"invalid data interval for {tensor_name}")
    source_element_bytes = {"BF16": 2, "F16": 2, "F32": 4}.get(source_dtype)
    if source_element_bytes is None:
        raise ValueError(f"unsupported checkpoint tensor dtype: {source_dtype}")
    element_count = int(np.prod(shape, dtype=np.int64)) if shape else 1
    if end - start != element_count * source_element_bytes:
        raise ValueError(f"shape/byte-count mismatch for {tensor_name}")
    output_bytes = element_count * 4
    header = _float32_safetensors_header(tensor_name, shape, output_bytes)
    digest = hashlib.sha256()
    shard_handle.seek(data_start + start)
    remaining = end - start
    with temporary.open("wb") as output:
        output.write(header)
        digest.update(header)
        while remaining:
            requested = min(chunk_bytes, remaining)
            requested -= requested % source_element_bytes
            raw = shard_handle.read(requested)
            if len(raw) != requested:
                raise ValueError(f"truncated tensor payload for {tensor_name}")
            widened = _widen_chunk(raw, source_dtype)
            output.write(widened)
            digest.update(widened)
            remaining -= requested
    return digest.hexdigest(), shape


def base_parameter_name(checkpoint_key: str) -> str | None:
    if checkpoint_key == "lm_head.weight":
        return None
    if not checkpoint_key.startswith("model."):
        raise ValueError(f"unexpected checkpoint key outside base model: {checkpoint_key}")
    return checkpoint_key.removeprefix("model.")


def append_event(path: Path, event: str, **payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"event": event, "time_unix": time.time(), **payload}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def convert(model_path: Path, output_dir: Path, events: Path) -> Path:
    index_path = model_path / "model.safetensors.index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    weight_map = index.get("weight_map")
    if not isinstance(weight_map, dict):
        raise ValueError("locked checkpoint index lacks weight_map")
    output_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    grouped: dict[str, list[str]] = {}
    for checkpoint_key, shard_name in weight_map.items():
        if base_parameter_name(str(checkpoint_key)) is None:
            continue
        grouped.setdefault(str(shard_name), []).append(str(checkpoint_key))
    ordinal = 0
    for shard_name, keys in sorted(grouped.items()):
        with (model_path / shard_name).open("rb") as shard_handle:
            data_start, shard_header = _read_safetensors_header(shard_handle)
            for checkpoint_key in sorted(keys):
                base_name = base_parameter_name(checkpoint_key)
                assert base_name is not None
                metadata = shard_header.get(checkpoint_key)
                if not isinstance(metadata, dict):
                    raise ValueError(
                        f"checkpoint tensor missing from shard: {checkpoint_key}"
                    )
                target = output_dir / f"parameter-{ordinal:04d}.safetensors"
                temporary = target.with_suffix(target.suffix + ".tmp")
                append_event(
                    events,
                    "float32_conversion_parameter_started",
                    parameter=base_name,
                    parameter_ordinal=ordinal,
                )
                tensor_hash, shape = _write_float32_tensor(
                    shard_handle=shard_handle,
                    data_start=data_start,
                    tensor_name=base_name,
                    tensor_metadata=metadata,
                    temporary=temporary,
                )
                temporary.replace(target)
                entries.append(
                    {
                        "base_parameter_name": base_name,
                        "checkpoint_key": checkpoint_key,
                        "path": target.name,
                        "sha256": tensor_hash,
                        "shape": shape,
                        "dtype": "float32",
                    }
                )
                ordinal += 1
                append_event(
                    events,
                    "float32_conversion_checkpoint",
                    parameters_completed=ordinal,
                )
    manifest = {
        "schema_version": "godel_float32_conversion_cache_v0_1",
        "source_index_sha256": sha256_file(index_path),
        "parameter_count": len(entries),
        "entries": entries,
    }
    manifest_path = output_dir / "manifest.json"
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    temporary.replace(manifest_path)
    append_event(events, "float32_conversion_completed", parameter_count=len(entries))
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    args = parser.parse_args()
    convert(args.model_path.resolve(), args.output_dir.resolve(), args.events.resolve())


if __name__ == "__main__":
    main()
