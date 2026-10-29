from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_6.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_protocol_quantifier_v0_7/RELEASE_MANIFEST_v0_7.json",
    "../asmp3_protocol_quantifier_v0_7/artifacts/protocol_quantifier_v0_7.json",
    "../asmp3_protocol_quantifier_v0_7/artifacts/protocol_quantifier_verification_v0_7.json",
    "../asmp3_block_selection_composition_v1_9/RELEASE_MANIFEST_v1_9.json",
    "../asmp3_block_selection_composition_v1_9/artifacts/block_selection_composition_v1_9.json",
    "../asmp3_block_selection_composition_v1_9/artifacts/block_selection_composition_verification_v1_9.json",
    "../asmp3_encoding_invariance_v2_0/RELEASE_MANIFEST_v2_0.json",
    "../asmp3_encoding_invariance_v2_0/artifacts/encoding_invariance_v2_0.json",
    "../asmp3_encoding_invariance_v2_0/artifacts/encoding_invariance_verification_v2_0.json",
    "../asmp3_honest_search_barrier_v2_1/RELEASE_MANIFEST_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_verification_v2_1.json",
    "../asmp3_resource_tradeoff_v2_2/RELEASE_MANIFEST_v2_2.json",
    "../asmp3_resource_tradeoff_v2_2/artifacts/resource_tradeoff_v2_2.json",
    "../asmp3_resource_tradeoff_v2_2/artifacts/resource_tradeoff_verification_v2_2.json",
    "../asmp3_constructive_refutation_protocol_v2_3/RELEASE_MANIFEST_v2_3.json",
    "../asmp3_constructive_refutation_protocol_v2_3/artifacts/constructive_refutation_protocol_v2_3.json",
    "../asmp3_constructive_refutation_protocol_v2_3/artifacts/constructive_refutation_protocol_verification_v2_3.json",
    "../asmp3_randomized_finder_amplification_v2_4/RELEASE_MANIFEST_v2_4.json",
    "../asmp3_randomized_finder_amplification_v2_4/artifacts/randomized_finder_amplification_v2_4.json",
    "../asmp3_randomized_finder_amplification_v2_4/artifacts/randomized_finder_amplification_verification_v2_4.json",
    "../asmp3_witness_transparent_normal_form_v2_5/RELEASE_MANIFEST_v2_5.json",
    "../asmp3_witness_transparent_normal_form_v2_5/artifacts/witness_transparent_normal_form_v2_5.json",
    "../asmp3_witness_transparent_normal_form_v2_5/artifacts/witness_transparent_normal_form_verification_v2_5.json",
    "../asmp3_resolution_boundary_v0_3/artifacts/expert_review_status_v0_6.json",
    ".gitignore",
    "README.md",
    "RESOLUTION_DISPOSITION_v2_6.md",
    "REQUIREMENT_EVIDENCE_MATRIX_v2_6.md",
    "STOPPING_BOUNDARY_v2_6.md",
    "EXTERNAL_REVIEW_HANDOFF_v2_6.md",
    "COMPLETION_AUDIT_v2_6.md",
    "resolution_disposition.py",
    "run_resolution_disposition.py",
    "verify_resolution_disposition.py",
    "test_resolution_disposition.py",
    "build_release_manifest.py",
    "artifacts/resolution_disposition_v2_6.json",
    "artifacts/resolution_disposition_verification_v2_6.json",
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
        "schema_version": "asmp3_resolution_disposition_release_v2_6",
        "experiment_id": "ASMP-3-RESOLUTION-DISPOSITION-v2.6",
        "release_status": "evidence_backed_negative_conjecture_disposition_and_stop_boundary",
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
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 v2.6 manifest self-check failed")
    print(f"ASMP-3 v2.6 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
