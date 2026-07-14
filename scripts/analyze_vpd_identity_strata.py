#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology import analyze_stratified_outcomes


parser = argparse.ArgumentParser()
parser.add_argument("--sealed", required=True)
parser.add_argument("--registration", required=True)
parser.add_argument("--outcomes", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

def rows(path: str):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]

registration = json.loads(Path(args.registration).read_text(encoding="utf-8"))
result = analyze_stratified_outcomes(rows(args.sealed), rows(args.outcomes), registration)
payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
target = Path(args.output)
if target.resolve() in {Path(args.sealed).resolve(), Path(args.registration).resolve(), Path(args.outcomes).resolve()}:
    raise ValueError("output may not overwrite any input")
if target.exists():
    raise FileExistsError(f"refusing to overwrite analysis: {target}")
target.write_text(payload, encoding="utf-8")
print(payload, end="")
