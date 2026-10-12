"""Target recovery versus representative-insensitive encoding for ASMP-9."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Sequence


Labels = tuple[Hashable, ...]


@dataclass(frozen=True)
class TargetInterfaceDiagnostic:
    status: str
    target_recoverable: bool
    representative_insensitive: bool
    exact_partition_match: bool
    underidentification_witnesses: tuple[tuple[int, int], ...]
    representative_leakage_witnesses: tuple[tuple[int, int], ...]
    target_decoder: tuple[tuple[Hashable, Hashable], ...] | None
    representative_insensitive_encoder: (
        tuple[tuple[Hashable, Hashable], ...] | None
    )


def classify_target_interface(
    target: Labels,
    observation: Labels,
) -> TargetInterfaceDiagnostic:
    if not target or len(target) != len(observation):
        raise ValueError("target and observation must have equal positive size")

    underidentified = []
    leakage = []
    for left, right in combinations(range(len(target)), 2):
        same_target = target[left] == target[right]
        same_observation = observation[left] == observation[right]
        if same_observation and not same_target:
            underidentified.append((left, right))
        if same_target and not same_observation:
            leakage.append((left, right))

    recoverable = not underidentified
    insensitive = not leakage
    if recoverable and insensitive:
        status = "exact_target_interface"
    elif recoverable:
        status = "recoverable_with_representative_leakage"
    elif insensitive:
        status = "underidentified"
    else:
        status = "cross_cut_misspecified_interface"

    decoder = None
    if recoverable:
        decoder_map: dict[Hashable, Hashable] = {}
        for observed, target_value in zip(observation, target):
            decoder_map[observed] = target_value
        decoder = tuple(sorted(decoder_map.items(), key=repr))

    encoder = None
    if insensitive:
        encoder_map: dict[Hashable, Hashable] = {}
        for target_value, observed in zip(target, observation):
            encoder_map[target_value] = observed
        encoder = tuple(sorted(encoder_map.items(), key=repr))

    return TargetInterfaceDiagnostic(
        status=status,
        target_recoverable=recoverable,
        representative_insensitive=insensitive,
        exact_partition_match=recoverable and insensitive,
        underidentification_witnesses=tuple(underidentified),
        representative_leakage_witnesses=tuple(leakage),
        target_decoder=decoder,
        representative_insensitive_encoder=encoder,
    )
