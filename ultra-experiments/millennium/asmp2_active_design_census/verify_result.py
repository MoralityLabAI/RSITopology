"""Independent verifier for the ASMP-2 active-design census."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent


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


def build_features() -> tuple[np.ndarray, np.ndarray, dict[str, tuple[int, ...]]]:
    points = np.array([[1 if mask & (1 << j) else -1 for j in range(4)] for mask in range(16)], dtype=float)
    terms = [np.ones(16)] + [points[:, j] for j in range(4)]
    terms += [points[:, i] * points[:, j] for i in range(4) for j in range(i + 1, 4)]
    features = np.stack(terms, axis=1)
    families = {
        "full_cube": tuple(range(16)),
        "nonnegative_sum": tuple(i for i, x in enumerate(points) if np.sum(x) >= 0),
        "even_parity": tuple(i for i, x in enumerate(points) if np.prod(x) == 1),
    }
    return points, features, families


def alternative_score(mask: int, features: np.ndarray, targets: Sequence[int], tolerance: float) -> tuple[float, int]:
    indices = [i for i in range(16) if mask & (1 << i)]
    if not indices:
        projector = np.eye(features.shape[1])
        rank = 0
    else:
        matrix = features[indices, :]
        projector = np.eye(features.shape[1]) - np.linalg.pinv(matrix, rcond=tolerance) @ matrix
        projector = (projector + projector.T) / 2
        rank = int(np.linalg.matrix_rank(matrix, tol=tolerance * np.linalg.svd(matrix, compute_uv=False)[0]))
    target = features[list(targets), :]
    values = np.sum((target @ projector) * target, axis=1)
    value = max(0.0, float(np.max(values)))
    return (0.0 if value < 1e-12 else value), rank


def q(value: float, decimals: int) -> int:
    return int(round(value * 10 ** decimals))


def recompute_census(protocol: dict[str, Any]) -> tuple[dict[str, np.ndarray], np.ndarray, str, np.ndarray, dict[str, tuple[int, ...]]]:
    _points, features, families = build_features()
    tolerance = float(protocol["numeric_contract"]["rank_relative_tolerance"])
    decimals = int(protocol["numeric_contract"]["score_round_decimals_for_ties_and_digest"])
    scores = {name: np.empty(1 << 16) for name in families}
    ranks = np.empty(1 << 16, dtype=np.int16)
    digest = hashlib.sha256()
    for mask in range(1 << 16):
        indices = [i for i in range(16) if mask & (1 << i)]
        if not indices:
            projector = np.eye(features.shape[1])
            rank = 0
        else:
            matrix = features[indices, :]
            projector = np.eye(features.shape[1]) - np.linalg.pinv(matrix, rcond=tolerance) @ matrix
            projector = (projector + projector.T) / 2
            singular = np.linalg.svd(matrix, compute_uv=False)
            rank = int(np.linalg.matrix_rank(matrix, tol=tolerance * singular[0]))
        row = []
        for name, targets in families.items():
            target = features[list(targets), :]
            values = np.sum((target @ projector) * target, axis=1)
            value = max(0.0, float(np.max(values)))
            value = 0.0 if value < 1e-12 else value
            scores[name][mask] = value
            row.append(q(value, decimals))
        ranks[mask] = rank
        digest.update(f"{mask}|{rank}|{'|'.join(map(str, row))}\n".encode())
    return scores, ranks, digest.hexdigest(), features, families


def best(values: np.ndarray, budget: int, decimals: int) -> int:
    return min((m for m in range(1 << 16) if m.bit_count() == budget), key=lambda m: (q(float(values[m]), decimals), m))


def greedy(values: np.ndarray, budgets: Sequence[int], decimals: int) -> list[tuple[int, int, int, float]]:
    mask = 0
    rows = []
    for budget in budgets:
        selected = min((i for i in range(16) if not (mask & (1 << i))), key=lambda i: (q(float(values[mask | (1 << i)]), decimals), i))
        mask |= 1 << selected
        rows.append((budget, selected, mask, float(values[mask])))
    return rows


def space_masks(budgets: Sequence[int]) -> list[tuple[int, int, int]]:
    selected = []
    mask = 0
    rows = []
    for budget in budgets:
        if not selected:
            chosen = 0
        else:
            chosen = min((i for i in range(16) if i not in selected), key=lambda i: (-min((i ^ j).bit_count() for j in selected), i))
        selected.append(chosen)
        mask |= 1 << chosen
        rows.append((budget, chosen, mask))
    return rows


def random_permutations(protocol: dict[str, Any]) -> tuple[list[list[int]], str]:
    settings = protocol["selectors"]["random"]
    children = np.random.SeedSequence(settings["seed_sequence_root"]).spawn(settings["seeds"])
    permutations = [np.random.default_rng(child).permutation(16).tolist() for child in children]
    return permutations, hashlib.sha256(canonical_json(permutations).encode()).hexdigest()


def curve_auc(curve: Sequence[float], budgets: Sequence[int]) -> float:
    return float(np.mean([curve[b - 1] / 11 for b in budgets]))


def exact_score(mask: int, rows: list[list[int]], targets: Sequence[int]) -> sp.Rational:
    selected = [rows[i] for i in range(16) if mask & (1 << i)]
    matrix = sp.Matrix(selected) if selected else sp.zeros(0, len(rows[0]))
    basis = matrix.nullspace()
    if not basis:
        return sp.Rational(0)
    null = sp.Matrix.hstack(*basis)
    projector = null * (null.T * null).inv() * null.T
    return max((sp.Matrix(rows[i]).T * projector * sp.Matrix(rows[i]))[0] for i in targets)


def close(left: float, right: float, tolerance: float = 1e-8) -> bool:
    return math.isclose(left, right, rel_tol=0, abs_tol=tolerance)


def verify(result_path: Path, receipt_path: Path) -> dict[str, Any]:
    protocol = json.loads((HERE / "protocol_v0_2.json").read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks = {
        "result_hash_matches_receipt": sha256_file(result_path) == receipt.get("result_sha256"),
        "protocol_hash_matches_receipt": sha256_file(HERE / "protocol_v0_2.json") == receipt.get("protocol_sha256"),
        "claim_hash_matches_receipt": sha256_file(HERE / "CLAIM_PACKET.md") == receipt.get("claim_packet_sha256"),
        "verifier_hash_matches_receipt": sha256_file(Path(__file__).resolve()) == receipt.get("verifier_sha256"),
        "schema_exact": result.get("schema_version") == "asmp2_active_design_result_v0_2",
        "runner_valid": result.get("instrument_status") == "valid" and result.get("runner_gate_pass") is True,
    }
    scores, ranks, census_digest, features, families = recompute_census(protocol)
    checks["census_digest_recomputed"] = census_digest == result["gates"]["G1_complete_census"]["census_sha256"]
    checks["boundary_calibration_recomputed"] = all(close(values[0], 11) and close(values[-1], 0) for values in scores.values()) and ranks[-1] == 11
    monotonic = all(
        scores[name][mask | (1 << environment)] <= scores[name][mask] + 1e-8
        for name in scores for mask in range(1 << 16) for environment in range(16) if not (mask & (1 << environment))
    )
    checks["subset_monotonicity_recomputed"] = monotonic
    budgets = list(map(int, protocol["budgets"]))
    scientific_budgets = list(map(int, protocol["scientific_budgets"]))
    decimals = int(protocol["numeric_contract"]["score_round_decimals_for_ties_and_digest"])
    space = space_masks(budgets)
    permutations, random_digest = random_permutations(protocol)
    checks["random_sequence_digest_recomputed"] = random_digest == result["gates"]["G7_selector_integrity"]["random_sequence_sha256"]
    family_match = True
    support_count = 0
    for name, targets in families.items():
        record = result["families"][name]
        values = scores[name]
        optimal = [(budget, best(values, budget, decimals)) for budget in budgets]
        active = greedy(values, budgets, decimals)
        family_match = family_match and [row[1] for row in optimal] == [row["mask"] for row in record["optimal"]]
        family_match = family_match and [row[2] for row in active] == [row["mask"] for row in record["active"]]
        family_match = family_match and [row[2] for row in space] == [row["mask"] for row in record["space_filling"]]
        active_curve = [row[3] for row in active]
        space_curve = [float(values[row[2]]) for row in space]
        random_aucs = []
        for permutation in permutations:
            mask = 0
            curve = []
            for environment in permutation[:10]:
                mask |= 1 << environment
                curve.append(float(values[mask]))
            random_aucs.append(curve_auc(curve, scientific_budgets))
        active_auc = curve_auc(active_curve, scientific_budgets)
        space_auc = curve_auc(space_curve, scientific_budgets)
        random_median = float(np.median(random_aucs))
        improve_random = (random_median - active_auc) / random_median if random_median else 0
        improve_space = (space_auc - active_auc) / space_auc if space_auc else 0
        regret = max(max(0.0, active[b - 1][3] - float(values[optimal[b - 1][1]])) / 11 for b in scientific_budgets)
        thresholds = protocol["scientific_thresholds"]
        supports = improve_random >= thresholds["minimum_relative_auc_improvement_over_random_median"] and improve_space >= thresholds["minimum_relative_auc_improvement_over_space_filling"] and regret <= thresholds["maximum_normalized_regret_to_global_optimum"]
        support_count += int(supports)
        family_match = family_match and close(active_auc, record["active_auc"])
        family_match = family_match and close(space_auc, record["space_filling_auc"])
        family_match = family_match and close(random_median, record["random_auc"]["median"])
        family_match = family_match and close(improve_random, record["relative_auc_improvement_over_random_median"])
        family_match = family_match and close(improve_space, record["relative_auc_improvement_over_space_filling"])
        family_match = family_match and close(regret, record["maximum_normalized_regret_to_global_optimum"])
        family_match = family_match and supports == record["supports_active_selector"]
    checks["selector_curves_and_classifications_recomputed"] = family_match
    expected_label = "active_design_supported_in_registered_finite_class" if support_count == 3 else "active_design_not_supported" if support_count == 0 else "active_design_mixed"
    checks["evidence_label_recomputed"] = result.get("evidence_label") == expected_label
    exact_ok = True
    exact_cache: dict[tuple[str, int], sp.Rational] = {}
    integer_features = features.astype(int).tolist()
    for witness in result["gates"]["G4_exact_witness_agreement"]["witnesses"]:
        cache_key = (witness["family"], witness["mask"])
        if cache_key not in exact_cache:
            exact_cache[cache_key] = exact_score(witness["mask"], integer_features, families[witness["family"]])
        exact = exact_cache[cache_key]
        exact_ok = exact_ok and str(exact) == witness["exact_radius_squared"] and close(float(exact), witness["numeric_radius_squared"])
    checks["exact_witnesses_recomputed"] = exact_ok
    checks["runner_gate_universe_and_pass"] = set(result.get("gates", {})) == {f"G{i}_{name}" for i, name in enumerate(("registration_binding", "complete_census", "boundary_calibration", "subset_monotonicity", "exact_witness_agreement", "coordinate_invariance", "geometry_liveness", "selector_integrity"))} and all(gate.get("pass") is True for gate in result.get("gates", {}).values())
    checks["resource_ceiling_pass"] = result.get("resource_receipt", {}).get("pass") is True
    checks["registration_commit_agrees"] = result.get("registration", {}).get("commit") == receipt.get("git_commit_at_run")
    passed = all(checks.values())
    return {
        "schema_version": "asmp2_active_design_verification_v0_2",
        "instrument_status": "valid" if passed else "invalid",
        "G8_independent_verification": {"pass": passed, "checks": checks},
        "stage_decision": "pass" if passed else "invalid",
        "evidence_label": expected_label if passed else "not_established_invalid_instrument",
        "claim_boundary": "Independent verification of one exhaustive finite polynomial-design census; no general ASMP-2 inference.",
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.result.is_file() or not args.receipt.is_file():
        raise FileNotFoundError("result and receipt required")
    if args.output.resolve() in {args.result.resolve(), args.receipt.resolve()}:
        raise ValueError("verification output aliases input")
    verification = verify(args.result.resolve(), args.receipt.resolve())
    write_once(args.output.resolve(), canonical_json(verification).encode())
    print(canonical_json(verification), end="")
    return 0 if verification["stage_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
