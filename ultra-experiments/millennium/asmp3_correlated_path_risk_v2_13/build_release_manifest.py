from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_13.json"

RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_independent_noise_amplification_v1_8/INDEPENDENT_NOISE_AMPLIFICATION_THEOREM_v1_8.md",
    "../asmp3_independent_noise_amplification_v1_8/RELEASE_MANIFEST_v1_8.json",
    "../asmp3_independent_noise_amplification_v1_8/artifacts/independent_noise_amplification_v1_8.json",
    "../asmp3_independent_noise_amplification_v1_8/artifacts/independent_noise_amplification_verification_v1_8.json",
    "../asmp3_online_noisy_trace_extractor_v2_10/ONLINE_NOISY_TRACE_EXTRACTOR_THEOREM_v2_10.md",
    "../asmp3_online_noisy_trace_extractor_v2_10/RELEASE_MANIFEST_v2_10.json",
    "../asmp3_online_noisy_trace_extractor_v2_10/artifacts/online_noisy_trace_extractor_v2_10.json",
    "../asmp3_online_noisy_trace_extractor_v2_10/artifacts/online_noisy_trace_extractor_verification_v2_10.json",
    "../asmp3_consolidated_resolution_disposition_v2_12/RESOLUTION_DISPOSITION_v2_12.md",
    "../asmp3_consolidated_resolution_disposition_v2_12/RELEASE_MANIFEST_v2_12.json",
    ".gitignore",
    "README.md",
    "CORRELATED_PATH_RISK_THEOREM_v2_13.md",
    "COMPLETION_AUDIT_v2_13.md",
    "correlated_path_risk.py",
    "run_correlated_path_risk.py",
    "verify_correlated_path_risk.py",
    "test_correlated_path_risk.py",
    "build_release_manifest.py",
    "artifacts/correlated_path_risk_v2_13.json",
    "artifacts/correlated_path_risk_verification_v2_13.json",
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
        "schema_version": "asmp3_correlated_path_risk_release_v2_13",
        "experiment_id": "ASMP-3-CORRELATED-PATH-RISK-v2.13",
        "release_status": "controlled_selected_path_risk_resolves_correlated_noise_block",
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
        raise RuntimeError("ASMP-3 v2.13 manifest self-check failed")
    print(f"ASMP-3 v2.13 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
