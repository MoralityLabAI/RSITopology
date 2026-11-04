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
    parser.add_argument("--repair-registration", type=Path, required=True)
    parser.add_argument("--original-registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--independent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    repair = json.loads(
        args.repair_registration.read_text(encoding="utf-8")
    )
    original = json.loads(
        args.original_registration.read_text(encoding="utf-8")
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    independent = json.loads(args.independent.read_text(encoding="utf-8"))
    protocol = json.loads(
        (REPO / repair["protocol_path"]).read_text(encoding="utf-8")
    )
    checks = {
        "independent_pass": (
            independent["pass"] and independent["check_count"] == 29
        ),
        "original_registration_binding": (
            receipt["registration_sha256"]
            == sha256(args.original_registration)
        ),
        "original_science_sealed": all(
            sha256(REPO / relative) == expected
            for relative, expected in original["sealed_files"].items()
        ),
        "repair_registration_binding": all(
            sha256(REPO / relative) == expected
            for relative, expected in repair["sealed_files"].items()
        ),
        "repair_scope": (
            "only peak_resident_bytes" in protocol["allowed_change"]
            and len(protocol["forbidden_changes"]) == 6
        ),
        "result_hash": receipt["result_sha256"] == sha256(args.result),
        "scientific_verdict": (
            result["verdict"]
            == "joint_approximate_boundary_established_v0_31"
        ),
        "all_scientific_gates": (
            len(result["gates"]) == 12
            and all(row["pass"] for row in result["gates"].values())
        ),
        "failure_preserved": (
            json.loads(
                (HERE.parent / "failure_receipt_v0_31.json").read_text(
                    encoding="utf-8"
                )
            )["status"]
            == "unavailable_resource_meter_failure_before_output"
        ),
        "resource_live": (
            not result["resource"]["gpu_used"]
            and 0 < result["resource"]["peak_resident_bytes"]
            <= protocol["resource_caps"]["peak_resident_bytes"]
        ),
    }
    output = {
        "check_count": len(checks),
        "checks": checks,
        "pass": all(checks.values()),
        "repair_registration_sha256": sha256(args.repair_registration),
        "result_sha256": sha256(args.result),
        "verifier_sha256": sha256(Path(__file__)),
    }
    write_json_exclusive(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))
    if not output["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
