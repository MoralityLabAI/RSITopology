"""Generate or verify the frozen fresh-context Stage-B prompt split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal
from rsi_topology.qwen_context_stageb import (
    generate_manifest,
    separation_receipt,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = ROOT / "protocols" / "qwen08_context_stageb_v0_1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def generate(args: argparse.Namespace) -> None:
    value = generate_manifest(protocol_path=args.protocol)
    prior = [_load(path) for path in args.separation_artifact]
    validate_manifest(
        value, protocol_path=args.protocol, separation_artifacts=prior
    )
    receipt = separation_receipt(value, compared_paths=args.separation_artifact)
    if not receipt["passed"]:
        raise ValueError("Stage-B prompt separation failed")
    write_once_or_equal(args.output, canonical_json_bytes(value))
    receipt.update(
        {
            "manifest_path": str(args.output.resolve()),
            "manifest_sha256": sha256_file(args.output),
            "scientific_protocol_sha256": sha256_file(args.protocol),
        }
    )
    write_once_or_equal(args.receipt, canonical_json_bytes(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))


def verify(args: argparse.Namespace) -> None:
    value = _load(args.manifest)
    prior = [_load(path) for path in args.separation_artifact]
    validate_manifest(
        value, protocol_path=args.protocol, separation_artifacts=prior
    )
    receipt = separation_receipt(value, compared_paths=args.separation_artifact)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if not receipt["passed"]:
        raise SystemExit(1)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    value.add_argument(
        "--separation-artifact", type=Path, action="append", required=True
    )
    sub = value.add_subparsers(dest="command", required=True)
    generate_parser = sub.add_parser("generate")
    generate_parser.add_argument("--output", type=Path, required=True)
    generate_parser.add_argument("--receipt", type=Path, required=True)
    generate_parser.set_defaults(function=generate)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.set_defaults(function=verify)
    return value


if __name__ == "__main__":
    args = parser().parse_args()
    args.function(args)

