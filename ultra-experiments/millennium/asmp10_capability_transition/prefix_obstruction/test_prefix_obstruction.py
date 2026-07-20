from fractions import Fraction
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("run_prefix_obstruction.py")
SPEC = importlib.util.spec_from_file_location("asmp10_prefix", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_exact_rank_threshold():
    for n_nodes in (1, 2, 4):
        for jet_order in (1, 2):
            observations = n_nodes * (jet_order + 1)
            for degree in (max(0, observations - 1), observations, observations + 2):
                rank = MODULE.exact_rank(MODULE.hermite_matrix(n_nodes, jet_order, degree))
                assert rank == min(degree + 1, observations)


def test_witness_is_in_exact_kernel():
    for n_nodes in (1, 3, 5):
        for jet_order in (1, 2, 3):
            vector = MODULE.invisible_witness(n_nodes, jet_order)
            matrix = MODULE.hermite_matrix(n_nodes, jet_order, len(vector) - 1)
            assert MODULE.matvec(matrix, vector) == [Fraction(0)] * len(matrix)


def test_mirage_pair_has_opposite_future_scores():
    pair = MODULE.mirage_pair(4, 2)
    assert pair["prefix_equal"]
    assert pair["kernel_exact"]
    assert pair["plus_future_score"] == "-1"
    assert pair["minus_future_score"] == "1"
    assert pair["capabilities_differ"]


def test_complete_census_passes_all_gates():
    result = MODULE.run_census()
    assert result["verdict"] == "finite_prefix_obstruction_established_for_registered_class"
    assert all(result["gates"].values())
    assert len(result["witnesses"]) == 15

