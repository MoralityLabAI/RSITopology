from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRATION = HERE / "registration_v0_32.json"

PUBLICATION_FILES = (
    "ILIAD_FELLOWSHIP_RESEARCH_LINKS_20260729.md",
    "ultra-experiments/millennium/V0_2_EXPERIMENT_PROGRESS_v0_1.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/RESOLUTION_AUDIT_v0_32.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/PUBLIC_SUMMARY_v0_32.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/THEOREM_v0_32.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/artifacts_v0_32/RESULT_v0_32.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/artifacts_v0_32/independent_verification_v0_32.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/artifacts_v0_32/result_v0_32.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/artifacts_v0_32/run_receipt_v0_32.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/make_release_manifest_v0_32.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/registration_v0_32.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/verify_release_manifest_v0_32.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    output = HERE / "artifacts_v0_32" / "release_manifest_v0_32.json"
    if output.exists():
        raise FileExistsError(output)

    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    paths = set(PUBLICATION_FILES)
    paths.update(registration["sealed_files"])

    artifacts: dict[str, str] = {}
    for item in sorted(paths):
        path = REPO / item
        if not path.is_file():
            raise FileNotFoundError(path)
        artifacts[item] = sha256(path)

    result_path = (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "behavioral_rectangle_v0_32/artifacts_v0_32/result_v0_32.json"
    )
    receipt_path = (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "behavioral_rectangle_v0_32/artifacts_v0_32/run_receipt_v0_32.json"
    )
    independent_path = (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "behavioral_rectangle_v0_32/artifacts_v0_32/"
        "independent_verification_v0_32.json"
    )

    manifest = {
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "execution": {
            "implementation_commit": registration["implementation_commit"],
            "registration_commit": (
                "f2fb9565996ae604aa1b3ba90fd7d4073aa1d835"
            ),
            "registration_sha256": sha256(REGISTRATION),
            "result_sha256": artifacts[result_path],
            "run_receipt_sha256": artifacts[receipt_path],
            "independent_verification_sha256": artifacts[independent_path],
        },
        "manifest_id": "ASMP-9-BEHAVIORAL-RECTANGLE-v0.32-release",
        "verdict": "behavioral_rectangle_boundary_established_v0_32",
    }
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
