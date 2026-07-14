"""Emit a v2 release manifest only after both OTS anchors validate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.anchor_guard_v2 import release_anchor_guard


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--pre-payload", type=Path, required=True)
    parser.add_argument("--pre-anchor-receipt", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--post-anchor-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    root = args.root.resolve()
    payload = json.loads(args.pre_payload.read_text(encoding="utf-8"))
    pre_anchor = json.loads(args.pre_anchor_receipt.read_text(encoding="utf-8"))
    post_anchor = json.loads(args.post_anchor_receipt.read_text(encoding="utf-8"))
    pre_files = {
        name: root / name for name in payload["file_sha256"]
    }
    guard = release_anchor_guard(
        pre_payload=payload,
        pre_anchor_receipt=pre_anchor,
        pre_files=pre_files,
        run_receipt_path=args.run_receipt.resolve(),
        post_anchor_receipt=post_anchor,
    )
    manifest = {
        "schema_version": "proposal_recursive_v2_0_3_release_manifest_v1",
        **guard,
        "run_receipt": str(args.run_receipt.resolve()),
        "release_emitted_only_after_post_submission": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": manifest["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
