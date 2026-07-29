from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f(value: Any) -> Fraction:
    return Fraction(str(value))


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

    registration = json.loads(args.registration.read_text(encoding="utf-8"))
    result = json.loads(args.result.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    sealed_ok = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    gates = result["gates"]
    primary = result["primary"]
    controls = result["controls"]
    risk = result["decision_controls"]["risk"]
    checks = {
        "all_gates_pass": (
            len(gates) == 12
            and all(record["pass"] for record in gates.values())
        ),
        "anisotropic_isotropic_radius": (
            f(controls["anisotropic"]["isotropic_radius"]) == Fraction(9, 10)
        ),
        "anisotropic_margin": (
            f(controls["anisotropic"]["margin"]) == Fraction(1, 5)
        ),
        "anisotropic_policy_pass": controls["anisotropic"]["policy"][
            "policy_identity_certified"
        ],
        "anisotropic_support": (
            f(controls["anisotropic"]["zonotope_support"])
            == Fraction(1, 100)
        ),
        "claim_boundary": (
            "resolution of ASMP-9"
            in protocol["claim_boundary"]["excludes"]
        ),
        "context_control": (
            controls["context_confounding"]["status"] == "context_confounded"
            and controls["context_confounding"]["projected_rank"] == 0
        ),
        "equality_inconclusive": (
            not result["decision_controls"]["equality"][
                "policy_identity_certified"
            ]
            and f(
                result["decision_controls"]["equality"]["margin_rows"][0][
                    "lower_margin"
                ]
            )
            == 0
        ),
        "mechanical_boundary": (
            controls["mechanical_boundary"]["status"]
            == "mechanical_contraction_unavailable"
            and f(controls["mechanical_boundary"]["mechanical_gain"]) == 1
        ),
        "primary_additive_radius": (
            f(primary["certificate"]["additive_radius"])
            == Fraction(37, 1500)
        ),
        "primary_direction_count": len(primary["direction_audits"]) == 7,
        "primary_direction_coverage": all(
            row["covered"] for row in primary["direction_audits"]
        ),
        "primary_mechanical_gain": (
            f(primary["certificate"]["mechanical_gain"]) == Fraction(1, 50)
        ),
        "primary_policy": (
            primary["policy"]["selected_policy"] == 4
            and primary["policy"]["policy_identity_certified"]
            and f(primary["policy"]["robust_regret_bound"]) == 0
        ),
        "primary_projected_rank": (
            primary["certificate"]["projected_rank"] == 3
        ),
        "primary_support": (
            f(primary["support_witness"]["attained_support"])
            == Fraction(90263, 588000)
        ),
        "primary_theta_hat": (
            tuple(map(f, primary["certificate"]["theta_hat"]))
            == (
                Fraction(5967, 4000),
                Fraction(-1193, 2400),
                Fraction(5949, 8000),
            )
        ),
        "protocol_hash": (
            receipt["protocol_sha256"]
            == sha256(REPO / registration["protocol_path"])
        ),
        "protocol_id": (
            result["protocol_id"] == "ASMP-9-JOINT-APPROXIMATE-v0.31"
        ),
        "registration_hash": (
            receipt["registration_sha256"] == sha256(args.registration)
        ),
        "resource_caps": (
            not result["resource"]["gpu_used"]
            and result["resource"]["wall_seconds"]
            <= protocol["resource_caps"]["wall_seconds"]
            and result["resource"]["peak_resident_bytes"]
            <= protocol["resource_caps"]["peak_resident_bytes"]
        ),
        "result_hash": receipt["result_sha256"] == sha256(args.result),
        "risk_bound_attained": (
            f(risk["actual_regret"]) == Fraction(9, 10)
            and f(risk["policy"]["robust_regret_bound"])
            == Fraction(9, 10)
        ),
        "sealed_files": sealed_ok,
        "semantic_cancellation": (
            f(controls["semantic_cancellation"]["structured_support"]) == 0
            and f(
                controls["semantic_cancellation"][
                    "naive_independent_support"
                ]
            )
            == Fraction(1, 5)
        ),
        "source_ablation_count": len(result["source_ablations"]) == 4,
        "source_ablations": all(
            row["full_support_covers"] and row["omission_exposes_error"]
            for row in result["source_ablations"]
        ),
        "support_witness": (
            primary["support_witness"]["attained_support"]
            == primary["direction_audits"][-1]["support"]
        ),
        "verdict": (
            result["verdict"]
            == "joint_approximate_boundary_established_v0_31"
            == receipt["verdict"]
        ),
    }
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
    if not output["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
