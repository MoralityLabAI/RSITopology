"""Write-once prospective registration for ASMP-9 v0.63."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = HERE / "verification_registration_v0_63.json"
RESULT = HERE / "VERIFY_RESULT_v0_63.json"
PREFIX = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "capped_simplex_modulus_v0_63/"
)

SOURCE_FILES = tuple(
    PREFIX + name
    for name in (
        "PRIOR_ART_GATE_v0_63.md",
        "PROOF_AUDIT_v0_63.md",
        "README.md",
        "THEOREM_DRAFT_v0_63.md",
        "VERIFICATION_PROTOCOL_v0_63.md",
        "capped_simplex_modulus.py",
        "independent_replay_v0_63.py",
        "primary_verifier_v0_63.py",
        "register_verification_v0_63.py",
        "test_capped_simplex_modulus.py",
        "verification_cells_v0_63.json",
        "verify_v0_63.py",
    )
)

BURNED_FILES = tuple(
    PREFIX + name
    for name in (
        "DEVELOPMENT_RESULT_v0_63.md",
        "verify_development.py",
    )
) + (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "exact_modulus_slice_v0_62/DEVELOPMENT_RESULT_v0_62.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("cannot register after a verification result")
    cells = json.loads(
        (HERE / "verification_cells_v0_63.json").read_text(encoding="utf-8")
    )
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        text=True,
    ).strip()
    registration = {
        "burned_inputs_sha256": {
            relative: sha256(REPO / relative)
            for relative in BURNED_FILES
        },
        "claim_boundary": (
            "Exact full-dimensional three-alternative fixed-binary "
            "capped-simplex calibration only; classical convex geometry; "
            "no general efficient RUM-modulus, hidden-menu, latent-"
            "confounding, strategic/dynamic, physical-access, welfare, "
            "novelty, or full ASMP-9 resolution claim."
        ),
        "expected_test_count": 8,
        "freshness": cells["burned"],
        "protocol_id": cells["protocol_id"],
        "resource_caps": cells["resource_caps"],
        "schema": "asmp9-v0.63-verification-registration-v1",
        "source_commit": commit,
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SOURCE_FILES
        },
        "test_command": (
            "python -m pytest -q -p no:cacheprovider "
            + PREFIX
            + "test_capped_simplex_modulus.py"
        ),
        "verification_command": "python " + PREFIX + "verify_v0_63.py",
    }
    encoded = (
        json.dumps(registration, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if OUTPUT.exists():
        if OUTPUT.read_bytes() != encoded:
            raise FileExistsError("registration exists with different bytes")
    else:
        OUTPUT.write_bytes(encoded)
    print(sha256(OUTPUT))


if __name__ == "__main__":
    main()

