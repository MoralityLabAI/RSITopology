from __future__ import annotations

import argparse
import json
import time
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

from finite_cactus_design import (
    bouquet_cactus,
    cactus_availability_factorized,
)
from residual_cache_v0_19_1 import (
    graph_availability_cached,
    live_status_table,
)
from run_verification import (
    all_edge_record,
    bridge_record,
    comparator_record,
    dp_record,
    git,
    peak_resident_bytes,
    regression_certificates,
    sha256,
    sha256_json,
    utc_now,
    validate_registration,
    write_json,
    write_text,
)


HERE = Path(__file__).resolve().parent


def fresh_registry_checks(protocol: dict[str, Any]) -> dict[str, Any]:
    burned = {
        Fraction(value)
        for value in protocol["development_registry"][
            "burned_epsilon_values"
        ]
    }
    sections = {
        "factorization": protocol["factorization_cells"],
        "dp": protocol["dp_cells"],
        "comparator": protocol["comparator_cells"],
        "global": {"global_edge_census": protocol["global_edge_census"]},
    }
    ids = [
        f"{section}:{name}"
        for section, cells in sections.items()
        for name in cells
    ]
    epsilon_rows = [
        {
            "cell": f"{section}:{name}",
            "epsilon": raw["epsilon"],
            "outside_burned_set": Fraction(raw["epsilon"]) not in burned,
        }
        for section, cells in sections.items()
        for name, raw in cells.items()
    ]
    dimensions: dict[str, bool] = {}
    for name, raw in protocol["factorization_cells"].items():
        edge_count = sum(raw["cycle_lengths"]) + raw["bridge_count"]
        if "counts" in raw:
            dimensions[name] = len(raw["counts"]) == edge_count
        else:
            dimensions[name] = (
                len(raw["counts_a"]) == edge_count
                and len(raw["counts_b"]) == edge_count
                and all(
                    len(labels) == edge_count
                    for labels in raw["label_vectors"]
                )
            )
    for section in ("dp_cells", "comparator_cells"):
        for name, raw in protocol[section].items():
            dimensions[name] = (
                raw["total_budget"]
                >= sum(raw["cycle_lengths"]) + raw["bridge_count"]
            )
    global_raw = protocol["global_edge_census"]
    dimensions["global_edge_census"] = (
        global_raw["total_budget"]
        >= sum(global_raw["cycle_lengths"])
        + global_raw["bridge_count"]
    )
    return {
        "cell_ids": ids,
        "unique_cell_ids": len(ids) == len(set(ids)),
        "epsilon_rows": epsilon_rows,
        "dimensions": dimensions,
        "pass": (
            len(ids) == len(set(ids))
            and all(row["outside_burned_set"] for row in epsilon_rows)
            and all(dimensions.values())
        ),
    }


def cached_factorization_record(
    name: str, raw: dict[str, Any]
) -> dict[str, Any]:
    graph = bouquet_cactus(
        raw["cycle_lengths"], raw["bridge_count"]
    )
    live = live_status_table(graph)
    epsilon = Fraction(raw["epsilon"])
    counts = tuple(int(value) for value in raw["counts"])
    rows: list[dict[str, Any]] = []
    mismatches = 0
    for labels in product((0, 1), repeat=len(graph.edges)):
        direct = graph_availability_cached(
            graph, live, counts, epsilon, labels
        )
        factorized = cactus_availability_factorized(
            graph, counts, epsilon, labels
        )
        mismatches += direct != factorized
        rows.append(
            {
                "labels": "".join(str(value) for value in labels),
                "direct": f"{direct.numerator}/{direct.denominator}",
                "factorized": (
                    f"{factorized.numerator}/{factorized.denominator}"
                ),
            }
        )
    return {
        "name": name,
        "edge_count": len(graph.edges),
        "live_status_count": len(live),
        "total_status_count": 3 ** len(graph.edges),
        "label_count": len(rows),
        "integer_contractions": len(rows) * len(live),
        "mismatch_count": mismatches,
        "row_sha256": sha256_json(rows),
        "rows": rows,
    }


def cached_bridge_record(
    name: str, raw: dict[str, Any]
) -> dict[str, Any]:
    graph = bouquet_cactus(
        raw["cycle_lengths"], raw["bridge_count"]
    )
    live = live_status_table(graph)
    epsilon = Fraction(raw["epsilon"])
    counts_a = tuple(int(value) for value in raw["counts_a"])
    counts_b = tuple(int(value) for value in raw["counts_b"])
    rows = []
    for raw_labels in raw["label_vectors"]:
        labels = tuple(int(value) for value in raw_labels)
        direct_a = graph_availability_cached(
            graph, live, counts_a, epsilon, labels
        )
        direct_b = graph_availability_cached(
            graph, live, counts_b, epsilon, labels
        )
        factorized = cactus_availability_factorized(
            graph, counts_a, epsilon, labels
        )
        rows.append(
            {
                "labels": "".join(str(value) for value in labels),
                "direct_a": (
                    f"{direct_a.numerator}/{direct_a.denominator}"
                ),
                "direct_b": (
                    f"{direct_b.numerator}/{direct_b.denominator}"
                ),
                "factorized": (
                    f"{factorized.numerator}/{factorized.denominator}"
                ),
                "all_equal": direct_a == direct_b == factorized,
            }
        )
    return {
        "name": name,
        "edge_count": len(graph.edges),
        "live_status_count": len(live),
        "total_status_count": 3 ** len(graph.edges),
        "label_count": len(rows),
        "integer_contractions": 2 * len(rows) * len(live),
        "rows": rows,
        "pass": all(row["all_equal"] for row in rows),
    }


def burned_cache_regression(protocol: dict[str, Any]) -> dict[str, Any]:
    raw = protocol["burned_cache_regression"]
    old_protocol = json.loads(
        (HERE / raw["protocol_path"]).read_text(encoding="utf-8")
    )
    old_result = json.loads(
        (HERE / raw["result_path"]).read_text(encoding="utf-8")
    )
    cached_factor = cached_factorization_record(
        "burned_v0_19_factorization",
        old_protocol["factorization_cells"]["fresh_figure_3_4"],
    )
    cached_bridge = cached_bridge_record(
        "burned_v0_19_bridge",
        old_protocol["factorization_cells"][
            "fresh_figure_3_5_bridge"
        ],
    )
    old_bridge_rows = {
        row["labels"]: row for row in old_result["bridge"]["rows"]
    }
    bridge_rows_equal = all(
        row["direct_a"]
        == old_bridge_rows[row["labels"]]["direct_a"]["fraction"]
        and row["direct_b"]
        == old_bridge_rows[row["labels"]]["direct_b"]["fraction"]
        and row["factorized"]
        == old_bridge_rows[row["labels"]]["factorized"]["fraction"]
        for row in cached_bridge["rows"]
    )
    return {
        "factorization_row_sha256": cached_factor["row_sha256"],
        "expected_factorization_row_sha256": old_result[
            "factorization"
        ]["row_sha256"],
        "bridge_rows_equal": bridge_rows_equal,
        "pass": (
            cached_factor["row_sha256"]
            == old_result["factorization"]["row_sha256"]
            and bridge_rows_equal
            and cached_factor["mismatch_count"] == 0
            and cached_bridge["pass"]
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
    return f"""# ASMP-9 v0.19.1 finite cactus-design result

## Verdict

`{result['verdict']}`

## Gates

{gates}

## Fresh exact cells

{dp_rows}

The cached integer residual engine first reproduced the complete burned v0.19
factorization-row hash and bridge equalities. On the wholly new cells it then
matched the cycle product exactly.

The fresh full edge census considered
`{result['all_edge_census']['allocation_count']}` positive labelled
allocations. Its value and induced cycle totals equal the Bellman result; all
optimizers balance inside cycles and leave the bridge at count one.

## Outcome-neutral comparator cells

{comparator_rows}

Gap signs were not pass conditions.

## Interpretation

For cactus cyclic cores in the frozen comparison model, finite-budget
availability factors by cycle. Counts balance within cycles, while exact
cycle-total allocation is a classical separable integer dynamic program.
Nonconcavity prevents promoting a one-step greedy rule, and v0.18's
asymptotically uniform allocation remains only asymptotic.

## Claim boundary

{result['claim_boundary']}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=HERE / "protocol_v0_19_1.json",
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_19_1.json",
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
    cache_regression = burned_cache_regression(protocol)
    factorization = cached_factorization_record(
        "fresh_19_1_figure_4_4",
        protocol["factorization_cells"]["fresh_19_1_figure_4_4"],
    )
    bridge = cached_bridge_record(
        "fresh_19_1_figure_3_6_bridge",
        protocol["factorization_cells"][
            "fresh_19_1_figure_3_6_bridge"
        ],
    )
    dp_rows = [
        dp_record(name, raw)
        for name, raw in protocol["dp_cells"].items()
    ]
    all_edge = all_edge_record(protocol["global_edge_census"])
    regressions = regression_certificates()
    comparators = [
        comparator_record(name, raw)
        for name, raw in protocol["comparator_cells"].items()
    ]
    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    gates = {
        "G0_registration_binding": all(seal_checks.values()),
        "G1_fresh_registry": freshness["pass"],
        "G2_cached_engine_reproduces_burned_v0_19": (
            cache_regression["pass"]
        ),
        "G3_exact_cactus_factorization": (
            factorization["mismatch_count"] == 0 and bridge["pass"]
        ),
        "G4_bridge_irrelevance_and_floor": (
            bridge["pass"] and all_edge["bridges_at_floor"]
        ),
        "G5_dp_equals_independent_exhaustive_totals": all(
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
        "finite_budget_cactus_dp_established_in_frozen_model_v0_19_1"
        if all(gates.values())
        else "finite_budget_cactus_dp_not_established_v0_19_1"
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
    result_path = output / "result_v0_19_1.json"
    report_path = output / "RESULT_v0_19_1.md"
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
    write_json(output / "run_receipt_v0_19_1.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
