"""Deterministic receipts, configuration, and serialization helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
import csv
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any, Iterable, Mapping

import numpy as np
import scipy


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            jsonable(value),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return jsonable(asdict(value))
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(item) for item in value]
    return value


def content_sha256(value: Any) -> str:
    return sha256(canonical_json_bytes(value)).hexdigest()


def implementation_fingerprint() -> str:
    """Hash the complete executable package used by every atomic receipt."""

    root = Path(__file__).resolve().parent
    digest = sha256()
    for path in sorted(root.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    """Load JSON-syntax YAML without introducing a YAML dependency."""

    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{source} must use JSON syntax (which is valid YAML 1.2): {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("configuration root must be an object")
    if value.get("schema_version") != "confinement-experiment-config-v1":
        raise ValueError("unsupported or missing confinement config schema")
    return value


def write_bytes_compare_or_fail(path: str | Path, payload: bytes) -> bool:
    """Write once; return False when an identical artifact already exists."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_bytes() != payload:
            raise FileExistsError(f"refusing to replace different artifact: {target}")
        return False
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(target)
    return True


def write_json_compare_or_fail(path: str | Path, value: Any) -> bool:
    return write_bytes_compare_or_fail(path, canonical_json_bytes(value))


def write_csv_compare_or_fail(path: str | Path, rows: list[dict[str, Any]]) -> bool:
    if not rows:
        raise ValueError("cannot serialize an empty aggregate")
    fieldnames = sorted({key for row in rows for key in row})
    lines: list[str] = []
    from io import StringIO

    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                key: json.dumps(jsonable(value), sort_keys=True)
                if isinstance(value, (dict, list, tuple))
                else value
                for key, value in row.items()
            }
        )
    return write_bytes_compare_or_fail(path, stream.getvalue().encode("utf-8"))


def environment_receipt() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "cpu_count": os.cpu_count(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "blas_threads": {
            name: os.environ.get(name)
            for name in (
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        },
    }


def derived_seed(root_seed: int, identity: str) -> int:
    digest = sha256(identity.encode("utf-8")).digest()
    words = np.frombuffer(digest[:16], dtype=np.uint32)
    sequence = np.random.SeedSequence([int(root_seed), *(int(word) for word in words)])
    return int(sequence.generate_state(1, dtype=np.uint32)[0])


@dataclass(frozen=True)
class WorkUnit:
    experiment: str
    payload: dict[str, Any]
    root_seed: int
    implementation_sha256: str

    @property
    def scientific_identity(self) -> str:
        """Identity of the registered mathematical cell, independent of code."""

        return content_sha256(
            {
                "experiment": self.experiment,
                "payload": self.payload,
            }
        )

    @property
    def unit_id(self) -> str:
        return content_sha256(
            {
                "experiment": self.experiment,
                "payload": self.payload,
                "implementation_sha256": self.implementation_sha256,
            }
        )[:20]

    @property
    def seed(self) -> int:
        # Receipt filenames include the implementation hash so stale results
        # cannot be reused after a code change. Randomness must not: a plotting
        # or serialization edit must leave the registered scientific sample
        # unchanged.
        return derived_seed(self.root_seed, self.scientific_identity)


def checksum_manifest(paths: Iterable[Path], *, relative_to: Path) -> dict[str, str]:
    return {
        str(path.relative_to(relative_to)).replace("\\", "/"): file_sha256(path)
        for path in sorted(paths)
    }
