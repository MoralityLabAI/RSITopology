from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_0.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_block_selection_composition_v1_9/BLOCK_SELECTION_COMPOSITION_THEOREM_v1_9.md",
    "../asmp3_block_selection_composition_v1_9/RELEASE_MANIFEST_v1_9.json",
    "../asmp3_block_selection_composition_v1_9/artifacts/block_selection_composition_v1_9.json",
    "../asmp3_independent_noise_amplification_v1_8/INDEPENDENT_NOISE_AMPLIFICATION_THEOREM_v1_8.md",
    "../asmp3_independent_noise_amplification_v1_8/RELEASE_MANIFEST_v1_8.json",
    "../asmp3_independent_noise_amplification_v1_8/artifacts/independent_noise_amplification_v1_8.json",
    ".gitignore",
    "README.md",
    "ENCODING_INVARIANCE_THEOREM_v2_0.md",
    "COMPLETION_AUDIT_v2_0.md",
    "encoding_invariance.py",
    "run_encoding_invariance.py",
    "verify_encoding_invariance.py",
    "test_encoding_invariance.py",
    "build_release_manifest.py",
    "artifacts/encoding_invariance_v2_0.json",
    "artifacts/encoding_invariance_verification_v2_0.json",
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
        "schema_version": "asmp3_encoding_invariance_release_v2_0",
        "experiment_id": "ASMP-3-ENCODING-INVARIANCE-v2.0",
        "release_status": "exact_replication_quotient_invariance_and_macro_cost_barrier",
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
        raise RuntimeError("ASMP-3 v2.0 manifest self-check failed")
    print(f"ASMP-3 v2.0 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
