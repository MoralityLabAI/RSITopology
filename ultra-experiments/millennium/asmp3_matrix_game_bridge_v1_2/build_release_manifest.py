from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v1_2.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_two_role_backward_bridge_v1_1/TWO_ROLE_BACKWARD_THEOREM_v1_1.md",
    "../asmp3_two_role_backward_bridge_v1_1/RELEASE_MANIFEST_v1_1.json",
    "../asmp3_two_role_backward_bridge_v1_1/artifacts/two_role_backward_bridge_v1_1.json",
    ".gitignore",
    "README.md",
    "MATRIX_GAME_THEOREM_v1_2.md",
    "COMPLETION_AUDIT_v1_2.md",
    "matrix_game_bridge.py",
    "run_matrix_game_bridge.py",
    "verify_matrix_game_bridge.py",
    "test_matrix_game_bridge.py",
    "build_release_manifest.py",
    "artifacts/matrix_game_bridge_v1_2.json",
    "artifacts/matrix_game_bridge_verification_v1_2.json",
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
        "schema_version": "asmp3_matrix_game_bridge_release_v1_2",
        "experiment_id": "ASMP-3-MATRIX-GAME-BRIDGE-v1.2",
        "release_status": "exact_simultaneous_hidden_action_bridge",
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
        raise RuntimeError("ASMP-3 v1.2 manifest self-check failed")
    print(f"ASMP-3 v1.2 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
