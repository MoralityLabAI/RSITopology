#!/usr/bin/env python
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology import persistence_curve, rank_audit_placements, section_edits, sectioning_input_from_dict


parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--budget", required=True, type=float)
parser.add_argument("--persistence-budgets", nargs="+", type=float, required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

source = Path(args.input)
receipts = sectioning_input_from_dict(json.loads(source.read_text(encoding="utf-8")))
artifacts = {
    "patch_plan.json": section_edits(receipts, args.budget),
    "persistence.json": persistence_curve(receipts, args.persistence_budgets),
    "audit_placement.json": rank_audit_placements(receipts, args.budget),
}
output = Path(args.output)
output.mkdir(parents=True, exist_ok=True)
hashes = {}
for name, value in artifacts.items():
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
    target = output / name
    if target.exists() and target.read_bytes() != payload:
        raise FileExistsError(f"refusing to overwrite different artifact: {target}")
    target.write_bytes(payload)
    hashes[name] = sha256(payload).hexdigest()
receipt = {
    "schema_version": "1.0.0",
    "input_sha256": sha256(source.read_bytes()).hexdigest(),
    "holonomy_budget": args.budget,
    "artifacts": hashes,
}
payload = json.dumps(receipt, indent=2, sort_keys=True).encode() + b"\n"
(output / "sectioning_receipt.json").write_bytes(payload)
print(json.dumps(receipt, indent=2, sort_keys=True))

