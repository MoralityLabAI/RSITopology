from fractions import Fraction as Q

from risk_polytope_access import (
    DEVELOPMENT_QUERIES,
    binary_group_partition_deficiency,
    classification_partition_deficiency,
    classification_problem,
    compile_access_table,
    development_problems,
    is_test_cover,
    minimal_access_sets,
)


def test_zero_deficiency_classification_matches_test_cover_exactly():
    rows = compile_access_table(
        DEVELOPMENT_QUERIES, (classification_problem(),)
    )
    for row in rows:
        assert (row.epsilon == 0) == is_test_cover(
            DEVELOPMENT_QUERIES, row.subset
        )
        assert row.epsilon == classification_partition_deficiency(
            DEVELOPMENT_QUERIES, row.subset
        )


def test_decision_type_changes_minimal_zero_error_access():
    expected = {
        "classification": (
            ("q0", "q1"),
            ("q0", "q2"),
            ("q1", "q2"),
        ),
        "q0_asymmetric": (("q0",), ("q1", "q2")),
        "q1_asymmetric": (("q1",), ("q0", "q2")),
        "combined_groups": (
            ("q0", "q1"),
            ("q0", "q2"),
            ("q1", "q2"),
        ),
    }
    for name, problems in development_problems().items():
        rows = compile_access_table(DEVELOPMENT_QUERIES, problems)
        assert minimal_access_sets(rows, Q(0)) == expected[name]


def test_target_independent_query_is_never_inclusion_minimal():
    for problems in development_problems().values():
        rows = compile_access_table(DEVELOPMENT_QUERIES, problems)
        for tolerance in {row.epsilon for row in rows}:
            assert all(
                "q_const" not in subset
                for subset in minimal_access_sets(rows, tolerance)
            )


def test_asymmetric_partition_formula_matches_exact_compiler():
    labels_and_costs = {
        "q0_asymmetric": ((0, 0, 1), Q(1, 3), Q(1)),
        "q1_asymmetric": ((0, 1, 0), Q(2, 5), Q(1)),
    }
    problems = development_problems()
    for name, (labels, false_positive, false_negative) in (
        labels_and_costs.items()
    ):
        rows = compile_access_table(DEVELOPMENT_QUERIES, problems[name])
        for row in rows:
            assert row.epsilon == binary_group_partition_deficiency(
                DEVELOPMENT_QUERIES,
                row.subset,
                labels,
                false_positive,
                false_negative,
            )
