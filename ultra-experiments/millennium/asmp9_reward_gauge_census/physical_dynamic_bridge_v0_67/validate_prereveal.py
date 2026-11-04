"""Validate the frozen v0.67 prompt/token contract without loading model weights."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SPEC = importlib.util.spec_from_file_location("bridge_core_v067", HERE / "bridge_core.py")
assert SPEC and SPEC.loader
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


DEFAULT_MODEL = Path(r"D:\Research_Engine\models\Qwen3.5\Qwen3.5-0.8B-Instruct")


def _artifact(path: Path) -> dict:
    resolved = path.resolve()
    return {"path": str(resolved), "sha256": core.sha256_file(resolved)}


def validate(model_path: Path, protocol_path: Path) -> dict:
    from transformers import AutoTokenizer

    manifest_path = HERE / "scenario_manifest_v0_67.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol["status"] != "registered_prereveal":
        raise ValueError("protocol is not frozen")
    manifest = core.load_manifest(manifest_path)
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, local_files_only=True, trust_remote_code=True
    )
    actual_contract = {
        "A": tokenizer.encode("A", add_special_tokens=False),
        "B": tokenizer.encode("B", add_special_tokens=False),
        "vocabulary_size": len(tokenizer),
        "eos_token_id": tokenizer.eos_token_id,
        "pad_token_id": tokenizer.pad_token_id,
    }
    if actual_contract != protocol["model_contract"]["tokenizer_contract"]:
        raise ValueError("tokenizer contract mismatch")

    counts: dict[str, int] = {}
    prompt_lengths: list[int] = []
    message_hashes: set[str] = set()
    boundary_checks = 0
    for split in ("construction", "confirmation"):
        jobs = core.score_jobs(manifest, split)
        counts[split] = len(jobs)
        for job in jobs:
            if (
                __import__("hashlib").sha256(
                    core.canonical_json_bytes(job["messages"])
                ).hexdigest()
                != job["messages_sha256"]
            ):
                raise ValueError(f"message hash mismatch: {job['record_id']}")
            text = tokenizer.apply_chat_template(
                job["messages"],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
            token_ids = tokenizer.encode(text, add_special_tokens=False)
            prompt_lengths.append(len(token_ids))
            if len(token_ids) > protocol["resource_contract"]["max_prompt_tokens"]:
                raise ValueError(f"prompt token cap exceeded: {job['record_id']}")
            for answer, expected in (("A", 32), ("B", 33)):
                combined = tokenizer.encode(text + answer, add_special_tokens=False)
                if (
                    combined[: len(token_ids)] != token_ids
                    or combined[len(token_ids) :] != [expected]
                ):
                    raise ValueError(
                        f"answer token boundary mismatch: {job['record_id']} {answer}"
                    )
                boundary_checks += 1
            message_hashes.add(job["messages_sha256"])

    model_files = [
        model_path / "model.safetensors-00001-of-00001.safetensors",
        model_path / "model.safetensors",
        model_path / "config.json",
        model_path / "tokenizer.json",
        model_path / "tokenizer_config.json",
        model_path / "chat_template.jinja",
    ]
    source_files = [
        HERE / "bridge_core.py",
        HERE / "run_qwen_bridge.py",
        HERE / "analyze_bridge.py",
        HERE / "prepare_registration.py",
        HERE / "validate_prereveal.py",
        HERE / "test_bridge_core.py",
        ROOT / "scripts" / "run_qwen_holonomy_jobobject.ps1",
    ]
    forbidden_outputs = [
        HERE / "records.jsonl",
        HERE / "analysis.json",
        HERE / "calibration.json",
        HERE / "registration.json",
        HERE / "completion_summary.json",
    ]
    if any(path.exists() for path in forbidden_outputs):
        raise ValueError("outcome or environment-registration file exists in source freeze")
    return {
        "schema_version": "asmp9_physical_dynamic_bridge_prereveal_validation_v0_67",
        "status": "passed",
        "outcomes_read": False,
        "intended_external_anchor": "the git commit containing this receipt",
        "protocol": _artifact(protocol_path),
        "scenario_manifest": _artifact(manifest_path),
        "source_files": [_artifact(path) for path in source_files],
        "model_files": [_artifact(path) for path in model_files],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "transformers": importlib.metadata.version("transformers"),
        },
        "tokenizer_contract": actual_contract,
        "validation": {
            "scenario_rows": len(manifest["rows"]),
            "behavior_families": len({row["family"] for row in manifest["rows"]}),
            "records_by_split": counts,
            "total_record_contracts": sum(counts.values()),
            "unique_message_hashes": len(message_hashes),
            "answer_boundary_checks": boundary_checks,
            "minimum_prompt_tokens": min(prompt_lengths),
            "maximum_prompt_tokens": max(prompt_lengths),
            "registered_prompt_cap": protocol["resource_contract"][
                "max_prompt_tokens"
            ],
            "model_weights_loaded": False,
            "model_forward_passes": 0,
        },
        "claim_boundary": (
            "This receipt validates source, scenario, tokenizer, rendering, and "
            "answer-boundary contracts only. It contains no model outcome."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument(
        "--protocol", type=Path, default=HERE / "protocol_v0_67.json"
    )
    parser.add_argument(
        "--output", type=Path, default=HERE / "PREREVEAL_VALIDATION_v0_67.json"
    )
    args = parser.parse_args()
    value = validate(args.model.resolve(), args.protocol.resolve())
    payload = core.canonical_json_bytes(value)
    if args.output.exists() and args.output.read_bytes() != payload:
        raise FileExistsError(f"write-once validation differs: {args.output}")
    args.output.write_bytes(payload)
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
