from fractions import Fraction

from balanced_cover import (
    bayes_error,
    optimal_balanced_laws,
    robustness_probes,
    sign_count_tv_upper_bound,
    theorem_cell,
    total_variation,
)


def test_optimizer_is_a_probability_pair_with_exact_uniform_average():
    for alphabet_size in range(2, 16):
        p0, p1 = optimal_balanced_laws(alphabet_size)
        assert min(p0 + p1) >= 0
        assert sum(p0) == sum(p1) == 1
        assert all((left + right) / 2 == Fraction(1, alphabet_size) for left, right in zip(p0, p1))


def test_parity_frontier_and_odd_error_formula():
    for alphabet_size in range(2, 32):
        cell = theorem_cell(alphabet_size)
        assert cell["perfect_decoding"] == (alphabet_size % 2 == 0)
        expected = Fraction(0) if alphabet_size % 2 == 0 else Fraction(1, 2 * alphabet_size)
        assert Fraction(cell["bayes_error"]) == expected


def test_witness_meets_sign_count_dual_bound():
    for alphabet_size in range(2, 32):
        p0, p1 = optimal_balanced_laws(alphabet_size)
        assert total_variation(p0, p1) == sign_count_tv_upper_bound(alphabet_size)


def test_per_message_cover_is_chance():
    for alphabet_size in range(2, 16):
        cover = [Fraction(1, alphabet_size)] * alphabet_size
        assert bayes_error(cover, cover) == Fraction(1, 2)


def test_metric_robustness_pack_passes():
    probes = robustness_probes()
    assert set(probes) == {"invariance", "sensitivity", "monotonicity", "anti_gaming", "clean_control"}
    assert all(record["pass"] for record in probes.values())
