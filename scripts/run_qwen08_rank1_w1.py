"""Run the sealed retrospective rank-one Stiefel--Whitney reanalysis."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_analysis import _family_indices
from rsi_topology.godel_capture import (
    canonical_json_bytes,
    sha256_file,
    write_once_or_equal,
)
from rsi_topology.qwen_geometry_analysis import (
    build_pair_store,
    validate_registered_inputs,
)
from rsi_topology.rank1_w1 import (
    LoopInterval,
    bootstrap_rank_one_basis,
    clopper_pearson,
    exact_uniform_class_probability,
    gf2_rank,
    permuted_rank_one_basis,
    predict_composite_sign,
    rank_one_between_class_basis,
    rectangular_loop_sign,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ID = "qwen08_rank1_w1_reanalysis_v0_1"


def _resolve(raw: str, *, root: Path) -> Path:
    value = Path(raw)
    return value.resolve() if value.is_absolute() else (root / value).resolve()


def _load_protocol(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("unexpected rank-one w1 protocol")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("rank-one reanalysis introduces an invariant level")
    if value.get("epistemic_status") != "retrospective_reanalysis_not_a_new_confirmatory_preregistration":
        raise ValueError("rank-one reanalysis must preserve retrospective status")
    return value


def _validate_bound(entry: Mapping[str, Any], *, root: Path) -> Path:
    path = _resolve(str(entry["path"]), root=root)
    if sha256_file(path) != str(entry["sha256"]).lower():
        raise ValueError(f"bound artifact hash mismatch: {path}")
    return path


def _site_number(site: str) -> str:
    return site.split(".")[-1]


def _admitted_generator_count(result: Mapping[str, Any], site: str) -> int:
    matches = [
        graph for graph in result["graphs"]
        if graph["site"] == site and graph["family"] == "graph_reachability"
    ]
    if len(matches) != 1 or int(matches[0]["rank"]) != 1:
        raise ValueError(f"missing unique rank-one graph for {site}")
    graph = matches[0]
    beta_one = int(graph["bifiltration"]["beta_1"])
    admitted = graph["bifiltration"]["admitted_loop_ids"]
    indices = sorted(int(str(value).rsplit("-", 1)[-1]) for value in admitted)
    if indices != list(range(beta_one)):
        raise ValueError(f"{site} admitted loops are not the registered prefix")
    return beta_one


def _raw_nodes(store, manifest, site: str) -> dict[tuple[str, str, int], tuple[np.ndarray, np.ndarray]]:
    output = {}
    for half in ("construction", "geometry_validation"):
        for state in ("base", "naive_qlora"):
            for shard_index in range(4):
                shard = f"shard-{shard_index:02d}"
                values = store.load(state, site, shard, half)
                indices, labels = _family_indices(
                    manifest,
                    shard=shard,
                    half=half,
                    family="graph_reachability",
                )
                output[(half, state, shard_index)] = (values[indices], labels)
    return output


def _point_bases(raw, *, half: str, dtype) -> dict[tuple[str, int], np.ndarray]:
    return {
        (state, shard): rank_one_between_class_basis(
            *raw[(half, state, shard)], dtype=dtype
        )
        for state in ("base", "naive_qlora")
        for shard in range(4)
    }


def _draw_bases(raw, *, half: str, rng: np.random.Generator, permuted: bool):
    builder = permuted_rank_one_basis if permuted else bootstrap_rank_one_basis
    return {
        (state, shard): builder(*raw[(half, state, shard)], rng, dtype=np.float64)
        for state in ("base", "naive_qlora")
        for shard in range(4)
    }


def _loop_signs(bases, generator_count: int) -> list[int]:
    return [
        rectangular_loop_sign(
            bases,
            states=("base", "naive_qlora"),
            interval=LoopInterval(index, index + 1),
        )
        for index in range(generator_count)
    ]


def _composite_sign(bases, interval: LoopInterval) -> int:
    return rectangular_loop_sign(
        bases,
        states=("base", "naive_qlora"),
        interval=interval,
    )


def _stable_seed(seed: int, *parts: str) -> int:
    digest = hashlib.sha256("\0".join(parts).encode("utf-8")).digest()
    return (seed + int.from_bytes(digest[:4], "big")) % (2**32)


def _analyze_site(raw, *, site: str, generator_count: int, intervals, replicates: int, seed: int):
    point: dict[str, dict[str, Any]] = {}
    precision_signs: dict[str, Any] = {}
    for dtype_name, dtype in (("float32", np.float32), ("float64", np.float64)):
        by_half = {
            half: _point_bases(raw, half=half, dtype=dtype)
            for half in ("construction", "geometry_validation")
        }
        precision_signs[dtype_name] = {
            half: {
                "generators": _loop_signs(by_half[half], generator_count),
                "composites": [
                    _composite_sign(by_half[half], interval) for interval in intervals
                ],
            }
            for half in by_half
        }
    precision_agreement = precision_signs["float32"] == precision_signs["float64"]
    full = precision_signs["float64"]
    for index, interval in enumerate(intervals):
        predicted = predict_composite_sign(full["construction"]["generators"], interval)
        observed = full["geometry_validation"]["composites"][index]
        point[f"{interval.start}-{interval.stop}"] = {
            "interval": [interval.start, interval.stop],
            "constraint_vector": [
                int(interval.start <= value < interval.stop)
                for value in range(generator_count)
            ],
            "construction_prediction": predicted,
            "geometry_validation_observation": observed,
            "prediction_hit": predicted == observed,
        }

    counts = {
        key: {"prediction": 0, "construction": 0, "validation": 0, "null": 0}
        for key in point
    }
    full_construction = full["construction"]["generators"]
    full_validation = full["geometry_validation"]["composites"]
    for replicate in range(replicates):
        observed_rng = np.random.default_rng(
            _stable_seed(seed, site, "observed", str(replicate))
        )
        construction = _draw_bases(
            raw, half="construction", rng=observed_rng, permuted=False
        )
        validation = _draw_bases(
            raw, half="geometry_validation", rng=observed_rng, permuted=False
        )
        construction_signs = _loop_signs(construction, generator_count)
        null_rng = np.random.default_rng(
            _stable_seed(seed, site, "permutation", str(replicate))
        )
        null_construction = _draw_bases(
            raw, half="construction", rng=null_rng, permuted=True
        )
        null_validation = _draw_bases(
            raw, half="geometry_validation", rng=null_rng, permuted=True
        )
        null_generators = _loop_signs(null_construction, generator_count)
        for index, interval in enumerate(intervals):
            key = f"{interval.start}-{interval.stop}"
            predicted = predict_composite_sign(construction_signs, interval)
            actual = _composite_sign(validation, interval)
            counts[key]["prediction"] += int(predicted == actual)
            included = range(interval.start, interval.stop)
            counts[key]["construction"] += int(
                all(construction_signs[value] == full_construction[value] for value in included)
            )
            counts[key]["validation"] += int(actual == full_validation[index])
            null_prediction = predict_composite_sign(null_generators, interval)
            null_actual = _composite_sign(null_validation, interval)
            counts[key]["null"] += int(null_prediction == null_actual)

    all_gates = True
    for key, values in counts.items():
        intervals_by_kind = {
            name: clopper_pearson(successes, replicates)
            for name, successes in values.items()
        }
        passed = (
            point[key]["prediction_hit"]
            and intervals_by_kind["prediction"][0] >= 0.95
            and intervals_by_kind["construction"][0] >= 0.95
            and intervals_by_kind["validation"][0] >= 0.95
            and intervals_by_kind["prediction"][0]
            > intervals_by_kind["null"][1] + 0.02
        )
        point[key]["resampling"] = {
            name: {
                "successes": values[name],
                "trials": replicates,
                "clopper_pearson_95": list(intervals_by_kind[name]),
            }
            for name in values
        }
        point[key]["derived_diagnostic_passed"] = passed
        all_gates = all_gates and passed
    construction_w1_zero = all(value == 1 for value in full["construction"]["generators"])
    validation_w1_zero = all(value == 1 for value in full["geometry_validation"]["generators"])
    return {
        "site": site,
        "beta_1": generator_count,
        "point_signs_by_analysis_precision": precision_signs,
        "analysis_precision_sign_agreement": precision_agreement,
        "construction_w1_zero": construction_w1_zero,
        "geometry_validation_w1_zero": validation_w1_zero,
        "line_bundle_status": (
            "orientable_trivializable_on_admitted_graph"
            if construction_w1_zero and validation_w1_zero
            else "nonzero_first_stiefel_whitney_class"
        ),
        "composite_checks": list(point.values()),
        "all_derived_diagnostics_passed": all_gates and precision_agreement,
    }


def _comparator(protocol: Mapping[str, Any], root: Path) -> dict[str, Any]:
    entry = protocol["retrospective_vpd_comparator"]
    receipt_path = _resolve(entry["receipt_path"], root=root)
    predictor_path = Path(entry["predictor_path"]).resolve()
    if sha256_file(receipt_path) != entry["receipt_sha256"]:
        raise ValueError("VPD comparator receipt hash mismatch")
    if sha256_file(predictor_path) != entry["predictor_sha256"]:
        raise ValueError("VPD comparator predictor hash mismatch")
    table = pd.read_parquet(predictor_path)
    first = table["det_h_negative_split_a"].astype(bool).to_numpy()
    second = table["det_h_negative_split_b"].astype(bool).to_numpy()
    return {
        "object": entry["object"],
        "epistemic_status": "retrospective_already_revealed_comparator",
        "rows": int(len(table)),
        "split_a_orientation_reversals": int(np.sum(first)),
        "split_b_orientation_reversals": int(np.sum(second)),
        "split_sign_agreement_count": int(np.sum(first == second)),
        "split_sign_agreement_rate": float(np.mean(first == second)),
        "stable_orientation_reversals": int(np.sum(first & second)),
        "stable_orientation_preserving": int(np.sum(~first & ~second)),
        "allowed_claim": entry["allowed_claim"],
    }


def _report(result: Mapping[str, Any]) -> str:
    rows = []
    for site in result["sites"]:
        rows.append(
            f"| {site['site']} | {site['beta_1']} | "
            f"{site['point_signs_by_analysis_precision']['float64']['geometry_validation']['generators']} | "
            f"{site['line_bundle_status']} | {site['all_derived_diagnostics_passed']} |"
        )
    comparator = result["retrospective_vpd_comparator"]
    return "\n".join(
        [
            "# Qwen0.8B rank-one sign-holonomy reanalysis",
            "",
            "> **Epistemic status:** retrospective reanalysis, not a new confirmatory preregistration. The earlier analysis had already revealed every elementary validation-loop sign, so composite signs are derived checks, not fresh held-out discoveries.",
            "",
            "## Result",
            "",
            "| Site | beta1 | validation generator signs | line-bundle result | derived diagnostics |",
            "|---|---:|---|---|---|",
            *rows,
            "",
            f"The registered composite constraints have total GF(2) rank **{result['total_constraint_rank']}**. "
            f"Conditional on all point predictions hitting, the descriptive uniform-class probability is **{result['descriptive_uniform_class_probability']}**. "
            "This is not reported as a confirmatory p-value because the elementary target signs were already known.",
            "",
            "Float32-versus-float64 refers only to analysis arithmetic over the same stored activation arrays. The model was captured once through a 4-bit runtime, so model-runtime precision stability remains unavailable.",
            "",
            "## Retrospective comparator",
            "",
            f"The separate **{comparator['object']}** has {comparator['stable_orientation_reversals']}/{comparator['rows']} stable orientation-reversing split evaluations and split-sign agreement {comparator['split_sign_agreement_count']}/{comparator['rows']}. "
            "It is not a natural-feature line bundle, and no complete w1 classification is claimed without its bound cycle basis.",
            "",
            "## Claim boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )


def run(protocol_path: Path, output_dir: Path) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    protocol = _load_protocol(protocol_path)
    dense_registration = _validate_bound(protocol["dense_analysis_registration"], root=ROOT)
    dense_result_path = _validate_bound(protocol["dense_analysis_result"], root=ROOT)
    dense_result = json.loads(dense_result_path.read_text(encoding="utf-8"))
    registration, _, manifest, state_paths = validate_registered_inputs(
        registration_path=dense_registration,
        repository_root=ROOT,
    )
    output_dir = output_dir.resolve()
    store = build_pair_store(
        registration=registration,
        registration_path=dense_registration,
        manifest=manifest,
        state_index_paths=state_paths,
        pair=("base", "naive_qlora"),
        output_dir=output_dir / "pair_view",
    )
    replicates = int(protocol["resampling"]["replicates"])
    seed = int(protocol["resampling"]["seed"])
    site_results = []
    total_rank = 0
    for site, raw_intervals in protocol["derived_composite_checks"]["registered_intervals_by_site"].items():
        generator_count = _admitted_generator_count(dense_result, site)
        intervals = [LoopInterval(*map(int, item)) for item in raw_intervals]
        rows = [
            [int(interval.start <= value < interval.stop) for value in range(generator_count)]
            for interval in intervals
        ]
        constraint_rank = gf2_rank(rows)
        total_rank += constraint_rank
        item = _analyze_site(
            _raw_nodes(store, manifest, site),
            site=site,
            generator_count=generator_count,
            intervals=intervals,
            replicates=replicates,
            seed=seed,
        )
        item["composite_constraint_rank"] = constraint_rank
        site_results.append(item)
    all_point_hits = all(
        check["prediction_hit"]
        for site in site_results
        for check in site["composite_checks"]
    )
    result = {
        "schema_version": "qwen08_rank1_w1_reanalysis_result_v0_1",
        "protocol_sha256": sha256_file(protocol_path),
        "dense_analysis_result_sha256": sha256_file(dense_result_path),
        "pair_capture_index_sha256": sha256_file(store.index_path),
        "epistemic_status": protocol["epistemic_status"],
        "sites": site_results,
        "total_constraint_rank": total_rank,
        "all_point_predictions_hit": all_point_hits,
        "descriptive_uniform_class_probability": (
            exact_uniform_class_probability(total_rank) if all_point_hits else None
        ),
        "all_analysis_precision_signs_stable": all(
            item["analysis_precision_sign_agreement"] for item in site_results
        ),
        "all_derived_diagnostics_passed": all(
            item["all_derived_diagnostics_passed"] for item in site_results
        ),
        "runtime_precision_status": protocol["precision"]["model_runtime_precision_status"],
        "retrospective_vpd_comparator": _comparator(protocol, ROOT),
        "claim_boundary": protocol["claim_boundary"],
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "new_invariant_levels": False,
    }
    write_once_or_equal(output_dir / "result.json", canonical_json_bytes(result))
    write_once_or_equal(output_dir / "REPORT.md", _report(result).encode("utf-8"))
    manifest_payload = {
        "schema_version": "qwen08_rank1_w1_release_manifest_v0_1",
        "files": {
            name: sha256_file(output_dir / name)
            for name in ("result.json", "REPORT.md", "pair_view/pair_capture_index.json")
        },
    }
    write_once_or_equal(
        output_dir / "release_manifest.json", canonical_json_bytes(manifest_payload)
    )
    return result


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument(
        "--protocol",
        type=Path,
        default=ROOT / "protocols" / "qwen08_rank1_w1_reanalysis_v0_1.json",
    )
    value.add_argument("--output-dir", type=Path, required=True)
    return value


def main() -> None:
    args = parser().parse_args()
    print(json.dumps(run(args.protocol, args.output_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
