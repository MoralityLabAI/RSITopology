from pathlib import Path

import pytest

from rsi_topology.qwen_support_recovery import cyclic_window, load_protocol


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocols" / "qwen08_between_class_support_recovery_v0_1.json"


def test_support_recovery_is_target_blind_and_cannot_certify():
    value = load_protocol(PROTOCOL)
    assert value["outcomes_consumed"] is False
    assert value["weight_mutation_performed"] is False
    assert value["new_invariant_levels"] is False
    assert "cannot receive lineage_certified or holonomy_clean" in value["claim_boundary"]
    assert value["primary_pool"]["bootstrap_and_permutation_replicates"] == 128


def test_cyclic_windows_are_complete_and_deterministic():
    assert cyclic_window(7, 2) == ("shard-07", "shard-00")
    assert cyclic_window(3, 4) == (
        "shard-03",
        "shard-04",
        "shard-05",
        "shard-06",
    )
    assert cyclic_window(5, 8) == tuple(f"shard-{index:02d}" for index in range(8))
    with pytest.raises(ValueError):
        cyclic_window(0, 0)
