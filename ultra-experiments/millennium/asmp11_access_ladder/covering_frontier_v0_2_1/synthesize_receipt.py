#!/usr/bin/env python3
"""Build the authoritative ASMP-11 v0.2.1.2 conclusion receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from release_contract import (
    ARTIFACT_DIRECTORY,
    CLAIM_BOUNDARY,
    PRIMARY_OUTPUTS,
    PRIMARY_GATE_IDS,
    RECEIPT_KEYS,
    RECEIPT_SCHEMA,
    REGISTRATION_FILENAME,
    REGISTRATION_KEYS,
    REGISTRATION_SCHEMA,
    RELEASE_ID,
    SYNTHESIS_FILENAME,
    SYNTHESIS_SCHEMA,
    VERIFICATION_FILENAME,
    VERIFICATION_GATE_IDS,
    VERIFICATION_KEYS,
    VERIFICATION_SCHEMA,
)
from verify_result import verify_bundle


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def write_lf_text(path: Path, payload: str) -> None:
    path.write_text(payload, encoding="utf-8", newline="\n")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(token: str) -> None:
    raise ValueError(f"non-finite JSON number: {token}")


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object,
        parse_constant=_reject_nonfinite,
    )


def _build_synthesis_impl(
    registration_path: Path,
    artifacts: Path,
    verification_path: Path,
) -> dict[str, Any]:
    registration = load_json(registration_path)
    receipt_path = artifacts / "receipt.json"
    receipt = load_json(receipt_path)
    verification = load_json(verification_path)
    result = load_json(artifacts / "result_layer.json")
    reliability = load_json(artifacts / "reliability_layer.json")
    claim = load_json(artifacts / "claim_layer.json")
    operation = load_json(artifacts / "operation_layer.json")
    replayed_verification = verify_bundle(
        registration_path,
        artifacts,
        ROOT / "experiment_v0_2_1.json",
        ROOT / "prior_anchor_v0_2.json",
        enforce_preverification_stage=False,
    )

    expected_stage = PRIMARY_OUTPUTS | {"receipt.json", VERIFICATION_FILENAME}
    observed_stage = {path.name for path in artifacts.iterdir() if path.is_file()}
    stage_exact = (
        artifacts.is_dir()
        and not artifacts.is_symlink()
        and verification_path.resolve() == (artifacts / VERIFICATION_FILENAME).resolve()
        and observed_stage == expected_stage
        and all(
            path.is_file() and not path.is_symlink() for path in artifacts.iterdir()
        )
    )
    expected_output_map = {
        name: sha256(artifacts / name) for name in sorted(PRIMARY_OUTPUTS)
    }
    expected_resource_assessment = {
        "measured_resource_checks": "passed",
        "wall_observations": "self_reported_internally_consistent",
        "ram_compliance": "not_established_unmeasured",
    }
    expected_counts = registration["claim_grid"]["expected_counts"]
    expected_verification_counts = {
        "covering_cells": int(expected_counts["covering_cells"]),
        "cost_cells": int(expected_counts["cost_cells"]),
        "brackets": int(expected_counts["brackets"]),
    }
    binding_match = (
        set(registration) == REGISTRATION_KEYS
        and registration.get("schema_version") == REGISTRATION_SCHEMA
        and registration.get("release_id") == RELEASE_ID
        and set(receipt) == RECEIPT_KEYS
        and receipt.get("schema_version") == RECEIPT_SCHEMA
        and receipt.get("release_id") == RELEASE_ID
        and set(verification) == VERIFICATION_KEYS
        and verification.get("schema_version") == VERIFICATION_SCHEMA
        and verification == replayed_verification
        and verification.get("release_id") == RELEASE_ID
        and verification.get("verified") is True
        and set(verification.get("gates", {})) == VERIFICATION_GATE_IDS
        and all(value is True for value in verification["gates"].values())
        and verification.get("counts") == expected_verification_counts
        and verification.get("registration_sha256") == sha256(registration_path)
        and verification.get("receipt_sha256") == sha256(receipt_path)
        and verification.get("primary_outputs")
        == dict(sorted(receipt["outputs"].items()))
        and verification.get("primary_outputs") == expected_output_map
        and verification.get("resource_assessment") == expected_resource_assessment
        and verification.get("claim_boundary") == CLAIM_BOUNDARY
        and receipt.get("registration_sha256") == sha256(registration_path)
        and receipt.get("manifest_sha256") == registration.get("manifest_sha256")
        and receipt.get("prior_anchor_sha256")
        == registration.get("prior_anchor_sha256")
        and set(receipt.get("outputs", {})) == PRIMARY_OUTPUTS
        and receipt.get("outputs") == expected_output_map
        and receipt.get("verdict") == claim.get("verdict")
        and operation.get("registration", {}).get("sha256") == sha256(registration_path)
        and registration.get("claim_boundary") == CLAIM_BOUNDARY
    )
    metric_totals = verification.get("metric_robustness", {}).get("totals", {})
    expected_cost_cells = int(
        registration["claim_grid"]["expected_counts"]["cost_cells"]
    )
    expected_robustness_records = expected_cost_cells * int(
        registration["claim_grid"]["expected_counts"]["robustness_probes_per_cost_cell"]
    )
    metric_complete = (
        metric_totals.get("robustness_records") == expected_robustness_records
        and metric_totals.get("robustness_agreements", 0)
        + metric_totals.get("robustness_disagreements", 0)
        == expected_robustness_records
        and metric_totals.get("identity_diagnostic_records") == expected_cost_cells
        and metric_totals.get("identity_diagnostic_agreements") == expected_cost_cells
    )
    metric_unanimous = (
        metric_complete and metric_totals.get("robustness_disagreements") == 0
    )
    task_pass = (
        result.get("exact_grid_counters")
        == {"covering": True, "cost": True, "bracket": True}
        and result.get("counts", {}).get("covering_cells")
        == int(expected_counts["covering_cells"])
        and result.get("counts", {}).get("cost_cells")
        == int(expected_counts["cost_cells"])
        and result.get("counts", {}).get("brackets") == int(expected_counts["brackets"])
        and len(result.get("brackets", [])) == int(expected_counts["brackets"])
    )
    primary_layers_consistent = (
        set(reliability.get("binding_gates", {})) == PRIMARY_GATE_IDS
        and all(value is True for value in reliability["binding_gates"].values())
        and claim.get("verdict") == "claim_ready_for_independent_verification"
        and operation.get("run_status") == "complete"
        and operation.get("resource_compliance", {}).get("ram", {}).get("compliance")
        == "not_established"
    )
    artifact_replay_pass = bool(
        stage_exact and binding_match and metric_complete and primary_layers_consistent
    )
    passed = bool(artifact_replay_pass and task_pass)
    return {
        "schema_version": SYNTHESIS_SCHEMA,
        "release_id": RELEASE_ID,
        "pass": passed,
        "bindings": {
            "registration_sha256": sha256(registration_path),
            "primary_receipt_sha256": sha256(receipt_path),
            "independent_verification_sha256": sha256(verification_path),
            "primary_outputs": dict(sorted(receipt["outputs"].items())),
        },
        "binding_match": binding_match,
        "stage_exact": stage_exact,
        "conclusion_layers": {
            "metric_robustness": (
                "four_nonidentity_alternative_metric_probes_agree"
                if artifact_replay_pass and metric_unanimous
                else (
                    "alternative_metric_sensitivity_detected"
                    if artifact_replay_pass and metric_complete
                    else "not_established"
                )
            ),
            "task_result": (
                "finite_intermediate_width_crossover_surface_established"
                if passed and task_pass
                else "not_established"
            ),
            "measurement_reliability": (
                "independent_replay_passed_wall_self_report_consistent_ram_unmeasured"
                if artifact_replay_pass
                else "failed"
            ),
            "claim_support": (
                "model_only_finite_registered_grid" if passed else "none"
            ),
            "operational_decision": (
                "accept_finite_result_with_ram_compliance_unestablished"
                if passed
                else "repair_or_rerun"
            ),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_synthesis(
    registration_path: Path,
    artifacts: Path,
    verification_path: Path,
) -> dict[str, Any]:
    """Build a fail-closed synthesis receipt from the exact three-stage bundle."""

    try:
        return _build_synthesis_impl(registration_path, artifacts, verification_path)
    except (ArithmeticError, AttributeError, KeyError, OSError, TypeError, ValueError):
        receipt_path = artifacts / "receipt.json"
        return {
            "schema_version": SYNTHESIS_SCHEMA,
            "release_id": RELEASE_ID,
            "pass": False,
            "bindings": {
                "registration_sha256": (
                    sha256(registration_path) if registration_path.is_file() else None
                ),
                "primary_receipt_sha256": (
                    sha256(receipt_path) if receipt_path.is_file() else None
                ),
                "independent_verification_sha256": (
                    sha256(verification_path) if verification_path.is_file() else None
                ),
                "primary_outputs": {},
            },
            "binding_match": False,
            "stage_exact": False,
            "conclusion_layers": {
                "metric_robustness": "not_established",
                "task_result": "not_established",
                "measurement_reliability": "failed",
                "claim_support": "none",
                "operational_decision": "repair_or_rerun",
            },
            "claim_boundary": CLAIM_BOUNDARY,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--verification", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    artifacts = args.artifacts.resolve()
    verification = (
        args.verification.resolve()
        if args.verification
        else artifacts / VERIFICATION_FILENAME
    )
    output = args.output.resolve() if args.output else artifacts / SYNTHESIS_FILENAME
    if args.registration.resolve() != (ROOT / REGISTRATION_FILENAME).resolve():
        raise ValueError("synthesis requires the exact v0.2.1.2 registration path")
    if artifacts != (ROOT / ARTIFACT_DIRECTORY).resolve():
        raise ValueError("synthesis requires the exact v0.2.1.2 artifact directory")
    if verification != artifacts / VERIFICATION_FILENAME:
        raise ValueError("synthesis requires the in-bundle verification receipt")
    if output != artifacts / SYNTHESIS_FILENAME:
        raise ValueError("synthesis output must use its exact in-bundle path")
    if output.exists():
        raise FileExistsError(f"synthesis receipt is write-once: {output}")
    synthesis = build_synthesis(args.registration.resolve(), artifacts, verification)
    temporary = output.with_suffix(output.suffix + ".tmp")
    write_lf_text(temporary, canonical_json(synthesis))
    os.replace(temporary, output)
    print(canonical_json(synthesis), end="")
    return 0 if synthesis["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
