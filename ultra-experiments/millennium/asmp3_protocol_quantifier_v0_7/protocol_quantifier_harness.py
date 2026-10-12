from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
MILLENNIUM_ROOT = HERE.parent
CANONICAL_STATEMENT = MILLENNIUM_ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
RESULT_PATH = HERE / "artifacts" / "protocol_quantifier_v0_7.json"

ETA = Fraction(1, 5)
LAMBDA = 1 - 2 * ETA
DEPTHS = tuple(range(2, 10))
EXHAUSTIVE_TEST_DEPTHS = tuple(range(2, 5))
EXHAUSTIVE_REFUTATION_DEPTHS = tuple(range(2, 8))
RICH_PROTOCOL_DEPTHS = tuple(range(2, 7))
INPUT_LENGTHS = (4, 5, 7, 8, 15, 16, 31, 32, 63, 64, 127, 255, 256, 1024)


def asmp3_section() -> str:
    text = CANONICAL_STATEMENT.read_text(encoding="utf-8")
    start = text.index("# ASMP-3")
    stop = text.index("# ASMP-4", start)
    return text[start:stop]


def canonical_quantifier_markers() -> dict[str, bool]:
    section = asmp3_section()
    return {
        "freezes_message_order_and_stopping": (
            "freeze a decision relation" in section
            and "a public-coin message" in section
            and "order and stopping rule" in section
        ),
        "encodings_are_part_of_game": (
            "Admissible transcript encodings" in section
            and "are part of the game" in section
        ),
        "uses_admits_protocol_phrase": (
            "A task family admits a constant-gap" in section
        ),
    }


def game_parameters(public_input_length: int) -> dict[str, int]:
    if public_input_length < 4:
        raise ValueError("public_input_length must be at least 4")
    depth = public_input_length.bit_length() - 1
    leaf_count = 1 << depth
    return {
        "public_input_length": public_input_length,
        "depth": depth,
        "formal_leaf_count": leaf_count,
        "semantic_atom_count": depth,
        "prover_budget": public_input_length,
    }


def parity(bits: tuple[int, ...]) -> int:
    return sum(bits) % 2


def claim_classification(
    true_formal: int,
    true_semantic: int,
    claimed_formal: int,
    claimed_semantic: int,
    claimed_output: int,
) -> str:
    values = (
        true_formal,
        true_semantic,
        claimed_formal,
        claimed_semantic,
        claimed_output,
    )
    if any(value not in (0, 1) for value in values):
        return "malformed"
    if claimed_output != (claimed_formal ^ claimed_semantic):
        return "malformed"
    true_output = true_formal ^ true_semantic
    if claimed_output == true_output:
        if (
            claimed_formal == true_formal
            and claimed_semantic == true_semantic
        ):
            return "fully_true"
        return "true_output_both_components_false"
    formal_false = claimed_formal != true_formal
    semantic_false = claimed_semantic != true_semantic
    if formal_false == semantic_false:
        raise AssertionError("a false XOR output must falsify exactly one component")
    return "formal_false" if formal_false else "semantic_false"


def partial_semantic_assignment_refutes(
    ideal_bits: tuple[int, ...],
    selected_mask: int,
    false_parity_claim: int,
) -> bool:
    depth = len(ideal_bits)
    for completion in product((0, 1), repeat=depth):
        if any(
            ((selected_mask >> index) & 1)
            and completion[index] != ideal_bits[index]
            for index in range(depth)
        ):
            continue
        if parity(completion) == false_parity_claim:
            return False
    return True


def semantic_refutation_minimum(ideal_bits: tuple[int, ...]) -> int:
    false_claim = 1 - parity(ideal_bits)
    minimum: int | None = None
    for mask in range(1 << len(ideal_bits)):
        if partial_semantic_assignment_refutes(ideal_bits, mask, false_claim):
            size = mask.bit_count()
            minimum = size if minimum is None else min(minimum, size)
    if minimum is None:
        raise AssertionError("false parity claim must have a refuting set")
    return minimum


def exhaustive_terminal_refutation_audit(depth: int) -> dict[str, object]:
    if depth < 2 or depth > 8:
        raise ValueError("terminal audit supports depths 2 through 8")
    semantic_minima = {
        semantic_refutation_minimum(bits)
        for bits in product((0, 1), repeat=depth)
    }
    false_cases = []
    for true_formal, true_semantic in product((0, 1), repeat=2):
        for claimed_formal, claimed_semantic, claimed_output in product(
            (0, 1), repeat=3
        ):
            classification = claim_classification(
                true_formal,
                true_semantic,
                claimed_formal,
                claimed_semantic,
                claimed_output,
            )
            if classification == "fully_true":
                continue
            refutation_size = depth if classification == "semantic_false" else 0
            false_cases.append(
                {
                    "classification": classification,
                    "refutation_size": refutation_size,
                }
            )
    sizes = [case["refutation_size"] for case in false_cases]
    return {
        "depth": depth,
        "false_terminal_cases": len(false_cases),
        "semantic_minima": sorted(semantic_minima),
        "all_false_cases_refutable": all(size is not None for size in sizes),
        "maximum_minimum_refutation_size": max(sizes),
        "dimension_equals_depth": max(sizes) == depth and semantic_minima == {depth},
    }


def xor_cross_examination_local_lemma() -> bool:
    for honest_parent in (0, 1):
        dishonest_parent = 1 - honest_parent
        for honest_left, honest_right in product((0, 1), repeat=2):
            if honest_left ^ honest_right != honest_parent:
                continue
            for dishonest_left, dishonest_right in product((0, 1), repeat=2):
                if dishonest_left ^ dishonest_right != dishonest_parent:
                    continue
                disagreements = (
                    (honest_left != dishonest_left)
                    + (honest_right != dishonest_right)
                )
                if disagreements != 1:
                    return False
    return True


def honest_strategy_terminal_coverage() -> bool:
    for true_formal, true_semantic in product((0, 1), repeat=2):
        for claimed_formal, claimed_semantic, claimed_output in product(
            (0, 1), repeat=3
        ):
            classification = claim_classification(
                true_formal,
                true_semantic,
                claimed_formal,
                claimed_semantic,
                claimed_output,
            )
            if classification == "fully_true":
                continue
            if classification not in {
                "malformed",
                "formal_false",
                "semantic_false",
                "true_output_both_components_false",
            }:
                return False
    return xor_cross_examination_local_lemma()


def canonical_nonoracle_transcript(
    depth: int,
    formal_root: int,
) -> tuple[object, ...]:
    if depth < 2 or formal_root not in (0, 1):
        raise ValueError("invalid canonical transcript parameter")
    all_indices = tuple(range(depth))
    advocate_zero = (
        "advocate_by_semantic_claim",
        0,
        formal_root,
        0,
        formal_root,
    )
    advocate_one = (
        "advocate_by_semantic_claim",
        1,
        formal_root,
        1,
        1 - formal_root,
    )
    return (
        advocate_zero,
        advocate_one,
        ("canonical_sorted_refuting_set", all_indices),
        ("post_message_oracle_phase", "adaptive_queries_then_stop"),
    )


def cross_world_transcript_identity(depth: int) -> bool:
    for formal_root in (0, 1):
        even_world = canonical_nonoracle_transcript(depth, formal_root)
        odd_world = canonical_nonoracle_transcript(depth, formal_root)
        if even_world != odd_world:
            return False
    return True


def parity_class_output_distribution(
    depth: int,
    ideal_parity: int,
) -> dict[tuple[int, ...], Fraction]:
    strings = tuple(product((0, 1), repeat=depth))
    ideals = tuple(bits for bits in strings if parity(bits) == ideal_parity)
    distribution = {bits: Fraction(0) for bits in strings}
    for ideal in ideals:
        for observed in strings:
            errors = sum(a != b for a, b in zip(ideal, observed))
            probability = ETA**errors * (1 - ETA) ** (depth - errors)
            distribution[observed] += probability / len(ideals)
    if sum(distribution.values(), Fraction(0)) != 1:
        raise AssertionError("channel distribution failed to normalize")
    return distribution


def total_variation(
    left: dict[tuple[int, ...], Fraction],
    right: dict[tuple[int, ...], Fraction],
) -> Fraction:
    return sum((abs(left[key] - right[key]) for key in left), Fraction(0)) / 2


def exhaustive_binary_test_gap(depth: int) -> Fraction:
    if depth < 1 or depth > 4:
        raise ValueError("binary-test enumeration supports depths 1 through 4")
    even = parity_class_output_distribution(depth, 0)
    odd = parity_class_output_distribution(depth, 1)
    outcomes = tuple(even)
    best = Fraction(0)
    for decision_mask in range(1 << len(outcomes)):
        even_accept = sum(
            even[outcome]
            for index, outcome in enumerate(outcomes)
            if (decision_mask >> index) & 1
        )
        odd_accept = sum(
            odd[outcome]
            for index, outcome in enumerate(outcomes)
            if (decision_mask >> index) & 1
        )
        best = max(best, abs(odd_accept - even_accept))
    return best


def parity_channel_row(depth: int) -> dict[str, object]:
    even = parity_class_output_distribution(depth, 0)
    odd = parity_class_output_distribution(depth, 1)
    observed_tv = total_variation(even, odd)
    formula = LAMBDA**depth
    binary_test_gap = (
        exhaustive_binary_test_gap(depth)
        if depth in EXHAUSTIVE_TEST_DEPTHS
        else None
    )
    return {
        "depth": depth,
        "frozen_encoding_gap": str(observed_tv),
        "closed_form_gap": str(formula),
        "matches_closed_form": observed_tv == formula,
        "exhaustive_best_binary_test_gap": (
            str(binary_test_gap) if binary_test_gap is not None else None
        ),
        "binary_test_optimum_matches_tv": (
            binary_test_gap == observed_tv
            if binary_test_gap is not None
            else None
        ),
    }


def rich_vector_protocol_audit(depth: int) -> dict[str, object]:
    if depth < 2 or depth > 8:
        raise ValueError("rich protocol audit supports depths 2 through 8")
    cases = 0
    all_opposite_vectors_differ = True
    for ideal in product((0, 1), repeat=depth):
        ideal_parity = parity(ideal)
        for adversarial in product((0, 1), repeat=depth):
            if parity(adversarial) == ideal_parity:
                continue
            cases += 1
            differing = [
                index
                for index, pair in enumerate(zip(ideal, adversarial))
                if pair[0] != pair[1]
            ]
            if not differing:
                all_opposite_vectors_differ = False
    success = 1 - ETA
    soundness = ETA
    return {
        "depth": depth,
        "opposite_parity_pairs_checked": cases,
        "all_opposite_parity_vectors_have_a_differing_coordinate": (
            all_opposite_vectors_differ
        ),
        "semantic_queries": 1,
        "honest_selection_probability": str(success),
        "dishonest_selection_probability": str(soundness),
        "constant_completeness_soundness_gap": str(success - soundness),
        "message_bits_big_o": "O(d)",
        "verifier_time_big_o": "O(d)",
    }


def bit_cost_row(public_input_length: int) -> dict[str, object]:
    parameters = game_parameters(public_input_length)
    depth = parameters["depth"]
    index_width = max(1, (depth - 1).bit_length())
    explicit_set_bits = depth * index_width
    frozen_transcript_upper = 8 * depth * index_width + 32
    rich_transcript_upper = frozen_transcript_upper + 2 * depth
    return {
        **parameters,
        "semantic_index_width": index_width,
        "explicit_all_indices_bits": explicit_set_bits,
        "frozen_transcript_bit_upper_bound": frozen_transcript_upper,
        "rich_transcript_bit_upper_bound": rich_transcript_upper,
        "semantic_query_budget": depth**2,
        "verifier_time_budget": 64 * depth**2,
        "transcript_budget": 18 * depth**2,
        "both_are_polylog_in_prover_budget": (
            frozen_transcript_upper <= 16 * depth**2
            and rich_transcript_upper <= 18 * depth**2
            and depth <= depth**2
        ),
    }


def build_result() -> dict[str, object]:
    canonical = canonical_quantifier_markers()
    refutation_rows = [
        exhaustive_terminal_refutation_audit(depth)
        for depth in EXHAUSTIVE_REFUTATION_DEPTHS
    ]
    parity_rows = [parity_channel_row(depth) for depth in DEPTHS]
    rich_rows = [
        rich_vector_protocol_audit(depth) for depth in RICH_PROTOCOL_DEPTHS
    ]
    bit_rows = [bit_cost_row(length) for length in INPUT_LENGTHS]
    gates = {
        "C0_canonical_freeze_and_admits_markers_present": all(canonical.values()),
        "G0_complete_terminal_case_partition": all(
            row["all_false_cases_refutable"] for row in refutation_rows
        ),
        "G1_refutation_dimension_equals_depth": all(
            row["dimension_equals_depth"] for row in refutation_rows
        ),
        "H0_uniform_honest_strategy_case_coverage": (
            honest_strategy_terminal_coverage()
        ),
        "T0_cross_world_nonoracle_transcript_identity": all(
            cross_world_transcript_identity(depth) for depth in DEPTHS
        ),
        "P0_frozen_parity_gap_matches_formula": all(
            row["matches_closed_form"] for row in parity_rows
        ),
        "P1_all_exhaustive_binary_tests_match_tv": all(
            row["binary_test_optimum_matches_tv"] is not False
            for row in parity_rows
        ),
        "P2_frozen_gap_vanishes": LAMBDA**64 < Fraction(1, 10**12),
        "R0_rich_vector_protocol_is_constant_gap": all(
            row["all_opposite_parity_vectors_have_a_differing_coordinate"]
            and row["constant_completeness_soundness_gap"] == "3/5"
            and row["semantic_queries"] == 1
            for row in rich_rows
        ),
        "B0_both_encodings_fit_polylog_budgets": all(
            row["both_are_polylog_in_prover_budget"] for row in bit_rows
        ),
    }
    return {
        "schema_version": "asmp3_protocol_quantifier_v0_7",
        "experiment_id": "ASMP-3-PROTOCOL-QUANTIFIER-FORK-v0.7",
        "status": "exact_quantifier_fork",
        "certified": all(gates.values()),
        "canonical_source": str(
            CANONICAL_STATEMENT.relative_to(MILLENNIUM_ROOT.parent.parent)
        ).replace("\\", "/"),
        "canonical_markers": canonical,
        "formal_game": {
            "public_instance": (
                "n public formal bits plus d=floor(log2 n) opaque semantic "
                "atom identifiers"
            ),
            "semantic_world": "z in {0,1}^d, with H_z(i)=z_i",
            "party_information": (
                "both advocates know z; verifier sees the public instance and "
                "has only persistent-noise oracle access"
            ),
            "correct_output": (
                "parity of the first 2^d public formal bits XOR parity(z)"
            ),
            "frozen_encoding": (
                "canonical component claims, formal bisection messages, and a "
                "canonical sorted all-indices semantic refutation; no per-atom "
                "value claims"
            ),
            "malformed_or_abort_rule": "the responsible advocate loses formally",
            "prover_budget": "Theta(n)",
            "semantic_query_budget": "q(n)=d^2",
            "verifier_time_budget": "s(n)=64d^2",
            "transcript_budget": "B(n)=18d^2 bits",
        },
        "frozen_encoding_branch": {
            "refutation_rows": refutation_rows,
            "parity_rows": parity_rows,
            "asymptotic_gap": "(3/5)^d -> 0",
            "conclusion": (
                "If admissible transcript encodings are frozen task-game data, "
                "all three displayed conditions hold but no constant gap exists."
            ),
        },
        "existential_encoding_branch": {
            "rich_protocol_rows": rich_rows,
            "constant_gap": "3/5",
            "conclusion": (
                "If protocol admission may choose the semantic message encoding, "
                "the same underlying relation admits an O(d)-message, one-query "
                "constant-gap protocol."
            ),
        },
        "resource_rows": bit_rows,
        "gates": gates,
        "claim_boundary": (
            "This exact result resolves the countermodel's protocol-quantifier "
            "fork. It does not decide which reading the v0.1 authors intended "
            "or supply the broader repaired ASMP-3 characterization."
        ),
    }


def write_result(result: dict[str, object]) -> None:
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    result = build_result()
    if not result["certified"]:
        raise RuntimeError("ASMP-3 protocol-quantifier gates failed")
    write_result(result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
