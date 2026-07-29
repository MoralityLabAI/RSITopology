"""Replay verifier for the ASMP-9 v0.37 registered result."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Any, Hashable, Iterable, Sequence

from experiment import (
    BinaryExperiment,
    connected_components,
    directional_deficiency,
    minimax_correspondence_risk,
    minimax_sample_risk,
    population_observation_sets,
    sampled_support_sets,
)


Q = Fraction
GRID = (Q(1, 4), Q(1, 3), Q(2, 3), Q(3, 4))
DECISIONS = (
    (0, 0, 1),
    (0, 1, 0),
    (0, 1, 1),
    (0, 1, 2),
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def experiment_from_flat(values: Sequence[Q]) -> BinaryExperiment:
    return BinaryExperiment(
        (
            (values[0], values[1]),
            (values[2], values[3]),
            (values[4], values[5]),
        )
    )


def oracle_summary(
    observations: callable,
    risk: callable,
) -> dict[str, Any]:
    groups: dict[
        tuple[tuple[int, ...], ...], set[tuple[Q, ...]]
    ] = defaultdict(set)
    for values in product(GRID, repeat=6):
        experiment = experiment_from_flat(values)
        components = connected_components(observations(experiment))
        profile = tuple(risk(experiment, decision) for decision in DECISIONS)
        groups[components].add(profile)
    maximum_spread = Q(0)
    for profiles in groups.values():
        for index in range(len(DECISIONS)):
            values = [profile[index] for profile in profiles]
            maximum_spread = max(
                maximum_spread, max(values) - min(values)
            )
    return {
        "quotient_classes": len(groups),
        "classes_with_multiple_risk_profiles": sum(
            len(profiles) > 1 for profiles in groups.values()
        ),
        "maximum_within_quotient_risk_spread": maximum_spread,
    }


def sample_risk(
    experiment: BinaryExperiment, decisions: Sequence[Hashable]
) -> Q:
    return minimax_sample_risk(experiment, decisions).value


def population_risk(
    experiment: BinaryExperiment, decisions: Sequence[Hashable]
) -> Q:
    return minimax_correspondence_risk(
        population_observation_sets(experiment), decisions
    ).value


def anchors() -> dict[str, Any]:
    uninformative = experiment_from_flat((Q(1, 2),) * 6)
    informative = BinaryExperiment(
        (
            (Q(1, 4), Q(1, 4)),
            (Q(1, 2), Q(1, 2)),
            (Q(3, 4), Q(3, 4)),
        )
    )
    constant = experiment_from_flat((Q(0),) * 6)
    nuisance = BinaryExperiment(
        ((Q(0), Q(1)), (Q(0), Q(1)), (Q(0), Q(1)))
    )
    path = BinaryExperiment(
        ((Q(0), Q(0)), (Q(0), Q(1)), (Q(1), Q(1)))
    )
    named = (uninformative, informative, constant, nuisance, path)
    violations = 0
    comparisons = 0
    minimum_slack: Q | None = None
    for source in named:
        for target in named:
            bound = directional_deficiency(source, target).value
            for decision in DECISIONS:
                comparisons += 1
                gap = (
                    minimax_sample_risk(source, decision).value
                    - minimax_sample_risk(target, decision).value
                )
                violations += gap > bound
                slack = bound - gap
                minimum_slack = (
                    slack
                    if minimum_slack is None
                    else min(minimum_slack, slack)
                )
    risk_gaps = tuple(
        minimax_sample_risk(constant, decision).value
        - minimax_sample_risk(nuisance, decision).value
        for decision in DECISIONS
    )
    return {
        "informative_to_uninformative": directional_deficiency(
            informative, uninformative
        ).value,
        "uninformative_to_informative": directional_deficiency(
            uninformative, informative
        ).value,
        "comparisons": comparisons,
        "violations": violations,
        "minimum_slack": minimum_slack,
        "conservatism_deficiency": directional_deficiency(
            constant, nuisance
        ).value,
        "maximum_target_risk_gap": max(risk_gaps),
    }


def verify(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected_hash = str(payload["result_content_sha256"])
    actual_hash = hashlib.sha256(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "result_content_sha256"
            }
        )
    ).hexdigest()
    sample = oracle_summary(sampled_support_sets, sample_risk)
    population = oracle_summary(
        population_observation_sets, population_risk
    )
    replay_anchors = anchors()
    checks = {
        "result_content_hash": expected_hash == actual_hash,
        "all_gates_pass": all(
            row["decision"] == "pass" for row in payload["gates"]
        ),
        "enumeration_count": payload["experiments"] == len(GRID) ** 6,
        "sample_quotient_classes": (
            payload["sampled_transcript_oracle"]["quotient_classes"]
            == sample["quotient_classes"]
        ),
        "sample_heterogeneous_classes": (
            payload["sampled_transcript_oracle"][
                "classes_with_multiple_risk_profiles"
            ]
            == sample["classes_with_multiple_risk_profiles"]
        ),
        "sample_maximum_spread": Q(
            payload["sampled_transcript_oracle"][
                "maximum_within_quotient_risk_spread"
            ]
        )
        == sample["maximum_within_quotient_risk_spread"],
        "population_quotient_classes": (
            payload["population_law_oracle"]["quotient_classes"]
            == population["quotient_classes"]
        ),
        "population_heterogeneous_classes": (
            payload["population_law_oracle"][
                "classes_with_multiple_risk_profiles"
            ]
            == population["classes_with_multiple_risk_profiles"]
        ),
        "population_maximum_spread": Q(
            payload["population_law_oracle"][
                "maximum_within_quotient_risk_spread"
            ]
        )
        == population["maximum_within_quotient_risk_spread"],
        "blackwell_anchor": (
            replay_anchors["informative_to_uninformative"] == 0
            and replay_anchors["uninformative_to_informative"] == Q(1, 4)
        ),
        "risk_transfer": (
            replay_anchors["comparisons"] == 100
            and replay_anchors["violations"] == 0
            and replay_anchors["minimum_slack"] is not None
            and replay_anchors["minimum_slack"] >= 0
        ),
        "conservatism": (
            replay_anchors["conservatism_deficiency"] == Q(1, 2)
            and replay_anchors["maximum_target_risk_gap"] == 0
        ),
    }
    return {
        "schema_version": (
            "asmp9_stochastic_experiment_verification_v0_37"
        ),
        "passed": all(checks.values()),
        "checks": checks,
        "recomputed": {
            "sampled_transcript_oracle": {
                **sample,
                "maximum_within_quotient_risk_spread": str(
                    sample["maximum_within_quotient_risk_spread"]
                ),
            },
            "population_law_oracle": {
                **population,
                "maximum_within_quotient_risk_spread": str(
                    population["maximum_within_quotient_risk_spread"]
                ),
            },
        },
        "result_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    verification = verify(args.result.resolve())
    data = canonical_bytes(verification)
    output = args.output.resolve()
    if output.exists() and output.read_bytes() != data:
        raise FileExistsError(f"refusing unequal verification: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        output.write_bytes(data)
    if not verification["passed"]:
        raise SystemExit(1)
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
