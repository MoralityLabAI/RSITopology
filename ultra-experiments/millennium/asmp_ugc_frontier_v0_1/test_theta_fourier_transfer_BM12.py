"""BM-12: independent exhaustive validation of theta Walsh transfer formula."""
from fractions import Fraction
from itertools import product
import unittest

from theta_fourier_transfer_BM12 import (
    theta_path_game, theta_walsh_transfer, theta_walsh_direct,
    theta_walsh_from_counts, theta_observation_counts,
    gain_equality_signature, transfer_manifest,
)
from theta_shared_cycle_erasure import theta_counts, THETA_SHIFTS
from diamond_weighted_fourier_BM10 import counts_for, SHIFT


class ThetaFourierTransferTests(unittest.TestCase):
    def test_all_walsh_indices_q4_diamond_match_independent_BM10_census(self):
        for gains in ((0,1,2),(0,1,0),(0,0,0),(0,2,3)):
            lengths=(1,2,2)
            game=theta_path_game(4,lengths,gains)
            counts=theta_observation_counts(game)
            for subset in range(1<<sum(lengths)):
                predicted=theta_walsh_transfer(4,lengths,gains,subset)
                observed=theta_walsh_from_counts(
                    counts,subset,4**game.vertices)
                self.assertEqual(predicted,observed)
                if subset in (0,1,31):
                    self.assertEqual(predicted,theta_walsh_direct(game,subset))
        self.assertEqual(theta_observation_counts(
            theta_path_game(4,(1,2,2),(0,1,2))),counts_for(SHIFT))

    def test_all_indices_q4_and_q8_K23_match_original_theta_oracle(self):
        for q,gains in ((4,(0,1,2)),(4,(0,1,0)),(8,(0,1,2))):
            lengths=(2,2,2)
            game=theta_path_game(q,lengths,gains)
            counts=theta_observation_counts(game)
            for subset in range(64):
                self.assertEqual(theta_walsh_transfer(q,lengths,gains,subset),
                                 theta_walsh_from_counts(
                                     counts,subset,q**game.vertices))
        self.assertEqual(theta_observation_counts(
            theta_path_game(8,(2,2,2),(0,1,2))),
            theta_counts(8,THETA_SHIFTS))

    def test_custom_path_lengths_random_gains_agree_with_direct_enumeration(self):
        for lengths,gains,q in (
            ((1,3,2),(0,1,2),4),
            ((1,2,3),(2,2,1),4),
            ((3,2,2),(0,1,3),4),
            ((1,1,3),(1,2,2),8),
            ((1,1),(0,1),4),
        ):
            game=theta_path_game(q,lengths,gains)
            counts=theta_observation_counts(game)
            for subset in range(1<<sum(lengths)):
                self.assertEqual(theta_walsh_transfer(q,lengths,gains,subset),
                                 theta_walsh_from_counts(
                                     counts,subset,q**game.vertices))

    def test_gain_partition_determines_every_walsh_coefficient(self):
        scenarios=(
            ((0,1,2),(3,6,7)),
            ((0,1,0),(7,4,7)),
            ((0,0,0),(6,6,6)),
        )
        for gains_a,gains_b in scenarios:
            self.assertEqual(gain_equality_signature(gains_a),
                             gain_equality_signature(gains_b))
            for lengths in ((1,2,2),(2,2,2),(1,3,2)):
                for S in range(1<<sum(lengths)):
                    self.assertEqual(
                        theta_walsh_transfer(8,lengths,gains_a,S),
                        theta_walsh_transfer(8,lengths,gains_b,S))

    def test_large_alphabet_queries_without_vertex_label_enumeration(self):
        q=1<<12
        lengths=(12,10,9)
        gains=(0,1,2)
        game=theta_path_game(q,lengths,gains)
        self.assertEqual(game.vertices,2+11+9+8)
        self.assertEqual(len(game.edges),31)
        for subset in (0,1,(1<<31)-1,0x55555555,0x11111111):
            a=theta_walsh_transfer(q,lengths,gains,subset)
            self.assertTrue(-1<=a<=1)
        manifest=transfer_manifest(q,lengths,gains)
        self.assertEqual(manifest["evaluated_alphabet_states"],0)
        self.assertEqual(manifest["coefficient_subsets_max"],8)
        self.assertEqual(manifest["gain_partition"],(0,1,2))

    def test_two_path_parallel_edge_special_case(self):
        for q in (2,4,8):
            for gains in ((0,0),(0,1)):
                game=theta_path_game(q,(1,1),gains)
                for subset in range(4):
                    self.assertEqual(theta_walsh_transfer(q,(1,1),gains,subset),
                                     theta_walsh_direct(game,subset))

    def test_validation_and_expected_full_BM09_fourier_support(self):
        manifest=transfer_manifest(4,(2,2,2),(0,1,2))
        self.assertEqual((manifest["vertices"],manifest["edges"]),(5,6))
        self.assertEqual(manifest["full_walsh"],"0")
        with self.assertRaises(ValueError):
            theta_walsh_transfer(3,(2,2,2),(0,1,2),63)
        with self.assertRaises(ValueError):
            theta_walsh_transfer(4,(2,2,2),(0,1,2),64)
        with self.assertRaises(ValueError):
            theta_walsh_transfer(4,(2,0,2),(0,1,2),2)
        with self.assertRaises(ValueError):
            theta_path_game(4,(2,2),(1,))
        with self.assertRaises(ValueError):
            theta_walsh_from_counts((1,2,3),0,4)


if __name__=="__main__":
    unittest.main()
