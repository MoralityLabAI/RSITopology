from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    registration = json.loads(args.registration.read_text())
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text()
    )
    result = json.loads(args.result.read_text())
    receipt = json.loads(args.receipt.read_text())
    sources = protocol["source_artifacts"]
    original_result = json.loads(
        (REPO / sources["result"]["path"]).read_text()
    )
    original_protocol = json.loads(
        (REPO / sources["protocol"]["path"]).read_text()
    )
    independent = json.loads(
        (REPO / sources["independent_verification"]["path"]).read_text()
    )
    checks = {}
    checks["registration_hash"] = (
        sha256(args.registration)
        == result["registration_sha256"]
        == receipt["registration_sha256"]
    )
    checks["result_hash"] = sha256(args.result) == receipt["result_sha256"]
    checks["protocol_hash"] = (
        sha256(REPO / registration["protocol_path"])
        == receipt["protocol_sha256"]
    )
    checks["repair_sealed_files"] = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    checks["source_hashes"] = all(
        sha256(REPO / source["path"]) == source["sha256"]
        for source in sources.values()
    )
    checks["original_science"] = all(
        passed
        for name, passed in original_result["gate_passes"].items()
        if name != "G9_prior_art_and_claim_boundary"
    )
    checks["original_failure_preserved"] = (
        not original_result["gate_passes"][
            "G9_prior_art_and_claim_boundary"
        ]
        and result["original_verdict_preserved"]
        == original_protocol["verdict_map"]["any_substantive_gate_fails"]
    )
    checks["independent_failure_isolation"] = sorted(
        name for name, passed in independent["checks"].items() if not passed
    ) == ["all_gates_pass", "verdict"]
    checks["prior_art_identifiers"] = sorted(
        row["identifier"] for row in original_protocol["prior_art"]
    ) == sorted(protocol["required_prior_art_identifiers"])
    checks["claim_boundary"] = (
        "ASMP-9 is resolved."
        in protocol["structured_claims"]["forbidden"]
        and "V0.26 itself passed."
        in protocol["structured_claims"]["forbidden"]
        and "no novelty is claimed" in original_protocol["claim_boundary"]
    )
    checks["gate_universe"] = set(result["gate_passes"]) == set(
        protocol["gate_ids"]
    )
    checks["all_gates_pass"] = all(result["gate_passes"].values())
    checks["verdict"] = (
        result["verdict"] == protocol["verdict_map"]["all_gates_pass"]
    )
    checks["repair_kind"] = (
        result["repair_kind"]
        == "mechanical_re_adjudication_no_new_scientific_run"
    )
    checks["resource_caps"] = (
        receipt["wall_seconds"] <= protocol["resource_caps"]["wall_seconds"]
        and receipt["peak_resident_bytes"]
        <= protocol["resource_caps"]["peak_resident_bytes"]
    )
    output = {
        "check_count": len(checks),
        "checks": checks,
        "pass": all(checks.values()),
        "receipt_sha256": sha256(args.receipt),
        "result_sha256": sha256(args.result),
        "verifier_sha256": sha256(Path(__file__)),
    }
    write_json_exclusive(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
