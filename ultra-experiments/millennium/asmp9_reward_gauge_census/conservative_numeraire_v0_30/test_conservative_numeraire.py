from copy import deepcopy
from fractions import Fraction

import pytest

from .conservative_numeraire import (
    apply_registered_mutation,
    build_value_table,
    calibration_constraint_matrix,
    deterministic_stationary_policies,
    expected_feature_occupancy,
    mechanics_hash,
    omitted_constraint_witness,
    pairwise_offset_bias_audit,
    rational_rank,
    rescaled_semantic_population_law,
    semantic_calibration,
    semantic_population_law,
    structural_conservativity,
    v028_eligibility,
)


def burned_mdp():
    return {
        "action_sets": {
            "s0": ["left", "right"],
            "s1": ["stay"],
            "terminal": ["stay"],
        },
        "feature_dimension": 2,
        "features": [
            {
                "action": "left",
                "next_state": "s1",
                "state": "s0",
                "vector": [1, 0],
            },
            {
                "action": "right",
                "next_state": "terminal",
                "state": "s0",
                "vector": [0, 2],
            },
            {
                "action": "stay",
                "next_state": "terminal",
                "state": "s1",
                "vector": [1, 1],
            },
            {
                "action": "stay",
                "next_state": "terminal",
                "state": "terminal",
                "vector": [0, 0],
            },
        ],
        "horizon": 3,
        "initial_distribution": {"s0": 1, "s1": 0, "terminal": 0},
        "states": ["s0", "s1", "terminal"],
        "transitions": [
            {
                "action": "left",
                "next_state": "s1",
                "probability": 1,
                "state": "s0",
            },
            {
                "action": "right",
                "next_state": "terminal",
                "probability": 1,
                "state": "s0",
            },
            {
                "action": "stay",
                "next_state": "terminal",
                "probability": 1,
                "state": "s1",
            },
            {
                "action": "stay",
                "next_state": "terminal",
                "probability": 1,
                "state": "terminal",
            },
        ],
    }


def copied_interventions(mdp, levels=(-2, 0, 3)):
    return tuple(
        {"level": str(level), "mdp": deepcopy(mdp)}
        for level in levels
    )


def test_exact_product_extension_preserves_every_stationary_occupancy():
    mdp = burned_mdp()
    interventions = copied_interventions(mdp)
    result = structural_conservativity(mdp, interventions)
    assert result["structurally_conservative"]
    assert len(
        {
            row["mechanics_hash"]
            for row in result["intervention_rows"]
        }
    ) == 1
    policies = deterministic_stationary_policies(mdp)
    assert len(policies) == 2
    baseline = tuple(expected_feature_occupancy(mdp, p) for p in policies)
    for intervention in interventions:
        assert tuple(
            expected_feature_occupancy(intervention["mdp"], p)
            for p in policies
        ) == baseline


@pytest.mark.parametrize(
    ("field", "mutate"),
    [
        ("horizon", lambda mdp: mdp.__setitem__("horizon", 4)),
        (
            "action_sets",
            lambda mdp: mdp["action_sets"]["s0"].append("wait"),
        ),
        (
            "transitions",
            lambda mdp: mdp["transitions"][0].__setitem__(
                "probability", Fraction(3, 4)
            ),
        ),
        (
            "features",
            lambda mdp: mdp["features"][0].__setitem__("vector", [2, 0]),
        ),
    ],
)
def test_each_mechanical_channel_is_checked(field, mutate):
    mdp = burned_mdp()
    changed = deepcopy(mdp)
    mutate(changed)
    if field == "action_sets":
        changed["transitions"].append(
            {
                "action": "wait",
                "next_state": "s0",
                "probability": 1,
                "state": "s0",
            }
        )
        changed["features"].append(
            {
                "action": "wait",
                "next_state": "s0",
                "state": "s0",
                "vector": [0, 0],
            }
        )
    if field == "transitions":
        changed["transitions"].append(
            {
                "action": "left",
                "next_state": "terminal",
                "probability": Fraction(1, 4),
                "state": "s0",
            }
        )
        changed["features"].append(
            {
                "action": "left",
                "next_state": "terminal",
                "state": "s0",
                "vector": [0, 0],
            }
        )
    result = structural_conservativity(
        mdp, ({"level": "changed", "mdp": changed},)
    )
    assert not result["structurally_conservative"]
    assert field in result["intervention_rows"][0]["changed_fields"]


def test_registered_mutation_grammar_covers_all_four_channels():
    mdp = burned_mdp()
    mutations = (
        {"kind": "set_horizon", "value": 5},
        {
            "action": "wait",
            "features": [
                {
                    "action": "wait",
                    "next_state": "s0",
                    "state": "s0",
                    "vector": [0, 0],
                }
            ],
            "kind": "add_action",
            "state": "s0",
            "transitions": [
                {
                    "action": "wait",
                    "next_state": "s0",
                    "probability": 1,
                    "state": "s0",
                }
            ],
        },
        {
            "action": "left",
            "features": [
                {
                    "action": "left",
                    "next_state": "s1",
                    "state": "s0",
                    "vector": [1, 0],
                },
                {
                    "action": "left",
                    "next_state": "terminal",
                    "state": "s0",
                    "vector": [0, 0],
                },
            ],
            "kind": "replace_transition_distribution",
            "state": "s0",
            "transitions": [
                {
                    "action": "left",
                    "next_state": "s1",
                    "probability": "2/3",
                    "state": "s0",
                },
                {
                    "action": "left",
                    "next_state": "terminal",
                    "probability": "1/3",
                    "state": "s0",
                },
            ],
        },
        {
            "action": "left",
            "kind": "replace_feature",
            "next_state": "s1",
            "state": "s0",
            "vector": [1, "1/5"],
        },
    )
    expected = ("horizon", "action_sets", "transitions", "features")
    for mutation, field in zip(mutations, expected):
        changed = apply_registered_mutation(mdp, mutation)
        result = structural_conservativity(
            mdp, ({"level": field, "mdp": changed},)
        )
        assert field in result["intervention_rows"][0]["changed_fields"]


def test_calibrated_unknown_scale_and_interaction_are_distinct():
    offsets = (-2, 0, 3)
    bases = (Fraction(1, 3), Fraction(-5, 7), Fraction(11, 4))
    calibrated = tuple(
        tuple(base + offset for offset in offsets)
        for base in bases
    )
    unknown_scale = tuple(
        tuple(base + Fraction(7, 5) * offset for offset in offsets)
        for base in bases
    )
    interaction = [list(row) for row in calibrated]
    interaction[2][2] += Fraction(1, 9)

    assert (
        semantic_calibration(offsets, calibrated, reference_index=1)[
            "classification"
        ]
        == "calibrated_additive"
    )
    scaled = semantic_calibration(
        offsets, unknown_scale, reference_index=1
    )
    assert scaled["classification"] == "separable_unknown_scale"
    assert scaled["proportional_coefficient"] == Fraction(7, 5)
    assert (
        semantic_calibration(offsets, interaction, reference_index=1)[
            "classification"
        ]
        == "context_interaction"
    )


def test_value_table_builder_separates_scale_interaction_and_missingness():
    offsets = (-3, 0, 2)
    bases = (Fraction(1, 5), Fraction(7, 9))
    calibrated = build_value_table(
        bases, offsets, common_constant=Fraction(2, 7)
    )
    assert (
        semantic_calibration(offsets, calibrated, reference_index=1)[
            "classification"
        ]
        == "calibrated_additive"
    )
    scaled = build_value_table(bases, offsets, coefficient=Fraction(4, 3))
    assert (
        semantic_calibration(offsets, scaled, reference_index=1)[
            "classification"
        ]
        == "separable_unknown_scale"
    )
    interaction = build_value_table(
        bases,
        offsets,
        adjustments=(
            {"base_index": 1, "delta": "1/13", "level_index": 2},
        ),
    )
    assert (
        semantic_calibration(offsets, interaction, reference_index=1)[
            "classification"
        ]
        == "context_interaction"
    )
    incomplete = build_value_table(
        bases, offsets, missing_cells=((0, 2),)
    )
    assert not semantic_calibration(
        offsets, incomplete, reference_index=1
    )["available"]


def test_incomplete_table_is_unavailable():
    result = semantic_calibration(
        (-1, 0, 1),
        ((0, 1, None), (2, 3, 4)),
        reference_index=1,
    )
    assert result == {
        "available": False,
        "classification": "incomplete_semantic_table",
        "complete": False,
    }


def test_pairwise_bias_bound_is_sharp():
    epsilon = Fraction(2, 11)
    offsets = (-1, 0, 2)
    table = (
        (-1 + epsilon, 0, 2),
        (-1 - epsilon, 0, 2),
    )
    result = pairwise_offset_bias_audit(
        offsets, table, reference_index=1
    )
    assert result["single_cell_residual_bound"] == epsilon
    assert result["maximum_pairwise_bias"] == 2 * epsilon
    assert result["bound"] == 2 * epsilon
    assert result["bound_valid"]


def test_calibration_constraint_count_is_sharp_under_omission():
    base_count, consequence_count, reference = 4, 5, 2
    matrix = calibration_constraint_matrix(
        base_count, consequence_count, reference
    )
    assert len(matrix) == base_count * (consequence_count - 1)
    assert rational_rank(matrix) == len(matrix)
    for base_index in range(base_count):
        for level_index in range(consequence_count):
            if level_index == reference:
                continue
            witness = omitted_constraint_witness(
                base_count,
                consequence_count,
                base_index,
                level_index,
                reference,
            )
            flattened = tuple(value for row in witness for value in row)
            evaluations = tuple(
                sum(
                    coefficient * value
                    for coefficient, value in zip(row, flattened)
                )
                for row in matrix
            )
            omitted_row = (
                base_index * (consequence_count - 1)
                + level_index
                - (1 if level_index > reference else 0)
            )
            assert evaluations[omitted_row] == 1
            assert all(
                value == 0
                for index, value in enumerate(evaluations)
                if index != omitted_row
            )


def test_unknown_coefficient_scale_coupling_survives_complete_grid():
    base_values = (Fraction(-3, 5), Fraction(7, 8), Fraction(11, 13))
    offsets = (-2, 0, 3)
    coefficient = Fraction(5, 7)
    radius = 5
    baseline = semantic_population_law(
        base_values, offsets, coefficient, radius
    )
    for alpha in (Fraction(2, 3), Fraction(9, 4)):
        assert baseline == rescaled_semantic_population_law(
            base_values,
            offsets,
            coefficient,
            alpha,
            radius,
        )


def test_mechanics_alone_cannot_distinguish_semantic_variants():
    mdp = burned_mdp()
    offsets = (-2, 0, 3)
    calibrated = ((-2, 0, 3), (3, 5, 8))
    unknown = (
        (Fraction(-14, 5), 0, Fraction(21, 5)),
        (Fraction(11, 5), 5, Fraction(46, 5)),
    )
    assert mechanics_hash(mdp) == mechanics_hash(deepcopy(mdp))
    assert (
        semantic_calibration(offsets, calibrated, reference_index=1)[
            "classification"
        ]
        == "calibrated_additive"
    )
    assert (
        semantic_calibration(offsets, unknown, reference_index=1)[
            "classification"
        ]
        == "separable_unknown_scale"
    )


def test_v028_eligibility_requires_both_certificates():
    mdp = burned_mdp()
    interventions = copied_interventions(mdp)
    offsets = (-2, 0, 3)
    calibrated = ((-2, 0, 3), (3, 5, 8))
    eligible = v028_eligibility(
        mdp,
        interventions,
        offsets,
        calibrated,
        reference_index=1,
    )
    assert eligible["eligible"]
    unknown = ((-4, 0, 6), (1, 5, 11))
    rejected = v028_eligibility(
        mdp,
        interventions,
        offsets,
        unknown,
        reference_index=1,
    )
    assert not rejected["eligible"]
    assert rejected["reasons"] == (
        "semantic_calibration_not_established",
    )
