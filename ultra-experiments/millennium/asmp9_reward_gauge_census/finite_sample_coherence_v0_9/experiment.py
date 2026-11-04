"""Reusable synthetic cells for the ASMP-9 v0.9 certificate."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Any

import numpy as np

from finite_sample_coherence import (
    Edge,
    certify_coherence,
    circulations,
    expit,
    fundamental_cycle_basis,
    hoeffding_probability_radius,
    sample_binomial_counts,
    simultaneous_event_holds,
    sufficient_samples_per_edge,
)


def cycle_graph(length: int) -> tuple[int, tuple[Edge, ...]]:
    if length < 3:
        raise ValueError("cycle length must be at least three")
    edges = tuple((index, index + 1) for index in range(length - 1))
    return length, edges + ((0, length - 1),)


def named_graphs() -> dict[str, tuple[int, tuple[Edge, ...]]]:
    return {
        "cycle_3": cycle_graph(3),
        "cycle_4": cycle_graph(4),
        "cycle_6": cycle_graph(6),
        "cycle_8": cycle_graph(8),
        "theta_4": (
            4,
            ((0, 1), (1, 3), (0, 2), (2, 3), (0, 3)),
        ),
        "complete_5": (
            5,
            tuple(
                (left, right)
                for left in range(5)
                for right in range(left + 1, 5)
            ),
        ),
    }


def graph_metadata(
    vertex_count: int, edges: tuple[Edge, ...]
) -> dict[str, Any]:
    basis = fundamental_cycle_basis(vertex_count, edges)
    lengths = tuple(sum(abs(value) for value in row) for row in basis)
    chord_indices = tuple(
        max(index for index, value in enumerate(row) if value)
        for row in basis
    )
    return {
        "vertex_count": vertex_count,
        "edges": [list(edge) for edge in edges],
        "edge_count": len(edges),
        "beta_1": len(basis),
        "cycle_lengths": list(lengths),
        "maximum_cycle_length": max(lengths, default=0),
        "chord_indices": list(chord_indices),
    }


def _status_counts(certificates) -> dict[str, int]:
    return dict(sorted(Counter(item.status for item in certificates).items()))


def run_graph_cells(
    *,
    graph_name: str,
    vertex_count: int,
    edges: tuple[Edge, ...],
    seed: int,
    replicates: int,
    multipliers: tuple[float, ...],
    alpha: float,
    probability_floor: float,
    coherent_tolerance: float,
    incoherent_margin: float,
    planted_circulation: float,
) -> dict[str, Any]:
    basis = fundamental_cycle_basis(vertex_count, edges)
    if not basis:
        raise ValueError("experiment graphs must contain a cycle")
    metadata = graph_metadata(vertex_count, edges)
    planted_index = metadata["chord_indices"][0]
    coherent_probabilities = tuple(0.5 for _ in edges)
    positive_probabilities = tuple(
        expit(planted_circulation if index == planted_index else 0.0)
        for index in range(len(edges))
    )
    negative_probabilities = tuple(
        1.0 - probability for probability in positive_probabilities
    )
    true_positive_logits = tuple(
        planted_circulation if index == planted_index else 0.0
        for index in range(len(edges))
    )
    true_negative_logits = tuple(-value for value in true_positive_logits)
    true_positive_cycles = circulations(basis, true_positive_logits)
    true_negative_cycles = circulations(basis, true_negative_logits)
    if max(map(abs, true_positive_cycles)) != planted_circulation:
        raise AssertionError("planted chord did not create requested circulation")

    interior_margin = min(
        min(
            probability - probability_floor,
            1.0 - probability_floor - probability,
        )
        for probability in positive_probabilities
    )
    bound = sufficient_samples_per_edge(
        len(edges),
        metadata["maximum_cycle_length"],
        alpha=alpha,
        probability_floor=probability_floor,
        probability_interior_margin=interior_margin,
        coherent_tolerance=coherent_tolerance,
        planted_circulation=planted_circulation,
        incoherent_margin=incoherent_margin,
    )
    cells: list[dict[str, Any]] = []
    for multiplier_index, multiplier in enumerate(multipliers):
        samples_per_edge = max(1, round(bound * multiplier))
        rng = np.random.default_rng(
            np.random.SeedSequence([seed, multiplier_index])
        )
        coherent_certificates = []
        positive_certificates = []
        negative_certificates = []
        event_failures = Counter()
        unsafe_on_event = Counter()
        for _ in range(replicates):
            coherent_counts = sample_binomial_counts(
                coherent_probabilities, samples_per_edge, rng
            )
            positive_counts = sample_binomial_counts(
                positive_probabilities, samples_per_edge, rng
            )
            negative_counts = tuple(
                samples_per_edge - value for value in positive_counts
            )
            arms = (
                ("coherent", coherent_counts, coherent_probabilities),
                ("positive", positive_counts, positive_probabilities),
                ("negative", negative_counts, negative_probabilities),
            )
            certificates = []
            for arm, counts, probabilities in arms:
                certificate = certify_coherence(
                    vertex_count,
                    edges,
                    counts,
                    samples_per_edge,
                    alpha=alpha,
                    probability_floor=probability_floor,
                    coherent_tolerance=coherent_tolerance,
                    incoherent_margin=incoherent_margin,
                )
                event = simultaneous_event_holds(
                    counts,
                    samples_per_edge,
                    probabilities,
                    hoeffding_probability_radius(
                        len(edges), samples_per_edge, alpha
                    ),
                )
                event_failures[arm] += int(not event)
                if event:
                    expected = (
                        "certified_coherent_within_tolerance"
                        if arm == "coherent"
                        else "certified_incoherent"
                    )
                    unsafe_on_event[arm] += int(
                        certificate.status
                        not in {
                            expected,
                            "inconclusive",
                            "unavailable_probability_floor",
                        }
                    )
                    if multiplier >= 1.0:
                        unsafe_on_event[f"{arm}_bound_miss"] += int(
                            certificate.status != expected
                        )
                certificates.append(certificate)
            coherent_certificates.append(certificates[0])
            positive_certificates.append(certificates[1])
            negative_certificates.append(certificates[2])

        cells.append(
            {
                "multiplier": multiplier,
                "samples_per_edge": samples_per_edge,
                "coherent_status_counts": _status_counts(
                    coherent_certificates
                ),
                "positive_status_counts": _status_counts(
                    positive_certificates
                ),
                "negative_status_counts": _status_counts(
                    negative_certificates
                ),
                "event_failure_counts": dict(sorted(event_failures.items())),
                "unsafe_on_event_counts": dict(sorted(unsafe_on_event.items())),
                "mirror_status_match": _status_counts(positive_certificates)
                == _status_counts(negative_certificates),
                "example_positive_band": (
                    asdict(positive_certificates[-1].cycle_bands[0])
                    if positive_certificates[-1].cycle_bands
                    else None
                ),
            }
        )
    return {
        "graph_name": graph_name,
        "metadata": metadata,
        "seed": seed,
        "replicates": replicates,
        "interior_margin": interior_margin,
        "sufficient_samples_per_edge": bound,
        "true_positive_circulations": list(true_positive_cycles),
        "true_negative_circulations": list(true_negative_cycles),
        "cells": cells,
    }


def run_forest_control(
    *,
    replicates: int,
    samples_per_edge: int,
    seed: int,
    alpha: float,
    probability_floor: float,
    coherent_tolerance: float,
    incoherent_margin: float,
) -> dict[str, Any]:
    vertex_count = 6
    edges = tuple((index, index + 1) for index in range(vertex_count - 1))
    probabilities = tuple(0.5 for _ in edges)
    rng = np.random.default_rng(seed)
    counts = Counter()
    for _ in range(replicates):
        observation = sample_binomial_counts(
            probabilities, samples_per_edge, rng
        )
        certificate = certify_coherence(
            vertex_count,
            edges,
            observation,
            samples_per_edge,
            alpha=alpha,
            probability_floor=probability_floor,
            coherent_tolerance=coherent_tolerance,
            incoherent_margin=incoherent_margin,
        )
        counts[certificate.status] += 1
    return {
        "replicates": replicates,
        "samples_per_edge": samples_per_edge,
        "status_counts": dict(sorted(counts.items())),
    }


def run_floor_control(
    *,
    replicates: int,
    samples_per_edge: int,
    seed: int,
    alpha: float,
    probability_floor: float,
    coherent_tolerance: float,
    incoherent_margin: float,
) -> dict[str, Any]:
    vertex_count, edges = cycle_graph(3)
    probabilities = (0.02, 0.5, 0.5)
    rng = np.random.default_rng(seed)
    counts = Counter()
    nonunavailable_on_event = 0
    event_failure_count = 0
    radius = hoeffding_probability_radius(
        len(edges), samples_per_edge, alpha
    )
    for _ in range(replicates):
        observation = sample_binomial_counts(
            probabilities, samples_per_edge, rng
        )
        certificate = certify_coherence(
            vertex_count,
            edges,
            observation,
            samples_per_edge,
            alpha=alpha,
            probability_floor=probability_floor,
            coherent_tolerance=coherent_tolerance,
            incoherent_margin=incoherent_margin,
        )
        event = simultaneous_event_holds(
            observation,
            samples_per_edge,
            probabilities,
            radius,
        )
        event_failure_count += int(not event)
        nonunavailable_on_event += int(
            event and certificate.status != "unavailable_probability_floor"
        )
        counts[certificate.status] += 1
    return {
        "replicates": replicates,
        "samples_per_edge": samples_per_edge,
        "status_counts": dict(sorted(counts.items())),
        "event_failure_count": event_failure_count,
        "nonunavailable_on_event": nonunavailable_on_event,
    }
