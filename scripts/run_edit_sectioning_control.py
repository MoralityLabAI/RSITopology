#!/usr/bin/env python
from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.sectioning_synthetic import build_sectioning_fixture, run_frozen_sectioning_gates


parser = argparse.ArgumentParser()
parser.add_argument("--protocol", default="protocols/edit_sectioning_synthetic_v0_2.json")
parser.add_argument("--output", required=True)
args = parser.parse_args()
protocol_path = Path(args.protocol)
protocol_bytes = protocol_path.read_bytes()
protocol = json.loads(protocol_bytes)
result = run_frozen_sectioning_gates()
result["protocol_id"] = protocol["protocol_id"]
result["protocol_sha256"] = sha256(protocol_bytes).hexdigest()
result["canonical_run_after_protocol_freeze"] = True
output = Path(args.output)
output.mkdir(parents=True, exist_ok=True)
artifacts = {
    "edit_sectioning_control.json": result,
    "mixed_curvature_input.json": asdict(build_sectioning_fixture("mixed_curvature")),
    "uniformly_curved_input.json": asdict(build_sectioning_fixture("uniformly_curved")),
    "audit_incomplete_input.json": asdict(build_sectioning_fixture("audit_incomplete")),
}
hashes = {}
for name, value in artifacts.items():
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
    target = output / name
    if target.exists() and target.read_bytes() != payload:
        raise FileExistsError(f"refusing to overwrite different artifact: {target}")
    target.write_bytes(payload)
    hashes[name] = sha256(payload).hexdigest()
manifest = {
    "protocol_sha256": result["protocol_sha256"],
    "all_gates_pass": result["all_gates_pass"],
    "artifacts": hashes,
}
payload = json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
(output / "manifest.json").write_bytes(payload)
print(json.dumps(manifest, indent=2, sort_keys=True))
