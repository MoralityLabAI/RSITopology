from __future__ import annotations

from dataclasses import dataclass
from math import inf, log
from typing import Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import linprog


Distribution = tuple[float, ...]


@dataclass(frozen=True)
class InformationDesign:
    allocation: dict[str, float]
    alternatives: tuple[str, ...]
    divergences: dict[str, dict[str, float]]
    rate: float


def validate_distribution(values: Sequence[float]) -> Distribution:
    distribution = tuple(float(value) for value in values)
    if not distribution:
        raise ValueError("a distribution must have nonempty support")
    if any(not np.isfinite(value) or value < 0 for value in distribution):
        raise ValueError("probabilities must be finite and nonnegative")
    if not np.isclose(sum(distribution), 1.0, atol=1e-12, rtol=0.0):
        raise ValueError("probabilities must sum to one")
    return distribution


def kl_divergence(first: Sequence[float], second: Sequence[float]) -> float:
    p = validate_distribution(first)
    q = validate_distribution(second)
    if len(p) != len(q):
        raise ValueError("distributions must have the same support")
    value = 0.0
    for left, right in zip(p, q, strict=True):
        if left == 0:
            continue
        if right == 0:
            return inf
        value += left * log(left / right)
    return value


def binary_relative_entropy(first: float, second: float) -> float:
    return kl_divergence((first, 1 - first), (second, 1 - second))


def decision_identifiable(
    laws: Mapping[str, Mapping[str, Sequence[float]]],
    answers: Mapping[str, Hashable],
) -> bool:
    hypotheses = tuple(sorted(laws))
    queries = _validate_model(laws, answers)
    for index, first in enumerate(hypotheses):
        for second in hypotheses[index + 1 :]:
            if answers[first] == answers[second]:
                continue
            if not any(
                kl_divergence(
                    laws[first][query],
                    laws[second][query],
                )
                > 0
                for query in queries
            ):
                return False
    return True


def characteristic_design(
    laws: Mapping[str, Mapping[str, Sequence[float]]],
    answers: Mapping[str, Hashable],
    truth: str,
    *,
    distinguish_full_hypothesis: bool = False,
) -> InformationDesign:
    queries = _validate_model(laws, answers)
    if truth not in laws:
        raise KeyError(truth)
    alternatives = tuple(
        hypothesis
        for hypothesis in sorted(laws)
        if hypothesis != truth
        and (
            distinguish_full_hypothesis
            or answers[hypothesis] != answers[truth]
        )
    )
    if not alternatives:
        return InformationDesign(
            allocation={query: 1.0 / len(queries) for query in queries},
            alternatives=(),
            divergences={},
            rate=inf,
        )

    divergences = {
        alternative: {
            query: kl_divergence(
                laws[truth][query],
                laws[alternative][query],
            )
            for query in queries
        }
        for alternative in alternatives
    }
    if any(
        all(value == 0 for value in row.values())
        for row in divergences.values()
    ):
        return InformationDesign(
            allocation={query: 0.0 for query in queries},
            alternatives=alternatives,
            divergences=divergences,
            rate=0.0,
        )
    if any(
        any(not np.isfinite(value) for value in row.values())
        for row in divergences.values()
    ):
        raise ValueError(
            "the development LP requires mutually absolutely continuous laws"
        )

    # Variables are query allocations followed by the guaranteed rate t.
    objective = np.zeros(len(queries) + 1)
    objective[-1] = -1.0
    upper = []
    for alternative in alternatives:
        row = [
            -divergences[alternative][query]
            for query in queries
        ]
        row.append(1.0)
        upper.append(row)
    equality = [([1.0] * len(queries)) + [0.0]]
    result = linprog(
        objective,
        A_ub=np.asarray(upper),
        b_ub=np.zeros(len(upper)),
        A_eq=np.asarray(equality),
        b_eq=np.asarray([1.0]),
        bounds=[(0.0, 1.0)] * len(queries) + [(0.0, None)],
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    allocation = {
        query: float(result.x[index])
        for index, query in enumerate(queries)
    }
    return InformationDesign(
        allocation=allocation,
        alternatives=alternatives,
        divergences=divergences,
        rate=float(result.x[-1]),
    )


def fixed_confidence_lower_bound(
    design: InformationDesign,
    delta: float,
) -> float:
    if not 0 < delta < 0.5:
        raise ValueError("delta must lie strictly between zero and one half")
    if design.rate == 0:
        return inf
    if design.rate == inf:
        return 0.0
    return binary_relative_entropy(1 - delta, delta) / design.rate


def xor_channel_fixture(
    *,
    include_gauge_alias: bool = True,
) -> tuple[
    dict[str, dict[str, Distribution]],
    dict[str, int],
]:
    laws: dict[str, dict[str, Distribution]] = {}
    answers: dict[str, int] = {}
    for reward_bit in (0, 1):
        for mechanics_bit in (0, 1):
            name = f"h{reward_bit}{mechanics_bit}"
            behavior_probability = 0.2 if reward_bit == 0 else 0.8
            mechanics_probability = 0.25 if mechanics_bit == 0 else 0.75
            laws[name] = {
                "behavior": (
                    behavior_probability,
                    1 - behavior_probability,
                ),
                "mechanics": (
                    mechanics_probability,
                    1 - mechanics_probability,
                ),
            }
            answers[name] = reward_bit ^ mechanics_bit
    if include_gauge_alias:
        laws["h00_gauge"] = dict(laws["h00"])
        answers["h00_gauge"] = answers["h00"]
    return laws, answers


def restrict_queries(
    laws: Mapping[str, Mapping[str, Sequence[float]]],
    queries: Sequence[str],
) -> dict[str, dict[str, Distribution]]:
    selected = tuple(queries)
    if not selected:
        raise ValueError("at least one query is required")
    return {
        hypothesis: {
            query: validate_distribution(query_laws[query])
            for query in selected
        }
        for hypothesis, query_laws in laws.items()
    }


def _validate_model(
    laws: Mapping[str, Mapping[str, Sequence[float]]],
    answers: Mapping[str, Hashable],
) -> tuple[str, ...]:
    if not laws:
        raise ValueError("at least one hypothesis is required")
    if set(laws) != set(answers):
        raise ValueError("laws and answers must have the same hypotheses")
    first_queries = tuple(sorted(next(iter(laws.values()))))
    if not first_queries:
        raise ValueError("at least one query is required")
    for query_laws in laws.values():
        if tuple(sorted(query_laws)) != first_queries:
            raise ValueError("every hypothesis must define the same queries")
        for distribution in query_laws.values():
            validate_distribution(distribution)
    return first_queries
