"""Verify the imported ASMP-9 v0.68.1 construction release."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import successor_design as design


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts_v0_68_1_construction"
MANIFEST = HERE / "release_manifest_v0_68_1_construction.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _records() -> list[dict]:
    path = ARTIFACTS / "records_v0_68_1.jsonl"
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def verify() -> dict:
    manifest = _load(MANIFEST)
    checked = []
    for item in manifest["files"]:
        path = HERE / item["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        actual_size = path.stat().st_size
        actual_hash = _sha256(path)
        if actual_size != item["bytes"]:
            raise ValueError(f"size mismatch: {item['path']}")
        if actual_hash != item["sha256"]:
            raise ValueError(f"hash mismatch: {item['path']}")
        checked.append(item["path"])

    prereveal = _load(
        ARTIFACTS / "PREREVEAL_VALIDATION_TARGET_v0_68_1.json"
    )
    if prereveal["status"] != "passed":
        raise ValueError("target prereveal did not pass")
    if prereveal["outcomes_read"]:
        raise ValueError("target prereveal read outcomes")
    if (
        prereveal["validation"]["model_weights_loaded"]
        or prereveal["validation"]["model_forward_passes"] != 0
    ):
        raise ValueError("target prereveal was not forward-free")

    registration_path = ARTIFACTS / "registration_v0_68_1.json"
    registration = _load(registration_path)
    if registration["status"] != "registered_prereveal":
        raise ValueError("registration was not prereveal")
    if registration["outcomes_read"]:
        raise ValueError("registration read outcomes")
    if registration["phase"] != "construction":
        raise ValueError("wrong registered phase")
    if registration["split_counts"]["records"] != 528:
        raise ValueError("wrong registered universe")

    completion = _load(ARTIFACTS / "completion_summary_v0_68_1.json")
    if completion["status"] != "completed":
        raise ValueError("run did not complete")
    if completion["records_completed"] != completion["records_expected"]:
        raise ValueError("completion universe is incomplete")
    if completion["registration_sha256"] != _sha256(registration_path):
        raise ValueError("completion does not bind registration")

    records = _records()
    record_ids = [record["record_id"] for record in records]
    if len(records) != 528 or len(set(record_ids)) != 528:
        raise ValueError("record universe is not 528 unique records")
    if {record["split"] for record in records} != {"construction"}:
        raise ValueError("non-construction record found")
    semantic_counts: dict[str, int] = {}
    for record in records:
        semantic_counts[record["semantic_id"]] = (
            semantic_counts.get(record["semantic_id"], 0) + 1
        )
    if set(semantic_counts.values()) != {2} or len(semantic_counts) != 264:
        raise ValueError("exact-repeat universe is malformed")

    scenario_manifest = _load(HERE / "scenario_manifest_v0_68.json")
    recomputed_analysis = design.analyze_records(
        records, scenario_manifest, "construction"
    )
    expected_analysis = (ARTIFACTS / "analysis_v0_68_1.json").read_bytes()
    if design.canonical_json_bytes(recomputed_analysis) != expected_analysis:
        raise ValueError("analysis does not reproduce from imported records")

    analysis = recomputed_analysis
    epsilon = analysis["thresholds"]["endpoint_epsilon"]
    if analysis["instrument"]["mechanical_repeat_status"] != "passed":
        raise ValueError("repeat gate failed")
    if analysis["instrument"]["quotient_admission_status"] != "passed":
        raise ValueError("quotient gate failed")
    if analysis["local_specificity"]["scenario_successes"] != 12:
        raise ValueError("local scenario result mismatch")
    if (
        analysis["local_specificity"]["status"]
        != "local_response_family_established_on_frozen_registry"
    ):
        raise ValueError("local gate did not establish")
    if analysis["median_specificity_minimum_directed"] <= epsilon:
        raise ValueError("median practical margin did not clear")
    if analysis["local_specificity"]["mean_scenario_mean_specificity"] <= epsilon:
        raise ValueError("mean practical margin did not clear")
    if analysis["global_specificity"]["status"] != "shared_effect_compatible":
        raise ValueError("global construction compatibility failed")

    decision = _load(ARTIFACTS / "decision_v0_68_1.json")
    if decision["decision"] != "local_and_global_confirmation_authorized":
        raise ValueError("unexpected construction decision")
    if not (
        decision["local_confirmation_authorized"]
        and decision["global_confirmation_authorized"]
    ):
        raise ValueError("confirmation lanes were not both authorized")
    if decision["registration_sha256"] != _sha256(registration_path):
        raise ValueError("decision does not bind registration")
    if decision["records_sha256"] != _sha256(
        ARTIFACTS / "records_v0_68_1.jsonl"
    ):
        raise ValueError("decision does not bind records")
    if decision["analysis_sha256"] != _sha256(
        ARTIFACTS / "analysis_v0_68_1.json"
    ):
        raise ValueError("decision does not bind analysis")

    first_wrapper = _load(
        ARTIFACTS / "attempt_1_wrapper_summary_v0_68_1.json"
    )
    first_cleanup = _load(
        ARTIFACTS / "attempt_1_cleanup_summary_v0_68_1.json"
    )
    second_wrapper = _load(
        ARTIFACTS / "attempt_2_wrapper_summary_v0_68_1.json"
    )
    second_cleanup = _load(
        ARTIFACTS / "attempt_2_cleanup_summary_v0_68_1.json"
    )
    if not (
        first_wrapper["status"] == "aborted"
        and first_wrapper["analysis_status"] == "not_run"
        and first_cleanup["cleanup_passed"]
    ):
        raise ValueError("first attempt receipt mismatch")
    if not (
        second_wrapper["status"] == "completed"
        and second_wrapper["runner_exit_code"] == 0
        and second_wrapper["analysis_exit_code"] == 0
        and second_cleanup["cleanup_passed"]
    ):
        raise ValueError("second attempt receipt mismatch")

    closeout = _load(HERE / "PRIME_POD_CLOSEOUT_ASMP9_V0681_20260729.json")
    if closeout["final_external_state"]["active_prime_pods"] != 0:
        raise ValueError("closeout reports active Prime pods")
    if not closeout["final_external_state"]["pod_terminated"]:
        raise ValueError("closeout does not report pod termination")
    if (
        closeout["final_external_state"]["protected_rl_run_status"]
        != "COMPLETED"
        or closeout["final_external_state"]["protected_rl_run_modified"]
    ):
        raise ValueError("protected RL status mismatch")

    return {
        "schema_version": "asmp9_context_quotient_release_verification_v0_68_1",
        "status": "passed",
        "manifest_files_checked": len(checked),
        "records": len(records),
        "semantic_inputs": len(semantic_counts),
        "scenarios": len(
            analysis["local_specificity"]["scenario_success_by_id"]
        ),
        "scenario_successes": analysis["local_specificity"][
            "scenario_successes"
        ],
        "median_specificity_minimum_directed": analysis[
            "median_specificity_minimum_directed"
        ],
        "mean_scenario_mean_specificity": analysis["local_specificity"][
            "mean_scenario_mean_specificity"
        ],
        "global_intersection": [
            analysis["global_specificity"]["intersection_lower"],
            analysis["global_specificity"]["intersection_upper"],
        ],
        "decision": decision["decision"],
        "claim_boundary": analysis["claim_boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify()
    payload = json.dumps(
        result, indent=2, sort_keys=True, ensure_ascii=False
    ) + "\n"
    if args.output:
        path = args.output.resolve()
        if path.exists() and path.read_text(encoding="utf-8") != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
