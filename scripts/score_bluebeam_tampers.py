#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.bluebeam_tamper import generate_tamper_suite, score_bluebeam_detections


parser = argparse.ArgumentParser()
parser.add_argument("--detections", required=True, help="JSONL with tamper_id, detected, detector")
parser.add_argument("--output")
args = parser.parse_args()
detections = [json.loads(line) for line in Path(args.detections).read_text(encoding="utf-8").splitlines() if line]
result = score_bluebeam_detections(generate_tamper_suite(), detections)
payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
if args.output:
    Path(args.output).write_text(payload, encoding="utf-8")
print(payload, end="")
