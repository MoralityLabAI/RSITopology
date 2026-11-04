import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from adaptive_reuse import canonical_json, compile_result, load_protocol, validate_protocol


HERE = Path(__file__).resolve().parent
SOURCE_FILES = (
    "adaptive_reuse.py",
    "protocol_v0_6.json",
    "PROTOCOL_v0_6.md",
    "README.md",
    "run.py",
    "verify_independent.py",
    "test_adaptive_reuse.py",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(canonical_json(value), encoding="utf-8", newline="\n")


def main() -> None:
    protocol = load_protocol(HERE / "protocol_v0_6.json")
    protocol_binding = validate_protocol(protocol)
    output_dir = HERE / "artifacts_v0_6"
    output = output_dir / "result_v0_6.json"
    receipt_path = output_dir / "run_receipt_v0_6.json"
    output_dir.mkdir(exist_ok=True)
    write_json(output, compile_result(protocol))
    receipt = {
        "schema_version": "asmp8_adaptive_reuse_run_receipt_v0_6_1",
        "protocol_id": protocol["protocol_id"],
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": sha256_file(HERE / "protocol_v0_6.json"),
        "result_sha256": sha256_file(output),
        "source_hashes": {name: sha256_file(HERE / name) for name in SOURCE_FILES},
        "protocol_binding": protocol_binding,
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "arithmetic": "fractions.Fraction",
            "gpu": "not used",
        },
    }
    write_json(receipt_path, receipt)
    print(json.dumps({"result": str(output), "receipt": str(receipt_path)}, indent=2))


if __name__ == "__main__":
    main()
