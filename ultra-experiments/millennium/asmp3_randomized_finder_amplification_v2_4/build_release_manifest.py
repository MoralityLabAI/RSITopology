from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_4.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_honest_search_barrier_v2_1/HONEST_SEARCH_BARRIER_THEOREM_v2_1.md",
    "../asmp3_honest_search_barrier_v2_1/RELEASE_MANIFEST_v2_1.json",
    "../asmp3_honest_search_barrier_v2_1/artifacts/honest_search_barrier_v2_1.json",
    "../asmp3_constructive_refutation_protocol_v2_3/CONSTRUCTIVE_REFUTATION_PROTOCOL_THEOREM_v2_3.md",
    "../asmp3_constructive_refutation_protocol_v2_3/RELEASE_MANIFEST_v2_3.json",
    "../asmp3_constructive_refutation_protocol_v2_3/artifacts/constructive_refutation_protocol_v2_3.json",
    ".gitignore",
    "README.md",
    "RANDOMIZED_FINDER_AMPLIFICATION_THEOREM_v2_4.md",
    "COMPLETION_AUDIT_v2_4.md",
    "randomized_finder_amplification.py",
    "run_randomized_finder_amplification.py",
    "verify_randomized_finder_amplification.py",
    "test_randomized_finder_amplification.py",
    "build_release_manifest.py",
    "artifacts/randomized_finder_amplification_v2_4.json",
    "artifacts/randomized_finder_amplification_verification_v2_4.json",
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
        "schema_version": "asmp3_randomized_finder_amplification_release_v2_4",
        "experiment_id": "ASMP-3-RANDOMIZED-FINDER-AMPLIFICATION-v2.4",
        "release_status": "exact_randomized_finder_restart_noise_and_budget_frontier",
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
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 v2.4 manifest self-check failed")
    print(f"ASMP-3 v2.4 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
