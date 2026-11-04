from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from identifiability_boundary import (
    as_fraction_matrix,
    build_result,
    exact_rank,
    gaussian_pairwise_lower_replicates,
    gaussian_upper_replicates,
    halting_coefficient_approximation,
    halting_reduction_fixture,
    halting_taylor_coefficient,
    identity,
    inverse,
    left_inverse,
    linear_gauge_fixture,
    main,
    matmul,
    nullspace_vector,
    run_design_census,
    sample_complexity_fixture,
    semialgebraic_boundary,
)
from verify_result import verify


class IdentifiabilityBoundaryTests(unittest.TestCase):
    def test_exact_linear_algebra(self) -> None:
        matrix = as_fraction_matrix(((1, 2), (3, 5)))
        self.assertEqual(exact_rank(matrix), 2)
        self.assertEqual(matmul(inverse(matrix), matrix), identity(2))
        tall = as_fraction_matrix(((1, 0), (0, 1), (1, 1)))
        self.assertEqual(matmul(left_inverse(tall), tall), identity(2))

    def test_nullspace_witness(self) -> None:
        matrix = as_fraction_matrix(((1, 2, 3), (2, 4, 6)))
        witness = nullspace_vector(matrix, 3)
        self.assertNotEqual(witness, (0, 0, 0))
        self.assertEqual(
            tuple(sum(a * b for a, b in zip(row, witness)) for row in matrix),
            (0, 0),
        )

    def test_small_exhaustive_design_census(self) -> None:
        result = run_design_census(max_quotient_dimension=2, max_rows=2)
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(result["matrix_count"], 104)
        self.assertEqual(result["full_rank_count"], 58)
        self.assertEqual(result["rank_deficient_count"], 46)

    def test_linear_gauge_fixture(self) -> None:
        result = linear_gauge_fixture()
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(result["good_separation_modulus"], Fraction(2))
        self.assertEqual(result["bad_collision_in_quotient_coordinates"], (0, 1))

    def test_sample_bounds(self) -> None:
        result = sample_complexity_fixture()
        self.assertTrue(all(result["gates"].values()))
        self.assertGreater(
            gaussian_upper_replicates(4, 0.5, 1.0, 0.1, 0.05),
            gaussian_upper_replicates(4, 1.0, 1.0, 0.1, 0.05),
        )
        self.assertGreater(
            gaussian_pairwise_lower_replicates(0.5, 1.0, 0.1, 0.05),
            gaussian_pairwise_lower_replicates(1.0, 1.0, 0.1, 0.05),
        )

    def test_halting_cauchy_name(self) -> None:
        self.assertEqual(halting_coefficient_approximation(5, 4), 0)
        self.assertEqual(halting_coefficient_approximation(5, 5), Fraction(1, 32))
        result = halting_reduction_fixture()
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(halting_taylor_coefficient(5, 5), 1)
        self.assertEqual(halting_taylor_coefficient(5, 4), 0)

    def test_semialgebraic_boundary(self) -> None:
        result = semialgebraic_boundary()
        self.assertTrue(all(result["gates"].values()))
        self.assertFalse(result["polynomial_time_claim"])

    def test_result_and_receipt(self) -> None:
        result = build_result(max_quotient_dimension=2, max_rows=2)
        self.assertTrue(result["all_exact_gates_pass"])
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "result.json"
            self.assertEqual(
                main(
                    [
                        "--max-quotient-dimension",
                        "2",
                        "--max-rows",
                        "2",
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            stored = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(stored["all_exact_gates_pass"])
            self.assertEqual(stored["linear_design_census"]["matrix_count"], 104)

    def test_verifier_rejects_small_receipt_as_full_registered_census(self) -> None:
        source = Path(__file__).with_name("identifiability_boundary.py")
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "small_result.json"
            self.assertEqual(
                main(
                    [
                        "--max-quotient-dimension",
                        "2",
                        "--max-rows",
                        "2",
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            receipt = verify(output, source, recompute=False)
            self.assertFalse(receipt["verified"])
            self.assertFalse(
                receipt["checks"]["registered_full_census_size"]
            )


if __name__ == "__main__":
    unittest.main()
