"""Projective angle-budget liveness analysis for rank-one holonomy."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from .godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal
from .qwen_precision_context import (
    PRECISIONS,
    STATES,
    _node_features,
    _stable_seed,
    build_pair_store,
    load_protocol as load_scientific_protocol,
    validate_manifest,
)
from .qwen_precision_filtration_w1 import (
    _resampled_bases,
    gauge_preflight,
    measure_graph,
)


PROTOCOL_ID = "qwen08_precision_frustration_margin_v0_1"
RESULT_SCHEMA = "qwen08_precision_frustration_margin_result_v0_1"
CHECKPOINT_SCHEMA = "qwen08_precision_frustration_margin_checkpoint_v0_1"


def load_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != PROTOCOL_ID or value.get("status") != "registered_not_run":
        raise ValueError("unexpected or unregistered frustration-margin protocol")
    if value.get("outcomes_consumed") is not False or value.get("new_invariant_levels") is not False:
        raise ValueError("frustration-margin protocol violates its claim boundary")
    return value


def edge_angle_degrees_from_retention(retention: float) -> float:
    if not np.isfinite(retention) or not 0.0 <= retention <= 1.0:
        raise ValueError("edge retention must be finite and in [0, 1]")
    return float(np.degrees(np.arccos(np.sqrt(np.clip(retention, 0.0, 1.0)))))


def cycle_budget_records(graph: Any) -> list[dict[str, Any]]:
    edge_by_id = {row["edge_id"]: row for row in graph.edges}
    rows = []
    for cycle in graph.cycles:
        conservative_angles = [
            edge_angle_degrees_from_retention(float(edge_by_id[edge_id]["lineage"]))
            for edge_id in cycle["edge_ids"]
        ]
        construction_angles = [
            float(np.degrees(np.arccos(np.clip(abs(edge_by_id[edge_id]["construction_overlap"]), 0.0, 1.0))))
            for edge_id in cycle["edge_ids"]
        ]
        validation_angles = [
            float(np.degrees(np.arccos(np.clip(abs(edge_by_id[edge_id]["geometry_validation_overlap"]), 0.0, 1.0))))
            for edge_id in cycle["edge_ids"]
        ]
        budget = float(sum(conservative_angles))
        rows.append(
            {
                "cycle_id": cycle["cycle_id"],
                "edge_ids": list(cycle["edge_ids"]),
                "edge_count": int(cycle["edge_count"]),
                "connected_simple_loop": bool(cycle["connected_simple_loop"]),
                "conservative_edge_angles_degrees": conservative_angles,
                "conservative_angle_budget_degrees": budget,
                "frustration_margin_degrees": 180.0 - budget,
                "construction_actual_angle_sum_degrees": float(sum(construction_angles)),
                "geometry_validation_actual_angle_sum_degrees": float(sum(validation_angles)),
                "geometry_validation_sign": int(cycle["geometry_validation_sign"]),
                "forced_orientable_point": budget < 180.0,
                "w1_live_point": budget >= 180.0,
            }
        )
    return rows


def summarize_graph(graph: Any) -> dict[str, Any]:
    cycles = cycle_budget_records(graph)
    simple = [row for row in cycles if row["connected_simple_loop"]]
    maximum = max(simple, key=lambda row: row["conservative_angle_budget_degrees"])
    return {
        "cycles": cycles,
        "maximum_simple_cycle_id": maximum["cycle_id"],
        "maximum_angle_budget_degrees": maximum["conservative_angle_budget_degrees"],
        "minimum_frustration_margin_degrees": maximum["frustration_margin_degrees"],
    }


def _interval(values: Sequence[float], point: float) -> dict[str, float | str]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "point": float(point),
        "lower_descriptive_90": float(np.quantile(array, 0.05, method="linear")),
        "upper_descriptive_90": float(np.quantile(array, 0.95, method="linear")),
        "coverage_claim": "descriptive_percentile_interval_no_calibrated_coverage",
    }


def _checkpoint_hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _load_blocks(directory: Path, *, binding: str) -> tuple[list[dict[str, Any]], str | None, int]:
    rows = []
    previous = None
    expected = 0
    for path in sorted(directory.glob("block_*.json")):
        item = json.loads(path.read_text(encoding="utf-8-sig"))
        if item.get("schema_version") != CHECKPOINT_SCHEMA or item.get("binding_sha256") != binding:
            raise ValueError(f"checkpoint binding differs: {path}")
        if item.get("previous_checkpoint_sha256") != previous or int(item["start"]) != expected:
            raise ValueError(f"checkpoint chain differs: {path}")
        block = list(item.get("replicates", ()))
        if int(item["stop"]) != expected + len(block):
            raise ValueError(f"checkpoint range differs: {path}")
        rows.extend(block)
        expected += len(block)
        previous = _checkpoint_hash(item)
    return rows, previous, expected


def _bootstrap_record(
    raw: Mapping[tuple[str, str, str, str], tuple[np.ndarray, np.ndarray, np.ndarray]],
    *,
    replicate: int,
    seed: int,
) -> dict[str, Any]:
    bases = _resampled_bases(
        raw,
        replicate_seed=_stable_seed(seed, "frustration-margin", str(replicate)),
    )
    graphs = {}
    for precision in PRECISIONS:
        for site in ("model.layers.19", "model.layers.23"):
            graph = measure_graph(
                {
                    (state, shard): bases[(precision, state, site, shard)]
                    for state in STATES
                    for shard in ("shard-00", "shard-01", "shard-02", "shard-03")
                }
            )
            summary = summarize_graph(graph)
            graphs[f"{precision}|{site}"] = {
                "maximum_angle_budget_degrees": summary["maximum_angle_budget_degrees"],
                "minimum_frustration_margin_degrees": summary["minimum_frustration_margin_degrees"],
                "cycle_budgets": {
                    row["cycle_id"]: row["conservative_angle_budget_degrees"]
                    for row in summary["cycles"]
                },
            }
    return {"replicate": replicate, "graphs": graphs}


def budget_gauge_preflight(
    bases: Mapping[tuple[str, str], Mapping[str, np.ndarray]],
    *,
    reframings: int,
    seed: int,
) -> dict[str, Any]:
    original = summarize_graph(measure_graph(bases))
    expected = {
        row["cycle_id"]: (
            row["conservative_angle_budget_degrees"],
            row["forced_orientable_point"],
            row["geometry_validation_sign"],
        )
        for row in original["cycles"]
    }
    rng = np.random.default_rng(seed)
    mismatches = 0
    for _ in range(reframings):
        reframed = {
            key: {
                half: np.asarray(vector) * float(rng.choice((-1, 1)))
                for half, vector in value.items()
            }
            for key, value in bases.items()
        }
        observed = summarize_graph(measure_graph(reframed))
        for row in observed["cycles"]:
            target = expected[row["cycle_id"]]
            mismatches += int(abs(row["conservative_angle_budget_degrees"] - target[0]) > 1e-10)
            mismatches += int(row["forced_orientable_point"] != target[1])
            mismatches += int(row["geometry_validation_sign"] != target[2])
    return {
        "reframings": reframings,
        "decisions_checked": reframings * len(expected) * 3,
        "mismatches": mismatches,
        "passed": mismatches == 0,
    }


def analyze(
    *,
    protocol_path: str | Path,
    scientific_protocol_path: str | Path,
    filtration_result_path: str | Path,
    manifest_path: str | Path,
    fourbit_indices: Mapping[str, str | Path],
    float16_indices: Mapping[str, str | Path],
    output_dir: str | Path,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    protocol_path = Path(protocol_path).resolve()
    scientific_protocol_path = Path(scientific_protocol_path).resolve()
    filtration_result_path = Path(filtration_result_path).resolve()
    manifest_path = Path(manifest_path).resolve()
    protocol = load_protocol(protocol_path)
    scientific = load_scientific_protocol(scientific_protocol_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    validate_manifest(manifest, protocol_path=scientific_protocol_path)
    locks = protocol["parent"]
    for path, expected, label in (
        (scientific_protocol_path, locks["scientific_protocol_sha256"], "scientific protocol"),
        (filtration_result_path, locks["filtration_result_sha256"], "filtration result"),
        (manifest_path, locks["prompt_manifest_sha256"], "prompt manifest"),
    ):
        if sha256_file(path) != expected:
            raise ValueError(f"{label} hash differs")
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    stores = {
        "4bit": build_pair_store(
            protocol_path=scientific_protocol_path,
            manifest_path=manifest_path,
            precision="4bit",
            state_index_paths=fourbit_indices,
            output_dir=output / "fourbit",
        ),
        "float16": build_pair_store(
            protocol_path=scientific_protocol_path,
            manifest_path=manifest_path,
            precision="float16",
            state_index_paths=float16_indices,
            output_dir=output / "float16",
        ),
    }
    raw = {}
    observed_bases = {}
    from .qwen_precision_filtration_w1 import _basis

    for precision, store in stores.items():
        for state in STATES:
            for site in scientific["sites"]:
                for shard_index in range(4):
                    shard = f"shard-{shard_index:02d}"
                    payload = _node_features(
                        store,
                        manifest,
                        runtime=state,
                        site=site,
                        family="graph_reachability",
                        shard=shard,
                    )
                    key = (precision, state, site, shard)
                    raw[key] = payload
                    observed_bases[key] = _basis(*payload)
    reference_labels, reference_halves = next(iter(raw.values()))[1:]
    for key, (_, labels, halves) in raw.items():
        if not np.array_equal(labels, reference_labels) or not np.array_equal(halves, reference_halves):
            raise ValueError(f"paired prompt strata differ at {key}")
    observed = {}
    gauges = {}
    for precision in PRECISIONS:
        for site in scientific["sites"]:
            key = f"{precision}|{site}"
            bases = {
                (state, shard): observed_bases[(precision, state, site, shard)]
                for state in STATES
                for shard in ("shard-00", "shard-01", "shard-02", "shard-03")
            }
            graph = measure_graph(bases)
            observed[key] = summarize_graph(graph)
            sign_gauge = gauge_preflight(
                graph,
                reframings=int(protocol["controls"]["gauge_preflight"].split()[0]),
                seed=_stable_seed(int(protocol["resampling"]["seed"]), "sign-gauge", key),
            )
            budget_gauge = budget_gauge_preflight(
                bases,
                reframings=384,
                seed=_stable_seed(int(protocol["resampling"]["seed"]), "budget-gauge", key),
            )
            gauges[key] = {"sign": sign_gauge, "budget_and_liveness": budget_gauge, "passed": sign_gauge["passed"] and budget_gauge["passed"]}
    binding = hashlib.sha256(
        canonical_json_bytes(
            {
                "protocol_sha256": sha256_file(protocol_path),
                "filtration_result_sha256": sha256_file(filtration_result_path),
                "pair_indices": {precision: sha256_file(store.index_path) for precision, store in stores.items()},
            }
        )
    ).hexdigest()
    checkpoints = output / "checkpoints"
    checkpoints.mkdir(exist_ok=True)
    rows, previous, completed = _load_blocks(checkpoints, binding=binding)
    total = int(protocol["resampling"]["replicates"])
    block_size = int(protocol["resampling"]["checkpoint_block_replicates"])
    while completed < total:
        stop = min(completed + block_size, total)
        block = [
            _bootstrap_record(raw, replicate=index, seed=int(protocol["resampling"]["seed"]))
            for index in range(completed, stop)
        ]
        item = {
            "schema_version": CHECKPOINT_SCHEMA,
            "binding_sha256": binding,
            "start": completed,
            "stop": stop,
            "replicates": block,
            "previous_checkpoint_sha256": previous,
        }
        path = checkpoints / f"block_{completed:04d}_{stop:04d}.json"
        write_once_or_equal(path, canonical_json_bytes(item))
        previous = _checkpoint_hash(item)
        rows.extend(block)
        completed = stop
        if progress:
            progress({"event": "checkpoint", "completed": completed, "total": total, "path": str(path), "sha256": previous})
    graph_rows = []
    for key, summary in observed.items():
        cycle_rows = []
        for cycle in summary["cycles"]:
            values = [row["graphs"][key]["cycle_budgets"][cycle["cycle_id"]] for row in rows]
            interval = _interval(values, cycle["conservative_angle_budget_degrees"])
            cycle_rows.append(
                {
                    **cycle,
                    "angle_budget_interval": interval,
                    "frustration_margin_interval": {
                        "point": cycle["frustration_margin_degrees"],
                        "lower_descriptive_90": 180.0 - float(interval["upper_descriptive_90"]),
                        "upper_descriptive_90": 180.0 - float(interval["lower_descriptive_90"]),
                        "coverage_claim": interval["coverage_claim"],
                    },
                    "forced_orientable_with_90_support": float(interval["upper_descriptive_90"]) < 180.0,
                }
            )
        max_values = [row["graphs"][key]["maximum_angle_budget_degrees"] for row in rows]
        max_interval = _interval(max_values, summary["maximum_angle_budget_degrees"])
        graph_rows.append(
            {
                "graph_id": key,
                "precision": key.split("|")[0],
                "site": key.split("|")[1],
                "cycles": cycle_rows,
                "maximum_simple_cycle_id": summary["maximum_simple_cycle_id"],
                "maximum_angle_budget_interval": max_interval,
                "minimum_frustration_margin_interval": {
                    "point": summary["minimum_frustration_margin_degrees"],
                    "lower_descriptive_90": 180.0 - float(max_interval["upper_descriptive_90"]),
                    "upper_descriptive_90": 180.0 - float(max_interval["lower_descriptive_90"]),
                    "coverage_claim": max_interval["coverage_claim"],
                },
                "forced_orientable_with_90_support": float(max_interval["upper_descriptive_90"]) < 180.0,
                "gauge_preflight": gauges[key],
            }
        )
    graph_by_id = {row["graph_id"]: row for row in graph_rows}
    erosions = []
    erosion_established = False
    for site in scientific["sites"]:
        four_key, full_key = f"4bit|{site}", f"float16|{site}"
        values = [
            row["graphs"][four_key]["maximum_angle_budget_degrees"]
            - row["graphs"][full_key]["maximum_angle_budget_degrees"]
            for row in rows
        ]
        point = (
            float(graph_by_id[four_key]["maximum_angle_budget_interval"]["point"])
            - float(graph_by_id[full_key]["maximum_angle_budget_interval"]["point"])
        )
        interval = _interval(values, point)
        float_margin = float(graph_by_id[full_key]["minimum_frustration_margin_interval"]["point"])
        established = float(interval["lower_descriptive_90"]) > 0.0
        erosion_established |= established
        matched = []
        four_cycles = {row["cycle_id"]: row for row in graph_by_id[four_key]["cycles"]}
        full_cycles = {row["cycle_id"]: row for row in graph_by_id[full_key]["cycles"]}
        for cycle_id in sorted(four_cycles):
            cycle_values = [
                row["graphs"][four_key]["cycle_budgets"][cycle_id]
                - row["graphs"][full_key]["cycle_budgets"][cycle_id]
                for row in rows
            ]
            cycle_point = four_cycles[cycle_id]["conservative_angle_budget_degrees"] - full_cycles[cycle_id]["conservative_angle_budget_degrees"]
            matched.append({"cycle_id": cycle_id, **_interval(cycle_values, cycle_point)})
        erosions.append(
            {
                "site": site,
                "contrast": "max_angle_budget_4bit_minus_float16",
                **interval,
                "relative_erosion_point": point / float_margin if float_margin > 0 else None,
                "quantization_erosion_established": established,
                "matched_cycle_erosions": matched,
            }
        )
    gauge_valid = all(row["gauge_preflight"]["passed"] for row in graph_rows)
    forcing = all(row["forced_orientable_with_90_support"] for row in graph_rows)
    if not gauge_valid:
        category = "invalid_gauge_instrument"
    elif forcing:
        category = "w1_forced_orientable_all_graphs"
    else:
        category = "w1_liveness_not_uniformly_bounded"
    result = {
        "schema_version": RESULT_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "protocol_sha256": sha256_file(protocol_path),
        "filtration_result_sha256": sha256_file(filtration_result_path),
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "graphs": graph_rows,
        "quantization_erosions": erosions,
        "quantization_erosion_established_any_site": erosion_established,
        "result_category": category,
        "superseded_interpretation": "Positive w1 signs in the parent analysis are forcing consequences, not empirical evidence of precision-stable holonomy.",
        "claim_boundary": protocol["reporting"]["claim_boundary"],
    }
    write_once_or_equal(output / "analysis_result.json", canonical_json_bytes(result))
    return result
