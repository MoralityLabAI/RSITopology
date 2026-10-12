from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_17.json"

RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_resolution_boundary_v0_3/artifacts/expert_review_status_v0_6.json",
    "../asmp3_consolidated_path_risk_disposition_v2_14/RESOLUTION_DISPOSITION_v2_14.md",
    "../asmp3_consolidated_path_risk_disposition_v2_14/REQUIREMENT_EVIDENCE_MATRIX_v2_14.md",
    "../asmp3_consolidated_path_risk_disposition_v2_14/HARNESS_STOP_CERTIFICATE_v2_14.md",
    "../asmp3_consolidated_path_risk_disposition_v2_14/RELEASE_MANIFEST_v2_14.json",
    "../asmp3_consolidated_path_risk_disposition_v2_14/artifacts/consolidated_path_risk_disposition_v2_14.json",
    "../asmp3_consolidated_path_risk_disposition_v2_14/artifacts/consolidated_path_risk_disposition_verification_v2_14.json",
    "../asmp3_interactive_covering_frontier_v2_15/INTERACTIVE_COVERING_THEOREM_v2_15.md",
    "../asmp3_interactive_covering_frontier_v2_15/RELEASE_MANIFEST_v2_15.json",
    "../asmp3_interactive_covering_frontier_v2_15/artifacts/interactive_covering_frontier_v2_15.json",
    "../asmp3_interactive_covering_frontier_v2_15/artifacts/interactive_covering_frontier_verification_v2_15.json",
    "../asmp3_bounded_soundness_frontier_v2_16/BOUNDED_SOUNDNESS_THEOREM_v2_16.md",
    "../asmp3_bounded_soundness_frontier_v2_16/RELEASE_MANIFEST_v2_16.json",
    "../asmp3_bounded_soundness_frontier_v2_16/artifacts/bounded_soundness_frontier_v2_16.json",
    "../asmp3_bounded_soundness_frontier_v2_16/artifacts/bounded_soundness_frontier_verification_v2_16.json",
    ".gitignore",
    "README.md",
    "RESOURCE_SCOPE_DISPOSITION_v2_17.md",
    "REQUIREMENT_EVIDENCE_MATRIX_v2_17.md",
    "HARNESS_STOP_CERTIFICATE_v2_17.md",
    "COMPLETION_AUDIT_v2_17.md",
    "consolidated_resource_scope.py",
    "run_consolidated_resource_scope.py",
    "verify_consolidated_resource_scope.py",
    "test_consolidated_resource_scope.py",
    "build_release_manifest.py",
    "artifacts/consolidated_resource_scope_v2_17.json",
    "artifacts/consolidated_resource_scope_verification_v2_17.json",
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
        "schema_version": "asmp3_consolidated_resource_scope_release_v2_17",
        "experiment_id": "ASMP-3-CONSOLIDATED-RESOURCE-SCOPE-v2.17",
        "release_status": "interactive_resource_strengthening_and_cross_task_definition_boundary",
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
        raise RuntimeError("ASMP-3 v2.17 manifest self-check failed")
    print(f"ASMP-3 v2.17 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
