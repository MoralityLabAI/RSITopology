from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from math import ceil, floor
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "bounded_soundness_frontier_v2_16.json"
VERIFY_PATH = HERE / "artifacts" / "bounded_soundness_frontier_verification_v2_16.json"
INTERACTIVE_PARENT_PATH = HERE.parent / "asmp3_interactive_covering_frontier_v2_15" / "artifacts" / "interactive_covering_frontier_v2_15.json"
PATH_RISK_PARENT_PATH = HERE.parent / "asmp3_correlated_path_risk_v2_13" / "artifacts" / "correlated_path_risk_v2_13.json"


SOUNDNESS = (
    Fraction(0), Fraction(1, 100), Fraction(1, 10), Fraction(1, 5),
    Fraction(1, 3), Fraction(1, 2), Fraction(2, 3), Fraction(9, 10),
)


def ratio(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def resources(limit: int) -> tuple[int, ...]:
    values = {1, 2, 3, 4, limit}
    values.update(value for value in (6, 8, 12, 16) if value <= limit)
    return tuple(sorted(value for value in values if value <= limit))


def reconstruct_frontier() -> list[dict[str, object]]:
    rows = []
    for n in tuple(range(2, 33)) + (48, 64, 96, 128):
        for k in resources(n):
            for q in resources(n):
                for soundness in SOUNDNESS:
                    covered = min(n, k * q)
                    good = Fraction(covered, n)
                    completeness = soundness + (1 - soundness) * good
                    gap = completeness - soundness
                    denominator = soundness.denominator
                    bad_modes = soundness.numerator
                    seed_atoms = denominator * n
                    accepting = bad_modes * n + (denominator - bad_modes) * covered
                    rows.append(
                        {
                            "semantic_atom_count": n,
                            "complete_prover_transcript_count": k,
                            "adaptive_semantic_query_budget": q,
                            "soundness_upper_bound": ratio(soundness),
                            "good_seed_marker_capacity": covered,
                            "good_seed_worst_marker_completeness": ratio(good),
                            "exact_bounded_soundness_completeness": ratio(completeness),
                            "exact_completeness_soundness_gap": ratio(gap),
                            "upper_bound_decomposition": "s+(1-s)*min(1,K*q/N)",
                            "rational_attainment_public_seed_atoms": seed_atoms,
                            "rational_attainment_bad_seed_atoms": bad_modes * n,
                            "rational_attainment_marker_accepting_seed_atoms": accepting,
                            "rational_attainment_probability": ratio(Fraction(accepting, seed_atoms)),
                            "perfect_completeness": completeness == 1,
                            "perfect_completeness_iff_Kq_at_least_N": (completeness == 1) == (k * q >= n),
                            "certified": completeness == Fraction(accepting, seed_atoms) and gap == (1 - soundness) * good and completeness <= 1,
                        }
                    )
    return rows


def balanced_blocks(n: int, size: int, count: int) -> list[tuple[int, ...]]:
    return [tuple((index * size + offset) % n for offset in range(size)) for index in range(count)]


def reconstruct_balancing() -> list[dict[str, object]]:
    rows = []
    for n in range(2, 17):
        for seeds in range(1, 13):
            for bad in range(seeds + 1):
                good = seeds - bad
                for capacity in range(1, n + 1):
                    degrees = [0] * n
                    for block in balanced_blocks(n, capacity, good):
                        for marker in block:
                            degrees[marker] += 1
                    minimum = min(degrees)
                    maximum = max(degrees)
                    optimum = floor(Fraction(good * capacity, n))
                    exact = Fraction(bad + minimum, seeds)
                    upper = Fraction(bad, seeds) + Fraction(good * capacity, seeds * n)
                    rows.append(
                        {
                            "semantic_atom_count": n,
                            "uniform_public_seed_count": seeds,
                            "bad_seed_count": bad,
                            "good_seed_count": good,
                            "markers_coverable_per_good_seed": capacity,
                            "minimum_good_seed_inclusions_per_marker": minimum,
                            "maximum_good_seed_inclusions_per_marker": maximum,
                            "optimal_minimum_good_degree": optimum,
                            "exact_discrete_worst_marker_completeness": ratio(exact),
                            "continuous_averaging_upper_bound": ratio(upper),
                            "rounding_loss": ratio(upper - exact),
                            "balanced_degrees_differ_by_at_most_one": maximum - minimum <= 1,
                            "certified": minimum == optimum and maximum - minimum <= 1,
                        }
                    )
    return rows


def masks(n: int, size: int) -> tuple[int, ...]:
    return tuple(sum(1 << marker for marker in subset) for subset in combinations(range(n), size))


def reconstruct_exhaustive() -> dict[str, object]:
    digest = hashlib.sha256()
    rows = []
    total = violations = 0
    for n in range(2, 6):
        for good_seeds in range(5):
            for capacity in range(1, min(n, 3) + 1):
                maximum_minimum = -1
                families = 0
                for family in product(masks(n, capacity), repeat=good_seeds):
                    degrees = [0] * n
                    for mask in family:
                        for marker in range(n):
                            degrees[marker] += int(bool(mask & (1 << marker)))
                    maximum_minimum = max(maximum_minimum, min(degrees))
                    families += 1
                    digest.update((f"{n}|{good_seeds}|{capacity}|{','.join(map(str, family))}|{','.join(map(str, degrees))}\n").encode("ascii"))
                expected = floor(Fraction(good_seeds * capacity, n))
                exact = maximum_minimum == expected
                violations += int(not exact)
                total += families
                rows.append(
                    {
                        "semantic_atom_count": n,
                        "good_seed_count": good_seeds,
                        "markers_coverable_per_good_seed": capacity,
                        "coverage_families_enumerated": families,
                        "maximum_minimum_degree_found": maximum_minimum,
                        "averaging_floor_upper_bound": expected,
                        "exact": exact,
                    }
                )
    return {
        "rows": rows,
        "families_enumerated": total,
        "optimality_violations": violations,
        "canonical_family_digest_sha256": digest.hexdigest().upper(),
        "certified": len(rows) == 55 and total == 25523 and violations == 0,
    }


def reconstruct_targets() -> list[dict[str, object]]:
    targets = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
    rows = []
    for index_bits in range(4, 17):
        n = 1 << index_bits
        for query_bits in range(min(index_bits, 8) + 1):
            q = 1 << query_bits
            for soundness in SOUNDNESS:
                for target in targets:
                    if target > 1 - soundness:
                        continue
                    k = max(1, ceil(target * n / ((1 - soundness) * q)))
                    attained = (1 - soundness) * min(Fraction(1), Fraction(k * q, n))
                    prior = (1 - soundness) * min(Fraction(1), Fraction(max(0, k - 1) * q, n))
                    rows.append(
                        {
                            "index_bits": index_bits,
                            "semantic_atom_count": n,
                            "query_budget": q,
                            "soundness_upper_bound": ratio(soundness),
                            "target_gap": ratio(target),
                            "minimum_complete_prover_transcripts": k,
                            "attained_gap": ratio(attained),
                            "one_fewer_transcript_gap": ratio(prior),
                            "target_attained": attained >= target,
                            "one_fewer_transcript_insufficient": k == 1 or prior < target,
                            "certified": attained >= target and (k == 1 or prior < target),
                        }
                    )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    interactive = json.loads(INTERACTIVE_PARENT_PATH.read_text(encoding="utf-8"))
    path_risk = json.loads(PATH_RISK_PARENT_PATH.read_text(encoding="utf-8"))
    frontier = reconstruct_frontier()
    balancing = reconstruct_balancing()
    exhaustive = reconstruct_exhaustive()
    targets = reconstruct_targets()
    theorem = result.get("theorem", {})
    checks = {
        "V0_schema_parent_and_status": result.get("schema_version") == "asmp3_bounded_soundness_frontier_v2_16" and result.get("parent_results") == ["ASMP-3-INTERACTIVE-COVERING-FRONTIER-v2.15", "ASMP-3-CORRELATED-PATH-RISK-v2.13"] and result.get("status") == "exact_public_coin_interactive_unique_marker_frontier_with_bounded_soundness",
        "V1_parent_contracts_reconstructed": interactive["certified"] is True and interactive["theorem"]["exact_value"] == "min(1,K*q/N)" and path_risk["certified"] is True and result.get("parent_audit", {}).get("certified") is True,
        "V2_all_17784_bounded_soundness_rows_reconstructed": len(frontier) == 17784 and result.get("bounded_frontier_rows") == frontier and all(row["certified"] for row in frontier),
        "V3_all_12150_finite_seed_balancing_rows_reconstructed": len(balancing) == 12150 and result.get("finite_seed_balancing_rows") == balancing and all(row["certified"] for row in balancing),
        "V4_all_25523_small_seed_families_reconstructed": exhaustive["families_enumerated"] == 25523 and exhaustive["optimality_violations"] == 0 and result.get("finite_seed_exhaustive_audit") == exhaustive,
        "V5_all_3103_target_gap_thresholds_reconstructed": len(targets) == 3103 and result.get("gap_target_rows") == targets and all(row["certified"] for row in targets),
        "V6_exact_completeness_and_gap_theorems_match": theorem.get("exact_completeness") == "C*=s+(1-s)*min(1,K*q/N)" and theorem.get("exact_gap") == "C*-s=(1-s)*min(1,K*q/N)" and theorem.get("target_gap") == "K>=ceil(gamma*N/((1-s)*q)) transcripts, subject to gamma<=1-s",
        "V7_zero_soundness_slice_recovers_v2_15": all(row["exact_bounded_soundness_completeness"] == row["good_seed_worst_marker_completeness"] for row in frontier if row["soundness_upper_bound"] == "0"),
        "V8_interface_and_claim_boundaries_are_explicit": all(phrase in result.get("claim_boundary", "") for phrase in ("public verifier coins visible to the prover", "private-coin protocols", "arbitrary ASMP-3 tasks")) and theorem.get("perfect_completeness") == "for s<1, K*q>=N iff perfect completeness is possible",
        "V9_all_ten_producer_gates_pass": len(result.get("gates", {})) == 10 and all(result.get("gates", {}).values()) and result.get("certified") is True,
    }
    return {
        "schema_version": "asmp3_bounded_soundness_frontier_verification_v2_16",
        "checker": "clean_room_bounded_soundness_bad_seed_balancing_exhaustive_gap_frontier_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": "This checker certifies the public-coin marker interface, not private-coin or arbitrary-task lower bounds.",
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if not receipt["passed"]:
        failed = [name for name, value in receipt["checks"].items() if not value]
        raise RuntimeError(f"ASMP-3 v2.16 verification failed: {failed}")
    print(f"ASMP-3 bounded-soundness verification passed: {receipt['check_count']}/{receipt['check_count']}")


if __name__ == "__main__":
    main()
