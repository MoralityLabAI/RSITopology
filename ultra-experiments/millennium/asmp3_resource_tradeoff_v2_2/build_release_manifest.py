from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_2.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_honest_search_barrier_v2_1/HONEST_SEARCH_BARRIER_THEOREM_v2_1.md",
    "../asmp3_honest_search_barrier_v2_1/RELEASE_MANIFEST_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_v2_1.json",
    "../asmp3_block_selection_composition_v1_9/BLOCK_SELECTION_COMPOSITION_THEOREM_v1_9.md",
    "../asmp3_block_selection_composition_v1_9/RELEASE_MANIFEST_v1_9.json",
    "../asmp3_block_selection_composition_v1_9/artifacts/block_selection_composition_v1_9.json",
    ".gitignore",
    "README.md",
    "RESOURCE_TRADEOFF_THEOREM_v2_2.md",
    "COMPLETION_AUDIT_v2_2.md",
    "resource_tradeoff.py",
    "run_resource_tradeoff.py",
    "verify_resource_tradeoff.py",
    "test_resource_tradeoff.py",
    "build_release_manifest.py",
    "artifacts/resource_tradeoff_v2_2.json",
    "artifacts/resource_tradeoff_verification_v2_2.json",
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
        files[relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return {
        "schema_version": "asmp3_resource_tradeoff_release_v2_2",
        "experiment_id": "ASMP-3-RESOURCE-TRADEOFF-v2.2",
        "release_status": "exact_unique_marker_communication_query_frontier",
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
        raise RuntimeError("ASMP-3 v2.2 manifest self-check failed")
    print(f"ASMP-3 v2.2 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
