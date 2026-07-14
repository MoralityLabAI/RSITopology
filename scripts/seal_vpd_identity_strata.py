#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology import AnchorRegistry, write_sealed_strata


parser = argparse.ArgumentParser()
parser.add_argument("--features", required=True)
parser.add_argument("--registry", required=True)
parser.add_argument("--protocol", default="protocols/vpd_identity_stratification_v0_2.json")
parser.add_argument("--output", required=True)
args = parser.parse_args()
features = [json.loads(line) for line in Path(args.features).read_text(encoding="utf-8").splitlines() if line]
manifest = write_sealed_strata(
    args.output,
    features,
    AnchorRegistry.load(args.registry),
    protocol_path=args.protocol,
)
print(json.dumps(manifest, indent=2, sort_keys=True))
