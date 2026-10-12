from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_20.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_typed_successor_v0_2/typed_successor_v0_2.json",
    "../asmp3_protocol_quantifier_v0_7/PROTOCOL_QUANTIFIER_THEOREM_v0_7.md",
    "../asmp3_protocol_quantifier_v0_7/artifacts/protocol_quantifier_v0_7.json",
    "../asmp3_finite_tv_frontier_v0_8/FINITE_TV_FRONTIER_THEOREM_v0_8.md",
    "../asmp3_finite_tv_frontier_v0_8/artifacts/finite_tv_frontier_v0_8.json",
    "../asmp3_sequence_form_bridge_v1_3/SEQUENCE_FORM_THEOREM_v1_3.md",
    "../asmp3_sequence_form_bridge_v1_3/artifacts/sequence_form_bridge_v1_3.json",
    "../asmp3_encoding_invariance_v2_0/artifacts/encoding_invariance_v2_0.json",
    "../asmp3_consolidated_resource_scope_v2_17/artifacts/consolidated_resource_scope_v2_17.json",
    "../asmp3_normative_closure_reassessment_v2_19/artifacts/normative_closure_reassessment_v2_19.json",
    ".gitignore",
    "README.md",
    "ASMP3_RESEARCH_REPORT_v2_20.md",
    "UNIFORM_MEMBERSHIP_UNDECIDABILITY_THEOREM_v2_20.md",
    "REQUIREMENT_AUDIT_v2_20.md",
    "RESOLUTION_DISPOSITION_v2_20.md",
    "PRIOR_ART_BOUNDARY_v2_20.md",
    "COMPLETION_AUDIT_v2_20.md",
    "uniform_membership_undecidability.py",
    "run_uniform_membership_undecidability.py",
    "verify_uniform_membership_undecidability.py",
    "test_uniform_membership_undecidability.py",
    "build_release_manifest.py",
    "artifacts/uniform_membership_undecidability_v2_20.json",
    "artifacts/uniform_membership_undecidability_verification_v2_20.json",
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
        "schema_version": "asmp3_uniform_membership_undecidability_release_v2_20",
        "experiment_id": "ASMP-3-UNIFORM-MEMBERSHIP-UNDECIDABILITY-v2.20",
        "release_status": "strict_FIX_arbitrary_computable_uniform_membership_undecidable_parent_resolution_conditional_on_representation",
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
    return MANIFEST_PATH.is_file() and json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 v2.20 release manifest verification failed")
    print(f"ASMP-3 v2.20 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
