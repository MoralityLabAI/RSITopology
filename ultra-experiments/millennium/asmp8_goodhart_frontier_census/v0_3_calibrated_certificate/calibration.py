"""Calibrated robust-Goodhart certificate for ASMP-8 v0.3a."""

from __future__ import annotations

import csv
import io
import json
import math
from collections import defaultdict
from typing import Any, Iterable

import numpy as np
from scipy.stats import beta


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def error_populations(count: int) -> dict[str, np.ndarray]:
    if count != 64:
        raise ValueError("v0.3a freezes a 64-outcome registry")
    index = np.arange(count)
    diffuse = ((index % 5) - 2).astype(float) * 0.025
    rank = index / (count - 1)
    heteroskedastic = -0.30 * rank**2 + np.where(index % 2 == 0, 0.025, -0.025)
    rare_tail = np.zeros(count, dtype=float)
    rare_tail[-2:] = -1.0
    populations = {
        "diffuse_low_error": diffuse,
        "heteroskedastic_proxy_coupled": heteroskedastic,
        "rare_top_tail": rare_tail,
    }
    if any(np.max(np.abs(values)) > 1 for values in populations.values()):
        raise AssertionError("pointwise error cap violated")
    return populations


def normalize(weights: np.ndarray) -> np.ndarray:
    total = float(np.sum(weights))
    if not np.isfinite(total) or total <= 0:
        raise ValueError("invalid policy weights")
    return weights / total


def policy_registry(proxy: np.ndarray, protocol: dict[str, Any]) -> list[dict[str, Any]]:
    count = proxy.size
    p0 = np.full(count, 1 / count)
    spec = protocol["policy_paths"]
    records: list[dict[str, Any]] = []

    def add(family: str, parameter: str, value: float, policy: np.ndarray) -> None:
        policy = normalize(policy)
        gain = float(np.dot(policy - p0, proxy))
        if gain <= 0:
            raise AssertionError(f"registered policy is not proxy-improving: {family}/{value}")
        records.append(
            {
                "policy_id": f"{family}:{parameter}={value:g}",
                "family": family,
                "parameter": parameter,
                "parameter_value": float(value),
                "policy": policy,
                "proxy_gain": gain,
            }
        )

    for value in spec["gibbs_betas"]:
        add("gibbs", "beta", value, np.exp(float(value) * proxy))

    cdf = np.arange(1, count + 1, dtype=float) / count
    previous = np.arange(0, count, dtype=float) / count
    for value in spec["best_of_n"]:
        add("best_of_n", "n", value, cdf ** int(value) - previous ** int(value))

    for value in spec["top_spike_alpha"]:
        policy = (1 - float(value)) * p0
        policy = policy.copy()
        policy[-1] += float(value)
        add("top_spike", "alpha", value, policy)

    phase = np.sin((np.arange(count) + 1) * 1.618033988749895)
    for value in spec["scrambled_gibbs_betas"]:
        add("scrambled_gibbs", "beta", value, np.exp(float(value) * proxy + 0.35 * phase))

    return records


def policy_coordinates(record: dict[str, Any], p0: np.ndarray) -> dict[str, float]:
    policy = record["policy"]
    ratio_deviation = policy / p0 - 1
    movement_l1 = float(np.dot(p0, np.abs(ratio_deviation)))
    movement_l2 = float(np.sqrt(np.dot(p0, ratio_deviation**2)))
    movement_linf = float(np.max(np.abs(ratio_deviation)))
    positive = policy > 0
    kl = float(np.sum(policy[positive] * np.log(policy[positive] / p0[positive])))
    return {
        "movement_l1": movement_l1,
        "movement_l2": movement_l2,
        "movement_linf": movement_linf,
        "kl_pi_p0": kl,
    }


def calibration_radii(
    errors: np.ndarray, sample_size: int, replicates: int, seed: int, alpha_each: float
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, errors.size, size=(replicates, sample_size), endpoint=False)
    sampled = errors[draws]
    radius = math.sqrt(math.log(1 / alpha_each) / (2 * sample_size))
    delta_1 = np.minimum(1.0, np.mean(np.abs(sampled), axis=1) + radius)
    delta_2 = np.sqrt(np.minimum(1.0, np.mean(sampled**2, axis=1) + radius))
    return {"delta_1": delta_1, "delta_2": delta_2, "delta_infinity": np.ones(replicates)}


def clopper_pearson_upper(failures: int, trials: int, confidence: float = 0.95) -> float:
    if not 0 <= failures <= trials or trials <= 0:
        raise ValueError("invalid binomial count")
    if failures == trials:
        return 1.0
    return float(beta.ppf(confidence, failures + 1, trials - failures))


def evaluate_condition(
    family: str,
    errors: np.ndarray,
    sample_size: int,
    replicates: int,
    seed: int,
    policies: list[dict[str, Any]],
    p0: np.ndarray,
    proxy: np.ndarray,
    alpha_each: float,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    radii = calibration_radii(errors, sample_size, replicates, seed, alpha_each)
    actual_l1 = float(np.dot(p0, np.abs(errors)))
    actual_l2 = float(np.sqrt(np.dot(p0, errors**2)))
    radius_valid = (radii["delta_1"] + 1e-15 >= actual_l1) & (
        radii["delta_2"] + 1e-15 >= actual_l2
    )
    failures = int(np.sum(~radius_valid))
    condition_policy_rows = []
    risk_rows = []

    for record in policies:
        coordinates = policy_coordinates(record, p0)
        proxy_gain = record["proxy_gain"]
        true_gain = float(np.dot(record["policy"] - p0, proxy + errors))
        lb_1 = proxy_gain - radii["delta_1"] * coordinates["movement_linf"]
        lb_2 = proxy_gain - radii["delta_2"] * coordinates["movement_l2"]
        lb_inf = proxy_gain - coordinates["movement_l1"]
        combined = np.maximum(np.maximum(lb_1, lb_2), lb_inf)
        registered_safe = combined > 0
        pinsker_lb = proxy_gain - math.sqrt(max(0.0, 2 * coordinates["kl_pi_p0"]))
        pinsker_safe = pinsker_lb > 0
        rmse_only_safe = proxy_gain - radii["delta_2"] > 0
        proxy_only_safe = proxy_gain > 0
        false_safe = registered_safe & (true_gain <= 0)
        conditional_false_safe = false_safe & radius_valid
        row = {
            "error_family": family,
            "sample_size": sample_size,
            "policy_id": record["policy_id"],
            "optimizer_family": record["family"],
            "proxy_gain": proxy_gain,
            "true_gain": true_gain,
            **coordinates,
            "registered_certified_fraction": float(np.mean(registered_safe)),
            "registered_false_safe_count": int(np.sum(false_safe)),
            "conditional_false_safe_count": int(np.sum(conditional_false_safe)),
            "pinsker_certified_fraction": float(pinsker_safe),
            "rmse_only_certified_fraction": float(np.mean(rmse_only_safe)),
            "proxy_only_certified_fraction": float(proxy_only_safe),
            "rmse_only_false_safe_count": int(np.sum(rmse_only_safe)) if true_gain <= 0 else 0,
            "proxy_only_false_safe_count": replicates if proxy_only_safe and true_gain <= 0 else 0,
        }
        condition_policy_rows.append(row)
        # Risk/coverage is evaluated at frozen lower-bound cutoffs.
        for threshold in (-0.20, -0.10, -0.05, 0.0, 0.025, 0.05, 0.10):
            selected = combined > threshold
            risk_rows.append(
                {
                    "error_family": family,
                    "sample_size": sample_size,
                    "policy_id": record["policy_id"],
                    "threshold": threshold,
                    "coverage": float(np.mean(selected)),
                    "false_safe_rate": float(np.mean(selected & (true_gain <= 0))),
                }
            )

    condition = {
        "error_family": family,
        "sample_size": sample_size,
        "replicates": replicates,
        "actual_l1": actual_l1,
        "actual_l2": actual_l2,
        "simultaneous_radius_failures": failures,
        "failure_rate": failures / replicates,
        "failure_rate_cp_upper_95": clopper_pearson_upper(failures, replicates),
        "mean_registered_coverage": float(
            np.mean([row["registered_certified_fraction"] for row in condition_policy_rows])
        ),
    }
    return condition, condition_policy_rows, risk_rows


def _optimizer_transfer(rows: list[dict[str, Any]]) -> dict[str, Any]:
    target = [
        row
        for row in rows
        if row["error_family"] == "diffuse_low_error" and row["sample_size"] == 512
    ]
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in target:
        by_family[row["optimizer_family"]].append(row)
    payload = {}
    for family, values in sorted(by_family.items()):
        best = max(values, key=lambda row: row["registered_certified_fraction"])
        payload[family] = {
            "best_policy_id": best["policy_id"],
            "best_certified_fraction": best["registered_certified_fraction"],
            "pass": best["registered_certified_fraction"] >= 0.5,
        }
    return payload


def run_experiment(protocol: dict[str, Any], replicates_override: int | None = None) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    spec = protocol["outcome_registry"]
    count = int(spec["outcome_count"])
    proxy = np.linspace(-0.5, 0.5, count)
    p0 = np.full(count, 1 / count)
    populations = error_populations(count)
    policies = policy_registry(proxy, protocol)
    calibration = protocol["calibration"]
    replicates = int(replicates_override or calibration["replicates_per_condition"])
    sample_sizes = [int(value) for value in calibration["sample_sizes"]]
    alpha_each = float(calibration["allocation"]["weighted_l1_error_moment"])
    seed_sequence = np.random.SeedSequence(int(calibration["root_seed"]))
    condition_seeds = seed_sequence.spawn(len(populations) * len(sample_sizes))

    conditions = []
    policy_rows = []
    risk_rows = []
    index = 0
    for family, errors in populations.items():
        for sample_size in sample_sizes:
            seed = int(condition_seeds[index].generate_state(1, dtype=np.uint64)[0])
            index += 1
            condition, rows, risks = evaluate_condition(
                family,
                errors,
                sample_size,
                replicates,
                seed,
                policies,
                p0,
                proxy,
                alpha_each,
            )
            condition["seed"] = seed
            conditions.append(condition)
            policy_rows.extend(rows)
            risk_rows.extend(risks)

    coverage_pass = all(
        row["failure_rate_cp_upper_95"]
        <= float(protocol["gates_numeric"]["max_failure_cp_upper"])
        for row in conditions
    )
    conditional_false_safe = sum(row["conditional_false_safe_count"] for row in policy_rows)
    diffuse_512 = [
        row
        for row in policy_rows
        if row["error_family"] == "diffuse_low_error"
        and row["sample_size"] == 512
        and row["true_gain"] > 0
    ]
    registered_nonvacuity = float(
        np.mean([row["registered_certified_fraction"] for row in diffuse_512])
    )
    pinsker_nonvacuity = float(np.mean([row["pinsker_certified_fraction"] for row in diffuse_512]))
    transfer = _optimizer_transfer(policy_rows)
    rare = [row for row in policy_rows if row["error_family"] == "rare_top_tail"]
    rare_proxy_false = sum(row["proxy_only_false_safe_count"] for row in rare)
    rare_rmse_false = sum(row["rmse_only_false_safe_count"] for row in rare)
    sample_order_payload = {}
    sample_order_pass = True
    for family in populations:
        values = [
            next(
                row["mean_registered_coverage"]
                for row in conditions
                if row["error_family"] == family and row["sample_size"] == sample_size
            )
            for sample_size in sample_sizes
        ]
        passed = all(right + 1e-15 >= left for left, right in zip(values, values[1:]))
        sample_order_pass &= passed
        sample_order_payload[family] = {"coverages": values, "pass": passed}

    numeric = protocol["gates_numeric"]
    gates = {
        "G1_calibration_coverage": {
            "pass": coverage_pass,
            "maximum_cp_upper": max(row["failure_rate_cp_upper_95"] for row in conditions),
        },
        "G2_certificate_soundness": {
            "pass": conditional_false_safe == 0,
            "conditional_false_safe_count": conditional_false_safe,
        },
        "G3_nonvacuity": {
            "pass": registered_nonvacuity >= float(numeric["minimum_diffuse_nonvacuity"]),
            "registered_fraction": registered_nonvacuity,
            "minimum": float(numeric["minimum_diffuse_nonvacuity"]),
        },
        "G4_stronger_than_pinsker": {
            "pass": registered_nonvacuity - pinsker_nonvacuity
            >= float(numeric["minimum_pinsker_advantage"]),
            "registered_fraction": registered_nonvacuity,
            "pinsker_fraction": pinsker_nonvacuity,
            "difference": registered_nonvacuity - pinsker_nonvacuity,
        },
        "G5_optimizer_transfer": {
            "pass": len(transfer) == 4 and all(item["pass"] for item in transfer.values()),
            "families": transfer,
        },
        "G6_rare_tail_liveness": {
            "pass": rare_proxy_false > 0 and rare_rmse_false > 0 and conditional_false_safe == 0,
            "proxy_only_false_safe_cells": rare_proxy_false,
            "rmse_only_false_safe_cells": rare_rmse_false,
        },
        "G7_sample_size_ordering": {
            "pass": sample_order_pass,
            "families": sample_order_payload,
        },
    }
    result = {
        "schema_version": "asmp8_calibrated_certificate_result_v0_3",
        "condition_count": len(conditions),
        "policy_count": len(policies),
        "policy_family_count": len({record["family"] for record in policies}),
        "replicates_per_condition": replicates,
        "gates": gates,
        "summary": {
            "registered_diffuse_m512_nonvacuity": registered_nonvacuity,
            "pinsker_diffuse_m512_nonvacuity": pinsker_nonvacuity,
            "conditional_false_safe_count": conditional_false_safe,
            "rare_proxy_only_false_safe_cells": rare_proxy_false,
            "rare_rmse_only_false_safe_cells": rare_rmse_false,
        },
        "claim_boundary": protocol["claim_boundary"],
    }
    return result, conditions, policy_rows, risk_rows


def rows_csv(rows: Iterable[dict[str, Any]], fields: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return stream.getvalue()
