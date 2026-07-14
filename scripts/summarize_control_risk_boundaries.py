#!/usr/bin/env python
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.risk_analysis import summarize_boundary_surface


parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
source = Path(args.input)
result = summarize_boundary_surface(json.loads(source.read_text(encoding="utf-8")))
result["source_sha256"] = sha256(source.read_bytes()).hexdigest()
payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
target = Path(args.output)
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists() and target.read_bytes() != payload:
    raise FileExistsError(f"refusing to overwrite different boundary summary: {target}")
target.write_bytes(payload)
print(json.dumps({"output": str(target), "sha256": sha256(payload).hexdigest()}, indent=2))

