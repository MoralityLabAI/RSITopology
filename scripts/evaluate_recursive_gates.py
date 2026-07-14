"""Apply the frozen total mapping to proposal-recursion gate records."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.recursive_gate import fixed_sequence


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evaluate(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("gates")
    if not isinstance(records, list) or not records:
        raise ValueError("input must contain a nonempty gates list")
    output = fixed_sequence(records)
    return {
        "schema_version": "proposal_recursive_gate_evaluation_v1",
        "input_sha256": sha256_file(path),
        "gates": output,
        "sequence_open": bool(output and output[-1]["gate_decision"] == "pass"),
        "earlier_passes_survive_downstream_invalidity": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    result = evaluate(args.input.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "complete", "gate_count": len(result["gates"])}))


if __name__ == "__main__":
    main()
