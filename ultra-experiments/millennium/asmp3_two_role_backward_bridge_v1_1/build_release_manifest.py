from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v1_1.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_realization_flow_bridge_v1_0/REALIZATION_FLOW_THEOREM_v1_0.md",
    "../asmp3_realization_flow_bridge_v1_0/RELEASE_MANIFEST_v1_0.json",
    "../asmp3_realization_flow_bridge_v1_0/artifacts/realization_flow_bridge_v1_0.json",
    ".gitignore",
    "README.md",
    "TWO_ROLE_BACKWARD_THEOREM_v1_1.md",
    "COMPLETION_AUDIT_v1_1.md",
    "two_role_backward_bridge.py",
    "run_two_role_backward_bridge.py",
    "verify_two_role_backward_bridge.py",
    "test_two_role_backward_bridge.py",
    "build_release_manifest.py",
    "artifacts/two_role_backward_bridge_v1_1.json",
    "artifacts/two_role_backward_bridge_verification_v1_1.json",
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
        files[relative] = {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    return {
        "schema_version": "asmp3_two_role_backward_bridge_release_v1_1",
        "experiment_id": "ASMP-3-TWO-ROLE-BACKWARD-BRIDGE-v1.1",
        "release_status": "exact_perfect_information_two_role_bridge",
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
        raise RuntimeError("ASMP-3 v1.1 manifest self-check failed")
    print(f"ASMP-3 v1.1 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
