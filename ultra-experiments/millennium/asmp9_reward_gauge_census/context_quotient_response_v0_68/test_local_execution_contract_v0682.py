import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "asmp9_local_registration_v0682",
        HERE / "prepare_local_execution_registration_v0682.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_local_amendment_is_execution_only() -> None:
    value = json.loads(
        (HERE / "local_execution_resource_amendment_v0_68_2.json").read_text(
            encoding="utf-8"
        )
    )
    assert value["status"] == "frozen_prereveal_execution_only"
    assert value["workload"] == {
        "phase": "confirmation",
        "training": False,
        "model_changed": False,
        "job_universe_changed": False,
        "analysis_changed": False,
    }
    assert value["resource_contract"]["batch_size"] == 1
    assert value["resource_contract"]["checkpoint_every_records"] == 1
    assert value["scientific_protocol"]["modified"] is False
    assert value["scientific_amendment"]["modified"] is False


def test_registration_builder_binds_local_sources_and_holdout() -> None:
    source = (
        HERE / "prepare_local_execution_registration_v0682.py"
    ).read_text(encoding="utf-8")
    assert 'design.score_jobs(manifest, "confirmation")' in source
    assert "if len(jobs) != 528" in source
    assert "execution_resource_amendment" in source
    assert "construction_decision" in source
    assert "global_lane_authorized" in source
    assert "outcomes_read" in source
    assert "run_windows_guarded_v0_68_2.ps1" in source
    assert "post_run_windows_v0_68_2.ps1" in source


def test_hash_helper_streams_large_model_files(tmp_path: Path) -> None:
    module = _load_module()
    path = tmp_path / "sample.bin"
    path.write_bytes(b"abc" * 1_000_000)
    assert module.sha256(path) == (
        "f4096a131e7e6ebfa7a512b5c299e13b065df34d15624ee1202ab394cc4d7e90"
    )


def test_windows_wrapper_has_hard_limits_and_pid_scoped_cleanup() -> None:
    wrapper = (
        HERE / "windows" / "run_windows_guarded_v0_68_2.ps1"
    ).read_text(encoding="utf-8")
    cleanup = (
        HERE / "windows" / "post_run_windows_v0_68_2.ps1"
    ).read_text(encoding="utf-8")
    assert "JOB_OBJECT_LIMIT_JOB_MEMORY" in wrapper
    assert "CPU_RATE_HARD_CAP" in wrapper
    assert "gpu_temperature_abort" in wrapper
    assert "sustained_io_abort" in wrapper
    assert "wall_timeout" in wrapper
    assert "page_file_increase_mb" in wrapper
    assert "owned_pids" in cleanup
    assert "Stop-Process -Id $ownedProcessId" in cleanup
    assert "Stop-Process -Name" not in cleanup
    smoke = (HERE / "smoke_windows_wrapper_v0682.ps1").read_text(
        encoding="utf-8"
    )
    assert "runner-smoke" in smoke
    assert "analysis-smoke" in smoke
