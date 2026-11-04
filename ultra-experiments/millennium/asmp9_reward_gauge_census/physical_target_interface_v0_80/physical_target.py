"""Controlled finite-MDP response channel for ASMP-9 v0.80."""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable


EdgeRewards = tuple[Fraction, Fraction, Fraction, Fraction]
SHAPING_DELTA: EdgeRewards = (
    Fraction(3, 5),
    Fraction(-3, 5),
    Fraction(4, 5),
    Fraction(-4, 5),
)
NON_GAUGE_DELTA: EdgeRewards = (
    Fraction(1),
    Fraction(0),
    Fraction(-1),
    Fraction(0),
)


@dataclass(frozen=True)
class Candidate:
    context: str
    split: str
    arm: str
    rewards: EdgeRewards
    target_margin: Fraction


def add(left: EdgeRewards, right: EdgeRewards) -> EdgeRewards:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def scale(value: Fraction, vector: EdgeRewards) -> EdgeRewards:
    return tuple(value * item for item in vector)  # type: ignore[return-value]


def squared_norm(vector: EdgeRewards) -> Fraction:
    return sum((item * item for item in vector), Fraction(0))


def route_margin(rewards: EdgeRewards) -> Fraction:
    return rewards[0] + rewards[1] - rewards[2] - rewards[3]


def build_candidates(config: dict[str, object]) -> tuple[Candidate, ...]:
    candidates = []
    arms = {
        "base": scale(Fraction(0), SHAPING_DELTA),
        "shape_plus": SHAPING_DELTA,
        "shape_minus": scale(Fraction(-1), SHAPING_DELTA),
        "nongauge_plus": NON_GAUGE_DELTA,
        "nongauge_minus": scale(Fraction(-1), NON_GAUGE_DELTA),
    }
    contexts = config["contexts"]
    assert isinstance(contexts, list)
    for context in contexts:
        assert isinstance(context, dict)
        margin = Fraction(str(context["base_margin"]))
        base: EdgeRewards = (
            Fraction(0),
            margin,
            Fraction(0),
            Fraction(0),
        )
        for arm, delta in arms.items():
            rewards = add(base, delta)
            candidates.append(
                Candidate(
                    context=str(context["name"]),
                    split=str(context["split"]),
                    arm=arm,
                    rewards=rewards,
                    target_margin=route_margin(rewards),
                )
            )
    return tuple(candidates)


def exact_wellposedness(config: dict[str, object]) -> dict[str, object]:
    candidates = build_candidates(config)
    by_context = {}
    for candidate in candidates:
        by_context.setdefault(candidate.context, {})[candidate.arm] = candidate
    gauge_ok = all(
        arms["base"].target_margin
        == arms["shape_plus"].target_margin
        == arms["shape_minus"].target_margin
        for arms in by_context.values()
    )
    nongauge_ok = all(
        arms["nongauge_plus"].target_margin
        != arms["base"].target_margin
        != arms["nongauge_minus"].target_margin
        for arms in by_context.values()
    )
    norm_match = squared_norm(SHAPING_DELTA) == squared_norm(NON_GAUGE_DELTA)
    return {
        "gauge_targets_match": gauge_ok,
        "nongauge_targets_change": nongauge_ok,
        "matched_delta_squared_norm": str(squared_norm(SHAPING_DELTA)),
        "delta_norms_match": norm_match,
        "pass": gauge_ok and nongauge_ok and norm_match,
    }


def sigmoid(value: float) -> float:
    if value >= 0:
        inverse = math.exp(-value)
        return 1.0 / (1.0 + inverse)
    direct = math.exp(value)
    return direct / (1.0 + direct)


def choice_probability(margin: Fraction, beta: float) -> float:
    return sigmoid(beta * float(margin))


def record_seed(global_seed: int, candidate_id: str) -> int:
    digest = hashlib.sha256(f"{global_seed}:{candidate_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def bernoulli_affinity(left_probability: float, right_probability: float) -> float:
    return math.sqrt(left_probability * right_probability) + math.sqrt(
        (1-left_probability) * (1-right_probability)
    )


def run_registered(config: dict[str, object], output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=False)
    candidates = build_candidates(config)
    betas = tuple(float(value) for value in config["betas"])  # type: ignore[arg-type]
    samples = int(config["samples_per_query"])
    global_seed = int(config["global_seed"])

    rows = []
    for candidate in candidates:
        for beta in betas:
            candidate_id = f"{candidate.context}|{candidate.arm}|beta={beta:g}"
            probability = choice_probability(candidate.target_margin, beta)
            generator = random.Random(record_seed(global_seed, candidate_id))
            successes = sum(generator.random() < probability for _ in range(samples))
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "context": candidate.context,
                    "split": candidate.split,
                    "arm": candidate.arm,
                    "beta": beta,
                    "samples": samples,
                    "successes": successes,
                    "empirical_probability": successes / samples,
                    "population_probability": probability,
                    "target_margin": float(candidate.target_margin),
                    "reward_edges": [str(value) for value in candidate.rewards],
                    "seed": record_seed(global_seed, candidate_id),
                }
            )

    raw_path = output_dir / "response_rows.jsonl"
    raw_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    result = analyze(config, candidates, rows)
    result_path = output_dir / "result.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    receipt = {
        "config_sha256": hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "response_rows_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
    }
    (output_dir / "run_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def analyze(
    config: dict[str, object],
    candidates: Iterable[Candidate],
    rows: list[dict[str, object]],
) -> dict[str, object]:
    candidates = tuple(candidates)
    betas = tuple(float(value) for value in config["betas"])  # type: ignore[arg-type]
    by_key = {
        (str(row["context"]), str(row["arm"]), float(row["beta"])): row
        for row in rows
    }

    estimates = []
    for candidate in candidates:
        beta_estimates = []
        for beta in betas:
            row = by_key[(candidate.context, candidate.arm, beta)]
            successes = int(row["successes"])
            samples = int(row["samples"])
            probability = (successes + 0.5) / (samples + 1.0)
            beta_estimates.append(math.log(probability / (1-probability)) / beta)
        estimate = sum(beta_estimates) / len(beta_estimates)
        estimates.append(
            {
                "context": candidate.context,
                "split": candidate.split,
                "arm": candidate.arm,
                "target_margin": float(candidate.target_margin),
                "estimated_margin": estimate,
                "absolute_error": abs(estimate - float(candidate.target_margin)),
                "sign_correct": (estimate >= 0) == (candidate.target_margin >= 0),
            }
        )

    leakage_differences = []
    for context in sorted({candidate.context for candidate in candidates}):
        for beta in betas:
            base = float(by_key[(context, "base", beta)]["empirical_probability"])
            for arm in ("shape_plus", "shape_minus"):
                shaped = float(by_key[(context, arm, beta)]["empirical_probability"])
                leakage_differences.append(abs(shaped - base))

    unique_margins = sorted({candidate.target_margin for candidate in candidates})
    sample_count = int(config["samples_per_query"])
    worst_h_bound = 0.0
    for left in unique_margins:
        bound = 0.0
        for right in unique_margins:
            if right == left:
                continue
            product_affinity = 1.0
            for beta in betas:
                product_affinity *= bernoulli_affinity(
                    choice_probability(left, beta),
                    choice_probability(right, beta),
                ) ** sample_count
            bound += product_affinity
        worst_h_bound = max(worst_h_bound, bound)

    epsilon = float(config["per_sample_tv_radius"])
    accumulated_tv = 1-(1-epsilon) ** (sample_count * len(betas))
    robust_bound = min(1.0, worst_h_bound + accumulated_tv)
    gates = {
        "W0": exact_wellposedness(config),
        "R0": {
            "maximum_absolute_margin_error": max(
                item["absolute_error"] for item in estimates
            ),
            "all_signs_correct": all(item["sign_correct"] for item in estimates),
            "threshold": float(config["maximum_absolute_margin_error"]),
        },
        "L0": {
            "maximum_empirical_gauge_probability_difference": max(
                leakage_differences
            ),
            "threshold": float(config["maximum_gauge_probability_difference"]),
        },
        "M0": {
            "registered_hellinger_union_bound": worst_h_bound,
            "per_sample_tv_radius": epsilon,
            "accumulated_tv_penalty": accumulated_tv,
            "robustified_bound": robust_bound,
            "threshold": float(config["maximum_robust_error_bound"]),
        },
    }
    gates["R0"]["pass"] = (
        gates["R0"]["maximum_absolute_margin_error"]  # type: ignore[index]
        <= gates["R0"]["threshold"]  # type: ignore[index]
        and gates["R0"]["all_signs_correct"]  # type: ignore[index]
    )
    gates["L0"]["pass"] = (
        gates["L0"]["maximum_empirical_gauge_probability_difference"]  # type: ignore[index]
        <= gates["L0"]["threshold"]  # type: ignore[index]
    )
    gates["M0"]["pass"] = (
        gates["M0"]["robustified_bound"] <= gates["M0"]["threshold"]  # type: ignore[index]
    )
    return {
        "status": "executed_registered_configuration",
        "estimates": estimates,
        "gates": gates,
        "overall_pass": all(gate["pass"] for gate in gates.values()),
        "claim_boundary": (
            "Controlled finite-MDP softmax demonstrator only; not human/model "
            "value identification or ASMP-9 resolution."
        ),
    }
