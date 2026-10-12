from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = (
    ROOT
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "physical_acquisition_v0_34"
)
ADAPTER = EXPERIMENT / "analyze_burned_pilot_prime_v0_34_4.py"
WRAPPER = ROOT / "scripts" / "run_prime_asmp9_analysis_v0344_guarded.sh"


def test_prime_analysis_adapter_changes_only_registration_schema() -> None:
    source = ADAPTER.read_text(encoding="utf-8")
    assert (
        "asmp9_physical_acquisition_burned_pilot_registration_v0_34_3"
        in source
    )
    assert "sealed_runner.REGISTRATION_SCHEMA = PRIME_REGISTRATION_SCHEMA" in source
    assert "sealed_analyzer.REGISTRATION_SCHEMA = PRIME_REGISTRATION_SCHEMA" in source
    assert "sealed_analyzer.run(sealed_analyzer.parse_args())" in source


def test_prime_analysis_wrapper_enforces_cpu_resource_caps() -> None:
    source = WRAPPER.read_text(encoding="utf-8")
    for sentinel in (
        'findmnt -T "${RUN_ROOT}"',
        "MemoryMax=4096M",
        "MemorySwapMax=0",
        "CPUQuota=50%",
        " 50M",
        "RuntimeMaxSec=600",
        "ASMP9_V034_ANALYSIS_CAP_ACTIVE",
    ):
        assert sentinel in source


def test_prime_analysis_wrapper_has_no_scientific_overrides() -> None:
    source = WRAPPER.read_text(encoding="utf-8")
    for forbidden in (
        "--threshold",
        "--alpha",
        "--confidence",
        "--quantile",
        "--seed",
        "--temperature",
    ):
        assert forbidden not in source
    assert "--analysis-json" in source
    assert "--report" in source
