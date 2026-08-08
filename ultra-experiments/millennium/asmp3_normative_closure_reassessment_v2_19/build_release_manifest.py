from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_19.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_typed_successor_v0_2/typed_successor_v0_2.json",
    "../asmp3_protocol_quantifier_v0_7/PROTOCOL_QUANTIFIER_THEOREM_v0_7.md",
    "../asmp3_protocol_quantifier_v0_7/artifacts/protocol_quantifier_v0_7.json",
    "../asmp3_witness_transparent_normal_form_v2_5/WITNESS_TRANSPARENT_NORMAL_FORM_THEOREM_v2_5.md",
    "../asmp3_witness_transparent_normal_form_v2_5/artifacts/witness_transparent_normal_form_v2_5.json",
    "../asmp3_consolidated_resource_scope_v2_17/RESOURCE_SCOPE_DISPOSITION_v2_17.md",
    "../asmp3_consolidated_resource_scope_v2_17/artifacts/consolidated_resource_scope_v2_17.json",
    "../asmp3_normative_closure_impossibility_v2_18/NORMATIVE_CLOSURE_IMPOSSIBILITY_THEOREM_v2_18.md",
    "../asmp3_normative_closure_impossibility_v2_18/SUPERSEDED_BY_v2_19.md",
    "../asmp3_normative_closure_impossibility_v2_18/artifacts/normative_closure_impossibility_v2_18.json",
    "../asmp3_normative_closure_impossibility_v2_18/artifacts/normative_closure_impossibility_verification_v2_18.json",
    "../asmp3_resolution_boundary_v0_3/artifacts/expert_review_status_v0_6.json",
    ".gitignore",
    "README.md",
    "ASMP3_RESEARCH_REPORT_v2_19.md",
    "REASSESSMENT_AND_CORRECTION_v2_19.md",
    "STRICT_FIX_DISPOSITION_v2_19.md",
    "LANE_STOP_AND_RESUME_v2_19.md",
    "COMPLETION_AUDIT_v2_19.md",
    "normative_closure_reassessment.py",
    "run_normative_closure_reassessment.py",
    "verify_normative_closure_reassessment.py",
    "test_normative_closure_reassessment.py",
    "build_release_manifest.py",
    "artifacts/normative_closure_reassessment_v2_19.json",
    "artifacts/normative_closure_reassessment_verification_v2_19.json",
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
        "schema_version": "asmp3_normative_closure_reassessment_release_v2_19",
        "experiment_id": "ASMP-3-NORMATIVE-CLOSURE-REASSESSMENT-v2.19",
        "release_status": "v2_18_goal_completion_withdrawn_conditional_lemma_retained_full_ASMP3_open",
        "deterministic": True,
        "file_count": len(files),
        "files": files,
    }


def write_manifest() -> None:
    MANIFEST_PATH.write_text(json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def verify_manifest() -> bool:
    return MANIFEST_PATH.is_file() and json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 v2.19 reassessment manifest verification failed")
    print(f"ASMP-3 v2.19 reassessment manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
