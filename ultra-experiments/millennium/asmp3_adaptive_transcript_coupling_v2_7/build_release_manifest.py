from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_7.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_block_selection_composition_v1_9/BLOCK_SELECTION_COMPOSITION_THEOREM_v1_9.md",
    "../asmp3_block_selection_composition_v1_9/RELEASE_MANIFEST_v1_9.json",
    "../asmp3_block_selection_composition_v1_9/artifacts/block_selection_composition_v1_9.json",
    "../asmp3_witness_transparent_normal_form_v2_5/WITNESS_TRANSPARENT_NORMAL_FORM_THEOREM_v2_5.md",
    "../asmp3_witness_transparent_normal_form_v2_5/RELEASE_MANIFEST_v2_5.json",
    "../asmp3_witness_transparent_normal_form_v2_5/artifacts/witness_transparent_normal_form_v2_5.json",
    "../asmp3_resolution_disposition_v2_6/STOPPING_BOUNDARY_v2_6.md",
    "../asmp3_resolution_disposition_v2_6/RELEASE_MANIFEST_v2_6.json",
    "../asmp3_resolution_disposition_v2_6/artifacts/resolution_disposition_v2_6.json",
    ".gitignore",
    "README.md",
    "ADAPTIVE_TRANSCRIPT_COUPLING_THEOREM_v2_7.md",
    "COMPLETION_AUDIT_v2_7.md",
    "adaptive_transcript_coupling.py",
    "run_adaptive_transcript_coupling.py",
    "verify_adaptive_transcript_coupling.py",
    "test_adaptive_transcript_coupling.py",
    "build_release_manifest.py",
    "artifacts/adaptive_transcript_coupling_v2_7.json",
    "artifacts/adaptive_transcript_coupling_verification_v2_7.json",
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
        "schema_version": "asmp3_adaptive_transcript_coupling_release_v2_7",
        "experiment_id": "ASMP-3-ADAPTIVE-TRANSCRIPT-COUPLING-v2.7",
        "release_status": "pathwise_adaptive_protocol_coupling_and_robustification_theorem",
        "deterministic": True,
        "file_count": len(files),
        "files": files,
    }


def write_manifest() -> None:
    MANIFEST_PATH.write_text(json.dumps(build_manifest(),indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")


def verify_manifest() -> bool:
    return MANIFEST_PATH.is_file() and json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))==build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest(): raise RuntimeError("ASMP-3 v2.7 manifest self-check failed")
    print(f"ASMP-3 v2.7 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__=="__main__": main()
