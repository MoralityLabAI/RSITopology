"""Create the write-once ASMP-9 v0.50 verification registration."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCES = (
    "README.md",
    "DEVELOPMENT_RESULT_v0_50.md",
    "PRIOR_ART_GATE_v0_50.md",
    "THEOREM_DRAFT_v0_50.md",
    "VERIFICATION_PROTOCOL_v0_50.md",
    "reference_weight.py",
    "test_reference_weight.py",
    "test_verifier_v0_50.py",
    "verify_theorems_v0_50.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    output = HERE / "verification_registration_v0_50.json"
    if output.exists():
        print(
            json.dumps(
                {
                    "path": output.relative_to(REPO).as_posix(),
                    "sha256": sha256(output),
                    "status": "already_registered",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    paths = [HERE / name for name in SOURCES]
    for path in paths:
        relative = path.relative_to(REPO).as_posix()
        if not path.is_file():
            raise FileNotFoundError(path)
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        if tracked.returncode:
            raise RuntimeError(f"untracked source: {relative}")
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=REPO,
        )
        if dirty.returncode:
            raise RuntimeError(f"dirty source: {relative}")

    payload = {
        "protocol_id": (
            "asmp9-reference-weight-robustness-verification-v0.50"
        ),
        "version": "0.50",
        "status": "registered_before_exhaustive_verification",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "source_commit": git("rev-parse", "HEAD"),
        "expected_admissible_table_count": 19,
        "expected_ordered_pair_count": 361,
        "reference_vertices": [
            ["1/2", "1/3", "1/6"],
            ["1/6", "1/3", "1/2"],
        ],
        "interpolation_coefficients": [
            "0",
            "1/4",
            "1/2",
            "3/4",
            "1",
        ],
        "region_grid_denominator": 6,
        "expected_region_checks": 1140,
        "expected_test_count": 11,
        "resource_ceiling": {
            "seconds": 120,
            "peak_aggregate_working_set_bytes": 536870912,
            "worker_processes": 1,
        },
        "source_sha256": {
            path.relative_to(REPO).as_posix(): sha256(path)
            for path in paths
        },
        "claim_boundary": (
            "Finite theorem verification only; not novelty, an empirical "
            "preference result, continuous or strategic robustness, or an "
            "ASMP-9 resolution."
        ),
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "path": output.relative_to(REPO).as_posix(),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "source_commit": payload["source_commit"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
