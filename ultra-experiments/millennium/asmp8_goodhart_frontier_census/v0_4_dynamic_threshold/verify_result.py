"""Independent replay verifier for ASMP-8 v0.4."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from dynamic_threshold import canonical_json, rows_csv, run_dynamic
from run import CDF_FIELDS, CONDITION_FIELDS, POLICY_FIELDS


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def verify(artifact_dir: Path) -> dict[str, Any]:
    protocol_path = HERE / "protocol_v0_4.json"
    registration_path = HERE / "registration_v0_4.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    result = json.loads((artifact_dir / "result_v0_4.json").read_text(encoding="utf-8"))
    receipt = json.loads((artifact_dir / "receipt_v0_4.json").read_text(encoding="utf-8"))
    replay, conditions, policies, cdf = run_dynamic(protocol)
    core_keys = [
        "schema_version", "streams_per_error_family", "checkpoints", "condition_count",
        "policy_condition_count", "focus", "claim_boundary",
    ]
    checks = {
        "artifact_hashes_match": all(
            sha256(artifact_dir / item["path"]) == item["sha256"]
            for item in receipt["artifacts"].values()
        ),
        "registration_hash_matches": sha256(registration_path) == receipt["registration_sha256"],
        "protocol_hash_matches": sha256(protocol_path) == receipt["protocol_sha256"],
        "registered_sources_match": all(
            sha256(REPO_ROOT / relative) == expected
            for relative, expected in registration["source_hashes"].items()
        ),
        "scientific_core_replays": all(result[key] == replay[key] for key in core_keys),
        "scientific_gates_replay": all(
            result["gates"][key] == replay["gates"][key] for key in replay["gates"]
        ),
        "conditions_replay_byte_exact": (
            artifact_dir / "condition_summary_v0_4.csv"
        ).read_text(encoding="utf-8") == rows_csv(conditions, CONDITION_FIELDS),
        "policies_replay_byte_exact": (
            artifact_dir / "policy_thresholds_v0_4.csv"
        ).read_text(encoding="utf-8") == rows_csv(policies, POLICY_FIELDS),
        "cdf_replay_byte_exact": (
            artifact_dir / "crossing_cdf_v0_4.csv"
        ).read_text(encoding="utf-8") == rows_csv(cdf, CDF_FIELDS),
        "gate_count": len(result["gates"]) == 8,
        "claim_boundary_present": result["claim_boundary"] in (
            artifact_dir / "RESULT_v0_4.md"
        ).read_text(encoding="utf-8"),
    }
    passed = all(checks.values())
    return {
        "schema_version": "asmp8_dynamic_threshold_verification_v0_4",
        "instrument_status": "valid" if passed else "invalid",
        "decision": "pass" if passed else "invalid_stop",
        "checks": checks,
        "claim_boundary": protocol["claim_boundary"],
    }


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=HERE / "artifacts_v0_4")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_dir = args.artifact_dir.resolve()
    output = args.output.resolve() if args.output else artifact_dir / "verification_v0_4.json"
    result = verify(artifact_dir)
    write_once(output, canonical_json(result).encode("utf-8"))
    print(canonical_json(result), end="")
    return 0 if result["decision"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
