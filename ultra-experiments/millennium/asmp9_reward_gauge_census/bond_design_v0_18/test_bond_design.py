from __future__ import annotations

from fractions import Fraction

import pytest

from bond_design import (
    bridge_indices,
    cactus_closed_form,
    cyclic_core_bonds,
)


def test_cycle_bonds_are_all_edge_pairs() -> None:
    edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    assert cyclic_core_bonds(4, edges) == (
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    )


def test_original_bridge_is_excluded() -> None:
    edges = ((0, 1), (1, 2), (2, 0), (0, 3))
    assert bridge_indices(4, edges) == (3,)
    assert cyclic_core_bonds(4, edges) == (
        (0, 1),
        (0, 2),
        (1, 2),
    )


def test_bowtie_bonds_are_cycle_local() -> None:
    edges = (
        (0, 1),
        (1, 2),
        (2, 0),
        (0, 3),
        (3, 4),
        (4, 0),
    )
    assert cyclic_core_bonds(5, edges) == (
        (0, 1),
        (0, 2),
        (1, 2),
        (3, 4),
        (3, 5),
        (4, 5),
    )


def test_cactus_closed_form_with_bridge() -> None:
    edges = (
        (0, 1),
        (1, 2),
        (2, 0),
        (3, 4),
        (4, 5),
        (5, 6),
        (6, 3),
        (2, 3),
    )
    result = cactus_closed_form(7, edges)
    assert result["threshold"] == Fraction(2, 7)
    assert result["weights"] == (Fraction(1, 7),) * 7 + (
        Fraction(0),
    )


def test_theta_is_rejected_as_cactus() -> None:
    edges = (
        (0, 1),
        (0, 2),
        (2, 1),
        (0, 3),
        (3, 1),
    )
    with pytest.raises(ValueError, match="do not form a cactus"):
        cactus_closed_form(4, edges)
