from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v2_5.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_protocol_quantifier_v0_7/PROTOCOL_QUANTIFIER_THEOREM_v0_7.md",
    "../asmp3_protocol_quantifier_v0_7/RELEASE_MANIFEST_v0_7.json",
    "../asmp3_protocol_quantifier_v0_7/artifacts/protocol_quantifier_v0_7.json",
    "../asmp3_encoding_invariance_v2_0/ENCODING_INVARIANCE_THEOREM_v2_0.md",
    "../asmp3_encoding_invariance_v2_0/RELEASE_MANIFEST_v2_0.json",
    "../asmp3_encoding_invariance_v2_0/artifacts/encoding_invariance_v2_0.json",
    "../asmp3_randomized_finder_amplification_v2_4/RANDOMIZED_FINDER_AMPLIFICATION_THEOREM_v2_4.md",
    "../asmp3_randomized_finder_amplification_v2_4/RELEASE_MANIFEST_v2_4.json",
    "../asmp3_randomized_finder_amplification_v2_4/artifacts/randomized_finder_amplification_v2_4.json",
    ".gitignore",
    "README.md",
    "WITNESS_TRANSPARENT_NORMAL_FORM_THEOREM_v2_5.md",
    "COMPLETION_AUDIT_v2_5.md",
    "witness_transparent_normal_form.py",
    "run_witness_transparent_normal_form.py",
    "verify_witness_transparent_normal_form.py",
    "test_witness_transparent_normal_form.py",
    "build_release_manifest.py",
    "artifacts/witness_transparent_normal_form_v2_5.json",
    "artifacts/witness_transparent_normal_form_verification_v2_5.json",
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
        files[relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return {
        "schema_version": "asmp3_witness_transparent_normal_form_release_v2_5",
        "experiment_id": "ASMP-3-WITNESS-TRANSPARENT-NORMAL-FORM-v2.5",
        "release_status": (
            "conditional_protocol_to_finder_normal_form_and_literal_two_sided_separation"
        ),
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
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 v2.5 manifest self-check failed")
    print(f"ASMP-3 v2.5 release manifest sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
