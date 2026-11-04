"""Run the frozen v0.68 analyzer, then add the preregistered v0.82 gates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
V068 = HERE.parent / "context_quotient_response_v0_68"


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


old_analyzer = _module("asmp9_analyze_v068_for_v082", V068 / "analyze_v068.py")
gate = _module("asmp9_transport_gate_v082", HERE / "transport_gate.py")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    previous = list(sys.argv)
    try:
        sys.argv = [
            str(V068 / "analyze_v068.py"),
            "--registration",
            str(args.registration.resolve()),
            "--result-dir",
            str(args.result_dir.resolve()),
            "--output-dir",
            str(args.output_dir.resolve()),
        ]
        old_analyzer.main()
    finally:
        sys.argv = previous

    registration = _load(args.registration.resolve())
    protocol_path = Path(registration["protocol"]["path"])
    protocol = _load(protocol_path)
    base_analysis_path = args.output_dir.resolve() / "analysis.json"
    transport = gate.evaluate_transport(_load(base_analysis_path), protocol)
    transport_path = args.output_dir.resolve() / "transport_analysis_v0_82.json"
    _write_once(transport_path, _canonical(transport))
    receipt = {
        "schema_version": "asmp9_out_of_family_transport_analysis_receipt_v0_82",
        "registration_sha256": _sha256(args.registration.resolve()),
        "protocol_sha256": _sha256(protocol_path),
        "base_analysis_sha256": _sha256(base_analysis_path),
        "transport_analysis_sha256": _sha256(transport_path),
        "provisional_scientific_decision": transport[
            "provisional_scientific_decision"
        ],
        "R0": "pending_wrapper_cleanup",
        "claim_boundary": protocol["claim_boundary"],
    }
    _write_once(
        args.output_dir.resolve() / "transport_receipt_v0_82.json",
        _canonical(receipt),
    )


if __name__ == "__main__":
    main()

