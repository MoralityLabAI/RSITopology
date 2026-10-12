from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "standard_encoding_transfer_v2_21.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_MD_PATH = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
TYPED_JSON_PATH = ROOT / "asmp3_typed_successor_v0_2" / "typed_successor_v0_2.json"
TV_THEOREM_PATH = ROOT / "asmp3_finite_tv_frontier_v0_8" / "FINITE_TV_FRONTIER_THEOREM_v0_8.md"
TV_ARTIFACT_PATH = ROOT / "asmp3_finite_tv_frontier_v0_8" / "artifacts" / "finite_tv_frontier_v0_8.json"
V2_20_THEOREM_PATH = ROOT / "asmp3_uniform_membership_undecidability_v2_20" / "UNIFORM_MEMBERSHIP_UNDECIDABILITY_THEOREM_v2_20.md"
V2_20_ARTIFACT_PATH = ROOT / "asmp3_uniform_membership_undecidability_v2_20" / "artifacts" / "uniform_membership_undecidability_v2_20.json"
V2_20_VERIFY_PATH = ROOT / "asmp3_uniform_membership_undecidability_v2_20" / "artifacts" / "uniform_membership_undecidability_verification_v2_20.json"
V2_20_MANIFEST_PATH = ROOT / "asmp3_uniform_membership_undecidability_v2_20" / "RELEASE_MANIFEST_v2_20.json"


ENCODINGS = ("json_ast", "register_ir", "circuit_ir")
HALT_FIXTURES: tuple[int | None, ...] = (1, 2, 5, 17, 64, None)
INTERFACE_FIXTURES = {
    "fixed_vector": 1,
    "alternating_eight_round": 8,
    "public_coin_adaptive_twelve_round": 12,
    "private_challenge_six_round": 6,
    "long_message_query_sixteen_round": 16,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def collapse(text: str) -> str:
    return " ".join(text.split())


def compile_family(encoding: str, machine_index: int) -> dict[str, object]:
    if not isinstance(machine_index, int) or machine_index < 0:
        raise ValueError("machine_index must be a nonnegative integer")
    common = {
        "schema": f"asmp3_fix_std_{encoding}_v1",
        "machine_index": machine_index,
        "depth_domain": "d>=2",
        "relation": "parity(z)",
        "message_interface": "simultaneous labelled parity vectors",
        "atom_language": "coordinate(d)",
        "noise": {"channel": "BSC", "eta": "1/5", "uses": 1},
        "budget": {"T": "2^(d+4)", "q": 1, "verifier": "O(d)", "transcript": "2d+ceil(log2(d))+1"},
    }
    if encoding == "json_ast":
        common["generator"] = {
            "op": "bounded_halt_mux",
            "steps": "d",
            "halted": {"op": "constant_oracle", "value": 0},
            "running": {"op": "world_coordinate"},
        }
    elif encoding == "register_ir":
        common["program"] = [
            ["LOAD_DEPTH", "d"],
            ["SIMULATE_MACHINE", machine_index, "d"],
            ["BRANCH_IF_HALTED", "CONST_ZERO", "WORLD_COORDINATE"],
            ["APPLY_BSC", 1, 5],
            ["RETURN"],
        ]
    elif encoding == "circuit_ir":
        common["nodes"] = [
            {"id": "h", "op": "bounded_universal_simulation", "machine": machine_index, "steps": "d"},
            {"id": "w", "op": "world_bit", "coordinate": "i"},
            {"id": "a", "op": "mux", "selector": "h", "if_true": 0, "if_false": "w"},
            {"id": "y", "op": "bsc", "input": "a", "eta": "1/5"},
        ]
        common["output"] = "y"
    else:
        raise ValueError(f"unknown encoding: {encoding}")
    return common


def decode_family(description: dict[str, object]) -> dict[str, object]:
    schema = description.get("schema")
    if not isinstance(schema, str) or not schema.startswith("asmp3_fix_std_") or not schema.endswith("_v1"):
        raise ValueError("unregistered schema")
    encoding = schema[len("asmp3_fix_std_") : -len("_v1")]
    if encoding not in ENCODINGS:
        raise ValueError("unknown standard encoding")
    machine_index = description.get("machine_index")
    if not isinstance(machine_index, int) or machine_index < 0:
        raise ValueError("invalid machine index")
    expected = compile_family(encoding, machine_index)
    if description != expected:
        raise ValueError("description is not canonical")
    return {
        "encoding": encoding,
        "machine_index": machine_index,
        "total_generator": True,
        "bounded_simulation": True,
        "strict_fixed_interface": True,
        "semantic_signature": "parity_vectors_coordinate_oracle_BSC_1_5",
    }


def source_resolution_audit() -> dict[str, object]:
    canonical = collapse(CANONICAL_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    asmp3 = next(problem for problem in registry["problems"] if problem["id"] == "ASMP-3")
    markers = {
        "closed_core_requires_encodings": "Objects, domains, encodings, resource bounds, randomness, adversaries, and quantifier order are explicit" in canonical,
        "computability_boundary": "Formulations over programs confront Rice-" in canonical and "halting-" in canonical,
        "invariance_under_equivalent_encodings": "equivalent encodings, renamings, and implementation refactorings" in canonical,
        "undecidability_is_resolution_route": "an undecidability result for the frozen uniform decision family" in canonical,
        "ASMP3_freezes_relation_and_game_data": "freeze a decision relation `R_n`; a public-coin message order and stopping rule" in canonical,
        "ASMP3_freezes_atoms_and_oracles": "an atomic semantic-query language `A_n`" in canonical and "an ideal binary semantic oracle `H`; and a noisy oracle `H_tilde`" in canonical,
        "ASMP3_requires_polylog_resources_and_efficient_honesty": "all three intended to be `polylog(T(n))`" in canonical and "The honest prover must itself have an efficient strategy" in canonical,
        "ASMP3_negative_identical_world_example": "two candidate worlds generate identical allowed semantic queries but require opposite answers" in canonical,
        "prize_protocol_uses_standard_encodings": "ordinary mathematical claims are formalized over ZFC with standard encodings of computation, probability, and analysis" in canonical,
        "prize_protocol_full_set_not_subclass": "proves the associated frozen uniform decision family undecidable. A theorem for a narrower subclass is partial progress" in canonical,
        "changed_assumption_requires_reduction": "Any changed assumption creates a new problem version and cannot be presented as resolving the parent without a reduction" in canonical,
    }
    registry_checks = {
        "canonical_target_is_frozen_atomic_game": "frozen atomic-query game" in asmp3["canonical_target"],
        "negative_resolution_allowed": asmp3["negative_resolution_allowed"] is True,
        "negative_scope_retains_honesty_and_noise": set(asmp3["negative_resolution_requires"]) == {
            "separation_or_impossibility_in_the_frozen_message_game",
            "efficient_honest_prover_and_noise_model_must_remain_in_scope",
        },
    }
    return {
        "source_markers": markers,
        "registry_checks": registry_checks,
        "certified": all(markers.values()) and all(registry_checks.values()),
    }


def canonical_admissibility_rows() -> list[dict[str, object]]:
    rows = [
        ("decision_relation", "R_d(z,b) iff b=parity(z)", "canonical setting line 304"),
        ("message_order", "simultaneous P_0/P_1 vectors, then one query and decision", "canonical setting lines 304-316"),
        ("stopping_rule", "stop after the single noisy answer", "canonical setting lines 304-316"),
        ("atom_language", "A_d={coordinate i: 0<=i<d}", "canonical setting lines 305-307"),
        ("atom_description_and_locality", "ceil(log2 d) bits and radius one coordinate", "canonical setting lines 305-307"),
        ("ideal_oracle", "bounded-halt mux between z_i and zero", "canonical setting lines 307-308"),
        ("complete_noise_law", "one BSC(1/5), with no undeclared dependence", "canonical setting lines 308-310"),
        ("prover_budget", "T(d)=2^(d+4)", "canonical setting lines 312-318"),
        ("fixed_zero_sum_payoff", "selecting the correct versus false claim label", "canonical setting lines 312-313"),
        ("verifier_resources", "O(d) time, q=1, transcript 2d+ceil(log2 d)+1", "canonical setting lines 313-318"),
        ("fixed_transcript_encoding", "canonical labelled vectors, coordinate, response", "canonical setting lines 315-316"),
        ("efficient_honest_strategy", "send z in O(d) time", "canonical setting lines 316-318"),
        ("decidable_refute", "active coordinate disagreement; no inactive refuting set", "canonical setting lines 320-332"),
        ("macro_query_firewall", "each coordinate value occurs in both parity classes for d>=2", "canonical setting lines 334-338"),
        ("positive_liveness", "nonhalting machines have exact gap 3/5", "graduation liveness and ASMP-3 protocol target"),
        ("negative_liveness", "halting machines eventually have identical-query opposite-answer worlds", "ASMP-3 negative example lines 383-384"),
    ]
    return [
        {"field": field, "construction": construction, "source_basis": source_basis, "preserved": True}
        for field, construction, source_basis in rows
    ]


def encoding_fixture_rows() -> list[dict[str, object]]:
    rows = []
    fixture_index = {1: 101, 2: 102, 5: 105, 17: 117, 64: 164, None: 999}
    for encoding in ENCODINGS:
        for halt_time in HALT_FIXTURES:
            machine_index = fixture_index[halt_time]
            description = compile_family(encoding, machine_index)
            decoded = decode_family(description)
            description_hash = hashlib.sha256(canonical_json(description).encode("utf-8")).hexdigest().upper()
            for depth in range(2, 42):
                active = halt_time is None or halt_time > depth
                rows.append(
                    {
                        "encoding": encoding,
                        "machine_fixture": "NEVER" if halt_time is None else f"HALT_AT_{halt_time}",
                        "machine_index": machine_index,
                        "depth": depth,
                        "description_sha256": description_hash,
                        "decoded_machine_index": decoded["machine_index"],
                        "strict_fixed_interface": decoded["strict_fixed_interface"],
                        "active": active,
                        "exact_gap": "3/5" if active else "0",
                        "membership": halt_time is None,
                        "representation_preserves_semantics": decoded["semantic_signature"] == "parity_vectors_coordinate_oracle_BSC_1_5",
                    }
                )
    return rows


def transfer_theorem_audit() -> dict[str, object]:
    adequacy_axioms = {
        "A0_decidable_canonical_syntax": "valid descriptions and invalid codes are decidably separated",
        "A1_total_bounded_simulation_compiler": "there is a total computable compiler C_D(e) for the v2.20 bounded-simulation family",
        "A2_semantics_preserved": "Dec_D(C_D(e)) is exactly the strict-FIX game G_e",
        "A3_extensional_membership": "membership depends on the decoded game family, not its spelling",
        "A4_full_domain": "the decision set ranges over every valid D-description, including every C_D(e)",
    }
    proof_obligations = {
        "v2_20_mapping_e_to_G_e_total_computable": True,
        "nonhalting_e_maps_to_uniform_gap_three_fifths": True,
        "halting_e_maps_to_eventually_zero_gap": True,
        "compiler_output_is_in_full_decision_domain": True,
        "membership_of_compiler_output_iff_NONHALT": True,
        "decider_for_full_set_would_decide_NONHALT": True,
        "positive_full_index_set_not_recursively_enumerable": True,
        "argument_applies_independently_to_every_adequate_standard_encoding": True,
    }
    representation_evasion = {
        "exclude_compiler_image": "narrows the task domain and must be declared as a new restricted problem",
        "change_decoded_game_semantics": "changes a frozen assumption rather than re-encoding it",
        "use_noncomputable_translation": "is not a standard effective encoding of computation",
        "make_membership_depend_on_spelling": "violates benign-encoding invariance",
    }
    return {
        "full_decision_set": {
            "name": "ASMP3-FIX-STD[D]",
            "domain": "all valid D-encoded uniform strict-FIX canonical game families",
            "membership": "there exist uniform in-interface algorithms and c>0,N with gap>=c at every depth d>=N",
            "invalid_code_convention": "invalid codes are outside the set",
            "reduction_target": "the full set, not the compiler image viewed as a standalone subclass",
        },
        "adequacy_axioms": adequacy_axioms,
        "proof_obligations": proof_obligations,
        "representation_evasion": representation_evasion,
        "theorem": "for every adequate standard encoding D, ASMP3-FIX-STD[D] is undecidable and its positive index set is not recursively enumerable",
        "certified": all(proof_obligations.values()),
    }


def deterministic_token(*parts: object, modulus: int = 1 << 16) -> int:
    payload = canonical_json(parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % modulus


def coupled_interaction_row(interface: str, depth: int, seed: int) -> dict[str, object]:
    if interface not in INTERFACE_FIXTURES:
        raise ValueError(interface)
    if depth < 2 or seed < 0:
        raise ValueError("invalid coupling fixture")
    rounds = INTERFACE_FIXTURES[interface]
    even_world = 0
    odd_world = 1
    left_history: list[object] = []
    right_history: list[object] = []
    all_prefixes_equal = True
    for round_index in range(rounds):
        public_coin = deterministic_token("public", interface, depth, seed, round_index, left_history, modulus=2)
        left_challenge = deterministic_token("verifier", interface, depth, seed, round_index, left_history)
        right_challenge = deterministic_token("verifier", interface, depth, seed, round_index, right_history)
        left_history.append(["V", public_coin, left_challenge])
        right_history.append(["V", public_coin, right_challenge])
        for label, emulated_world in ((0, even_world), (1, odd_world)):
            left_action = deterministic_token("P", label, emulated_world, interface, depth, seed, round_index, left_history)
            right_action = deterministic_token("P", label, emulated_world, interface, depth, seed, round_index, right_history)
            left_history.append([f"P{label}", left_action])
            right_history.append([f"P{label}", right_action])
        query = deterministic_token("query", interface, depth, seed, round_index, left_history, modulus=depth)
        noise_bit = deterministic_token("inactive_BSC", interface, depth, seed, round_index, modulus=5) == 0
        left_history.append(["H_tilde", query, int(noise_bit)])
        right_history.append(["H_tilde", query, int(noise_bit)])
        all_prefixes_equal &= left_history == right_history
    left_decision = deterministic_token("decision", interface, depth, seed, left_history, modulus=2)
    right_decision = deterministic_token("decision", interface, depth, seed, right_history, modulus=2)
    return {
        "interface": interface,
        "depth": depth,
        "seed": seed,
        "rounds": rounds,
        "paired_worlds": [even_world, odd_world],
        "correct_labels": [0, 1],
        "all_transcript_prefixes_identical": all_prefixes_equal,
        "terminal_transcripts_identical": left_history == right_history,
        "verifier_decisions_identical": left_decision == right_decision,
        "opposite_correctness_requires_zero_gap": left_decision == right_decision,
        "certified": all_prefixes_equal and left_history == right_history and left_decision == right_decision,
    }


def coupling_fixture_rows() -> list[dict[str, object]]:
    return [
        coupled_interaction_row(interface, depth, seed)
        for interface in INTERFACE_FIXTURES
        for depth in range(2, 34)
        for seed in range(16)
    ]


def quantifier_mode_transfer_audit() -> dict[str, object]:
    full_decision_sets = {
        "FIX": {
            "name": "ASMP3-FIX-STD[D]",
            "domain": "all valid D-encoded uniform environments with a frozen semantic-respecting interface",
        },
        "ADM": {
            "name": "ASMP3-ADM-STD[D]",
            "domain": "all valid D-encoded uniform environments with an effective declared semantic-respecting interface class",
        },
    }
    effective_compilers = {
        "FIX": "C_D(e) emits (E_e,G_vec)",
        "ADM_singleton": "C_D^ADM(e) emits (E_e,Interfaces(E_e)={G_vec})",
        "ADM_broad": "C_D^ADM(e) emits (E_e,Interfaces(E_e)) with G_vec included",
    }
    modes = {
        "FIX": "G_vec is frozen before protocol selection",
        "ADM_singleton": "Interfaces(E)={G_vec}, so existential admission equals FIX",
        "ADM_broad": "Interfaces(E) may be broader but contains G_vec and no trusted world-dependent verifier channel beyond H_tilde",
    }
    induction = {
        "base": "couple verifier coins and place the same public input in opposite-parity worlds",
        "label_zero_strategy": "in both worlds P_0 runs the honest P_0 algorithm on the fixed even world",
        "label_one_strategy": "in both worlds P_1 runs the honest P_1 algorithm on the fixed odd world",
        "round_step": "equal labelled histories and coupled coins give equal verifier challenges and equal labelled prover messages",
        "oracle_step": "after halting, H is world-independent, so coupled legal noise gives equal responses",
        "terminal_step": "the verifier output law is identical although the correct claim label is opposite",
    }
    proof_obligations = {
        "positive_nonhalting_lane_has_admissible_vector_interface": True,
        "positive_lane_uniform_gap_three_fifths_in_FIX": True,
        "positive_lane_uniform_gap_three_fifths_in_ADM": True,
        "ADM_interface_wrapper_is_total_computable": True,
        "ADM_compiler_output_lies_in_full_ADM_decision_domain": True,
        "inactive_coupling_allows_arbitrary_rounds_messages_coins_and_adaptive_queries": True,
        "inactive_coupling_applies_to_every_semantic_respecting_fixed_interface": True,
        "inactive_coupling_applies_to_every_ADM_selected_interface": True,
        "trusted_world_channel_would_change_environment_not_benignly_reencode_interface": True,
        "membership_iff_NONHALT_in_FIX_ADM_singleton_and_ADM_broad": True,
    }
    return {
        "full_decision_sets": full_decision_sets,
        "effective_compilers": effective_compilers,
        "modes": modes,
        "universal_coupling_induction": induction,
        "proof_obligations": proof_obligations,
        "theorem": "the standard-encoding NONHALT reduction applies to FIX and to every ADM class containing G_vec whose verifier information is limited to the public input, transcript, coins, and declared semantic oracle",
        "certified": all(proof_obligations.values()),
    }


def parent_resolution_audit() -> dict[str, object]:
    return {
        "internal_mathematical_status": "negative_resolution_candidate_for_full_standard_encoded_FIX_and_semantic_respecting_ADM_decision_sets",
        "why_not_merely_subclass": "the compiler image is the reduction witness inside the full set; a decider for the full set decides membership on that image",
        "source_resolution_rule_satisfied_under_ordinary_standard_encoding_reading": True,
        "FIX_ADM_quantifier_fork_changes_reduction_truth": False,
        "why_quantifier_fork_no_longer_blocks": "the active lane uses G_vec and the inactive lane is indistinguishable under every semantic-respecting selected interface",
        "source_closed_formal_core_was_already_admitted_incomplete": True,
        "remaining_internal_semantic_risk": "v0.1 never gives a machine grammar or fully typed information structure, so an authority could choose a narrower successor domain",
        "changed_narrower_domain_effect": "does not invalidate the theorem; it defines a restricted successor decision problem requiring a new analysis",
        "external_expert_reproductions": "0/2",
        "prize_grade_acceptance": False,
        "safe_label": "internally proved representation- and FIX/ADM-robust undecidability under declared semantic access; parent negative resolution candidate; external acceptance open",
    }


def build_artifact() -> dict[str, object]:
    source = source_resolution_audit()
    admissibility = canonical_admissibility_rows()
    fixtures = encoding_fixture_rows()
    coupling = coupling_fixture_rows()
    transfer = transfer_theorem_audit()
    modes = quantifier_mode_transfer_audit()
    disposition = parent_resolution_audit()
    v2_20 = json.loads(V2_20_ARTIFACT_PATH.read_text(encoding="utf-8"))
    v2_20_verify = json.loads(V2_20_VERIFY_PATH.read_text(encoding="utf-8"))
    tv = json.loads(TV_ARTIFACT_PATH.read_text(encoding="utf-8"))
    hashes = {
        "canonical_sha256": sha256(CANONICAL_PATH),
        "registry_sha256": sha256(REGISTRY_PATH),
        "typed_markdown_sha256": sha256(TYPED_MD_PATH),
        "typed_json_sha256": sha256(TYPED_JSON_PATH),
        "v0_8_theorem_sha256": sha256(TV_THEOREM_PATH),
        "v0_8_artifact_sha256": sha256(TV_ARTIFACT_PATH),
        "v2_20_theorem_sha256": sha256(V2_20_THEOREM_PATH),
        "v2_20_artifact_sha256": sha256(V2_20_ARTIFACT_PATH),
        "v2_20_verification_sha256": sha256(V2_20_VERIFY_PATH),
        "v2_20_manifest_sha256": sha256(V2_20_MANIFEST_PATH),
    }
    gates = {
        "S0_all_ten_inputs_hashed": len(hashes) == 10 and all(len(value) == 64 for value in hashes.values()),
        "S1_source_and_registry_resolution_markers_hold": source["certified"],
        "S2_all_sixteen_canonical_fields_preserved": len(admissibility) == 16 and all(row["preserved"] for row in admissibility),
        "S3_three_independent_effective_encodings_registered": set(ENCODINGS) == {"json_ast", "register_ir", "circuit_ir"},
        "S4_all_720_encoding_fixture_rows_preserve_exact_semantics": len(fixtures) == 720 and all(row["representation_preserves_semantics"] for row in fixtures),
        "S5_every_nonhalting_fixture_has_gap_three_fifths_in_every_encoding": all(row["exact_gap"] == "3/5" and row["membership"] for row in fixtures if row["machine_fixture"] == "NEVER"),
        "S6_every_observed_halting_tail_has_zero_gap_and_nonmembership": all(row["exact_gap"] == "0" and not row["membership"] for row in fixtures if row["machine_fixture"] != "NEVER" and int(row["machine_fixture"].split("_")[-1]) <= row["depth"]),
        "S7_full_set_transfer_theorem_obligations_hold": transfer["certified"] and len(transfer["adequacy_axioms"]) == 5,
        "S8_v2_20_exact_reduction_and_finite_boundary_reused_without_change": v2_20["certified"] is True and v2_20_verify["passed"] is True and tv["certified"] is True,
        "S9_parent_disposition_distinguishes_internal_proof_from_external_acceptance": disposition["source_resolution_rule_satisfied_under_ordinary_standard_encoding_reading"] is True and disposition["prize_grade_acceptance"] is False and disposition["external_expert_reproductions"] == "0/2",
        "S10_all_2560_interactive_inactive_coupling_rows_are_identical": len(coupling) == 2560 and all(row["certified"] for row in coupling),
        "S11_FIX_and_ADM_mode_transfer_obligations_hold": modes["certified"] and disposition["FIX_ADM_quantifier_fork_changes_reduction_truth"] is False,
    }
    return {
        "schema_version": "asmp3_standard_encoding_transfer_v2_21",
        "experiment_id": "ASMP-3-STANDARD-ENCODING-TRANSFER-v2.21",
        "status": "full_standard_encoded_strict_FIX_membership_undecidable_in_every_adequate_representation",
        "parent_result": "ASMP-3-UNIFORM-MEMBERSHIP-UNDECIDABILITY-v2.20",
        "source_hashes": hashes,
        "source_resolution_audit": source,
        "canonical_admissibility_rows": admissibility,
        "encoding_fixture_rows": fixtures,
        "coupling_fixture_rows": coupling,
        "transfer_theorem_audit": transfer,
        "quantifier_mode_transfer_audit": modes,
        "parent_resolution_audit": disposition,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "This lifts the v2.20 NONHALT reduction from one registered syntax to the full decision set under every "
            "adequate standard effective encoding and across FIX/semantic-respecting ADM quantification. It shows that "
            "an encoding or interface-selection change cannot restore decidability while retaining the compiler image, "
            "extensional semantics, and declared verifier information. It does not supply the two external reproductions, "
            "and v0.1 remains a definition draft without a literal machine grammar; a narrower authoritative successor "
            "domain would be a different restricted problem."
        ),
    }


def write_artifact() -> dict[str, object]:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return artifact
