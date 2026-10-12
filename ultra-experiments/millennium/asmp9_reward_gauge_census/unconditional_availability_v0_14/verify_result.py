from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from experiment import parse_fraction, run_registry
from run_verification import (
    evaluate_scientific_gates,
    render_report,
    summarize_records,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    artifact_dir = args.artifact_dir.resolve()
    result = json.loads(
        (artifact_dir / "result_v0_14.json").read_text(encoding="utf-8")
    )
    receipt = json.loads(
        (artifact_dir / "receipt_v0_14.json").read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    replay_registry = run_registry(protocol["fresh_registry"])
    replay_summary = summarize_records(
        replay_registry["records"],
        alpha=parse_fraction(protocol["fresh_registry"]["alpha"]),
        balanced_nuisance=protocol["balanced_nuisance_ratio"],
        extreme_nuisance=protocol["extreme_nuisance_ratio"],
        interior_nuisance=protocol["interior_nuisance_ratio"],
        interior_epsilon=parse_fraction(
            protocol["interior_probability_floor"]
        ),
        ratio_ceiling=parse_fraction(
            protocol["maximum_extreme_to_balanced_excess_ratio"]
        ),
    )
    replay_gates = evaluate_scientific_gates(
        replay_registry, replay_summary, protocol
    )
    result_scientific_gates = {
        name: result["gates"][name] for name in replay_gates
    }
    limits = protocol["resource_limits"]
    checks = {
        "registration_hash": (
            sha256(registration_path)
            == receipt["registration_sha256"]
            == result["registration_sha256"]
        ),
        "sealed_inputs": all(
            sha256(REPO / relative) == expected
            for relative, expected in registration["sealed_files"].items()
        ),
        "output_hashes": all(
            sha256(artifact_dir / name) == expected
            for name, expected in receipt["output_hashes"].items()
        ),
        "output_hash_universe": set(receipt["output_hashes"])
        == {"result_v0_14.json", "RESULT_v0_14.md"},
        "protocol_identity": (
            result["protocol_id"]
            == receipt["protocol_id"]
            == protocol["protocol_id"]
        ),
        "registration_commit": (
            result["registration_commit"] == receipt["registration_commit"]
        ),
        "implementation_commit": (
            receipt["implementation_commit"]
            == registration["implementation_commit"]
        ),
        "binding_checks": all(result["binding_checks"].values()),
        "exact_registry_replay": replay_registry == result["registry"],
        "exact_summary_replay": replay_summary == result["summary"],
        "scientific_gate_replay": (
            replay_gates == result_scientific_gates
            and all(replay_gates.values())
        ),
        "rendered_report_replay": (
            (artifact_dir / "RESULT_v0_14.md").read_text(encoding="utf-8")
            == render_report(result)
        ),
        "resource_record": (
            result["resource_observation"]["gpu_used"] is False
            and result["elapsed_seconds"]
            <= limits["maximum_wall_seconds"]
            and result["resource_observation"]["peak_resident_bytes"]
            <= int(float(limits["maximum_ram_gib"]) * (1024**3))
        ),
        "claim_boundary": (
            result["claim_boundary"] == protocol["claim_boundary"]
        ),
        "all_gates_pass": all(result["gates"].values()),
        "verdict": result["verdict"] == protocol["success_verdict"],
    }
    verdict = "verified" if all(checks.values()) else "invalid"
    print(json.dumps({"checks": checks, "verdict": verdict}, indent=2))
    raise SystemExit(0 if verdict == "verified" else 1)


if __name__ == "__main__":
    main()
