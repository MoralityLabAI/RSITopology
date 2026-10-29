from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_12.json"

UPSTREAM_PACKAGES = (
    ("asmp3_protocol_quantifier_v0_7", "RELEASE_MANIFEST_v0_7.json", "artifacts/protocol_quantifier_v0_7.json", "artifacts/protocol_quantifier_verification_v0_7.json"),
    ("asmp3_encoding_invariance_v2_0", "RELEASE_MANIFEST_v2_0.json", "artifacts/encoding_invariance_v2_0.json", "artifacts/encoding_invariance_verification_v2_0.json"),
    ("asmp3_honest_search_barrier_v2_1", "RELEASE_MANIFEST_v2_1.json", "artifacts/honest_search_barrier_v2_1.json", "artifacts/honest_search_barrier_verification_v2_1.json"),
    ("asmp3_resource_tradeoff_v2_2", "RELEASE_MANIFEST_v2_2.json", "artifacts/resource_tradeoff_v2_2.json", "artifacts/resource_tradeoff_verification_v2_2.json"),
    ("asmp3_constructive_refutation_protocol_v2_3", "RELEASE_MANIFEST_v2_3.json", "artifacts/constructive_refutation_protocol_v2_3.json", "artifacts/constructive_refutation_protocol_verification_v2_3.json"),
    ("asmp3_randomized_finder_amplification_v2_4", "RELEASE_MANIFEST_v2_4.json", "artifacts/randomized_finder_amplification_v2_4.json", "artifacts/randomized_finder_amplification_verification_v2_4.json"),
    ("asmp3_witness_transparent_normal_form_v2_5", "RELEASE_MANIFEST_v2_5.json", "artifacts/witness_transparent_normal_form_v2_5.json", "artifacts/witness_transparent_normal_form_verification_v2_5.json"),
    ("asmp3_adaptive_transcript_coupling_v2_7", "RELEASE_MANIFEST_v2_7.json", "artifacts/adaptive_transcript_coupling_v2_7.json", "artifacts/adaptive_transcript_coupling_verification_v2_7.json"),
    ("asmp3_trace_binding_extractor_v2_8", "RELEASE_MANIFEST_v2_8.json", "artifacts/trace_binding_extractor_v2_8.json", "artifacts/trace_binding_extractor_verification_v2_8.json"),
    ("asmp3_oracle_parametric_replay_v2_9", "RELEASE_MANIFEST_v2_9.json", "artifacts/oracle_parametric_replay_v2_9.json", "artifacts/oracle_parametric_replay_verification_v2_9.json"),
    ("asmp3_online_noisy_trace_extractor_v2_10", "RELEASE_MANIFEST_v2_10.json", "artifacts/online_noisy_trace_extractor_v2_10.json", "artifacts/online_noisy_trace_extractor_verification_v2_10.json"),
    ("asmp3_online_contract_minimality_v2_11", "RELEASE_MANIFEST_v2_11.json", "artifacts/online_contract_minimality_v2_11.json", "artifacts/online_contract_minimality_verification_v2_11.json"),
)

RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_resolution_boundary_v0_3/artifacts/expert_review_status_v0_6.json",
    "../asmp3_online_contract_minimality_v2_11/STOPPING_BOUNDARY_v2_11.md",
    *tuple(
        f"../{directory}/{relative}"
        for directory, manifest, result, verifier in UPSTREAM_PACKAGES
        for relative in (manifest, result, verifier)
    ),
    ".gitignore",
    "README.md",
    "RESOLUTION_DISPOSITION_v2_12.md",
    "REQUIREMENT_EVIDENCE_MATRIX_v2_12.md",
    "EXTERNAL_REVIEW_HANDOFF_v2_12.md",
    "STOPPING_DECISION_v2_12.md",
    "COMPLETION_AUDIT_v2_12.md",
    "consolidated_resolution_disposition.py",
    "run_consolidated_resolution_disposition.py",
    "verify_consolidated_resolution_disposition.py",
    "test_consolidated_resolution_disposition.py",
    "build_release_manifest.py",
    "artifacts/consolidated_resolution_disposition_v2_12.json",
    "artifacts/consolidated_resolution_disposition_verification_v2_12.json",
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
        "schema_version": "asmp3_consolidated_resolution_disposition_release_v2_12",
        "experiment_id": "ASMP-3-CONSOLIDATED-RESOLUTION-DISPOSITION-v2.12",
        "release_status": "literal_refutation_online_subclass_minimality_and_updated_stop_disposition",
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
        raise RuntimeError("ASMP-3 v2.12 manifest self-check failed")
    print(f"ASMP-3 v2.12 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
