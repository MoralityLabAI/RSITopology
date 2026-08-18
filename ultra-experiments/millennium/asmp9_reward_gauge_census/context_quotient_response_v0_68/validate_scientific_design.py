"""Outcome-free validation receipt for the v0.68.1 amended design."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "asmp9_successor_design_v068", HERE / "successor_design.py"
)
assert SPEC and SPEC.loader
design = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(design)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def job_payload(jobs: list[dict]) -> bytes:
    serializable = [
        {key: value for key, value in job.items() if key != "messages"}
        | {"messages": job["messages"]}
        for job in jobs
    ]
    return design.canonical_json_bytes(serializable)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol_path = HERE / "protocol_v0_68.json"
    amendment_path = HERE / "protocol_amendment_v0_68_1.json"
    manifest_path = HERE / "scenario_manifest_v0_68.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
    manifest = design.load_manifest(manifest_path)
    if amendment["base_protocol"]["sha256"] != sha256(protocol_path):
        raise ValueError("amendment does not bind the immutable base protocol")
    if protocol["fresh_universe"]["scenario_manifest_sha256"] != sha256(
        manifest_path
    ):
        raise ValueError("protocol does not bind the scenario manifest")
    if not all(design.validate_endpoint_coefficients().values()):
        raise ValueError("an endpoint fails nuisance admission")

    splits = {}
    for split in ("construction", "confirmation"):
        jobs = design.score_jobs(manifest, split)
        ids = {job["record_id"] for job in jobs}
        semantic_ids = {job["semantic_id"] for job in jobs}
        if len(ids) != 528 or len(semantic_ids) != 264:
            raise ValueError("unexpected score universe")
        splits[split] = {
            "record_count": len(ids),
            "semantic_input_count": len(semantic_ids),
            "job_list_sha256": hashlib.sha256(job_payload(jobs)).hexdigest(),
        }

    result = {
        "schema_version": "asmp9_context_quotient_design_validation_v0_68_1",
        "status": "passed_scientific_design_only",
        "protocol_sha256": sha256(protocol_path),
        "protocol_amendment_sha256": sha256(amendment_path),
        "scenario_manifest_sha256": sha256(manifest_path),
        "scenario_generator_sha256": sha256(
            HERE / "prepare_fresh_scenarios.py"
        ),
        "validator_source_sha256": sha256(HERE / "validate_scientific_design.py"),
        "successor_design_sha256": sha256(HERE / "successor_design.py"),
        "quotient_source_sha256": sha256(HERE / "response_quotient.py"),
        "v067_prompt_dependency_sha256": sha256(
            HERE.parent / "physical_dynamic_bridge_v0_67" / "bridge_core.py"
        ),
        "endpoint_admission": design.validate_endpoint_coefficients(),
        "splits": splits,
        "execution_authorized": False,
        "claim_boundary": (
            "This receipt validates the outcome-free scientific design and "
            "score universe. It does not register an execution environment or "
            "authorize model inference."
        ),
    }
    payload = design.canonical_json_bytes(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and args.output.read_bytes() != payload:
        raise FileExistsError("existing validation receipt differs")
    args.output.write_bytes(payload)
    print(payload.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
