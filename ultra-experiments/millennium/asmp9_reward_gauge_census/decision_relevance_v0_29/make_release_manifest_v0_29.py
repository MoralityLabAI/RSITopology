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
    "ultra-experiments/millennium/asmp9_reward_gauge_census/RESOLUTION_AUDIT_v0_29.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/DEVELOPMENT_NOTE_v0_29.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/PRIOR_ART_GATE_v0_29.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/PUBLIC_SUMMARY_v0_29.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/THEOREM_DRAFT_v0_29.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/THEOREM_v0_29.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/artifacts_v0_29/RESULT_v0_29.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/artifacts_v0_29/independent_verification_v0_29.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/artifacts_v0_29/result_v0_29.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/artifacts_v0_29/run_receipt_v0_29.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/decision_relevance.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/environment_lock_v0_29.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/make_release_manifest_v0_29.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/protocol_v0_29.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/register_v0_29.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/registration_v0_29.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/run_verification_v0_29.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/test_decision_relevance.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/test_protocol_v0_29.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29/verify_result_v0_29.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    output = HERE / "artifacts_v0_29" / "release_manifest_v0_29.json"
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
        "implementation_commit": "c54dde192b432b32feb41625a2db16f073e392b7",
        "manifest_id": "ASMP-9-DECISION-RELEVANCE-v0.29-release",
        "registration_commit": "283c3420d940dcd1f8cf39df75a664d51555ce2c",
        "verdict": "decision_relevance_boundary_established_v0_29",
    }
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
