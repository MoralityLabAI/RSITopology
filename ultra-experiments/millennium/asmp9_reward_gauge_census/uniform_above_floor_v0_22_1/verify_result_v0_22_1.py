from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V022 = HERE.parent / "uniform_above_floor_v0_22"
sys.path.insert(0, str(V022))

from verify_result_v0_22 import (  # noqa: E402
    microtrial,
    tutte_deletion_contraction,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def graph_parts(
    raw: dict[str, Any],
) -> tuple[int, tuple[tuple[int, int], ...]]:
    return int(raw["node_count"]), tuple(
        tuple(edge) for edge in raw["edges"]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    registration = json.loads(
        args.registration.read_text(encoding="utf-8")
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    checks: dict[str, bool] = {
        "registration_hash": (
            sha256(args.registration)
            == result["registration_sha256"]
            == receipt["registration_sha256"]
        ),
        "result_hash": sha256(args.result) == receipt["result_sha256"],
        "sealed_hashes": all(
            sha256(REPO / relative) == expected
            for relative, expected in registration["sealed_files"].items()
        ),
        "predecessor_binding": result["gates"][
            "G0_registration_and_predecessor_binding"
        ]["predecessor"]["pass"],
        "structured_attribution": result["gates"][
            "G8_structured_complexity_attribution"
        ]["allowed_exact_match"]
        and result["gates"]["G8_structured_complexity_attribution"][
            "forbidden_exact_match"
        ],
    }

    independent: dict[str, Any] = {}
    for graph_name, raw in protocol["primary_graphs"].items():
        node_count, edges = graph_parts(raw)
        genus = len(edges) - node_count + 1
        graph_results: dict[str, Any] = {}
        for trial_count in protocol["registered_trial_counts"]:
            z = Fraction(1, 2**trial_count)
            x_value = (1 - 2 * z) / (1 - z)
            y_value = 1 / z
            tutte = tutte_deletion_contraction(edges, x_value, y_value)
            availability = (
                (1 - z) ** (node_count - 1) * z**genus * tutte
            )
            expected = Fraction(
                result["cells"][graph_name][str(trial_count)][
                    "availability"
                ]
            )
            checks[f"{graph_name}_r{trial_count}"] = (
                availability == expected
            )
            graph_results[str(trial_count)] = {
                "availability": (
                    f"{availability.numerator}/{availability.denominator}"
                ),
                "tutte_value": (
                    f"{tutte.numerator}/{tutte.denominator}"
                ),
            }
        independent[graph_name] = graph_results

    micro_name = result["gates"][
        "G5_minimal_above_floor_microtrial"
    ]["graph"]
    micro_n, micro_edges = graph_parts(
        protocol["primary_graphs"][micro_name]
    )
    independent_micro = microtrial(micro_n, micro_edges, 2)
    expected_micro = Fraction(
        result["gates"]["G5_minimal_above_floor_microtrial"][
            "microtrial_availability"
        ]
    )
    checks["independent_microtrial"] = (
        independent_micro == expected_micro
    )
    checks["all_registered_gates_pass"] = all(
        result["gate_passes"].values()
    )
    checks["verdict"] = (
        result["verdict"]
        == protocol["verdict_map"]["all_gates_pass"]
    )

    payload = {
        "check_count": len(checks),
        "checks": checks,
        "independent_microtrial": (
            f"{independent_micro.numerator}/{independent_micro.denominator}"
        ),
        "independent_results": independent,
        "pass": all(checks.values()),
        "result_sha256": sha256(args.result),
        "verifier_imports_implementation": False,
        "verifier_imports_runner": False,
        "verifier_reuses_preoutcome_v0_22_independent_algorithms": True,
    }
    write_json_exclusive(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
