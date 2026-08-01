from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v1_7.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_weighted_noise_subset_sum_v1_6/WEIGHTED_NOISE_SUBSET_SUM_THEOREM_v1_6.md",
    "../asmp3_weighted_noise_subset_sum_v1_6/RELEASE_MANIFEST_v1_6.json",
    "../asmp3_weighted_noise_subset_sum_v1_6/artifacts/weighted_noise_subset_sum_v1_6.json",
    ".gitignore",
    "README.md",
    "EXPECTED_WEIGHTED_NOISE_THEOREM_v1_7.md",
    "COMPLETION_AUDIT_v1_7.md",
    "expected_weighted_noise.py",
    "run_expected_weighted_noise.py",
    "verify_expected_weighted_noise.py",
    "test_expected_weighted_noise.py",
    "build_release_manifest.py",
    "artifacts/expected_weighted_noise_v1_7.json",
    "artifacts/expected_weighted_noise_verification_v1_7.json",
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
        "schema_version": "asmp3_expected_weighted_noise_release_v1_7",
        "experiment_id": "ASMP-3-EXPECTED-WEIGHTED-NOISE-v1.7",
        "release_status": "exact_expected_budget_tv_phase",
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
        raise RuntimeError("ASMP-3 v1.7 manifest self-check failed")
    print(f"ASMP-3 v1.7 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
