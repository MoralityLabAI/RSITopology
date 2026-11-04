"""Verification adapter for ASMP-2 v0.2.2 plus v0.2.1 scientific replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any, Iterable

import run as parent
import verify_result_v0_2_1 as scientific_verifier


HERE = Path(__file__).resolve().parent


def verify(result_path: Path, receipt_path: Path) -> dict[str, Any]:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    amendment_path = HERE / "protocol_v0_2_2.json"
    amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
    checks = {
        "result_hash_matches_receipt": parent.sha256_file(result_path) == receipt.get("result_sha256"),
        "scientific_parent_hash_matches": parent.sha256_file(HERE / "protocol_v0_2.json") == amendment["scientific_parent_sha256"] == receipt.get("scientific_parent_sha256"),
        "performance_parent_hash_matches": parent.sha256_file(HERE / "protocol_v0_2_1.json") == amendment["performance_parent_sha256"] == receipt.get("performance_parent_sha256"),
        "amendment_hash_matches_receipt": parent.sha256_file(amendment_path) == receipt.get("amendment_sha256"),
        "claim_hash_matches_receipt": parent.sha256_file(HERE / "CLAIM_PACKET_v0_2_2.md") == receipt.get("claim_packet_sha256"),
        "verifier_hash_matches_receipt": parent.sha256_file(Path(__file__).resolve()) == receipt.get("verifier_sha256"),
        "schema_exact": result.get("schema_version") == "asmp2_active_design_result_v0_2_2",
        "runner_valid": result.get("instrument_status") == "valid" and result.get("runner_gate_pass") is True,
        "scientific_contract_unchanged": result.get("amendment", {}).get("scientific_contract_changes") == "none",
        "resource_measurement_pass": result.get("resource_receipt", {}).get("pass") is True,
        "operational_margin_positive": result.get("resource_receipt", {}).get("operational_elapsed_seconds", 1e9) < amendment["resource_measurement"]["operational_wall_ceiling_seconds"],
        "rss_below_ceiling": result.get("resource_receipt", {}).get("process_peak_rss_bytes", 1 << 62) < amendment["resource_measurement"]["process_peak_rss_bytes"],
        "registration_commit_agrees": result.get("registration", {}).get("commit") == receipt.get("git_commit_at_run"),
    }
    compatibility_result = dict(result)
    compatibility_result["schema_version"] = "asmp2_active_design_result_v0_2_1"
    compatibility_result["amendment"] = {
        "scope": "implementation_performance_only",
        "scientific_contract_changes": "none",
        "parent_protocol_sha256": amendment["scientific_parent_sha256"],
    }
    with tempfile.TemporaryDirectory(prefix="asmp2_v022_verify_") as directory:
        temporary = Path(directory)
        compat_result_path = temporary / "result.json"
        compat_result_payload = parent.canonical_json(compatibility_result).encode()
        compat_result_path.write_bytes(compat_result_payload)
        compatibility_receipt = {
            "result_sha256": hashlib.sha256(compat_result_payload).hexdigest(),
            "parent_protocol_sha256": parent.sha256_file(HERE / "protocol_v0_2.json"),
            "amendment_sha256": parent.sha256_file(HERE / "protocol_v0_2_1.json"),
            "claim_packet_sha256": parent.sha256_file(HERE / "CLAIM_PACKET_v0_2_1.md"),
            "verifier_sha256": parent.sha256_file(HERE / "verify_result_v0_2_1.py"),
            "git_commit_at_run": result.get("registration", {}).get("commit"),
        }
        compat_receipt_path = temporary / "receipt.json"
        compat_receipt_path.write_text(parent.canonical_json(compatibility_receipt), encoding="utf-8")
        scientific = scientific_verifier.verify(compat_result_path, compat_receipt_path)
    checks["opposite_parent_scientific_replay_passes"] = scientific["stage_decision"] == "pass"
    checks["scientific_label_matches_replay"] = scientific["evidence_label"] == result.get("evidence_label")
    passed = all(checks.values())
    return {
        "schema_version": "asmp2_active_design_verification_v0_2_2",
        "instrument_status": "valid" if passed else "invalid",
        "G8_independent_verification": {"pass": passed, "checks": checks, "scientific_replay": scientific["G8_independent_verification"]},
        "stage_decision": "pass" if passed else "invalid",
        "evidence_label": scientific["evidence_label"] if passed else "not_established_invalid_instrument",
        "claim_boundary": "Resource-repaired execution with opposite-parent replay of the unchanged finite scientific contract; no general ASMP-2 inference.",
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.result.is_file() or not args.receipt.is_file():
        raise FileNotFoundError("result and receipt required")
    verification = verify(args.result.resolve(), args.receipt.resolve())
    parent.write_once(args.output.resolve(), parent.canonical_json(verification).encode())
    print(parent.canonical_json(verification), end="")
    return 0 if verification["stage_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

