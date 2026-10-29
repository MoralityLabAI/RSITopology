"""Exact-universe numerical census for the ASMP-2 active-design successor."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import subprocess
import time
import tracemalloc
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=text)


def bind_committed_inputs(paths: Sequence[Path]) -> dict[str, Any]:
    commit = git("rev-parse", "HEAD").stdout.strip()
    bindings = {}
    for path in paths:
        relative = path.resolve().relative_to(REPO_ROOT).as_posix()
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise ValueError(f"sealed input dirty or untracked: {relative}")
        payload = path.read_bytes()
        if git("show", f"HEAD:{relative}", text=False).stdout != payload:
            raise ValueError(f"sealed input differs from HEAD: {relative}")
        bindings[relative] = {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "git_blob": git("rev-parse", f"HEAD:{relative}").stdout.strip(),
        }
    tracked_diff_hash = hashlib.sha256(git("diff", "--binary", "HEAD", "--", text=False).stdout).hexdigest()
    if tracked_diff_hash != EMPTY_SHA256:
        raise ValueError("tracked diff is nonempty at run start")
    return {"commit": commit, "tracked_diff_sha256": tracked_diff_hash, "sealed_inputs": bindings}


def corners(dimension: int = 4) -> np.ndarray:
    return np.asarray(
        [[1 if (mask >> coordinate) & 1 else -1 for coordinate in range(dimension)] for mask in range(1 << dimension)],
        dtype=np.float64,
    )


def feature_matrix(points: np.ndarray) -> np.ndarray:
    dimension = points.shape[1]
    columns = [np.ones(points.shape[0], dtype=np.float64)]
    columns.extend(points[:, coordinate] for coordinate in range(dimension))
    columns.extend(points[:, left] * points[:, right] for left in range(dimension) for right in range(left + 1, dimension))
    return np.column_stack(columns)


def deployment_families(points: np.ndarray) -> dict[str, tuple[int, ...]]:
    return {
        "full_cube": tuple(range(points.shape[0])),
        "nonnegative_sum": tuple(index for index, point in enumerate(points) if point.sum() >= 0),
        "even_parity": tuple(index for index, point in enumerate(points) if int(np.prod(point)) == 1),
    }


def null_projector(rows: np.ndarray, feature_count: int, relative_tolerance: float) -> tuple[np.ndarray, int]:
    if rows.shape[0] == 0:
        return np.eye(feature_count), 0
    _u, singular_values, vt = np.linalg.svd(rows, full_matrices=True)
    threshold = relative_tolerance * singular_values[0] if singular_values.size else relative_tolerance
    rank = int(np.sum(singular_values > threshold))
    null_basis = vt[rank:, :].T
    projector = null_basis @ null_basis.T
    projector = (projector + projector.T) / 2
    return projector, rank


def score_mask(mask: int, features: np.ndarray, targets: Sequence[int], tolerance: float) -> tuple[float, int]:
    selected = [index for index in range(features.shape[0]) if (mask >> index) & 1]
    rows = features[selected, :] if selected else np.empty((0, features.shape[1]))
    projector, rank = null_projector(rows, features.shape[1], tolerance)
    target_features = features[list(targets), :]
    values = np.einsum("ij,jk,ik->i", target_features, projector, target_features)
    score = max(0.0, float(np.max(values)))
    if score < 1e-12:
        score = 0.0
    return score, rank


def score_projector(projector: np.ndarray, features: np.ndarray, targets: Sequence[int]) -> float:
    target_features = features[list(targets), :]
    values = np.einsum("ij,jk,ik->i", target_features, projector, target_features)
    score = max(0.0, float(np.max(values)))
    return 0.0 if score < 1e-12 else score


def exact_score(mask: int, feature_rows: list[list[int]], targets: Sequence[int]) -> sp.Rational:
    selected = [index for index in range(len(feature_rows)) if (mask >> index) & 1]
    feature_count = len(feature_rows[0])
    matrix = sp.Matrix([feature_rows[index] for index in selected]) if selected else sp.zeros(0, feature_count)
    basis = matrix.nullspace()
    if not basis:
        return sp.Rational(0)
    null_matrix = sp.Matrix.hstack(*basis)
    projector = null_matrix * (null_matrix.T * null_matrix).inv() * null_matrix.T
    values = []
    for target in targets:
        vector = sp.Matrix(feature_rows[target])
        values.append((vector.T * projector * vector)[0])
    return max(values)


def quantized(value: float, decimals: int) -> int:
    return int(round(value * (10 ** decimals)))


def exhaustive_census(protocol: dict[str, Any]) -> dict[str, Any]:
    dimension = int(protocol["dimension"])
    points = corners(dimension)
    features = feature_matrix(points)
    families = deployment_families(points)
    tolerance = float(protocol["numeric_contract"]["rank_relative_tolerance"])
    decimals = int(protocol["numeric_contract"]["score_round_decimals_for_ties_and_digest"])
    subset_count = 1 << points.shape[0]
    scores = {name: np.empty(subset_count, dtype=np.float64) for name in families}
    ranks = np.empty(subset_count, dtype=np.int16)
    digest = hashlib.sha256()
    for mask in range(subset_count):
        selected = [index for index in range(points.shape[0]) if (mask >> index) & 1]
        rows = features[selected, :] if selected else np.empty((0, features.shape[1]))
        projector, rank = null_projector(rows, features.shape[1], tolerance)
        row_values = []
        for name, targets in families.items():
            value = score_projector(projector, features, targets)
            scores[name][mask] = value
            row_values.append(quantized(value, decimals))
        ranks[mask] = int(rank)
        digest.update(f"{mask}|{rank}|{'|'.join(map(str, row_values))}\n".encode())
    return {
        "points": points,
        "features": features,
        "families": families,
        "scores": scores,
        "ranks": ranks,
        "digest": digest.hexdigest(),
    }


def best_mask_at_budget(values: np.ndarray, budget: int, decimals: int) -> int:
    candidates = (mask for mask in range(values.size) if mask.bit_count() == budget)
    return min(candidates, key=lambda mask: (quantized(float(values[mask]), decimals), mask))


def greedy_curve(values: np.ndarray, budgets: Sequence[int], decimals: int) -> list[dict[str, Any]]:
    mask = 0
    records = []
    for budget in budgets:
        if budget != mask.bit_count() + 1:
            raise ValueError("budgets must be consecutive from one")
        candidates = (index for index in range(16) if not ((mask >> index) & 1))
        selected = min(candidates, key=lambda index: (quantized(float(values[mask | (1 << index)]), decimals), index))
        mask |= 1 << selected
        records.append({"budget": budget, "selected_environment": selected, "mask": mask, "radius_squared": float(values[mask])})
    return records


def space_filling_masks(budgets: Sequence[int]) -> list[dict[str, int]]:
    selected: list[int] = []
    records = []
    mask = 0
    for budget in budgets:
        if not selected:
            chosen = 0
        else:
            candidates = [candidate for candidate in range(16) if candidate not in selected]
            chosen = min(candidates, key=lambda candidate: (-min((candidate ^ prior).bit_count() for prior in selected), candidate))
        selected.append(chosen)
        mask |= 1 << chosen
        records.append({"budget": budget, "selected_environment": chosen, "mask": mask})
    return records


def random_sequences(protocol: dict[str, Any]) -> tuple[list[list[int]], str]:
    settings = protocol["selectors"]["random"]
    sequence = np.random.SeedSequence(int(settings["seed_sequence_root"]))
    children = sequence.spawn(int(settings["seeds"]))
    permutations = [np.random.default_rng(child).permutation(16).tolist() for child in children]
    digest = hashlib.sha256(canonical_json(permutations).encode()).hexdigest()
    return permutations, digest


def auc(curve: Sequence[float], scientific_budgets: Sequence[int], empty_radius: float) -> float:
    selected = [curve[budget - 1] / empty_radius for budget in scientific_budgets]
    return float(np.mean(selected))


def map_corner(mask: int, permutation: Sequence[int], sign_mask: int) -> int:
    source = [1 if (mask >> coordinate) & 1 else -1 for coordinate in range(4)]
    target = [source[permutation[coordinate]] * (-1 if (sign_mask >> coordinate) & 1 else 1) for coordinate in range(4)]
    return sum((value == 1) << coordinate for coordinate, value in enumerate(target))


def map_subset(mask: int, permutation: Sequence[int], sign_mask: int) -> int:
    mapped = 0
    for environment in range(16):
        if (mask >> environment) & 1:
            mapped |= 1 << map_corner(environment, permutation, sign_mask)
    return mapped


def run_registered(protocol: dict[str, Any]) -> dict[str, Any]:
    census = exhaustive_census(protocol)
    points, features, families = census["points"], census["features"], census["families"]
    scores, ranks = census["scores"], census["ranks"]
    budgets = list(map(int, protocol["budgets"]))
    scientific_budgets = list(map(int, protocol["scientific_budgets"]))
    decimals = int(protocol["numeric_contract"]["score_round_decimals_for_ties_and_digest"])
    empty_radius = float(protocol["instrument_gates"]["empty_design_radius_squared"])
    space_records = space_filling_masks(budgets)
    permutations, random_digest = random_sequences(protocol)
    family_records: dict[str, Any] = {}
    deterministic_masks: set[tuple[str, str, int]] = set()

    for name, targets in families.items():
        values = scores[name]
        optimal = []
        for budget in budgets:
            mask = best_mask_at_budget(values, budget, decimals)
            optimal.append({"budget": budget, "mask": mask, "radius_squared": float(values[mask])})
            deterministic_masks.add((name, "optimal", mask))
        greedy = greedy_curve(values, budgets, decimals)
        for record in greedy:
            deterministic_masks.add((name, "active", record["mask"]))
        space = [{**record, "radius_squared": float(values[record["mask"]])} for record in space_records]
        for record in space:
            deterministic_masks.add((name, "space_filling", record["mask"]))
        random_aucs = []
        for permutation in permutations:
            mask = 0
            curve = []
            for environment in permutation[: max(budgets)]:
                mask |= 1 << int(environment)
                curve.append(float(values[mask]))
            random_aucs.append(auc(curve, scientific_budgets, empty_radius))
        greedy_curve_values = [record["radius_squared"] for record in greedy]
        space_curve_values = [record["radius_squared"] for record in space]
        greedy_auc = auc(greedy_curve_values, scientific_budgets, empty_radius)
        space_auc = auc(space_curve_values, scientific_budgets, empty_radius)
        random_median = float(np.median(random_aucs))
        improvement_random = (random_median - greedy_auc) / random_median if random_median > 0 else 0.0
        improvement_space = (space_auc - greedy_auc) / space_auc if space_auc > 0 else 0.0
        normalized_regrets = [
            max(0.0, greedy[budget - 1]["radius_squared"] - optimal[budget - 1]["radius_squared"]) / empty_radius
            for budget in scientific_budgets
        ]
        thresholds = protocol["scientific_thresholds"]
        supports = (
            improvement_random >= thresholds["minimum_relative_auc_improvement_over_random_median"]
            and improvement_space >= thresholds["minimum_relative_auc_improvement_over_space_filling"]
            and max(normalized_regrets) <= thresholds["maximum_normalized_regret_to_global_optimum"]
        )
        family_records[name] = {
            "target_masks": list(targets),
            "optimal": optimal,
            "active": greedy,
            "space_filling": space,
            "active_auc": greedy_auc,
            "space_filling_auc": space_auc,
            "random_auc": {
                "minimum": float(np.min(random_aucs)),
                "q05": float(np.quantile(random_aucs, 0.05, method="linear")),
                "median": random_median,
                "q95": float(np.quantile(random_aucs, 0.95, method="linear")),
                "maximum": float(np.max(random_aucs)),
            },
            "relative_auc_improvement_over_random_median": improvement_random,
            "relative_auc_improvement_over_space_filling": improvement_space,
            "maximum_normalized_regret_to_global_optimum": max(normalized_regrets),
            "supports_active_selector": supports,
        }

    feature_rows = features.astype(int).tolist()
    exact_witnesses = []
    exact_agreement = True
    exact_tolerance = float(protocol["numeric_contract"]["exact_numeric_agreement_absolute"])
    exact_cache: dict[tuple[str, int], sp.Rational] = {}
    for family_name, selector, mask in sorted(deterministic_masks):
        cache_key = (family_name, mask)
        if cache_key not in exact_cache:
            exact_cache[cache_key] = exact_score(mask, feature_rows, families[family_name])
        rational = exact_cache[cache_key]
        numeric = float(scores[family_name][mask])
        agreement = abs(float(rational) - numeric) <= exact_tolerance
        exact_agreement = exact_agreement and agreement
        exact_witnesses.append({
            "family": family_name,
            "selector": selector,
            "mask": mask,
            "exact_radius_squared": str(rational),
            "numeric_radius_squared": numeric,
            "agreement": agreement,
        })

    monotonic = True
    monotonic_checks = 0
    for name, values in scores.items():
        for mask in range(values.size):
            for environment in range(16):
                if not ((mask >> environment) & 1):
                    monotonic_checks += 1
                    if values[mask | (1 << environment)] > values[mask] + exact_tolerance:
                        monotonic = False
                        break
            if not monotonic:
                break
        if not monotonic:
            break

    coordinate_invariance = True
    coordinate_checks = 0
    representative_masks = {name: record["active"][4]["mask"] for name, record in family_records.items()}
    for name, targets in families.items():
        source_mask = representative_masks[name]
        source_score = float(scores[name][source_mask])
        for permutation in itertools.permutations(range(4)):
            for sign_mask in range(16):
                mapped_source = map_subset(source_mask, permutation, sign_mask)
                mapped_targets = tuple(sorted(map_corner(target, permutation, sign_mask) for target in targets))
                mapped_score, _ = score_mask(mapped_source, features, mapped_targets, float(protocol["numeric_contract"]["rank_relative_tolerance"]))
                coordinate_checks += 1
                if abs(mapped_score - source_score) > exact_tolerance:
                    coordinate_invariance = False
                    break
            if not coordinate_invariance:
                break
        if not coordinate_invariance:
            break

    geometry_ranges = {}
    geometry_live = True
    budget_five_masks = [mask for mask in range(1 << 16) if mask.bit_count() == 5]
    for name, values in scores.items():
        observed_range = float(max(values[mask] for mask in budget_five_masks) - min(values[mask] for mask in budget_five_masks))
        geometry_ranges[name] = observed_range
        geometry_live = geometry_live and observed_range >= protocol["instrument_gates"]["minimum_geometry_liveness_range"]

    empty_ok = all(abs(float(values[0]) - empty_radius) <= exact_tolerance for values in scores.values())
    full_ok = all(abs(float(values[(1 << 16) - 1])) <= exact_tolerance for values in scores.values()) and int(ranks[-1]) == features.shape[1]
    support_count = sum(record["supports_active_selector"] for record in family_records.values())
    if support_count == len(family_records):
        scientific_label = "active_design_supported_in_registered_finite_class"
    elif support_count == 0:
        scientific_label = "active_design_not_supported"
    else:
        scientific_label = "active_design_mixed"
    gates = {
        "G0_registration_binding": {"pass": True},
        "G1_complete_census": {"pass": len(ranks) == protocol["instrument_gates"]["complete_subset_count"], "subset_count": len(ranks), "census_sha256": census["digest"]},
        "G2_boundary_calibration": {"pass": empty_ok and full_ok, "empty_design_pass": empty_ok, "full_design_pass": full_ok},
        "G3_subset_monotonicity": {"pass": monotonic, "one_edge_checks": monotonic_checks},
        "G4_exact_witness_agreement": {"pass": exact_agreement, "witness_count": len(exact_witnesses), "witnesses": exact_witnesses},
        "G5_coordinate_invariance": {"pass": coordinate_invariance, "checks": coordinate_checks},
        "G6_geometry_liveness": {"pass": geometry_live, "budget_five_ranges": geometry_ranges},
        "G7_selector_integrity": {"pass": all(len({record["selected_environment"] for record in family_records[name]["active"]}) == len(budgets) for name in family_records), "random_sequence_sha256": random_digest, "random_sequences": len(permutations)},
    }
    instrument_valid = all(record["pass"] for record in gates.values())
    return {
        "schema_version": "asmp2_active_design_result_v0_2",
        "protocol_id": protocol["protocol_id"],
        "instrument_status": "valid" if instrument_valid else "invalid",
        "evidence_label": scientific_label if instrument_valid else "not_established_invalid_instrument",
        "runner_gate_pass": instrument_valid,
        "stage_decision": "pending_independent_verification" if instrument_valid else "invalid_stop",
        "feature_count": int(features.shape[1]),
        "environment_count": int(points.shape[0]),
        "gates": gates,
        "families": family_records,
        "claim_boundary": protocol["prohibited_claims"],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    protocol_path = args.protocol.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "asmp2_active_design_protocol_v0_2":
        raise ValueError("unexpected protocol schema")
    sealed = (protocol_path, HERE / "CLAIM_PACKET.md", HERE / "README.md", Path(__file__).resolve(), HERE / "verify_result.py", HERE / "test_active_design.py")
    output_dir = args.output_dir.resolve()
    if any(output_dir == path or output_dir in path.parents for path in sealed):
        raise ValueError("output directory aliases a sealed input")
    result_path, receipt_path = output_dir / "result_v0_2.json", output_dir / "receipt_v0_2.json"
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("registered output already exists")
    registration = bind_committed_inputs(sealed)
    tracemalloc.start()
    started = time.perf_counter()
    result = run_registered(protocol)
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ceiling = protocol["resource_ceiling"]
    resource_pass = elapsed <= ceiling["wall_seconds"] and peak <= ceiling["python_peak_bytes"]
    result["resource_receipt"] = {"elapsed_seconds": elapsed, "python_tracemalloc_peak_bytes": peak, "pass": resource_pass, "wall_ceiling_seconds": ceiling["wall_seconds"], "python_peak_ceiling_bytes": ceiling["python_peak_bytes"]}
    if not resource_pass:
        result["instrument_status"] = "unavailable"
        result["evidence_label"] = "unavailable_resource_cap"
        result["runner_gate_pass"] = False
        result["stage_decision"] = "unavailable_resource_cap"
    result["registration"] = registration
    result["protocol_sha256"] = sha256_file(protocol_path)
    payload = canonical_json(result).encode()
    write_once(result_path, payload)
    receipt = {
        "schema_version": "asmp2_active_design_receipt_v0_2",
        "git_commit_at_run": registration["commit"],
        "git_tracked_diff_sha256_at_run": registration["tracked_diff_sha256"],
        "protocol_sha256": sha256_file(protocol_path),
        "claim_packet_sha256": sha256_file(HERE / "CLAIM_PACKET.md"),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "verifier_sha256": sha256_file(HERE / "verify_result.py"),
        "tests_sha256": sha256_file(HERE / "test_active_design.py"),
        "result_sha256": hashlib.sha256(payload).hexdigest(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "sympy": sp.__version__, "platform": platform.platform()},
    }
    write_once(receipt_path, canonical_json(receipt).encode())
    print(canonical_json({"instrument_status": result["instrument_status"], "evidence_label": result["evidence_label"], "stage_decision": result["stage_decision"], "elapsed_seconds": elapsed, "result": str(result_path)}), end="")
    return 0 if result["runner_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
