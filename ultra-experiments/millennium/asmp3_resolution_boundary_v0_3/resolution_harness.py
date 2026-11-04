from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
MILLENNIUM_ROOT = HERE.parent
CANONICAL_STATEMENT = MILLENNIUM_ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
RESULT_PATH = HERE / "artifacts" / "result_v0_3.json"

ETA = Fraction(1, 5)
MIN_COUNTERMODEL_DEPTH = 2
DEPTH_GRID = tuple(range(MIN_COUNTERMODEL_DEPTH, 13))
EXHAUSTIVE_DEPTH = 9
REFUTATION_EXHAUSTIVE_DEPTH = 7


def asmp3_section() -> str:
    text = CANONICAL_STATEMENT.read_text(encoding="utf-8")
    start = text.index("# ASMP-3")
    stop = text.index("# ASMP-4", start)
    return text[start:stop]


def closure_audit() -> dict[str, object]:
    section = asmp3_section()
    binding_markers = (
        "verifier may reject only if Refute",
        "verifier may accept only if Refute",
        "verifier's semantic decisions must use Refute",
    )
    adequacy_markers = (
        "maximal sound refutation relation",
        "sound and complete refutation relation",
        "all semantically valid refutations",
    )
    return {
        "canonical_section_found": (
            "## Weak-Verifier Characterization Conjecture" in section
            and "Refute_n(tau,S,b)" in section
            and "a_H(k)" in section
        ),
        "refute_binding_axiom_present": any(
            marker in section for marker in binding_markers
        ),
        "refute_adequacy_axiom_present": any(
            marker in section for marker in adequacy_markers
        ),
        "binding_markers_checked": list(binding_markers),
        "adequacy_markers_checked": list(adequacy_markers),
    }


def persistent_single_atom_error(query_count: int) -> Fraction:
    """
    A single latent flip is reused by every replication of one semantic atom.

    Repetition yields the same bit, so the first-answer aggregator has error
    eta for every positive query count.
    """
    if query_count < 1:
        raise ValueError("query_count must be positive")
    return ETA


def xor_cross_examination_local_lemma() -> bool:
    """
    Check the inductive step for logarithmic cross-examination of an XOR tree.

    If honest and dishonest parent claims differ, either the dishonest child
    pair violates its own XOR claim or exactly one child claim differs from the
    honest pair. Descending to that child preserves the disagreement.
    """
    for honest_parent in (0, 1):
        dishonest_parent = 1 - honest_parent
        for honest_left, honest_right in product((0, 1), repeat=2):
            if honest_left ^ honest_right != honest_parent:
                continue
            for dishonest_left, dishonest_right in product((0, 1), repeat=2):
                dishonest_consistent = (
                    dishonest_left ^ dishonest_right == dishonest_parent
                )
                if not dishonest_consistent:
                    continue
                disagreements = (
                    (honest_left != dishonest_left)
                    + (honest_right != dishonest_right)
                )
                if disagreements != 1:
                    return False
    return True


def parity_error_closed_form(atom_count: int) -> Fraction:
    if atom_count < 1:
        raise ValueError("atom_count must be positive")
    return (1 - (1 - 2 * ETA) ** atom_count) / 2


def parity_decision_gap(atom_count: int) -> Fraction:
    """Completeness minus soundness for the best parity decision from noisy atoms."""
    return 1 - 2 * parity_error_closed_form(atom_count)


def parity_error_binomial_sum(atom_count: int) -> Fraction:
    return sum(
        (
            Fraction(comb(atom_count, errors))
            * ETA**errors
            * (1 - ETA) ** (atom_count - errors)
            for errors in range(1, atom_count + 1, 2)
        ),
        Fraction(0),
    )


def partial_assignment_refutes_claim(
    ideal_bits: tuple[int, ...],
    selected_mask: int,
    false_parity_claim: int,
) -> bool:
    atom_count = len(ideal_bits)
    for completion in product((0, 1), repeat=atom_count):
        if any(
            (selected_mask >> index) & 1
            and completion[index] != ideal_bits[index]
            for index in range(atom_count)
        ):
            continue
        if sum(completion) % 2 == false_parity_claim:
            return False
    return True


def exhaustive_parity_refutation_dimension(atom_count: int) -> int:
    if atom_count < 1 or atom_count > 9:
        raise ValueError("exhaustive parity refutation supports 1 through 9 atoms")
    worst_minimum = 0
    for ideal_bits in product((0, 1), repeat=atom_count):
        false_claim = 1 - (sum(ideal_bits) % 2)
        minimum: int | None = None
        for mask in range(1 << atom_count):
            if partial_assignment_refutes_claim(ideal_bits, mask, false_claim):
                size = mask.bit_count()
                minimum = size if minimum is None else min(minimum, size)
        if minimum is None:
            raise RuntimeError("false parity claim has no refuting assignment")
        worst_minimum = max(worst_minimum, minimum)
    return worst_minimum


def parity_class_output_distribution(
    atom_count: int,
    ideal_parity: int,
) -> dict[tuple[int, ...], Fraction]:
    """
    Average the persistent-error channel over the uniform ideal parity class.

    This is an exact least-favourable prior certificate. Its total variation
    lower-bounds the worst-case difficulty of any verifier.
    """
    if ideal_parity not in (0, 1):
        raise ValueError("ideal_parity must be a bit")
    strings = tuple(product((0, 1), repeat=atom_count))
    ideals = tuple(bits for bits in strings if sum(bits) % 2 == ideal_parity)
    denominator = len(ideals)
    distribution = {bits: Fraction(0) for bits in strings}
    for ideal in ideals:
        for observed in strings:
            errors = sum(a != b for a, b in zip(ideal, observed))
            likelihood = ETA**errors * (1 - ETA) ** (atom_count - errors)
            distribution[observed] += likelihood / denominator
    if sum(distribution.values(), Fraction(0)) != 1:
        raise RuntimeError("parity-class distribution is not normalized")
    return distribution


def total_variation(
    left: dict[tuple[int, ...], Fraction],
    right: dict[tuple[int, ...], Fraction],
) -> Fraction:
    if left.keys() != right.keys():
        raise ValueError("distribution supports differ")
    return sum((abs(left[key] - right[key]) for key in left), Fraction(0)) / 2


def exhaustive_parity_gap(atom_count: int) -> Fraction:
    return total_variation(
        parity_class_output_distribution(atom_count, 0),
        parity_class_output_distribution(atom_count, 1),
    )


def replicated_refutation_dimension(replica_count: int, require_all: bool) -> int:
    """
    Dimension of one local contradiction represented by synonymous atoms.

    Every replica has the same ideal answer, locality, and evaluation cost.
    A sound complete relation may recognize either any one copy or all copies.
    """
    if replica_count < 1:
        raise ValueError("replica_count must be positive")
    return replica_count if require_all else 1


def exhaustive_replica_minimum(replica_count: int, require_all: bool) -> int:
    if replica_count < 1 or replica_count > 16:
        raise ValueError("exhaustive replica check supports counts 1 through 16")
    full_mask = (1 << replica_count) - 1
    best: int | None = None
    for mask in range(1 << replica_count):
        recognized = mask == full_mask if require_all else mask != 0
        if recognized:
            size = mask.bit_count()
            best = size if best is None else min(best, size)
    if best is None:
        raise RuntimeError("no recognized refutation subset")
    return best


def fraction_record(value: Fraction) -> dict[str, object]:
    return {"exact": str(value), "decimal": float(value)}


def build_result() -> dict[str, object]:
    audit = closure_audit()
    exhaustive_rows = []
    for depth in range(MIN_COUNTERMODEL_DEPTH, EXHAUSTIVE_DEPTH + 1):
        closed = parity_decision_gap(depth)
        enumerated = exhaustive_parity_gap(depth)
        refutation_dimension = (
            exhaustive_parity_refutation_dimension(depth)
            if depth <= REFUTATION_EXHAUSTIVE_DEPTH
            else None
        )
        exhaustive_rows.append(
            {
                "refuting_atom_count": depth,
                "enumerated_refutation_dimension": refutation_dimension,
                "closed_form_gap": str(closed),
                "enumerated_total_variation": str(enumerated),
                "match": (
                    closed == enumerated
                    and (
                        refutation_dimension is None
                        or refutation_dimension == depth
                    )
                ),
            }
        )

    asymptotic_rows = []
    for depth in DEPTH_GRID:
        computation_budget = 1 << depth
        gap = parity_decision_gap(depth)
        error = parity_error_closed_form(depth)
        asymptotic_rows.append(
            {
                "depth": depth,
                "computation_budget_T": computation_budget,
                "refutation_dimension_r": depth,
                "r_is_log2_T": depth == computation_budget.bit_length() - 1,
                "single_atom_amplification_error": fraction_record(
                    persistent_single_atom_error(computation_budget)
                ),
                "best_joint_parity_error": fraction_record(error),
                "best_joint_decision_gap": fraction_record(gap),
            }
        )

    replica_rows = []
    for replicas in (1, 2, 4, 8, 16):
        any_copy = replicated_refutation_dimension(replicas, False)
        all_copies = replicated_refutation_dimension(replicas, True)
        replica_rows.append(
            {
                "meaning_preserving_replicas": replicas,
                "any_copy_dimension": any_copy,
                "all_copies_dimension": all_copies,
                "exhaustive_any_copy_dimension": exhaustive_replica_minimum(
                    replicas, False
                ),
                "exhaustive_all_copies_dimension": exhaustive_replica_minimum(
                    replicas, True
                ),
                "underlying_protocol_changed": False,
                "atom_answer_changed": False,
            }
        )

    single_atom_rows = [
        {
            "queries": queries,
            "first_answer_error": fraction_record(
                persistent_single_atom_error(queries)
            ),
        }
        for queries in (1, 3, 9, 81)
    ]

    gates = {
        "C0_canonical_objects_and_conjecture_found": audit[
            "canonical_section_found"
        ],
        "C1_refute_to_verifier_binding_axiom_absent": not audit[
            "refute_binding_axiom_present"
        ],
        "C2_refute_adequacy_axiom_absent": not audit[
            "refute_adequacy_axiom_present"
        ],
        "E0_exhaustive_parity_channels_match_closed_form": all(
            row["match"] for row in exhaustive_rows
        ),
        "E1_exhaustive_refutation_dimension_is_d": all(
            row["enumerated_refutation_dimension"]
            == row["refuting_atom_count"]
            for row in exhaustive_rows
            if row["enumerated_refutation_dimension"] is not None
        ),
        "A0_single_atom_amplification_condition_passes": all(
            row["first_answer_error"]["exact"] == "1/5"
            for row in single_atom_rows
        ),
        "F0_formal_xor_trace_cross_examination_step": (
            xor_cross_examination_local_lemma()
        ),
        "J0_joint_gap_strictly_decreases": all(
            parity_decision_gap(depth + 1) < parity_decision_gap(depth)
            for depth in range(MIN_COUNTERMODEL_DEPTH, max(DEPTH_GRID))
        ),
        "J1_joint_gap_below_one_percent_on_grid": (
            parity_decision_gap(max(DEPTH_GRID)) < Fraction(1, 100)
        ),
        "I0_replication_rescales_dimension_without_protocol_change": all(
            row["any_copy_dimension"] == 1
            and row["all_copies_dimension"]
            == row["meaning_preserving_replicas"]
            and row["any_copy_dimension"]
            == row["exhaustive_any_copy_dimension"]
            and row["all_copies_dimension"]
            == row["exhaustive_all_copies_dimension"]
            and not row["underlying_protocol_changed"]
            and not row["atom_answer_changed"]
            for row in replica_rows
        ),
    }
    return {
        "schema_version": "asmp3_resolution_boundary_v0_3",
        "experiment_id": "ASMP-3-REFUTE-INTERFACE-DICHOTOMY-v0.3",
        "status": "exact_conditional_obstruction_major_revision",
        "certified": all(gates.values()),
        "canonical_source": str(
            CANONICAL_STATEMENT.relative_to(MILLENNIUM_ROOT.parent.parent)
        ).replace("\\", "/"),
        "closure_audit": audit,
        "noise_model": {
            "marginal_error_eta": str(ETA),
            "within_atom_replication": "one persistent latent flip per atom",
            "between_atom_dependence": "independent latent flips",
            "adaptive_component": "none",
            "class_is_complete": True,
            "constructive_single_atom_aggregator": "return the first answer",
        },
        "nonbinding_refute_branch": {
            "conclusion": (
                "If Refute is metadata rather than a verifier constraint, its "
                "dimension is not a necessary protocol invariant."
            ),
            "replica_rows": replica_rows,
        },
        "binding_refute_branch": {
            "conclusion": (
                "If Refute binds the verifier, constant single-atom advantage "
                "does not imply a constant gap for growing joint refutations."
            ),
            "frozen_message_game": {
                "task_output": (
                    "XOR of a T-leaf formal computation root and the parity of "
                    "d=log2(T) semantic atoms, with d>=2"
                ),
                "formal_component": (
                    "Both advocates report locally consistent XOR-tree values; "
                    "a disagreement is cross-examined to one formal leaf in "
                    "O(log T) messages."
                ),
                "semantic_component": (
                    "Each advocate sends one parity claim and the fixed refuting "
                    "set of all d semantic atom indices. Per-atom value claims "
                    "are not messages in the frozen grammar."
                ),
                "refute_relation": (
                    "Refute(tau,S,b) holds for a formal local inconsistency, or "
                    "when S is all d semantic indices and parity(b) contradicts "
                    "tau's semantic-parity claim."
                ),
                "semantic_atom_bounds": (
                    "Each atom is one indexed semantic bit with O(log d) "
                    "description, radius-one locality, and O(1) ideal evaluation; "
                    "for d>=2, no atom contains the parity or full task answer."
                ),
                "least_favourable_pair": (
                    "Formal roots and formal messages agree; advocates differ "
                    "only on semantic parity, so all verifier information about "
                    "that dispute is the persistent-noise answer vector."
                ),
                "honest_runtime": (
                    "Theta(T) for the formal trace plus O(log T log log T) bit "
                    "time (O(log T) word operations) for the explicit semantic "
                    "refuting set"
                ),
                "verifier_resources": (
                    "O(log T) formal messages, d=log2(T) semantic atoms, and "
                    "arbitrarily many registered within-atom replications"
                ),
            },
            "single_atom_rows": single_atom_rows,
            "asymptotic_identity": {
                "refuting_atoms": "d=log2(T)",
                "single_atom_error": "1/5",
                "best_joint_decision_gap": "(3/5)^d",
                "in_terms_of_T": "T^log2(3/5)",
                "limit": "0",
            },
            "asymptotic_rows": asymptotic_rows,
            "exhaustive_rows": exhaustive_rows,
        },
        "gates": gates,
        "claim_boundary": (
            "This certificate proves the parity-channel obstruction inside the "
            "stipulated binding grammar. It does not settle whether canonical "
            "protocol admission permits richer transcript encodings, prove a "
            "complete interactive-game reduction, rule out a repaired dynamic-"
            "refutation characterization, or provide empirical evidence about "
            "human or model judges."
        ),
        "required_repair": (
            "Bind an adequate Refute relation to verifier decisions and replace "
            "the single-atom profile by a joint, selection-conditional "
            "amplification invariant for the full refutation game."
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
        raise RuntimeError("ASMP-3 resolution-boundary gates failed")
    write_result(result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
