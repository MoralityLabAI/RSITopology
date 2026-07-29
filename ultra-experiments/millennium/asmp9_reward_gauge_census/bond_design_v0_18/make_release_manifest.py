from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

PATHS = (
    "DEVELOPMENT_NOTE_v0_18.md",
    "FORMULATION_DRAFT_v0_18.md",
    "POSTRUN_NOTE_v0_18.md",
    "PRIOR_ART_GATE_v0_18.md",
    "PROTOCOL_v0_18.md",
    "PUBLIC_SUMMARY_v0_18.md",
    "README.md",
    "artifacts_v0_18/RESULT_v0_18.md",
    "artifacts_v0_18/result_v0_18.json",
    "artifacts_v0_18/run_receipt_v0_18.json",
    "artifacts_v0_18/verification_v0_18.json",
    "bond_design.py",
    "development_check.py",
    "make_release_manifest.py",
    "protocol_v0_18.json",
    "register.py",
    "registration_v0_18.json",
    "run_verification.py",
    "test_bond_design.py",
    "test_protocol.py",
    "verify_result.py",
    "../RESOLUTION_AUDIT_v0_18.md",
    "../README.md",
    "../../V0_2_EXPERIMENT_PROGRESS_v0_1.md",
    "../../../../docs/ILIAD_FELLOWSHIP_RESEARCH_LINKS_20260727.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite manifest: {output}")

    registration = json.loads(
        (HERE / "registration_v0_18.json").read_text(encoding="utf-8")
    )
    result = json.loads(
        (HERE / "artifacts_v0_18/result_v0_18.json").read_text(
            encoding="utf-8"
        )
    )
    verification = json.loads(
        (HERE / "artifacts_v0_18/verification_v0_18.json").read_text(
            encoding="utf-8"
        )
    )
    files: dict[str, str] = {}
    for relative in PATHS:
        path = (HERE / relative).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        files[path.relative_to(REPO).as_posix()] = sha256(path)

    manifest = {
        "release_id": "ASMP-9-BOND-DESIGN-v0.18-release",
        "release_commit_parent": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip(),
        "implementation_commit": registration["implementation_commit"],
        "registration_sha256": sha256(HERE / "registration_v0_18.json"),
        "verdict": result["verdict"],
        "gate_pass_count": sum(result["gates"].values()),
        "gate_count": len(result["gates"]),
        "independent_status": (
            "pass" if verification["pass"] else "fail"
        ),
        "independent_check_count": verification["check_count"],
        "files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, manifest)
    print(
        json.dumps(
            {
                "file_count": len(files),
                "manifest_sha256": sha256(output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
