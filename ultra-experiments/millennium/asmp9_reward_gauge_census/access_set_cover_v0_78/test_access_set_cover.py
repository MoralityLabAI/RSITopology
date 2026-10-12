from __future__ import annotations

import random

from access_set_cover import (
    build_access_instance,
    minimum_access_family,
    minimum_set_cover,
    query_family_separates,
)


UNIVERSE = (0, 1, 2, 3)
SETS = ({0, 1}, {2, 3}, {0, 2}, {1, 3})


def test_frozen_cover_optimum_is_two() -> None:
    assert minimum_set_cover(UNIVERSE, SETS) == (0, 1)


def test_frozen_access_optimum_is_anchor_plus_cover() -> None:
    instance = build_access_instance(UNIVERSE, SETS)
    assert minimum_access_family(instance) == (0, 1, 2)
    assert query_family_separates(
        instance.target_labels,
        instance.queries,
        (0, 1, 2),
    )


def test_anchor_query_is_mandatory() -> None:
    instance = build_access_instance(UNIVERSE, SETS)
    all_non_anchor = tuple(range(1, len(instance.queries)))
    assert not query_family_separates(
        instance.target_labels,
        instance.queries,
        all_non_anchor,
    )


def test_uncovered_element_makes_both_instances_infeasible() -> None:
    sets = ({0}, {1})
    assert minimum_set_cover((0, 1, 2), sets) is None
    instance = build_access_instance((0, 1, 2), sets)
    assert minimum_access_family(instance) is None


def test_optimum_shift_holds_on_seeded_small_registry() -> None:
    generator = random.Random(7801)
    checked = 0
    for _ in range(48):
        universe = tuple(range(5))
        sets = []
        for _query in range(6):
            sets.append(
                {
                    element
                    for element in universe
                    if generator.random() < 0.45
                }
            )
        cover = minimum_set_cover(universe, sets)
        access = minimum_access_family(build_access_instance(universe, sets))
        if cover is None:
            assert access is None
        else:
            assert access is not None
            assert access[0] == 0
            assert len(access) == len(cover) + 1
        checked += 1
    assert checked == 48


def test_outside_cover_element_is_rejected() -> None:
    try:
        build_access_instance((0, 1), ({0, 2},))
    except ValueError as error:
        assert "outside universe" in str(error)
    else:
        raise AssertionError("invalid cover was accepted")
