"""Import-independent full-grid verification for ASMP-6 v0.2."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
FROZEN_COVER_LAW = "uniform"
FROZEN_MESSAGE_COUNT = 2
FROZEN_MESSAGE_PRIOR = (Fraction(1, 2), Fraction(1, 2))
FROZEN_ALPHABET_RANGE = (2, 31)
FROZEN_ENUMERATION_MAXIMUM = 9
FROZEN_PROTOCOL_ID = "ASMP6-BALANCED-COVER-v0.2"
FROZEN_PROTOCOL_SCHEMA = "asmp6_balanced_cover_protocol_v0_2"
FROZEN_PROTOCOL_FIELDS = {
    "alphabet_sizes",
    "claim_boundary",
    "cover_law",
    "independent_extremal_enumeration_maximum",
    "message_count",
    "message_prior",
    "protocol_id",
    "schema_version",
}
EXPECTED_RESULT_FIELDS = {
    "cells",
    "claim_boundary",
    "claim_support",
    "gates",
    "measurement_reliability",
    "metric_robustness",
    "operational_decision",
    "protocol_binding",
    "protocol_id",
    "schema_version",
    "task_result",
}
FROZEN_CLAIM_BOUNDARY = (
    "one-shot opaque-symbol laws only",
    "exactly two equiprobable messages only",
    "uniform benign cover law only",
    "exact message-averaged cover and exact per-message control only",
    "no learned or linguistic encoder",
    "no multiletter or ASMP-6 resolution claim",
)
FINAL_CLAIM_SUPPORT = (
    "one_shot_two_equiprobable_messages_uniform_exact_average_cover"
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def total_variation(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    if len(left) != len(right):
        raise ValueError("probability laws must have equal length")
    return sum((abs(a - b) for a, b in zip(left, right)), Fraction()) / 2


def equal_prior_bayes_error(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return (1 - total_variation(left, right)) / 2


def _fraction_field_equals(
    record: dict[str, Any], field: str, expected: Fraction
) -> bool:
    try:
        return Fraction(record[field]) == expected
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def protocol_binding_checks(protocol: dict[str, Any]) -> dict[str, bool]:
    try:
        prior = tuple(Fraction(value) for value in protocol["message_prior"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        prior = ()
    limits = protocol.get("alphabet_sizes", {})
    minimum = limits.get("minimum") if isinstance(limits, dict) else None
    maximum = limits.get("maximum") if isinstance(limits, dict) else None
    boundary = protocol.get("claim_boundary")
    return {
        "protocol_fields_are_exact": set(protocol) == FROZEN_PROTOCOL_FIELDS,
        "protocol_id_is_frozen": protocol.get("protocol_id") == FROZEN_PROTOCOL_ID,
        "protocol_schema_is_frozen": (
            protocol.get("schema_version") == FROZEN_PROTOCOL_SCHEMA
        ),
        "cover_law_is_uniform": protocol.get("cover_law") == FROZEN_COVER_LAW,
        "message_count_is_two": (
            type(protocol.get("message_count")) is int
            and protocol.get("message_count") == FROZEN_MESSAGE_COUNT
        ),
        "message_prior_is_equal_half": prior == FROZEN_MESSAGE_PRIOR,
        "registered_alphabet_range_is_2_through_31": (
            type(minimum) is int
            and type(maximum) is int
            and (minimum, maximum) == FROZEN_ALPHABET_RANGE
        ),
        "enumeration_maximum_is_nine": (
            type(protocol.get("independent_extremal_enumeration_maximum")) is int
            and protocol.get("independent_extremal_enumeration_maximum")
            == FROZEN_ENUMERATION_MAXIMUM
        ),
        "claim_boundary_is_frozen": (
            isinstance(boundary, list) and tuple(boundary) == FROZEN_CLAIM_BOUNDARY
        ),
    }


def independent_cell(alphabet_size: int) -> dict[str, Any]:
    """Reconstruct a full expected cell without importing the primary path."""

    if alphabet_size < 2:
        raise ValueError("alphabet_size must be at least two")
    radius = Fraction(1, alphabet_size)
    pairs = alphabet_size // 2
    p0 = [2 * radius] * pairs + [Fraction(0)] * pairs
    p1 = [Fraction(0)] * pairs + [2 * radius] * pairs
    if alphabet_size % 2:
        p0.append(radius)
        p1.append(radius)
    cover = [radius] * alphabet_size
    average = [(left + right) / 2 for left, right in zip(p0, p1)]
    tv = total_variation(p0, p1)
    dual_bound = Fraction(2 * pairs, alphabet_size)
    error = equal_prior_bayes_error(p0, p1)
    messagewise_error = equal_prior_bayes_error(cover, cover)
    return {
        "alphabet_size": alphabet_size,
        "parity": "even" if alphabet_size % 2 == 0 else "odd",
        "averaged_cover_exact": average == cover,
        "p0": [fraction_text(value) for value in p0],
        "p1": [fraction_text(value) for value in p1],
        "total_variation": fraction_text(tv),
        "dual_tv_upper_bound": fraction_text(dual_bound),
        "bayes_error": fraction_text(error),
        "messagewise_bayes_error": fraction_text(messagewise_error),
        "perfect_decoding": error == 0,
        "optimality_gap": fraction_text(dual_bound - tv),
    }


def continuous_vertex_extremum(alphabet_size: int) -> Fraction:
    """Maximize L1 over the full continuous feasible polytope exactly.

    The polytope is ``[-1/m,1/m]^m`` intersected with ``sum(d)=0``.  A convex
    piecewise-linear objective has an extreme-point maximizer.  At a vertex at
    least ``m-1`` coordinates are box-bound, so enumerating their signs and
    solving the last coordinate covers the continuous, not merely ternary,
    feasible laws.
    """

    radius = Fraction(1, alphabet_size)
    best = Fraction(-1)
    for free_coordinate in range(alphabet_size):
        fixed = [index for index in range(alphabet_size) if index != free_coordinate]
        for signs in itertools.product((-1, 1), repeat=alphabet_size - 1):
            deviation = [Fraction(0)] * alphabet_size
            for coordinate, sign in zip(fixed, signs):
                deviation[coordinate] = sign * radius
            deviation[free_coordinate] = -sum(
                (deviation[coordinate] for coordinate in fixed), Fraction()
            )
            if -radius <= deviation[free_coordinate] <= radius:
                best = max(
                    best,
                    sum((abs(value) for value in deviation), Fraction()),
                )
    return best


def extremal_enumeration(alphabet_size: int) -> Fraction:
    """Backward-compatible name for the continuous-polytope vertex replay."""

    return continuous_vertex_extremum(alphabet_size)


def sign_count_upper_bound(alphabet_size: int) -> Fraction:
    return Fraction(2 * (alphabet_size // 2), alphabet_size)


def independent_metric_probes(expected_cells: dict[int, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    p0 = [Fraction(value) for value in expected_cells[7]["p0"]]
    p1 = [Fraction(value) for value in expected_cells[7]["p1"]]
    permutation = (3, 0, 6, 2, 5, 1, 4)
    original_error = equal_prior_bayes_error(p0, p1)
    permuted_error = equal_prior_bayes_error(
        [p0[index] for index in permutation],
        [p1[index] for index in permutation],
    )
    return {
        "invariance": {
            "pass": permuted_error == original_error,
            "probe": "symbol_label_permutation",
        },
        "sensitivity": {
            "pass": expected_cells[3]["perfect_decoding"] is False
            and expected_cells[4]["perfect_decoding"] is True,
            "probe": "odd_to_even_divisibility_boundary",
        },
        "monotonicity": {
            "pass": all(
                Fraction(cell["bayes_error"])
                <= Fraction(cell["messagewise_bayes_error"])
                for cell in expected_cells.values()
            ),
            "probe": "relax_messagewise_cover_to_averaged_cover",
        },
        "anti_gaming": {
            "pass": all(
                cell["optimality_gap"] == "0/1"
                for cell in expected_cells.values()
            ),
            "probe": "witness_matches_sign_count_dual_bound",
        },
        "clean_control": {
            "pass": all(
                cell["messagewise_bayes_error"] == "1/2"
                for cell in expected_cells.values()
            ),
            "probe": "identical_message_laws_are_chance",
        },
    }


def probability_cell_valid(cell: dict[str, Any]) -> bool:
    try:
        alphabet_size = int(cell["alphabet_size"])
        if isinstance(cell["alphabet_size"], bool) or alphabet_size < 2:
            return False
        p0 = [Fraction(value) for value in cell["p0"]]
        p1 = [Fraction(value) for value in cell["p1"]]
        if len(p0) != alphabet_size or len(p1) != alphabet_size:
            return False
        cover = [Fraction(1, alphabet_size)] * alphabet_size
        return bool(
            all(value >= 0 for value in p0 + p1)
            and sum(p0, Fraction()) == 1
            and sum(p1, Fraction()) == 1
            and all(
                (left + right) / 2 == target
                for left, right, target in zip(p0, p1, cover)
            )
            and total_variation(p0, p1) == Fraction(cell["total_variation"])
            and equal_prior_bayes_error(p0, p1) == Fraction(cell["bayes_error"])
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def _cell_mismatches(
    expected_cells: dict[int, dict[str, Any]],
    reported_cells: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], bool]:
    reported_list = list(reported_cells)
    keys = [
        cell.get("alphabet_size") if isinstance(cell, dict) else None
        for cell in reported_list
    ]
    grid_exact = (
        all(type(key) is int for key in keys)
        and len(keys) == len(set(keys))
        and set(keys) == set(expected_cells)
    )
    lookup = {
        cell["alphabet_size"]: cell
        for cell in reported_list
        if isinstance(cell, dict)
        and isinstance(cell.get("alphabet_size"), int)
        and not isinstance(cell.get("alphabet_size"), bool)
    }
    mismatches: list[dict[str, Any]] = []
    for alphabet_size, expected in expected_cells.items():
        reported = lookup.get(alphabet_size)
        if reported is None:
            mismatches.append({"alphabet_size": alphabet_size, "field": "cell", "reported": "missing"})
            continue
        for field in sorted(set(expected) | set(reported)):
            expected_value = expected.get(field, "<field absent>")
            reported_value = reported.get(field, "<field absent>")
            if field not in expected or field not in reported or reported_value != expected_value:
                mismatches.append(
                    {
                        "alphabet_size": alphabet_size,
                        "field": field,
                        "expected": expected_value,
                        "reported": reported_value,
                    }
                )
    return mismatches, grid_exact


def verify(
    protocol_path: Path | None = None,
    result_path: Path | None = None,
) -> dict[str, Any]:
    protocol_path = protocol_path or HERE / "protocol_v0_2.json"
    result_path = result_path or HERE / "artifacts_v0_2" / "result_v0_2.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    binding = protocol_binding_checks(protocol)

    limits = protocol.get("alphabet_sizes", {})
    minimum = limits.get("minimum", 2) if isinstance(limits, dict) else 2
    maximum = limits.get("maximum", 1) if isinstance(limits, dict) else 1
    expected_cells = (
        {size: independent_cell(size) for size in range(minimum, maximum + 1)}
        if binding["registered_alphabet_range_is_2_through_31"]
        else {}
    )
    reported_cells = result.get("cells", [])
    if not isinstance(reported_cells, list):
        reported_cells = []
    mismatches, grid_exact = _cell_mismatches(expected_cells, reported_cells)
    probability_failures = [
        cell.get("alphabet_size")
        if isinstance(cell, dict)
        else None
        for cell in reported_cells
        if not isinstance(cell, dict) or not probability_cell_valid(cell)
    ]

    enumeration_maximum = protocol.get("independent_extremal_enumeration_maximum", 1)
    continuous_vertex_failures: list[dict[str, Any]] = []
    enumerated_sizes: list[int] = []
    if enumeration_maximum == FROZEN_ENUMERATION_MAXIMUM:
        for alphabet_size in range(2, enumeration_maximum + 1):
            enumerated_sizes.append(alphabet_size)
            enumerated = continuous_vertex_extremum(alphabet_size)
            expected = sign_count_upper_bound(alphabet_size)
            if enumerated != expected:
                continuous_vertex_failures.append(
                    {
                        "alphabet_size": alphabet_size,
                        "enumerated": fraction_text(enumerated),
                        "expected": fraction_text(expected),
                    }
                )
    else:
        continuous_vertex_failures.append({"error": "invalid enumeration maximum"})

    dual_bound_failures = [
        alphabet_size
        for alphabet_size in range(2, 64)
        if (1 - sign_count_upper_bound(alphabet_size)) / 2
        != (Fraction(0) if alphabet_size % 2 == 0 else Fraction(1, 2 * alphabet_size))
    ]

    expected_probes = (
        independent_metric_probes(expected_cells)
        if all(size in expected_cells for size in (3, 4, 7))
        else {}
    )
    reported_probes = result.get("metric_robustness", {})
    if not isinstance(reported_probes, dict):
        reported_probes = {}
    metric_probe_mismatches = [
        name
        for name in sorted(set(expected_probes) | set(reported_probes))
        if expected_probes.get(name) != reported_probes.get(name)
    ]

    reported_cell_grid = {
        cell["alphabet_size"]: cell
        for cell in reported_cells
        if isinstance(cell, dict)
        and isinstance(cell.get("alphabet_size"), int)
        and not isinstance(cell.get("alphabet_size"), bool)
    }
    derived_primary_gates = {
        "G0_frozen_protocol_binding": all(binding.values()),
        "G1_probability_feasibility": not probability_failures and grid_exact,
        "G2_exact_optimality": grid_exact
        and all(
            reported_cell_grid[size].get("optimality_gap") == "0/1"
            for size in expected_cells
        ),
        "G3_parity_boundary": grid_exact
        and all(
            reported_cell_grid[size].get("perfect_decoding") == (size % 2 == 0)
            for size in expected_cells
        ),
        "G4_odd_error_formula": grid_exact
        and all(
            _fraction_field_equals(
                reported_cell_grid[size], "bayes_error", Fraction(1, 2 * size)
            )
            for size in expected_cells
            if size % 2
        ),
        "G5_messagewise_control": grid_exact
        and all(
            reported_cell_grid[size].get("messagewise_bayes_error") == "1/2"
            for size in expected_cells
        ),
        "G6_metric_robustness": bool(expected_probes)
        and not metric_probe_mismatches
        and all(record["pass"] for record in expected_probes.values()),
    }
    reported_primary_gates = result.get("gates", {})
    if not isinstance(reported_primary_gates, dict):
        reported_primary_gates = {}
    primary_gate_mismatches = [
        name
        for name in sorted(set(derived_primary_gates) | set(reported_primary_gates))
        if derived_primary_gates.get(name) != reported_primary_gates.get(name)
    ]

    preverification_layers_match = bool(
        result.get("task_result") == "sharp_uniform_alphabet_parity_frontier"
        and result.get("measurement_reliability") == "awaiting_independent_verification"
        and result.get("claim_support") == FINAL_CLAIM_SUPPORT
        and result.get("operational_decision") == "await_independent_verification"
        and result.get("protocol_binding") == binding
        and result.get("claim_boundary") == protocol.get("claim_boundary")
    )

    independent_gates = {
        "V0_frozen_protocol_binding": all(binding.values()),
        "V1_registered_cell_grid_exact": bool(expected_cells) and grid_exact,
        "V2_every_registered_cell_recomputed_exactly": bool(expected_cells)
        and grid_exact
        and not mismatches,
        "V3_probability_and_cover_recomputed": bool(expected_cells)
        and grid_exact
        and not probability_failures,
        "V4_continuous_polytope_vertex_replay": not continuous_vertex_failures
        and bool(enumerated_sizes),
        "V5_general_sign_count_dual_replay": not dual_bound_failures,
        "V6_metric_probe_pack_recomputed": not metric_probe_mismatches
        and bool(expected_probes)
        and all(record["pass"] for record in expected_probes.values()),
        "V7_primary_gates_derived_and_matched": not primary_gate_mismatches,
        "V8_preverification_conclusion_layers_match": preverification_layers_match,
        "V9_protocol_and_result_identity_match": bool(
            protocol.get("schema_version") == "asmp6_balanced_cover_protocol_v0_2"
            and result.get("schema_version") == "asmp6_balanced_cover_result_v0_2"
            and result.get("protocol_id") == protocol.get("protocol_id")
            and set(result) == EXPECTED_RESULT_FIELDS
        ),
    }
    passed = all(independent_gates.values())
    final_layers = {
        "metric_robustness": (
            "five_probe_pack_independently_replayed"
            if passed
            else "not_established"
        ),
        "task_result": (
            "sharp_uniform_alphabet_parity_frontier"
            if passed
            else "not_established"
        ),
        "measurement_reliability": (
            "independent_full_grid_continuous_extremal_and_dual_replay_passed"
            if passed
            else "failed"
        ),
        "claim_support": FINAL_CLAIM_SUPPORT if passed else "none",
        "operational_decision": "register_multiletter_successor" if passed else "repair",
    }
    return {
        "schema_version": "asmp6_balanced_cover_verification_v0_2_1",
        "pass": passed,
        "protocol_binding": binding,
        "registered_alphabet_sizes": sorted(expected_cells),
        "continuous_vertex_enumerated_alphabet_sizes": enumerated_sizes,
        "cell_mismatches": mismatches,
        "probability_failures": probability_failures,
        "continuous_vertex_failures": continuous_vertex_failures,
        "dual_bound_failures": dual_bound_failures,
        "metric_probe_mismatches": metric_probe_mismatches,
        "primary_gate_mismatches": primary_gate_mismatches,
        "derived_primary_gates": derived_primary_gates,
        "independent_gates": independent_gates,
        "final_conclusion_layers": final_layers,
        # Compatibility fields remain explicit for existing consumers.
        "measurement_reliability": final_layers["measurement_reliability"],
        "claim_support": final_layers["claim_support"],
        "operational_decision": final_layers["operational_decision"],
        "bindings": {
            "protocol_v0_2.json": sha256_file(protocol_path),
            "result_v0_2.json": sha256_file(result_path),
        },
    }


def main() -> None:
    verification = verify()
    output = HERE / "artifacts_v0_2" / "verification_v0_2.json"
    output.write_text(canonical_json(verification), encoding="utf-8", newline="\n")
    print(output)
    if not verification["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
