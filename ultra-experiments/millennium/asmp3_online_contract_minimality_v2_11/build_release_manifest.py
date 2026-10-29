from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_11.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_honest_search_barrier_v2_1/HONEST_SEARCH_BARRIER_THEOREM_v2_1.md",
    "../asmp3_honest_search_barrier_v2_1/RELEASE_MANIFEST_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_v2_1.json",
    "../asmp3_witness_transparent_normal_form_v2_5/WITNESS_TRANSPARENT_NORMAL_FORM_THEOREM_v2_5.md",
    "../asmp3_witness_transparent_normal_form_v2_5/artifacts/witness_transparent_normal_form_v2_5.json",
    "../asmp3_trace_binding_extractor_v2_8/TRACE_BINDING_EXTRACTOR_THEOREM_v2_8.md",
    "../asmp3_trace_binding_extractor_v2_8/RELEASE_MANIFEST_v2_8.json",
    "../asmp3_trace_binding_extractor_v2_8/artifacts/trace_binding_extractor_v2_8.json",
    "../asmp3_trace_binding_extractor_v2_8/artifacts/trace_binding_extractor_verification_v2_8.json",
    "../asmp3_online_noisy_trace_extractor_v2_10/ONLINE_NOISY_TRACE_EXTRACTOR_THEOREM_v2_10.md",
    "../asmp3_online_noisy_trace_extractor_v2_10/RELEASE_MANIFEST_v2_10.json",
    "../asmp3_online_noisy_trace_extractor_v2_10/artifacts/online_noisy_trace_extractor_v2_10.json",
    "../asmp3_online_noisy_trace_extractor_v2_10/artifacts/online_noisy_trace_extractor_verification_v2_10.json",
    ".gitignore",
    "README.md",
    "ONLINE_CONTRACT_MINIMALITY_THEOREM_v2_11.md",
    "STOPPING_BOUNDARY_v2_11.md",
    "COMPLETION_AUDIT_v2_11.md",
    "online_contract_minimality.py",
    "run_online_contract_minimality.py",
    "verify_online_contract_minimality.py",
    "test_online_contract_minimality.py",
    "build_release_manifest.py",
    "artifacts/online_contract_minimality_v2_11.json",
    "artifacts/online_contract_minimality_verification_v2_11.json",
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
        "schema_version": "asmp3_online_contract_minimality_release_v2_11",
        "experiment_id": "ASMP-3-ONLINE-CONTRACT-MINIMALITY-v2.11",
        "release_status": "black_box_las_vegas_online_contract_minimality",
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
        raise RuntimeError("ASMP-3 v2.11 manifest self-check failed")
    print(f"ASMP-3 v2.11 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
