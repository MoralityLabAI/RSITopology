from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from physical_target import run_registered


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    registration = json.loads(args.registration.read_text(encoding="utf-8"))
    for name, expected in registration["source_hashes"].items():
        actual = sha256(ROOT / name)
        if actual != expected:
            raise RuntimeError(f"prereveal hash mismatch: {name}")

    args.output_dir.mkdir(parents=True, exist_ok=False)
    config = json.loads((ROOT / "config_v0_80.json").read_text(encoding="utf-8"))
    primary_result = run_registered(config, args.output_dir / "primary")
    replay_result = run_registered(config, args.output_dir / "replay")

    replay_identical = all(
        (args.output_dir / "primary" / name).read_bytes()
        == (args.output_dir / "replay" / name).read_bytes()
        for name in ("response_rows.jsonl", "result.json")
    )
    sequence = []
    instrument_valid = replay_identical
    w0 = bool(primary_result["gates"]["W0"]["pass"])
    sequence.append({"gate": "W0", "decision": "pass" if w0 else "fail"})
    sequence.append(
        {
            "gate": "I0",
            "decision": "pass" if replay_identical else "not_evaluated",
            "instrument_status": "valid" if replay_identical else "invalid",
        }
    )
    can_continue = w0 and replay_identical
    for gate in ("R0", "L0", "M0"):
        if can_continue:
            passed = bool(primary_result["gates"][gate]["pass"])
            decision = "pass" if passed else "fail"
            can_continue = passed
        else:
            decision = "not_evaluated"
        sequence.append({"gate": gate, "decision": decision})

    adjudication = {
        "experiment_id": registration["experiment_id"],
        "instrument_valid": instrument_valid,
        "fixed_sequence": sequence,
        "overall_pass": all(item["decision"] == "pass" for item in sequence),
        "primary_result": primary_result,
        "claim_boundary": primary_result["claim_boundary"],
    }
    adjudication_path = args.output_dir / "adjudication.json"
    adjudication_path.write_text(
        json.dumps(adjudication, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    receipt = {
        "registration_sha256": sha256(args.registration),
        "primary_rows_sha256": sha256(
            args.output_dir / "primary" / "response_rows.jsonl"
        ),
        "primary_result_sha256": sha256(
            args.output_dir / "primary" / "result.json"
        ),
        "replay_rows_sha256": sha256(
            args.output_dir / "replay" / "response_rows.jsonl"
        ),
        "replay_result_sha256": sha256(
            args.output_dir / "replay" / "result.json"
        ),
        "adjudication_sha256": sha256(adjudication_path),
    }
    (args.output_dir / "execution_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"overall_pass": adjudication["overall_pass"]}))


if __name__ == "__main__":
    main()
