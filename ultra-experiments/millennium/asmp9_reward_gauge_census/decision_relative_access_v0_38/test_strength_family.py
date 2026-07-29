from fractions import Fraction as Q

from explore_strength_family import build_result


def test_registered_burned_strengths_match_half_gap() -> None:
    result = build_result()
    for row in result["rows"]:
        assert Q(row["target_relative_deficiency"]) == Q(row["half_gap"])
        assert Q(row["ordinary_target_deficiency"]) == Q(row["half_gap"])


def test_value_gap_is_strictly_coarser_on_burned_strengths() -> None:
    result = build_result()
    for row in result["rows"]:
        assert Q(row["optimized_value_gap"]) < Q(
            row["target_relative_deficiency"]
        )

