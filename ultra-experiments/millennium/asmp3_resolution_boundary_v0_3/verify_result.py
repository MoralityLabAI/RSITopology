from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "result_v0_3.json"
VERIFICATION_PATH = HERE / "artifacts" / "verification_v0_3.json"
CANONICAL = HERE.parent / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
ETA = Fraction(1, 5)


def parse_fraction(record: dict[str, object]) -> Fraction:
    return Fraction(str(record["exact"]))


def direct_parity_error(atom_count: int) -> Fraction:
    return sum(
        (
            Fraction(comb(atom_count, errors))
            * ETA**errors
            * (1 - ETA) ** (atom_count - errors)
            for errors in range(1, atom_count + 1, 2)
        ),
        Fraction(0),
    )


def direct_total_variation(atom_count: int) -> Fraction:
    strings = tuple(product((0, 1), repeat=atom_count))
    classes = {
        parity: tuple(bits for bits in strings if sum(bits) % 2 == parity)
        for parity in (0, 1)
    }
    distributions: dict[int, dict[tuple[int, ...], Fraction]] = {}
    for parity in (0, 1):
        distribution = {observed: Fraction(0) for observed in strings}
        for ideal in classes[parity]:
            for observed in strings:
                errors = sum(a != b for a, b in zip(ideal, observed))
                distribution[observed] += (
                    ETA**errors
                    * (1 - ETA) ** (atom_count - errors)
                    / len(classes[parity])
                )
        distributions[parity] = distribution
    return sum(
        (
            abs(distributions[0][observed] - distributions[1][observed])
            for observed in strings
        ),
        Fraction(0),
    ) / 2


def direct_refutation_dimension(atom_count: int) -> int:
    worst = 0
    for ideal in product((0, 1), repeat=atom_count):
        false_claim = 1 - (sum(ideal) % 2)
        best: int | None = None
        for mask in range(1 << atom_count):
            refutes = True
            for completion in product((0, 1), repeat=atom_count):
                if any(
                    (mask >> index) & 1 and completion[index] != ideal[index]
                    for index in range(atom_count)
                ):
                    continue
                if sum(completion) % 2 == false_claim:
                    refutes = False
                    break
            if refutes:
                size = mask.bit_count()
                best = size if best is None else min(best, size)
        if best is None:
            raise RuntimeError("missing parity refutation")
        worst = max(worst, best)
    return worst


def direct_replica_minimum(replica_count: int, require_all: bool) -> int:
    recognized_sizes = []
    for mask in range(1 << replica_count):
        recognized = (
            mask == (1 << replica_count) - 1 if require_all else mask != 0
        )
        if recognized:
            recognized_sizes.append(mask.bit_count())
    return min(recognized_sizes)


def direct_xor_local_lemma() -> bool:
    for honest_parent in (0, 1):
        dishonest_parent = 1 - honest_parent
        for honest in product((0, 1), repeat=2):
            if honest[0] ^ honest[1] != honest_parent:
                continue
            for dishonest in product((0, 1), repeat=2):
                if dishonest[0] ^ dishonest[1] != dishonest_parent:
                    continue
                if sum(a != b for a, b in zip(honest, dishonest)) != 1:
                    return False
    return True


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    canonical = CANONICAL.read_text(encoding="utf-8")
    start = canonical.index("# ASMP-3")
    stop = canonical.index("# ASMP-4", start)
    section = canonical[start:stop]

    checks: dict[str, bool] = {}
    checks["schema"] = (
        result["schema_version"] == "asmp3_resolution_boundary_v0_3"
        and result["experiment_id"]
        == "ASMP-3-REFUTE-INTERFACE-DICHOTOMY-v0.3"
    )
    checks["canonical_conjecture_present"] = (
        "## Weak-Verifier Characterization Conjecture" in section
        and "Refute_n(tau,S,b)" in section
        and "a_H(k)" in section
    )
    checks["binding_axiom_absent"] = (
        "verifier may reject only if Refute" not in section
        and "verifier's semantic decisions must use Refute" not in section
    )
    checks["adequacy_axiom_absent"] = (
        "maximal sound refutation relation" not in section
        and "sound and complete refutation relation" not in section
    )

    binding = result["binding_refute_branch"]
    checks["single_atom_error"] = all(
        parse_fraction(row["first_answer_error"]) == ETA
        for row in binding["single_atom_rows"]
    )
    checks["formal_xor_cross_examination"] = direct_xor_local_lemma()
    checks["message_grammar_is_frozen"] = (
        "Per-atom value claims are not messages"
        in binding["frozen_message_game"]["semantic_component"]
        and "d=log2(T) semantic atoms"
        in binding["frozen_message_game"]["verifier_resources"]
    )
    checks["refute_and_atom_bounds_are_explicit"] = (
        "S is all d semantic indices"
        in binding["frozen_message_game"]["refute_relation"]
        and "no atom contains the parity or full task answer"
        in binding["frozen_message_game"]["semantic_atom_bounds"]
    )
    checks["binomial_identity"] = all(
        parse_fraction(row["best_joint_parity_error"])
        == direct_parity_error(int(row["depth"]))
        for row in binding["asymptotic_rows"]
    )
    checks["gap_identity"] = all(
        parse_fraction(row["best_joint_decision_gap"])
        == (1 - 2 * ETA) ** int(row["depth"])
        for row in binding["asymptotic_rows"]
    )
    checks["independent_tv_enumeration"] = all(
        Fraction(row["enumerated_total_variation"])
        == direct_total_variation(int(row["refuting_atom_count"]))
        == Fraction(row["closed_form_gap"])
        for row in binding["exhaustive_rows"]
    )
    checks["independent_refutation_dimension"] = all(
        int(row["enumerated_refutation_dimension"])
        == direct_refutation_dimension(int(row["refuting_atom_count"]))
        == int(row["refuting_atom_count"])
        for row in binding["exhaustive_rows"]
        if row["enumerated_refutation_dimension"] is not None
    )
    checks["joint_gap_tends_toward_zero"] = all(
        parse_fraction(binding["asymptotic_rows"][index + 1][
            "best_joint_decision_gap"
        ])
        < parse_fraction(binding["asymptotic_rows"][index][
            "best_joint_decision_gap"
        ])
        for index in range(len(binding["asymptotic_rows"]) - 1)
    )

    replica_rows = result["nonbinding_refute_branch"]["replica_rows"]
    checks["replica_dimensions"] = all(
        row["any_copy_dimension"]
        == direct_replica_minimum(int(row["meaning_preserving_replicas"]), False)
        == 1
        and row["all_copies_dimension"]
        == direct_replica_minimum(int(row["meaning_preserving_replicas"]), True)
        == row["meaning_preserving_replicas"]
        and row["underlying_protocol_changed"] is False
        and row["atom_answer_changed"] is False
        for row in replica_rows
    )
    checks["producer_gates"] = result["certified"] and all(
        result["gates"].values()
    )
    passed = all(checks.values())
    return {
        "schema_version": "asmp3_resolution_boundary_verification_v0_3",
        "verified_experiment_id": result["experiment_id"],
        "passed": passed,
        "checks": checks,
        "check_count": len(checks),
        "method": (
            "Independent JSON consumer with separate binomial, total-variation, "
            "powerset, and canonical-text computations; does not import the "
            "producer module."
        ),
    }


def main() -> None:
    verification = verify()
    VERIFICATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFICATION_PATH.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not verification["passed"]:
        raise RuntimeError("independent ASMP-3 verification failed")
    print(
        f"ASMP-3 independent verification passed: "
        f"{verification['check_count']}/{verification['check_count']}"
    )


if __name__ == "__main__":
    main()
