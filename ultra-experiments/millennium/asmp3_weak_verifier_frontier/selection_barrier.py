from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path


ATOM_GRID = (64, 256, 1024, 4096)
ERROR_LIMIT = Fraction(1, 20)
ADJUDICATION_QUERY_GRID = (1, 3, 5, 7, 9)


def ceil_log2(value: int) -> int:
    if value < 1:
        raise ValueError("value must be positive")
    return (value - 1).bit_length()


def polylog_calibration_budget(atom_count: int) -> int:
    """Reuse the round-robin transcript-scale budget as a concrete comparator."""
    return min(atom_count, 2 * ceil_log2(atom_count) + 12)


def validate_counts(atom_count: int, calibration_count: int, blind_count: int) -> None:
    if atom_count < 1:
        raise ValueError("atom_count must be positive")
    if not 0 <= calibration_count <= atom_count:
        raise ValueError("calibration_count must lie in [0, atom_count]")
    if not 0 <= blind_count <= atom_count:
        raise ValueError("blind_count must lie in [0, atom_count]")


def miss_probability_without_replacement(
    atom_count: int,
    calibration_count: int,
    blind_count: int = 1,
) -> Fraction:
    """Probability that a uniform distinct calibration set misses every blind atom."""
    validate_counts(atom_count, calibration_count, blind_count)
    if calibration_count > atom_count - blind_count:
        return Fraction(0)
    return Fraction(
        comb(atom_count - blind_count, calibration_count),
        comb(atom_count, calibration_count),
    )


def detection_probability_without_replacement(
    atom_count: int,
    calibration_count: int,
    blind_count: int = 1,
) -> Fraction:
    return 1 - miss_probability_without_replacement(
        atom_count,
        calibration_count,
        blind_count,
    )


def randomized_minimax_false_accept(
    atom_count: int,
    calibration_count: int,
) -> Fraction:
    """
    Sharp one-blind-spot minimax value.

    Any randomized calibration strategy checks at most m distinct atoms. The
    sum of atom inclusion probabilities is therefore at most m, so some atom is
    checked with probability at most m/N. A uniformly random size-m subset
    attains equality for every atom.
    """
    validate_counts(atom_count, calibration_count, 1)
    return Fraction(atom_count - calibration_count, atom_count)


def deterministic_worst_case_false_accept(
    atom_count: int,
    calibration_count: int,
) -> Fraction:
    """A fixed calibration set leaves a selectable blind spot unless it is exhaustive."""
    validate_counts(atom_count, calibration_count, 1)
    return Fraction(1 if calibration_count < atom_count else 0)


def required_distinct_calibration(
    atom_count: int,
    false_accept_limit: Fraction = ERROR_LIMIT,
) -> int:
    """Smallest m for which the sharp randomized minimax value is at most the limit."""
    if not 0 <= false_accept_limit <= 1:
        raise ValueError("false_accept_limit must lie in [0, 1]")
    numerator = atom_count * (1 - false_accept_limit).numerator
    denominator = (1 - false_accept_limit).denominator
    return (numerator + denominator - 1) // denominator


def selected_blind_spot_majority_false_accept(query_count: int) -> Fraction:
    """
    Repeating adjudication cannot repair a deterministic error on the selected atom.
    """
    if query_count < 1 or query_count % 2 == 0:
        raise ValueError("query_count must be a positive odd integer")
    return Fraction(1)


def exhaustive_formula_check(max_atoms: int = 9) -> bool:
    """Brute-force the hypergeometric miss formula on every small finite universe."""
    universe_cache = {n: tuple(range(n)) for n in range(1, max_atoms + 1)}
    for atom_count, universe in universe_cache.items():
        for blind_count in range(atom_count + 1):
            blind_sets = tuple(combinations(universe, blind_count))
            for calibration_count in range(atom_count + 1):
                calibration_sets = tuple(combinations(universe, calibration_count))
                misses = 0
                total = len(blind_sets) * len(calibration_sets)
                for blind in blind_sets:
                    blind_lookup = set(blind)
                    for calibration in calibration_sets:
                        if blind_lookup.isdisjoint(calibration):
                            misses += 1
                observed = Fraction(misses, total)
                expected = miss_probability_without_replacement(
                    atom_count,
                    calibration_count,
                    blind_count,
                )
                if observed != expected:
                    return False
    return True


def fraction_record(value: Fraction) -> dict[str, object]:
    return {"exact": str(value), "decimal": float(value)}


def build_result() -> dict[str, object]:
    exhaustive_valid = exhaustive_formula_check()
    rows = []
    for atom_count in ATOM_GRID:
        calibration_count = polylog_calibration_budget(atom_count)
        false_accept = randomized_minimax_false_accept(
            atom_count,
            calibration_count,
        )
        required = required_distinct_calibration(atom_count)
        rows.append(
            {
                "atom_count": atom_count,
                "polylog_calibration_budget": calibration_count,
                "randomized_minimax_false_accept": fraction_record(false_accept),
                "passes_5_percent": false_accept <= ERROR_LIMIT,
                "minimum_distinct_checks_for_5_percent": required,
                "minimum_fraction_checked": fraction_record(
                    Fraction(required, atom_count)
                ),
                "deterministic_worst_case_false_accept": fraction_record(
                    deterministic_worst_case_false_accept(
                        atom_count,
                        calibration_count,
                    )
                ),
            }
        )

    repeated_adjudication = {
        str(query_count): fraction_record(
            selected_blind_spot_majority_false_accept(query_count)
        )
        for query_count in ADJUDICATION_QUERY_GRID
    }
    gates = {
        "E0_exhaustive_small_universe_check": exhaustive_valid,
        "M0_minimax_matches_hypergeometric_single_spot": all(
            randomized_minimax_false_accept(n, m)
            == miss_probability_without_replacement(n, m, 1)
            for n in range(1, 33)
            for m in range(n + 1)
        ),
        "P0_polylog_budget_cannot_meet_5_percent": all(
            not row["passes_5_percent"] for row in rows
        ),
        "L0_five_percent_requires_at_least_95_percent_coverage": all(
            row["minimum_distinct_checks_for_5_percent"]
            >= Fraction(19, 20) * row["atom_count"]
            for row in rows
        ),
        "D0_fixed_nonexhaustive_calibration_has_unit_worst_case": all(
            row["deterministic_worst_case_false_accept"]["exact"] == "1"
            for row in rows
        ),
        "R0_repetition_does_not_repair_selected_blind_spot": all(
            record["exact"] == "1" for record in repeated_adjudication.values()
        ),
    }
    return {
        "experiment_id": "ASMP-3-SELECTED-ATOM-CALIBRATION-BARRIER-v0.2",
        "status": "post_result_exact_lower_bound_harness",
        "certified": all(gates.values()),
        "model": {
            "semantic_atom_universe": "N local binary atoms",
            "legal_error_family": (
                "for each atom j, one oracle is deterministically wrong on j "
                "and correct on every other atom"
            ),
            "calibration": (
                "at most m distinct atom checks before a dishonest prover selects "
                "a false transcript whose unique refutation is the blind atom"
            ),
            "false_accept_limit": str(ERROR_LIMIT),
        },
        "theorem": {
            "randomized_minimax_false_accept": "(N-m)/N",
            "deterministic_nonexhaustive_false_accept": "1",
            "minimum_m_for_error_epsilon": "ceil((1-epsilon)N)",
        },
        "polylog_grid": rows,
        "selected_blind_spot_repeated_adjudication": repeated_adjudication,
        "gates": gates,
        "claim_boundary": (
            "Exact lower bound for calibration-only coverage of an unstructured "
            "finite semantic-atom registry with one selectable deterministic blind "
            "spot. It is not a lower bound for every interactive protocol and does "
            "not resolve ASMP-3."
        ),
        "stopping_conclusion": (
            "Scaling the existing majority/correlation harness cannot close the "
            "selected-atom gap. A successor needs a structural per-atom error "
            "theorem, a restriction preventing adversarial refutation selection, "
            "or a different protocol class; another aggregate finite calibration "
            "grid is not informative."
        ),
    }


def main() -> None:
    result = build_result()
    if not result["certified"]:
        raise RuntimeError("selected-atom calibration barrier certification failed")
    output = Path(__file__).resolve().parent / "selection_barrier_v0_2.json"
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
