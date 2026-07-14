from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocols" / "one_prompt_real_model_benchmark_v0_1.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def is_sha256(value: object) -> bool:
    text = str(value).lower()
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def validate(payload: dict) -> None:
    required = set(json.loads((ROOT / "protocols" / "one_prompt_run_registration_template.json").read_text()))
    missing = required - set(payload)
    if missing:
        raise ValueError(f"registration is missing fields: {sorted(missing)}")
    for field in (
        "model_weight_sha256",
        "tokenizer_sha256",
        "prompt_corpus_sha256",
        "jspace_protocol_sha256",
        "environment_lock_sha256",
    ):
        if not is_sha256(payload[field]):
            raise ValueError(f"{field} must be a SHA-256")
    commit = str(payload["implementation_commit"]).lower()
    if len(commit) < 7 or any(character not in "0123456789abcdef" for character in commit):
        raise ValueError("implementation_commit must be a git commit")
    if payload.get("outcomes_prohibited") is not True or payload.get("weight_mutation_prohibited") is not True:
        raise ValueError("one-prompt benchmark must prohibit outcomes and weight mutation")
    if len(payload.get("exact_command", [])) < 2:
        raise ValueError("exact_command must be a nonempty argv array")
    if not payload.get("candidate_sites") or not payload.get("module_graph_mapping"):
        raise ValueError("candidate sites and module graph mapping are required")
    if int(payload.get("candidate_count", 0)) <= 0:
        raise ValueError("candidate_count must be positive")
    caps = payload.get("resource_caps", {})
    if any(int(caps.get(field, 0)) <= 0 for field in ("memory_mb", "cpu_percent", "io_mb_s", "timeout_seconds")):
        raise ValueError("all resource caps and timeout must be explicit and positive")
    if int(caps.get("swap_bytes", -1)) != 0:
        raise ValueError("benchmark requires swap_bytes=0")


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze a one-prompt outcome-free benchmark registration.")
    parser.add_argument("registration", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.registration.read_text(encoding="utf-8"))
    validate(payload)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    frozen_core = {
        **payload,
        "benchmark_protocol_id": protocol["protocol_id"],
        "benchmark_protocol_sha256": sha256_file(PROTOCOL),
    }
    frozen = {
        **frozen_core,
        "registration_payload_sha256": canonical_hash(frozen_core),
        "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "registered_outcome_free_benchmark",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output = args.out_dir / "run_registration.json"
    if output.exists():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing.get("registration_payload_sha256") != frozen["registration_payload_sha256"]:
            raise FileExistsError("registration is write-once and existing content differs")
        print(json.dumps(existing, indent=2, sort_keys=True))
        return 0
    output.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(frozen, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

