from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from interaction_tomography import (
    analyze_boolean_census,
    canonical_orbit_map,
    conditional_walsh_mismatches_for_table,
    design_dimension,
    fwht,
    greedy_minimum_cost_basis,
    intervention_rows,
    main,
    matrix_rank_mod,
    minimum_structural_cost,
    parity_truth_mask,
    protocol_registration_checks,
    signed_parent_assignment_maps,
    subsets_upto,
    walsh_coefficients,
    walsh_signature,
)


class InteractionTomographyTests(unittest.TestCase):
    def test_subset_and_design_dimensions(self) -> None:
        for n in range(1, 7):
            for order in range(n + 1):
                expected = sum(math.comb(n, size) for size in range(order + 1))
                self.assertEqual(len(subsets_upto(n, order)), expected)
                self.assertEqual(design_dimension(n, order), expected)

    def test_exact_design_rank_on_small_grid(self) -> None:
        for n in range(1, 6):
            for order in range(n + 1):
                rows = intervention_rows(n, order)
                self.assertEqual(
                    matrix_rank_mod([row["vector"] for row in rows]),
                    design_dimension(n, order),
                )

    def test_minimum_cost_zeta_basis(self) -> None:
        for n in range(1, 7):
            for order in range(min(n, 3) + 1):
                basis = greedy_minimum_cost_basis(n, order)
                self.assertEqual(basis["row_count"], design_dimension(n, order))
                self.assertEqual(
                    basis["total_cost"], minimum_structural_cost(n, order)
                )
                self.assertEqual(
                    basis["all_positive_assignment_count"],
                    design_dimension(n, order),
                )

    def test_fwht_and_parity_support(self) -> None:
        n = 4
        character = 0b1011
        truth_mask = parity_truth_mask(n, character)
        coefficients = walsh_coefficients(truth_mask, n)
        self.assertEqual(coefficients[character], 1 << n)
        self.assertEqual(
            [value for index, value in enumerate(coefficients) if index != character],
            [0] * ((1 << n) - 1),
        )
        self.assertEqual(fwht(fwht([1, -1, 1, 1])), (4, -4, 4, 4))

    def test_conditional_walsh_identity_on_all_three_parent_tables(self) -> None:
        mismatch_count = sum(
            conditional_walsh_mismatches_for_table(truth_mask, 3)
            for truth_mask in range(1 << (1 << 3))
        )
        self.assertEqual(mismatch_count, 0)

    def test_parent_gauge_parity_classes(self) -> None:
        canonical, metadata = canonical_orbit_map(3)
        self.assertEqual(metadata["group_size"], math.factorial(3) * (1 << 3))
        top = parity_truth_mask(3, 0b111, sign=1)
        negative_top = parity_truth_mask(3, 0b111, sign=-1)
        degree_one = parity_truth_mask(3, 0b001)
        degree_two = parity_truth_mask(3, 0b011)
        self.assertEqual(canonical[top], canonical[negative_top])
        self.assertNotEqual(canonical[degree_one], canonical[degree_two])
        self.assertEqual(walsh_signature(top, 3, 2), walsh_signature(negative_top, 3, 2))

    def test_two_parent_complete_census_thresholds(self) -> None:
        census = analyze_boolean_census(2)
        self.assertEqual(census["conditional_walsh_identity_mismatch_count"], 0)
        self.assertEqual(census["labelled_identifiability_threshold"], 2)
        self.assertEqual(census["quotient_identifiability_threshold"], 1)
        self.assertTrue(all(fixture["passed"] for fixture in census["parity_fixtures"]))

    def test_signed_parent_maps_are_unique(self) -> None:
        for n in range(1, 5):
            maps = signed_parent_assignment_maps(n)
            self.assertEqual(len(maps), math.factorial(n) * (1 << n))
            self.assertEqual(len(set(maps)), len(maps))

    def test_runner_rejects_output_alias_before_enumeration(self) -> None:
        protocol = Path(__file__).with_name("protocol_v0_1.json")
        with self.assertRaisesRegex(ValueError, "aliases"):
            main(["--protocol", str(protocol), "--output", str(protocol)])

    def test_protocol_registration_fields_are_bound(self) -> None:
        protocol_path = Path(__file__).with_name("protocol_v0_1.json")
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        self.assertTrue(all(protocol_registration_checks(protocol).values()))
        mutated = copy.deepcopy(protocol)
        mutated["registered_grid"]["boolean_quotient_census"]["n"] = [2, 3]
        self.assertFalse(all(protocol_registration_checks(mutated).values()))


if __name__ == "__main__":
    unittest.main()
