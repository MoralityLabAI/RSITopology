#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.bluebeam_tamper import write_tamper_pack


parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True)
args = parser.parse_args()
print(json.dumps(write_tamper_pack(args.output), indent=2, sort_keys=True))
