"""Convert the locked Qwen base checkpoint to one-tensor float32 safetensors.

This helper is launched as a child of the registered Job Object.  Keeping the
conversion in a short-lived process ensures PyTorch's CPU allocator cache is
returned to Windows before the capture maps the converted tensors.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import torch
from safetensors import safe_open
from safetensors.torch import save_file


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
        with safe_open(
            str(model_path / shard_name), framework="pt", device="cpu"
        ) as archive:
            for checkpoint_key in sorted(keys):
                base_name = base_parameter_name(checkpoint_key)
                assert base_name is not None
                target = output_dir / f"parameter-{ordinal:04d}.safetensors"
                value = archive.get_tensor(checkpoint_key)
                converted = value.to(dtype=torch.float32)
                if converted.dtype != torch.float32:
                    raise RuntimeError("converter did not produce float32")
                temporary = target.with_suffix(target.suffix + ".tmp")
                save_file({base_name: converted.contiguous()}, str(temporary))
                temporary.replace(target)
                entries.append(
                    {
                        "base_parameter_name": base_name,
                        "checkpoint_key": checkpoint_key,
                        "path": target.name,
                        "sha256": sha256_file(target),
                        "shape": list(converted.shape),
                        "dtype": "float32",
                    }
                )
                del converted, value
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
