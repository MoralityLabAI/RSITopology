from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_3.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_block_selection_composition_v1_9/BLOCK_SELECTION_COMPOSITION_THEOREM_v1_9.md",
    "../asmp3_block_selection_composition_v1_9/RELEASE_MANIFEST_v1_9.json",
    "../asmp3_block_selection_composition_v1_9/artifacts/block_selection_composition_v1_9.json",
    "../asmp3_encoding_invariance_v2_0/ENCODING_INVARIANCE_THEOREM_v2_0.md",
    "../asmp3_encoding_invariance_v2_0/RELEASE_MANIFEST_v2_0.json",
    "../asmp3_encoding_invariance_v2_0/artifacts/encoding_invariance_v2_0.json",
    "../asmp3_honest_search_barrier_v2_1/HONEST_SEARCH_BARRIER_THEOREM_v2_1.md",
    "../asmp3_honest_search_barrier_v2_1/RELEASE_MANIFEST_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_v2_1.json",
    "../asmp3_resource_tradeoff_v2_2/RESOURCE_TRADEOFF_THEOREM_v2_2.md",
    "../asmp3_resource_tradeoff_v2_2/RELEASE_MANIFEST_v2_2.json",
    "../asmp3_resource_tradeoff_v2_2/artifacts/resource_tradeoff_v2_2.json",
    ".gitignore",
    "README.md",
    "CONSTRUCTIVE_REFUTATION_PROTOCOL_THEOREM_v2_3.md",
    "COMPLETION_AUDIT_v2_3.md",
    "constructive_refutation_protocol.py",
    "run_constructive_refutation_protocol.py",
    "verify_constructive_refutation_protocol.py",
    "test_constructive_refutation_protocol.py",
    "build_release_manifest.py",
    "artifacts/constructive_refutation_protocol_v2_3.json",
    "artifacts/constructive_refutation_protocol_verification_v2_3.json",
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
        "schema_version": "asmp3_constructive_refutation_protocol_release_v2_3",
        "experiment_id": "ASMP-3-CONSTRUCTIVE-REFUTATION-PROTOCOL-v2.3",
        "release_status": "constructive_positive_protocol_under_typed_finder_noise_contracts",
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
        raise RuntimeError("ASMP-3 v2.3 manifest self-check failed")
    print(f"ASMP-3 v2.3 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
