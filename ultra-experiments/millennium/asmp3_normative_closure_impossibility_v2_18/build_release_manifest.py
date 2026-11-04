from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_18.json"

RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_typed_successor_v0_2/typed_successor_v0_2.json",
    "../asmp3_protocol_quantifier_v0_7/PROTOCOL_QUANTIFIER_THEOREM_v0_7.md",
    "../asmp3_protocol_quantifier_v0_7/RELEASE_MANIFEST_v0_7.json",
    "../asmp3_protocol_quantifier_v0_7/artifacts/protocol_quantifier_v0_7.json",
    "../asmp3_protocol_quantifier_v0_7/artifacts/protocol_quantifier_verification_v0_7.json",
    "../asmp3_consolidated_resource_scope_v2_17/RESOURCE_SCOPE_DISPOSITION_v2_17.md",
    "../asmp3_consolidated_resource_scope_v2_17/RELEASE_MANIFEST_v2_17.json",
    "../asmp3_consolidated_resource_scope_v2_17/artifacts/consolidated_resource_scope_v2_17.json",
    "../asmp3_consolidated_resource_scope_v2_17/artifacts/consolidated_resource_scope_verification_v2_17.json",
    "../asmp3_resolution_boundary_v0_3/artifacts/expert_review_status_v0_6.json",
    ".gitignore",
    "README.md",
    "NORMATIVE_CLOSURE_IMPOSSIBILITY_THEOREM_v2_18.md",
    "AUTHORITY_HANDOFF_v2_18.md",
    "COMPLETION_AUDIT_v2_18.md",
    "normative_closure_impossibility.py",
    "run_normative_closure_impossibility.py",
    "verify_normative_closure_impossibility.py",
    "test_normative_closure_impossibility.py",
    "build_release_manifest.py",
    "artifacts/normative_closure_impossibility_v2_18.json",
    "artifacts/normative_closure_impossibility_verification_v2_18.json",
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
        "schema_version": "asmp3_normative_closure_impossibility_release_v2_18",
        "experiment_id": "ASMP-3-NORMATIVE-CLOSURE-IMPOSSIBILITY-v2.18",
        "release_status": "source_relative_impossibility_of_sound_decisive_normative_closure",
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
        raise RuntimeError("ASMP-3 v2.18 manifest self-check failed")
    print(f"ASMP-3 v2.18 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
