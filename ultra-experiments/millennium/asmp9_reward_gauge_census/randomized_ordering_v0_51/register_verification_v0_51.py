"""Create the write-once ASMP-9 v0.51 verification registration."""

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
    "DEVELOPMENT_RESULT_v0_51.md",
    "PRIOR_ART_GATE_v0_51.md",
    "THEOREM_DRAFT_v0_51.md",
    "VERIFICATION_PROTOCOL_v0_51.md",
    "randomized_ordering.py",
    "test_randomized_ordering.py",
    "test_verifier_v0_51.py",
    "verify_theorems_v0_51.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    output = HERE / "verification_registration_v0_51.json"
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
            "asmp9-randomized-ordering-verification-v0.51"
        ),
        "version": "0.51",
        "status": "registered_before_exhaustive_verification",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "source_commit": git("rev-parse", "HEAD"),
        "expected_table_count": 19,
        "expected_ordered_pair_count": 361,
        "expected_ordering_count": 6,
        "expected_scenario_count": 4,
        "reference_vertices": [
            ["1/2", "1/3", "1/6"],
            ["1/6", "1/3", "1/2"],
        ],
        "expected_test_count": 10,
        "resource_ceiling": {
            "seconds": 180,
            "peak_aggregate_working_set_bytes": 536870912,
            "worker_processes": 1,
        },
        "source_sha256": {
            path.relative_to(REPO).as_posix(): sha256(path)
            for path in paths
        },
        "claim_boundary": (
            "Finite Buehler specialization of established randomized "
            "minmax regret; not novelty, operational authorization, "
            "physical preference evidence, or an ASMP-9 resolution."
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
