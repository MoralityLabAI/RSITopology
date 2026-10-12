from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from structured_target import canonical_json_bytes, run_registered


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    if registration.get("status") != "registered_prereveal_no_outcomes":
        raise RuntimeError("registration is not prereveal-authorized")
    for name, expected in registration["source_hashes"].items():
        actual = sha256(ROOT / name)
        if actual != expected:
            raise RuntimeError(f"prereveal hash mismatch: {name}")

    args.output_dir.mkdir(parents=True, exist_ok=False)
    config = json.loads((ROOT / "config_v0_81.json").read_text(encoding="utf-8"))
    primary = run_registered(config, args.output_dir / "primary")
    replay = run_registered(config, args.output_dir / "replay")
    del replay

    replay_identical = all(
        (args.output_dir / "primary" / name).read_bytes()
        == (args.output_dir / "replay" / name).read_bytes()
        for name in ("response_rows.jsonl", "result.json", "run_receipt.json")
    )
    sequence = []
    can_continue = True
    for gate in ("W0",):
        passed = bool(primary["gates"][gate]["pass"])
        sequence.append({"gate": gate, "decision": "pass" if passed else "fail"})
        can_continue = can_continue and passed
    sequence.append(
        {
            "gate": "I0",
            "instrument_status": "valid" if replay_identical else "invalid",
            "decision": (
                "pass" if can_continue and replay_identical else "not_evaluated"
            ),
        }
    )
    can_continue = can_continue and replay_identical
    for gate in ("D0", "R0", "L0", "M0"):
        if can_continue:
            passed = bool(primary["gates"][gate]["pass"])
            decision = "pass" if passed else "fail"
            can_continue = passed
        else:
            decision = "not_evaluated"
        sequence.append({"gate": gate, "decision": decision})

    adjudication = {
        "schema_version": "asmp9_structured_target_adjudication_v0_81",
        "experiment_id": registration["experiment_id"],
        "registration_sha256": sha256(registration_path),
        "instrument_valid": replay_identical,
        "fixed_sequence": sequence,
        "overall_pass": all(item["decision"] == "pass" for item in sequence),
        "primary_result": primary,
        "claim_boundary": primary["claim_boundary"],
    }
    adjudication_path = args.output_dir / "adjudication.json"
    adjudication_path.write_bytes(canonical_json_bytes(adjudication))
    receipt = {
        "schema_version": "asmp9_structured_target_execution_receipt_v0_81",
        "registration_sha256": sha256(registration_path),
        "primary_rows_sha256": sha256(
            args.output_dir / "primary" / "response_rows.jsonl"
        ),
        "primary_result_sha256": sha256(
            args.output_dir / "primary" / "result.json"
        ),
        "primary_receipt_sha256": sha256(
            args.output_dir / "primary" / "run_receipt.json"
        ),
        "replay_rows_sha256": sha256(
            args.output_dir / "replay" / "response_rows.jsonl"
        ),
        "replay_result_sha256": sha256(
            args.output_dir / "replay" / "result.json"
        ),
        "replay_receipt_sha256": sha256(
            args.output_dir / "replay" / "run_receipt.json"
        ),
        "adjudication_sha256": sha256(adjudication_path),
    }
    (args.output_dir / "execution_receipt.json").write_bytes(
        canonical_json_bytes(receipt)
    )
    print(
        json.dumps(
            {
                "overall_pass": adjudication["overall_pass"],
                "registration_sha256": receipt["registration_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

