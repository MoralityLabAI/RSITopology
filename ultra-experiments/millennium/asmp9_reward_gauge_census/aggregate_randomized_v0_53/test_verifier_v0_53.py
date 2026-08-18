from fractions import Fraction as Q

from verify_theorems_v0_53 import (
    controls,
    independent_binary_vertices,
    independent_deterministic_optimum,
    independent_randomized_optimum,
    independent_subset_table,
)


def test_independent_polygon_vertices_include_optimum():
    vertices = independent_binary_vertices(Q(3, 5))
    assert (Q(5, 6), Q(0)) in vertices
    assert len(vertices) == 4


def test_independent_primal_values():
    assert independent_randomized_optimum(Q(3, 5))[0] == Q(5, 12)
    assert independent_randomized_optimum(Q(9, 10))[0] == Q(5, 18)
    assert independent_deterministic_optimum(Q(3, 5))[0] == Q(1, 2)


def test_independent_subset_table_contrast():
    assert independent_subset_table(Q(3, 5)) == (0, 1, 0, 1)
    assert independent_subset_table(Q(9, 10)) == (0, 1, 0, 1)
    assert independent_subset_table(Q(1, 2)) == (0, 0, 0, 1)


def test_controls_separate_aggregate_and_component_validity():
    result = controls()
    mixture = result["invalid_component_mixture"]
    assert mixture["aggregate_coverage"] == "1/2"
    assert mixture["invalid_component_coverage"] == "0"
    assert result["crossing_support"]["positive_report_atoms"] == 4
