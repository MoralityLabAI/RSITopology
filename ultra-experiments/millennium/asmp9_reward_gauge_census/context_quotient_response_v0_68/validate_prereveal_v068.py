"""Validate v0.68.1 sources, tokenizer, rendering, and jobs without weights."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "asmp9_successor_design_v068", HERE / "successor_design.py"
)
assert SPEC and SPEC.loader
design = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(design)
QUOTIENT_SPEC = importlib.util.spec_from_file_location(
    "asmp9_response_quotient_v068", HERE / "response_quotient.py"
)
assert QUOTIENT_SPEC and QUOTIENT_SPEC.loader
quotient = importlib.util.module_from_spec(QUOTIENT_SPEC)
QUOTIENT_SPEC.loader.exec_module(quotient)

DEFAULT_MODEL = Path(
    r"D:\Research_Engine\models\Qwen3.5\Qwen3.5-0.8B-Instruct"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path) -> dict:
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    return {"path": str(resolved), "sha256": sha256(resolved)}


def validate(model_path: Path) -> dict:
    from transformers import AutoTokenizer

    protocol_path = HERE / "protocol_v0_68.json"
    amendment_path = HERE / "protocol_amendment_v0_68_1.json"
    manifest_path = HERE / "scenario_manifest_v0_68.json"
    validation_path = HERE / "SCIENTIFIC_DESIGN_VALIDATION_v0_68_1.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
    design_validation = json.loads(
        validation_path.read_text(encoding="utf-8")
    )
    if (
        protocol["status"]
        != "scientific_protocol_frozen_execution_unregistered"
        or amendment["status"]
        != "frozen_prereveal_amendment_execution_unregistered"
        or design_validation["execution_authorized"] is not False
    ):
        raise ValueError("scientific design is not in the prereveal state")
    if amendment["base_protocol"]["sha256"] != sha256(protocol_path):
        raise ValueError("amendment/base protocol binding mismatch")
    if design_validation["protocol_amendment_sha256"] != sha256(
        amendment_path
    ):
        raise ValueError("design validation/amendment binding mismatch")
    manifest = design.load_manifest(manifest_path)
    if protocol["fresh_universe"]["scenario_manifest_sha256"] != sha256(
        manifest_path
    ):
        raise ValueError("protocol/manifest binding mismatch")
    common_fixture = ((0, 2), (10, 12))
    shifted_fixture = quotient.gauge_shift(common_fixture, (7, -4))
    interaction_fixture = ((0, 2), (10, 15))
    if (
        quotient.within_reference_quotient(common_fixture)
        != quotient.within_reference_quotient(shifted_fixture)
        or quotient.within_reference_quotient(common_fixture)
        == quotient.within_reference_quotient(interaction_fixture)
    ):
        raise ValueError("synthetic quotient controls failed")

    tokenizer = AutoTokenizer.from_pretrained(
        model_path, local_files_only=True, trust_remote_code=True
    )
    tokenizer_contract = {
        "A": tokenizer.encode("A", add_special_tokens=False),
        "B": tokenizer.encode("B", add_special_tokens=False),
        "vocabulary_size": len(tokenizer),
        "eos_token_id": tokenizer.eos_token_id,
        "pad_token_id": tokenizer.pad_token_id,
    }
    if tokenizer_contract["A"] != [32] or tokenizer_contract["B"] != [33]:
        raise ValueError("A/B answer-token contract changed")

    split_receipts = {}
    all_message_hashes = set()
    prompt_lengths = []
    boundary_checks = 0
    for split in ("construction", "confirmation"):
        jobs = design.score_jobs(manifest, split)
        job_hash = hashlib.sha256(
            design.canonical_json_bytes(jobs)
        ).hexdigest()
        expected_hash = design_validation["splits"][split][
            "job_list_sha256"
        ]
        if job_hash != expected_hash:
            raise ValueError(f"{split} job-list hash mismatch")
        repeat_messages = {}
        for job in jobs:
            if hashlib.sha256(
                design.v067.canonical_json_bytes(job["messages"])
            ).hexdigest() != job["messages_sha256"]:
                raise ValueError(f"message hash mismatch: {job['record_id']}")
            repeat_messages.setdefault(job["semantic_id"], set()).add(
                job["messages_sha256"]
            )
            text = tokenizer.apply_chat_template(
                job["messages"],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
            token_ids = tokenizer.encode(text, add_special_tokens=False)
            prompt_lengths.append(len(token_ids))
            if len(token_ids) > 768:
                raise ValueError(f"prompt cap exceeded: {job['record_id']}")
            for answer, expected in (("A", 32), ("B", 33)):
                combined = tokenizer.encode(
                    text + answer, add_special_tokens=False
                )
                if (
                    combined[: len(token_ids)] != token_ids
                    or combined[len(token_ids) :] != [expected]
                ):
                    raise ValueError(
                        f"answer boundary mismatch: "
                        f"{job['record_id']} {answer}"
                    )
                boundary_checks += 1
            all_message_hashes.add(job["messages_sha256"])
        if any(len(values) != 1 for values in repeat_messages.values()):
            raise ValueError("exact repeats render different messages")
        split_receipts[split] = {
            "records": len(jobs),
            "semantic_inputs": len(repeat_messages),
            "job_list_sha256": job_hash,
        }

    source_files = [
        HERE / "response_quotient.py",
        HERE / "successor_design.py",
        HERE / "run_qwen_v068.py",
        HERE / "analyze_v068.py",
        HERE / "prepare_execution_registration.py",
        HERE / "validate_prereveal_v068.py",
        HERE / "protocol_v0_68.json",
        HERE / "protocol_amendment_v0_68_1.json",
        HERE / "SCIENTIFIC_PROTOCOL_AMENDMENT_v0_68_1.md",
        HERE / "scenario_manifest_v0_68.json",
        HERE / "SCIENTIFIC_DESIGN_VALIDATION_v0_68_1.json",
        HERE / "validate_scientific_design.py",
        HERE / "test_response_quotient.py",
        HERE / "test_successor_design.py",
        HERE / "test_execution_contract.py",
        HERE / "test_scientific_protocol.py",
        HERE / "prime" / "run_prime_guarded_v0_68.sh",
        HERE / "prime" / "post_run_prime_v0_68.sh",
        HERE.parent / "physical_dynamic_bridge_v0_67" / "bridge_core.py",
    ]
    model_files = [
        model_path / "model.safetensors-00001-of-00001.safetensors",
        model_path / "model.safetensors",
        model_path / "config.json",
        model_path / "tokenizer.json",
        model_path / "tokenizer_config.json",
        model_path / "chat_template.jinja",
    ]
    forbidden = [
        HERE / "registration.json",
        HERE / "records.jsonl",
        HERE / "analysis.json",
        HERE / "decision.json",
        HERE / "completion_summary.json",
    ]
    if any(path.exists() for path in forbidden):
        raise ValueError("an outcome/registration file exists in source tree")
    return {
        "schema_version": "asmp9_context_quotient_prereveal_validation_v0_68_1",
        "status": "passed",
        "outcomes_read": False,
        "protocol": _artifact(protocol_path),
        "protocol_amendment": _artifact(amendment_path),
        "scenario_manifest": _artifact(manifest_path),
        "scientific_design_validation": _artifact(validation_path),
        "source_files": [_artifact(path) for path in source_files],
        "model_files": [_artifact(path) for path in model_files],
        "environment": {
            "python": platform.python_version(),
            "packages": {
                name: importlib.metadata.version(name)
                for name in (
                    "torch",
                    "transformers",
                    "accelerate",
                    "safetensors",
                )
            },
        },
        "tokenizer_contract": tokenizer_contract,
        "validation": {
            "scenario_rows": len(manifest["rows"]),
            "families": len({row["family"] for row in manifest["rows"]}),
            "splits": split_receipts,
            "unique_message_hashes": len(all_message_hashes),
            "answer_boundary_checks": boundary_checks,
            "minimum_prompt_tokens": min(prompt_lengths),
            "maximum_prompt_tokens": max(prompt_lengths),
            "registered_prompt_cap": 768,
            "model_weights_loaded": False,
            "model_forward_passes": 0,
            "synthetic_common_mode_removed": True,
            "synthetic_arm_by_order_interaction_retained": True,
        },
        "claim_boundary": (
            "This validates source, model/tokenizer bytes, rendering, exact "
            "repeats, and answer-token boundaries without loading weights or "
            "reading an outcome."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = validate(args.model.resolve())
    payload = design.canonical_json_bytes(value)
    if args.output.exists() and args.output.read_bytes() != payload:
        raise FileExistsError(f"write-once validation differs: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
