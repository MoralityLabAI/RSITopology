from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Sequence

try:
    from .decision_information import Distribution
except ImportError:
    from decision_information import Distribution  # type: ignore[no-redef]


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V029_PROTOCOL = (
    REPO
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "decision_relevance_v0_29"
    / "protocol_v0_29.json"
)
V031_PROTOCOL = (
    REPO
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "joint_approximate_v0_31"
    / "protocol_v0_31.json"
)
V031_RESULT = (
    REPO
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "joint_approximate_v0_31"
    / "artifacts_v0_31_1"
    / "result_v0_31.json"
)
V032_PROTOCOL = (
    REPO
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "behavioral_rectangle_v0_32"
    / "protocol_v0_32.json"
)
V032_RESULT = (
    REPO
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "behavioral_rectangle_v0_32"
    / "artifacts_v0_32"
    / "result_v0_32.json"
)


@dataclass(frozen=True)
class NativeHypothesis:
    name: str
    reward: tuple[Fraction, ...]
    mechanics: str
    mixture: str


@dataclass(frozen=True)
class NativeSources:
    gauge_basis: tuple[tuple[Fraction, ...], ...]
    measurement_matrix: tuple[tuple[Fraction, ...], ...]
    policies: tuple[tuple[Fraction, ...], ...]
    true_reward: tuple[Fraction, ...]
    valid_mixture_residual: Fraction
    invalid_mixture_residual: Fraction
    v031_analysis_map: tuple[tuple[Fraction, ...], ...]
    v031_measurement_rows: int
    v031_policies: tuple[tuple[Fraction, ...], ...]
    v032_semantic_operator: tuple[tuple[Fraction, ...], ...]
    v032_semantic_residual_rows: int
    source_hashes: dict[str, str]


def q(value: int | str | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational_link(value: Fraction) -> Fraction:
    value = q(value)
    return Fraction(1, 2) + value / (2 * (1 + abs(value)))


def dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    return sum((a * b for a, b in zip(left, right, strict=True)), Fraction())


def mixture_residual(specification: dict) -> Fraction:
    first = q(specification["first"])
    second = q(specification["second"])
    mixture = q(specification["mixture"])
    weight = q(specification["first_weight"])
    return mixture - weight * first - (1 - weight) * second


def load_native_sources() -> NativeSources:
    v029 = json.loads(V029_PROTOCOL.read_text(encoding="utf-8"))
    v031 = json.loads(V031_PROTOCOL.read_text(encoding="utf-8"))
    v031_result = json.loads(V031_RESULT.read_text(encoding="utf-8"))
    v032 = json.loads(V032_PROTOCOL.read_text(encoding="utf-8"))
    v032_result = json.loads(V032_RESULT.read_text(encoding="utf-8"))
    cell = v029["fresh_validation"]["composition_cell"]
    valid = mixture_residual(v032["mixture_controls"]["consistent"])
    invalid = mixture_residual(v032["mixture_controls"]["distorted"])
    policies = tuple(
        tuple(q(value) for value in row)
        for row in cell["policy_occupancies"]
    )
    gauge = tuple(
        tuple(q(value) for value in row)
        for row in cell["gauge_basis"]
    )
    measurement = tuple(
        tuple(q(value) for value in row)
        for row in cell["measurement_matrix"]
    )
    reward = tuple(q(value) for value in cell["true_reward"])
    analysis_map = tuple(
        tuple(q(value) for value in row)
        for row in v031_result["primary"]["certificate"]["analysis_map"]
    )
    v031_policies = tuple(
        tuple(q(value) for value in row)
        for row in v031["primary_fixture"]["policies"]
    )
    semantic_operator = tuple(
        tuple(q(value) for value in row)
        for row in v032_result["primary"]["operator"]
    )

    if any(dot(g, tuple(a - b for a, b in zip(policy, policies[0])))
           for g in gauge for policy in policies[1:]):
        raise RuntimeError("v0.29 gauge is not decision-null")
    if valid != 0 or invalid != Fraction(1, 16):
        raise RuntimeError("v0.32 mixture controls changed unexpectedly")
    v031_rows = len(v031["primary_fixture"]["nominal_design"])
    v032_rows = (
        v032["primary_fixture"]["row_count"] - 1
    ) * (v032["primary_fixture"]["column_count"] - 1)
    return NativeSources(
        gauge_basis=gauge,
        measurement_matrix=measurement,
        policies=policies,
        true_reward=reward,
        valid_mixture_residual=valid,
        invalid_mixture_residual=invalid,
        v031_analysis_map=analysis_map,
        v031_measurement_rows=v031_rows,
        v031_policies=v031_policies,
        v032_semantic_operator=semantic_operator,
        v032_semantic_residual_rows=v032_rows,
        source_hashes={
            V029_PROTOCOL.relative_to(REPO).as_posix(): sha256(V029_PROTOCOL),
            V031_PROTOCOL.relative_to(REPO).as_posix(): sha256(V031_PROTOCOL),
            V031_RESULT.relative_to(REPO).as_posix(): sha256(V031_RESULT),
            V032_PROTOCOL.relative_to(REPO).as_posix(): sha256(V032_PROTOCOL),
            V032_RESULT.relative_to(REPO).as_posix(): sha256(V032_RESULT),
        },
    )


def mechanics_policies(
    sources: NativeSources,
    state: str,
) -> tuple[tuple[Fraction, ...], ...]:
    if state == "nominal":
        return sources.policies
    if state == "coordinate_swap":
        return tuple(
            (policy[1], policy[0], *policy[2:])
            for policy in sources.policies
        )
    raise ValueError(f"unknown mechanics state: {state}")


def answer_for(
    hypothesis: NativeHypothesis,
    sources: NativeSources,
) -> str:
    if hypothesis.mixture != "valid":
        return "not_certified"
    policies = mechanics_policies(sources, hypothesis.mechanics)
    values = tuple(dot(policy, hypothesis.reward) for policy in policies)
    maximum = max(values)
    selected = next(index for index, value in enumerate(values) if value == maximum)
    return f"policy_{selected}"


def native_hypotheses(
    sources: NativeSources,
) -> tuple[NativeHypothesis, ...]:
    reward = sources.true_reward
    reward_flip = (reward[1], reward[0], *reward[2:])
    gauge_alias = tuple(
        value + 7 * sources.gauge_basis[0][index]
        for index, value in enumerate(reward)
    )
    return (
        NativeHypothesis("base", reward, "nominal", "valid"),
        NativeHypothesis(
            "reward_flip",
            reward_flip,
            "nominal",
            "valid",
        ),
        NativeHypothesis(
            "mechanics_flip",
            reward,
            "coordinate_swap",
            "valid",
        ),
        NativeHypothesis(
            "mixture_invalid",
            reward,
            "nominal",
            "invalid",
        ),
        NativeHypothesis(
            "gauge_alias",
            gauge_alias,
            "nominal",
            "valid",
        ),
    )


def bernoulli(probability: Fraction) -> Distribution:
    if not 0 < probability < 1:
        raise ValueError("native fixture requires full-support Bernoulli laws")
    return float(probability), float(1 - probability)


def native_laws_and_answers() -> tuple[
    dict[str, dict[str, Distribution]],
    dict[str, str],
    NativeSources,
]:
    sources = load_native_sources()
    laws: dict[str, dict[str, Distribution]] = {}
    answers: dict[str, str] = {}
    for hypothesis in native_hypotheses(sources):
        row_values = tuple(
            dot(row, hypothesis.reward)
            for row in sources.measurement_matrix
        )
        mechanics_argument = (
            Fraction(1)
            if hypothesis.mechanics == "nominal"
            else Fraction(-1)
        )
        mixture_residual_value = (
            sources.valid_mixture_residual
            if hypothesis.mixture == "valid"
            else sources.invalid_mixture_residual
        )
        laws[hypothesis.name] = {
            **{
                f"return_{index}": bernoulli(rational_link(value))
                for index, value in enumerate(row_values)
            },
            "mechanics_probe": bernoulli(
                rational_link(mechanics_argument)
            ),
            "mixture_audit": bernoulli(
                rational_link(mixture_residual_value)
            ),
        }
        answers[hypothesis.name] = answer_for(hypothesis, sources)
    return laws, answers, sources


def query_families() -> dict[str, tuple[str, ...]]:
    return {
        "return": ("return_0", "return_1"),
        "mechanics": ("mechanics_probe",),
        "mixture": ("mixture_audit",),
    }
