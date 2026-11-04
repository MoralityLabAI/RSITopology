from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("spike_consequences", HERE / "analyze_spike_consequences_v0_4_2.py")
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_real_burned_table_has_registered_counts_and_no_gate():
    result = MODULE.analyze(HERE / "pilot_artifacts_v0_4" / "runs")
    assert result["status"] == "posthoc_descriptive_no_gate"
    assert result["aggregate"]["post_crossing_spikes"] == 15
    assert result["aggregate"]["old_detector_excursion_spikes"] == 7
    assert result["aggregate"]["nonexcursion_spikes"] == 8
    assert len(result["records"]) == 15


def test_markdown_is_total_over_records():
    result = MODULE.analyze(HERE / "pilot_artifacts_v0_4" / "runs")
    text = MODULE.markdown(result)
    assert "no gate consumes this table" in text
    for record in result["records"]:
        assert record["run_id"] in text
        assert f"| {record['step']} |" in text

