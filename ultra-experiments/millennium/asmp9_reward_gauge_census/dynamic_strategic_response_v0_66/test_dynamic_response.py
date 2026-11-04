from itertools import combinations, product

import pytest

from dynamic_response import (
    Transducer,
    branch_map,
    classify,
    identifies_and_restores,
    identifies_initial_state,
    identity_distortion,
    initial_belief,
    make_transducer,
    maximum_identifiable_subset,
    minimum_worst_disturbance,
    pairwise_but_not_global_fixture,
    read_only_fixture,
    read_then_reset_fixture,
    reset_then_read_fixture,
    reversible_flip_fixture,
    solve_with_budget,
    transition_is_permutation,
)


def binary_transducers():
    for output_flat in product(range(2), repeat=4):
        outputs = (
            output_flat[:2],
            output_flat[2:],
        )
        for transition_flat in product(range(2), repeat=4):
            transitions = (
                transition_flat[:2],
                transition_flat[2:],
            )
            yield make_transducer(outputs, transitions)


def brute_wins(machine, distortion, budget, start, depth):
    if len(start) == 1:
        initial, current = start[0]
        if distortion[initial][current] <= budget:
            return True
    if depth == 0:
        return False
    currents = [current for _, current in start]
    if len(set(currents)) != len(currents):
        return False
    return any(
        all(
            brute_wins(
                machine,
                distortion,
                budget,
                branch,
                depth - 1,
            )
            for branch in branch_map(machine, start, query).values()
        )
        for query in range(machine.query_count)
    )


def test_read_only_query_identifies_without_altering():
    machine = read_only_fixture(4)
    ordinary = identifies_initial_state(machine)
    safe = identifies_and_restores(machine)
    assert ordinary.winning and ordinary.minimum_depth == 1
    assert safe.winning and safe.minimum_depth == 1
    assert classify(machine) == "identify_and_restore"


def test_read_then_reset_identifies_but_does_not_preserve():
    machine = read_then_reset_fixture(4)
    ordinary = identifies_initial_state(machine)
    safe = identifies_and_restores(machine)
    assert ordinary.winning and ordinary.minimum_depth == 1
    assert not safe.winning
    assert classify(machine) == "identify_only_altering"
    budget, result = minimum_worst_disturbance(
        machine,
        identity_distortion(machine),
    )
    assert budget == 1
    assert result is not None and result.winning


def test_reset_then_read_constructs_consensus_without_identifying():
    machine = reset_then_read_fixture(4)
    assert not identifies_initial_state(machine).winning
    assert maximum_identifiable_subset(machine) == 1
    assert classify(machine) == "unidentifiable"


def test_reversible_probe_can_identify_then_restore():
    machine = reversible_flip_fixture()
    ordinary = identifies_initial_state(machine)
    safe = identifies_and_restores(machine)
    assert ordinary.winning and ordinary.minimum_depth == 1
    assert safe.winning and safe.minimum_depth == 2
    assert transition_is_permutation(machine, 0)


def test_pairwise_distinguishability_does_not_imply_global_experiment():
    machine = pairwise_but_not_global_fixture()
    for pair in combinations(range(3), 2):
        assert identifies_initial_state(machine, pair).winning
    assert not identifies_initial_state(machine).winning
    assert maximum_identifiable_subset(machine) == 2


def test_fixed_point_matches_bounded_tree_search_on_every_binary_machine():
    checked = 0
    for machine in binary_transducers():
        start = initial_belief(2)
        for distortion, budget in (
            (((0, 0), (0, 0)), 0),
            (((0, 1), (1, 0)), 0),
        ):
            exact = solve_with_budget(machine, distortion, budget)
            brute = brute_wins(
                machine,
                distortion,
                budget,
                start,
                depth=exact.reachable_belief_count,
            )
            assert exact.winning == brute
        checked += 1
    assert checked == 256


def test_safe_identification_implies_ordinary_identification_exhaustively():
    for machine in binary_transducers():
        if identifies_and_restores(machine).winning:
            assert identifies_initial_state(machine).winning


def test_inverse_closed_permutation_queries_restore_after_identification():
    checked = 0
    for machine in binary_transducers():
        if all(
            transition_is_permutation(machine, query)
            for query in range(machine.query_count)
        ):
            assert (
                identifies_initial_state(machine).winning
                == identifies_and_restores(machine).winning
            )
            checked += 1
    assert checked == 64


def test_distortion_frontier_uses_declared_terminal_loss():
    machine = read_then_reset_fixture(3)
    distortion = (
        (0, 2, 4),
        (3, 0, 2),
        (7, 5, 0),
    )
    budget, result = minimum_worst_disturbance(machine, distortion)
    assert budget == 7
    assert result is not None and result.minimum_depth == 1


def test_invalid_objects_fail_closed():
    with pytest.raises(ValueError):
        Transducer(outputs=((0,),), transitions=((0,),))
    with pytest.raises(ValueError):
        make_transducer(((0,), (1,)), ((0,), (2,)))
    with pytest.raises(ValueError):
        initial_belief(2, ())
    with pytest.raises(ValueError):
        initial_belief(2, (0, 0))
    with pytest.raises(ValueError):
        solve_with_budget(read_only_fixture(), ((0,),), 0)
    with pytest.raises(ValueError):
        solve_with_budget(
            read_only_fixture(),
            identity_distortion(read_only_fixture()),
            -1,
        )
