"""Independent opposite-parent verifier for ASMP-2 v0.2.1."""

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

import run as parent
import verify_result as legacy


HERE = Path(__file__).resolve().parent


def reverse_parent_census(protocol: dict[str, Any], amendment: dict[str, Any]):
    _points, features, families = legacy.build_features()
    subset_count, feature_count = 1 << 16, features.shape[1]
    projectors = np.empty((subset_count, feature_count, feature_count), dtype=np.float64)
    ranks = np.empty(subset_count, dtype=np.int16)
    projectors[0], ranks[0] = np.eye(feature_count), 0
    tolerance = float(amendment["residual_squared_rank_tolerance"])
    for mask in range(1, subset_count):
        highest_bit = 1 << (mask.bit_length() - 1)
        environment = highest_bit.bit_length() - 1
        previous = mask ^ highest_bit
        prior = projectors[previous]
        residual = prior @ features[environment]
        norm_squared = float(residual @ residual)
        if norm_squared > tolerance:
            update = prior - np.outer(residual, residual) / norm_squared
            projectors[mask] = (update + update.T) / 2
            ranks[mask] = ranks[previous] + 1
        else:
            projectors[mask] = prior
            ranks[mask] = ranks[previous]
    scores = {name: np.empty(subset_count) for name in families}
    chunk_size = int(amendment["score_chunk_size"])
    for name, targets in families.items():
        target_features = features[list(targets)]
        for start in range(0, subset_count, chunk_size):
            end = min(start + chunk_size, subset_count)
            projected = np.einsum("nij,tj->nti", projectors[start:end], target_features, optimize=True)
            values = np.einsum("nti,ti->nt", projected, target_features, optimize=True)
            scores[name][start:end] = np.maximum(0.0, np.max(values, axis=1))
        scores[name][scores[name] < 1e-12] = 0.0
    decimals = int(protocol["numeric_contract"]["score_round_decimals_for_ties_and_digest"])
    digest = hashlib.sha256()
    for mask in range(subset_count):
        row = [legacy.q(float(scores[name][mask]), decimals) for name in families]
        digest.update(f"{mask}|{int(ranks[mask])}|{'|'.join(map(str, row))}\n".encode())
    return scores, ranks, digest.hexdigest(), features, families


def close(left: float, right: float, tolerance: float = 1e-8) -> bool:
    return math.isclose(left, right, rel_tol=0, abs_tol=tolerance)


def map_corner(mask: int, permutation: Sequence[int], sign_mask: int) -> int:
    source = [1 if mask & (1 << coordinate) else -1 for coordinate in range(4)]
    transformed = [source[permutation[j]] * (-1 if sign_mask & (1 << j) else 1) for j in range(4)]
    return sum((value == 1) << j for j, value in enumerate(transformed))


def map_subset(mask: int, permutation: Sequence[int], sign_mask: int) -> int:
    return sum(1 << map_corner(environment, permutation, sign_mask) for environment in range(16) if mask & (1 << environment))


def verify(result_path: Path, receipt_path: Path) -> dict[str, Any]:
    amendment_path = HERE / "protocol_v0_2_1.json"
    parent_protocol_path = HERE / "protocol_v0_2.json"
    amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
    protocol = json.loads(parent_protocol_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks = {
        "result_hash_matches_receipt": parent.sha256_file(result_path) == receipt.get("result_sha256"),
        "parent_protocol_hash_matches": parent.sha256_file(parent_protocol_path) == amendment["parent_protocol_sha256"] == receipt.get("parent_protocol_sha256"),
        "amendment_hash_matches_receipt": parent.sha256_file(amendment_path) == receipt.get("amendment_sha256"),
        "claim_hash_matches_receipt": parent.sha256_file(HERE / "CLAIM_PACKET_v0_2_1.md") == receipt.get("claim_packet_sha256"),
        "verifier_hash_matches_receipt": parent.sha256_file(Path(__file__).resolve()) == receipt.get("verifier_sha256"),
        "schema_exact": result.get("schema_version") == "asmp2_active_design_result_v0_2_1",
        "runner_valid": result.get("instrument_status") == "valid" and result.get("runner_gate_pass") is True,
        "scientific_contract_unchanged": result.get("amendment", {}).get("scientific_contract_changes") == "none",
    }
    scores, ranks, digest, features, families = reverse_parent_census(protocol, amendment)
    checks["opposite_parent_census_digest_matches"] = digest == result["gates"]["G1_complete_census"]["census_sha256"]
    checks["boundary_calibration_recomputed"] = all(close(values[0], 11) and close(values[-1], 0) for values in scores.values()) and int(ranks[-1]) == 11
    checks["subset_monotonicity_recomputed"] = all(
        scores[name][mask | (1 << environment)] <= scores[name][mask] + 1e-8
        for name in scores for mask in range(1 << 16) for environment in range(16) if not mask & (1 << environment)
    )
    budgets = list(map(int, protocol["budgets"]))
    scientific_budgets = list(map(int, protocol["scientific_budgets"]))
    decimals = int(protocol["numeric_contract"]["score_round_decimals_for_ties_and_digest"])
    space = legacy.space_masks(budgets)
    random_permutations, random_digest = legacy.random_permutations(protocol)
    checks["random_sequence_digest_recomputed"] = random_digest == result["gates"]["G7_selector_integrity"]["random_sequence_sha256"]
    family_match = True
    support_count = 0
    for name in families:
        values = scores[name]
        record = result["families"][name]
        optimal = [(budget, legacy.best(values, budget, decimals)) for budget in budgets]
        active = legacy.greedy(values, budgets, decimals)
        family_match &= [mask for _budget, mask in optimal] == [row["mask"] for row in record["optimal"]]
        family_match &= [row[2] for row in active] == [row["mask"] for row in record["active"]]
        family_match &= [row[2] for row in space] == [row["mask"] for row in record["space_filling"]]
        active_curve = [row[3] for row in active]
        space_curve = [float(values[row[2]]) for row in space]
        random_aucs = []
        for permutation in random_permutations:
            mask, curve = 0, []
            for environment in permutation[:10]:
                mask |= 1 << environment
                curve.append(float(values[mask]))
            random_aucs.append(legacy.curve_auc(curve, scientific_budgets))
        active_auc = legacy.curve_auc(active_curve, scientific_budgets)
        space_auc = legacy.curve_auc(space_curve, scientific_budgets)
        random_median = float(np.median(random_aucs))
        improve_random = (random_median - active_auc) / random_median if random_median else 0.0
        improve_space = (space_auc - active_auc) / space_auc if space_auc else 0.0
        regret = max(max(0.0, active[b - 1][3] - float(values[optimal[b - 1][1]])) / 11 for b in scientific_budgets)
        thresholds = protocol["scientific_thresholds"]
        supports = improve_random >= thresholds["minimum_relative_auc_improvement_over_random_median"] and improve_space >= thresholds["minimum_relative_auc_improvement_over_space_filling"] and regret <= thresholds["maximum_normalized_regret_to_global_optimum"]
        support_count += int(supports)
        family_match &= close(active_auc, record["active_auc"])
        family_match &= close(space_auc, record["space_filling_auc"])
        family_match &= close(random_median, record["random_auc"]["median"])
        family_match &= close(improve_random, record["relative_auc_improvement_over_random_median"])
        family_match &= close(improve_space, record["relative_auc_improvement_over_space_filling"])
        family_match &= close(regret, record["maximum_normalized_regret_to_global_optimum"])
        family_match &= supports == record["supports_active_selector"]
    checks["selector_curves_and_classifications_recomputed"] = family_match
    expected_label = "active_design_supported_in_registered_finite_class" if support_count == 3 else "active_design_not_supported" if support_count == 0 else "active_design_mixed"
    checks["evidence_label_recomputed"] = result.get("evidence_label") == expected_label
    exact_cache: dict[tuple[str, int], sp.Rational] = {}
    exact_ok = True
    rows = features.astype(int).tolist()
    for witness in result["gates"]["G4_exact_witness_agreement"]["witnesses"]:
        key = (witness["family"], witness["mask"])
        if key not in exact_cache:
            exact_cache[key] = legacy.exact_score(witness["mask"], rows, families[witness["family"]])
        exact = exact_cache[key]
        exact_ok &= str(exact) == witness["exact_radius_squared"] and close(float(exact), witness["numeric_radius_squared"])
    checks["exact_witnesses_recomputed"] = exact_ok
    coordinate_ok, coordinate_checks = True, 0
    for name, targets in families.items():
        source_mask = result["families"][name]["active"][4]["mask"]
        source_score = float(scores[name][source_mask])
        for permutation in itertools.permutations(range(4)):
            for sign_mask in range(16):
                mapped_source = map_subset(source_mask, permutation, sign_mask)
                mapped_targets = tuple(sorted(map_corner(target, permutation, sign_mask) for target in targets))
                mapped_score, _ = legacy.alternative_score(mapped_source, features, mapped_targets, 1e-12)
                coordinate_checks += 1
                coordinate_ok &= close(mapped_score, source_score)
    checks["coordinate_invariance_recomputed"] = coordinate_ok and coordinate_checks == 1152
    checks["runner_gate_universe_and_pass"] = len(result.get("gates", {})) == 8 and all(gate.get("pass") is True for gate in result.get("gates", {}).values())
    checks["resource_ceiling_pass"] = result.get("resource_receipt", {}).get("pass") is True
    checks["registration_commit_agrees"] = result.get("registration", {}).get("commit") == receipt.get("git_commit_at_run")
    passed = all(checks.values())
    return {
        "schema_version": "asmp2_active_design_verification_v0_2_1",
        "instrument_status": "valid" if passed else "invalid",
        "G8_independent_verification": {"pass": passed, "checks": checks},
        "stage_decision": "pass" if passed else "invalid",
        "evidence_label": expected_label if passed else "not_established_invalid_instrument",
        "claim_boundary": "Opposite-parent verification of the registered finite numerical census; no general ASMP-2 inference.",
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
    verification = verify(args.result.resolve(), args.receipt.resolve())
    parent.write_once(args.output.resolve(), parent.canonical_json(verification).encode())
    print(parent.canonical_json(verification), end="")
    return 0 if verification["stage_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

