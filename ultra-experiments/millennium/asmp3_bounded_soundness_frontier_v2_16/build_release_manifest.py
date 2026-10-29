from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_16.json"

RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_correlated_path_risk_v2_13/CORRELATED_PATH_RISK_THEOREM_v2_13.md",
    "../asmp3_correlated_path_risk_v2_13/RELEASE_MANIFEST_v2_13.json",
    "../asmp3_correlated_path_risk_v2_13/artifacts/correlated_path_risk_v2_13.json",
    "../asmp3_correlated_path_risk_v2_13/artifacts/correlated_path_risk_verification_v2_13.json",
    "../asmp3_interactive_covering_frontier_v2_15/INTERACTIVE_COVERING_THEOREM_v2_15.md",
    "../asmp3_interactive_covering_frontier_v2_15/RELEASE_MANIFEST_v2_15.json",
    "../asmp3_interactive_covering_frontier_v2_15/artifacts/interactive_covering_frontier_v2_15.json",
    "../asmp3_interactive_covering_frontier_v2_15/artifacts/interactive_covering_frontier_verification_v2_15.json",
    ".gitignore",
    "README.md",
    "BOUNDED_SOUNDNESS_THEOREM_v2_16.md",
    "COMPLETION_AUDIT_v2_16.md",
    "bounded_soundness_frontier.py",
    "run_bounded_soundness_frontier.py",
    "verify_bounded_soundness_frontier.py",
    "test_bounded_soundness_frontier.py",
    "build_release_manifest.py",
    "artifacts/bounded_soundness_frontier_v2_16.json",
    "artifacts/bounded_soundness_frontier_verification_v2_16.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def build_manifest() -> dict[str, object]:
    files: dict[str, object] = {}
    for relative in RELEASE_FILES:
        path = HERE / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        files[relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return {
        "schema_version": "asmp3_bounded_soundness_frontier_release_v2_16",
        "experiment_id": "ASMP-3-BOUNDED-SOUNDNESS-FRONTIER-v2.16",
        "release_status": "exact_public_coin_interactive_marker_frontier_with_bounded_soundness",
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
    return MANIFEST_PATH.is_file() and json.loads(
        MANIFEST_PATH.read_text(encoding="utf-8")
    ) == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 v2.16 manifest self-check failed")
    print(f"ASMP-3 v2.16 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
