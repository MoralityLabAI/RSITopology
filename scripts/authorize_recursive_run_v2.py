"""Validate a Bitcoin-confirmed run pre-anchor and emit one launch authorization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.run_preparation_v2 import (
    authorize_run,
    canonical_json_bytes,
    write_once_or_equal,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--pre-payload", type=Path, required=True)
    parser.add_argument("--pre-anchor-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    payload = json.loads(args.pre_payload.read_text(encoding="utf-8"))
    anchor = json.loads(args.pre_anchor_receipt.read_text(encoding="utf-8"))
    authorization = authorize_run(
        registration=registration,
        registration_path=registration_path,
        payload=payload,
        anchor_receipt=anchor,
    )
    write_once_or_equal(args.output.resolve(), canonical_json_bytes(authorization))
    print(json.dumps(authorization, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
