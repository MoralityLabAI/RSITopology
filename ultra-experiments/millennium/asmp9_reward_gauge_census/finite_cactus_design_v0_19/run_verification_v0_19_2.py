from __future__ import annotations

import argparse
import json
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from cycle_cache_v0_19_2 import (
    CachedExhaustiveResult,
    optimize_cycle_totals_cached_independent,
)
from finite_cactus_design import (
    allocation_value,
    fraction_record,
    globally_balanced_cycle_totals,
    marginal_greedy_endpoints,
    optimize_cactus_dp,
)
from run_verification import (
    all_edge_record,
    git,
    peak_resident_bytes,
    regression_certificates,
    sha256,
    utc_now,
    validate_registration,
    write_json,
    write_text,
)
from run_verification_v0_19_1 import (
    cached_bridge_record,
    cached_factorization_record,
    fresh_registry_checks,
)


HERE = Path(__file__).resolve().parent


def cached_result_record(
    value: CachedExhaustiveResult,
) -> dict[str, Any]:
    return {
        "value": fraction_record(value.value),
        "cycle_totals": [list(totals) for totals in value.cycle_totals],
        "allocations_evaluated": value.allocations_evaluated,
        "independent_cycle_values_evaluated": (
            value.independent_cycle_values_evaluated
        ),
    }


def dynamic_result_record(value: Any) -> dict[str, Any]:
    return {
        "value": fraction_record(value.value),
        "cycle_totals": [list(totals) for totals in value.cycle_totals],
        "transitions_evaluated": value.transitions_evaluated,
    }


def dp_record_cached(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    lengths = tuple(int(value) for value in raw["cycle_lengths"])
    total = int(raw["total_budget"])
    bridges = int(raw["bridge_count"])
    epsilon = Fraction(raw["epsilon"])
    dynamic = optimize_cactus_dp(lengths, total, epsilon, bridges)
    independent = optimize_cycle_totals_cached_independent(
        lengths, total, epsilon, bridges
    )
    return {
        "name": name,
        "cycle_lengths": list(lengths),
        "bridge_count": bridges,
        "total_budget": total,
        "epsilon": raw["epsilon"],
        "dynamic": dynamic_result_record(dynamic),
        "independent_exhaustive": cached_result_record(independent),
        "value_equal": dynamic.value == independent.value,
        "optimizers_equal": (
            dynamic.cycle_totals == independent.cycle_totals
        ),
    }


def comparator_record_cached(
    name: str, raw: dict[str, Any]
) -> dict[str, Any]:
    lengths = tuple(int(value) for value in raw["cycle_lengths"])
    epsilon = Fraction(raw["epsilon"])
    total = int(raw["total_budget"])
    bridges = int(raw["bridge_count"])
    if bridges:
        raise ValueError("registered comparator cells have no bridges")
    dynamic = optimize_cactus_dp(lengths, total, epsilon, bridges)
    independent = optimize_cycle_totals_cached_independent(
        lengths, total, epsilon, bridges
    )
    greedy_totals = marginal_greedy_endpoints(lengths, total, epsilon)
    greedy_rows = [
        {
            "cycle_totals": list(totals),
            "value": fraction_record(
                allocation_value(lengths, totals, epsilon)
            ),
        }
        for totals in greedy_totals
    ]
    global_totals = globally_balanced_cycle_totals(lengths, total)
    global_rows = [
        {
            "cycle_totals": list(totals),
            "value": fraction_record(
                allocation_value(lengths, totals, epsilon)
            ),
        }
        for totals in global_totals
    ]
    best_greedy = max(
        Fraction(row["value"]["fraction"]) for row in greedy_rows
    )
    best_global = max(
        Fraction(row["value"]["fraction"]) for row in global_rows
    )
    return {
        "name": name,
        "cycle_lengths": list(lengths),
        "total_budget": total,
        "epsilon": raw["epsilon"],
        "dynamic": dynamic_result_record(dynamic),
        "independent_exhaustive": cached_result_record(independent),
        "greedy": greedy_rows,
        "globally_balanced": global_rows,
        "greedy_gap": fraction_record(dynamic.value - best_greedy),
        "globally_balanced_gap": fraction_record(
            dynamic.value - best_global
        ),
        "dp_exhaustive_equal": (
            dynamic.value == independent.value
            and dynamic.cycle_totals == independent.cycle_totals
        ),
    }


def burned_cycle_cache_regression(
    protocol: dict[str, Any],
) -> dict[str, Any]:
    raw = protocol["burned_cache_regression"]
    old_protocol = json.loads(
        (HERE / raw["protocol_path"]).read_text(encoding="utf-8")
    )
    old_result = json.loads(
        (HERE / raw["result_path"]).read_text(encoding="utf-8")
    )
    reported = {row["name"]: row for row in old_result["dp_cells"]}
    rows = []
    for name, cell in old_protocol["dp_cells"].items():
        lengths = tuple(cell["cycle_lengths"])
        independent = optimize_cycle_totals_cached_independent(
            lengths,
            int(cell["total_budget"]),
            Fraction(cell["epsilon"]),
            int(cell["bridge_count"]),
        )
        expected = reported[name]["dynamic"]
        row = {
            "name": name,
            "value_equal": (
                Fraction(expected["value"]["fraction"])
                == independent.value
            ),
            "optimizers_equal": (
                tuple(tuple(item) for item in expected["cycle_totals"])
                == independent.cycle_totals
            ),
            "independent_cycle_values_evaluated": (
                independent.independent_cycle_values_evaluated
            ),
        }
        rows.append(row)
    return {
        "rows": rows,
        "pass": all(
            row["value_equal"] and row["optimizers_equal"] for row in rows
        ),
    }


def render_result(result: dict[str, Any]) -> str:
    gates = "\n".join(
        f"- `{gate}`: **{'PASS' if passed else 'FAIL'}**"
        for gate, passed in result["gates"].items()
    )
    dp_rows = "\n".join(
        (
            f"- `{row['name']}`: "
            f"`{row['dynamic']['value']['fraction']}`, totals "
            f"`{row['dynamic']['cycle_totals']}`"
        )
        for row in result["dp_cells"]
    )
    comparator_rows = "\n".join(
        (
            f"- `{row['name']}`: greedy gap "
            f"`{row['greedy_gap']['fraction']}`, global-balance gap "
            f"`{row['globally_balanced_gap']['fraction']}`"
        )
        for row in result["comparators"]
    )
    return f"""# ASMP-9 finite cactus-design result v0.19.2

## Verdict

```text
{result['verdict']}
```

## Gates

{gates}

## Exact finite allocations

{dp_rows}

The memoized checker still exhausted every feasible vector of cycle totals
and every endpoint-label assignment needed for each distinct one-cycle
value. It only removed duplicate evaluation of the same local value.

## Full edge census

The fresh labelled all-edge census evaluated
`{result['all_edge_census']['allocation_count']}` positive allocations.
Its value and complete induced optimizer-total set matched Bellman; every
optimizer balanced counts within each cycle and left bridges at count one.

## Outcome-neutral comparators

{comparator_rows}

Comparator gap signs were not gates.

## Resources

- elapsed: `{result['elapsed_seconds']:.6f}` seconds
- peak resident memory: `{result['peak_resident_bytes']}` bytes
- GPU used: `{result['gpu_used']}`

## Claim boundary

{result['claim_boundary']}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=HERE / "protocol_v0_19_2.json",
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_19_2.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    started_at = utc_now()
    started = time.perf_counter()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing nonempty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    protocol_path = args.protocol.resolve()
    registration_path = args.registration.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registration, registration_sha, seal_checks = validate_registration(
        registration_path, protocol_path
    )
    freshness = fresh_registry_checks(protocol)
    cache_regression = burned_cycle_cache_regression(protocol)
    factor_name, factor_raw = next(
        (
            (name, raw)
            for name, raw in protocol["factorization_cells"].items()
            if "counts" in raw
        )
    )
    bridge_name, bridge_raw = next(
        (
            (name, raw)
            for name, raw in protocol["factorization_cells"].items()
            if "counts_a" in raw
        )
    )
    factorization = cached_factorization_record(
        factor_name, factor_raw
    )
    bridge = cached_bridge_record(bridge_name, bridge_raw)
    dp_rows = [
        dp_record_cached(name, raw)
        for name, raw in protocol["dp_cells"].items()
    ]
    all_edge = all_edge_record(protocol["global_edge_census"])
    regressions = regression_certificates()
    comparators = [
        comparator_record_cached(name, raw)
        for name, raw in protocol["comparator_cells"].items()
    ]
    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    gates = {
        "G0_registration_binding": all(seal_checks.values()),
        "G1_fresh_registry": freshness["pass"],
        "G2_cached_cycle_engine_reproduces_burned_v0_19_1": (
            cache_regression["pass"]
        ),
        "G3_exact_cactus_factorization": (
            factorization["mismatch_count"] == 0 and bridge["pass"]
        ),
        "G4_bridge_irrelevance_and_floor": (
            bridge["pass"] and all_edge["bridges_at_floor"]
        ),
        "G5_dp_equals_cached_independent_exhaustive_totals": all(
            row["value_equal"] and row["optimizers_equal"]
            for row in dp_rows
        ),
        "G6_dp_equals_all_edge_census": (
            all_edge["value_equal"]
            and all_edge["totals_equal"]
            and all_edge["cycles_balanced"]
            and all_edge["bridges_at_floor"]
        ),
        "G7_nonconcavity_and_comparator_certificates": (
            regressions["greedy"]["pass"]
            and regressions["finite_uniform"]["pass"]
        ),
        "G8_fresh_comparator_classification": (
            len(comparators) == len(protocol["comparator_cells"])
            and all(row["dp_exhaustive_equal"] for row in comparators)
        ),
        "G9_resource_and_scope": (
            elapsed <= float(protocol["resource_caps"]["wall_seconds"])
            and peak
            <= int(protocol["resource_caps"]["peak_resident_bytes"])
            and not bool(protocol["resource_caps"]["gpu_allowed"])
        ),
    }
    verdict = (
        "finite_budget_cactus_dp_established_in_frozen_model_v0_19_2"
        if all(gates.values())
        else "finite_budget_cactus_dp_not_established_v0_19_2"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256(protocol_path),
        "registration_id": registration["registration_id"],
        "registration_sha256": registration_sha,
        "execution_commit": git("rev-parse", "HEAD"),
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "elapsed_seconds": elapsed,
        "peak_resident_bytes": peak,
        "gpu_used": False,
        "freshness": freshness,
        "seal_checks": seal_checks,
        "cache_regression": cache_regression,
        "factorization": factorization,
        "bridge": bridge,
        "dp_cells": dp_rows,
        "all_edge_census": all_edge,
        "regression_certificates": regressions,
        "comparators": comparators,
        "gates": gates,
        "verdict": verdict,
        "claim_boundary": protocol["claim_boundary"],
    }
    result_path = output / "result_v0_19_2.json"
    report_path = output / "RESULT_v0_19_2.md"
    write_json(result_path, result)
    write_text(report_path, render_result(result))
    receipt = {
        "protocol_sha256": sha256(protocol_path),
        "registration_sha256": registration_sha,
        "result_sha256": sha256(result_path),
        "report_sha256": sha256(report_path),
        "verdict": verdict,
        "gate_count": len(gates),
        "passed_gate_count": sum(gates.values()),
        "elapsed_seconds": elapsed,
        "peak_resident_bytes": peak,
    }
    write_json(output / "run_receipt_v0_19_2.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
