"""Independent exact verifier for ASMP-9 sequential risk access v0.41."""

from __future__ import annotations

import json
from pathlib import Path

from confirmation import run_confirmation
from execute_confirmation import (
    canonical_bytes,
    sha256_bytes,
    sha256_file,
    validate_registration,
)


BASE = Path(__file__).resolve().parent


def verify(registration_path: Path, result_path: Path) -> dict:
    registration = validate_registration(registration_path)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    content_hash = result["result_content_sha256"]
    unhashed = {
        key: value
        for key, value in result.items()
        if key != "result_content_sha256"
    }
    if sha256_bytes(canonical_bytes(unhashed)) != content_hash:
        raise ValueError("result content hash does not reproduce")
    if result["registration_file_sha256"] != sha256_file(registration_path):
        raise ValueError("result is not bound to this registration")
    replay = run_confirmation()
    for key in (
        "query_channels",
        "classification_cells",
        "group_cells",
        "adaptivity_gap",
    ):
        if result[key] != replay[key]:
            raise ValueError(f"exact replay mismatch in {key}")
    for gate, state in replay["gates"].items():
        if result["gates"].get(gate) != state:
            raise ValueError(f"exact replay mismatch in gate {gate}")
    if result["status"] != (
        "finite_sequential_risk_access_characterization_established"
    ):
        raise ValueError("unexpected result status")
    if not all(result["gates"].values()):
        raise ValueError("a registered gate did not pass")
    return {
        "status": "independent_exact_replay_passed",
        "registration_file_sha256": sha256_file(registration_path),
        "result_file_sha256": sha256_file(result_path),
        "result_content_sha256": content_hash,
        "sealed_files_revalidated": len(registration["sealed_files"]),
        "classification_cells_replayed": len(
            result["classification_cells"]
        ),
        "group_cells_replayed": len(result["group_cells"]),
        "all_registered_gates_pass": True,
    }


def main() -> None:
    registration = BASE / "registration_v0_41.json"
    result = BASE / "artifacts_v0_41" / "RESULT_v0_41.json"
    output = BASE / "artifacts_v0_41" / "VERIFY_v0_41.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    payload = verify(registration, result)
    output.write_bytes(canonical_bytes(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
