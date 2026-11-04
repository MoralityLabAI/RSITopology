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
    "ultra-experiments/millennium/asmp9_reward_gauge_census/RESOLUTION_AUDIT_v0_30.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/DEVELOPMENT_NOTE_v0_30.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/PRIOR_ART_GATE_v0_30.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/PUBLIC_SUMMARY_v0_30.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/THEOREM_DRAFT_v0_30.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/THEOREM_v0_30.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/artifacts_v0_30/RESULT_v0_30.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/artifacts_v0_30/independent_verification_v0_30.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/artifacts_v0_30/result_v0_30.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/artifacts_v0_30/run_receipt_v0_30.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/conservative_numeraire.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/environment_lock_v0_30.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/make_release_manifest_v0_30.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/protocol_v0_30.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/register_v0_30.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/registration_v0_30.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/run_verification_v0_30.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/test_conservative_numeraire.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/test_protocol_v0_30.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/conservative_numeraire_v0_30/verify_result_v0_30.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    output = HERE / "artifacts_v0_30" / "release_manifest_v0_30.json"
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
        "implementation_commit": "b510b38a28fc30c6bd7b48f2c254122220f3b1ed",
        "manifest_id": "ASMP-9-CONSERVATIVE-NUMERAIRE-v0.30-release",
        "registration_commit": "6669fcdc95d828bdf12f27d48dce77c7c8840023",
        "verdict": "conservative_numeraire_boundary_established_v0_30",
    }
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
