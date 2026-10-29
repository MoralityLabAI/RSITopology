import math

from tiling import (
    balanced_shape,
    catalan,
    certificate_is_complete,
    chain_shape,
    label_shape,
    metrics,
    pareto_pairs,
    shapes,
)


def test_small_catalan_counts():
    assert [len(shapes(k)) for k in range(1, 7)] == [1, 1, 2, 5, 14, 42]
    assert all(len(shapes(k)) == catalan(k - 1) for k in range(1, 7))


def test_total_nodes_and_minimum_depth():
    for leaves in range(1, 8):
        assert all(metrics(shape)[1] == 2 * leaves - 1 for shape in shapes(leaves))
        assert min(metrics(shape)[2] for shape in shapes(leaves)) == math.ceil(math.log2(leaves))


def test_chain_balanced_resource_reversal_primitives():
    assert metrics(chain_shape(12))[2:] == (11, 2)
    assert metrics(balanced_shape(12))[2:] == (4, 4)


def test_certificate_requires_exact_leaf_coverage():
    certificate, end = label_shape(balanced_shape(6))
    assert end == 6
    assert certificate_is_complete(certificate, frozenset(range(6)))
    assert not certificate_is_complete(("summary", tuple(range(6))), frozenset(range(6)))
    assert not certificate_is_complete(("and", ("leaf", 0), ("leaf", 0)), frozenset({0, 1}))


def test_pareto_pairs_are_nondominated():
    for leaves in range(1, 7):
        pairs = pareto_pairs(leaves)
        assert all(
            not any(other != pair and other[0] <= pair[0] and other[1] <= pair[1] for other in pairs)
            for pair in pairs
        )
