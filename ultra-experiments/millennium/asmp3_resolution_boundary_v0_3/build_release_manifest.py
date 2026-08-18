from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v0_3.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "README.md",
    "INTERFACE_DICHOTOMY_THEOREM_v0_3.md",
    "NEGATIVE_RESOLUTION_CANDIDATE_v0_3.md",
    "RESOLUTION_OBLIGATION_MATRIX_v0_3.md",
    "COMPLETION_AUDIT_v0_3.md",
    "BLOCKED_AUDIT_v0_6.md",
    "PRIOR_ART_v0_3.md",
    "EXPERT_REVIEW_PACKET_v0_3.md",
    "REVIEWER_HANDOFF_v0_5.md",
    "SIMULATED_ULTRA_REVIEW_SYNTHESIS_v0_6.md",
    "simulated_reviews/COMPLEXITY_GAME_ULTRA_v0_6.md",
    "simulated_reviews/PROBABILITY_NOISE_ULTRA_v0_6.md",
    "expert_review.schema.json",
    "external_review_checklist_v0_6.json",
    "reviews/README.md",
    "reviews/checkers/README.md",
    "build_release_manifest.py",
    "verify_expert_reviews.py",
    "resolution_harness.py",
    "run_harness.py",
    "verify_result.py",
    "verify_fourier_certificate.py",
    "test_resolution_harness.py",
    "artifacts/result_v0_3.json",
    "artifacts/verification_v0_3.json",
    "artifacts/fourier_verification_v0_3.json",
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
        files[relative] = {
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }
    return {
        "schema_version": "asmp3_resolution_boundary_release_v0_3",
        "experiment_id": "ASMP-3-REFUTE-INTERFACE-DICHOTOMY-v0.3",
        "release_status": "conditional_obstruction_major_revision",
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
    recorded = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return recorded == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 release manifest self-check failed")
    print(f"ASMP-3 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
