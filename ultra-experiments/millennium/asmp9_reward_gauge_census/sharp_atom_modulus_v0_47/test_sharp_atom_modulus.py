from fractions import Fraction as Q
from itertools import product

import pytest

from sharp_atom_modulus import (
    allocation_modulus_census,
    all_zero_probability,
    buehler_upper_table,
    boundary_parameters,
    classification_risk_table,
    mandatory_atom_region,
    method_of_types_coupled_upper,
    parameter_grid,
    root_group_risk_table,
    sharp_atom_modulus,
    spike_confidence_coverage,
    total_error_cdf,
)


def test_all_zero_probability_is_exact_product():
    assert all_zero_probability(
        (Q(1, 10), Q(1, 5), Q(1, 4)),
        (2, 3, 1),
    ) == Q(9, 10) ** 2 * Q(4, 5) ** 3 * Q(3, 4)


def test_total_error_cdf_is_exact_and_starts_at_zero_atom():
    parameter = (Q(1, 10), Q(1, 5), Q(1, 4))
    allocation = (2, 3, 1)
    row = total_error_cdf(parameter, allocation)
    assert len(row) == sum(allocation) + 1
    assert row[0] == all_zero_probability(parameter, allocation)
    assert row[-1] == 1
    assert all(left <= right for left, right in zip(row, row[1:]))


def test_mandatory_region_uses_strict_probability_threshold():
    parameters = (
        (Q(0), Q(0), Q(0)),
        (Q(1, 2), Q(0), Q(0)),
    )
    assert mandatory_atom_region(parameters, (1, 1, 1), Q(1, 2)) == (
        parameters[0],
    )
    assert boundary_parameters(parameters, (1, 1, 1), Q(1, 2)) == (
        parameters[1],
    )


def test_spike_construction_has_uniform_coverage():
    parameters = parameter_grid((Q(0), Q(1, 4), Q(1, 2)))
    alpha = Q(1, 20)
    coverage = spike_confidence_coverage(
        parameters, (3, 2, 1), alpha
    )
    assert min(coverage.values()) >= Q(19, 20)


def test_sharp_modulus_matches_mandatory_lower_and_spike_upper():
    parameters = parameter_grid((Q(0), Q(1, 4), Q(1, 2)))
    risks = {
        parameter: sum(parameter, Q(0)) for parameter in parameters
    }
    result = sharp_atom_modulus(risks, (3, 2, 1), Q(1, 20))
    mandatory = mandatory_atom_region(
        parameters, (3, 2, 1), Q(1, 20)
    )
    expected = max(risks[parameter] for parameter in mandatory)
    assert result.lower == expected
    assert result.upper == expected
    assert result.minimum_spike_coverage >= Q(19, 20)


def test_partial_risk_table_may_omit_only_nonmandatory_parameters():
    parameters = parameter_grid((Q(0), Q(1, 4), Q(1, 2)))
    allocation = (3, 2, 1)
    alpha = Q(1, 20)
    mandatory = mandatory_atom_region(parameters, allocation, alpha)
    risks = {
        parameter: sum(parameter, Q(0)) for parameter in mandatory
    }
    result = sharp_atom_modulus(
        risks,
        allocation,
        alpha,
        parameter_universe=parameters,
    )
    assert result.mandatory_count == len(mandatory)
    with pytest.raises(ValueError):
        sharp_atom_modulus(
            {mandatory[0]: risks[mandatory[0]]},
            allocation,
            alpha,
            parameter_universe=parameters,
        )


def test_buehler_table_is_monotone_honest_and_matches_atom_modulus():
    risks = {"low": Q(1, 10), "high": Q(2, 5)}
    cdfs = {
        "low": (Q(1, 100), Q(1, 2), Q(1)),
        "high": (Q(1, 10), Q(1, 4), Q(1)),
    }
    table = buehler_upper_table(risks, cdfs, Q(1, 20))
    assert table == (Q(2, 5), Q(2, 5), Q(2, 5))
    atom_expected = max(
        risks[parameter]
        for parameter in risks
        if cdfs[parameter][0] > Q(1, 20)
    )
    assert table[0] == atom_expected


def test_buehler_table_can_increase_with_evidence_order():
    risks = {"low": Q(1, 10), "high": Q(2, 5)}
    cdfs = {
        "low": (Q(1, 10), Q(1)),
        "high": (Q(1, 100), Q(1)),
    }
    assert buehler_upper_table(
        risks, cdfs, Q(1, 20)
    ) == (Q(1, 10), Q(2, 5))


def test_parameter_grid_rejects_invalid_levels():
    with pytest.raises(ValueError):
        parameter_grid((Q(1, 10), Q(1, 5)))
    with pytest.raises(ValueError):
        parameter_grid((Q(0), Q(3, 5)))


def test_root_group_risk_uses_only_root_coordinate():
    levels = (Q(0), Q(1, 4), Q(1, 2))
    table = root_group_risk_table(levels)
    for parameter in product(levels, repeat=3):
        assert table[parameter] == parameter[0]


def test_classification_risk_anchor_points():
    table = classification_risk_table((Q(0), Q(1, 2)))
    assert table[(Q(0), Q(0), Q(0))] == 0
    assert table[(Q(1, 2), Q(1, 2), Q(1, 2))] == Q(3, 4)
    assert all(Q(0) <= risk <= Q(3, 4) for risk in table.values())


def test_same_parameter_radius_can_have_different_decision_risk():
    table = classification_risk_table((Q(0), Q(1, 10)))
    assert table[(Q(1, 10), Q(0), Q(0))] == Q(1, 10)
    assert table[(Q(1, 10), Q(1, 10), Q(1, 10))] == Q(19, 100)


def test_confirmation_design_has_no_alpha_boundary_equalities():
    parameters = parameter_grid(
        (
            Q(0),
            Q(1, 50),
            Q(1, 25),
            Q(1, 20),
            Q(3, 50),
            Q(2, 25),
            Q(1, 10),
            Q(3, 25),
            Q(13, 100),
            Q(7, 50),
            Q(3, 20),
        )
    )
    for allocation in ((30, 21, 21), (70, 1, 1), (24, 24, 24)):
        assert not boundary_parameters(
            parameters, allocation, Q(1, 20)
        )


def test_inherited_method_of_types_upper_is_available_at_n72_designs():
    for allocation in ((30, 21, 21), (24, 24, 24)):
        assert 0 < method_of_types_coupled_upper(
            allocation, "branch_classification"
        ) <= Q(3, 4)
    for allocation in ((70, 1, 1), (24, 24, 24)):
        assert 0 < method_of_types_coupled_upper(
            allocation, "root_group"
        ) <= Q(1, 2)


def test_small_allocation_census_is_exact_and_complete():
    levels = (Q(0), Q(1, 4), Q(1, 2))
    result = allocation_modulus_census(
        root_group_risk_table(levels),
        total_budget=8,
        alpha=Q(1, 20),
    )
    assert result["allocation_count"] == 21
    assert result["optimum"] >= 0
    assert all(
        row.modulus.lower == row.modulus.upper
        for row in result["rows"]
    )
