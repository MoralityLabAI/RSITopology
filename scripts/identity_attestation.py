#!/usr/bin/env python
"""Build immutable anchor registries and issue lineage certificates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.attestation import AnchorRegistry, anchor_from_dict


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--records", nargs="+", required=True)
    build.add_argument("--output", required=True)
    certify = sub.add_parser("certify")
    certify.add_argument("--registry", required=True)
    certify.add_argument("--site", required=True)
    certify.add_argument("--use")
    certify.add_argument("--output")
    args = parser.parse_args()

    if args.command == "build":
        records = [anchor_from_dict(json.loads(Path(path).read_text(encoding="utf-8"))) for path in args.records]
        registry = AnchorRegistry(records=records)
        file_sha = registry.write_once(args.output)
        result = {"registry_sha256": registry.sha256, "file_sha256": file_sha, "record_count": len(records)}
    else:
        registry = AnchorRegistry.load(args.registry)
        result = registry.certify(args.site, requested_use=args.use).to_dict()
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if getattr(args, "output", None) and args.command == "certify":
        target = Path(args.output)
        if target.exists() and target.read_text(encoding="utf-8") != payload:
            raise FileExistsError(f"refusing to overwrite different certificate: {target}")
        target.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
