from fractions import Fraction

from find_value_gap_witness import run


Q = Fraction


def test_complete_burned_grid_and_live_collision() -> None:
    result = run()
    assert result["status"] == "development_not_claim_eligible"
    assert result["experiments"] == 81
    assert (
        result["ordered_equal_value_pairs_with_positive_deficiency"] == 160
    )
    assert Q(
        result["largest_directional_deficiency_among_collisions"]
    ) == Q(15, 88)


def test_canonical_witness_is_exact_and_symmetric() -> None:
    witness = run()["canonical_witness"]
    assert witness == {
        "left_probabilities": ["1", "1/2"],
        "right_probabilities": ["1/2", "0"],
        "left_minimax_error": "1/3",
        "right_minimax_error": "1/3",
        "left_to_right_deficiency": "1/6",
        "right_to_left_deficiency": "1/6",
    }
