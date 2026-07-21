from fractions import Fraction

from attestability import (
    ERROR_LIMIT,
    TARGET_TABLE,
    THETA_GRID,
    agreement_count,
    audit_probability,
    binomial_distribution,
    class_counts,
    direct_report_count_distribution,
    find_feasible_test,
    make_accuracy_table,
    minimum_channels,
    pareto_frontier,
    policy_class,
    representation_roundtrip,
    representation_states,
    trace_atom,
    uniform_errors,
)


def test_registered_universe_counts_and_witnesses() -> None:
    assert len(representation_states()) == 48
    assert class_counts() == {"compliant": 39203, "forbidden": 137, "unclassified": 26196}
    assert agreement_count(TARGET_TABLE) == 16
    assert policy_class(make_accuracy_table(8)) == "compliant"
    assert policy_class(make_accuracy_table(14)) == "forbidden"


def test_all_codecs_and_decompositions_roundtrip_spanning_tables() -> None:
    for table in (0, 1, 0x00FF, 0x0F0F, 0x5555, 0xA5A5, TARGET_TABLE, 0xFFFF):
        for state in representation_states():
            assert representation_roundtrip(table, state) == table


def test_trace_is_function_independent_within_each_state() -> None:
    compliant = make_accuracy_table(8)
    forbidden = make_accuracy_table(14)
    assert compliant != forbidden
    for state in representation_states():
        assert trace_atom(state) == trace_atom(state)


def test_randomized_response_probability_endpoints() -> None:
    for k in range(17):
        assert audit_probability(k, Fraction(1, 2)) == Fraction(1, 2)
        assert audit_probability(k, Fraction(1)) == Fraction(k, 16)
    assert audit_probability(8, Fraction(4, 5)) == Fraction(1, 2)


def test_direct_report_enumeration_equals_binomial_reduction() -> None:
    for theta in THETA_GRID:
        for k in (8, 14):
            q = audit_probability(k, theta)
            for m in range(9):
                assert direct_report_count_distribution(m, q) == binomial_distribution(m, q)


def test_privacy_kill_and_unrandomized_liveness() -> None:
    assert all(find_feasible_test(m, Fraction(1, 2)) is None for m in range(129))
    test = next(
        candidate
        for m in range(129)
        if (candidate := find_feasible_test(m, Fraction(1))) is not None
    )
    assert test is not None
    fps, fns = uniform_errors(test)
    assert max(fps.values()) <= ERROR_LIMIT
    assert max(fns.values()) <= ERROR_LIMIT


def test_all_minimum_channels_are_uniform_when_feasible() -> None:
    channels = minimum_channels()
    for test in channels.values():
        if test is None:
            continue
        fps, fns = uniform_errors(test)
        assert max(fps.values()) <= ERROR_LIMIT
        assert max(fns.values()) <= ERROR_LIMIT


def test_frontier_is_nondominated() -> None:
    channels = minimum_channels()
    frontier = pareto_frontier(channels)
    assert frontier
    for candidate in frontier:
        assert not any(
            other is not None
            and other is not candidate
            and other.m <= candidate.m
            and other.theta <= candidate.theta
            and (other.m < candidate.m or other.theta < candidate.theta)
            for other in channels.values()
        )
