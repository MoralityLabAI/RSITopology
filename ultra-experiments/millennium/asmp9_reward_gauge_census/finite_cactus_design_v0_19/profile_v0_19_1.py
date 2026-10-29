"""Post-outcome timing profile for the burned v0.19.1 workload.

This diagnostic is not part of the registered evidence.  It identifies the
runtime-dominant exact stage before any further successor is designed.
"""

from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path
from typing import Any, Callable

from run_verification import (
    all_edge_record,
    comparator_record,
    dp_record,
    regression_certificates,
)
from run_verification_v0_19_1 import (
    burned_cache_regression,
    cached_bridge_record,
    cached_factorization_record,
)


HERE = Path(__file__).resolve().parent


def timed(name: str, call: Callable[[], Any]) -> dict[str, Any]:
    gc.collect()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    value = call()
    row = {
        "name": name,
        "wall_seconds": time.perf_counter() - wall_start,
        "cpu_seconds": time.process_time() - cpu_start,
    }
    if isinstance(value, dict):
        if "mismatch_count" in value:
            row["mismatch_count"] = value["mismatch_count"]
        if "allocation_count" in value:
            row["allocation_count"] = value["allocation_count"]
        if "pass" in value:
            row["stage_pass"] = value["pass"]
    print(json.dumps(row, sort_keys=True), flush=True)
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=HERE / "protocol_v0_19_1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    rows.append(
        timed(
            "burned_cache_regression",
            lambda: burned_cache_regression(protocol),
        )
    )
    factor_raw = protocol["factorization_cells"][
        "fresh_19_1_figure_4_4"
    ]
    rows.append(
        timed(
            "fresh_factorization_4_4",
            lambda: cached_factorization_record(
                "fresh_19_1_figure_4_4", factor_raw
            ),
        )
    )
    bridge_raw = protocol["factorization_cells"][
        "fresh_19_1_figure_3_6_bridge"
    ]
    rows.append(
        timed(
            "fresh_bridge_3_6",
            lambda: cached_bridge_record(
                "fresh_19_1_figure_3_6_bridge", bridge_raw
            ),
        )
    )
    for name, raw in protocol["dp_cells"].items():
        rows.append(timed(f"dp:{name}", lambda n=name, r=raw: dp_record(n, r)))
    rows.append(
        timed(
            "all_edge_census",
            lambda: all_edge_record(protocol["global_edge_census"]),
        )
    )
    rows.append(timed("regressions", regression_certificates))
    for name, raw in protocol["comparator_cells"].items():
        rows.append(
            timed(
                f"comparator:{name}",
                lambda n=name, r=raw: comparator_record(n, r),
            )
        )

    summary = {
        "diagnostic_only": True,
        "protocol_id": protocol["protocol_id"],
        "total_profiled_wall_seconds": sum(
            row["wall_seconds"] for row in rows
        ),
        "dominant_stage": max(rows, key=lambda row: row["wall_seconds"])[
            "name"
        ],
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
