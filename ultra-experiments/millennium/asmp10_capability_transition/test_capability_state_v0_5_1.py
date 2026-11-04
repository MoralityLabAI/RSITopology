from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("capability_state", HERE / "capability_state_v0_5_1.py")
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def row(step, accuracy=0.1, loss=2.0):
    return {"step": step, "test_accuracy": accuracy, "test_loss": loss}


def regular_grid():
    return [row(step) for step in range(0, 15001, 25)]


def set_range(rows, start, end, accuracy, loss):
    for item in rows:
        if start <= item["step"] <= end:
            item["test_accuracy"] = accuracy
            item["test_loss"] = loss


def test_hysteresis_ignores_single_grid_excursion():
    rows = regular_grid()
    set_range(rows, 1000, 15000, 0.95, 0.1)
    set_range(rows, 5000, 5000, 0.1, 3.0)
    result = MODULE.classify(rows, 25, memorization_step=100)
    assert result["label"] == "delayed_horizon_stable"
    assert [event["kind"] for event in result["events"]] == ["entry"]


def test_persistent_adverse_dwell_creates_one_exit_and_reentry():
    rows = regular_grid()
    set_range(rows, 1000, 15000, 0.95, 0.1)
    set_range(rows, 5000, 5100, 0.1, 3.0)
    result = MODULE.classify(rows, 25, memorization_step=100)
    assert [event["kind"] for event in result["events"]] == ["entry", "exit", "entry"]
    assert result["stable_entry_onset_step"] == 5125


def test_cadence_gate_detects_cycle_hidden_from_sparse_grid():
    rows = regular_grid()
    set_range(rows, 1000, 15000, 0.95, 0.1)
    # Five adverse 25-step evaluations trigger the primary exit. The 50/100
    # grids do not see the same consecutive evidence.
    set_range(rows, 5025, 5125, 0.1, 3.0)
    replay = MODULE.cadence_replay(rows, memorization_step=100)
    assert replay["instrument_status"] == "cadence_dependent"
    assert replay["gate_decision"] == "not_evaluated"
    assert replay["event_order_agreement"] is False


def test_two_sided_labels_are_distinct():
    early = regular_grid()
    delayed = regular_grid()
    set_range(early, 400, 15000, 0.95, 0.1)
    set_range(delayed, 1000, 15000, 0.95, 0.1)
    assert MODULE.classify(early, 25, 100)["label"] == "early_horizon_stable"
    assert MODULE.classify(delayed, 25, 100)["label"] == "delayed_horizon_stable"

