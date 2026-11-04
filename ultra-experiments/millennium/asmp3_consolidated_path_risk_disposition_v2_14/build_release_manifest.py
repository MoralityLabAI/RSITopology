from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_14.json"

RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_resolution_boundary_v0_3/artifacts/expert_review_status_v0_6.json",
    "../asmp3_consolidated_resolution_disposition_v2_12/RESOLUTION_DISPOSITION_v2_12.md",
    "../asmp3_consolidated_resolution_disposition_v2_12/REQUIREMENT_EVIDENCE_MATRIX_v2_12.md",
    "../asmp3_consolidated_resolution_disposition_v2_12/STOPPING_DECISION_v2_12.md",
    "../asmp3_consolidated_resolution_disposition_v2_12/RELEASE_MANIFEST_v2_12.json",
    "../asmp3_consolidated_resolution_disposition_v2_12/artifacts/consolidated_resolution_disposition_v2_12.json",
    "../asmp3_consolidated_resolution_disposition_v2_12/artifacts/consolidated_resolution_disposition_verification_v2_12.json",
    "../asmp3_correlated_path_risk_v2_13/CORRELATED_PATH_RISK_THEOREM_v2_13.md",
    "../asmp3_correlated_path_risk_v2_13/COMPLETION_AUDIT_v2_13.md",
    "../asmp3_correlated_path_risk_v2_13/RELEASE_MANIFEST_v2_13.json",
    "../asmp3_correlated_path_risk_v2_13/artifacts/correlated_path_risk_v2_13.json",
    "../asmp3_correlated_path_risk_v2_13/artifacts/correlated_path_risk_verification_v2_13.json",
    ".gitignore",
    "README.md",
    "RESOLUTION_DISPOSITION_v2_14.md",
    "REQUIREMENT_EVIDENCE_MATRIX_v2_14.md",
    "HARNESS_STOP_CERTIFICATE_v2_14.md",
    "COMPLETION_AUDIT_v2_14.md",
    "consolidated_path_risk_disposition.py",
    "run_consolidated_path_risk_disposition.py",
    "verify_consolidated_path_risk_disposition.py",
    "test_consolidated_path_risk_disposition.py",
    "build_release_manifest.py",
    "artifacts/consolidated_path_risk_disposition_v2_14.json",
    "artifacts/consolidated_path_risk_disposition_verification_v2_14.json",
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
        "schema_version": "asmp3_consolidated_path_risk_disposition_release_v2_14",
        "experiment_id": "ASMP-3-CONSOLIDATED-PATH-RISK-DISPOSITION-v2.14",
        "release_status": "path_risk_correction_four_blocker_stop_disposition",
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
        raise RuntimeError("ASMP-3 v2.14 manifest self-check failed")
    print(f"ASMP-3 v2.14 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
