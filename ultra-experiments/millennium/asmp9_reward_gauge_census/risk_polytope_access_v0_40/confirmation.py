"""Prospective disjoint ASMP-9 v0.40 risk-polytope confirmation."""

from __future__ import annotations

from fractions import Fraction as Q

from risk_polytope_access import (
    all_subsets,
    binary_group_partition_deficiency,
    classification_partition_deficiency,
    classification_problem,
    compile_access_table,
    group_problem,
    is_test_cover,
    minimal_access_sets,
    persistence_curve,
    qstr,
    relative_deficiency,
    subset_experiment,
)


CONFIRMATION_QUERIES = {
    "s0": (Q(0), Q(0), Q(1), Q(1)),
    "s1": (Q(0), Q(1), Q(0), Q(1)),
    "sx": (Q(0), Q(1), Q(1), Q(0)),
    "s_const": (Q(1), Q(1), Q(1), Q(1)),
}

S0_LABELS = (0, 0, 1, 1)
S1_LABELS = (0, 1, 0, 1)
S0_FP = Q(1, 4)
S0_FN = Q(1)
S1_FP = Q(3, 5)
S1_FN = Q(4, 5)


def confirmation_problems():
    classification = classification_problem(4)
    s0 = group_problem(
        "s0_asymmetric_group", S0_LABELS, S0_FP, S0_FN
    )
    s1 = group_problem(
        "s1_asymmetric_group", S1_LABELS, S1_FP, S1_FN
    )
    return {
        "classification": (classification,),
        "s0_asymmetric": (s0,),
        "s1_asymmetric": (s1,),
        "combined_groups": (s0, s1),
    }


def _analytic_classification_rows() -> list[dict]:
    return [
        {
            "subset": list(subset),
            "subset_size": len(subset),
            "epsilon": qstr(
                classification_partition_deficiency(
                    CONFIRMATION_QUERIES, subset
                )
            ),
            "is_test_cover": is_test_cover(
                CONFIRMATION_QUERIES, subset
            ),
        }
        for subset in all_subsets(tuple(CONFIRMATION_QUERIES))
    ]


def _solver_spotchecks() -> list[dict]:
    problem = confirmation_problems()["classification"]
    reference = subset_experiment(
        CONFIRMATION_QUERIES, tuple(CONFIRMATION_QUERIES)
    )
    subsets = ((), ("s0",), ("s0", "s1"))
    rows = []
    for subset in subsets:
        source = subset_experiment(CONFIRMATION_QUERIES, subset)
        certificate = relative_deficiency(source, reference, problem)
        expected = classification_partition_deficiency(
            CONFIRMATION_QUERIES, subset
        )
        rows.append(
            {
                "subset": list(subset),
                "exact_solver_epsilon": qstr(certificate.epsilon),
                "partition_formula_epsilon": qstr(expected),
                "match": certificate.epsilon == expected,
            }
        )
    return rows


def _group_formula_gate(name: str, rows) -> bool:
    if name == "s0_asymmetric":
        labels, fp, fn = S0_LABELS, S0_FP, S0_FN
    elif name == "s1_asymmetric":
        labels, fp, fn = S1_LABELS, S1_FP, S1_FN
    else:
        raise ValueError(name)
    return all(
        row.epsilon
        == binary_group_partition_deficiency(
            CONFIRMATION_QUERIES, row.subset, labels, fp, fn
        )
        for row in rows
    )


def run_confirmation() -> dict:
    problems = confirmation_problems()
    classification_rows = _analytic_classification_rows()
    compiled = {
        name: compile_access_table(CONFIRMATION_QUERIES, decision_type)
        for name, decision_type in problems.items()
        if name != "classification"
    }
    solver_spotchecks = _solver_spotchecks()

    zero_minima = {
        "classification": tuple(
            tuple(row["subset"])
            for row in classification_rows
            if row["epsilon"] == "0"
            and len(row["subset"]) == 2
            and "s_const" not in row["subset"]
        ),
        **{
            name: minimal_access_sets(rows, Q(0))
            for name, rows in compiled.items()
        },
    }
    expected_zero = {
        "classification": (
            ("s0", "s1"),
            ("s0", "sx"),
            ("s1", "sx"),
        ),
        "s0_asymmetric": (("s0",), ("s1", "sx")),
        "s1_asymmetric": (("s1",), ("s0", "sx")),
        "combined_groups": (
            ("s0", "s1"),
            ("s0", "sx"),
            ("s1", "sx"),
        ),
    }

    classification_curve = (
        {
            "tolerance": "0",
            "minimal_access_sets": [
                ["s0", "s1"], ["s0", "sx"], ["s1", "sx"]
            ],
        },
        {
            "tolerance": "1/2",
            "minimal_access_sets": [["s0"], ["s1"], ["sx"]],
        },
        {"tolerance": "3/4", "minimal_access_sets": [[]]},
    )
    curves = {
        "classification": list(classification_curve),
        **{
            name: list(persistence_curve(rows))
            for name, rows in compiled.items()
        },
    }
    expected_curves = {
        "classification": list(classification_curve),
        "s0_asymmetric": [
            {
                "tolerance": "0",
                "minimal_access_sets": [["s0"], ["s1", "sx"]],
            },
            {"tolerance": "1/5", "minimal_access_sets": [[]]},
        ],
        "s1_asymmetric": [
            {
                "tolerance": "0",
                "minimal_access_sets": [["s1"], ["s0", "sx"]],
            },
            {"tolerance": "12/35", "minimal_access_sets": [[]]},
        ],
        "combined_groups": [
            {
                "tolerance": "0",
                "minimal_access_sets": [
                    ["s0", "s1"], ["s0", "sx"], ["s1", "sx"]
                ],
            },
            {
                "tolerance": "1/5",
                "minimal_access_sets": [["s1"], ["s0", "sx"]],
            },
            {"tolerance": "12/35", "minimal_access_sets": [[]]},
        ],
    }

    constant_invariance = True
    for name, rows in compiled.items():
        by_subset = {row.subset: row.epsilon for row in rows}
        for subset, epsilon in by_subset.items():
            if "s_const" in subset:
                continue
            with_constant = tuple(
                query
                for query in CONFIRMATION_QUERIES
                if query in set(subset).union({"s_const"})
            )
            constant_invariance &= by_subset[with_constant] == epsilon

    gates = {
        "C0_classification_formula": all(
            (Q(row["epsilon"]) == 0) == row["is_test_cover"]
            and Q(row["epsilon"])
            == classification_partition_deficiency(
                CONFIRMATION_QUERIES, row["subset"]
            )
            for row in classification_rows
        ),
        "H0_solver_formula_agreement": all(
            row["match"] for row in solver_spotchecks
        ),
        "G0_asymmetric_group_formula": (
            _group_formula_gate(
                "s0_asymmetric", compiled["s0_asymmetric"]
            )
            and _group_formula_gate(
                "s1_asymmetric", compiled["s1_asymmetric"]
            )
        ),
        "D0_decision_type_antichains": zero_minima == expected_zero,
        "F0_full_persistence_curves": curves == expected_curves,
        "K0_ancillary_query_invariance": constant_invariance,
    }
    return {
        "status": (
            "finite_risk_polytope_access_characterization_established"
            if all(gates.values())
            else "registered_gate_failed"
        ),
        "gates": gates,
        "classification_rows": classification_rows,
        "compiled_rows": {
            name: [row.jsonable() for row in rows]
            for name, rows in compiled.items()
        },
        "solver_spotchecks": solver_spotchecks,
        "zero_tolerance_minimal_access": {
            name: [list(subset) for subset in minima]
            for name, minima in zero_minima.items()
        },
        "persistence_curves": curves,
    }
