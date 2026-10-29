from fractions import Fraction as Q

from aggregate_randomized import (
    exact_randomized_optimum,
    one_outcome_strict_gain,
    subset_bound_table,
    two_experiment_witness,
)


def test_one_outcome_randomization_strictly_improves():
    control = one_outcome_strict_gain(Q(1, 2))
    assert control["deterministic_value"] == Q(1)
    assert control["randomized_value"] == Q(1, 2)
    assert control["optimizer"] == ((Q(1, 2), Q(1, 2)),)


def test_same_subset_table_different_randomized_values():
    witness = two_experiment_witness()
    first, second = witness["experiments"]
    assert first["subset_table"] == second["subset_table"]
    assert first["subset_table"] == (Q(0), Q(1), Q(0), Q(1))
    assert first["deterministic_value"] == Q(1, 2)
    assert second["deterministic_value"] == Q(1, 2)
    assert first["randomized_value"] == Q(5, 12)
    assert second["randomized_value"] == Q(5, 18)
    assert first["randomized_value"] != second["randomized_value"]


def test_witness_has_matching_exact_dual_certificates():
    witness = two_experiment_witness()
    for experiment in witness["experiments"]:
        assert experiment["dual_feasible"]
        assert (
            experiment["dual_value"]
            == experiment["randomized_value"]
        )


def test_subset_table_uses_strict_alpha():
    assert subset_bound_table(
        (Q(1),),
        ((Q(1, 2), Q(1, 2)),),
        Q(1, 2),
    ) == (Q(0), Q(0), Q(0), Q(1))


def test_exact_solver_handles_two_constraints():
    optimum = exact_randomized_optimum(
        (Q(1), Q(1)),
        (
            (Q(3, 4), Q(1, 4)),
            (Q(1, 4), Q(3, 4)),
        ),
        (Q(0), Q(1)),
        Q(1, 4),
        (Q(1, 2), Q(1, 2)),
    )
    assert optimum.value == Q(3, 4)
    assert sum(value > 0 for row in optimum.optimizer for value in row) <= 4
