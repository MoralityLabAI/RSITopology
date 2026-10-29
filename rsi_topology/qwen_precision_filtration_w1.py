"""Outcome-free precision filtration and rank-one w1 analysis.

The graph is the frozen 2-state x 4-context ladder at one physical site.  All
ten edge receipts are retained before thresholding.  Rank-one loop signs are
evaluations of the Z/2 edge cochain on the complete nonzero cycle space.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from .bifiltration import build_lineage_holonomy_bifiltration
from .discovery import _between_class_scatter_basis
from .godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal
from .qwen_precision_context import (
    HALVES,
    PRECISIONS,
    STATES,
    _node_features,
    _stable_seed,
    _stratified_bootstrap_indices,
    build_pair_store,
    load_protocol as load_parent_protocol,
    validate_manifest,
)


PROTOCOL_ID = "qwen08_precision_filtration_w1_v0_1"
RESULT_SCHEMA = "qwen08_precision_filtration_w1_result_v0_1"
CHECKPOINT_SCHEMA = "qwen08_precision_filtration_w1_checkpoint_v0_1"


def load_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("unexpected filtration/w1 protocol")
    if value.get("status") != "registered_not_run":
        raise ValueError("filtration/w1 protocol is not prereveal")
    if value.get("outcomes_consumed") is not False:
        raise ValueError("filtration/w1 protocol is not outcome-free")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("filtration/w1 protocol adds an invariant level")
    return value


def _basis(features: np.ndarray, labels: np.ndarray, halves: np.ndarray) -> dict[str, np.ndarray]:
    result = {}
    for half in HALVES:
        mask = halves == half
        value, _ = _between_class_scatter_basis(features[mask], labels[mask], 1)
        result[half] = np.asarray(value[:, 0], dtype=np.float64)
    return result


def _edge_id_context(state: str, column: int) -> str:
    return f"context:{state}:{column:02d}-{column + 1:02d}"


def _edge_id_state(column: int) -> str:
    return f"state:base-naive_qlora:{column:02d}"


def _node_id(state: str, shard: str) -> str:
    return f"{state}/{shard}"


def _edge_specs() -> dict[str, tuple[tuple[str, str], tuple[str, str]]]:
    edges = {}
    for state in STATES:
        for column in range(3):
            edges[_edge_id_context(state, column)] = (
                (state, f"shard-{column:02d}"),
                (state, f"shard-{column + 1:02d}"),
            )
    for column in range(4):
        edges[_edge_id_state(column)] = (
            ("base", f"shard-{column:02d}"),
            ("naive_qlora", f"shard-{column:02d}"),
        )
    return edges


def _plaquette_edges(column: int) -> frozenset[str]:
    return frozenset(
        (
            _edge_id_context("base", column),
            _edge_id_state(column + 1),
            _edge_id_context("naive_qlora", column),
            _edge_id_state(column),
        )
    )


def cycle_space() -> tuple[dict[str, Any], ...]:
    rows = []
    for mask in range(1, 8):
        generators = tuple(index for index in range(3) if mask & (1 << index))
        boundary: set[str] = set()
        for index in generators:
            boundary.symmetric_difference_update(_plaquette_edges(index))
        connected = generators != (0, 2)
        rows.append(
            {
                "cycle_id": "xor:" + "+".join(f"p{index}" for index in generators),
                "generator_indices": list(generators),
                "edge_ids": sorted(boundary),
                "edge_count": len(boundary),
                "connected_simple_loop": connected,
            }
        )
    return tuple(rows)


@dataclass(frozen=True)
class GraphMeasurement:
    edges: tuple[dict[str, Any], ...]
    cycles: tuple[dict[str, Any], ...]
    filtration: tuple[dict[str, Any], ...]
    tau_conn: float
    tau_cycle: float
    tau_loop: float


def _sign(value: float) -> int:
    if not np.isfinite(value) or abs(value) <= 1e-14:
        raise ValueError("rank-one transport is numerically singular")
    return 1 if value > 0.0 else -1


def measure_graph(bases: Mapping[tuple[str, str], Mapping[str, np.ndarray]]) -> GraphMeasurement:
    edge_rows = []
    for edge_id, (source, target) in sorted(_edge_specs().items()):
        overlaps = {
            half: float(np.dot(bases[source][half], bases[target][half]))
            for half in HALVES
        }
        edge_rows.append(
            {
                "edge_id": edge_id,
                "source_node": _node_id(*source),
                "target_node": _node_id(*target),
                "construction_overlap": overlaps["construction"],
                "geometry_validation_overlap": overlaps["geometry_validation"],
                "construction_sign": _sign(overlaps["construction"]),
                "geometry_validation_sign": _sign(overlaps["geometry_validation"]),
                "lineage": min(value * value for value in overlaps.values()),
            }
        )
    edge_by_id = {row["edge_id"]: row for row in edge_rows}
    cycles = []
    for spec in cycle_space():
        signs = {
            half: int(np.prod([edge_by_id[edge_id][f"{half}_sign"] for edge_id in spec["edge_ids"]]))
            for half in HALVES
        }
        bottleneck = min(edge_by_id[edge_id]["lineage"] for edge_id in spec["edge_ids"])
        cycles.append(
            {
                **spec,
                "construction_sign": signs["construction"],
                "geometry_validation_sign": signs["geometry_validation"],
                "construction_validation_agreement": signs["construction"] == signs["geometry_validation"],
                "lineage_bottleneck": float(bottleneck),
                "orientation_flag": signs["geometry_validation"] < 0,
                "det_h": float(signs["geometry_validation"]),
                "canonical_angles_degrees": None,
            }
        )
    nodes = [_node_id(state, f"shard-{column:02d}") for state in STATES for column in range(4)]
    simple = [row for row in cycles if row["connected_simple_loop"]]
    thresholds = sorted(
        {0.0, 0.5, 0.9, 1.0, *[float(row["lineage"]) for row in edge_rows]},
        reverse=True,
    )
    filtration = []
    for tau in thresholds:
        value = build_lineage_holonomy_bifiltration(
            edges=edge_rows,
            lineage_floor=tau,
            loops=[{"loop_id": row["cycle_id"], "edge_ids": row["edge_ids"]} for row in simple],
            registered_nodes=nodes,
        )
        filtration.append(
            {
                "tau": float(tau),
                "admitted_edge_count": value.admitted_edge_count,
                "component_count": value.connected_component_count,
                "beta_1": value.beta_1,
                "admitted_simple_loop_count": len(value.admitted_loop_ids),
            }
        )

    def maximum(predicate: Callable[[Mapping[str, Any]], bool]) -> float:
        eligible = [row["tau"] for row in filtration if predicate(row)]
        if not eligible:
            raise ValueError("full frozen graph failed to reach a required filtration state")
        return float(max(eligible))

    return GraphMeasurement(
        edges=tuple(edge_rows),
        cycles=tuple(cycles),
        filtration=tuple(filtration),
        tau_conn=maximum(lambda row: row["component_count"] == 1),
        tau_cycle=maximum(lambda row: row["beta_1"] > 0),
        tau_loop=maximum(lambda row: row["admitted_simple_loop_count"] > 0),
    )


def gauge_preflight(
    graph: GraphMeasurement, *, reframings: int, seed: int
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    nodes = sorted(
        {row["source_node"] for row in graph.edges}
        | {row["target_node"] for row in graph.edges}
    )
    edge_by_id = {row["edge_id"]: row for row in graph.edges}
    expected = {row["cycle_id"]: row["geometry_validation_sign"] for row in graph.cycles}
    mismatches = 0
    for _ in range(reframings):
        flips = {node: int(rng.choice((-1, 1))) for node in nodes}
        reframed = {
            edge_id: flips[row["source_node"]]
            * int(row["geometry_validation_sign"])
            * flips[row["target_node"]]
            for edge_id, row in edge_by_id.items()
        }
        for cycle in graph.cycles:
            observed = int(np.prod([reframed[edge_id] for edge_id in cycle["edge_ids"]]))
            mismatches += int(observed != expected[cycle["cycle_id"]])
    return {
        "reframings": reframings,
        "cycle_decisions_checked": reframings * len(graph.cycles),
        "determinant_decision_mismatches": mismatches,
        "passed": mismatches == 0,
    }


def _checkpoint_hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _load_blocks(
    directory: Path, *, binding: str
) -> tuple[list[dict[str, Any]], str | None, int]:
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


def _resampled_bases(
    raw: Mapping[tuple[str, str, str, str], tuple[np.ndarray, np.ndarray, np.ndarray]],
    *,
    replicate_seed: int,
) -> dict[tuple[str, str, str, str], dict[str, np.ndarray]]:
    first = next(iter(raw.values()))
    rng = np.random.default_rng(replicate_seed)
    indices = _stratified_bootstrap_indices(first[1], first[2], rng)
    result = {}
    for key, (features, labels, halves) in raw.items():
        result[key] = _basis(features[indices], labels[indices], halves[indices])
    return result


def _bootstrap_record(
    raw: Mapping[tuple[str, str, str, str], tuple[np.ndarray, np.ndarray, np.ndarray]],
    *,
    replicate: int,
    seed: int,
) -> dict[str, Any]:
    all_bases = _resampled_bases(raw, replicate_seed=_stable_seed(seed, "filtration-w1", str(replicate)))
    graphs = {}
    for precision in PRECISIONS:
        for site in ("model.layers.19", "model.layers.23"):
            bases = {
                (state, shard): all_bases[(precision, state, site, shard)]
                for state in STATES
                for shard in ("shard-00", "shard-01", "shard-02", "shard-03")
            }
            measured = measure_graph(bases)
            graphs[f"{precision}|{site}"] = {
                "tau_conn": measured.tau_conn,
                "tau_cycle": measured.tau_cycle,
                "tau_loop": measured.tau_loop,
                "cycle_signs": {
                    row["cycle_id"]: row["geometry_validation_sign"]
                    for row in measured.cycles
                },
            }
    return {"replicate": replicate, "graphs": graphs}


def _interval(values: Sequence[float], observed: float) -> dict[str, float]:
    array = np.asarray([*values, observed], dtype=np.float64)
    return {
        "point": float(observed),
        "lower_90": float(np.quantile(array, 0.05, method="linear")),
        "upper_90": float(np.quantile(array, 0.95, method="linear")),
    }


def analyze(
    *,
    protocol_path: str | Path,
    parent_protocol_path: str | Path,
    manifest_path: str | Path,
    parent_result_path: str | Path,
    fourbit_indices: Mapping[str, str | Path],
    float16_indices: Mapping[str, str | Path],
    output_dir: str | Path,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    protocol_path = Path(protocol_path).resolve()
    parent_protocol_path = Path(parent_protocol_path).resolve()
    manifest_path = Path(manifest_path).resolve()
    parent_result_path = Path(parent_result_path).resolve()
    protocol = load_protocol(protocol_path)
    parent_protocol = load_parent_protocol(parent_protocol_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    validate_manifest(manifest, protocol_path=parent_protocol_path)
    parent_result = json.loads(parent_result_path.read_text(encoding="utf-8-sig"))
    parent_lock = protocol["parent"]
    for observed, expected, label in (
        (sha256_file(parent_protocol_path), parent_lock["scientific_protocol_sha256"], "parent protocol"),
        (sha256_file(manifest_path), parent_lock["prompt_manifest_sha256"], "prompt manifest"),
        (sha256_file(parent_result_path), parent_lock["completed_analysis_result_sha256"], "parent result"),
    ):
        if observed != expected:
            raise ValueError(f"{label} hash differs")
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    stores = {
        "4bit": build_pair_store(
            protocol_path=parent_protocol_path,
            manifest_path=manifest_path,
            precision="4bit",
            state_index_paths=fourbit_indices,
            output_dir=output / "fourbit",
        ),
        "float16": build_pair_store(
            protocol_path=parent_protocol_path,
            manifest_path=manifest_path,
            precision="float16",
            state_index_paths=float16_indices,
            output_dir=output / "float16",
        ),
    }
    raw = {}
    observed_bases = {}
    for precision, store in stores.items():
        for state in STATES:
            for site in parent_protocol["sites"]:
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
    reference_labels = next(iter(raw.values()))[1]
    reference_halves = next(iter(raw.values()))[2]
    for key, (_, labels, halves) in raw.items():
        if not np.array_equal(labels, reference_labels) or not np.array_equal(
            halves, reference_halves
        ):
            raise ValueError(f"paired prompt strata differ at {key}")
    observed_graphs: dict[str, GraphMeasurement] = {}
    gauge = {}
    for precision in PRECISIONS:
        for site in parent_protocol["sites"]:
            key = f"{precision}|{site}"
            measured = measure_graph(
                {
                    (state, shard): observed_bases[(precision, state, site, shard)]
                    for state in STATES
                    for shard in ("shard-00", "shard-01", "shard-02", "shard-03")
                }
            )
            observed_graphs[key] = measured
            gauge[key] = gauge_preflight(
                measured,
                reframings=int(protocol["gauge_preflight"]["reframings"]),
                seed=_stable_seed(int(protocol["gauge_preflight"]["seed"]), precision, site),
            )
    binding = hashlib.sha256(
        canonical_json_bytes(
            {
                "protocol_sha256": sha256_file(protocol_path),
                "parent_result_sha256": sha256_file(parent_result_path),
                "pair_indices": {
                    "4bit": sha256_file(stores["4bit"].index_path),
                    "float16": sha256_file(stores["float16"].index_path),
                },
            }
        )
    ).hexdigest()
    checkpoints = output / "checkpoints"
    checkpoints.mkdir(exist_ok=True)
    rows, previous, completed = _load_blocks(checkpoints, binding=binding)
    total = int(protocol["resampling"]["replicates"])
    block_size = 16
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
    reproducibility_gate = float(protocol["resampling"]["reproducible_sign_gate"])
    for key, observed in observed_graphs.items():
        tau_samples = {
            name: [float(row["graphs"][key][name]) for row in rows]
            for name in ("tau_conn", "tau_cycle", "tau_loop")
        }
        cycles = []
        for cycle in observed.cycles:
            signs = [int(row["graphs"][key]["cycle_signs"][cycle["cycle_id"]]) for row in rows]
            agreement = float(np.mean(np.asarray(signs) == cycle["geometry_validation_sign"]))
            cycles.append(
                {
                    **cycle,
                    "bootstrap_sign_agreement": agreement,
                    "reproducible_sign": agreement >= reproducibility_gate,
                }
            )
        tau_cycle_interval = _interval(tau_samples["tau_cycle"], observed.tau_cycle)
        floor = float(protocol["graph"]["frozen_lineage_floor"])
        if tau_cycle_interval["lower_90"] <= floor <= tau_cycle_interval["upper_90"]:
            fragility = "critical_surface_overlap"
        elif tau_cycle_interval["upper_90"] < floor:
            fragility = "robustly_below_floor"
        else:
            fragility = "robustly_above_floor"
        graph_rows.append(
            {
                "graph_id": key,
                "precision": key.split("|")[0],
                "site": key.split("|")[1],
                "edges": list(observed.edges),
                "cycles": cycles,
                "filtration": list(observed.filtration),
                "tau_conn": _interval(tau_samples["tau_conn"], observed.tau_conn),
                "tau_cycle": tau_cycle_interval,
                "tau_loop": _interval(tau_samples["tau_loop"], observed.tau_loop),
                "fragility_margin_point": abs(floor - observed.tau_cycle),
                "fragility_classification": fragility,
                "gauge_preflight": gauge[key],
            }
        )
    graph_by_id = {row["graph_id"]: row for row in graph_rows}
    deltas = []
    percolation_shift = False
    for site in parent_protocol["sites"]:
        values = [
            float(row["graphs"][f"float16|{site}"]["tau_cycle"])
            - float(row["graphs"][f"4bit|{site}"]["tau_cycle"])
            for row in rows
        ]
        point = observed_graphs[f"float16|{site}"].tau_cycle - observed_graphs[f"4bit|{site}"].tau_cycle
        interval = _interval(values, point)
        interval["site"] = site
        interval["contrast"] = "tau_cycle_float16_minus_4bit"
        interval["excludes_zero"] = interval["lower_90"] > 0 or interval["upper_90"] < 0
        percolation_shift |= bool(interval["excludes_zero"])
        deltas.append(interval)
    gauge_valid = all(row["gauge_preflight"]["passed"] for row in graph_rows)
    quantization_sensitive = False
    thin_candidates = []
    for site in parent_protocol["sites"]:
        four = {row["cycle_id"]: row for row in graph_by_id[f"4bit|{site}"]["cycles"]}
        full = {row["cycle_id"]: row for row in graph_by_id[f"float16|{site}"]["cycles"]}
        for cycle_id in sorted(four):
            a, b = four[cycle_id], full[cycle_id]
            if not a["connected_simple_loop"]:
                continue
            eligible = min(a["lineage_bottleneck"], b["lineage_bottleneck"]) >= 0.5
            if eligible:
                thin_candidates.append((a, b))
            quantization_sensitive |= bool(
                eligible
                and a["reproducible_sign"]
                and b["reproducible_sign"]
                and a["construction_validation_agreement"]
                and b["construction_validation_agreement"]
                and a["geometry_validation_sign"] == -1
                and b["geometry_validation_sign"] == 1
            )
    thin = bool(thin_candidates) and all(
        a["reproducible_sign"]
        and b["reproducible_sign"]
        and a["construction_validation_agreement"]
        and b["construction_validation_agreement"]
        and a["geometry_validation_sign"] == 1
        and b["geometry_validation_sign"] == 1
        for a, b in thin_candidates
    )
    if not gauge_valid:
        category = "invalid_gauge_instrument"
    elif quantization_sensitive:
        category = "quantization_sensitive_w1"
    elif thin:
        category = "precision_stable_diagnostically_thin"
    else:
        category = "inconclusive"
    result = {
        "schema_version": RESULT_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "protocol_sha256": sha256_file(protocol_path),
        "parent_result_sha256": sha256_file(parent_result_path),
        "prompt_manifest_sha256": sha256_file(manifest_path),
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "graphs": graph_rows,
        "tau_cycle_precision_contrasts": deltas,
        "percolation_shift_established": percolation_shift,
        "w1_category": category,
        "support_records": parent_result["support_records"],
        "paired_precision_records": parent_result["paired_precision_records"],
        "sentinel_interaction": parent_result["sentinel_interaction"],
        "claim_boundary": protocol["evidence_discipline"]["claim_boundary"],
    }
    write_once_or_equal(output / "analysis_result.json", canonical_json_bytes(result))
    return result
