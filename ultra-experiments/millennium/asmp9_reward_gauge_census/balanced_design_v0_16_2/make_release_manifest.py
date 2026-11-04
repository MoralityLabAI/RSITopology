from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = HERE / "release_manifest_v0_16_2.json"

ARTIFACTS = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "RESOLUTION_AUDIT_v0_16.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16/PRIOR_ART_GATE_v0_16.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16/THEOREM_v0_16.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16/RUN_ABORT_v0_16.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_1/RUN_ABORT_v0_16_1.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/PROTOCOL_v0_16_2.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/PUBLIC_SUMMARY_v0_16_2.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/protocol_v0_16_2.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/registration_v0_16_2.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/run_verification.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/threshold_search.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/verify_result.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/artifacts_v0_16_2/RESULT_v0_16_2.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/artifacts_v0_16_2/progress_v0_16_2.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/artifacts_v0_16_2/receipt_v0_16_2.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/artifacts_v0_16_2/result_v0_16_2.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/artifacts_v0_16_2/start_v0_16_2.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "balanced_design_v0_16_2/artifacts_v0_16_2/verification_v0_16_2.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUTPUT}")
    missing = [
        relative for relative in ARTIFACTS if not (REPO / relative).is_file()
    ]
    if missing:
        raise FileNotFoundError(f"missing release artifacts: {missing!r}")
    manifest = {
        "protocol_id": "ASMP-9-BALANCED-MAXIMIN-DESIGN-v0.16.2",
        "implementation_commit": (
            "af94d8db0fd4164e94a116487894459a79972f35"
        ),
        "registration_commit": (
            "c139fa3363763de6ab52b8727f0ff3e4a3545654"
        ),
        "result_commit": (
            "72884b1a2ac1f5f7e15f817627d473ee8e264d90"
        ),
        "registration_sha256": (
            "14ad8dbecd19af0b679a706d18c81eaad1c7136d679aa0de65869a7dfff2c095"
        ),
        "artifact_hashes": {
            relative: sha256(REPO / relative)
            for relative in sorted(ARTIFACTS)
        },
        "clean_replay": {
            "replay_commit": (
                "72884b1a2ac1f5f7e15f817627d473ee8e264d90"
            ),
            "focused_tests_passed": 19,
            "independent_check_count": 46,
            "independent_status": "pass",
            "all_scientific_fields_equal": True,
        },
        "resource_envelope": {
            "registered_wall_seconds": 120,
            "registered_peak_resident_bytes": 1073741824,
            "observed_elapsed_seconds": 41.89900820000912,
            "observed_peak_resident_bytes": 34738176,
            "gpu_used": False,
        },
    }
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
