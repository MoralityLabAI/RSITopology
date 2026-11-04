from fractions import Fraction as Q

from run_reward_fixture import ALL_QUERIES, build_result


def row_by_queries(result: dict, queries: tuple[str, ...]) -> dict:
    return next(row for row in result["rows"] if row["queries"] == list(queries))


def test_gauge_query_is_target_null_but_expanded_relevant() -> None:
    result = build_result()
    target_only = row_by_queries(
        result, ("q_target_0", "q_target_1")
    )
    full = row_by_queries(result, ALL_QUERIES)
    assert target_only["target_relative_deficiency"] == "0"
    assert target_only["expanded_parameter_deficiency"] == "1/2"
    assert full["target_relative_deficiency"] == "0"
    assert full["expanded_parameter_deficiency"] == "0"


def test_each_target_query_is_necessary_at_zero_tolerance() -> None:
    result = build_result()
    without_target_0 = row_by_queries(
        result, ("q_target_1", "q_gauge_shift")
    )
    without_target_1 = row_by_queries(
        result, ("q_target_0", "q_gauge_shift")
    )
    assert Q(without_target_0["target_relative_deficiency"]) > 0
    assert Q(without_target_1["target_relative_deficiency"]) > 0


def test_constant_shift_representatives_are_explicit() -> None:
    result = build_result()
    for representatives in result["raw_reward_representatives"].values():
        base, shifted = representatives
        assert [right - left for left, right in zip(base, shifted)] == [1, 1, 1]

