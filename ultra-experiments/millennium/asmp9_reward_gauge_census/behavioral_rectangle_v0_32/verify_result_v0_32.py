from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Any) -> Fraction:
    return Fraction(value)


def majority_error(repeats: int, probability: Fraction) -> Fraction:
    return sum(
        (
            comb(repeats, correct)
            * probability**correct
            * (1 - probability) ** (repeats - correct)
            for correct in range((repeats - 1) // 2 + 1)
        ),
        Fraction(0),
    )


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
    protocol_path = REPO / registration["protocol_path"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    gates = result["gates"]
    checks: dict[str, bool] = {}

    checks["protocol_id"] = (
        result["protocol_id"] == "ASMP-9-BEHAVIORAL-RECTANGLE-v0.32"
    )
    checks["verdict"] = (
        result["verdict"]
        == "behavioral_rectangle_boundary_established_v0_32"
        == receipt["verdict"]
    )
    checks["gate_count"] = len(gates) == 12
    checks["all_gates_pass"] = all(row["pass"] for row in gates.values())
    checks["registration_hash"] = (
        sha256(args.registration) == receipt["registration_sha256"]
    )
    checks["protocol_hash"] = (
        sha256(protocol_path) == receipt["protocol_sha256"]
    )
    checks["result_hash"] = sha256(args.result) == receipt["result_sha256"]
    checks["sealed_files"] = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    checks["chronology"] = (
        registration["registered_at_utc"]
        == receipt["registered_at_utc"]
        < receipt["started_at_utc"]
        <= receipt["finished_at_utc"]
    )
    checks["population_queries"] = (
        result["primary"]["population_query_count"] == 48
        and result["primary"]["transcript_lower_bound"] == 48
        and gates["G1_population_acquisition"]["exact_recovery"]
    )
    checks["operator"] = (
        gates["G2_rectangle_algebra"]["operator_rank"] == 6
        and gates["G2_rectangle_algebra"]["operator_shape"] == [6, 12]
        and all(
            q(value) == 0
            for value in gates["G2_rectangle_algebra"]["additive_residuals"]
        )
    )
    checks["coverage"] = (
        gates["G3_complete_coverage"]["omission_count"] == 12
        and all(
            row["nonadditive"] and row["observed_cells_unchanged"]
            for row in gates["G3_complete_coverage"]["witnesses"]
        )
    )
    checks["shared_geometry"] = (
        q(gates["G4_shared_uncertainty_geometry"]["structured_support"])
        == Fraction(1, 4)
        and q(
            gates["G4_shared_uncertainty_geometry"][
                "independent_residual_support"
            ]
        )
        == Fraction(1, 2)
    )
    checks["three_states"] = gates["G5_three_state_semantics"] == {
        "additive": "approximately_additive_certified",
        "inconclusive": "inconclusive",
        "interaction": "interaction_certified",
        "pass": True,
    }
    mixture = gates["G6_mixture_affinity_liveness"]["controls"]
    checks["mixture_controls"] = (
        mixture["consistent"]["decision"] == "mixture_affinity_certified"
        and q(mixture["consistent"]["residual"]) == 0
        and mixture["distorted"]["decision"] == "mixture_affinity_rejected"
        and q(mixture["distorted"]["residual"]) == Fraction(1, 16)
        and mixture["uncertain"]["decision"] == "inconclusive"
    )
    checks["no_go"] = (
        gates["G7_access_no_go"]["ordinal_transcript_equal"]
        and gates["G7_access_no_go"]["row_local_coordinates_equal"]
        and q(
            gates["G7_access_no_go"]["ordinal_interactive_residual"][0]
        )
        == Fraction(4, 9)
    )
    finite = gates["G8_finite_sample"]
    probability = Fraction(3, 4)
    checks["finite_sample"] = (
        finite["minimum_odd_repeats"] == 43
        and q(finite["family_bound"]) == 48 * majority_error(43, probability)
        and q(finite["previous_odd_bound"])
        == 48 * majority_error(41, probability)
        and q(finite["family_bound"]) <= Fraction(1, 100)
        and q(finite["previous_odd_bound"]) > Fraction(1, 100)
        and finite["chance_unavailable"]
    )
    checks["handoff"] = (
        len(result["handoff"]["semantic_incidence"]) == 6
        and len(result["handoff"]["semantic_incidence"][0]) == 12
        and gates["G9_v031_handoff"]["shared_cell_count"] > 0
    )
    caps = protocol["resource_caps"]
    checks["resources"] = (
        not result["resource"]["gpu_used"]
        and result["resource"]["wall_seconds"] <= caps["wall_seconds"]
        and result["resource"]["peak_resident_bytes"]
        <= caps["peak_resident_bytes"]
    )
    checks["claim_boundary"] = (
        "resolution of ASMP-9" in protocol["claim_boundary"]["excludes"]
        and "validating expected utility for humans or models"
        in protocol["claim_boundary"]["excludes"]
    )

    verification = {
        "check_count": len(checks),
        "checks": checks,
        "pass": all(checks.values()),
        "receipt_sha256": sha256(args.receipt),
        "result_sha256": sha256(args.result),
        "verifier_sha256": sha256(Path(__file__)),
    }
    write_json_exclusive(args.output, verification)
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
