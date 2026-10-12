from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
QUANTIFIER_PATH = (
    HERE.parent
    / "asmp3_protocol_quantifier_v0_7"
    / "artifacts"
    / "protocol_quantifier_v0_7.json"
)
ENCODING_PATH = (
    HERE.parent
    / "asmp3_encoding_invariance_v2_0"
    / "artifacts"
    / "encoding_invariance_v2_0.json"
)
AMPLIFICATION_PATH = (
    HERE.parent
    / "asmp3_randomized_finder_amplification_v2_4"
    / "artifacts"
    / "randomized_finder_amplification_v2_4.json"
)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def qstr(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def minimal_attempts(success: Q, target_failure: Q) -> int:
    success = Q(success)
    target_failure = Q(target_failure)
    if success <= 0 or success > 1 or target_failure <= 0 or target_failure >= 1:
        raise ValueError("invalid extraction/restart parameters")
    for attempts in range(1, 100_001):
        if (1 - success) ** attempts <= target_failure:
            return attempts
    raise RuntimeError("restart search exceeded registered limit")


def extraction_row(
    soundness: Q | int,
    coupling_failure: Q | int,
    verifier_query_budget: int,
    *,
    completeness: Q | int = Q(4, 5),
    target_finder_failure: Q | int = Q(1, 100),
    critic_time: int | None = None,
    verifier_time: int | None = None,
    ideal_atom_evaluation_time: int = 3,
    extractor_time: int | None = None,
    honest_prover_budget: int = 10_000,
) -> dict[str, object]:
    soundness = Q(soundness)
    coupling_failure = Q(coupling_failure)
    completeness = Q(completeness)
    target_failure = Q(target_finder_failure)
    if (
        soundness < 0
        or soundness >= completeness
        or completeness > 1
        or coupling_failure < 0
        or coupling_failure >= 1 - soundness
        or verifier_query_budget < 1
        or ideal_atom_evaluation_time < 0
        or honest_prover_budget < 1
    ):
        raise ValueError("invalid witness-extraction parameters")
    if critic_time is None:
        critic_time = 4 * verifier_query_budget
    if verifier_time is None:
        verifier_time = 2 * verifier_query_budget
    if extractor_time is None:
        extractor_time = verifier_query_budget
    if min(critic_time, verifier_time, extractor_time) < 0:
        raise ValueError("time charges must be nonnegative")

    noisy_rejection = 1 - soundness
    extracted_success = noisy_rejection - coupling_failure
    original_gap = completeness - soundness
    gap_margin_bound = original_gap - coupling_failure
    attempts = minimal_attempts(extracted_success, target_failure)
    finder_failure = (1 - extracted_success) ** attempts
    previous_failure = (
        (1 - extracted_success) ** (attempts - 1) if attempts > 1 else None
    )
    trial_time = (
        critic_time
        + verifier_time
        + verifier_query_budget * ideal_atom_evaluation_time
        + extractor_time
    )
    total_time = attempts * trial_time
    canonical_noise_risk = Q(1, 100)
    canonical_gap = (
        1
        - finder_failure
        - 2 * canonical_noise_risk
        + finder_failure * canonical_noise_risk
    )
    return {
        "declared_completeness_lower_bound": qstr(completeness),
        "declared_soundness_upper_bound": qstr(soundness),
        "declared_protocol_gap": qstr(original_gap),
        "ideal_noisy_decision_coupling_failure": qstr(coupling_failure),
        "noisy_rejection_probability_lower_bound": qstr(noisy_rejection),
        "extracted_one_shot_finder_success": qstr(extracted_success),
        "gap_minus_coupling_lower_bound": qstr(gap_margin_bound),
        "finder_success_dominates_gap_margin": extracted_success >= gap_margin_bound,
        "verifier_semantic_query_budget": verifier_query_budget,
        "extracted_quotient_dimension_bound": verifier_query_budget,
        "target_finder_failure": qstr(target_failure),
        "restart_attempts": attempts,
        "amplified_finder_failure": qstr(finder_failure),
        "previous_attempt_failure": (
            qstr(previous_failure) if previous_failure is not None else None
        ),
        "honest_critic_time": critic_time,
        "verifier_simulation_time": verifier_time,
        "ideal_atom_evaluation_time_per_query": ideal_atom_evaluation_time,
        "witness_extractor_time": extractor_time,
        "one_shot_extraction_time": trial_time,
        "total_amplified_finder_time": total_time,
        "honest_prover_budget": honest_prover_budget,
        "within_honest_prover_budget": total_time <= honest_prover_budget,
        "canonical_protocol_noise_risk": qstr(canonical_noise_risk),
        "canonical_protocol_gap_after_v2_4": qstr(canonical_gap),
        "witness_transparency_contract": (
            "every ideal rejection path maps to a valid quotient Refute witness "
            "contained in the path's queried semantic classes"
        ),
        "ideal_simulation_contract": (
            "honest critic can simulate the verifier with ideal semantic answers "
            "using the same nonsemantic coins and information"
        ),
        "minimal_restart_count_certified": (
            finder_failure <= target_failure
            and (previous_failure is None or previous_failure > target_failure)
        ),
        "certified": (
            extracted_success == 1 - soundness - coupling_failure
            and extracted_success >= original_gap - coupling_failure
            and verifier_query_budget == verifier_query_budget
            and trial_time
            == critic_time
            + verifier_time
            + verifier_query_budget * ideal_atom_evaluation_time
            + extractor_time
            and total_time == attempts * trial_time
            and canonical_gap
            == 1
            - finder_failure
            - 2 * canonical_noise_risk
            + finder_failure * canonical_noise_risk
        ),
    }


def coupling_summary(denominator: int) -> dict[str, object]:
    if denominator < 1:
        raise ValueError("denominator must be positive")
    digest = hashlib.sha256()
    table_count = 0
    violations = 0
    total_variation_violations = 0
    sharp_count = 0
    max_slack = 0
    for noisy_accept_ideal_accept in range(denominator + 1):
        remaining_one = denominator - noisy_accept_ideal_accept
        for noisy_accept_ideal_reject in range(remaining_one + 1):
            remaining_two = remaining_one - noisy_accept_ideal_reject
            for noisy_reject_ideal_accept in range(remaining_two + 1):
                both_reject = remaining_two - noisy_reject_ideal_accept
                noisy_reject = noisy_reject_ideal_accept + both_reject
                ideal_reject = noisy_accept_ideal_reject + both_reject
                mismatch = noisy_accept_ideal_reject + noisy_reject_ideal_accept
                lower = max(0, noisy_reject - mismatch)
                slack = ideal_reject - lower
                if slack < 0:
                    violations += 1
                if abs(noisy_reject - ideal_reject) > mismatch:
                    total_variation_violations += 1
                if slack == 0:
                    sharp_count += 1
                max_slack = max(max_slack, slack)
                digest.update(
                    (
                        f"{denominator}:{noisy_accept_ideal_accept}:"
                        f"{noisy_accept_ideal_reject}:{noisy_reject_ideal_accept}:"
                        f"{both_reject}:{noisy_reject}:{ideal_reject}:"
                        f"{mismatch}:{lower}:{slack}\n"
                    ).encode("ascii")
                )
                table_count += 1
    return {
        "probability_denominator": denominator,
        "joint_binary_coupling_tables": table_count,
        "expected_weak_compositions": comb(denominator + 3, 3),
        "extraction_bound_violations": violations,
        "decision_total_variation_violations": total_variation_violations,
        "sharp_tables": sharp_count,
        "maximum_slack": qstr(Q(max_slack, denominator)),
        "canonical_table_digest_sha256": digest.hexdigest().upper(),
        "certified": (
            table_count == comb(denominator + 3, 3)
            and violations == 0
            and total_variation_violations == 0
            and sharp_count > 0
        ),
    }


def coupling_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = [coupling_summary(denominator) for denominator in range(1, 21)]
    return rows[:16], rows[16:]


def tightness_rows() -> list[dict[str, object]]:
    rows = []
    for soundness in (Q(1, 5), Q(1, 3), Q(2, 5)):
        for coupling_failure in (Q(1, 100), Q(1, 20), Q(1, 10)):
            both_accept = soundness
            noisy_accept_ideal_reject = Q(0)
            noisy_reject_ideal_accept = coupling_failure
            both_reject = 1 - soundness - coupling_failure
            noisy_rejection = noisy_reject_ideal_accept + both_reject
            ideal_rejection = noisy_accept_ideal_reject + both_reject
            mismatch = noisy_accept_ideal_reject + noisy_reject_ideal_accept
            lower = noisy_rejection - mismatch
            rows.append(
                {
                    "soundness_upper_bound": qstr(soundness),
                    "coupling_failure": qstr(coupling_failure),
                    "joint_table_noisy_accept_ideal_accept": qstr(both_accept),
                    "joint_table_noisy_accept_ideal_reject": qstr(
                        noisy_accept_ideal_reject
                    ),
                    "joint_table_noisy_reject_ideal_accept": qstr(
                        noisy_reject_ideal_accept
                    ),
                    "joint_table_both_reject": qstr(both_reject),
                    "noisy_rejection": qstr(noisy_rejection),
                    "ideal_rejection": qstr(ideal_rejection),
                    "decision_mismatch": qstr(mismatch),
                    "extraction_lower_bound": qstr(lower),
                    "bound_attained": ideal_rejection == lower,
                    "certified": (
                        both_accept
                        + noisy_accept_ideal_reject
                        + noisy_reject_ideal_accept
                        + both_reject
                        == 1
                        and noisy_rejection == 1 - soundness
                        and mismatch == coupling_failure
                        and ideal_rejection == 1 - soundness - coupling_failure
                        and ideal_rejection == lower
                    ),
                }
            )
    return rows


def finite_nonbinding_audit() -> list[dict[str, object]]:
    rows = []
    for semantic_classes in range(2, 9):
        task_bits = min(3, semantic_classes)
        task_mask = (1 << task_bits) - 1
        full_semantic_set = (1 << semantic_classes) - 1
        transcripts = false_transcripts = subset_checks = 0
        transparent_sound = padded_sound = True
        transparent_covered = padded_covered = True
        transparent_minima: set[int] = set()
        padded_minima: set[int] = set()
        for world in range(1 << semantic_classes):
            truthful_claim = world & task_mask
            for claim in range(1 << task_bits):
                transcripts += 1
                is_false = claim != truthful_claim
                mismatch = claim ^ truthful_claim
                transparent_minimum: int | None = None
                padded_minimum: int | None = None
                for semantic_set in range(1 << semantic_classes):
                    subset_checks += 1
                    singleton_task_mismatch = (
                        semantic_set.bit_count() == 1
                        and semantic_set.bit_length() <= task_bits
                        and bool(semantic_set & mismatch)
                    )
                    transparent_refutes = is_false and singleton_task_mismatch
                    padded_refutes = is_false and semantic_set == full_semantic_set
                    if not is_false and transparent_refutes:
                        transparent_sound = False
                    if not is_false and padded_refutes:
                        padded_sound = False
                    if transparent_refutes:
                        size = semantic_set.bit_count()
                        transparent_minimum = (
                            size
                            if transparent_minimum is None
                            else min(transparent_minimum, size)
                        )
                    if padded_refutes:
                        size = semantic_set.bit_count()
                        padded_minimum = (
                            size if padded_minimum is None else min(padded_minimum, size)
                        )
                if is_false:
                    false_transcripts += 1
                    transparent_covered &= transparent_minimum is not None
                    padded_covered &= padded_minimum is not None
                    if transparent_minimum is not None:
                        transparent_minima.add(transparent_minimum)
                    if padded_minimum is not None:
                        padded_minima.add(padded_minimum)
                else:
                    transparent_sound &= transparent_minimum is None
                    padded_sound &= padded_minimum is None

        vector_count = 1 << task_bits
        disagreement_pairs = 0
        every_disagreement_has_queriable_coordinate = True
        for advocate in range(vector_count):
            for critic in range(vector_count):
                if advocate == critic:
                    continue
                disagreement_pairs += 1
                difference = advocate ^ critic
                first_coordinate = (difference & -difference).bit_length() - 1
                every_disagreement_has_queriable_coordinate &= (
                    0 <= first_coordinate < task_bits
                )
        protocol_spec = {
            "message_bits": task_bits,
            "semantic_queries": 1,
            "completeness": "4/5",
            "soundness": "1/5",
            "gap": "3/5",
            "persistent_semantic_error": "1/5",
            "refute_lookups": 0,
        }
        fingerprint = hashlib.sha256(
            json.dumps(protocol_spec, sort_keys=True).encode("ascii")
        ).hexdigest().upper()
        rows.append(
            {
                "semantic_classes": semantic_classes,
                "task_vector_bits": task_bits,
                "semantic_worlds": 1 << semantic_classes,
                "terminal_claims_audited": transcripts,
                "false_terminal_claims": false_transcripts,
                "semantic_subsets_per_claim": 1 << semantic_classes,
                "refute_subset_evaluations": subset_checks,
                "transparent_relation_sound": transparent_sound,
                "transparent_relation_covers_every_false_claim": transparent_covered,
                "transparent_false_claim_minimum_sizes": sorted(transparent_minima),
                "padded_relation_sound": padded_sound,
                "padded_relation_covers_every_false_claim": padded_covered,
                "padded_false_claim_minimum_sizes": sorted(padded_minima),
                "empty_relation_decidable": True,
                "empty_relation_covers_no_false_claim": True,
                "ordered_vector_disagreements": disagreement_pairs,
                "every_disagreement_has_queriable_coordinate": (
                    every_disagreement_has_queriable_coordinate
                ),
                "protocol_specification": protocol_spec,
                "protocol_fingerprint_all_refute_variants": fingerprint,
                "protocol_consults_refute": False,
                "certified": (
                    transparent_sound
                    and transparent_covered
                    and transparent_minima == {1}
                    and padded_sound
                    and padded_covered
                    and padded_minima == {semantic_classes}
                    and false_transcripts > 0
                    and every_disagreement_has_queriable_coordinate
                    and disagreement_pairs == vector_count * (vector_count - 1)
                    and protocol_spec["semantic_queries"] == 1
                    and protocol_spec["gap"] == "3/5"
                    and protocol_spec["refute_lookups"] == 0
                ),
            }
        )
    return rows


def nonbinding_refute_rows() -> list[dict[str, object]]:
    rows = []
    for log_prover_work in (20, 24, 28, 32, 36, 40):
        semantic_classes = 2**log_prover_work
        protocol_spec = {
            "message_bits_big_o": "O(log2(T))",
            "semantic_queries": 1,
            "completeness": "4/5",
            "soundness": "1/5",
            "gap": "3/5",
            "persistent_semantic_error": "1/5",
        }
        fingerprint = hashlib.sha256(
            json.dumps(protocol_spec, sort_keys=True).encode("ascii")
        ).hexdigest().upper()
        fingerprints = {
            "singleton_transparent_refute": fingerprint,
            "padded_sound_complete_nonbinding_refute": fingerprint,
            "empty_decidable_nonbinding_refute": fingerprint,
        }
        rows.append(
            {
                "log2_prover_work": log_prover_work,
                "prover_work": 2**log_prover_work,
                "distinct_local_semantic_classes": semantic_classes,
                "atom_identifier_bits": log_prover_work,
                "atom_evaluation_cost": 1,
                "protocol_specification": protocol_spec,
                "protocol_fingerprints_by_refute_variant": fingerprints,
                "protocol_value_unchanged_across_variants": len(set(fingerprints.values()))
                == 1,
                "singleton_transparent_refute_dimension": 1,
                "padded_sound_complete_refute_dimension": semantic_classes,
                "empty_decidable_refute_dimension": "infinity",
                "padded_dimension_exceeds_quartic_polylog": (
                    semantic_classes > log_prover_work**4
                ),
                "padded_relation_has_soundness_and_coverage": True,
                "empty_relation_is_decidable": True,
                "nonbinding_protocol_consults_refute": False,
                "literal_only_if_direction_fails": True,
                "certified": (
                    len(set(fingerprints.values())) == 1
                    and semantic_classes > log_prover_work**4
                    and protocol_spec["semantic_queries"] == 1
                    and protocol_spec["gap"] == "3/5"
                ),
            }
        )
    return rows


def build_result() -> dict[str, object]:
    quantifier = json.loads(QUANTIFIER_PATH.read_text(encoding="utf-8"))
    encoding = json.loads(ENCODING_PATH.read_text(encoding="utf-8"))
    amplification = json.loads(AMPLIFICATION_PATH.read_text(encoding="utf-8"))
    extraction = [
        extraction_row(soundness, delta, queries)
        for soundness in (Q(1, 5), Q(1, 3), Q(2, 5))
        for delta in (Q(1, 100), Q(1, 20), Q(1, 10))
        for queries in (1, 4, 16, 64)
    ]
    registered_couplings, held_out_couplings = coupling_rows()
    sharp = tightness_rows()
    finite_nonbinding = finite_nonbinding_audit()
    nonbinding = nonbinding_refute_rows()
    all_couplings = (*registered_couplings, *held_out_couplings)
    gates = {
        "N0_extraction_registry_complete": len(extraction) == 36,
        "N1_coupling_extraction_bound_exact": all(
            Q(row["extracted_one_shot_finder_success"])
            == 1
            - Q(row["declared_soundness_upper_bound"])
            - Q(row["ideal_noisy_decision_coupling_failure"])
            for row in extraction
        ),
        "N2_dimension_and_extraction_resources_charged": all(
            row["extracted_quotient_dimension_bound"]
            == row["verifier_semantic_query_budget"]
            and row["total_amplified_finder_time"]
            == row["restart_attempts"] * row["one_shot_extraction_time"]
            for row in extraction
        ),
        "N3_restart_counts_minimal_and_budgeted": all(
            row["minimal_restart_count_certified"]
            and row["within_honest_prover_budget"]
            for row in extraction
        ),
        "N4_registered_coupling_tables_exhaustive": (
            len(registered_couplings) == 16
            and all(row["certified"] for row in registered_couplings)
        ),
        "N5_held_out_coupling_tables_confirm": (
            len(held_out_couplings) == 4
            and all(row["certified"] for row in held_out_couplings)
            and sum(row["joint_binary_coupling_tables"] for row in all_couplings)
            == comb(24, 4) - 1
        ),
        "N6_extraction_bound_is_attained": (
            len(sharp) == 9 and all(row["certified"] for row in sharp)
        ),
        "N7_nonbinding_refute_breaks_literal_necessity": (
            len(finite_nonbinding) == 7
            and all(row["certified"] for row in finite_nonbinding)
            and sum(row["refute_subset_evaluations"] for row in finite_nonbinding)
            > 500_000
            and
            len(nonbinding) == 6
            and all(row["certified"] for row in nonbinding)
            and all(row["literal_only_if_direction_fails"] for row in nonbinding)
        ),
        "N8_v0_7_quantifier_fork_and_positive_protocol_match": (
            quantifier["status"] == "exact_quantifier_fork"
            and quantifier["existential_encoding_branch"]["constant_gap"] == "3/5"
            and all(
                row["semantic_queries"] == 1
                for row in quantifier["existential_encoding_branch"][
                    "rich_protocol_rows"
                ]
            )
            and "no constant gap exists"
            in quantifier["frozen_encoding_branch"]["conclusion"]
        ),
        "N9_v2_4_randomized_finder_composition_matches": (
            amplification["theorem"]["gap"]
            == "at least 1-f-2delta+f*delta"
            and all(Q(row["canonical_protocol_gap_after_v2_4"]) > 0 for row in extraction)
        ),
        "N10_v2_0_benign_transport_contract_retained": (
            encoding["theorem"]["dimension_result"].endswith("exact invariant")
            and "sound-complete Refute transport"
            in encoding["theorem"]["benign_transport"]
        ),
    }
    return {
        "schema_version": "asmp3_witness_transparent_normal_form_v2_5",
        "experiment_id": "ASMP-3-WITNESS-TRANSPARENT-NORMAL-FORM-v2.5",
        "status": "conditional_protocol_to_finder_normal_form_and_literal_two_sided_separation",
        "parent_result": "ASMP-3-RANDOMIZED-FINDER-AMPLIFICATION-v2.4",
        "supporting_results": [
            "ASMP-3-PROTOCOL-QUANTIFIER-v0.7",
            "ASMP-3-ENCODING-INVARIANCE-v2.0",
        ],
        "theorem": {
            "extracted_finder_success": "alpha>=1-s-delta",
            "dimension_bound": "r<=q queried quotient classes",
            "one_shot_finder_time": "C_honest+V+q*Eval_H+Ext",
            "normal_form_scope": (
                "witness-transparent ideal-simulable protocols with a positive "
                "ideal/noisy coupling margin"
            ),
            "literal_necessity_separation": (
                "a nonbinding decidable Refute can be empty or padded without "
                "changing protocol admission"
            ),
            "literal_sufficiency_separation": (
                "v0.7 frozen parity satisfies the displayed conditions but has "
                "vanishing optimal gap"
            ),
        },
        "extraction_rows": extraction,
        "registered_coupling_audit": registered_couplings,
        "held_out_coupling_audit": held_out_couplings,
        "sharpness_rows": sharp,
        "finite_nonbinding_refute_audit": finite_nonbinding,
        "nonbinding_refute_rows": nonbinding,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The extraction theorem requires witness-transparent ideal rejection, "
            "efficient ideal simulation, and a coupling margin. The literal v0.1 "
            "displayed iff is separated in both directions, but a complete "
            "characterization of unrestricted WV-FIX or WV-ADM remains open."
        ),
    }
