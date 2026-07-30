from __future__ import annotations

from fiber_group import (
    diagnose_access,
    full_fiber_group_size,
    generated_group,
    minimum_exact_query_family,
    orbit_partition,
)


def test_observation_fibers_are_orbits_of_full_fiber_group() -> None:
    observation = ("a", "a", "a", "b", "b")
    assert full_fiber_group_size(observation) == 12


def test_group_equality_is_not_required_for_orbit_equality() -> None:
    cyclic_three = ((1, 2, 0),)
    assert len(generated_group(3, cyclic_three)) == 3
    assert orbit_partition(3, cyclic_three) == ((0, 1, 2),)
    assert full_fiber_group_size(("same", "same", "same")) == 6
    diagnostic = diagnose_access([("same", "same", "same")], cyclic_three)
    assert diagnostic.status == "exact_quotient_identification"


def test_underidentification_emits_non_gauge_witnesses() -> None:
    swap_within_pairs = ((1, 0, 2, 3), (0, 1, 3, 2))
    diagnostic = diagnose_access(
        [("same", "same", "same", "same")],
        swap_within_pairs,
    )
    assert diagnostic.status == "underidentified"
    assert diagnostic.unseparated_non_gauge_pairs == (
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
    )


def test_query_that_splits_gauge_is_rejected() -> None:
    swap_first_pair = ((1, 0, 2),)
    diagnostic = diagnose_access([("left", "right", "other")], swap_first_pair)
    assert diagnostic.status == "overdiscriminates_licensed_gauge"
    assert diagnostic.gauge_split_witnesses == ((0, 1),)


def test_exact_access_matches_orbit_partition() -> None:
    swap_within_pairs = ((1, 0, 2, 3), (0, 1, 3, 2))
    diagnostic = diagnose_access(
        [("first", "first", "second", "second")],
        swap_within_pairs,
    )
    assert diagnostic.status == "exact_quotient_identification"
    assert diagnostic.observation_fibers == diagnostic.gauge_orbits


def test_minimum_query_family_is_exact_set_cover() -> None:
    identity_gauge: tuple[tuple[int, ...], ...] = tuple()
    candidates = (
        (0, 0, 1, 1),
        (0, 1, 0, 1),
        (0, 0, 0, 0),
    )
    assert minimum_exact_query_family(candidates, identity_gauge) == (0, 1)


def test_no_candidate_family_can_repair_a_gauge_splitting_registry() -> None:
    swaps_within_pairs = ((1, 0, 2, 3), (0, 1, 3, 2))
    splitting_candidates = ((0, 1, 0, 1), (1, 0, 1, 0))
    assert (
        minimum_exact_query_family(splitting_candidates, swaps_within_pairs)
        is None
    )
