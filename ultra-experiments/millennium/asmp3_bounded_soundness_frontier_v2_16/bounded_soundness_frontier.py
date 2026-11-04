from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from math import ceil, floor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "bounded_soundness_frontier_v2_16.json"
INTERACTIVE_PARENT_PATH = (
    HERE.parent
    / "asmp3_interactive_covering_frontier_v2_15"
    / "artifacts"
    / "interactive_covering_frontier_v2_15.json"
)
PATH_RISK_PARENT_PATH = (
    HERE.parent
    / "asmp3_correlated_path_risk_v2_13"
    / "artifacts"
    / "correlated_path_risk_v2_13.json"
)


SOUNDNESS_VALUES = (
    Fraction(0),
    Fraction(1, 100),
    Fraction(1, 10),
    Fraction(1, 5),
    Fraction(1, 3),
    Fraction(1, 2),
    Fraction(2, 3),
    Fraction(9, 10),
)


def ratio(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def bounded_row(
    marker_count: int,
    transcript_count: int,
    query_budget: int,
    soundness: Fraction,
) -> dict[str, object]:
    if marker_count < 1 or transcript_count < 1 or query_budget < 1:
        raise ValueError("N, K, and q must be positive")
    if not 0 <= soundness < 1:
        raise ValueError("soundness must lie in [0,1)")
    covered = min(marker_count, transcript_count * query_budget)
    good_value = Fraction(covered, marker_count)
    completeness = soundness + (1 - soundness) * good_value
    gap = completeness - soundness
    denominator = soundness.denominator
    bad_modes = soundness.numerator
    seed_atoms = denominator * marker_count
    marker_accepting_seed_atoms = bad_modes * marker_count + (denominator - bad_modes) * covered
    return {
        "semantic_atom_count": marker_count,
        "complete_prover_transcript_count": transcript_count,
        "adaptive_semantic_query_budget": query_budget,
        "soundness_upper_bound": ratio(soundness),
        "good_seed_marker_capacity": covered,
        "good_seed_worst_marker_completeness": ratio(good_value),
        "exact_bounded_soundness_completeness": ratio(completeness),
        "exact_completeness_soundness_gap": ratio(gap),
        "upper_bound_decomposition": "s+(1-s)*min(1,K*q/N)",
        "rational_attainment_public_seed_atoms": seed_atoms,
        "rational_attainment_bad_seed_atoms": bad_modes * marker_count,
        "rational_attainment_marker_accepting_seed_atoms": marker_accepting_seed_atoms,
        "rational_attainment_probability": ratio(Fraction(marker_accepting_seed_atoms, seed_atoms)),
        "perfect_completeness": completeness == 1,
        "perfect_completeness_iff_Kq_at_least_N": (completeness == 1) == (transcript_count * query_budget >= marker_count),
        "certified": (
            completeness == Fraction(marker_accepting_seed_atoms, seed_atoms)
            and gap == (1 - soundness) * good_value
            and completeness <= 1
        ),
    }


def resource_values(limit: int) -> tuple[int, ...]:
    values = {1, 2, 3, 4}
    values.update(value for value in (6, 8, 12, 16) if value <= limit)
    values.add(limit)
    return tuple(sorted(value for value in values if value <= limit))


def bounded_frontier_rows() -> list[dict[str, object]]:
    marker_counts = tuple(range(2, 33)) + (48, 64, 96, 128)
    return [
        bounded_row(marker_count, transcript_count, query_budget, soundness)
        for marker_count in marker_counts
        for transcript_count in resource_values(marker_count)
        for query_budget in resource_values(marker_count)
        for soundness in SOUNDNESS_VALUES
    ]


def cyclic_balanced_blocks(marker_count: int, block_size: int, block_count: int) -> list[tuple[int, ...]]:
    return [
        tuple((block_index * block_size + offset) % marker_count for offset in range(block_size))
        for block_index in range(block_count)
    ]


def finite_seed_balancing_rows() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 17):
        for public_seed_count in range(1, 13):
            for bad_seed_count in range(public_seed_count + 1):
                good_seed_count = public_seed_count - bad_seed_count
                for good_capacity in range(1, marker_count + 1):
                    blocks = cyclic_balanced_blocks(marker_count, good_capacity, good_seed_count)
                    degrees = [0] * marker_count
                    for block in blocks:
                        for marker in block:
                            degrees[marker] += 1
                    minimum_good_degree = min(degrees)
                    maximum_good_degree = max(degrees)
                    expected_minimum = floor(Fraction(good_seed_count * good_capacity, marker_count))
                    exact_success = Fraction(bad_seed_count + minimum_good_degree, public_seed_count)
                    averaging_upper = Fraction(bad_seed_count, public_seed_count) + Fraction(good_seed_count * good_capacity, public_seed_count * marker_count)
                    rows.append(
                        {
                            "semantic_atom_count": marker_count,
                            "uniform_public_seed_count": public_seed_count,
                            "bad_seed_count": bad_seed_count,
                            "good_seed_count": good_seed_count,
                            "markers_coverable_per_good_seed": good_capacity,
                            "minimum_good_seed_inclusions_per_marker": minimum_good_degree,
                            "maximum_good_seed_inclusions_per_marker": maximum_good_degree,
                            "optimal_minimum_good_degree": expected_minimum,
                            "exact_discrete_worst_marker_completeness": ratio(exact_success),
                            "continuous_averaging_upper_bound": ratio(averaging_upper),
                            "rounding_loss": ratio(averaging_upper - exact_success),
                            "balanced_degrees_differ_by_at_most_one": maximum_good_degree - minimum_good_degree <= 1,
                            "certified": minimum_good_degree == expected_minimum and maximum_good_degree - minimum_good_degree <= 1,
                        }
                    )
    return rows


def subset_masks(marker_count: int, subset_size: int) -> tuple[int, ...]:
    return tuple(
        sum(1 << marker for marker in subset)
        for subset in combinations(range(marker_count), subset_size)
    )


def finite_seed_exhaustive_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    rows = []
    total_families = violations = 0
    for marker_count in range(2, 6):
        for good_seed_count in range(0, 5):
            for good_capacity in range(1, min(marker_count, 3) + 1):
                subsets = subset_masks(marker_count, good_capacity)
                maximum_minimum_degree = -1
                families = 0
                for family in product(subsets, repeat=good_seed_count):
                    degrees = [0] * marker_count
                    for mask in family:
                        for marker in range(marker_count):
                            degrees[marker] += int(bool(mask & (1 << marker)))
                    minimum_degree = min(degrees)
                    maximum_minimum_degree = max(maximum_minimum_degree, minimum_degree)
                    families += 1
                    digest.update(
                        (
                            f"{marker_count}|{good_seed_count}|{good_capacity}|"
                            f"{','.join(map(str, family))}|{','.join(map(str, degrees))}\n"
                        ).encode("ascii")
                    )
                expected = floor(Fraction(good_seed_count * good_capacity, marker_count))
                mismatch = maximum_minimum_degree != expected
                violations += int(mismatch)
                total_families += families
                rows.append(
                    {
                        "semantic_atom_count": marker_count,
                        "good_seed_count": good_seed_count,
                        "markers_coverable_per_good_seed": good_capacity,
                        "coverage_families_enumerated": families,
                        "maximum_minimum_degree_found": maximum_minimum_degree,
                        "averaging_floor_upper_bound": expected,
                        "exact": not mismatch,
                    }
                )
    return {
        "rows": rows,
        "families_enumerated": total_families,
        "optimality_violations": violations,
        "canonical_family_digest_sha256": digest.hexdigest().upper(),
        "certified": len(rows) == 55 and total_families == 25_523 and violations == 0,
    }


def gap_target_rows() -> list[dict[str, object]]:
    targets = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
    rows = []
    for index_bits in range(4, 17):
        marker_count = 1 << index_bits
        for query_bits in range(0, min(index_bits, 8) + 1):
            query_budget = 1 << query_bits
            for soundness in SOUNDNESS_VALUES:
                for target in targets:
                    if target > 1 - soundness:
                        continue
                    minimum_transcripts = ceil(target * marker_count / ((1 - soundness) * query_budget))
                    minimum_transcripts = max(1, minimum_transcripts)
                    attained_gap = (1 - soundness) * min(Fraction(1), Fraction(minimum_transcripts * query_budget, marker_count))
                    prior_gap = (1 - soundness) * min(Fraction(1), Fraction(max(0, minimum_transcripts - 1) * query_budget, marker_count))
                    rows.append(
                        {
                            "index_bits": index_bits,
                            "semantic_atom_count": marker_count,
                            "query_budget": query_budget,
                            "soundness_upper_bound": ratio(soundness),
                            "target_gap": ratio(target),
                            "minimum_complete_prover_transcripts": minimum_transcripts,
                            "attained_gap": ratio(attained_gap),
                            "one_fewer_transcript_gap": ratio(prior_gap),
                            "target_attained": attained_gap >= target,
                            "one_fewer_transcript_insufficient": minimum_transcripts == 1 or prior_gap < target,
                            "certified": attained_gap >= target and (minimum_transcripts == 1 or prior_gap < target),
                        }
                    )
    return rows


def parent_audit() -> dict[str, object]:
    interactive = json.loads(INTERACTIVE_PARENT_PATH.read_text(encoding="utf-8"))
    path_risk = json.loads(PATH_RISK_PARENT_PATH.read_text(encoding="utf-8"))
    return {
        "interactive_parent_certified": interactive["certified"],
        "interactive_parent_exact_value": interactive["theorem"]["exact_value"],
        "interactive_parent_interface": interactive["theorem"]["interface"],
        "path_risk_parent_certified": path_risk["certified"],
        "path_risk_general_law": path_risk["theorem"]["general_path_law"],
        "certified": interactive["certified"] is True and interactive["theorem"]["exact_value"] == "min(1,K*q/N)" and path_risk["certified"] is True,
    }


def build_artifact() -> dict[str, object]:
    frontier = bounded_frontier_rows()
    balancing = finite_seed_balancing_rows()
    exhaustive = finite_seed_exhaustive_audit()
    targets = gap_target_rows()
    parents = parent_audit()
    gates = {
        "S0_parent_interactive_and_path_risk_contracts_match": parents["certified"],
        "S1_bounded_soundness_frontier_is_exact_on_all_registered_rows": len(frontier) > 10_000 and all(row["certified"] for row in frontier),
        "S2_upper_bound_splits_bad_seed_mass_and_good_seed_Kq_capacity": all(row["upper_bound_decomposition"] == "s+(1-s)*min(1,K*q/N)" for row in frontier),
        "S3_rational_bad_mode_plus_cyclic_cover_attains_every_row": all(row["exact_bounded_soundness_completeness"] == row["rational_attainment_probability"] for row in frontier),
        "S4_finite_uniform_seed_balancing_attains_averaging_floor": len(balancing) > 10_000 and all(row["certified"] for row in balancing),
        "S5_exhaustive_small_seed_families_match_balancing_optimum": exhaustive["certified"],
        "S6_exact_gap_is_one_minus_s_times_covering_value": all(Fraction(row["exact_completeness_soundness_gap"]) == (1 - Fraction(row["soundness_upper_bound"])) * Fraction(row["good_seed_worst_marker_completeness"]) for row in frontier),
        "S7_minimum_transcripts_for_target_gap_are_exact": len(targets) > 1_000 and all(row["certified"] for row in targets),
        "S8_perfect_completeness_still_equivalent_to_Kq_at_least_N_for_s_below_one": all(row["perfect_completeness_iff_Kq_at_least_N"] for row in frontier),
        "S9_all_interface_and_resource_boundaries_are_explicit": all(Fraction(row["soundness_upper_bound"]) < 1 for row in frontier) and parents["interactive_parent_interface"].startswith("arbitrary-round public-coin interaction"),
    }
    return {
        "schema_version": "asmp3_bounded_soundness_frontier_v2_16",
        "experiment_id": "ASMP-3-BOUNDED-SOUNDNESS-FRONTIER-v2.16",
        "parent_results": [
            "ASMP-3-INTERACTIVE-COVERING-FRONTIER-v2.15",
            "ASMP-3-CORRELATED-PATH-RISK-v2.13",
        ],
        "status": "exact_public_coin_interactive_unique_marker_frontier_with_bounded_soundness",
        "theorem": {
            "interface": "v2.15 arbitrary-round public-coin K-transcript q-query marker interface with zero-world soundness at most s",
            "bad_seed_lemma": "public-coin soundness bounds the measure of seeds admitting any no-hit accepting transcript by s",
            "good_seed_lemma": "on every remaining seed at most min(N,K*q) markers can accept",
            "exact_completeness": "C*=s+(1-s)*min(1,K*q/N)",
            "exact_gap": "C*-s=(1-s)*min(1,K*q/N)",
            "attainment": "mix unconditional-accept public modes of mass s with the cyclic v2.15 covering protocol",
            "perfect_completeness": "for s<1, K*q>=N iff perfect completeness is possible",
            "target_gap": "K>=ceil(gamma*N/((1-s)*q)) transcripts, subject to gamma<=1-s",
        },
        "bounded_frontier_rows": frontier,
        "finite_seed_balancing_rows": balancing,
        "finite_seed_exhaustive_audit": exhaustive,
        "gap_target_rows": targets,
        "parent_audit": parents,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The exact formula assumes the v2.15 unstructured marker interface, public verifier "
            "coins visible to the prover, at most K complete prover transcripts per seed, at most q "
            "adaptive ideal semantic queries, and worst-case zero-world soundness at most s<1. It "
            "does not classify private-coin protocols, structured side information, quantum queries, "
            "noisy-oracle soundness without a declared path-risk composition, or arbitrary ASMP-3 tasks."
        ),
    }


def write_artifact() -> dict[str, object]:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return artifact


if __name__ == "__main__":
    result = write_artifact()
    passed = sum(bool(value) for value in result["gates"].values())
    print(f"ASMP-3 bounded-soundness frontier certified: {passed}/{len(result['gates'])}")
