from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("capability_state_v052", HERE / "capability_state_v0_5_2.py")
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def row(step, accuracy=0.1, loss=2.0):
    return {"step": step, "test_accuracy": accuracy, "test_loss": loss}


def grid():
    return [row(step) for step in range(0, 15001, 25)]


def set_range(rows, start, end, accuracy, loss):
    for item in rows:
        if start <= item["step"] <= end:
            item["test_accuracy"] = accuracy
            item["test_loss"] = loss


def capable_grid():
    rows = grid()
    set_range(rows, 1000, 15000, 0.95, 0.1)
    return rows


def test_sub_200_step_burned_like_excursion_cannot_exit_primary_state():
    rows = capable_grid()
    set_range(rows, 5000, 5175, 0.1, 3.0)
    result = MODULE.classify(rows, 25, memorization_step=100)
    assert result["event_kind_order"] == ["entry"]
    assert result["final_state"] == "capable"


def test_300_step_adverse_dwell_exits_and_then_reenters():
    rows = capable_grid()
    set_range(rows, 5000, 5300, 0.1, 3.0)
    result = MODULE.classify(rows, 25, memorization_step=100)
    assert result["event_kind_order"] == ["entry", "exit", "entry"]
    assert result["events"][1]["confirmation_step"] == 5300


def test_dwell_fragility_is_not_misreported_as_evidence():
    rows = capable_grid()
    set_range(rows, 5000, 5275, 0.1, 3.0)
    replay = MODULE.dwell_replay(rows, memorization_step=100)
    assert replay["instrument_status"] == "dwell_fragile"
    assert replay["gate_decision"] == "not_evaluated"
    assert replay["event_order_agreement"] is False


def test_cadence_hidden_cycle_remains_a_separate_failure_mode():
    rows = capable_grid()
    set_range(rows, 5025, 5325, 0.1, 3.0)
    replay = MODULE.cadence_replay(rows, memorization_step=100)
    assert replay["instrument_status"] == "cadence_dependent"
    assert replay["gate_decision"] == "not_evaluated"


def test_clean_stable_trajectory_passes_both_measurement_checks():
    rows = capable_grid()
    validity = MODULE.measurement_validity(rows, memorization_step=100)
    assert validity["instrument_status"] == "valid"
    assert validity["gate_decision"] == "continue"


def test_entry_is_conjunctive_and_exit_is_disjunctive():
    rows = grid()
    # Accuracy alone is insufficient to enter.
    set_range(rows, 1000, 2000, 0.95, 0.8)
    assert MODULE.classify(rows, 25, 100)["events"] == []

    rows = capable_grid()
    # Sustained loss failure alone is sufficient to exit.
    set_range(rows, 5000, 5300, 0.95, 0.8)
    assert "exit" in MODULE.classify(rows, 25, 100)["event_kind_order"]

