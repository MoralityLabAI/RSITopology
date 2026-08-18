from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ORIGINAL_REGISTRATION = HERE / "registration_v0_31.json"
REPAIR_REGISTRATION = HERE / "repair_v0_31_1" / "registration_v0_31_1.json"

PUBLICATION_FILES = (
    "ILIAD_FELLOWSHIP_RESEARCH_LINKS_20260729.md",
    "ultra-experiments/millennium/V0_2_EXPERIMENT_PROGRESS_v0_1.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/RESOLUTION_AUDIT_v0_31.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/PUBLIC_SUMMARY_v0_31.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/THEOREM_v0_31.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/artifacts_v0_31_1/RESULT_v0_31.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/artifacts_v0_31_1/independent_verification_v0_31.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/artifacts_v0_31_1/repair_verification_v0_31_1.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/artifacts_v0_31_1/result_v0_31.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/artifacts_v0_31_1/run_receipt_v0_31.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/failure_receipt_v0_31.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/make_release_manifest_v0_31.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/registration_v0_31.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/joint_approximate_v0_31/repair_v0_31_1/registration_v0_31_1.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def main() -> None:
    output = HERE / "artifacts_v0_31_1" / "release_manifest_v0_31.json"
    if output.exists():
        raise FileExistsError(output)

    original_registration = json.loads(
        ORIGINAL_REGISTRATION.read_text(encoding="utf-8")
    )
    repair_registration = json.loads(
        REPAIR_REGISTRATION.read_text(encoding="utf-8")
    )

    paths = set(PUBLICATION_FILES)
    paths.update(original_registration["sealed_files"])
    paths.update(repair_registration["sealed_files"])

    artifacts: dict[str, str] = {}
    for item in sorted(paths):
        path = REPO / item
        if not path.is_file():
            raise FileNotFoundError(path)
        artifacts[item] = sha256(path)

    manifest = {
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "manifest_id": "ASMP-9-JOINT-APPROXIMATE-v0.31-release",
        "original_attempt": {
            "implementation_commit": (
                "896904058fd80a0343f2c0ef4ee736f0edd2738c"
            ),
            "registration_commit": (
                "7af9a09a9db9677aea542aea5e1e4d6f015a5611"
            ),
            "registration_sha256": sha256(ORIGINAL_REGISTRATION),
            "status": "unavailable_resource_meter_failure_before_output",
        },
        "repair_execution": {
            "implementation_commit": (
                "c50659e9c21b9c34783d2f89ec7757a4aef94f97"
            ),
            "registration_commit": (
                "50593abf361afcf867f753b2039261a01434725c"
            ),
            "registration_sha256": sha256(REPAIR_REGISTRATION),
            "result_sha256": artifacts[
                "ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/joint_approximate_v0_31/"
                "artifacts_v0_31_1/result_v0_31.json"
            ],
        },
        "verdict": "joint_approximate_boundary_established_v0_31",
    }
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
