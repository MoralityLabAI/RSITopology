from fractions import Fraction

from frontier import (
    ERROR_LIMIT,
    QUERY_GRID,
    beta_binomial_distribution,
    compute_rows,
    evaluate_gates,
    global_flip_error,
    majority_error,
    targeted_average_attack,
)


def test_probability_mass_is_exact() -> None:
    for n in range(1, 10):
        for rho in (Fraction(0), Fraction(1, 20), Fraction(1, 5), Fraction(1, 2)):
            assert sum(beta_binomial_distribution(n, rho)) == 1


def test_independent_q9_matches_closed_binomial_value() -> None:
    assert majority_error(9, 1, Fraction(0)) == Fraction(7649, 390625)


def test_registered_correlation_boundary() -> None:
    assert majority_error(9, 1, Fraction(1, 20)) <= ERROR_LIMIT
    assert majority_error(9, 1, Fraction(1, 10)) > ERROR_LIMIT


def test_independent_family_diversity_recovers_q9_rho_point_two() -> None:
    assert majority_error(9, 1, Fraction(1, 5)) > ERROR_LIMIT
    assert majority_error(9, 3, Fraction(1, 5)) <= ERROR_LIMIT
    assert majority_error(9, 9, Fraction(1, 5)) <= ERROR_LIMIT


def test_global_flip_does_not_amplify() -> None:
    assert all(global_flip_error(q) == Fraction(1, 5) for q in QUERY_GRID)


def test_atom_average_bound_does_not_give_uniform_soundness() -> None:
    for n in (16, 64, 256, 1024):
        attack = targeted_average_attack(n)
        assert attack["atom_average_error"] <= Fraction(1, 5)
        assert attack["worst_case_false_accept"] == 1


def test_all_registered_gates_pass() -> None:
    gates = evaluate_gates(compute_rows())
    assert all(record["pass"] for record in gates.values())

