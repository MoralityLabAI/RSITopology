from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRATION = HERE / "registration_v0_20.json"
OUTPUT = HERE / "release_manifest_v0_20.json"

EXTRAS = (
    "registration_v0_20.json",
    "artifacts_v0_20/result_v0_20.json",
    "artifacts_v0_20/run_receipt_v0_20.json",
    "artifacts_v0_20/independent_verification_v0_20.json",
    "artifacts_v0_20/RESULT_v0_20.md",
    "POSTRUN_NOTE_v0_20.md",
    "PUBLIC_SUMMARY_v0_20.md",
    "make_release_manifest_v0_20.py",
    "../RESOLUTION_AUDIT_v0_20.md",
    "../../V0_2_EXPERIMENT_PROGRESS_v0_1.md",
    "../../../../docs/ILIAD_FELLOWSHIP_RESEARCH_LINKS_20260727.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(
            f"refusing to overwrite release manifest: {OUTPUT}"
        )
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError(
            "tracked tree must be clean before release manifest"
        )
    registration = json.loads(
        REGISTRATION.read_text(encoding="utf-8")
    )
    paths = {
        relative: REPO / relative
        for relative in registration["sealed_files"]
    }
    for relative in EXTRAS:
        path = (HERE / relative).resolve()
        paths[path.relative_to(REPO).as_posix()] = path
    files = {}
    for relative, path in sorted(paths.items()):
        if not path.is_file():
            raise FileNotFoundError(path)
        files[relative] = sha256(path)
    manifest = {
        "release_id": "ASMP-9-BLOCK-FACTORIZATION-v0.20-release",
        "result_commit": git("rev-parse", "HEAD"),
        "registration_sha256": sha256(REGISTRATION),
        "result_sha256": sha256(
            HERE / "artifacts_v0_20" / "result_v0_20.json"
        ),
        "file_count": len(files),
        "files": files,
    }
    with OUTPUT.open(
        "x", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
