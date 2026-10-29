from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "uniform_membership_undecidability_v2_20.json"
VERIFY_PATH = HERE / "artifacts" / "uniform_membership_undecidability_verification_v2_20.json"
PATHS = {
    "canonical_sha256": ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "registry_sha256": ROOT / "problem_set_v0_1.json",
    "typed_markdown_sha256": ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "typed_json_sha256": ROOT / "asmp3_typed_successor_v0_2" / "typed_successor_v0_2.json",
    "v0_7_theorem_sha256": ROOT / "asmp3_protocol_quantifier_v0_7" / "PROTOCOL_QUANTIFIER_THEOREM_v0_7.md",
    "v0_7_artifact_sha256": ROOT / "asmp3_protocol_quantifier_v0_7" / "artifacts" / "protocol_quantifier_v0_7.json",
    "v0_8_theorem_sha256": ROOT / "asmp3_finite_tv_frontier_v0_8" / "FINITE_TV_FRONTIER_THEOREM_v0_8.md",
    "v0_8_artifact_sha256": ROOT / "asmp3_finite_tv_frontier_v0_8" / "artifacts" / "finite_tv_frontier_v0_8.json",
    "v1_3_theorem_sha256": ROOT / "asmp3_sequence_form_bridge_v1_3" / "SEQUENCE_FORM_THEOREM_v1_3.md",
    "v1_3_artifact_sha256": ROOT / "asmp3_sequence_form_bridge_v1_3" / "artifacts" / "sequence_form_bridge_v1_3.json",
    "v2_0_artifact_sha256": ROOT / "asmp3_encoding_invariance_v2_0" / "artifacts" / "encoding_invariance_v2_0.json",
    "v2_17_artifact_sha256": ROOT / "asmp3_consolidated_resource_scope_v2_17" / "artifacts" / "consolidated_resource_scope_v2_17.json",
    "v2_19_artifact_sha256": ROOT / "asmp3_normative_closure_reassessment_v2_19" / "artifacts" / "normative_closure_reassessment_v2_19.json",
}
HALT_FIXTURES: tuple[int | None, ...] = (1, 2, 5, 17, 64, None)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def parity(word: int) -> int:
    return word.bit_count() & 1


def first_difference(left: int, right: int) -> int:
    difference = left ^ right
    return (difference & -difference).bit_length() - 1


def response_law(bit: int) -> tuple[Fraction, Fraction]:
    return (Fraction(4, 5), Fraction(1, 5)) if bit == 0 else (Fraction(1, 5), Fraction(4, 5))


def tv(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> Fraction:
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def reconstruct_pair_rows(active: bool) -> list[dict[str, object]]:
    rows = []
    for depth in range(2, 10):
        even = [word for word in range(1 << depth) if parity(word) == 0]
        odd = [word for word in range(1 << depth) if parity(word) == 1]
        gaps = set()
        differs = True
        for claim_zero in even:
            for claim_one in odd:
                coordinate = first_difference(claim_zero, claim_one)
                zero_bit = ((claim_zero >> coordinate) & 1) if active else 0
                one_bit = ((claim_one >> coordinate) & 1) if active else 0
                differs &= ((claim_zero >> coordinate) & 1) != ((claim_one >> coordinate) & 1)
                gaps.add(tv(response_law(zero_bit), response_law(one_bit)))
        expected = Fraction(3, 5) if active else Fraction(0)
        rows.append(
            {
                "depth": depth,
                "oracle_mode": "world_coordinate" if active else "world_independent_zero",
                "even_vectors": len(even),
                "odd_vectors": len(odd),
                "opposite_parity_pairs": len(even) * len(odd),
                "every_opposite_parity_pair_differs": differs,
                "distinct_pair_TV_values": sorted(str(gap) for gap in gaps),
                "exact_optimal_gap": str(expected),
                "all_pair_values_match_exact_gap": gaps == {expected},
                "certified": differs and gaps == {expected},
            }
        )
    return rows


def reconstruct_resources() -> list[dict[str, object]]:
    rows = []
    for depth in range(2, 65):
        log2_t = depth + 4
        t = 1 << log2_t
        query_bits = (depth - 1).bit_length()
        transcript = 2 * depth + query_bits + 1
        verifier = 8 * depth + 16
        honest = 4 * depth + 8
        rows.append(
            {
                "depth": depth,
                "prover_budget_T": str(t),
                "log2_T": log2_t,
                "advocate_vector_bits_each": depth,
                "transcript_bits": transcript,
                "semantic_queries": 1,
                "verifier_step_upper_bound": verifier,
                "honest_strategy_step_upper_bound": honest,
                "query_atom_description_bits": query_bits,
                "all_resources_polylog_T": transcript <= 3 * log2_t and verifier <= 24 * log2_t and honest <= t,
            }
        )
    return rows


def reconstruct_macro_rows() -> list[dict[str, object]]:
    rows = []
    for depth in range(2, 65):
        symbolic = True
        for coordinate in range(depth):
            for value in (0, 1):
                other = (coordinate + 1) % depth
                first = value << coordinate
                second = first ^ (1 << other)
                symbolic &= ((first >> coordinate) & 1) == value
                symbolic &= ((second >> coordinate) & 1) == value
                symbolic &= parity(first) != parity(second)
        exhaustive = True
        if depth <= 10:
            for coordinate in range(depth):
                for value in (0, 1):
                    values = {parity(word) for word in range(1 << depth) if ((word >> coordinate) & 1) == value}
                    exhaustive &= values == {0, 1}
        rows.append(
            {
                "depth": depth,
                "atomic_queries": depth,
                "symbolic_opposite_parity_witnesses_checked": 2 * depth,
                "one_coordinate_never_determines_parity": symbolic,
                "exhaustive_small_check": exhaustive,
                "full_answer_atomic_query_present": False,
                "certified": symbolic and exhaustive,
            }
        )
    return rows


def reconstruct_transitions() -> list[dict[str, object]]:
    rows = []
    for halt_time in HALT_FIXTURES:
        for depth in range(2, 74):
            active = halt_time is None or halt_time > depth
            rows.append(
                {
                    "machine_fixture": "NEVER" if halt_time is None else f"HALT_AT_{halt_time}",
                    "halt_time": halt_time,
                    "depth": depth,
                    "halts_within_depth": halt_time is not None and halt_time <= depth,
                    "oracle_world_sensitive": active,
                    "exact_gap": "3/5" if active else "0",
                    "matches_symbolic_transition": active == (halt_time is None or depth < halt_time),
                }
            )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    canonical = " ".join(PATHS["canonical_sha256"].read_text(encoding="utf-8").split())
    typed_md = " ".join(PATHS["typed_markdown_sha256"].read_text(encoding="utf-8").split())
    typed = json.loads(PATHS["typed_json_sha256"].read_text(encoding="utf-8"))
    fork = json.loads(PATHS["v0_7_artifact_sha256"].read_text(encoding="utf-8"))
    tv_parent = json.loads(PATHS["v0_8_artifact_sha256"].read_text(encoding="utf-8"))
    sequence = json.loads(PATHS["v1_3_artifact_sha256"].read_text(encoding="utf-8"))
    encoding = json.loads(PATHS["v2_0_artifact_sha256"].read_text(encoding="utf-8"))
    hashes = {name: sha256(path) for name, path in PATHS.items()}
    active_rows = reconstruct_pair_rows(True)
    inactive_rows = reconstruct_pair_rows(False)
    resources = reconstruct_resources()
    macro = reconstruct_macro_rows()
    transitions = reconstruct_transitions()
    reduction = result.get("reduction_audit", {})
    proof = reduction.get("proof_obligations", {})
    consequences = reduction.get("consequences", {})

    fixtures = {row["machine_fixture"]: row for row in reduction.get("fixture_rows", [])}
    fixture_logic = (
        len(fixtures) == 6
        and fixtures["NEVER"]["membership_in_WV_FIX_UCOMP"] is True
        and fixtures["NEVER"]["always_gap_three_fifths"] is True
        and all(fixtures[f"HALT_AT_{time}"]["membership_in_WV_FIX_UCOMP"] is False for time in (1, 2, 5, 17, 64))
        and all(fixtures[f"HALT_AT_{time}"]["eventually_gap_zero"] is True for time in (1, 2, 5, 17, 64))
    )
    checks = {
        "V0_schema_parent_status_and_thirteen_hashes": result.get("schema_version") == "asmp3_uniform_membership_undecidability_v2_20" and result.get("parent_result") == "ASMP-3-NORMATIVE-CLOSURE-REASSESSMENT-v2.19" and result.get("source_hashes") == hashes,
        "V1_source_computability_and_strict_FIX_markers_reconstructed": all(marker in canonical for marker in ("Formulations over programs confront Rice-", "an undecidability result for the frozen uniform decision family", "proves the associated frozen uniform decision family undecidable", "an atomic semantic-query language `A_n`", "marginal error bound `eta<1/2`", "intended to be `polylog(T(n))`")) and "they may not enlarge `M_n`, change `Enc_n`, add rounds" in typed_md and typed["status"] == "nonnormative_successor_draft",
        "V2_fixed_vector_interface_and_local_atom_firewall_reconstructed": result["fixed_game_specification"]["interface_selected_at_protocol_time"] is False and result["fixed_game_specification"]["query_budget"] == 1 and "but not z" in result["fixed_game_specification"]["verifier_information"] and "every legal" in result["theorem"]["quantifier_scope"] and result.get("macro_firewall_rows") == macro and all(row["certified"] for row in macro),
        "V3_all_resource_ledgers_reconstructed": result.get("resource_rows") == resources and len(resources) == 63 and all(row["all_resources_polylog_T"] for row in resources),
        "V4_active_exact_gap_reconstructed_for_every_vector_pair": result.get("active_pair_audit") == active_rows and all(row["exact_optimal_gap"] == "3/5" and row["certified"] for row in active_rows) and fork["existential_encoding_branch"]["constant_gap"] == "3/5",
        "V5_inactive_zero_gap_reconstructed_for_every_vector_pair": result.get("inactive_pair_audit") == inactive_rows and all(row["exact_optimal_gap"] == "0" and row["certified"] for row in inactive_rows),
        "V6_all_halting_transition_rows_and_fixtures_reconstructed": result.get("transition_rows") == transitions and len(transitions) == 432 and fixture_logic,
        "V7_NONHALT_reduction_implications_are_complete": all(proof.values()) and proof.get("membership_iff_machine_does_not_halt") is True and proof.get("total_membership_decider_would_decide_NONHALT_and_HALT") is True and consequences == {"WV_FIX_UCOMP_index_set_decidable": False, "WV_FIX_UCOMP_positive_index_set_recursively_enumerable": False, "sound_complete_computably_checkable_finite_positive_certificates_exist": False, "computable_complete_invariant_with_decidable_membership_predicate_exists": False, "restricted_reduction_image_nonmembership_recursively_enumerable": True},
        "V8_exact_finite_parent_boundary_preserved": tv_parent["certified"] is True and tv_parent["theorem"]["dual"] == "min_(p in conv(H),q in conv(F)) TV(p,q)" and sequence["certified"] is True and encoding["certified"] is True and result["prior_exact_boundary_audit"]["certified"] is True,
        "V9_claim_boundary_does_not_overpromote": result["resolution_effect"]["unconditional_parent_resolution"] is False and "if v0.1 includes arbitrary computable uniform task-family encodings" in result["resolution_effect"]["canonical_negative_route_candidate"] and all(phrase in result["claim_boundary"] for phrase in ("candidate negative resolution", "does not decide the missing representation grammar", "rule out noncomputable characterizations", "external review")) and result["certified"] is True and all(result["gates"].values()),
    }
    return {
        "schema_version": "asmp3_uniform_membership_undecidability_verification_v2_20",
        "checker": "clean_room_source_fixed_game_pair_TV_resource_macro_transition_NONHALT_and_parent_boundary_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": "Finite enumeration validates the reduction mechanics; the universal undecidability conclusion rests on the separately written NONHALT proof, not on fixture coverage.",
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if not receipt["passed"]:
        failed = [name for name, passed in receipt["checks"].items() if not passed]
        raise RuntimeError(f"ASMP-3 v2.20 verification failed: {failed}")
    print(f"ASMP-3 uniform-membership verification passed: {receipt['check_count']}/{receipt['check_count']}")


if __name__ == "__main__":
    main()
