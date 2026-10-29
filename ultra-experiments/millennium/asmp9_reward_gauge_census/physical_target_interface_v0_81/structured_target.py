"""Structured finite-MDP target decoder for ASMP-9 v0.81."""

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
ARM_DELTAS: dict[str, EdgeRewards] = {
    "base": (Fraction(0),) * 4,
    "shape_plus": SHAPING_DELTA,
    "shape_minus": tuple(-value for value in SHAPING_DELTA),  # type: ignore[dict-item]
    "nongauge_plus": NON_GAUGE_DELTA,
    "nongauge_minus": tuple(-value for value in NON_GAUGE_DELTA),  # type: ignore[dict-item]
}


@dataclass(frozen=True)
class Candidate:
    context: str
    split: str
    arm: str
    rewards: EdgeRewards
    base_margin: Fraction
    target_margin: Fraction


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(left: EdgeRewards, right: EdgeRewards) -> EdgeRewards:
    return tuple(a + b for a, b in zip(left, right, strict=True))  # type: ignore[return-value]


def squared_norm(vector: EdgeRewards) -> Fraction:
    return sum((value * value for value in vector), Fraction(0))


def route_margin(rewards: EdgeRewards) -> Fraction:
    return rewards[0] + rewards[1] - rewards[2] - rewards[3]


def sigmoid(value: float) -> float:
    if value >= 0:
        inverse = math.exp(-value)
        return 1.0 / (1.0 + inverse)
    direct = math.exp(value)
    return direct / (1.0 + direct)


def build_candidates(config: dict[str, object]) -> tuple[Candidate, ...]:
    candidates = []
    contexts = config["contexts"]
    assert isinstance(contexts, list)
    for context in contexts:
        assert isinstance(context, dict)
        base_margin = Fraction(str(context["base_margin"]))
        base: EdgeRewards = (
            Fraction(0),
            base_margin,
            Fraction(0),
            Fraction(0),
        )
        for arm, delta in ARM_DELTAS.items():
            rewards = add(base, delta)
            candidates.append(
                Candidate(
                    context=str(context["name"]),
                    split=str(context["split"]),
                    arm=arm,
                    rewards=rewards,
                    base_margin=base_margin,
                    target_margin=route_margin(rewards),
                )
            )
    return tuple(candidates)


def exact_wellposedness(config: dict[str, object]) -> dict[str, object]:
    by_context: dict[str, dict[str, Candidate]] = {}
    for candidate in build_candidates(config):
        by_context.setdefault(candidate.context, {})[candidate.arm] = candidate
    gauge_ok = all(
        arms["base"].target_margin
        == arms["shape_plus"].target_margin
        == arms["shape_minus"].target_margin
        for arms in by_context.values()
    )
    nongauge_ok = all(
        arms["nongauge_plus"].target_margin - arms["base"].target_margin == 2
        and arms["nongauge_minus"].target_margin - arms["base"].target_margin
        == -2
        for arms in by_context.values()
    )
    norm_match = squared_norm(SHAPING_DELTA) == squared_norm(NON_GAUGE_DELTA)
    return {
        "gauge_targets_match": gauge_ok,
        "nongauge_offsets_exact": nongauge_ok,
        "matched_delta_squared_norm": str(squared_norm(SHAPING_DELTA)),
        "delta_norms_match": norm_match,
        "pass": gauge_ok and nongauge_ok and norm_match,
    }


def record_seed(global_seed: int, candidate_id: str) -> int:
    digest = hashlib.sha256(f"{global_seed}:{candidate_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def choice_probability(margin: float, beta: float) -> float:
    return sigmoid(beta * margin)


def bernoulli_affinity(left_probability: float, right_probability: float) -> float:
    return math.sqrt(left_probability * right_probability) + math.sqrt(
        (1.0 - left_probability) * (1.0 - right_probability)
    )


def structured_score(
    theta: float,
    rows: Iterable[dict[str, object]],
    offsets: dict[str, float],
) -> float:
    total = 0.0
    for row in rows:
        arm = str(row["arm"])
        beta = float(row["beta"])
        successes = int(row["successes"])
        samples = int(row["samples"])
        probability = sigmoid(beta * (theta + offsets[arm]))
        total += beta * ((successes + 0.5) - (samples + 1.0) * probability)
    return total


def structured_mle(
    rows: list[dict[str, object]], config: dict[str, object]
) -> tuple[float, dict[str, object]]:
    offsets = {
        str(key): float(value)
        for key, value in dict(config["decoder_arm_offsets"]).items()
    }
    decoder_rows = [row for row in rows if str(row["arm"]) in offsets]
    expected = len(offsets) * len(config["betas"])  # type: ignore[arg-type]
    if len(decoder_rows) != expected:
        raise ValueError("incomplete structured-decoder row universe")
    bracket = [float(value) for value in config["mle_bracket"]]  # type: ignore[arg-type]
    lower, upper = bracket
    lower_score = structured_score(lower, decoder_rows, offsets)
    upper_score = structured_score(upper, decoder_rows, offsets)
    admitted = lower_score > 0.0 and upper_score < 0.0
    if not admitted:
        raise ValueError("structured score does not cross zero inside bracket")
    iterations = int(config["mle_bisection_iterations"])
    for _ in range(iterations):
        midpoint = (lower + upper) / 2.0
        if structured_score(midpoint, decoder_rows, offsets) > 0.0:
            lower = midpoint
        else:
            upper = midpoint
    estimate = (lower + upper) / 2.0
    return estimate, {
        "decoder_rows": len(decoder_rows),
        "lower_score": lower_score,
        "upper_score": upper_score,
        "iterations": iterations,
        "final_bracket_width": upper - lower,
        "admitted": admitted,
    }


def armwise_v080_estimate(rows: list[dict[str, object]]) -> float:
    estimates = []
    for row in sorted(rows, key=lambda item: float(item["beta"])):
        successes = int(row["successes"])
        samples = int(row["samples"])
        probability = (successes + 0.5) / (samples + 1.0)
        estimates.append(
            math.log(probability / (1.0 - probability)) / float(row["beta"])
        )
    return sum(estimates) / len(estimates)


def structured_hellinger_bound(config: dict[str, object]) -> dict[str, object]:
    offsets = tuple(
        float(value)
        for _, value in sorted(dict(config["decoder_arm_offsets"]).items())
    )
    betas = tuple(float(value) for value in config["betas"])  # type: ignore[arg-type]
    samples = int(config["samples_per_query"])
    hypotheses = tuple(
        sorted(float(Fraction(str(row["base_margin"]))) for row in config["contexts"])  # type: ignore[index]
    )
    worst_union = 0.0
    by_hypothesis = []
    for left in hypotheses:
        union = 0.0
        for right in hypotheses:
            if right == left:
                continue
            affinity = 1.0
            for offset in offsets:
                for beta in betas:
                    affinity *= bernoulli_affinity(
                        choice_probability(left + offset, beta),
                        choice_probability(right + offset, beta),
                    ) ** samples
            union += affinity
        by_hypothesis.append({"base_margin": left, "union_bound": union})
        worst_union = max(worst_union, union)
    decoder_samples = len(offsets) * len(betas) * samples
    epsilon = float(config["per_sample_tv_radius"])
    tv_penalty = 1.0 - (1.0 - epsilon) ** decoder_samples
    robustified = min(1.0, worst_union + tv_penalty)
    return {
        "hypotheses": list(hypotheses),
        "decoder_arm_count": len(offsets),
        "beta_count": len(betas),
        "samples_per_cell": samples,
        "decoder_samples_per_context": decoder_samples,
        "hellinger_union_bound": worst_union,
        "by_hypothesis": by_hypothesis,
        "per_sample_tv_radius": epsilon,
        "accumulated_tv_penalty": tv_penalty,
        "robustified_bound": robustified,
        "threshold": float(config["maximum_robust_error_bound"]),
        "pass": robustified <= float(config["maximum_robust_error_bound"]),
    }


def analyze(
    config: dict[str, object],
    candidates: Iterable[Candidate],
    rows: list[dict[str, object]],
) -> dict[str, object]:
    candidates = tuple(candidates)
    by_context: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_context.setdefault(str(row["context"]), []).append(row)
    candidate_by_key = {
        (candidate.context, candidate.arm): candidate for candidate in candidates
    }

    offsets = {
        str(key): float(value)
        for key, value in dict(config["decoder_arm_offsets"]).items()
    }
    exact_offsets = {
        arm: float(route_margin(ARM_DELTAS[arm])) for arm in offsets
    }
    decoder_arm_set_ok = set(offsets) == {
        "base",
        "nongauge_minus",
        "nongauge_plus",
    }
    shaping_excluded = not {"shape_plus", "shape_minus"}.intersection(offsets)
    offsets_exact = offsets == exact_offsets

    estimates = []
    context_diagnostics = []
    for context in sorted(by_context):
        theta_hat, diagnostic = structured_mle(by_context[context], config)
        diagnostic["context"] = context
        context_diagnostics.append(diagnostic)
        for arm in ARM_DELTAS:
            candidate = candidate_by_key[(context, arm)]
            arm_offset = float(route_margin(ARM_DELTAS[arm]))
            estimated = theta_hat + arm_offset
            target = float(candidate.target_margin)
            estimates.append(
                {
                    "context": context,
                    "split": candidate.split,
                    "arm": arm,
                    "target_margin": target,
                    "estimated_margin": estimated,
                    "absolute_error": abs(estimated - target),
                    "sign_correct": (estimated >= 0.0) == (target >= 0.0),
                }
            )

    baseline_estimates = []
    for context in sorted(by_context):
        for arm in ARM_DELTAS:
            arm_rows = [
                row for row in by_context[context] if str(row["arm"]) == arm
            ]
            estimate = armwise_v080_estimate(arm_rows)
            target = float(candidate_by_key[(context, arm)].target_margin)
            baseline_estimates.append(
                {
                    "context": context,
                    "arm": arm,
                    "target_margin": target,
                    "estimated_margin": estimate,
                    "absolute_error": abs(estimate - target),
                }
            )

    betas = tuple(float(value) for value in config["betas"])  # type: ignore[arg-type]
    row_by_key = {
        (str(row["context"]), str(row["arm"]), float(row["beta"])): row
        for row in rows
    }
    leakage = []
    for context in sorted(by_context):
        for beta in betas:
            base = float(row_by_key[(context, "base", beta)]["empirical_probability"])
            for arm in ("shape_plus", "shape_minus"):
                shaped = float(
                    row_by_key[(context, arm, beta)]["empirical_probability"]
                )
                leakage.append(abs(shaped - base))

    w0 = exact_wellposedness(config)
    d0_pass = (
        decoder_arm_set_ok
        and shaping_excluded
        and offsets_exact
        and all(item["admitted"] for item in context_diagnostics)
    )
    maximum_error = max(item["absolute_error"] for item in estimates)
    all_signs_correct = all(item["sign_correct"] for item in estimates)
    r0_pass = (
        maximum_error <= float(config["maximum_absolute_margin_error"])
        and all_signs_correct
    )
    maximum_leakage = max(leakage)
    l0_pass = maximum_leakage <= float(
        config["maximum_gauge_probability_difference"]
    )
    m0 = structured_hellinger_bound(config)
    return {
        "schema_version": "asmp9_structured_target_result_v0_81",
        "status": "executed_registered_configuration",
        "estimates": estimates,
        "context_diagnostics": context_diagnostics,
        "burned_design_comparator": {
            "gate_consumed": False,
            "estimates": baseline_estimates,
            "maximum_absolute_margin_error": max(
                item["absolute_error"] for item in baseline_estimates
            ),
        },
        "gates": {
            "W0": w0,
            "D0": {
                "decoder_arm_set_exact": decoder_arm_set_ok,
                "shaping_representatives_excluded": shaping_excluded,
                "registered_offsets_exact": offsets_exact,
                "all_scores_bracketed": all(
                    item["admitted"] for item in context_diagnostics
                ),
                "pass": d0_pass,
            },
            "R0": {
                "maximum_absolute_margin_error": maximum_error,
                "all_signs_correct": all_signs_correct,
                "threshold": float(config["maximum_absolute_margin_error"]),
                "pass": r0_pass,
            },
            "L0": {
                "maximum_empirical_gauge_probability_difference": maximum_leakage,
                "threshold": float(
                    config["maximum_gauge_probability_difference"]
                ),
                "pass": l0_pass,
            },
            "M0": m0,
        },
        "claim_boundary": (
            "Known intervention offsets in one controlled finite-MDP softmax "
            "fixture only; not natural value identification or ASMP-9 resolution."
        ),
    }


def run_registered(config: dict[str, object], output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=False)
    candidates = build_candidates(config)
    betas = tuple(float(value) for value in config["betas"])  # type: ignore[arg-type]
    samples = int(config["samples_per_query"])
    global_seed = int(config["global_seed"])
    rows = []
    for candidate in candidates:
        for beta in betas:
            candidate_id = (
                f"v081|{candidate.context}|{candidate.arm}|beta={beta:g}"
            )
            probability = choice_probability(float(candidate.target_margin), beta)
            seed = record_seed(global_seed, candidate_id)
            generator = random.Random(seed)
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
                    "base_margin": float(candidate.base_margin),
                    "target_margin": float(candidate.target_margin),
                    "reward_edges": [str(value) for value in candidate.rewards],
                    "seed": seed,
                }
            )
    rows.sort(key=lambda row: str(row["candidate_id"]))
    rows_path = output_dir / "response_rows.jsonl"
    rows_path.write_bytes(
        b"".join(canonical_json_bytes(row) for row in rows)
    )
    result = analyze(config, candidates, rows)
    result_path = output_dir / "result.json"
    result_path.write_bytes(canonical_json_bytes(result))
    receipt = {
        "config_sha256": hashlib.sha256(canonical_json_bytes(config)).hexdigest(),
        "response_rows_sha256": sha256(rows_path),
        "result_sha256": sha256(result_path),
    }
    (output_dir / "run_receipt.json").write_bytes(canonical_json_bytes(receipt))
    return result

