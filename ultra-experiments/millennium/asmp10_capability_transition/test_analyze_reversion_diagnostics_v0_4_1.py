from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location(
    "reversion_diagnostics", HERE / "analyze_reversion_diagnostics_v0_4_1.py"
)
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def row(step, test_accuracy=0.95, test_loss=0.1, train_loss=0.01, gradient_norm=0.01):
    return {
        "step": step,
        "test_accuracy": test_accuracy,
        "test_loss": test_loss,
        "train_accuracy": 1.0,
        "train_loss": train_loss,
        "gradient_norm": gradient_norm,
    }


def test_isolated_spike_is_an_excursion_not_persistent_reversion():
    rows = [row(step) for step in range(100, 1600, 100)]
    rows[10] = row(1100, test_accuracy=0.70, test_loss=1.0, train_loss=1.0, gradient_norm=10.0)
    result = MODULE.summarize_rows("synthetic", rows)
    assert result["old_detector_excursion_count"] == 1
    assert result["spike_count_after_crossing"] == 1
    event = result["events"][0]
    assert event["duration_evaluations"] == 1
    assert event["recovered_at_next_evaluation"] is True
    assert event["posthoc_spike_rule_passed"] is True
    assert event["crosses_proposed_down_threshold"] is True


def test_spike_is_not_sufficient_for_threshold_excursion():
    rows = [row(step) for step in range(100, 1600, 100)]
    rows[10] = row(1100, test_accuracy=0.95, test_loss=0.1, train_loss=1.0, gradient_norm=10.0)
    result = MODULE.summarize_rows("synthetic", rows)
    assert result["old_detector_excursion_count"] == 0
    assert result["spike_count_after_crossing"] == 1
    assert result["spikes_not_starting_old_detector_excursions"] == 1


def test_no_crossing_has_no_post_crossing_diagnostics():
    rows = [row(step, test_accuracy=0.5, test_loss=2.0) for step in range(100, 700, 100)]
    result = MODULE.summarize_rows("synthetic", rows)
    assert result["first_sustained_crossing_step"] is None
    assert result["events"] == []
