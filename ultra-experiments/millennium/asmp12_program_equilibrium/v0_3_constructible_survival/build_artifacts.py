#!/usr/bin/env python3
"""Write a source-bound ASMP-12 v0.3.1 evidence bundle exactly once."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

import constructible_survival as primary
import run_constructible_survival as runner
import verify_constructible_survival as independent


HERE = Path(__file__).resolve().parent
BOUND_SOURCES = (
    "README.md",
    "PROTOCOL_v0_3.md",
    "CLAIM_BOUNDARY_v0_3.md",
    "protocol_v0_3_1.json",
    "constructible_survival.py",
    "run_constructible_survival.py",
    "verify_constructible_survival.py",
    "build_artifacts.py",
    "test_constructible_survival.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def compact_json(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


def write_lf_json(path: Path, payload: object) -> None:
    path.write_text(canonical_json(payload), encoding="utf-8", newline="\n")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=HERE, text=True).strip()


def ensure_source_checkpoint(source_commit: str) -> dict[str, str]:
    repository = Path(git("rev-parse", "--show-toplevel"))
    source_hashes = {}
    missing = []
    changed = []
    for name in BOUND_SOURCES:
        path = HERE / name
        relative = path.relative_to(repository).as_posix()
        try:
            committed = subprocess.check_output(
                ["git", "show", f"{source_commit}:{relative}"], cwd=HERE
            )
        except subprocess.CalledProcessError:
            missing.append(relative)
            continue
        current_hash = sha256(path)
        source_hashes[name] = current_hash
        if hashlib.sha256(committed).hexdigest() != current_hash:
            changed.append(relative)
    if missing or changed:
        raise RuntimeError(
            f"source checkpoint does not bind current sources; missing={missing}, changed={changed}"
        )
    return source_hashes


def jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"fraction": [value.numerator, value.denominator]}
    if isinstance(value, dict):
        items = [(jsonable(key), jsonable(item)) for key, item in value.items()]
        return {
            "mapping": sorted(
                items,
                key=lambda pair: compact_json(pair[0]),
            )
        }
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [jsonable(item) for item in value]
        return {"set": sorted(items, key=compact_json)}
    if value is None or isinstance(value, (bool, int, str)):
        return value
    raise TypeError(f"unsupported canonical evidence value: {type(value)!r}")


def digest_value(value: object) -> str:
    return hashlib.sha256(compact_json(jsonable(value))).hexdigest()


def evidence_roots(surface: dict[str, object], report: dict[str, object]) -> dict[str, str]:
    roots = {
        "manifest": sha256(independent.MANIFEST_PATH),
        "catalog_sequence": digest_value(surface["catalogs"]),
        "graph_key_registry": digest_value(tuple(surface["graphs"])),
        "cell_graphs": report["task_result"]["cell_graph_digest_root"],
        "budget_maps": digest_value(surface["graph_maps"]["budget_inclusions"]),
        "temptation_zigzags": digest_value(
            surface["graph_maps"]["temptation_adjacent_union_zigzags"]
        ),
        "cooperative_sink_events": digest_value(surface["cooperative_sink_events"]),
        "robustness_probes": digest_value(report["reliability"]["robustness_probes"]),
    }
    roots["root_of_roots"] = hashlib.sha256(compact_json(roots)).hexdigest()
    return roots


def build_bundle(source_commit: str) -> tuple[dict[str, object], ...]:
    source_hashes = ensure_source_checkpoint(source_commit)
    surface = primary.build_surface()
    report = runner.build_report_from_surface(surface)
    verification = independent.verify_surface(surface)
    roots = evidence_roots(surface, report)
    passed = bool(
        report["task_result"]["status"]
        == "finite_constructible_survival_correspondence_built"
        and all(report["reliability"]["gates"].values())
        and verification["verified"]
    )
    result = {
        **report,
        "schema_version": "asmp12_constructible_survival_v0_3_1_result_v1",
        "source_checkpoint": source_commit,
        "source_hashes": source_hashes,
        "evidence_roots": roots,
    }
    verification_record = {
        **verification,
        "schema_version": "asmp12_constructible_survival_v0_3_1_independent_verification_v1",
        "source_checkpoint": source_commit,
        "source_hashes": source_hashes,
        "evidence_roots": roots,
        "verifier": "verify_constructible_survival.verify_surface",
    }
    return result, verification_record, {
        "passed_before_artifact_binding": passed,
        "source_checkpoint": source_commit,
        "source_hashes": source_hashes,
        "evidence_roots": roots,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source_commit = args.source_commit or git("rev-parse", "HEAD")
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"write-once output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    result, verification, synthesis_seed = build_bundle(source_commit)
    result_path = output_dir / "result.json"
    write_lf_json(result_path, result)
    verification["result_sha256"] = sha256(result_path)
    verification_path = output_dir / "independent_verification.json"
    write_lf_json(verification_path, verification)

    binding_match = bool(
        verification["result_sha256"] == sha256(result_path)
        and verification["source_hashes"] == synthesis_seed["source_hashes"]
        and verification["evidence_roots"] == synthesis_seed["evidence_roots"]
    )
    passed = bool(synthesis_seed["passed_before_artifact_binding"] and binding_match)
    synthesis = {
        "schema_version": "asmp12_constructible_survival_v0_3_1_synthesis_receipt_v1",
        "verified": passed,
        "binding_match": binding_match,
        "bindings": {
            "result.json": sha256(result_path),
            "independent_verification.json": sha256(verification_path),
            "protocol_v0_3_1.json": sha256(independent.MANIFEST_PATH),
        },
        "source_checkpoint": source_commit,
        "source_hashes": synthesis_seed["source_hashes"],
        "evidence_roots": synthesis_seed["evidence_roots"],
        "conclusion_layers": {
            "task_result": (
                "finite_constructible_survival_correspondence_built"
                if passed
                else "not_established"
            ),
            "measurement_reliability": (
                "exact_registry_and_full_payload_replay_passed" if passed else "failed"
            ),
            "claim_support": (
                "registered_finite_constructible_correspondence_only" if passed else "none"
            ),
            "operation": "deterministic_cpu_exact_source_bound_bundle",
        },
    }
    write_lf_json(output_dir / "synthesis_receipt.json", synthesis)
    print(canonical_json(synthesis), end="")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
