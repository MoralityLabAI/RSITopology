from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v1_4.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_sequence_form_bridge_v1_3/SEQUENCE_FORM_THEOREM_v1_3.md",
    "../asmp3_sequence_form_bridge_v1_3/RELEASE_MANIFEST_v1_3.json",
    "../asmp3_sequence_form_bridge_v1_3/artifacts/sequence_form_bridge_v1_3.json",
    ".gitignore",
    "README.md",
    "ADAPTIVE_NOISE_THEOREM_v1_4.md",
    "COMPLETION_AUDIT_v1_4.md",
    "adaptive_noise_sequence.py",
    "run_adaptive_noise_sequence.py",
    "verify_adaptive_noise_sequence.py",
    "test_adaptive_noise_sequence.py",
    "build_release_manifest.py",
    "artifacts/adaptive_noise_sequence_v1_4.json",
    "artifacts/adaptive_noise_sequence_verification_v1_4.json",
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
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    return {
        "schema_version": "asmp3_adaptive_noise_sequence_release_v1_4",
        "experiment_id": "ASMP-3-ADAPTIVE-NOISE-SEQUENCE-v1.4",
        "release_status": "exact_joint_noise_budget_phase",
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
        raise RuntimeError("ASMP-3 v1.4 manifest self-check failed")
    print(f"ASMP-3 v1.4 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
