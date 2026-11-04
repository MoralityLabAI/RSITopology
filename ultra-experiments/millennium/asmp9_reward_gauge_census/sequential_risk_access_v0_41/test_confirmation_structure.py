from fractions import Fraction as Q

from confirmation import (
    CONFIRMATION_QUERIES,
    ERROR_RATES,
    ROOT_GROUP,
    SIGNATURES,
)


def test_confirmation_channel_universe_is_disjoint_and_exact():
    assert tuple(query.name for query in CONFIRMATION_QUERIES) == (
        "root_q",
        "left_q",
        "right_q",
    )
    assert ERROR_RATES == {
        "root_q": Q(1, 5),
        "left_q": Q(1, 4),
        "right_q": Q(1, 3),
    }
    assert SIGNATURES["root_q"] == (0, 0, 1, 1)


def test_confirmation_group_loss_is_asymmetric():
    assert ROOT_GROUP.losses[0] == (Q(0), Q(1, 3))
    assert ROOT_GROUP.losses[2] == (Q(2, 3), Q(0))
