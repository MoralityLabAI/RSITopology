from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from experiment import run_fresh_liveness
from optimized_experiment_v0_13_1 import (
    run_power_calibration_streaming,
)
from run_verification import (
    REPO,
    peak_resident_bytes,
    sha256,
    validate_registration,
    write_json,
    write_text,
)


def render_report(result: dict[str, Any]) -> str:
    liveness = result["liveness"]
    calibration = result["power_calibration"]
    powers = [
        record["exact_power"]["decimal"] for record in calibration["records"]
    ]
    lines = [
        "# ASMP-9 conditional-fiber quotient verification v0.13.1",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "## Gates",
        "",
    ]
    for name, passed in result["gates"].items():
        lines.append(f"- **{name}:** {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Fresh conditional-fiber census",
            "",
            f"- graphs: {liveness['graph_count']}",
            f"- graph/sample cells: {liveness['cell_count']}",
            "- gauge-factor mismatches: "
            + str(liveness["gauge_factor_mismatch_count"]),
            "- normalized-law mismatches: "
            + str(liveness["normalized_law_mismatch_count"]),
            "- rank-above-cycle-rank mismatches: "
            + str(liveness["rank_upper_mismatch_count"]),
            "",
            "## Fresh conditional-power calibration",
            "",
            f"- cells: {calibration['cell_count']}",
            f"- minimum exact power: {min(powers):.9f}",
            f"- maximum exact power: {max(powers):.9f}",
            "- exact-size mismatches: "
            + str(calibration["size_mismatch_count"]),
            "- formula mismatches: "
            + str(calibration["formula_mismatch_count"]),
            "- exact representation: "
            + calibration["exact_representation"],
            "",
            "The registered sample counts are calibration points, not "
            "monotone critical thresholds.",
            "",
            "## Claim boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(
            f"refusing to overwrite output directory: {args.output_dir}"
        )
    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    amendment = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    base_protocol = json.loads(
        (REPO / amendment["base_protocol_path"]).read_text(encoding="utf-8")
    )
    if not amendment["scientific_specification_unchanged"]:
        raise RuntimeError("repair does not preserve scientific specification")

    started = time.perf_counter()
    registration_commit, binding = validate_registration(
        registration_path, registration
    )
    liveness = run_fresh_liveness(base_protocol["fresh_liveness_graphs"])
    calibration = run_power_calibration_streaming(
        base_protocol["power_calibration"]
    )
    elapsed = time.perf_counter() - started
    peak_bytes = peak_resident_bytes()
    limits = base_protocol["resource_limits"]
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_graph_arithmetic": (
            liveness["graph_arithmetic_mismatch_count"] == 0
            and liveness["mass_mismatch_count"] == 0
        ),
        "G2_scalar_nuisance_cancellation": (
            liveness["gauge_factor_mismatch_count"] == 0
            and liveness["normalized_law_mismatch_count"] == 0
        ),
        "G3_visible_quotient": (
            liveness["rank_upper_mismatch_count"] == 0
            and liveness["missing_full_rank_graph_count"] == 0
            and liveness["missing_deficient_graph_count"] == 0
        ),
        "G4_nonvacuous_statuses": (
            liveness["zero_full_mass_graph_count"] == 0
            and liveness["zero_deficient_mass_graph_count"] == 0
        ),
        "G5_one_cycle_formula": (
            calibration["formula_mismatch_count"] == 0
        ),
        "G6_exact_conditional_test": (
            calibration["likelihood_ratio_mismatch_count"] == 0
            and calibration["size_mismatch_count"] == 0
            and calibration["nonpositive_power_gain_count"] == 0
        ),
        "G7_fresh_power_calibration": (
            calibration["cell_count"]
            == len(base_protocol["power_calibration"]["cells"])
            and calibration["power_band_mismatch_count"] == 0
        ),
        "G8_claim_boundary_telemetry": (
            all(
                "full_quotient_mass" in record
                and "deficient_mass" in record
                for record in liveness["records"]
            )
            and all(
                record.get("scope")
                == "conditional_on_zero_vertex_balance"
                for record in calibration["records"]
            )
            and bool(calibration["nonmonotonicity_warning"])
        ),
        "G9_resource_envelope": (
            bool(limits["cpu_only"])
            and elapsed <= limits["maximum_wall_seconds"]
            and peak_bytes
            <= int(float(limits["maximum_ram_gib"]) * (1024**3))
        ),
    }
    if list(gates) != list(base_protocol["gate_ids"]):
        raise RuntimeError("runtime gate universe differs from base protocol")
    verdict = (
        amendment["success_verdict"]
        if all(gates.values())
        else "conditional_fiber_cycle_quotient_not_verified_v0_13_1"
    )
    result = {
        "protocol_id": amendment["protocol_id"],
        "base_protocol_id": base_protocol["protocol_id"],
        "scientific_specification_unchanged": True,
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "binding_checks": binding,
        "elapsed_seconds": elapsed,
        "resource_observation": {
            "gpu_used": False,
            "peak_resident_bytes": peak_bytes,
            "maximum_ram_bytes": int(
                float(limits["maximum_ram_gib"]) * (1024**3)
            ),
            "maximum_wall_seconds": limits["maximum_wall_seconds"],
        },
        "liveness": liveness,
        "power_calibration": calibration,
        "gates": gates,
        "verdict": verdict,
        "claim_boundary": base_protocol["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_13_1.json"
    report_path = args.output_dir / "RESULT_v0_13_1.md"
    write_json(result_path, result)
    write_text(report_path, render_report(result))
    receipt = {
        "protocol_id": amendment["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "implementation_commit": registration["implementation_commit"],
        "elapsed_seconds": elapsed,
        "output_hashes": {
            result_path.name: sha256(result_path),
            report_path.name: sha256(report_path),
        },
    }
    write_json(args.output_dir / "receipt_v0_13_1.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
