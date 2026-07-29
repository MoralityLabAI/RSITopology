from copy import deepcopy

from verify_theorems_v0_49_1 import (
    corrected_universe_valid,
    original_failure_is_count_only,
)


def valid_original():
    return {
        "ok": False,
        "status": "finite_common_ordering_theorem_not_verified",
        "gates": {
            "H0": True,
            "T0": True,
            "M0": True,
            "D0": False,
            "G0": True,
            "V0": True,
            "RESOURCE": True,
        },
        "exhaustive_four_outcome": {
            "expected_table_count": 168,
            "expected_ordered_pair_count": 168**2,
            "table_count": 167,
            "ordered_pair_count": 167**2,
            "tight_dag_mismatches": 0,
            "common_chain_mismatches": 0,
        },
    }


def test_exact_count_only_failure_is_repairable():
    original = valid_original()
    assert corrected_universe_valid(original)
    assert original_failure_is_count_only(original)


def test_scientific_mismatch_is_not_repairable():
    original = deepcopy(valid_original())
    original["exhaustive_four_outcome"][
        "common_chain_mismatches"
    ] = 1
    assert not corrected_universe_valid(original)
    assert not original_failure_is_count_only(original)


def test_other_gate_failure_is_not_repairable():
    original = deepcopy(valid_original())
    original["gates"]["V0"] = False
    assert corrected_universe_valid(original)
    assert not original_failure_is_count_only(original)
