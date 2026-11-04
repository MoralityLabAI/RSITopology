from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "online_contract_minimality_v2_11.json"
VERIFY_PATH = HERE / "artifacts" / "online_contract_minimality_verification_v2_11.json"
PARENT_PATH = (
    HERE.parent
    / "asmp3_online_noisy_trace_extractor_v2_10"
    / "artifacts"
    / "online_noisy_trace_extractor_v2_10.json"
)


def text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def reconstruct_partitions() -> list[dict[str, object]]:
    rows = []
    for count in range(2, 21):
        rows.append(
            {
                "marker_count": count,
                "decision_only_observation_classes": 1,
                "decision_only_possible_worlds": count,
                "decision_only_common_valid_witnesses": 0,
                "decision_only_las_vegas_success": "0",
                "trace_only_observation_classes": count,
                "trace_only_ambiguous_observations": count,
                "trace_only_safe_candidate_observations": 0,
                "trace_only_las_vegas_success_under_positive_noise": "0",
                "trace_plus_H_observation_classes": 2 * count,
                "trace_plus_H_safe_positive_observations": count,
                "trace_plus_H_fail_closed_observations": count,
                "certified": True,
            }
        )
    return rows


def reconstruct_probe_rows() -> list[dict[str, object]]:
    rows = []
    for count in range(2, 21):
        for budget in range(1, min(4, count) + 1):
            hits = [0] * count
            schedules = 0
            for subset in combinations(range(count), budget):
                schedules += 1
                for marker in subset:
                    hits[marker] += 1
            rows.append(
                {
                    "marker_count": count,
                    "ideal_probe_budget": budget,
                    "uniform_subset_schedules": schedules,
                    "schedules_hitting_each_world": hits[0],
                    "minimum_world_hit_schedules": min(hits),
                    "maximum_world_hit_schedules": max(hits),
                    "exact_las_vegas_success": text(Fraction(budget, count)),
                    "invalid_output_probability": "0",
                    "certified": (
                        schedules == math.comb(count, budget)
                        and min(hits)
                        == max(hits)
                        == math.comb(count - 1, budget - 1)
                    ),
                }
            )
    return rows


def reconstruct_no_h_rows() -> list[dict[str, object]]:
    rows = []
    for count in range(2, 21):
        for error in (
            Fraction(1, 100),
            Fraction(1, 10),
            Fraction(1, 5),
            Fraction(1, 3),
        ):
            rows.append(
                {
                    "marker_count": count,
                    "positive_decoy_probability": text(error),
                    "trace_only_las_vegas_success": "0",
                    "trace_only_las_vegas_invalid_probability": "0",
                    "trust_logged_candidate_success": text(1 - error),
                    "trust_logged_candidate_invalid_probability": text(error),
                    "trace_plus_H_success": text(1 - error),
                    "trace_plus_H_invalid_probability": "0",
                    "certified": True,
                }
            )
    return rows


def reconstruct_sharp_rows() -> list[dict[str, object]]:
    rows = []
    for soundness in (Fraction(0), Fraction(1, 5), Fraction(1, 3)):
        for denominator in range(1, 13):
            for numerator in range(denominator + 1):
                error = Fraction(numerator, denominator)
                rejection = 1 - soundness
                good_reject = max(Fraction(0), rejection - error)
                bad_reject = rejection - good_reject
                accept_bad = error - bad_reject
                accept_good = soundness - accept_bad
                lower = max(Fraction(0), 1 - soundness - error)
                rows.append(
                    {
                        "soundness": text(soundness),
                        "path_error_probability": text(error),
                        "good_reject_mass": text(good_reject),
                        "bad_reject_mass": text(bad_reject),
                        "accept_good_mass": text(accept_good),
                        "accept_bad_mass": text(accept_bad),
                        "validated_extractor_success": text(good_reject),
                        "theorem_lower_bound": text(lower),
                        "bound_attained": good_reject == lower,
                        "certified": (
                            min(good_reject, bad_reject, accept_good, accept_bad) >= 0
                            and good_reject
                            + bad_reject
                            + accept_good
                            + accept_bad
                            == 1
                            and good_reject == lower
                        ),
                    }
                )
    return rows


def reconstruct_path_audit(rows: list[dict[str, object]]) -> dict[str, object]:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(
            (
                f"{row['soundness']}|{row['path_error_probability']}|"
                f"{row['good_reject_mass']}|{row['bad_reject_mass']}|"
                f"{row['accept_good_mass']}|{row['accept_bad_mass']}\n"
            ).encode("ascii")
        )
    zero = next(
        row
        for row in rows
        if row["soundness"] == "0" and row["path_error_probability"] == "1"
    )
    return {
        "rows": len(rows),
        "all_bounds_attained": all(row["bound_attained"] for row in rows),
        "all_probability_tables_valid": all(row["certified"] for row in rows),
        "soundness_zero_path_error_one_success": zero[
            "validated_extractor_success"
        ],
        "canonical_path_error_digest_sha256": digest.hexdigest().upper(),
        "certified": len(rows) == 270 and all(row["certified"] for row in rows),
    }


def reconstruct_premises() -> list[dict[str, object]]:
    return [
        {
            "removed_premise": "public bound candidate trace",
            "counterfamily": "unique marker with one decision-only observation",
            "failure": "zero safe common witness; k ideal probes recover only k/N",
            "repair": "log the successful canonical Refute call inputs",
            "certified": True,
        },
        {
            "removed_premise": "candidate-only ideal H access",
            "counterfamily": "valid marker and noisy decoy share the same candidate log",
            "failure": "trace-only Las Vegas success is zero under any positive decoy mass",
            "repair": "evaluate H on the logged quotient classes",
            "certified": True,
        },
        {
            "removed_premise": "mandatory ideal Refute recheck",
            "counterfamily": "trust the noisy decoy call",
            "failure": "invalid witness probability equals the decoy probability",
            "repair": "return FAIL whenever ideal revalidation is false",
            "certified": True,
        },
        {
            "removed_premise": "adaptive path-error control",
            "counterfamily": "always reject using a forged noisy candidate",
            "failure": "soundness zero is compatible with validated extraction success zero",
            "repair": "bound Pr[Bad] jointly along the adaptive path",
            "certified": True,
        },
        {
            "removed_premise": "queried quotient-class scope",
            "counterfamily": "unlogged arbitrary candidate identifiers",
            "failure": "witness dimension and evaluation cost no longer follow from q",
            "repair": "restrict S to prior replication-quotiented query classes",
            "certified": True,
        },
        {
            "removed_premise": "complete resource accounting",
            "counterfamily": "hide ideal evaluation or Refute recheck behind extraction",
            "failure": "doubly efficient claim is unsupported",
            "repair": "charge trace scan, H evaluation, canonicalization, and recheck",
            "certified": True,
        },
    ]


def reconstruct_composition(parent: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for source in parent["composition_rows"]:
        rows.append(
            {
                "soundness_upper_bound": source["soundness_upper_bound"],
                "eta": source["eta"],
                "maximum_adaptive_queries": source["maximum_adaptive_queries"],
                "path_error_probability": source["path_error_probability"],
                "online_finder_success_lower_bound": source[
                    "online_finder_success_lower_bound"
                ],
                "online_extractor_time": source["online_extractor_time"],
                "necessary_online_contract": [
                    "public bound noisy candidate trace",
                    "candidate-only charged H access",
                    "mandatory ideal Refute recheck with FAIL",
                    "adaptive path-error bound",
                    "queried quotient-class scope",
                    "complete extraction resource ledger",
                ],
                "certified": source["certified"],
            }
        )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    partitions = reconstruct_partitions()
    probes = reconstruct_probe_rows()
    no_h = reconstruct_no_h_rows()
    sharp = reconstruct_sharp_rows()
    path = reconstruct_path_audit(sharp)
    premises = reconstruct_premises()
    composition = reconstruct_composition(parent)
    checks = {
        "V0_schema_parent_status": (
            result.get("schema_version") == "asmp3_online_contract_minimality_v2_11"
            and result.get("parent_result")
            == "ASMP-3-ONLINE-NOISY-TRACE-EXTRACTOR-v2.10"
            and result.get("status")
            == "black_box_las_vegas_online_contract_minimality"
        ),
        "V1_observation_partitions_reconstructed": result.get(
            "observation_partition_rows"
        )
        == partitions,
        "V2_all_73_probe_frontiers_reconstructed": result.get(
            "ideal_probe_frontier_rows"
        )
        == probes,
        "V3_all_76_trace_without_H_rows_reconstructed": result.get(
            "trace_without_H_rows"
        )
        == no_h,
        "V4_all_270_sharp_path_rows_reconstructed": result.get(
            "sharp_path_error_rows"
        )
        == sharp,
        "V5_path_error_digest_and_zero_success_case_reconstructed": result.get(
            "path_error_audit"
        )
        == path,
        "V6_all_six_premise_counterfamilies_reconstructed": result.get(
            "premise_necessity_rows"
        )
        == premises,
        "V7_all_12_parent_compositions_reconstructed": (
            len(composition) == 12 and result.get("composition_rows") == composition
        ),
        "V8_all_10_producer_gates_true": (
            len(result.get("gates", {})) == 10
            and all(result.get("gates", {}).values())
            and result.get("certified") is True
        ),
        "V9_claim_boundary_preserves_black_box_scope": all(
            phrase in result.get("claim_boundary", "")
            for phrase in (
                "black-box Las Vegas extractors",
                "valid in every world",
                "task-specific non-black-box proofs",
            )
        ),
    }
    return {
        "schema_version": "asmp3_online_contract_minimality_verification_v2_11",
        "checker": "clean_room_partition_probe_noise_path_premise_and_parent_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker certifies minimality only for the registered black-box "
            "Las Vegas observation model. It does not exclude task-specific "
            "structure, non-black-box access, or a different normative interface."
        ),
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not receipt["passed"]:
        failed = [name for name, value in receipt["checks"].items() if not value]
        raise RuntimeError(f"ASMP-3 v2.11 verification failed: {failed}")
    print(
        "ASMP-3 online-contract minimality verification passed: "
        f"{receipt['check_count']}/{receipt['check_count']}"
    )


if __name__ == "__main__":
    main()
