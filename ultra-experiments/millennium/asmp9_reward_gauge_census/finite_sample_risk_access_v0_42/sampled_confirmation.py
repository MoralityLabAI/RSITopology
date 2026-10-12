"""Seed-bound iid sampling and exact empirical-channel compilation for v0.42."""

from __future__ import annotations

from fractions import Fraction as Q
import hashlib
from pathlib import Path
import sys
from typing import Mapping


BASE = Path(__file__).resolve().parent
V41 = BASE.parent / "sequential_risk_access_v0_41"
if str(V41) not in sys.path:
    sys.path.insert(0, str(V41))

from confirmation import (  # noqa: E402
    CLASSIFICATION,
    ERROR_RATES,
    FULL_RISK,
    ROOT_GROUP,
    SIGNATURES,
    noisy_binary_query,
)
from sequential_access import (  # noqa: E402
    DecisionProblem,
    QueryChannel,
    adaptive_upper_generators,
    directed_upper_deficiency,
    nonadaptive_upper_generators,
    qstr,
)

from finite_sample_access import (  # noqa: E402
    TRUE_ADAPTIVE,
    TRUE_OPEN_LOOP,
    access_decision,
    deficiency_interval,
    policy_risk_radii,
    shared_binary_flip_radius,
)


QUERY_ORDER = ("root_q", "left_q", "right_q")
TRUE_DEFICIENCIES = {
    (CLASSIFICATION.name, "adaptive"): TRUE_ADAPTIVE,
    (CLASSIFICATION.name, "open_loop"): TRUE_OPEN_LOOP,
    (ROOT_GROUP.name, "adaptive"): Q(4, 45),
    (ROOT_GROUP.name, "open_loop"): Q(4, 45),
}
TOLERANCES = {
    CLASSIFICATION.name: Q(1, 2),
    ROOT_GROUP.name: Q(1, 10),
}


def seed_from_registration_bytes(registration_bytes: bytes) -> bytes:
    """Derive a seed after the registration bytes have been frozen."""

    return hashlib.sha256(
        registration_bytes + b"\0asmp9-v0.42-sampled-confirmation"
    ).digest()


def _uniform_residue(
    seed: bytes,
    stream: str,
    trial: int,
    modulus: int,
) -> int:
    """Return a deterministic unbiased residue using rejection sampling."""

    if not seed:
        raise ValueError("seed cannot be empty")
    if trial < 0 or modulus < 1:
        raise ValueError("trial must be nonnegative and modulus positive")
    space = 1 << 64
    limit = space - (space % modulus)
    attempt = 0
    while True:
        message = f"{stream}\0{trial}\0{attempt}".encode("utf-8")
        draw = int.from_bytes(
            hashlib.blake2b(
                message,
                key=seed,
                digest_size=8,
            ).digest(),
            "big",
        )
        if draw < limit:
            return draw % modulus
        attempt += 1


def exact_bernoulli_count(
    seed: bytes,
    stream: str,
    trials: int,
    probability: Q,
) -> int:
    """Count seeded Bernoulli draws without floating-point sampling."""

    probability = Q(probability)
    if trials < 1:
        raise ValueError("trials must be positive")
    if not Q(0) <= probability <= Q(1):
        raise ValueError("probability must lie in [0,1]")
    return sum(
        _uniform_residue(
            seed,
            stream,
            trial,
            probability.denominator,
        )
        < probability.numerator
        for trial in range(trials)
    )


def sample_shared_flip_channels(
    samples_per_target: int,
    seed: bytes,
) -> tuple[tuple[QueryChannel, ...], dict]:
    """Sample each target, then pool the registered shared flip parameter."""

    if samples_per_target < 1:
        raise ValueError("samples_per_target must be positive")
    target_count = CLASSIFICATION.target_count
    channels = []
    receipt = {}
    for query_name in QUERY_ORDER:
        counts = [
            exact_bernoulli_count(
                seed,
                f"{query_name}/target-{target}",
                samples_per_target,
                ERROR_RATES[query_name],
            )
            for target in range(target_count)
        ]
        total = target_count * samples_per_target
        pooled_count = sum(counts)
        empirical_error = Q(pooled_count, total)
        channels.append(
            noisy_binary_query(
                query_name,
                SIGNATURES[query_name],
                empirical_error,
            )
        )
        receipt[query_name] = {
            "true_error_rate": qstr(ERROR_RATES[query_name]),
            "flip_counts_by_target": counts,
            "pooled_flips": pooled_count,
            "pooled_trials": total,
            "empirical_error_rate": qstr(empirical_error),
            "absolute_error": qstr(
                abs(empirical_error - ERROR_RATES[query_name])
            ),
        }
    return tuple(channels), receipt


def _compile_arm(
    queries: tuple[QueryChannel, ...],
    problem: DecisionProblem,
    mode: str,
) -> tuple[Q, int]:
    if mode == "adaptive":
        generators = adaptive_upper_generators(queries, problem, 2)
    elif mode == "open_loop":
        generators = nonadaptive_upper_generators(queries, problem, 2)
    else:
        raise ValueError(f"unknown mode: {mode}")
    certificate = directed_upper_deficiency(generators, FULL_RISK)
    return certificate.epsilon, len(generators)


def run_sampled_confirmation(
    samples_per_target: int,
    seed: bytes,
    alpha: float = 0.05,
    practical_margins: Mapping[str, float] | None = None,
) -> dict:
    """Compile sampled channels and confidence-valid access decisions."""

    practical_margins = dict(practical_margins or {})
    queries, sampling_receipt = sample_shared_flip_channels(
        samples_per_target,
        seed,
    )
    radius = shared_binary_flip_radius(
        query_count=len(queries),
        targets=CLASSIFICATION.target_count,
        samples_per_target=samples_per_target,
        alpha=alpha,
    )
    tv_radii = {
        (target, query_name): radius
        for target in range(CLASSIFICATION.target_count)
        for query_name in QUERY_ORDER
    }
    event_holds = all(
        float(Q(row["absolute_error"])) <= radius
        for row in sampling_receipt.values()
    )
    problems = (CLASSIFICATION, ROOT_GROUP)
    arms = []
    for problem in problems:
        risk_radii = policy_risk_radii(
            problem.losses,
            horizon=2,
            query_names=QUERY_ORDER,
            tv_radii=tv_radii,
        )
        for mode in ("adaptive", "open_loop"):
            point, generator_count = _compile_arm(
                queries,
                problem,
                mode,
            )
            interval = deficiency_interval(
                float(point),
                risk_radii,
                (0.0,) * problem.target_count,
                alpha=alpha,
            )
            true_value = TRUE_DEFICIENCIES[(problem.name, mode)]
            margin = float(practical_margins.get(problem.name, 0.0))
            arms.append(
                {
                    "decision_problem": problem.name,
                    "mode": mode,
                    "empirical_deficiency": qstr(point),
                    "true_deficiency": qstr(true_value),
                    "generator_count": generator_count,
                    "targetwise_risk_radii": list(risk_radii),
                    "interval": interval.jsonable(),
                    "contains_true_deficiency": (
                        interval.lower
                        <= float(true_value)
                        <= interval.upper
                    ),
                    "tolerance": qstr(TOLERANCES[problem.name]),
                    "practical_margin": margin,
                    "decision": access_decision(
                        interval,
                        float(TOLERANCES[problem.name]),
                        practical_margin=margin,
                    ),
                }
            )
    return {
        "phase": "sampled_confirmation",
        "samples_per_target_query": samples_per_target,
        "pooled_samples_per_query": (
            CLASSIFICATION.target_count * samples_per_target
        ),
        "alpha": alpha,
        "seed_sha256": hashlib.sha256(seed).hexdigest(),
        "simultaneous_query_tv_radius": radius,
        "simultaneous_channel_event_holds": event_holds,
        "sampling_receipt": sampling_receipt,
        "arms": arms,
        "all_true_deficiencies_contained": all(
            row["contains_true_deficiency"] for row in arms
        ),
    }
