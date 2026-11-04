"""Prepare and seal the target-blind Qwen projector-tomography run."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rsi_topology.attestation import array_sha256
from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal
from rsi_topology.projector_tomography import (
    orthogonal_random_direction,
    reconstruct_rank_one,
)


DEFAULT_PROTOCOL = ROOT / "protocols" / "qwen08_projector_tomography_v0_1.json"
DEFAULT_OUTPUT = Path(r"D:\Research_Engine\runs\qwen08_projector_tomography_v0_1")
DEFAULT_WRAPPER = ROOT / "scripts" / "run_qwen_holonomy_jobobject.ps1"
DEFAULT_CLEANUP = Path(
    r"C:\Users\patri\.codex\skills\hrm-trainer\scripts\post_run_memory_cleanup.ps1"
)
DEFAULT_REPO_RECEIPT = (
    ROOT
    / "ultra-experiments"
    / "millennium"
    / "asmp1_qwen_projector_tomography"
    / "registration.json"
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _stable_seed(seed: int, value: str) -> int:
    return (seed + int.from_bytes(hashlib.sha256(value.encode()).digest()[:4], "big")) % 2**32


def _certificate_map(path: Path) -> dict[str, dict]:
    return {
        item["site_id"]: item
        for item in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    }


def prepare(
    protocol_path: Path,
    output: Path,
    wrapper: Path,
    cleanup: Path,
    repo_receipt: Path,
) -> None:
    protocol_path = protocol_path.resolve()
    protocol = _load(protocol_path)
    source = protocol["source_geometry"]
    manifest_path = (ROOT / source["prompt_manifest"]).resolve()
    manifest = _load(manifest_path)
    index_path = Path(source["capture_index"]).resolve()
    capture_root = Path(source["capture_root"]).resolve()
    certificate_path = Path(source["certificate_file"]).resolve()
    analysis_path = Path(source["analysis_result"]).resolve()
    index = _load(index_path)
    analysis_result = _load(analysis_path)
    certificates = _certificate_map(certificate_path)
    rows_by_id = {row["prompt_id"]: row for row in manifest["rows"]}
    output.mkdir(parents=True, exist_ok=True)

    directions, centers, random_directions, eigenvalues = [], [], [], []
    basis_receipts = []
    seed = int(protocol["intervention"]["random_seed"])
    for site in source["site_ids"]:
        layer = int(site.rsplit(".", 1)[1])
        certificate_id = f"base/L{layer}/graph_reachability/shard-00/rank-1"
        certificate = certificates.get(certificate_id)
        if certificate is None or certificate.get("attained_level") != source["required_certificate_level"]:
            raise ValueError(f"required certificate missing or insufficient: {certificate_id}")
        chunks = [
            item
            for item in index["chunks"]
            if item["site_id"] == site
            and item["context_shard"] == source["context_shard"]
            and item["half"] == source["basis_half"]
        ]
        if len(chunks) != 1:
            raise ValueError(f"expected one construction chunk for {site}")
        chunk = chunks[0]
        chunk_path = capture_root / chunk["path"]
        if sha256_file(chunk_path) != chunk["sha256"]:
            raise ValueError(f"chunk hash mismatch: {chunk_path}")
        activations = np.load(chunk_path)["activations"]
        selected_indices = [
            i
            for i, prompt_id in enumerate(chunk["prompt_ids"])
            if rows_by_id[prompt_id]["behavior_family"] == source["behavior_family"]
        ]
        labels = [rows_by_id[chunk["prompt_ids"][i]]["subcondition_id"] for i in selected_indices]
        direction, center, eigenvalue = reconstruct_rank_one(activations[selected_indices], labels)
        random_direction = orthogonal_random_direction(direction, seed=_stable_seed(seed, site))
        actual_hash = array_sha256(direction[:, None])
        node_receipts = [
            row
            for row in analysis_result["node_rank_filtrations"]
            if row["runtime_precision"] == "base"
            and row["site_id"] == site
            and row["behavior_family"] == source["behavior_family"]
            and row["context_shard"] == source["context_shard"]
        ]
        if len(node_receipts) != 1:
            raise ValueError(f"missing unique node receipt for {site}")
        rank_receipt = node_receipts[0]["rank_receipts"][0]
        discovery_hash = hashlib.sha256(
            np.asarray(direction[:, None], dtype="<f8").tobytes()
        ).hexdigest()
        expected_discovery_hash = rank_receipt["basis_by_half_sha256"][0]
        if discovery_hash != expected_discovery_hash:
            raise ValueError(f"reconstructed basis differs from discovery receipt: {site}")
        directions.append(direction)
        centers.append(center)
        random_directions.append(random_direction)
        eigenvalues.append(eigenvalue)
        basis_receipts.append(
            {
                "site_id": site,
                "certificate_site_id": certificate_id,
                "certificate_record_sha256": certificate["record_sha256"],
                "attained_level": certificate["attained_level"],
                "basis_sha256": actual_hash,
                "discovery_basis_sha256": discovery_hash,
                "expected_discovery_basis_sha256": expected_discovery_hash,
                "certificate_basis_hash_check": "exact construction-basis receipt match; vv^T is sign-gauge invariant",
                "source_chunk": str(chunk_path),
                "source_chunk_sha256": chunk["sha256"],
                "construction_row_count": len(selected_indices),
                "eigenvalue": eigenvalue,
                "random_direction_sha256": array_sha256(random_direction[:, None]),
            }
        )

    basis_path = output / "sealed_projectors.npz"
    np.savez(
        basis_path,
        selected=np.asarray(directions, dtype=np.float64),
        centers=np.asarray(centers, dtype=np.float64),
        matched_random=np.asarray(random_directions, dtype=np.float64),
        eigenvalues=np.asarray(eigenvalues, dtype=np.float64),
    )

    selected_rows = [
        row
        for row in manifest["rows"]
        if row["behavior_family"] == source["behavior_family"]
        and row["context_shard"] == source["context_shard"]
        and row["half"] == source["evaluation_half"]
        and int(row["within_half_index"]) < int(source["evaluation_rows_per_subcondition"])
    ]
    selected_rows.sort(key=lambda row: row["prompt_id"])
    prompt_path = output / "sealed_evaluation_prompts.json"
    write_once_or_equal(prompt_path, canonical_json_bytes({"rows": selected_rows}))

    run_id = "qwen08-projector-tomography-v01"
    result_dir = output / "result"
    command = [
        sys.executable,
        str((ROOT / "scripts" / "run_qwen08_projector_tomography.py").resolve()),
        "--protocol", str(protocol_path),
        "--registration", str((output / "registration.json").resolve()),
        "--output-dir", str(result_dir.resolve()),
        "--batch-size", str(protocol["resource_contract"]["batch_size"]),
    ]
    registration = {
        "schema_version": "qwen08_projector_tomography_registration_v0_1",
        "run_id": run_id,
        "protocol": {"path": str(protocol_path), "sha256": sha256_file(protocol_path)},
        "prompt_manifest": {"path": str(manifest_path), "sha256": sha256_file(manifest_path)},
        "capture_index": {"path": str(index_path), "sha256": sha256_file(index_path)},
        "certificate_file": {"path": str(certificate_path), "sha256": sha256_file(certificate_path)},
        "analysis_result": {"path": str(analysis_path), "sha256": sha256_file(analysis_path)},
        "sealed_projectors": {"path": str(basis_path.resolve()), "sha256": sha256_file(basis_path)},
        "sealed_evaluation_prompts": {"path": str(prompt_path.resolve()), "sha256": sha256_file(prompt_path)},
        "basis_receipts": basis_receipts,
        "prompt_count": len(selected_rows),
        "subcondition_count": len({row["subcondition_id"] for row in selected_rows}),
        "source_files": {
            str(path.resolve()): sha256_file(path)
            for path in (
                Path(__file__),
                ROOT / "scripts" / "run_qwen08_projector_tomography.py",
                ROOT / "scripts" / "analyze_qwen08_projector_tomography.py",
                ROOT / "rsi_topology" / "projector_tomography.py",
                wrapper,
                cleanup,
            )
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "torch", "transformers", "bitsandbytes", "accelerate")
            },
        },
        "exact_inner_command": command,
        "outcomes_read": False,
    }
    registration_path = output / "registration.json"
    write_once_or_equal(registration_path, canonical_json_bytes(registration))
    repo_receipt.parent.mkdir(parents=True, exist_ok=True)
    write_once_or_equal(repo_receipt, canonical_json_bytes(registration))
    caps = dict(protocol["resource_contract"])
    authorization = {
        "schema_version": "qwen_projector_tomography_authorization_v0_1",
        "run_id": run_id,
        "resource_caps": caps,
        "exact_inner_command": command,
        "wrapper_output_dir": str((output / "_wrapper").resolve()),
        "capture_parameters": {"output_dir": str(result_dir.resolve())},
        "hard_cap_wrapper": {"path": str(wrapper.resolve()), "sha256": sha256_file(wrapper)},
        "cleanup_script": {"path": str(cleanup.resolve()), "sha256": sha256_file(cleanup)},
        "registration": {"path": str(registration_path.resolve()), "sha256": sha256_file(registration_path)},
    }
    write_once_or_equal(output / "authorization.json", canonical_json_bytes(authorization))
    print(json.dumps({"status": "prepared", "output": str(output), "registration_sha256": sha256_file(registration_path), "prompt_count": len(selected_rows)}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--wrapper", type=Path, default=DEFAULT_WRAPPER)
    parser.add_argument("--cleanup", type=Path, default=DEFAULT_CLEANUP)
    parser.add_argument("--repo-receipt", type=Path, default=DEFAULT_REPO_RECEIPT)
    args = parser.parse_args()
    prepare(
        args.protocol,
        args.output_dir.resolve(),
        args.wrapper.resolve(),
        args.cleanup.resolve(),
        args.repo_receipt.resolve(),
    )


if __name__ == "__main__":
    main()
