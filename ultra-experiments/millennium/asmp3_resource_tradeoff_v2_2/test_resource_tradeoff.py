from __future__ import annotations

from math import ceil
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from resource_tradeoff import (
    build_result,
    ceil_log2,
    exhaustive_cover_audit,
    query_values,
    resource_row,
)
from verify_resource_tradeoff import verify


HERE = Path(__file__).resolve().parent


def test_invalid_parameters_are_rejected() -> None:
    with pytest.raises(ValueError):
        ceil_log2(0)
    for count, queries in ((0, 1), (8, 0), (8, 9)):
        with pytest.raises(ValueError):
            resource_row(count, queries)


def test_ceil_log2_is_exact() -> None:
    expected = {1: 0, 2: 1, 3: 2, 4: 2, 5: 3, 8: 3, 9: 4}
    assert {value: ceil_log2(value) for value in expected} == expected


def test_covering_lower_bound_and_bits_are_exact() -> None:
    for count in (2, 3, 8, 17, 1024):
        for queries in {1, min(3, count), max(1, count - 1), count}:
            row = resource_row(count, queries)
            assert row["minimum_message_count"] == ceil(count / queries)
            assert row["minimum_communication_bits"] == ceil_log2(
                row["minimum_message_count"]
            )
            assert row["capacity_sufficient"]
            assert row["one_fewer_bit_insufficient"]


def test_partition_protocol_attains_every_point_in_constant_space() -> None:
    for count in (7, 16, 1 << 20):
        for queries in (1, min(5, count), count):
            row = resource_row(count, queries)
            histogram = row["constructive_block_size_histogram"]
            assert sum(int(size) * blocks for size, blocks in histogram.items()) == count
            assert row["constructive_block_count"] == row["minimum_message_count"]
            assert row["constructive_max_block_size"] <= queries
            assert row["perfect_completeness"]


def test_endpoint_tradeoffs_are_index_or_recomputation() -> None:
    for bits in range(1, 25):
        count = 1 << bits
        assert resource_row(count, 1)["minimum_communication_bits"] == bits
        assert resource_row(count, count)["minimum_communication_bits"] == 0


def test_power_of_two_frontier_has_b_plus_log_q_equal_n() -> None:
    for bits in range(1, 17):
        count = 1 << bits
        for exponent in range(bits + 1):
            queries = 1 << exponent
            row = resource_row(count, queries)
            assert row["minimum_communication_bits"] + exponent == bits


def test_nonpower_query_values_are_registered() -> None:
    values = query_values(10)
    assert all(1 <= value <= 1024 for value in values)
    assert {3, 5, 7, 10, 1023} <= set(values)


def test_small_cover_frontiers_are_exhaustively_minimal() -> None:
    rows = exhaustive_cover_audit()
    assert len(rows) == 35
    assert all(not row["cover_below_minimum_exists"] for row in rows)
    assert all(row["cover_at_minimum_exists"] for row in rows)
    assert all(row["minimum_certified"] for row in rows)


def test_honest_search_cost_remains_separate() -> None:
    for count in (8, 1024):
        for queries in (1, count // 2, count):
            row = resource_row(count, queries)
            assert row["honest_marker_search_queries"] == count
            assert row["verifier_ideal_semantic_queries"] == queries


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["frontier_rows"]) == 433
    assert len(result["exhaustive_cover_rows"]) == 35
    assert len(result["robust_replication_rows"]) == 4
    assert result["certified"]
    assert len(result["gates"]) == 10
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_interface_and_universal_boundaries_are_explicit() -> None:
    theorem = (HERE / "RESOURCE_TRADEOFF_THEOREM_v2_2.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v2_2.md").read_text(encoding="utf-8")
    assert "Interface firewall" in theorem
    assert "honest Find cost" in theorem
    assert "universal matching lower bounds" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
