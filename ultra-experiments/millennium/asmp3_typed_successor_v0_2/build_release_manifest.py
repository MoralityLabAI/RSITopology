from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_DRAFT_v0_2.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_protocol_quantifier_v0_7/FROZEN_GAME_SPECIFICATION_v0_7.md",
    "../asmp3_protocol_quantifier_v0_7/PROTOCOL_QUANTIFIER_THEOREM_v0_7.md",
    "../asmp3_protocol_quantifier_v0_7/RELEASE_MANIFEST_v0_7.json",
    "../asmp3_protocol_quantifier_v0_7/artifacts/protocol_quantifier_v0_7.json",
    ".gitignore",
    "README.md",
    "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "typed_successor_v0_2.json",
    "validate_typed_successor.py",
    "test_typed_successor.py",
    "build_release_manifest.py",
    "artifacts/typed_successor_validation_v0_2.json",
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
        "schema_version": "asmp3_typed_successor_release_draft_v0_2",
        "parent_problem_id": "ASMP-3",
        "release_status": "nonnormative_typed_successor_draft",
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
        raise RuntimeError("ASMP-3 typed successor manifest self-check failed")
    print(
        "ASMP-3 typed successor draft manifest sealed: "
        f"{len(RELEASE_FILES)} files"
    )


if __name__ == "__main__":
    main()
