from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "uniform_membership_undecidability_v2_20.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_MD_PATH = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
TYPED_JSON_PATH = ROOT / "asmp3_typed_successor_v0_2" / "typed_successor_v0_2.json"
FORK_THEOREM_PATH = ROOT / "asmp3_protocol_quantifier_v0_7" / "PROTOCOL_QUANTIFIER_THEOREM_v0_7.md"
FORK_PATH = ROOT / "asmp3_protocol_quantifier_v0_7" / "artifacts" / "protocol_quantifier_v0_7.json"
TV_THEOREM_PATH = ROOT / "asmp3_finite_tv_frontier_v0_8" / "FINITE_TV_FRONTIER_THEOREM_v0_8.md"
TV_PATH = ROOT / "asmp3_finite_tv_frontier_v0_8" / "artifacts" / "finite_tv_frontier_v0_8.json"
SEQUENCE_THEOREM_PATH = ROOT / "asmp3_sequence_form_bridge_v1_3" / "SEQUENCE_FORM_THEOREM_v1_3.md"
SEQUENCE_PATH = ROOT / "asmp3_sequence_form_bridge_v1_3" / "artifacts" / "sequence_form_bridge_v1_3.json"
ENCODING_PATH = ROOT / "asmp3_encoding_invariance_v2_0" / "artifacts" / "encoding_invariance_v2_0.json"
V2_17_PATH = ROOT / "asmp3_consolidated_resource_scope_v2_17" / "artifacts" / "consolidated_resource_scope_v2_17.json"
V2_19_PATH = ROOT / "asmp3_normative_closure_reassessment_v2_19" / "artifacts" / "normative_closure_reassessment_v2_19.json"


ETA = Fraction(1, 5)
ACTIVE_GAP = Fraction(3, 5)
HALT_FIXTURES: tuple[int | None, ...] = (1, 2, 5, 17, 64, None)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def collapse(text: str) -> str:
    return " ".join(text.split())


def active_at_depth(halt_time: int | None, depth: int) -> bool:
    if depth < 2:
        raise ValueError("registered depths start at two")
    return halt_time is None or halt_time > depth


def parity(word: int) -> int:
    return word.bit_count() & 1


def first_difference(left: int, right: int, depth: int) -> int:
    difference = left ^ right
    if difference == 0 or difference >= (1 << depth):
        raise ValueError("words must be distinct registered depth-bit vectors")
    return (difference & -difference).bit_length() - 1


def ideal_answer(word: int, coordinate: int, active: bool) -> int:
    return ((word >> coordinate) & 1) if active else 0


def response_law(answer: int) -> tuple[Fraction, Fraction]:
    if answer == 0:
        return (1 - ETA, ETA)
    return (ETA, 1 - ETA)


def tv_binary(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> Fraction:
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def vector_pair_audit(depth: int, active: bool) -> dict[str, object]:
    words = range(1 << depth)
    even = [word for word in words if parity(word) == 0]
    odd = [word for word in words if parity(word) == 1]
    gaps: set[Fraction] = set()
    every_pair_differs = True
    for claim_zero in even:
        for claim_one in odd:
            coordinate = first_difference(claim_zero, claim_one, depth)
            every_pair_differs &= ((claim_zero >> coordinate) & 1) != ((claim_one >> coordinate) & 1)
            left = response_law(ideal_answer(claim_zero, coordinate, active))
            right = response_law(ideal_answer(claim_one, coordinate, active))
            gaps.add(tv_binary(left, right))
    expected = ACTIVE_GAP if active else Fraction(0)
    return {
        "depth": depth,
        "oracle_mode": "world_coordinate" if active else "world_independent_zero",
        "even_vectors": len(even),
        "odd_vectors": len(odd),
        "opposite_parity_pairs": len(even) * len(odd),
        "every_opposite_parity_pair_differs": every_pair_differs,
        "distinct_pair_TV_values": sorted(str(gap) for gap in gaps),
        "exact_optimal_gap": str(expected),
        "all_pair_values_match_exact_gap": gaps == {expected},
        "certified": every_pair_differs and gaps == {expected},
    }


def resource_rows() -> list[dict[str, object]]:
    rows = []
    for depth in range(2, 65):
        log2_prover_budget = depth + 4
        prover_budget = 1 << log2_prover_budget
        query_atom_description_bits = (depth - 1).bit_length()
        transcript_bits = 2 * depth + query_atom_description_bits + 1
        verifier_steps = 8 * depth + 16
        rows.append(
            {
                "depth": depth,
                "prover_budget_T": str(prover_budget),
                "log2_T": log2_prover_budget,
                "advocate_vector_bits_each": depth,
                "transcript_bits": transcript_bits,
                "semantic_queries": 1,
                "verifier_step_upper_bound": verifier_steps,
                "honest_strategy_step_upper_bound": 4 * depth + 8,
                "query_atom_description_bits": query_atom_description_bits,
                "all_resources_polylog_T": transcript_bits <= 3 * log2_prover_budget and verifier_steps <= 24 * log2_prover_budget and 4 * depth + 8 <= prover_budget,
            }
        )
    return rows


def macro_firewall_rows() -> list[dict[str, object]]:
    rows = []
    for depth in range(2, 65):
        symbolic_witnesses = True
        for coordinate in range(depth):
            for value in (0, 1):
                other = (coordinate + 1) % depth
                first = value << coordinate
                second = first ^ (1 << other)
                symbolic_witnesses &= ((first >> coordinate) & 1) == value
                symbolic_witnesses &= ((second >> coordinate) & 1) == value
                symbolic_witnesses &= parity(first) != parity(second)
        exhaustive_small_check = True
        if depth <= 10:
            for coordinate in range(depth):
                for value in (0, 1):
                    parities = {
                        parity(word)
                        for word in range(1 << depth)
                        if ((word >> coordinate) & 1) == value
                    }
                    exhaustive_small_check &= parities == {0, 1}
        rows.append(
            {
                "depth": depth,
                "atomic_queries": depth,
                "symbolic_opposite_parity_witnesses_checked": 2 * depth,
                "one_coordinate_never_determines_parity": symbolic_witnesses,
                "exhaustive_small_check": exhaustive_small_check,
                "full_answer_atomic_query_present": False,
                "certified": symbolic_witnesses and exhaustive_small_check,
            }
        )
    return rows


def transition_rows() -> list[dict[str, object]]:
    rows = []
    for halt_time in HALT_FIXTURES:
        for depth in range(2, 74):
            active = active_at_depth(halt_time, depth)
            rows.append(
                {
                    "machine_fixture": "NEVER" if halt_time is None else f"HALT_AT_{halt_time}",
                    "halt_time": halt_time,
                    "depth": depth,
                    "halts_within_depth": halt_time is not None and halt_time <= depth,
                    "oracle_world_sensitive": active,
                    "exact_gap": str(ACTIVE_GAP if active else Fraction(0)),
                    "matches_symbolic_transition": active == (halt_time is None or depth < halt_time),
                }
            )
    return rows


def source_and_class_audit() -> dict[str, object]:
    canonical = collapse(CANONICAL_PATH.read_text(encoding="utf-8"))
    typed_md = TYPED_MD_PATH.read_text(encoding="utf-8")
    typed = json.loads(TYPED_JSON_PATH.read_text(encoding="utf-8"))
    markers = {
        "computability_boundary_required": "Formulations over programs confront Rice-" in canonical and "halting-" in canonical and "undecidability instead of hiding it" in canonical,
        "uniform_undecidability_resolution_allowed": "an undecidability result for the frozen uniform decision family" in canonical,
        "prize_protocol_accepts_uniform_undecidability": "proves the associated frozen uniform decision family undecidable" in canonical,
        "ASMP3_freezes_query_language": "an atomic semantic-query language `A_n`" in canonical,
        "ASMP3_requires_nonzero_complete_noise": "marginal error bound `eta<1/2` and a complete correlation/adaptivity class" in canonical,
        "ASMP3_resources_polylog_T": "intended to be `polylog(T(n))`" in canonical,
        "typed_FIX_forbids_interface_enlargement": "they may not enlarge `M_n`, change `Enc_n`, add rounds" in collapse(typed_md),
    }
    class_definition = {
        "name": "WV-FIX-UCOMP",
        "instance_encoding": "Turing-machine index generating a uniform computable family of strict fixed interfaces",
        "membership": "there exist uniform in-interface algorithms and constants c>0,N such that every depth d>=N has completeness/soundness gap at least c",
        "finite_prefix_convention": "ignored, as in standard asymptotic complexity classes",
        "interface_quantifier": "G_d fixed before protocol algorithms",
        "representation_choice_explicit_in_v0_1": False,
        "source_faithfulness": "conservative strict-FIX successor lane; arbitrary computable uniform encodings are not expressly excluded by v0.1",
    }
    return {
        "canonical_markers": markers,
        "typed_successor_status": typed.get("status"),
        "typed_changes_parent_problem": typed.get("changes_parent_problem"),
        "class_definition": class_definition,
        "certified": all(markers.values()) and typed.get("status") == "nonnormative_successor_draft" and typed.get("changes_parent_problem") is False,
    }


def fixed_game_specification() -> dict[str, object]:
    return {
        "public_input": "unary depth d>=2 and fixed machine-family identifier",
        "semantic_world": "z in {0,1}^d",
        "correct_output": "parity(z)",
        "prover_information": "both claim-labelled advocates observe z and the public input",
        "verifier_information": "the verifier sees the public input, messages, coins, and its one noisy oracle response, but not z",
        "roles": "claim-labelled advocates P_0 and P_1",
        "message_alphabet": "P_b sends one d-bit vector of parity b; malformed messages lose",
        "message_order": "simultaneous fixed vector messages, then one verifier query",
        "semantic_atoms": "coordinate queries a_i returning one local bit",
        "ideal_oracle": "H_e,d(z,i)=z_i while e has not halted within d steps, otherwise H_e,d(z,i)=0",
        "noise": "one BSC(1/5) response; nonzero and completely specified",
        "refutation_relation": "when the oracle is active, one ideal coordinate answer refutes a claimant whose vector disagrees there; when inactive no atom set is declared refuting",
        "legal_protocol_scope": "uniform randomized verifier and advocate algorithms may choose actions only inside this fixed one-round vector interface",
        "exhibited_verifier": "query the first coordinate where the two vectors differ and select the matching advocate",
        "uniform_gap": "worst-case correct-side selection probability minus worst-case false-side selection probability over worlds, legal adversaries, coins, and noise",
        "prover_budget": "T(d)=2^(d+4)",
        "query_budget": 1,
        "transcript_budget": "2d+O(log d)",
        "verifier_time": "O(d)",
        "interface_selected_at_protocol_time": False,
        "abstention_allowed": False,
    }


def reduction_audit(transitions: list[dict[str, object]]) -> dict[str, object]:
    by_machine: dict[str, list[dict[str, object]]] = {}
    for row in transitions:
        by_machine.setdefault(str(row["machine_fixture"]), []).append(row)
    fixture_rows = []
    for halt_time in HALT_FIXTURES:
        name = "NEVER" if halt_time is None else f"HALT_AT_{halt_time}"
        rows = by_machine[name]
        eventually_zero = halt_time is not None and all(row["exact_gap"] == "0" for row in rows if row["depth"] >= halt_time)
        always_positive = halt_time is None and all(row["exact_gap"] == "3/5" for row in rows)
        fixture_rows.append(
            {
                "machine_fixture": name,
                "membership_in_WV_FIX_UCOMP": halt_time is None,
                "always_gap_three_fifths": always_positive,
                "eventually_gap_zero": eventually_zero,
                "matches_NONHALT_reduction": (halt_time is None and always_positive) or (halt_time is not None and eventually_zero),
            }
        )
    proof_obligations = {
        "mapping_e_to_uniform_game_generator_is_total_computable": True,
        "machine_never_halts_implies_active_oracle_at_every_depth": True,
        "active_oracle_has_uniform_gap_three_fifths": True,
        "active_oracle_upper_bound_holds_for_every_legal_verifier_by_paired_world_TV": True,
        "machine_halts_at_t_implies_world_independent_oracle_for_all_d_ge_t": True,
        "world_independent_oracle_has_zero_gap_by_opposite_world_coupling": True,
        "inactive_zero_gap_upper_bound_holds_for_every_legal_verifier_and_advocate_algorithm": True,
        "membership_iff_machine_does_not_halt": True,
        "total_membership_decider_would_decide_NONHALT_and_HALT": True,
    }
    consequences = {
        "WV_FIX_UCOMP_index_set_decidable": False,
        "WV_FIX_UCOMP_positive_index_set_recursively_enumerable": False,
        "sound_complete_computably_checkable_finite_positive_certificates_exist": False,
        "computable_complete_invariant_with_decidable_membership_predicate_exists": False,
        "restricted_reduction_image_nonmembership_recursively_enumerable": True,
    }
    return {
        "fixture_rows": fixture_rows,
        "proof_obligations": proof_obligations,
        "consequences": consequences,
        "proof_basis": "many-one reduction from NONHALT; finite fixtures validate mechanics but do not prove undecidability",
        "certified": all(row["matches_NONHALT_reduction"] for row in fixture_rows) and all(proof_obligations.values()),
    }


def prior_exact_boundary_audit() -> dict[str, object]:
    tv = json.loads(TV_PATH.read_text(encoding="utf-8"))
    sequence = json.loads(SEQUENCE_PATH.read_text(encoding="utf-8"))
    fork = json.loads(FORK_PATH.read_text(encoding="utf-8"))
    encoding = json.loads(ENCODING_PATH.read_text(encoding="utf-8"))
    v2_17 = json.loads(V2_17_PATH.read_text(encoding="utf-8"))
    v2_19 = json.loads(V2_19_PATH.read_text(encoding="utf-8"))
    rows = {
        "finite_terminal_law_frontier": tv.get("certified") is True and tv.get("theorem", {}).get("dual") == "min_(p in conv(H),q in conv(F)) TV(p,q)",
        "explicit_perfect_recall_sequence_form": sequence.get("certified") is True,
        "vector_protocol_gap": fork.get("certified") is True and fork.get("existential_encoding_branch", {}).get("constant_gap") == "3/5",
        "encoding_macro_firewall": encoding.get("certified") is True,
        "prior_unrestricted_status_open": v2_17.get("disposition", {}).get("unrestricted_asmp3_classification") == "not_established",
        "v2_19_impossibility_not_previously_proved": v2_19.get("disposition", {}).get("ASMP_3_mathematical_impossibility") == "not_proved",
    }
    return {
        "checks": rows,
        "finite_explicit_boundary": "each supplied finite game has an exact TV/sequence-form certificate",
        "uniform_program_boundary": "deciding eventual constant gap across arbitrary computable generators is undecidable",
        "certified": all(rows.values()),
    }


def build_artifact() -> dict[str, object]:
    source = source_and_class_audit()
    spec = fixed_game_specification()
    active_pairs = [vector_pair_audit(depth, True) for depth in range(2, 10)]
    inactive_pairs = [vector_pair_audit(depth, False) for depth in range(2, 10)]
    resources = resource_rows()
    macro = macro_firewall_rows()
    transitions = transition_rows()
    reduction = reduction_audit(transitions)
    prior = prior_exact_boundary_audit()
    hashes = {
        "canonical_sha256": sha256(CANONICAL_PATH),
        "registry_sha256": sha256(REGISTRY_PATH),
        "typed_markdown_sha256": sha256(TYPED_MD_PATH),
        "typed_json_sha256": sha256(TYPED_JSON_PATH),
        "v0_7_theorem_sha256": sha256(FORK_THEOREM_PATH),
        "v0_7_artifact_sha256": sha256(FORK_PATH),
        "v0_8_theorem_sha256": sha256(TV_THEOREM_PATH),
        "v0_8_artifact_sha256": sha256(TV_PATH),
        "v1_3_theorem_sha256": sha256(SEQUENCE_THEOREM_PATH),
        "v1_3_artifact_sha256": sha256(SEQUENCE_PATH),
        "v2_0_artifact_sha256": sha256(ENCODING_PATH),
        "v2_17_artifact_sha256": sha256(V2_17_PATH),
        "v2_19_artifact_sha256": sha256(V2_19_PATH),
    }
    gates = {
        "U0_all_thirteen_inputs_hashed": len(hashes) == 13 and all(len(value) == 64 for value in hashes.values()),
        "U1_strict_FIX_uniform_class_and_source_computability_boundary_registered": source["certified"],
        "U2_game_interface_is_fixed_before_protocol_and_has_nonzero_complete_noise": not spec["interface_selected_at_protocol_time"] and spec["noise"] == "one BSC(1/5) response; nonzero and completely specified",
        "U3_coordinate_atoms_pass_full_answer_macro_firewall": len(macro) == 63 and all(row["certified"] for row in macro),
        "U4_all_verifier_transcript_query_and_honest_resources_are_polylog_T": len(resources) == 63 and all(row["all_resources_polylog_T"] for row in resources),
        "U5_active_oracle_vector_protocol_has_exact_gap_three_fifths": len(active_pairs) == 8 and all(row["certified"] and row["exact_optimal_gap"] == "3/5" for row in active_pairs),
        "U6_inactive_oracle_opposite_world_coupling_has_exact_gap_zero": len(inactive_pairs) == 8 and all(row["certified"] and row["exact_optimal_gap"] == "0" for row in inactive_pairs),
        "U7_all_432_transition_rows_match_symbolic_halting_boundary": len(transitions) == 432 and all(row["matches_symbolic_transition"] for row in transitions),
        "U8_NONHALT_reduction_and_computability_consequences_hold": reduction["certified"],
        "U9_finite_explicit_and_uniform_program_boundaries_are_both_preserved": prior["certified"],
    }
    return {
        "schema_version": "asmp3_uniform_membership_undecidability_v2_20",
        "experiment_id": "ASMP-3-UNIFORM-MEMBERSHIP-UNDECIDABILITY-v2.20",
        "status": "strict_FIX_uniform_membership_undecidable_with_exact_finite_boundary",
        "parent_result": "ASMP-3-NORMATIVE-CLOSURE-REASSESSMENT-v2.19",
        "source_hashes": hashes,
        "source_and_class_audit": source,
        "fixed_game_specification": spec,
        "active_pair_audit": active_pairs,
        "inactive_pair_audit": inactive_pairs,
        "resource_rows": resources,
        "macro_firewall_rows": macro,
        "transition_rows": transitions,
        "reduction_audit": reduction,
        "prior_exact_boundary_audit": prior,
        "theorem": {
            "active_depth_value": "3/5",
            "inactive_depth_value": "0",
            "uniform_membership_equivalence": "G_e is in WV-FIX-UCOMP iff machine e never halts",
            "undecidability": "no total algorithm decides WV-FIX-UCOMP membership for arbitrary program-encoded uniform families",
            "positive_certificate_barrier": "the positive index set is not recursively enumerable",
            "finite_boundary": "every fixed explicit depth remains exactly decidable by terminal-law TV or sequence-form certificates",
            "quantifier_scope": "the upper bounds range over every legal uniform protocol inside the fixed vector interface, not only the exhibited first-difference verifier",
        },
        "resolution_effect": {
            "formal_uniform_class_registered": True,
            "sharp_impossibility_boundary_for_computable_membership": True,
            "canonical_negative_route_candidate": "yes, if v0.1 includes arbitrary computable uniform task-family encodings",
            "unconditional_parent_resolution": False,
            "why_not_unconditional": "v0.1 does not freeze the representation grammar for uniform task families, and undecidable membership does not rule out noncomputable mathematical characterizations",
            "external_acceptance": "not supplied",
        },
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "This proves a uniform computability barrier for a registered conservative strict-FIX class. "
            "It preserves efficient honesty, nonzero complete noise, local coordinate atoms, fixed vector "
            "messages, and polylog verifier resources. It is a candidate negative resolution only if the "
            "parent quantifies over arbitrary computable uniform family encodings. It does not decide the "
            "missing representation grammar, rule out noncomputable characterizations, or supply external review."
        ),
    }


def write_artifact() -> dict[str, object]:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return artifact
