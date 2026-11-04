from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from experiment import run_registry


DEFAULT_SPEC = {
    "alpha": "1/20",
    "cycle_lengths": [3, 4, 5],
    "trials_per_edge": [1, 2, 3],
    "odds_ratios": ["3/2", "2/1", "3/1"],
    "nuisance_ratios": ["1/1", "2/1", "4/1", "16/1", "256/1"],
}


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def endpoint_pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[int, int, str], dict[str, dict[str, Any]]] = {}
    for record in records:
        key = (
            record["cycle_length"],
            record["trials_per_edge"],
            record["odds_ratio"],
        )
        groups.setdefault(key, {})[record["nuisance_ratio"]] = record
    pairs = []
    for key, by_nuisance in sorted(groups.items()):
        balanced = by_nuisance["1/1"]
        extreme = by_nuisance["256/1"]
        balanced_excess = balanced["excess_power"]["decimal"]
        extreme_excess = extreme["excess_power"]["decimal"]
        pairs.append(
            {
                "cycle_length": key[0],
                "trials_per_edge": key[1],
                "odds_ratio": key[2],
                "balanced_availability": balanced[
                    "availability_alternative"
                ]["decimal"],
                "extreme_availability": extreme[
                    "availability_alternative"
                ]["decimal"],
                "balanced_excess_power": balanced_excess,
                "extreme_excess_power": extreme_excess,
                "excess_power_ratio": (
                    extreme_excess / balanced_excess
                    if balanced_excess > 0
                    else None
                ),
            }
        )
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    result = run_registry(DEFAULT_SPEC)
    pairs = endpoint_pairs(result["records"])
    result["endpoint_pairs"] = pairs
    result["endpoint_pair_count"] = len(pairs)
    result["all_extreme_availability_lower"] = all(
        pair["extreme_availability"] < pair["balanced_availability"]
        for pair in pairs
    )
    result["all_extreme_excess_power_lower"] = all(
        pair["extreme_excess_power"] < pair["balanced_excess_power"]
        for pair in pairs
    )
    result["maximum_extreme_to_balanced_excess_ratio"] = max(
        pair["excess_power_ratio"] for pair in pairs
    )
    write_json(args.output, result)
    receipt_path = args.output.with_name(
        args.output.stem + "_receipt.json"
    )
    write_json(
        receipt_path,
        {
            "result_sha256": sha256(args.output),
            "cell_count": result["cell_count"],
            "status": "burned_development_only",
        },
    )
    print(
        json.dumps(
            {
                "cell_count": result["cell_count"],
                "availability_formula_mismatch_count": result[
                    "availability_formula_mismatch_count"
                ],
                "conditional_size_mismatch_count": result[
                    "conditional_size_mismatch_count"
                ],
                "excess_decomposition_mismatch_count": result[
                    "excess_decomposition_mismatch_count"
                ],
                "upper_bound_mismatch_count": result[
                    "upper_bound_mismatch_count"
                ],
                "interior_lower_bound_mismatch_count": result[
                    "interior_lower_bound_mismatch_count"
                ],
                "all_extreme_availability_lower": result[
                    "all_extreme_availability_lower"
                ],
                "all_extreme_excess_power_lower": result[
                    "all_extreme_excess_power_lower"
                ],
                "maximum_extreme_to_balanced_excess_ratio": result[
                    "maximum_extreme_to_balanced_excess_ratio"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
