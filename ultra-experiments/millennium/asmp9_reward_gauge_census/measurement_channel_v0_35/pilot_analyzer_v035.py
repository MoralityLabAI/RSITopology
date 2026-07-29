"""Total evaluator for the draft ASMP-9 v0.35 measurement pilot."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import math
import statistics
from typing import Any, Iterable, Mapping

from monotone_ruler import monotone_linf_radius, robust_zero_crossing


FACTORIAL_CELLS = {
    ("target_first", "natural"),
    ("target_first", "reverse"),
    ("target_second", "natural"),
    ("target_second", "reverse"),
}


def _finite(value: Any) -> float:
    output = float(value)
    if not math.isfinite(output):
        raise ValueError("target_log_odds must be finite")
    return output


def validate_and_join(
    manifest: Mapping[str, Any],
    records: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if manifest.get("schema_version") != (
        "asmp9_measurement_channel_prompt_manifest_v0_35"
    ):
        raise ValueError("unexpected manifest schema")
    row_by_id = {str(row["row_id"]): row for row in manifest["rows"]}
    if len(row_by_id) != int(manifest["unique_prompt_rows"]):
        raise ValueError("manifest row ids are not unique")
    joined: list[dict[str, Any]] = []
    observed: dict[str, set[int]] = defaultdict(set)
    for record in records:
        row_id = str(record["row_id"])
        if row_id not in row_by_id:
            raise ValueError(f"record outside manifest: {row_id}")
        epoch = int(record["planned_epoch"])
        if epoch not in (0, 1) or epoch in observed[row_id]:
            raise ValueError(f"invalid or duplicate epoch for {row_id}")
        observed[row_id].add(epoch)
        joined.append(
            {
                **row_by_id[row_id],
                "planned_epoch": epoch,
                "target_log_odds": _finite(record["target_log_odds"]),
            }
        )
    if set(observed) != set(row_by_id):
        raise ValueError("record universe does not equal manifest universe")
    if any(epochs != {0, 1} for epochs in observed.values()):
        raise ValueError("every prompt row requires two cold-start epochs")
    return joined


def factorial_contrasts(
    joined: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_content: dict[
        tuple[str, str, str],
        dict[tuple[str, str], list[float]],
    ] = defaultdict(lambda: defaultdict(list))
    metadata: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    for row in joined:
        key = (
            str(row["family_id"]),
            str(row["query_type"]),
            str(row["content_id"]),
        )
        cell = (
            str(row["presentation_order"]),
            str(row["code_mapping"]),
        )
        by_content[key][cell].append(float(row["target_log_odds"]))
        metadata[key] = row
    output: list[dict[str, Any]] = []
    for key, cells in sorted(by_content.items()):
        if set(cells) != FACTORIAL_CELLS:
            raise ValueError(f"incomplete factorial for {key}")
        if any(len(values) != 2 for values in cells.values()):
            raise ValueError(f"incomplete cold-start factorial for {key}")
        means = {cell: statistics.fmean(values) for cell, values in cells.items()}
        semantic = statistics.fmean(means.values())
        position = statistics.fmean(
            (1 if cell[0] == "target_first" else -1) * value
            for cell, value in means.items()
        )
        code = statistics.fmean(
            (1 if cell[1] == "natural" else -1) * value
            for cell, value in means.items()
        )
        interaction = statistics.fmean(
            (1 if cell[0] == "target_first" else -1)
            * (1 if cell[1] == "natural" else -1)
            * value
            for cell, value in means.items()
        )
        row = metadata[key]
        keep = {
            field: row[field]
            for field in (
                "cell_id",
                "cell_index",
                "mixture_id",
                "anchor_probability",
                "lower_probability",
                "upper_probability",
                "dominance_relation",
            )
            if field in row
        }
        output.append(
            {
                "family_id": key[0],
                "query_type": key[1],
                "content_id": key[2],
                **keep,
                "semantic_contrast": semantic,
                "position_component": position,
                "code_component": code,
                "position_code_interaction": interaction,
                "factorial_cell_means": {
                    f"{cell[0]}--{cell[1]}": value
                    for cell, value in sorted(means.items())
                },
            }
        )
    return output


def cold_start_radius(joined: Iterable[Mapping[str, Any]]) -> float:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in joined:
        grouped[str(row["row_id"])].append(float(row["target_log_odds"]))
    return max(abs(values[0] - values[1]) for values in grouped.values())


def ruler_rows(
    contrasts: Iterable[Mapping[str, Any]],
    query_type: str,
    object_field: str,
    instrument_radius: float,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[tuple[Fraction, float]]] = defaultdict(
        list
    )
    for row in contrasts:
        if row["query_type"] == query_type:
            grouped[(str(row[object_field]), str(row["family_id"]))].append(
                (
                    Fraction(str(row["anchor_probability"])),
                    float(row["semantic_contrast"]),
                )
            )
    output: list[dict[str, Any]] = []
    for (object_id, family_id), points in sorted(grouped.items()):
        ordered = sorted(points)
        if [point[0] for point in ordered] != [
            Fraction(0),
            Fraction(1, 12),
            Fraction(1, 6),
            Fraction(1, 3),
            Fraction(1, 2),
            Fraction(2, 3),
            Fraction(5, 6),
            Fraction(11, 12),
            Fraction(1),
        ]:
            raise ValueError(f"probability grid changed for {object_id}")
        values = [point[1] for point in ordered]
        repair = monotone_linf_radius(values)
        output.append(
            {
                object_field: object_id,
                "family_id": family_id,
                "monotone_linf_radius": repair,
                "repair_within_instrument_radius": repair <= instrument_radius,
                "robust_zero_crossing": robust_zero_crossing(
                    values, instrument_radius
                ),
                "admitted": (
                    repair <= instrument_radius
                    and robust_zero_crossing(values, instrument_radius)
                ),
                "semantic_curve": values,
            }
        )
    return output


def resolve_gate(
    gate: str,
    passed: bool,
    reason: str,
    sequence_open: bool,
) -> tuple[dict[str, Any], bool]:
    if not sequence_open:
        return (
            {
                "gate": gate,
                "instrument_status": "not_evaluated_upstream_stop",
                "decision": "not_evaluated",
                "reason": "upstream_gate_stopped_fixed_sequence",
            },
            False,
        )
    decision = "pass" if passed else "fail"
    return (
        {
            "gate": gate,
            "instrument_status": "valid",
            "decision": decision,
            "reason": "passed" if passed else reason,
        },
        passed,
    )


def evaluate(
    manifest: Mapping[str, Any],
    records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    joined = validate_and_join(manifest, records)
    contrasts = factorial_contrasts(joined)
    cold_radius = cold_start_radius(joined)
    equality = [
        row
        for row in contrasts
        if row["query_type"] == "semantic_equality_control"
    ]
    equality_radius = max(
        abs(float(row["semantic_contrast"])) for row in equality
    )
    instrument_radius = equality_radius + cold_radius

    by_row_epoch: dict[str, list[float]] = defaultdict(list)
    for row in joined:
        if row["query_type"] == "code_mapping_control":
            by_row_epoch[str(row["row_id"])].append(
                float(row["target_log_odds"])
            )
    c0_pass = bool(by_row_epoch) and all(
        value > 0 for values in by_row_epoch.values() for value in values
    )

    dominance = [
        row
        for row in contrasts
        if row["query_type"]
        in {"probability_order_control", "anchor_dominance_control"}
    ]
    d0_pass = bool(dominance) and all(
        float(row["semantic_contrast"]) > instrument_radius
        for row in dominance
    )

    standard = ruler_rows(
        contrasts,
        "standard_gamble",
        "cell_id",
        instrument_radius,
    )
    compound = ruler_rows(
        contrasts,
        "compound_gamble",
        "mixture_id",
        instrument_radius,
    )
    m0_pass = len(standard) == 36 and len(compound) == 18 and all(
        bool(row["admitted"]) for row in (*standard, *compound)
    )

    standard_admission = {
        (str(row["cell_id"]), str(row["family_id"])): bool(row["admitted"])
        for row in standard
    }
    compound_admission = {
        (str(row["mixture_id"]), str(row["family_id"])): bool(row["admitted"])
        for row in compound
    }
    source_mixtures = {
        str(row["mixture_id"]): (
            f"cell_{int(row['first_cell_index']):02d}",
            f"cell_{int(row['second_cell_index']):02d}",
        )
        for row in manifest["source_compound_mixtures"]
    }
    joint_rows: list[dict[str, Any]] = []
    for mixture_id, (first, second) in sorted(source_mixtures.items()):
        for family_id in sorted(manifest["families"]):
            admitted = (
                compound_admission[(mixture_id, family_id)]
                and standard_admission[(first, family_id)]
                and standard_admission[(second, family_id)]
            )
            joint_rows.append(
                {
                    "mixture_id": mixture_id,
                    "family_id": family_id,
                    "first_cell_id": first,
                    "second_cell_id": second,
                    "admitted": admitted,
                }
            )
    j0_pass = len(joint_rows) == 18 and all(
        bool(row["admitted"]) for row in joint_rows
    )

    gates: list[dict[str, Any]] = []
    sequence_open = True
    for gate, passed, reason in (
        ("C0", c0_pass, "code_channel_invalid"),
        ("D0", d0_pass, "semantic_order_invalid"),
        ("M0", m0_pass, "monotone_ruler_not_established"),
        ("J0", j0_pass, "mixture_analysis_unavailable"),
    ):
        record, sequence_open = resolve_gate(
            gate, passed, reason, sequence_open
        )
        gates.append(record)
    all_pass = all(row["decision"] == "pass" for row in gates)
    return {
        "schema_version": "asmp9_measurement_channel_gate_result_v0_35",
        "status": (
            "measurement_channel_admitted_for_successor_design_only"
            if all_pass
            else "measurement_channel_stopped"
        ),
        "instrument_radius": {
            "semantic_equality_maximum": equality_radius,
            "cold_start_maximum_delta": cold_radius,
            "total": instrument_radius,
        },
        "gates": gates,
        "standard_rulers": standard,
        "compound_rulers": compound,
        "joint_mixture_rows": joint_rows,
        "factorial_contrasts": contrasts,
        "claim_boundary": (
            "A passing result admits this measurement channel for successor "
            "design only. It does not confirm mixture affinity or the v0.33 "
            "decision quotient and does not resolve ASMP-9."
        ),
    }
