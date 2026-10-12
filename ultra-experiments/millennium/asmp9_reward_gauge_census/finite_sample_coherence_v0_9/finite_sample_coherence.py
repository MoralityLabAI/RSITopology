"""Finite-sample cycle-coherence certificates for ASMP-9 v0.9.

The module deliberately separates a simultaneous probability event from the
scientific decision. Failure to certify coherence is never converted into
evidence of incoherence, or vice versa.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import exp, log, sqrt
from typing import Iterable, Sequence


Edge = tuple[int, int]


@dataclass(frozen=True)
class CycleBand:
    chord_index: int
    coefficients: tuple[int, ...]
    estimate: float
    radius: float

    @property
    def lower(self) -> float:
        return self.estimate - self.radius

    @property
    def upper(self) -> float:
        return self.estimate + self.radius

    @property
    def length(self) -> int:
        return sum(abs(value) for value in self.coefficients)


@dataclass(frozen=True)
class CoherenceCertificate:
    status: str
    alpha: float
    probability_radius: float
    logit_radius: float
    cycle_bands: tuple[CycleBand, ...]
    reason: str


def _validate_graph(vertex_count: int, edges: Sequence[Edge]) -> None:
    if vertex_count < 1:
        raise ValueError("vertex_count must be positive")
    for source, target in edges:
        if not (0 <= source < vertex_count and 0 <= target < vertex_count):
            raise ValueError("edge endpoint outside vertex universe")


def spanning_forest_indices(
    vertex_count: int, edges: Sequence[Edge]
) -> tuple[int, ...]:
    """Return deterministic weak-spanning-forest edge indices."""
    _validate_graph(vertex_count, edges)
    parent = list(range(vertex_count))

    def find(vertex: int) -> int:
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    chosen: list[int] = []
    for index, (source, target) in enumerate(edges):
        left, right = find(source), find(target)
        if left == right:
            continue
        parent[right] = left
        chosen.append(index)
    return tuple(chosen)


def fundamental_cycle_basis(
    vertex_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    """Return signed edge coefficients for a deterministic fundamental basis.

    The row for a chord is its score minus the oriented score accumulated on
    the unique forest path from the chord source to its target.
    """
    _validate_graph(vertex_count, edges)
    forest = set(spanning_forest_indices(vertex_count, edges))
    adjacency: list[list[tuple[int, int, int]]] = [
        [] for _ in range(vertex_count)
    ]
    for index in sorted(forest):
        source, target = edges[index]
        adjacency[source].append((target, index, 1))
        adjacency[target].append((source, index, -1))

    rows: list[tuple[int, ...]] = []
    for chord_index, (source, target) in enumerate(edges):
        if chord_index in forest:
            continue
        coefficients = [0] * len(edges)
        coefficients[chord_index] = 1
        if source == target:
            rows.append(tuple(coefficients))
            continue

        queue = deque([source])
        previous: dict[int, tuple[int, int, int] | None] = {source: None}
        while queue and target not in previous:
            vertex = queue.popleft()
            for neighbor, edge_index, direction in adjacency[vertex]:
                if neighbor in previous:
                    continue
                previous[neighbor] = (vertex, edge_index, direction)
                queue.append(neighbor)
        if target not in previous:
            # A chord cannot join different forest components, so this signals
            # an implementation or input inconsistency.
            raise ValueError("chord endpoints are disconnected in forest")

        cursor = target
        path: list[tuple[int, int]] = []
        while cursor != source:
            step = previous[cursor]
            if step is None:
                raise AssertionError("broken forest predecessor chain")
            parent, edge_index, direction = step
            path.append((edge_index, direction))
            cursor = parent
        for edge_index, direction in reversed(path):
            coefficients[edge_index] -= direction
        rows.append(tuple(coefficients))
    return tuple(rows)


def circulations(
    cycle_basis: Sequence[Sequence[int]], edge_scores: Sequence[float]
) -> tuple[float, ...]:
    return tuple(
        sum(float(coefficient) * float(score) for coefficient, score in zip(row, edge_scores))
        for row in cycle_basis
    )


def expit(value: float) -> float:
    if value >= 0:
        tail = exp(-value)
        return 1.0 / (1.0 + tail)
    head = exp(value)
    return head / (1.0 + head)


def logit(probability: float) -> float:
    if not 0.0 < probability < 1.0:
        raise ValueError("logit requires a probability strictly between zero and one")
    return log(probability / (1.0 - probability))


def hoeffding_probability_radius(
    edge_count: int, samples_per_edge: int, alpha: float
) -> float:
    """Bonferroni-uniform two-sided Hoeffding radius over all edges."""
    if edge_count < 1:
        raise ValueError("edge_count must be positive")
    if samples_per_edge < 1:
        raise ValueError("samples_per_edge must be positive")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    return sqrt(log(2.0 * edge_count / alpha) / (2.0 * samples_per_edge))


def simultaneous_event_holds(
    counts: Sequence[int],
    samples_per_edge: int,
    true_probabilities: Sequence[float],
    probability_radius: float,
) -> bool:
    if len(counts) != len(true_probabilities):
        raise ValueError("counts and probabilities must have equal length")
    return all(
        abs(count / samples_per_edge - probability) <= probability_radius
        for count, probability in zip(counts, true_probabilities)
    )


def certify_coherence(
    vertex_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
    samples_per_edge: int,
    *,
    alpha: float,
    probability_floor: float,
    coherent_tolerance: float,
    incoherent_margin: float,
) -> CoherenceCertificate:
    """Return a three-way finite-sample coherence certificate.

    Admission requires every simultaneous probability interval to lie inside
    ``[probability_floor, 1-probability_floor]``. On the simultaneous
    Hoeffding event, the logit Lipschitz constant is therefore bounded by
    ``1/(floor*(1-floor))``.
    """
    _validate_graph(vertex_count, edges)
    if len(edges) != len(counts):
        raise ValueError("one binomial count is required per edge")
    if not edges:
        return CoherenceCertificate(
            status="unavailable_no_edges",
            alpha=alpha,
            probability_radius=float("inf"),
            logit_radius=float("inf"),
            cycle_bands=(),
            reason="no comparison edges",
        )
    if any(count < 0 or count > samples_per_edge for count in counts):
        raise ValueError("count outside binomial support")
    if not 0.0 < probability_floor < 0.5:
        raise ValueError("probability_floor must lie in (0,1/2)")
    if not 0.0 <= coherent_tolerance < incoherent_margin:
        raise ValueError("require 0 <= coherent_tolerance < incoherent_margin")

    basis = fundamental_cycle_basis(vertex_count, edges)
    if not basis:
        return CoherenceCertificate(
            status="unavailable_no_cycles",
            alpha=alpha,
            probability_radius=hoeffding_probability_radius(
                len(edges), samples_per_edge, alpha
            ),
            logit_radius=float("inf"),
            cycle_bands=(),
            reason="comparison graph has beta_1=0",
        )

    probability_radius = hoeffding_probability_radius(
        len(edges), samples_per_edge, alpha
    )
    proportions = tuple(count / samples_per_edge for count in counts)
    if any(
        estimate - probability_radius < probability_floor
        or estimate + probability_radius > 1.0 - probability_floor
        for estimate in proportions
    ):
        return CoherenceCertificate(
            status="unavailable_probability_floor",
            alpha=alpha,
            probability_radius=probability_radius,
            logit_radius=float("inf"),
            cycle_bands=(),
            reason="simultaneous probability band leaves the registered interior",
        )

    edge_logit_radius = probability_radius / (
        probability_floor * (1.0 - probability_floor)
    )
    estimates = tuple(logit(value) for value in proportions)
    bands = tuple(
        CycleBand(
            chord_index=next(
                index
                for index, coefficient in enumerate(row)
                if coefficient and index not in spanning_forest_indices(vertex_count, edges)
            ),
            coefficients=tuple(row),
            estimate=sum(
                coefficient * estimate
                for coefficient, estimate in zip(row, estimates)
            ),
            radius=sum(abs(coefficient) for coefficient in row)
            * edge_logit_radius,
        )
        for row in basis
    )

    if all(
        max(abs(band.lower), abs(band.upper)) <= coherent_tolerance
        for band in bands
    ):
        return CoherenceCertificate(
            status="certified_coherent_within_tolerance",
            alpha=alpha,
            probability_radius=probability_radius,
            logit_radius=edge_logit_radius,
            cycle_bands=bands,
            reason="every simultaneous cycle band lies inside coherent tolerance",
        )

    if any(
        band.lower >= incoherent_margin or band.upper <= -incoherent_margin
        for band in bands
    ):
        return CoherenceCertificate(
            status="certified_incoherent",
            alpha=alpha,
            probability_radius=probability_radius,
            logit_radius=edge_logit_radius,
            cycle_bands=bands,
            reason="a simultaneous cycle band clears the incoherence margin",
        )

    return CoherenceCertificate(
        status="inconclusive",
        alpha=alpha,
        probability_radius=probability_radius,
        logit_radius=edge_logit_radius,
        cycle_bands=bands,
        reason="simultaneous bands certify neither registered region",
    )


def sufficient_samples_per_edge(
    edge_count: int,
    maximum_cycle_length: int,
    *,
    alpha: float,
    probability_floor: float,
    probability_interior_margin: float,
    coherent_tolerance: float,
    planted_circulation: float,
    incoherent_margin: float,
) -> int:
    """Return a conservative integer sample bound for both planted poles.

    On the simultaneous event, exact coherence is certified if twice the
    maximum cycle radius clears ``coherent_tolerance``. A planted cycle of
    magnitude ``planted_circulation`` is certified incoherent if its magnitude
    minus twice its radius clears ``incoherent_margin``.
    """
    if maximum_cycle_length < 1:
        raise ValueError("maximum_cycle_length must be positive")
    if probability_interior_margin <= 0.0:
        raise ValueError("probability_interior_margin must be positive")
    coherent_budget = coherent_tolerance
    alternative_budget = planted_circulation - incoherent_margin
    if coherent_budget <= 0.0 or alternative_budget <= 0.0:
        raise ValueError("registered margins leave no positive error budget")
    allowed_cycle_radius = min(coherent_budget, alternative_budget) / 2.0
    cycle_probability_radius = (
        allowed_cycle_radius
        * probability_floor
        * (1.0 - probability_floor)
        / maximum_cycle_length
    )
    # If every true probability is this far inside the registered boundary,
    # 2*delta <= margin guarantees data-dependent admission on the
    # simultaneous event.
    allowed_probability_radius = min(
        cycle_probability_radius,
        probability_interior_margin / 2.0,
    )
    return max(
        1,
        int(
            (
                log(2.0 * edge_count / alpha)
                / (2.0 * allowed_probability_radius**2)
            )
            // 1
        )
        + 1,
    )


def sample_binomial_counts(
    probabilities: Sequence[float],
    samples_per_edge: int,
    rng,
) -> tuple[int, ...]:
    """Sample independent edge counts from an object exposing ``binomial``."""
    return tuple(
        int(rng.binomial(samples_per_edge, probability))
        for probability in probabilities
    )


def gradient_logits(
    utilities: Sequence[float], edges: Iterable[Edge]
) -> tuple[float, ...]:
    return tuple(
        float(utilities[target]) - float(utilities[source])
        for source, target in edges
    )
