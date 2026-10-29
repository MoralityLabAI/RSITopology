"""Run the burned v0.37 exact-rational liveness census."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
from typing import Any, Callable, Hashable, Sequence

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
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "DEVELOPMENT_RESULT_v0_37.json"
GRID = (Q(0), Q(1, 2), Q(1))
DECISIONS = {
    "cut_01_vs_2": (0, 0, 1),
    "cut_02_vs_1": (0, 1, 0),
    "cut_0_vs_12": (0, 1, 1),
    "identity": (0, 1, 2),
}


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def experiment_from_flat(values: Sequence[Q]) -> BinaryExperiment:
    return BinaryExperiment(
        (
            (values[0], values[1]),
            (values[2], values[3]),
            (values[4], values[5]),
        )
    )


def flat_record(experiment: BinaryExperiment) -> list[str]:
    return [
        qstr(value)
        for row in experiment.probabilities
        for value in row
    ]


def risk_profile(
    experiment: BinaryExperiment,
    risk_function: Callable[
        [BinaryExperiment, Sequence[Hashable]], Any
    ],
) -> tuple[Q, ...]:
    return tuple(
        risk_function(experiment, decision).value
        for decision in DECISIONS.values()
    )


def population_risk(
    experiment: BinaryExperiment,
    decisions: Sequence[Hashable],
) -> Any:
    return minimax_correspondence_risk(
        population_observation_sets(experiment), decisions
    )


def quotient_summary(
    rows: Sequence[
        tuple[
            tuple[tuple[int, ...], ...],
            tuple[Q, ...],
            BinaryExperiment,
        ]
    ],
) -> dict[str, Any]:
    groups: dict[
        tuple[tuple[int, ...], ...],
        list[tuple[tuple[Q, ...], BinaryExperiment]],
    ] = defaultdict(list)
    for components, profile, experiment in rows:
        groups[components].append((profile, experiment))

    heterogeneous = 0
    best: tuple[
        Q,
        str,
        tuple[tuple[int, ...], ...],
        BinaryExperiment,
        BinaryExperiment,
        Q,
        Q,
    ] | None = None
    decision_names = tuple(DECISIONS)
    for components, members in groups.items():
        profiles = {profile for profile, _ in members}
        heterogeneous += len(profiles) > 1
        for decision_index, decision_name in enumerate(decision_names):
            low_profile, low_experiment = min(
                members, key=lambda item: item[0][decision_index]
            )
            high_profile, high_experiment = max(
                members, key=lambda item: item[0][decision_index]
            )
            low = low_profile[decision_index]
            high = high_profile[decision_index]
            candidate = (
                high - low,
                decision_name,
                components,
                low_experiment,
                high_experiment,
                low,
                high,
            )
            if best is None or (
                candidate[0],
                candidate[1],
                candidate[2],
                flat_record(candidate[3]),
                flat_record(candidate[4]),
            ) > (
                best[0],
                best[1],
                best[2],
                flat_record(best[3]),
                flat_record(best[4]),
            ):
                best = candidate
    if best is None:
        raise AssertionError("empty quotient census")
    (
        spread,
        decision_name,
        components,
        low_experiment,
        high_experiment,
        low,
        high,
    ) = best
    return {
        "quotient_classes": len(groups),
        "classes_with_multiple_risk_profiles": heterogeneous,
        "maximum_within_quotient_risk_spread": qstr(spread),
        "maximum_spread_witness": {
            "decision": decision_name,
            "components": [list(component) for component in components],
            "low_risk": qstr(low),
            "high_risk": qstr(high),
            "low_experiment": flat_record(low_experiment),
            "high_experiment": flat_record(high_experiment),
        },
    }


def named_experiments() -> dict[str, BinaryExperiment]:
    return {
        "uninformative": experiment_from_flat((Q(1, 2),) * 6),
        "informative": BinaryExperiment(
            (
                (Q(1, 4), Q(1, 4)),
                (Q(1, 2), Q(1, 2)),
                (Q(3, 4), Q(3, 4)),
            )
        ),
        "constant_zero": experiment_from_flat((Q(0),) * 6),
        "nuisance_only": BinaryExperiment(
            ((Q(0), Q(1)), (Q(0), Q(1)), (Q(0), Q(1)))
        ),
        "population_path": BinaryExperiment(
            ((Q(0), Q(0)), (Q(0), Q(1)), (Q(1), Q(1)))
        ),
    }


def anchor_checks() -> dict[str, Any]:
    experiments = named_experiments()
    uninformative = experiments["uninformative"]
    informative = experiments["informative"]
    constant_zero = experiments["constant_zero"]
    nuisance_only = experiments["nuisance_only"]

    comparisons = 0
    violations = 0
    minimum_slack: Q | None = None
    for source in experiments.values():
        for target in experiments.values():
            bound = directional_deficiency(source, target).value
            for decision in DECISIONS.values():
                comparisons += 1
                source_risk = minimax_sample_risk(
                    source, decision
                ).value
                target_risk = minimax_sample_risk(
                    target, decision
                ).value
                gap = source_risk - target_risk
                violations += gap > bound
                slack = bound - gap
                minimum_slack = (
                    slack
                    if minimum_slack is None
                    else min(minimum_slack, slack)
                )

    target_only_gaps = []
    for decision in DECISIONS.values():
        target_only_gaps.append(
            minimax_sample_risk(constant_zero, decision).value
            - minimax_sample_risk(nuisance_only, decision).value
        )
    return {
        "blackwell_anchor": {
            "informative_to_uninformative": qstr(
                directional_deficiency(
                    informative, uninformative
                ).value
            ),
            "uninformative_to_informative": qstr(
                directional_deficiency(
                    uninformative, informative
                ).value
            ),
        },
        "risk_transfer": {
            "comparisons": comparisons,
            "violations": violations,
            "minimum_bound_minus_gap": qstr(
                minimum_slack if minimum_slack is not None else Q(0)
            ),
        },
        "conservatism_witness": {
            "expanded_parameter_deficiency": qstr(
                directional_deficiency(
                    constant_zero, nuisance_only
                ).value
            ),
            "maximum_registered_target_only_risk_gap": qstr(
                max(target_only_gaps)
            ),
            "all_registered_risk_gaps": [
                qstr(value) for value in target_only_gaps
            ],
        },
    }


def run_grid(grid: Sequence[Q]) -> dict[str, Any]:
    sample_rows = []
    population_rows = []
    experiments = 0
    for values in product(grid, repeat=6):
        current = experiment_from_flat(values)
        experiments += 1
        sample_rows.append(
            (
                connected_components(sampled_support_sets(current)),
                risk_profile(current, minimax_sample_risk),
                current,
            )
        )
        population_rows.append(
            (
                connected_components(
                    population_observation_sets(current)
                ),
                risk_profile(current, population_risk),
                current,
            )
        )
    return {
        "grid": [qstr(value) for value in grid],
        "experiments": experiments,
        "decisions": {
            name: list(decision) for name, decision in DECISIONS.items()
        },
        "sampled_transcript_oracle": quotient_summary(sample_rows),
        "population_law_oracle": quotient_summary(population_rows),
        "anchors": anchor_checks(),
    }


def run() -> dict[str, Any]:
    return {
        "schema_version": (
            "asmp9_stochastic_experiment_development_result_v0_37"
        ),
        "status": "development_not_claim_eligible",
        **run_grid(GRID),
        "claim_boundary": (
            "Burned liveness census for instrument design. Classical "
            "Blackwell/Le Cam and zero-error facts are not novelty claims. "
            "No v0.37 protocol was registered before this run."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run()
    data = (
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    output = args.output.resolve()
    if output.exists() and output.read_bytes() != data:
        raise FileExistsError(f"refusing unequal development result: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        output.write_bytes(data)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
