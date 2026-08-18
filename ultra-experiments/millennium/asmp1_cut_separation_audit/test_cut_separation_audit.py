from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from cut_separation_audit import (
    analytic_cut_aliasing_counterexample,
    build_result,
    canonical_hyperoctahedral_table,
    exact_rank,
    main,
    necessity_counterexample,
    q_is_identifiable,
    singleton_observation_matrix,
    structural_hypergraph_audit,
    sufficiency_counterexample,
)


class CutSeparationAuditTests(unittest.TestCase):
    def test_exact_rank_and_factorization_criterion(self) -> None:
        observation = ((Fraction(1), Fraction(0)),)
        same_q = ((Fraction(2), Fraction(0)),)
        larger_q = ((Fraction(0), Fraction(1)),)
        self.assertEqual(exact_rank(observation), 1)
        self.assertTrue(q_is_identifiable(observation, same_q))
        self.assertFalse(q_is_identifiable(observation, larger_q))

    def test_necessity_counterexample(self) -> None:
        result = necessity_counterexample()
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(result["observation_rank"], 1)
        self.assertEqual(result["full_excitation_rank"], 8)
        self.assertEqual(result["q_rank"], 1)

    def test_structural_hypergraph_passes_three_strong_readings(self) -> None:
        result = structural_hypergraph_audit(3)
        self.assertTrue(result["coverage"])
        self.assertTrue(result["pair_separation"])
        self.assertTrue(result["full_incidence_rank"])
        self.assertEqual(result["incidence_matrix"], ((1, 0, 0), (0, 1, 0), (0, 0, 1)))

    def test_full_cut_replacement_still_leaves_analytic_aliasing(self) -> None:
        result = analytic_cut_aliasing_counterexample()
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(result["natural_observation_rank"], 2)
        self.assertEqual(result["natural_observation_nullity"], 2)
        self.assertEqual(result["shared_natural_outputs"], (0, 1))
        self.assertEqual(result["replacement_probe_count"], 25)

    def test_singleton_design_has_exact_higher_order_kernel(self) -> None:
        design = singleton_observation_matrix(3)
        self.assertEqual(len(design), 7)
        self.assertEqual(exact_rank(design), 4)

    def test_sufficiency_counterexample(self) -> None:
        result = sufficiency_counterexample()
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(result["observation_rank"], 4)
        self.assertEqual(result["observation_nullity"], 4)
        self.assertEqual(result["left_registered_laws"], result["right_registered_laws"])
        self.assertGreater(result["minimum_bernoulli_variance"], Fraction(1, 5))
        self.assertEqual(
            result["certified_open_blind_interval"],
            (Fraction(-1, 25), Fraction(1, 25)),
        )

    def test_parent_gauge_canonicalization_is_stable(self) -> None:
        result = sufficiency_counterexample()
        self.assertTrue(result["gates"]["mechanisms_are_not_parent_gauge_equivalent"])
        left = tuple(
            Fraction(value)
            for value in (
                Fraction(1, 2),
                Fraction(1, 2),
                Fraction(1, 2),
                Fraction(1, 2),
                Fraction(1, 2),
                Fraction(1, 2),
                Fraction(1, 2),
                Fraction(1, 2),
            )
        )
        self.assertEqual(
            canonical_hyperoctahedral_table(left, 3),
            left,
        )

    def test_result_and_json_receipt(self) -> None:
        result = build_result()
        self.assertTrue(result["all_exact_gates_pass"])
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "result.json"
            self.assertEqual(main(["--output", str(output)]), 0)
            stored = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(stored["all_exact_gates_pass"])
            self.assertEqual(
                stored["verdict"],
                "cut_separation_conjecture_not_well_posed_as_a_closed_iff",
            )


if __name__ == "__main__":
    unittest.main()
