from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_v0_1_1 as hardened  # noqa: E402


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path: Path, values: np.ndarray) -> Path:
    chunk = tmp_path / "chunks" / "x.npz"
    chunk.parent.mkdir()
    np.savez(chunk, activations=values)
    index = {
        "chunks": [
            {
                "chunk_id": "x",
                "path": "chunks/x.npz",
                "sha256": _sha(chunk),
                "prompt_ids": [f"p{i}" for i in range(len(values))],
                "row_count": len(values),
                "ambient_dimension": values.shape[1],
                "dtype": str(values.dtype),
            }
        ]
    }
    path = tmp_path / "capture_index.json"
    path.write_text(json.dumps(index), encoding="utf-8")
    return path


def test_indexed_chunk_validation_accepts_exact_fixture(tmp_path: Path) -> None:
    path = _fixture(tmp_path, np.arange(12, dtype=np.float32).reshape(3, 4))
    receipt = hardened.validate_indexed_chunks(path)
    assert receipt["all_indexed_chunks_valid"] is True
    assert receipt["chunk_count"] == 1


def test_indexed_chunk_validation_rejects_changed_bytes(tmp_path: Path) -> None:
    path = _fixture(tmp_path, np.ones((3, 4), dtype=np.float32))
    np.savez(tmp_path / "chunks" / "x.npz", activations=np.zeros((3, 4), dtype=np.float32))
    with pytest.raises(ValueError, match="hash mismatch"):
        hardened.validate_indexed_chunks(path)


def test_indexed_chunk_validation_rejects_nonfinite_values(tmp_path: Path) -> None:
    values = np.ones((3, 4), dtype=np.float32)
    values[0, 0] = np.nan
    path = _fixture(tmp_path, values)
    with pytest.raises(ValueError, match="nonfinite"):
        hardened.validate_indexed_chunks(path)


def test_indexed_chunk_validation_rejects_duplicate_universe(tmp_path: Path) -> None:
    path = _fixture(tmp_path, np.ones((3, 4), dtype=np.float32))
    value = json.loads(path.read_text(encoding="utf-8"))
    value["chunks"].append(dict(value["chunks"][0]))
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate chunk_id"):
        hardened.validate_indexed_chunks(path)
