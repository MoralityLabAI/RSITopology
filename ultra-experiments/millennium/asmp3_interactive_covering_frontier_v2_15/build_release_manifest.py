from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_15.json"

RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_honest_search_barrier_v2_1/HONEST_SEARCH_BARRIER_THEOREM_v2_1.md",
    "../asmp3_honest_search_barrier_v2_1/RELEASE_MANIFEST_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_verification_v2_1.json",
    "../asmp3_resource_tradeoff_v2_2/RESOURCE_TRADEOFF_THEOREM_v2_2.md",
    "../asmp3_resource_tradeoff_v2_2/RELEASE_MANIFEST_v2_2.json",
    "../asmp3_resource_tradeoff_v2_2/artifacts/resource_tradeoff_v2_2.json",
    "../asmp3_resource_tradeoff_v2_2/artifacts/resource_tradeoff_verification_v2_2.json",
    "../asmp3_correlated_path_risk_v2_13/CORRELATED_PATH_RISK_THEOREM_v2_13.md",
    "../asmp3_correlated_path_risk_v2_13/RELEASE_MANIFEST_v2_13.json",
    "../asmp3_correlated_path_risk_v2_13/artifacts/correlated_path_risk_v2_13.json",
    "../asmp3_correlated_path_risk_v2_13/artifacts/correlated_path_risk_verification_v2_13.json",
    ".gitignore",
    "README.md",
    "INTERACTIVE_COVERING_THEOREM_v2_15.md",
    "COMPLETION_AUDIT_v2_15.md",
    "interactive_covering_frontier.py",
    "run_interactive_covering_frontier.py",
    "verify_interactive_covering_frontier.py",
    "test_interactive_covering_frontier.py",
    "build_release_manifest.py",
    "artifacts/interactive_covering_frontier_v2_15.json",
    "artifacts/interactive_covering_frontier_verification_v2_15.json",
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
        "schema_version": "asmp3_interactive_covering_frontier_release_v2_15",
        "experiment_id": "ASMP-3-INTERACTIVE-COVERING-FRONTIER-v2.15",
        "release_status": "exact_arbitrary_round_public_coin_unique_marker_frontier",
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
        raise RuntimeError("ASMP-3 v2.15 manifest self-check failed")
    print(f"ASMP-3 v2.15 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
