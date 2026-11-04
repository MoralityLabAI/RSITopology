from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

from conservative_numeraire import (
    apply_registered_mutation,
    build_value_table,
    calibration_constraint_matrix,
    deterministic_stationary_policies,
    expected_feature_occupancy,
    mechanics_hash,
    omitted_constraint_witness,
    pairwise_offset_bias_audit,
    q,
    rational_rank,
    rescaled_semantic_population_law,
    semantic_calibration,
    semantic_population_law,
    structural_conservativity,
    v028_eligibility,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def peak_resident_bytes() -> int:
    if os.name == "nt":
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
            wintypes.DWORD,
        )
        if not psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(counters.PeakWorkingSetSize)
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF)
    return int(usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024))


def validate_registration(path: Path):
    registration = json.loads(path.read_text())
    for relative, expected in registration["sealed_files"].items():
        if sha256(REPO / relative) != expected:
            raise RuntimeError(f"sealed hash mismatch: {relative}")
    subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            registration["implementation_commit"],
            "HEAD",
        ],
        cwd=REPO,
        check=True,
    )
    protocol = json.loads((REPO / registration["protocol_path"]).read_text())
    return registration, protocol, sha256(path)


def jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    return value


def build_semantic_cell(cell: dict, offsets: tuple[Fraction, ...]):
    return build_value_table(
        cell["base_values"],
        offsets,
        coefficient=cell["coefficient"],
        common_constant=cell["common_constant"],
        adjustments=cell["adjustments"],
        missing_cells=cell["missing_cells"],
    )


def dot(left, right):
    return sum((q(a) * q(b) for a, b in zip(left, right)), Fraction(0))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before execution")

    started = time.perf_counter()
    started_at = utc_now()
    registration, protocol, registration_hash = validate_registration(
        args.registration.resolve()
    )
    fresh = protocol["fresh_validation"]
    baseline = fresh["baseline_mdp"]
    offsets = tuple(q(value) for value in fresh["declared_offsets"])
    reference = int(fresh["reference_index"])
    gates: dict[str, dict[str, Any]] = {}
    gates["G0_registration_binding"] = {
        "pass": True,
        "registration_sha256": registration_hash,
        "sealed_file_count": len(registration["sealed_files"]),
    }

    interventions = tuple(
        {
            "level": f"level_{index}",
            "mdp": deepcopy(baseline),
        }
        for index in range(len(offsets))
    )
    structural = structural_conservativity(baseline, interventions)
    policies = deterministic_stationary_policies(baseline)
    baseline_occupancies = tuple(
        expected_feature_occupancy(baseline, policy)
        for policy in policies
    )
    occupancy_checks = 0
    occupancy_match = True
    for intervention in interventions:
        for policy, expected in zip(policies, baseline_occupancies):
            observed = expected_feature_occupancy(
                intervention["mdp"], policy
            )
            occupancy_checks += 1
            occupancy_match &= observed == expected
    structural_pass = (
        structural["structurally_conservative"]
        and occupancy_match
        and len({row["mechanics_hash"] for row in structural["intervention_rows"]})
        == 1
    )
    gates["G1_structural_product_extension"] = {
        "consequence_levels": len(interventions),
        "occupancy_checks": occupancy_checks,
        "pass": structural_pass,
        "policy_count": len(policies),
    }

    control_rows = []
    controls_pass = True
    mutated_mdps = {}
    for control in fresh["mechanical_controls"]:
        mutated = apply_registered_mutation(baseline, control["mutation"])
        mutated_mdps[control["name"]] = mutated
        result = structural_conservativity(
            baseline,
            ({"level": control["name"], "mdp": mutated},),
        )
        changed = tuple(
            result["intervention_rows"][0]["changed_fields"]
        )
        expected = tuple(sorted(control["expected_changed_fields"]))
        passed = (
            not result["structurally_conservative"]
            and tuple(sorted(changed)) == expected
        )
        controls_pass &= passed
        control_rows.append(
            {
                "changed_fields": changed,
                "name": control["name"],
                "pass": passed,
            }
        )
    gates["G2_mechanical_negative_controls"] = {
        "control_count": len(control_rows),
        "controls": control_rows,
        "pass": controls_pass,
    }

    semantic_tables = {
        name: build_semantic_cell(cell, offsets)
        for name, cell in fresh["semantic_cells"].items()
    }
    semantic_results = {
        name: semantic_calibration(offsets, table, reference)
        for name, table in semantic_tables.items()
    }
    calibrated = semantic_results["calibrated"]
    gates["G3_semantic_calibration"] = {
        "classification": calibrated["classification"],
        "constraint_count": len(semantic_tables["calibrated"])
        * (len(offsets) - 1),
        "maximum_residual": str(
            calibrated["maximum_calibration_residual"]
        ),
        "pass": (
            calibrated["classification"] == "calibrated_additive"
            and calibrated["maximum_calibration_residual"] == 0
        ),
    }

    unknown = semantic_results["unknown_scale"]
    interaction = semantic_results["interaction"]
    incomplete = semantic_results["incomplete"]
    semantic_controls_pass = (
        unknown["classification"] == "separable_unknown_scale"
        and unknown["proportional_coefficient"] == Fraction(9, 7)
        and interaction["classification"] == "context_interaction"
        and not incomplete["available"]
        and incomplete["classification"] == "incomplete_semantic_table"
    )
    gates["G4_semantic_negative_controls"] = {
        "incomplete_classification": incomplete["classification"],
        "interaction_classification": interaction["classification"],
        "pass": semantic_controls_pass,
        "unknown_scale_classification": unknown["classification"],
        "unknown_scale_coefficient": str(
            unknown["proportional_coefficient"]
        ),
    }

    constraint = fresh["constraint_cell"]
    constraint_matrix = calibration_constraint_matrix(
        int(constraint["base_object_count"]),
        int(constraint["consequence_count"]),
        int(constraint["reference_index"]),
    )
    constraint_rank = rational_rank(constraint_matrix)
    omission_checks = 0
    omission_pass = True
    row_index = 0
    for base_index in range(int(constraint["base_object_count"])):
        for level_index in range(int(constraint["consequence_count"])):
            if level_index == int(constraint["reference_index"]):
                continue
            witness = omitted_constraint_witness(
                int(constraint["base_object_count"]),
                int(constraint["consequence_count"]),
                base_index,
                level_index,
                int(constraint["reference_index"]),
            )
            flattened = tuple(value for row in witness for value in row)
            evaluations = tuple(
                dot(row, flattened) for row in constraint_matrix
            )
            omission_pass &= (
                evaluations[row_index] == 1
                and all(
                    value == 0
                    for index, value in enumerate(evaluations)
                    if index != row_index
                )
            )
            omission_checks += 1
            row_index += 1
    expected_rank = int(constraint["base_object_count"]) * (
        int(constraint["consequence_count"]) - 1
    )
    gates["G5_constraint_rank_and_omission"] = {
        "constraint_rank": constraint_rank,
        "expected_rank": expected_rank,
        "omission_checks": omission_checks,
        "pass": (
            constraint_rank == expected_rank
            and omission_checks == expected_rank
            and omission_pass
        ),
    }

    population = fresh["population_cell"]
    population_baseline = semantic_population_law(
        population["base_values"],
        offsets,
        population["coefficient"],
        population["radius"],
    )
    scale_matches = tuple(
        population_baseline
        == rescaled_semantic_population_law(
            population["base_values"],
            offsets,
            population["coefficient"],
            alpha,
            population["radius"],
        )
        for alpha in population["scale_factors"]
    )
    shared_mechanics_hashes = {
        name: mechanics_hash(baseline) for name in semantic_tables
    }
    no_go_pass = (
        len(set(shared_mechanics_hashes.values())) == 1
        and len(
            {
                semantic_results[name]["classification"]
                for name in ("calibrated", "unknown_scale", "interaction")
            }
        )
        == 3
        and all(scale_matches)
    )
    gates["G6_mechanics_only_and_scale_no_go"] = {
        "distinct_semantic_classes": 3,
        "mechanics_hash_count": len(set(shared_mechanics_hashes.values())),
        "pass": no_go_pass,
        "scale_match_count": sum(scale_matches),
    }

    approximate = fresh["approximate_cell"]
    approximate_table = []
    for base_value, residual_row in zip(
        approximate["base_values"], approximate["residuals"]
    ):
        approximate_table.append(
            tuple(
                q(base_value)
                + q(approximate["common_constant"])
                + offset
                + q(residual)
                for offset, residual in zip(offsets, residual_row)
            )
        )
    approximate_audit = pairwise_offset_bias_audit(
        offsets,
        approximate_table,
        reference,
    )
    epsilon = q(approximate["epsilon"])
    approximate_pass = (
        approximate_audit["single_cell_residual_bound"] == epsilon
        and approximate_audit["maximum_pairwise_bias"] == 2 * epsilon
        and approximate_audit["bound"] == 2 * epsilon
        and approximate_audit["bound_valid"]
    )
    gates["G7_approximate_calibration"] = {
        "epsilon": str(epsilon),
        "maximum_pairwise_bias": str(
            approximate_audit["maximum_pairwise_bias"]
        ),
        "pass": approximate_pass,
        "registered_bound": str(2 * epsilon),
    }

    eligible = v028_eligibility(
        baseline,
        interventions,
        offsets,
        semantic_tables["calibrated"],
        reference,
    )
    unknown_eligibility = v028_eligibility(
        baseline,
        interventions,
        offsets,
        semantic_tables["unknown_scale"],
        reference,
    )
    incomplete_eligibility = v028_eligibility(
        baseline,
        interventions,
        offsets,
        semantic_tables["incomplete"],
        reference,
    )
    structural_ineligibilities = []
    for name, mutated in mutated_mdps.items():
        result = v028_eligibility(
            baseline,
            ({"level": name, "mdp": mutated},),
            offsets,
            semantic_tables["calibrated"],
            reference,
        )
        structural_ineligibilities.append(
            not result["eligible"]
            and "mechanics_not_conservative" in result["reasons"]
        )
    eligibility_pass = (
        eligible["eligible"]
        and not unknown_eligibility["eligible"]
        and unknown_eligibility["reasons"]
        == ("semantic_calibration_not_established",)
        and not incomplete_eligibility["eligible"]
        and incomplete_eligibility["reasons"]
        == ("semantic_table_incomplete",)
        and all(structural_ineligibilities)
    )
    gates["G8_v028_eligibility"] = {
        "eligible_positive": eligible["eligible"],
        "incomplete_reasons": incomplete_eligibility["reasons"],
        "pass": eligibility_pass,
        "structural_rejections": sum(structural_ineligibilities),
        "unknown_scale_reasons": unknown_eligibility["reasons"],
    }

    identifiers = sorted(row["identifier"] for row in protocol["prior_art"])
    required = sorted(
        [
            "DOI:10.1016/0022-2496(64)90015-X",
            "Krantz-Luce-Suppes-Tversky-1971",
            "ICML-1999-Ng-Harada-Russell",
            "PMLR:80:1262-1270",
            "PMLR:202:32033-32058",
            "PMLR:235:24808-24828",
            "ASMP-9-v0.28",
            "ASMP-9-v0.29",
        ]
    )
    claim_pass = (
        identifiers == required
        and len(protocol["structured_claims"]["allowed"]) == 7
        and len(protocol["structured_claims"]["forbidden"]) == 8
        and "ASMP-9 is resolved."
        in protocol["structured_claims"]["forbidden"]
        and "no novelty is claimed" in protocol["claim_boundary"]
    )
    gates["G9_prior_art_and_claim_boundary"] = {
        "identifiers": identifiers,
        "pass": claim_pass,
    }

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    gates["G10_resource_and_scope"] = {
        "gpu_used": False,
        "pass": (
            not caps["gpu_allowed"]
            and elapsed <= caps["wall_seconds"]
            and peak <= caps["peak_resident_bytes"]
        ),
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    gate_passes = {name: bool(row["pass"]) for name, row in gates.items()}
    if not gate_passes["G0_registration_binding"] or not gate_passes[
        "G10_resource_and_scope"
    ]:
        verdict_key = "binding_or_resource_gate_fails"
    elif all(gate_passes.values()):
        verdict_key = "all_gates_pass"
    else:
        verdict_key = "any_substantive_gate_fails"
    result = {
        "approximate_audit": jsonable(approximate_audit),
        "gate_passes": gate_passes,
        "gates": jsonable(gates),
        "policy_occupancies": jsonable(baseline_occupancies),
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_hash,
        "semantic_results": jsonable(semantic_results),
        "structural_result": jsonable(structural),
        "verdict": protocol["verdict_map"][verdict_key],
    }
    args.output_dir.mkdir(parents=True)
    result_path = args.output_dir / "result_v0_30.json"
    receipt_path = args.output_dir / "run_receipt_v0_30.json"
    write_json_exclusive(result_path, result)
    receipt = {
        "finished_at_utc": utc_now(),
        "implementation_commit": registration["implementation_commit"],
        "peak_resident_bytes": peak,
        "protocol_sha256": sha256(REPO / registration["protocol_path"]),
        "registration_sha256": registration_hash,
        "result_sha256": sha256(result_path),
        "run_commit": git("rev-parse", "HEAD"),
        "started_at_utc": started_at,
        "wall_seconds": elapsed,
    }
    write_json_exclusive(receipt_path, receipt)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
