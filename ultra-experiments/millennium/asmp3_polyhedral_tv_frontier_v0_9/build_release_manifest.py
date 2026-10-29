from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v0_9.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_finite_tv_frontier_v0_8/FINITE_TV_FRONTIER_THEOREM_v0_8.md",
    "../asmp3_finite_tv_frontier_v0_8/RELEASE_MANIFEST_v0_8.json",
    "../asmp3_finite_tv_frontier_v0_8/artifacts/finite_tv_frontier_v0_8.json",
    ".gitignore",
    "README.md",
    "POLYHEDRAL_TV_FRONTIER_THEOREM_v0_9.md",
    "COMPLETION_AUDIT_v0_9.md",
    "polyhedral_tv_frontier.py",
    "run_polyhedral_tv_frontier.py",
    "verify_polyhedral_tv_frontier.py",
    "test_polyhedral_tv_frontier.py",
    "build_release_manifest.py",
    "artifacts/polyhedral_tv_frontier_v0_9.json",
    "artifacts/polyhedral_tv_frontier_verification_v0_9.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def build_manifest() -> dict[str, object]:
    files = {}
    for relative in RELEASE_FILES:
        path = HERE / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        files[relative] = {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    return {
        "schema_version": "asmp3_polyhedral_tv_frontier_release_v0_9",
        "experiment_id": "ASMP-3-POLYHEDRAL-TV-FRONTIER-v0.9",
        "release_status": "exact_rational_polyhedral_subtheorem",
        "deterministic": True,
        "file_count": len(files),
        "files": files,
    }


def write_manifest() -> None:
    MANIFEST_PATH.write_text(
        json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify_manifest() -> bool:
    if not MANIFEST_PATH.is_file():
        return False
    recorded = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return recorded == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 v0.9 manifest self-check failed")
    print(f"ASMP-3 v0.9 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
