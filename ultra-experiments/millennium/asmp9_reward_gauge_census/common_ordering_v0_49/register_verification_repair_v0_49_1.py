"""Register the post-outcome v0.49.1 universe repair."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
LOCAL_SOURCES = (
    "UNIVERSE_REPAIR_PROTOCOL_v0_49_1.md",
    "verify_theorems_v0_49_1.py",
    "test_universe_repair_v0_49_1.py",
    "verification_registration_v0_49.json",
    "VERIFY_RESULT_v0_49.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    output = HERE / "verification_repair_registration_v0_49_1.json"
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
    source_paths = [HERE / name for name in LOCAL_SOURCES]
    for path in source_paths:
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
            raise RuntimeError(f"untracked repair source: {relative}")
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=REPO,
        )
        if dirty.returncode:
            raise RuntimeError(f"dirty repair source: {relative}")
    payload = {
        "protocol_id": (
            "asmp9-common-ordering-verification-repair-v0.49.1"
        ),
        "version": "0.49.1",
        "status": "registered_after_count_mismatch_for_verifier_only",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "repair_source_commit": git("rev-parse", "HEAD"),
        "original_verification_sha256": sha256(
            HERE / "VERIFY_RESULT_v0_49.json"
        ),
        "original_expected_table_count": 168,
        "corrected_admissible_table_count": 167,
        "corrected_ordered_pair_count": 167**2,
        "scientific_changes_permitted": False,
        "source_sha256": {
            path.relative_to(REPO).as_posix(): sha256(path)
            for path in source_paths
        },
        "claim_boundary": (
            "Post-outcome universe-count repair only. No theorem value, "
            "witness, enumeration row, test, or scientific gate may change."
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
                "repair_source_commit": payload[
                    "repair_source_commit"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
