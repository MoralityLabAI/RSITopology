from fractions import Fraction as Q

from verify_theorems_v0_54 import (
    binary_projection,
    census_kernels,
    independent_bm_table,
    independent_classification,
    independent_ranking_mixture,
    witnesses,
)


def test_independent_witness_classifications():
    scalar, middle, none, _ = witnesses()
    assert independent_classification(scalar)[0] == "scalar_luce"
    assert independent_classification(middle)[0] == "random_utility_non_luce"
    assert independent_classification(none)[0] == "no_random_utility_representation"


def test_independent_no_object_certificate():
    _, _, none, _ = witnesses()
    table = independent_bm_table(none)
    assert table[("a", ("a", "b"))] == Q(-1, 4)
    assert independent_ranking_mixture(none) is None


def test_independent_access_projection():
    _, _, none, scalar_access = witnesses()
    assert binary_projection(none) == binary_projection(scalar_access)
    assert independent_classification(scalar_access)[0] == "scalar_luce"


def test_independent_census_cardinality():
    assert sum(1 for _ in census_kernels()) == 1250


def test_independent_middle_mixture_is_exact():
    _, middle, _, _ = witnesses()
    mixture = independent_ranking_mixture(middle)
    assert mixture is not None
    assert sum(mixture.values(), Q(0)) == 1
    assert all(value >= 0 for value in mixture.values())

