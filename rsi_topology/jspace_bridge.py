"""Sealed sparse-operator bridge from JSpace to spectral-bundle discovery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.sparse import csr_matrix


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _layout(operator: Any) -> dict[str, Any]:
    sheaf = operator.sheaf
    return {
        "vertex_ids": list(sheaf.vertex_ids),
        "vertex_dims": {key: int(value) for key, value in sheaf.vertex_dims.items()},
        "vertex_slices": {
            key: [int(value.start), int(value.stop)]
            for key, value in sheaf.vertex_slices.items()
        },
        "total_vertex_dim": int(sheaf.total_vertex_dim),
        "edge_ids": [edge.edge_id for edge in sheaf.edges],
    }


def write_operator_bundle(
    path: Path,
    operators: Iterable[Any],
    *,
    candidate_sites: Iterable[str],
    source_protocol_path: Path,
    source_seal_path: Path | None = None,
) -> dict[str, Any]:
    """Write normalized weighted Laplacians with one exact common-space layout."""

    if path.exists():
        raise FileExistsError(f"operator bundle is write-once: {path}")
    values = list(operators)
    if len(values) < 3:
        raise ValueError("operator bundle requires at least three prompt/context operators")
    layouts = [_layout(operator) for operator in values]
    if any(layout != layouts[0] for layout in layouts[1:]):
        raise ValueError("operators do not share one exact registered edit-space layout")
    sites = tuple(str(site) for site in candidate_sites)
    if not sites or len(set(sites)) != len(sites):
        raise ValueError("candidate_sites must be a nonempty unique set")
    missing_sites = sorted(set(sites) - set(layouts[0]["vertex_ids"]))
    if missing_sites:
        raise ValueError(f"candidate sites are absent from the common layout: {missing_sites}")
    keys: set[tuple[str, float]] = set()
    arrays: dict[str, np.ndarray] = {}
    records = []
    for index, operator in enumerate(values):
        operator_key = (str(operator.prompt_id), float(operator.norm))
        if operator_key in keys:
            raise ValueError(f"duplicate operator key: {operator_key}")
        keys.add(operator_key)
        matrix = csr_matrix(operator.laplacian, dtype=np.float64)
        if matrix.shape != (
            layouts[0]["total_vertex_dim"],
            layouts[0]["total_vertex_dim"],
        ):
            raise ValueError("operator Laplacian disagrees with registered layout")
        prefix = f"operator_{index:05d}"
        array_keys = {
            "data": f"{prefix}_data",
            "indices": f"{prefix}_indices",
            "indptr": f"{prefix}_indptr",
            "shape": f"{prefix}_shape",
        }
        arrays[array_keys["data"]] = matrix.data.astype(np.float64, copy=False)
        arrays[array_keys["indices"]] = matrix.indices.astype(np.int64, copy=False)
        arrays[array_keys["indptr"]] = matrix.indptr.astype(np.int64, copy=False)
        arrays[array_keys["shape"]] = np.asarray(matrix.shape, dtype=np.int64)
        records.append(
            {
                "prompt_id": operator_key[0],
                "norm": operator_key[1],
                "array_keys": array_keys,
                "largest_eigenvalue_pre_normalization": float(
                    operator.largest_eigenvalue
                ),
                "naturality_defect_float64": float(operator.naturality_defect),
            }
        )
    manifest = {
        "format": "rsi_topology_jspace_operator_bundle_v1",
        "source_protocol_path": str(source_protocol_path.resolve()),
        "source_protocol_sha256": sha256_file(source_protocol_path),
        "source_seal_path": (
            None if source_seal_path is None else str(source_seal_path.resolve())
        ),
        "source_seal_sha256": (
            None if source_seal_path is None else sha256_file(source_seal_path)
        ),
        "common_edit_space": layouts[0],
        "candidate_sites": list(sites),
        "operator_count": len(records),
        "operators": records,
    }
    arrays["manifest_json_utf8"] = np.frombuffer(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        dtype=np.uint8,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        np.savez_compressed(handle, **arrays)
    return manifest


def load_operator_bundle(
    path: Path, *, expected_sha256: str | None = None
) -> tuple[dict[str, Any], dict[str, csr_matrix]]:
    if expected_sha256 is not None and sha256_file(path) != expected_sha256:
        raise PermissionError("operator bundle hash does not match the sealed receipt")
    with np.load(path, allow_pickle=False) as archive:
        if "manifest_json_utf8" not in archive.files:
            raise ValueError("operator bundle is missing its manifest")
        manifest = json.loads(bytes(archive["manifest_json_utf8"]).decode("utf-8"))
        if manifest.get("format") != "rsi_topology_jspace_operator_bundle_v1":
            raise ValueError("unsupported operator bundle format")
        referenced = {"manifest_json_utf8"}
        output: dict[str, csr_matrix] = {}
        for record in manifest["operators"]:
            keys = record["array_keys"]
            if set(keys) != {"data", "indices", "indptr", "shape"}:
                raise ValueError("operator record has incomplete CSR references")
            for key in keys.values():
                if key not in archive.files or key in referenced:
                    raise ValueError("operator bundle has missing or reused arrays")
                referenced.add(key)
            shape_values = np.asarray(archive[keys["shape"]], dtype=np.int64)
            if shape_values.shape != (2,):
                raise ValueError("operator shape receipt is malformed")
            shape = tuple(int(value) for value in shape_values)
            matrix = csr_matrix(
                (
                    np.asarray(archive[keys["data"]], dtype=np.float64),
                    np.asarray(archive[keys["indices"]], dtype=np.int64),
                    np.asarray(archive[keys["indptr"]], dtype=np.int64),
                ),
                shape=shape,
            )
            if not np.isfinite(matrix.data).all():
                raise ValueError("operator bundle contains non-finite values")
            key = f"{record['prompt_id']}|norm={float(record['norm']):g}"
            if key in output:
                raise ValueError("operator bundle has duplicate semantic keys")
            output[key] = matrix
        if referenced != set(archive.files):
            raise ValueError("operator bundle contains unreferenced arrays")
    if len(output) != int(manifest["operator_count"]):
        raise ValueError("operator count does not match manifest")
    dimension = int(manifest["common_edit_space"]["total_vertex_dim"])
    if any(matrix.shape != (dimension, dimension) for matrix in output.values()):
        raise ValueError("operator matrices disagree with common edit-space dimension")
    return manifest, output


__all__ = ["load_operator_bundle", "sha256_file", "write_operator_bundle"]

