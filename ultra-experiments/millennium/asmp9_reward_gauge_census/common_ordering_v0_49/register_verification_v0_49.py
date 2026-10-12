"""Register source hashes for the ASMP-9 v0.49 theorem verification."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
LOCAL_SOURCES = (
    "README.md",
    "DEVELOPMENT_RESULT_v0_49.md",
    "PRIOR_ART_GATE_v0_49.md",
    "THEOREM_DRAFT_v0_49.md",
    "VERIFICATION_PROTOCOL_v0_49.md",
    "common_ordering.py",
    "test_common_ordering.py",
    "verify_theorems_v0_49.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    output = HERE / "verification_registration_v0_49.json"
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
            raise RuntimeError(f"untracked verification source: {relative}")
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=REPO,
        )
        if dirty.returncode:
            raise RuntimeError(f"dirty verification source: {relative}")

    payload = {
        "protocol_id": "asmp9-common-ordering-verification-v0.49",
        "version": "0.49",
        "status": "registered_before_verification_sweep",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "source_commit": git("rev-parse", "HEAD"),
        "expected_test_count": 7,
        "expected_monotone_binary_table_count": 168,
        "expected_ordered_pair_count": 168 * 168,
        "resource_ceiling": {
            "seconds": 120,
            "peak_aggregate_working_set_bytes": 512 * 1024 * 1024,
            "worker_processes": 1,
        },
        "source_sha256": {
            path.relative_to(REPO).as_posix(): sha256(path)
            for path in source_paths
        },
        "claim_boundary": (
            "Verification of finite theorem consequences only; not a "
            "prospective empirical result, novelty claim, physical "
            "preference-channel validation, or ASMP-9 resolution."
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
