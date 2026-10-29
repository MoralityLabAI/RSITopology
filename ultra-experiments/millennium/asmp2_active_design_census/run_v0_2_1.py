"""Performance-only v0.2.1 runner for the ASMP-2 active-design census."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
import tracemalloc
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import sympy as sp

import run as parent


HERE = Path(__file__).resolve().parent


def fast_census(protocol: dict[str, Any], amendment: dict[str, Any]) -> dict[str, Any]:
    points = parent.corners(int(protocol["dimension"]))
    features = parent.feature_matrix(points)
    families = parent.deployment_families(points)
    subset_count = 1 << points.shape[0]
    feature_count = features.shape[1]
    projectors = np.empty((subset_count, feature_count, feature_count), dtype=np.float64)
    ranks = np.empty(subset_count, dtype=np.int16)
    projectors[0] = np.eye(feature_count)
    ranks[0] = 0
    residual_tolerance = float(amendment["residual_squared_rank_tolerance"])
    for mask in range(1, subset_count):
        least_bit = mask & -mask
        environment = least_bit.bit_length() - 1
        previous = mask ^ least_bit
        prior = projectors[previous]
        residual = prior @ features[environment]
        norm_squared = float(residual @ residual)
        if norm_squared > residual_tolerance:
            projectors[mask] = prior - np.outer(residual, residual) / norm_squared
            projectors[mask] = (projectors[mask] + projectors[mask].T) / 2
            ranks[mask] = ranks[previous] + 1
        else:
            projectors[mask] = prior
            ranks[mask] = ranks[previous]
    scores = {name: np.empty(subset_count, dtype=np.float64) for name in families}
    chunk_size = int(amendment["score_chunk_size"])
    for name, targets in families.items():
        target_features = features[list(targets)]
        for start in range(0, subset_count, chunk_size):
            end = min(start + chunk_size, subset_count)
            projected = np.einsum("nij,tj->nti", projectors[start:end], target_features, optimize=True)
            values = np.einsum("nti,ti->nt", projected, target_features, optimize=True)
            scores[name][start:end] = np.maximum(0.0, np.max(values, axis=1))
        scores[name][scores[name] < 1e-12] = 0.0
    decimals = int(protocol["numeric_contract"]["score_round_decimals_for_ties_and_digest"])
    digest = hashlib.sha256()
    for mask in range(subset_count):
        row = [parent.quantized(float(scores[name][mask]), decimals) for name in families]
        digest.update(f"{mask}|{int(ranks[mask])}|{'|'.join(map(str, row))}\n".encode())
    return {"points": points, "features": features, "families": families, "scores": scores, "ranks": ranks, "digest": digest.hexdigest()}


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--amendment", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    amendment_path = args.amendment.resolve()
    amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
    if amendment.get("schema_version") != "asmp2_active_design_amendment_v0_2_1":
        raise ValueError("unexpected amendment schema")
    parent_protocol_path = HERE / amendment["parent_protocol"]
    if parent.sha256_file(parent_protocol_path) != amendment["parent_protocol_sha256"]:
        raise ValueError("parent protocol hash mismatch")
    protocol = json.loads(parent_protocol_path.read_text(encoding="utf-8"))
    sealed = (
        amendment_path, parent_protocol_path, HERE / "CLAIM_PACKET.md", HERE / "README.md", HERE / "run.py",
        HERE / "verify_result.py", HERE / "test_active_design.py", HERE / "README_v0_2_1.md",
        HERE / "CLAIM_PACKET_v0_2_1.md", Path(__file__).resolve(), HERE / "verify_result_v0_2_1.py",
        HERE / "test_active_design_v0_2_1.py",
    )
    output_dir = args.output_dir.resolve()
    if any(output_dir == path or output_dir in path.parents for path in sealed):
        raise ValueError("output directory aliases a sealed input")
    result_path = output_dir / "result_v0_2_1.json"
    receipt_path = output_dir / "receipt_v0_2_1.json"
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("registered v0.2.1 output already exists")
    registration = parent.bind_committed_inputs(sealed)
    original_census = parent.exhaustive_census
    parent.exhaustive_census = lambda _protocol: fast_census(_protocol, amendment)
    tracemalloc.start()
    started = time.perf_counter()
    try:
        result = parent.run_registered(protocol)
    finally:
        parent.exhaustive_census = original_census
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result["schema_version"] = "asmp2_active_design_result_v0_2_1"
    result["protocol_id"] = amendment["protocol_id"]
    result["amendment"] = {
        "scope": amendment["amendment_scope"],
        "scientific_contract_changes": amendment["scientific_contract_changes"],
        "parent_protocol_sha256": amendment["parent_protocol_sha256"],
    }
    ceiling = amendment["resource_ceiling"]
    resource_pass = elapsed <= ceiling["wall_seconds"] and peak <= ceiling["python_peak_bytes"]
    result["resource_receipt"] = {"elapsed_seconds": elapsed, "python_tracemalloc_peak_bytes": peak, "pass": resource_pass, "wall_ceiling_seconds": ceiling["wall_seconds"], "python_peak_ceiling_bytes": ceiling["python_peak_bytes"]}
    if not resource_pass:
        result["instrument_status"] = "unavailable"
        result["evidence_label"] = "unavailable_resource_cap"
        result["runner_gate_pass"] = False
        result["stage_decision"] = ceiling["on_exceed"]
    result["registration"] = registration
    result["protocol_sha256"] = parent.sha256_file(parent_protocol_path)
    result["amendment_sha256"] = parent.sha256_file(amendment_path)
    payload = parent.canonical_json(result).encode()
    parent.write_once(result_path, payload)
    receipt = {
        "schema_version": "asmp2_active_design_receipt_v0_2_1",
        "git_commit_at_run": registration["commit"],
        "git_tracked_diff_sha256_at_run": registration["tracked_diff_sha256"],
        "parent_protocol_sha256": parent.sha256_file(parent_protocol_path),
        "amendment_sha256": parent.sha256_file(amendment_path),
        "claim_packet_sha256": parent.sha256_file(HERE / "CLAIM_PACKET_v0_2_1.md"),
        "runner_sha256": parent.sha256_file(Path(__file__).resolve()),
        "verifier_sha256": parent.sha256_file(HERE / "verify_result_v0_2_1.py"),
        "tests_sha256": parent.sha256_file(HERE / "test_active_design_v0_2_1.py"),
        "result_sha256": hashlib.sha256(payload).hexdigest(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "sympy": sp.__version__, "platform": platform.platform()},
    }
    parent.write_once(receipt_path, parent.canonical_json(receipt).encode())
    print(parent.canonical_json({"instrument_status": result["instrument_status"], "evidence_label": result["evidence_label"], "stage_decision": result["stage_decision"], "elapsed_seconds": elapsed, "result": str(result_path)}), end="")
    return 0 if result["runner_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
