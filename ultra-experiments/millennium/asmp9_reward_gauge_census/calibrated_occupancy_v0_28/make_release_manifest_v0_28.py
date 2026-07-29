from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RELATIVE_FILES = (
    "ILIAD_FELLOWSHIP_RESEARCH_LINKS_20260729.md",
    "ultra-experiments/millennium/V0_2_EXPERIMENT_PROGRESS_v0_1.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/RESOLUTION_AUDIT_v0_28.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/DEVELOPMENT_NOTE_v0_28.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/PRIOR_ART_GATE_v0_28.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/PUBLIC_SUMMARY_v0_28.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/THEOREM_DRAFT_v0_28.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/THEOREM_v0_28.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/artifacts_v0_28/RESULT_v0_28.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/artifacts_v0_28/independent_verification_v0_28.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/artifacts_v0_28/result_v0_28.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/artifacts_v0_28/run_receipt_v0_28.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/environment_lock_v0_28.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/linear_access.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/make_release_manifest_v0_28.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/protocol_v0_28.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/register_v0_28.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/registration_v0_28.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/run_verification_v0_28.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/test_linear_access.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/test_protocol_v0_28.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/verify_result_v0_28.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    output = HERE / "artifacts_v0_28" / "release_manifest_v0_28.json"
    if output.exists():
        raise FileExistsError(output)
    artifacts = {}
    for relative in RELATIVE_FILES:
        path = REPO / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        artifacts[relative] = sha256(path)
    manifest = {
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "implementation_commit": "fcab52dd08ff88f382d3a33d585bd439bfa3c99d",
        "manifest_id": "ASMP-9-CALIBRATED-OCCUPANCY-v0.28-release",
        "registration_commit": "9fdeaca64da1e59c13ca24e00f54bf2fe0022eeb",
        "verdict": "calibrated_occupancy_boundary_established_v0_28",
    }
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
