"""Independent replay verifier for ASMP-8 v0.2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from frontier import canonical_json, frontier_csv, run_census


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
    protocol_path = HERE / "protocol_v0_2.json"
    registration_path = HERE / "registration_v0_2.json"
    result_path = artifact_dir / "result_v0_2.json"
    frontier_path = artifact_dir / "frontier_v0_2.csv"
    witnesses_path = artifact_dir / "witnesses_v0_2.json"
    report_path = artifact_dir / "RESULT_v0_2.md"
    receipt_path = artifact_dir / "receipt_v0_2.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

    replay_result, replay_rows, replay_witnesses = run_census(protocol)
    core_keys = [
        "schema_version",
        "policy_count",
        "proxy_improving_policy_count",
        "registered_epsilon",
        "phase_counts",
        "coordinate_minimality",
        "controls",
        "claim_boundary",
    ]
    checks = {
        "artifact_hashes_match": all(
            sha256(artifact_dir / payload["path"]) == payload["sha256"]
            for payload in receipt["artifacts"].values()
        ),
        "registration_hash_matches": sha256(registration_path) == receipt["registration_sha256"],
        "protocol_hash_matches": sha256(protocol_path) == receipt["protocol_sha256"],
        "registered_sources_match": all(
            sha256(REPO_ROOT / relative) == expected
            for relative, expected in registration["source_hashes"].items()
        ),
        "scientific_core_replays": all(result[key] == replay_result[key] for key in core_keys),
        "core_gates_replay": all(
            result["gates"][key] == replay_result["gates"][key]
            for key in replay_result["gates"]
        ),
        "frontier_replays_byte_exact": frontier_path.read_text(encoding="utf-8") == frontier_csv(replay_rows),
        "witnesses_replay_exact": json.loads(witnesses_path.read_text(encoding="utf-8")) == replay_witnesses,
        "runner_gate_count_and_pass": len(result["gates"]) == 8 and all(gate["pass"] for gate in result["gates"].values()),
        "verdict_exact": result["verdict"] == "dual_frontier_validated",
        "report_claim_boundary_present": result["claim_boundary"] in report_path.read_text(encoding="utf-8"),
    }
    passed = all(checks.values())
    return {
        "schema_version": "asmp8_dual_frontier_verification_v0_2",
        "instrument_status": "valid" if passed else "invalid",
        "decision": "pass" if passed else "invalid_stop",
        "checks": checks,
        "claim_boundary": protocol["claim_boundary"],
    }


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=HERE / "artifacts_v0_2")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_dir = args.artifact_dir.resolve()
    output = args.output.resolve() if args.output else artifact_dir / "verification_v0_2.json"
    result = verify(artifact_dir)
    write_once(output, canonical_json(result).encode("utf-8"))
    print(canonical_json(result), end="")
    return 0 if result["decision"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())

