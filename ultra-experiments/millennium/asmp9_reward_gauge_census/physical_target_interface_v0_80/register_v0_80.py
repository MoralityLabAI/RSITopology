from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "registration_v0_80.json"
FILES = (
    "PROTOCOL_v0_80.md",
    "config_v0_80.json",
    "physical_target.py",
    "run_experiment.py",
    "execute_registered.py",
    "test_physical_target.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = {
        "experiment_id": "ASMP9-PHYSICAL-TARGET-INTERFACE-v0.80",
        "status": "registered_prereveal_no_outcomes",
        "source_hashes": {name: sha256(ROOT / name) for name in FILES},
        "environment": {
            "python": sys.version,
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "claim_boundary": (
            "Controlled finite-MDP softmax demonstrator only; registration "
            "precedes outcomes and does not constitute ASMP-9 evidence."
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
