from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
MILLENNIUM_ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "protocol_quantifier_v0_7.json"
VERIFICATION_PATH = (
    HERE / "artifacts" / "protocol_quantifier_verification_v0_7.json"
)
CANONICAL = MILLENNIUM_ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"

ETA = Fraction(1, 5)
LAMBDA = Fraction(3, 5)


def bit_parity(bits: tuple[int, ...]) -> int:
    value = 0
    for bit in bits:
        value ^= bit
    return value


def channel_distribution(
    depth: int,
    ideal_parity: int,
) -> dict[tuple[int, ...], Fraction]:
    outputs = tuple(product((0, 1), repeat=depth))
    ideals = tuple(
        bits for bits in outputs if bit_parity(bits) == ideal_parity
    )
    distribution: dict[tuple[int, ...], Fraction] = {}
    for output in outputs:
        mass = Fraction(0)
        for ideal in ideals:
            errors = sum(a ^ b for a, b in zip(ideal, output))
            mass += ETA**errors * (1 - ETA) ** (depth - errors)
        distribution[output] = mass / len(ideals)
    return distribution


def distribution_tv(
    left: dict[tuple[int, ...], Fraction],
    right: dict[tuple[int, ...], Fraction],
) -> Fraction:
    return sum(abs(left[key] - right[key]) for key in left) / 2


def semantic_minimum(depth: int) -> int:
    ideal = (0,) * depth
    false_claim = 1
    for selected_size in range(depth + 1):
        for selected in product((0, 1), repeat=depth):
            if sum(selected) != selected_size:
                continue
            mask = tuple(bool(value) for value in selected)
            refutes = True
            for completion in product((0, 1), repeat=depth):
                if any(mask[i] and completion[i] != ideal[i] for i in range(depth)):
                    continue
                if bit_parity(completion) == false_claim:
                    refutes = False
                    break
            if refutes:
                return selected_size
    raise AssertionError("semantic falsehood had no refutation")


def canonical_markers() -> bool:
    text = CANONICAL.read_text(encoding="utf-8")
    start = text.index("# ASMP-3")
    stop = text.index("# ASMP-4", start)
    section = text[start:stop]
    return (
        "freeze a decision relation" in section
        and "order and stopping rule" in section
        and "Admissible transcript encodings" in section
        and "are part of the game" in section
        and "A task family admits a constant-gap" in section
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    frozen = result["frozen_encoding_branch"]
    extended = result["existential_encoding_branch"]
    parity_rows = frozen["parity_rows"]
    refutation_rows = frozen["refutation_rows"]
    rich_rows = extended["rich_protocol_rows"]
    resource_rows = result["resource_rows"]

    direct_tv_rows = []
    for row in parity_rows:
        depth = int(row["depth"])
        even = channel_distribution(depth, 0)
        odd = channel_distribution(depth, 1)
        direct_tv = distribution_tv(even, odd)
        direct_tv_rows.append(
            {
                "depth": depth,
                "direct_tv": str(direct_tv),
                "matches_artifact": (
                    direct_tv == Fraction(row["frozen_encoding_gap"])
                    == LAMBDA**depth
                ),
            }
        )

    checks = {
        "schema_and_experiment": (
            result["schema_version"] == "asmp3_protocol_quantifier_v0_7"
            and result["experiment_id"]
            == "ASMP-3-PROTOCOL-QUANTIFIER-FORK-v0.7"
            and result["status"] == "exact_quantifier_fork"
        ),
        "canonical_quantifier_markers": canonical_markers(),
        "independent_parity_tv": all(
            row["matches_artifact"] for row in direct_tv_rows
        ),
        "independent_refutation_dimension": all(
            semantic_minimum(int(row["depth"])) == int(row["depth"])
            == int(row["maximum_minimum_refutation_size"])
            and row["dimension_equals_depth"]
            for row in refutation_rows
        ),
        "rich_protocol_pair_counts": all(
            int(row["opposite_parity_pairs_checked"])
            == 2 ** (2 * int(row["depth"]) - 1)
            for row in rich_rows
        ),
        "rich_protocol_constant_gap": all(
            Fraction(row["honest_selection_probability"]) == 1 - ETA
            and Fraction(row["dishonest_selection_probability"]) == ETA
            and Fraction(row["constant_completeness_soundness_gap"])
            == 1 - 2 * ETA
            and int(row["semantic_queries"]) == 1
            for row in rich_rows
        ),
        "resource_scaling": all(
            int(row["formal_leaf_count"])
            == 1 << int(row["depth"])
            and int(row["formal_leaf_count"])
            <= int(row["public_input_length"])
            < 2 * int(row["formal_leaf_count"])
            and int(row["semantic_query_budget"]) == int(row["depth"]) ** 2
            and int(row["verifier_time_budget"]) == 64 * int(row["depth"]) ** 2
            and int(row["transcript_budget"]) == 18 * int(row["depth"]) ** 2
            and int(row["rich_transcript_bit_upper_bound"])
            <= int(row["transcript_budget"])
            and row["both_are_polylog_in_prover_budget"]
            for row in resource_rows
        ),
        "producer_gates": (
            result["certified"] and all(result["gates"].values())
        ),
        "claim_boundary_preserves_scope": (
            "does not decide which reading" in result["claim_boundary"]
        ),
    }
    verification = {
        "schema_version": "asmp3_protocol_quantifier_verification_v0_7",
        "verified_experiment_id": result["experiment_id"],
        "method": (
            "Independent JSON consumer with separate channel enumeration, "
            "subset-completion refutation search, protocol pair counting, and "
            "canonical-text checks; does not import the producer."
        ),
        "direct_tv_rows": direct_tv_rows,
        "checks": checks,
        "check_count": len(checks),
        "passed": all(checks.values()),
    }
    return verification


def main() -> None:
    verification = verify()
    VERIFICATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFICATION_PATH.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not verification["passed"]:
        failed = [
            name for name, passed in verification["checks"].items() if not passed
        ]
        raise SystemExit(f"ASMP-3 protocol-quantifier verification failed: {failed}")
    print(
        "ASMP-3 protocol-quantifier verification passed: "
        f"{verification['check_count']}/{verification['check_count']}"
    )


if __name__ == "__main__":
    main()
