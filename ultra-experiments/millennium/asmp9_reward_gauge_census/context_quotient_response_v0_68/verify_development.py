"""Import-independent exact verifier for the v0.68 development theorem."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "asmp9_response_quotient_v068", HERE / "response_quotient.py"
)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": "asmp9_context_quotient_development_verification_v0_68",
        "status": "passed",
        "audit": module.exhaustive_small_audit(),
        "source_sha256": sha256(HERE / "response_quotient.py"),
        "claim_boundary": (
            "Exact finite measurement-nuisance quotient only; no reward "
            "identification, behavioral validation, or ASMP-9 resolution."
        ),
    }
    payload = (
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(payload.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
