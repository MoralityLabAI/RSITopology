from __future__ import annotations

import argparse
import json
from pathlib import Path

from physical_target import run_registered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = run_registered(config, args.output_dir)
    print(json.dumps({"overall_pass": result["overall_pass"]}, sort_keys=True))


if __name__ == "__main__":
    main()
