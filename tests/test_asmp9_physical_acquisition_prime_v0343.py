from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = (
    ROOT
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "physical_acquisition_v0_34"
)
WRAPPER = ROOT / "scripts" / "run_prime_asmp9_v0343_guarded.sh"
CLEANUP = ROOT / "scripts" / "post_run_prime_asmp9_v0343.sh"
PREPARER = EXPERIMENT / "prepare_prime_registration_v0_34_3.py"


def test_prime_shim_changes_only_registration_schema_and_entrypoint() -> None:
    source = (EXPERIMENT / "run_burned_pilot_prime_v0_34_3.py").read_text(
        encoding="utf-8"
    )
    assert (
        "asmp9_physical_acquisition_burned_pilot_registration_v0_34_3"
        in source
    )
    assert "sealed_runner.REGISTRATION_SCHEMA = PRIME_REGISTRATION_SCHEMA" in source
    assert "sealed_runner.main()" in source


def test_prime_wrapper_enforces_registered_cgroup_caps() -> None:
    source = WRAPPER.read_text(encoding="utf-8")
    for sentinel in (
        "MemoryMax=4096M",
        "MemorySwapMax=0",
        "CPUQuota=50%",
        " 50M",
        "RuntimeMaxSec=1800",
        "GPU_MEMORY_LIMIT_MB:-1600",
        "GPU_TEMPERATURE_LIMIT_C:-88",
        "GPU_CLEAN_START_CEILING_MB:-64",
    ):
        assert sentinel in source
    assert "--execution-class burned_pilot" in source
    assert "ASMP9_V034_HARD_CAP_ACTIVE" in source


def test_prime_wrapper_has_no_scientific_threshold_override() -> None:
    source = WRAPPER.read_text(encoding="utf-8")
    forbidden = (
        "--smoke-rows-per-type",
        "--temperature",
        "--top-p",
        "--top-k",
        "--seed-base",
        "--cold-start",
    )
    for token in forbidden:
        assert token not in source


def test_cleanup_is_owned_unit_scoped_and_checks_gpu_apps() -> None:
    source = CLEANUP.read_text(encoding="utf-8")
    assert 'systemctl kill --kill-who=all "${UNIT_NAME}.service"' in source
    assert "--query-compute-apps=pid,process_name,used_memory" in source
    assert not re.search(r"\bpkill\b|\bkillall\b", source)


def test_prime_registration_preparer_is_prereveal_and_compare_or_fail() -> None:
    source = PREPARER.read_text(encoding="utf-8")
    assert '"outcomes_consumed": False' in source
    assert '"query_count_before_registration": 0' in source
    assert "refusing to replace unequal registration" in source
    assert "registration_content_sha256" in source
