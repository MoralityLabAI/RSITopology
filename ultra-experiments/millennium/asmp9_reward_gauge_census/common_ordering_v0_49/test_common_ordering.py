from fractions import Fraction as Q
from itertools import permutations
import json
from pathlib import Path

from common_ordering import (
    common_chain_certificate,
    finite_buehler_subset_bounds,
    ordering_gauge_certificate,
    ordering_gauge_scale_compatibility,
    square_curls,
    tight_predecessor_dag,
)


HERE = Path(__file__).resolve().parent
V048 = HERE.parent / "ordering_modulus_v0_48"


def ordering_cost(ordering, bounds, weights):
    mask = 0
    value = Q(0)
    for index in ordering:
        mask |= 1 << index
        value += weights[index] * bounds[mask]
    return value


def exhaustive_optima(bounds, weights):
    rows = [
        (ordering_cost(ordering, bounds, weights), ordering)
        for ordering in permutations(range(len(weights)))
    ]
    optimum = min(value for value, _ in rows)
    return {
        ordering for value, ordering in rows if value == optimum
    }


def test_tight_dag_matches_exhaustive_optimizer_count():
    weights = (Q(1, 10), Q(1, 5), Q(3, 10), Q(2, 5))
    bounds = tuple(
        Q(mask.bit_count() ** 2 + (mask % 3), 17)
        for mask in range(16)
    )
    exact = exhaustive_optima(bounds, weights)
    dag = tight_predecessor_dag(bounds, weights)
    assert dag.optimizer_counts[-1] == len(exact)


def test_disjoint_tight_dags_certify_no_common_order():
    weights = (Q(1, 2), Q(1, 2))
    first = (Q(0), Q(0), Q(1), Q(1))
    second = (Q(0), Q(1), Q(0), Q(1))
    certificate = common_chain_certificate(first, second, weights)
    assert certificate.first_optimizer_count == 1
    assert certificate.second_optimizer_count == 1
    assert certificate.common_optimizer_count == 0
    assert not certificate.common_optimizer_exists
    assert certificate.boundary


def test_minimal_two_by_two_statistical_witness():
    rows = (
        (Q(9, 10), Q(1, 10)),
        (Q(1, 10), Q(9, 10)),
    )
    first = finite_buehler_subset_bounds(
        risks=(Q(0), Q(1)),
        probability_rows=rows,
        alpha=Q(1, 5),
    )
    second = finite_buehler_subset_bounds(
        risks=(Q(1), Q(0)),
        probability_rows=rows,
        alpha=Q(1, 5),
    )
    assert first == (Q(0), Q(0), Q(1), Q(1))
    assert second == (Q(0), Q(1), Q(0), Q(1))
    weights = (Q(1, 2), Q(1, 2))
    certificate = common_chain_certificate(first, second, weights)
    assert certificate.common_optimizer_count == 0
    assert ordering_cost((0, 1), first, weights) == Q(1, 2)
    assert ordering_cost((1, 0), first, weights) == Q(1)
    assert ordering_cost((1, 0), second, weights) == Q(1, 2)
    assert ordering_cost((0, 1), second, weights) == Q(1)


def test_common_chain_count_matches_exhaustive_intersection():
    weights = (Q(1, 6), Q(1, 3), Q(1, 2))
    first = tuple(Q(mask.bit_count(), 5) for mask in range(8))
    second = tuple(
        Q(2) * value + Q(3, 7) for value in first
    )
    second = (Q(0),) + second[1:]
    exact_first = exhaustive_optima(first, weights)
    exact_second = exhaustive_optima(second, weights)
    certificate = common_chain_certificate(first, second, weights)
    assert certificate.common_optimizer_count == len(
        exact_first.intersection(exact_second)
    )
    assert certificate.common_optimizer_exists


def test_zero_curl_gauge_preserves_all_ordering_differences():
    weights = (Q(1, 6), Q(1, 3), Q(1, 2))
    first = tuple(Q(mask * mask + 1, 13) for mask in range(8))
    second = tuple(Q(2) * value + Q(5, 11) for value in first)
    certificate = ordering_gauge_certificate(
        first, second, weights, scale=Q(2)
    )
    assert certificate.valid
    assert not certificate.nonzero_curls
    assert certificate.additive_constant == Q(5, 11)
    for ordering in permutations(range(3)):
        assert ordering_cost(ordering, second, weights) == (
            Q(2) * ordering_cost(ordering, first, weights)
            + certificate.additive_constant
        )
    assert exhaustive_optima(first, weights) == exhaustive_optima(
        second, weights
    )


def test_nonzero_square_curl_rejects_ordering_gauge():
    weights = (Q(1, 2), Q(1, 2))
    perturbation = (Q(0), Q(0), Q(1), Q(0))
    curls = square_curls(perturbation, weights)
    assert len(curls) == 1
    assert curls[0]["curl"] == Q(-1, 2)
    certificate = ordering_gauge_certificate(
        (Q(0),) * 4,
        perturbation,
        weights,
        scale=Q(1),
    )
    assert not certificate.valid


def test_v048_confirmation_common_count_is_recovered():
    subset = json.loads(
        (
            V048
            / "artifacts_v0_48"
            / "subset_bounds_v0_48.json"
        ).read_text(encoding="utf-8")
    )
    result = json.loads(
        (
            V048
            / "artifacts_v0_48"
            / "result_v0_48.json"
        ).read_text(encoding="utf-8")
    )
    weights = tuple(
        Q(value)
        for value in result["scientific"]["primary"][
            "reference_weights"
        ]
    )
    certificate = common_chain_certificate(
        tuple(Q(value) for value in subset["classification"]),
        tuple(Q(value) for value in subset["root_group"]),
        weights,
    )
    assert certificate.first_optimizer_count == 1_451_520
    assert certificate.second_optimizer_count == 4_354_560
    assert certificate.common_optimizer_count == 1_451_520
    assert certificate.common_optimizer_exists
    gauge = ordering_gauge_scale_compatibility(
        tuple(Q(value) for value in subset["classification"]),
        tuple(Q(value) for value in subset["root_group"]),
        weights,
    )
    assert gauge.status == "no_positive_scale"
    assert len(gauge.distinct_required_scales) > 1
