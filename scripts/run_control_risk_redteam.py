#!/usr/bin/env python
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.risk_redteam import run_control_risk_redteam


parser = argparse.ArgumentParser()
parser.add_argument("--protocol", default="protocols/control_risk_redteam_v0_1.json")
parser.add_argument("--output", required=True)
args = parser.parse_args()
protocol = Path(args.protocol)
result = run_control_risk_redteam()
result["protocol_sha256"] = sha256(protocol.read_bytes()).hexdigest()
payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
target = Path(args.output)
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists() and target.read_bytes() != payload:
    raise FileExistsError(f"refusing to overwrite different canonical receipt: {target}")
target.write_bytes(payload)
print(json.dumps({
    "output": str(target),
    "sha256": sha256(payload).hexdigest(),
    "all_gates_pass": result["all_gates_pass"],
    "metrics": result["metrics"],
}, indent=2, sort_keys=True))

