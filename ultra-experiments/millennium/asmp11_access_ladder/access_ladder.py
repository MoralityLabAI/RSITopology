"""Finite Boolean access-ladder instrument for ASMP-11.

The construction is deliberately transparent and exact.  It validates a
resource-indexed detector interface; it is not a cryptographic backdoor.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb


N_VARIABLES = 6
K_GRID = (2, 3, 4, 5, 6)
RESOURCE_GRID = tuple(range(N_VARIABLES + 1))


@dataclass(frozen=True)
class Mechanism:
    support: tuple[int, ...]
    sign: int

    @property
    def degree(self) -> int:
        return len(self.support)


@dataclass(frozen=True)
class AccessCell:
    degree: int
    observation_order: int
    intervention_budget: int
    detector_advantage: Fraction
    signature_nonzero_fraction: Fraction
    query_upper_bound: int
    threshold_predicted: bool


def mechanisms(degree: int) -> tuple[Mechanism, ...]:
    if degree not in K_GRID:
        raise ValueError("degree is outside the registered grid")
    return tuple(
        Mechanism(tuple(support), sign)
        for support in combinations(range(N_VARIABLES), degree)
        for sign in (-1, 1)
    )


def benign_action(mechanism: Mechanism, bits: tuple[int, ...]) -> int:
    """Both paired models emit the same benign action."""

    if len(bits) != N_VARIABLES:
        raise ValueError("wrong input dimension")
    return 0


def defect_action(mechanism: Mechanism, bits: tuple[int, ...], deployment_flag: int) -> int:
    if deployment_flag == 0:
        return 0
    value = mechanism.sign
    for index in mechanism.support:
        value *= bits[index]
    return value


def matched_unlabelled_coefficient_spectrum(mechanism: Mechanism) -> tuple[int, ...]:
    """Clean stores the parity in a dormant channel; defect routes it to action.

    Forgetting output-channel labels gives the same coefficient magnitudes.
    """

    return (0, abs(mechanism.sign))


def nonzero_signature_entries(
    mechanism: Mechanism, observation_order: int, intervention_budget: int
) -> frozenset[tuple[tuple[int, ...], tuple[int, ...]]]:
    r"""Return nonzero restricted-Walsh coordinates, suppressing amplitudes.

    An intervention fixes a subset I of coordinates.  The parity retains
    support T\I and is visible to an order-r observer iff |T\I| <= r.
    Assignments only affect sign, not visibility, so the signature keys record
    the intervention set and remaining Fourier support.
    """

    if observation_order not in RESOURCE_GRID or intervention_budget not in RESOURCE_GRID:
        raise ValueError("resource outside registered grid")
    support = frozenset(mechanism.support)
    entries: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    for size in range(min(intervention_budget, N_VARIABLES) + 1):
        for intervention in combinations(range(N_VARIABLES), size):
            remainder = tuple(sorted(support.difference(intervention)))
            if len(remainder) <= observation_order:
                entries.add((tuple(intervention), remainder))
    return frozenset(entries)


def detector_advantage(degree: int, observation_order: int, intervention_budget: int) -> Fraction:
    """TV advantage between the clean and planted observation laws.

    The clean signature is empty.  The planted ensemble is uniform over
    supports and signs.  Advantage is therefore the planted mass with a
    nonempty signature.
    """

    ensemble = mechanisms(degree)
    visible = sum(
        bool(nonzero_signature_entries(item, observation_order, intervention_budget))
        for item in ensemble
    )
    return Fraction(visible, len(ensemble))


def query_upper_bound(observation_order: int, intervention_budget: int) -> int:
    """Registered exhaustive-query count for the access class.

    Each fixed coordinate has two assignments.  For every restriction the
    observer requests all Fourier coordinates through the registered order.
    """

    total = 0
    for fixed in range(intervention_budget + 1):
        remaining = N_VARIABLES - fixed
        coefficient_count = sum(comb(remaining, order) for order in range(min(observation_order, remaining) + 1))
        total += comb(N_VARIABLES, fixed) * (2**fixed) * coefficient_count
    return total


def census() -> tuple[AccessCell, ...]:
    rows: list[AccessCell] = []
    for degree in K_GRID:
        for observation_order in RESOURCE_GRID:
            for intervention_budget in RESOURCE_GRID:
                advantage = detector_advantage(degree, observation_order, intervention_budget)
                rows.append(
                    AccessCell(
                        degree=degree,
                        observation_order=observation_order,
                        intervention_budget=intervention_budget,
                        detector_advantage=advantage,
                        signature_nonzero_fraction=advantage,
                        query_upper_bound=query_upper_bound(observation_order, intervention_budget),
                        threshold_predicted=observation_order + intervention_budget >= degree,
                    )
                )
    return tuple(rows)


def simulator_contains(
    mechanism: Mechanism,
    weak_order: int,
    weak_interventions: int,
    strong_order: int,
    strong_interventions: int,
) -> bool:
    if strong_order < weak_order or strong_interventions < weak_interventions:
        raise ValueError("strong access must dominate weak access coordinatewise")
    weak = nonzero_signature_entries(mechanism, weak_order, weak_interventions)
    strong = nonzero_signature_entries(mechanism, strong_order, strong_interventions)
    return weak.issubset(strong)
