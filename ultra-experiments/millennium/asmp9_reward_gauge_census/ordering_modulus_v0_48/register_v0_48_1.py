"""Register the additive ASMP-9 v0.48.1 verifier-only repair."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

SEALED = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/VERIFIER_REPAIR_PROTOCOL_v0_48_1.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/verify_result_v0_48_1.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/test_verifier_repair_v0_48_1.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/build_release_v0_48_1.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/registration_v0_48.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/VERIFY_RESULT_v0_48.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/artifacts_v0_48/"
    "experiment_rows_v0_48.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/artifacts_v0_48/"
    "subset_bounds_v0_48.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/artifacts_v0_48/result_v0_48.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    for relative in SEALED:
        path = REPO / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        if tracked.returncode:
            raise RuntimeError(f"repair source is not tracked: {relative}")
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=REPO,
        )
        if dirty.returncode:
            raise RuntimeError(
                f"repair source differs from commit: {relative}"
            )

    payload = {
        "protocol_id": "asmp9-ordering-verifier-repair-v0.48.1",
        "version": "0.48.1",
        "status": "registered_after_outcome_for_verifier_only",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "repair_implementation_commit": git("rev-parse", "HEAD"),
        "scientific_result_commit": (
            "83bae5e5e850a5c586d028745f09ad48a70fc0a5"
        ),
        "expected_recorded_status": (
            "decision_dependent_ordering_not_established"
        ),
        "expected_prediction_gate_X0": False,
        "permitted_change": (
            "independent verifier acceptance mapping only"
        ),
        "scientific_changes_permitted": False,
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SEALED
        },
        "claim_boundary": (
            "Post-outcome provenance repair only. It may verify a valid "
            "registered null but cannot alter, strengthen, or reinterpret "
            "any scientific value or prediction."
        ),
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output = HERE / "registration_v0_48_1.json"
    if output.exists():
        if output.read_bytes() != encoded:
            raise RuntimeError("write-once repair registration mismatch")
    else:
        output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "path": output.relative_to(REPO).as_posix(),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "repair_implementation_commit": payload[
                    "repair_implementation_commit"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
