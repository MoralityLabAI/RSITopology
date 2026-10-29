from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "RELEASE_MANIFEST_v0_3.json"
RELEASE_FILES = (
    "../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "../problem_set_v0_1.json",
    "../asmp3_typed_successor_v0_2/ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "../asmp3_typed_successor_v0_2/typed_successor_v0_2.json",
    "../asmp3_standard_encoding_transfer_v2_21/STANDARD_ENCODING_AND_QUANTIFIER_TRANSFER_THEOREM_v2_21.md",
    "../asmp3_standard_encoding_transfer_v2_21/artifacts/standard_encoding_transfer_v2_21.json",
    "../asmp3_standard_encoding_transfer_v2_21/artifacts/standard_encoding_transfer_verification_v2_21.json",
    "../asmp3_standard_encoding_transfer_v2_21/RELEASE_MANIFEST_v2_21.json",
    ".gitignore",
    "README.md",
    "ASMP3_MACHINE_GRAMMAR_SPEC_v0_3.md",
    "BUILTIN_SEMANTICS_v0_3.md",
    "ASMP3_MACHINE_GRAMMAR_REPORT_v0_3.md",
    "RESOLUTION_EFFECT_v0_3.md",
    "ADOPTION_CHECKLIST_v0_3.md",
    "COMPLETION_AUDIT_v0_3.md",
    "asmp3_machine_grammar_v0_3.json",
    "machine_grammar.py",
    "run_machine_grammar.py",
    "verify_machine_grammar.py",
    "test_machine_grammar.py",
    "build_release_manifest.py",
    "artifacts/machine_grammar_v0_3.json",
    "artifacts/machine_grammar_verification_v0_3.json",
    "artifacts/v2_21_e17_FIX.machine.json",
    "artifacts/v2_21_e17_ADM.machine.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def build_manifest() -> dict[str, object]:
    files: dict[str, object] = {}
    for relative in RELEASE_FILES:
        path = HERE / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        files[relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return {
        "schema_version": "asmp3_machine_grammar_release_v0_3",
        "experiment_id": "ASMP-3-MACHINE-GRAMMAR-v0.3",
        "release_status": "executable_successor_grammar_v2_21_reduction_compiles_adoption_and_external_review_open",
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
    return MANIFEST_PATH.is_file() and json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) == build_manifest()


def main() -> None:
    write_manifest()
    if not verify_manifest():
        raise RuntimeError("ASMP-3 machine grammar release manifest verification failed")
    print(f"ASMP-3 machine grammar release sealed: {len(RELEASE_FILES)} files")


if __name__ == "__main__":
    main()
