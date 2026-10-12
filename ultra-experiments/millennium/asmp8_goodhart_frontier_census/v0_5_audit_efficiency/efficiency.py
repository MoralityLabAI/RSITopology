"""Audit-efficiency comparison for ASMP-8 v0.5."""

from __future__ import annotations

import csv
import io
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.stats import beta


HERE = Path(__file__).resolve().parent
V03 = HERE.parent / "v0_3_calibrated_certificate"
V04 = HERE.parent / "v0_4_dynamic_threshold"
for path in (V03, V04):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from calibration import error_populations, policy_coordinates, policy_registry  # noqa: E402


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def cp_upper(failures: int, trials: int) -> float:
    return 1.0 if failures == trials else float(beta.ppf(0.95, failures + 1, trials - failures))


def empirical_bernstein_envelopes(
    errors: np.ndarray,
    checkpoints: list[int],
    streams: int,
    seed: int,
    familywise_alpha: float,
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    probability = np.full(errors.size, 1 / errors.size)
    counts = np.zeros((streams, errors.size), dtype=np.int64)
    envelope_1 = np.ones(streams)
    envelope_2 = np.ones(streams)
    all_1, all_2 = [], []
    delta = familywise_alpha / (2 * len(checkpoints))
    log_term = math.log(2 / delta)
    previous = 0
    z1 = np.abs(errors)
    z2 = errors**2
    for checkpoint in checkpoints:
        counts += rng.multinomial(checkpoint - previous, probability, size=streams)
        bounds = []
        for values in (z1, z2):
            mean = counts @ values / checkpoint
            second = counts @ (values**2) / checkpoint
            variance = np.maximum(0.0, checkpoint * (second - mean**2) / (checkpoint - 1))
            upper = (
                mean
                + np.sqrt(2 * variance * log_term / checkpoint)
                + 7 * log_term / (3 * (checkpoint - 1))
            )
            bounds.append(np.minimum(1.0, upper))
        envelope_1 = np.minimum(envelope_1, bounds[0])
        envelope_2 = np.minimum(envelope_2, np.sqrt(bounds[1]))
        all_1.append(envelope_1.copy())
        all_2.append(envelope_2.copy())
        previous = checkpoint
    return {"u1": np.asarray(all_1), "u2": np.asarray(all_2)}


def first_crossings(margins: np.ndarray, checkpoints: list[int]) -> np.ndarray:
    positive = margins > 0
    crossed = np.any(positive, axis=0)
    first = np.zeros(margins.shape[1], dtype=np.int64)
    indices = np.argmax(positive, axis=0)
    first[crossed] = np.asarray(checkpoints)[indices[crossed]]
    return first


def crossing_summary(first: np.ndarray) -> dict[str, Any]:
    values = first[first > 0]
    if values.size == 0:
        return {
            "crossed_streams": 0,
            "censored_streams": int(first.size),
            "minimum": None,
            "q25": None,
            "median": None,
            "q75": None,
            "maximum": None,
        }
    return {
        "crossed_streams": int(values.size),
        "censored_streams": int(first.size - values.size),
        "minimum": int(np.min(values)),
        "q25": float(np.quantile(values, 0.25, method="inverted_cdf")),
        "median": float(np.quantile(values, 0.5, method="inverted_cdf")),
        "q75": float(np.quantile(values, 0.75, method="inverted_cdf")),
        "maximum": int(np.max(values)),
    }


def movement_partial_census(
    policy: np.ndarray,
    p0: np.ndarray,
    errors: np.ndarray,
    proxy_gain: float,
    cap: float = 1.0,
) -> tuple[int | None, list[float], float]:
    displacement = policy - p0
    order = sorted(range(policy.size), key=lambda index: (-abs(displacement[index]), index))
    observed = 0.0
    unseen = float(np.sum(np.abs(displacement))) * cap
    margins = []
    crossing = None
    for audits, index in enumerate(order, start=1):
        unseen -= abs(float(displacement[index])) * cap
        observed += float(displacement[index] * errors[index])
        margin = proxy_gain + observed - max(0.0, unseen)
        margins.append(margin)
        if crossing is None and margin > 0:
            crossing = audits
    exact_true_gain = proxy_gain + float(np.dot(displacement, errors))
    return crossing, margins, exact_true_gain


def load_hoeffding_rows() -> dict[tuple[str, str], dict[str, Any]]:
    rows = {}
    with (V04 / "artifacts_v0_4" / "policy_thresholds_v0_4.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        for row in csv.DictReader(stream):
            rows[(row["error_family"], row["policy_id"])] = row
    return rows


def run_efficiency(protocol: dict[str, Any], streams_override: int | None = None) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    audit = protocol["shared_audit"]
    checkpoints = [int(value) for value in audit["checkpoints"]]
    streams = int(streams_override or audit["nested_streams"])
    alpha = float(audit["familywise_alpha"])
    proxy = np.linspace(-0.5, 0.5, 64)
    p0 = np.full(64, 1 / 64)
    parent_protocol = json.loads((V03 / "protocol_v0_3.json").read_text(encoding="utf-8"))
    policies = policy_registry(proxy, parent_protocol)
    populations = error_populations(64)
    baseline = load_hoeffding_rows()
    seeds = np.random.SeedSequence(int(audit["root_seed"])).spawn(len(populations))
    conditions, rows, cdf_rows = [], [], []
    monotone_violations = reversions = false_crossings = exactness_failures = 0

    for family_index, (family, errors) in enumerate(populations.items()):
        seed = int(seeds[family_index].generate_state(1, dtype=np.uint64)[0])
        envelopes = empirical_bernstein_envelopes(errors, checkpoints, streams, seed, alpha)
        actual_l1 = float(np.mean(np.abs(errors)))
        actual_l2 = float(np.sqrt(np.mean(errors**2)))
        valid = np.all(envelopes["u1"] + 1e-15 >= actual_l1, axis=0) & np.all(
            envelopes["u2"] + 1e-15 >= actual_l2, axis=0
        )
        invalid = int(np.sum(~valid))
        conditions.append(
            {
                "error_family": family,
                "streams": streams,
                "seed": seed,
                "instrument_failure_streams": invalid,
                "failure_cp_upper_95": cp_upper(invalid, streams),
            }
        )
        for record in policies:
            coordinates = policy_coordinates(record, p0)
            gain = float(record["proxy_gain"])
            true_gain = float(np.dot(record["policy"] - p0, proxy + errors))
            margins = np.maximum.reduce(
                [
                    gain - envelopes["u1"] * coordinates["movement_linf"],
                    gain - envelopes["u2"] * coordinates["movement_l2"],
                    np.full_like(envelopes["u1"], gain - coordinates["movement_l1"]),
                ]
            )
            monotone_violations += int(np.sum(np.diff(margins, axis=0) < -1e-12))
            first = first_crossings(margins, checkpoints)
            for stream_index, crossing in enumerate(first):
                if crossing:
                    start = checkpoints.index(int(crossing))
                    if not np.all(margins[start:, stream_index] > 0):
                        reversions += 1
            if true_gain <= 0:
                false_crossings += int(np.sum((first > 0) & valid))
            eb = crossing_summary(first)
            partial, partial_margins, exact = movement_partial_census(
                record["policy"], p0, errors, gain
            )
            if abs(partial_margins[-1] - exact) > 1e-12 or abs(exact - true_gain) > 1e-12:
                exactness_failures += 1
            if true_gain <= 0 and partial is not None:
                false_crossings += 1
            base = baseline[(family, record["policy_id"])]
            row = {
                "error_family": family,
                "policy_id": record["policy_id"],
                "optimizer_family": record["family"],
                "true_gain": true_gain,
                "hoeffding_minimum": int(base["minimum"]) if base["minimum"] else None,
                "hoeffding_median": float(base["median"]) if base["median"] else None,
                "empirical_bernstein_minimum": eb["minimum"],
                "empirical_bernstein_q25": eb["q25"],
                "empirical_bernstein_median": eb["median"],
                "empirical_bernstein_q75": eb["q75"],
                "empirical_bernstein_maximum": eb["maximum"],
                "empirical_bernstein_censored": eb["censored_streams"],
                "movement_partial_census": partial,
                "full_census": 64 if true_gain > 0 else None,
            }
            rows.append(row)
            for checkpoint_index, checkpoint in enumerate(checkpoints):
                cdf_rows.append(
                    {
                        "error_family": family,
                        "policy_id": record["policy_id"],
                        "optimizer_family": record["family"],
                        "checkpoint": checkpoint,
                        "empirical_bernstein_crossing_fraction_descriptive": float(
                            np.mean((first > 0) & (first <= checkpoint))
                        ),
                        "mean_margin": float(np.mean(margins[checkpoint_index])),
                    }
                )

    focus = [
        row
        for row in rows
        if row["error_family"] == "diffuse_low_error" and row["optimizer_family"] == "top_spike"
    ]
    efficiency_pass = all(
        row["movement_partial_census"] is not None
        and row["empirical_bernstein_median"] is not None
        and row["hoeffding_minimum"] is not None
        and row["movement_partial_census"] < row["empirical_bernstein_median"] < row["hoeffding_minimum"]
        for row in focus
    )
    max_cp = max(row["failure_cp_upper_95"] for row in conditions)
    gates = {
        "G1_empirical_bernstein_instrument": {
            "pass": max_cp <= float(protocol["gates_numeric"]["maximum_instrument_failure_cp_upper"]),
            "maximum_cp_upper": max_cp,
        },
        "G2_conditional_soundness": {"pass": false_crossings == 0, "false_crossings": false_crossings},
        "G3_monotone_dynamics": {
            "pass": monotone_violations == 0 and reversions == 0,
            "monotone_violations": monotone_violations,
            "reversions": reversions,
        },
        "G4_partial_census_exactness": {
            "pass": exactness_failures == 0,
            "exactness_failures": exactness_failures,
        },
        "G5_top_spike_efficiency_order": {"pass": efficiency_pass, "focus": focus},
        "G6_complete_threshold_reporting": {
            "pass": len(rows) == 60,
            "reported_policy_error_cells": len(rows),
        },
    }
    result = {
        "schema_version": "asmp8_audit_efficiency_result_v0_5",
        "streams_per_error_family": streams,
        "checkpoints": checkpoints,
        "gates": gates,
        "focus": {"diffuse_top_spike": focus},
        "claim_boundary": protocol["claim_boundary"],
    }
    return result, conditions, rows, cdf_rows


def rows_csv(rows: Iterable[dict[str, Any]], fields: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()
