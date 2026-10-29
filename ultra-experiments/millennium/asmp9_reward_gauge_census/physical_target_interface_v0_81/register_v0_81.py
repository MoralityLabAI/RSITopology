from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "registration_v0_81.json"
FILES = (
    "README.md",
    "PRIOR_ART_GATE_v0_81.md",
    "DESIGN_FROM_BURNED_v0_81.md",
    "PROTOCOL_v0_81.md",
    "config_v0_81.json",
    "structured_target.py",
    "execute_registered.py",
    "test_structured_target.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = {
        "schema_version": "asmp9_structured_target_registration_v0_81",
        "experiment_id": "ASMP9-STRUCTURED-PHYSICAL-TARGET-v0.81",
        "status": "registered_prereveal_no_outcomes",
        "parent_negative_result": {
            "path": "../physical_target_interface_v0_80/RESULT_v0_80.md",
            "sha256": sha256(
                ROOT.parent / "physical_target_interface_v0_80" / "RESULT_v0_80.md"
            ),
        },
        "source_hashes": {name: sha256(ROOT / name) for name in FILES},
        "environment": {
            "python": sys.version,
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "outcomes_read": False,
        "claim_boundary": (
            "Known intervention offsets in one controlled finite-MDP softmax "
            "fixture only; registration precedes outcomes and does not resolve ASMP-9."
        ),
    }
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if OUTPUT.exists():
        if OUTPUT.read_text(encoding="utf-8") != serialized:
            raise RuntimeError("registration exists with different bytes")
        print(f"registration_unchanged {sha256(OUTPUT)}")
        return
    with OUTPUT.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)
    print(f"registration_created {sha256(OUTPUT)}")


if __name__ == "__main__":
    main()
