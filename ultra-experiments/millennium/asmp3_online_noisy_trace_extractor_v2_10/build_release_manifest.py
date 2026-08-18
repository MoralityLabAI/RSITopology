from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_10.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_honest_search_barrier_v2_1/HONEST_SEARCH_BARRIER_THEOREM_v2_1.md",
    "../asmp3_honest_search_barrier_v2_1/RELEASE_MANIFEST_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_v2_1.json",
    "../asmp3_witness_transparent_normal_form_v2_5/WITNESS_TRANSPARENT_NORMAL_FORM_THEOREM_v2_5.md",
    "../asmp3_witness_transparent_normal_form_v2_5/artifacts/witness_transparent_normal_form_v2_5.json",
    "../asmp3_adaptive_transcript_coupling_v2_7/ADAPTIVE_TRANSCRIPT_COUPLING_THEOREM_v2_7.md",
    "../asmp3_adaptive_transcript_coupling_v2_7/RELEASE_MANIFEST_v2_7.json",
    "../asmp3_adaptive_transcript_coupling_v2_7/artifacts/adaptive_transcript_coupling_v2_7.json",
    "../asmp3_trace_binding_extractor_v2_8/TRACE_BINDING_EXTRACTOR_THEOREM_v2_8.md",
    "../asmp3_trace_binding_extractor_v2_8/RELEASE_MANIFEST_v2_8.json",
    "../asmp3_trace_binding_extractor_v2_8/artifacts/trace_binding_extractor_v2_8.json",
    "../asmp3_trace_binding_extractor_v2_8/artifacts/trace_binding_extractor_verification_v2_8.json",
    "../asmp3_oracle_parametric_replay_v2_9/ORACLE_PARAMETRIC_REPLAY_THEOREM_v2_9.md",
    "../asmp3_oracle_parametric_replay_v2_9/RELEASE_MANIFEST_v2_9.json",
    "../asmp3_oracle_parametric_replay_v2_9/artifacts/oracle_parametric_replay_v2_9.json",
    "../asmp3_oracle_parametric_replay_v2_9/artifacts/oracle_parametric_replay_verification_v2_9.json",
    ".gitignore",
    "README.md",
    "ONLINE_NOISY_TRACE_EXTRACTOR_THEOREM_v2_10.md",
    "COMPLETION_AUDIT_v2_10.md",
    "online_noisy_trace_extractor.py",
    "run_online_noisy_trace_extractor.py",
    "verify_online_noisy_trace_extractor.py",
    "test_online_noisy_trace_extractor.py",
    "build_release_manifest.py",
    "artifacts/online_noisy_trace_extractor_v2_10.json",
    "artifacts/online_noisy_trace_extractor_verification_v2_10.json",
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
        "schema_version": "asmp3_online_noisy_trace_extractor_release_v2_10",
        "experiment_id": "ASMP-3-ONLINE-NOISY-TRACE-EXTRACTOR-v2.10",
        "release_status": "one_shot_online_noisy_trace_finder_without_restart",
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
        raise RuntimeError("ASMP-3 v2.10 manifest self-check failed")
    print(f"ASMP-3 v2.10 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
