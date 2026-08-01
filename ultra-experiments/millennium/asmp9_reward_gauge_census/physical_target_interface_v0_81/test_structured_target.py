from __future__ import annotations

import json
from pathlib import Path

import pytest

from structured_target import (
    ARM_DELTAS,
    analyze,
    build_candidates,
    choice_probability,
    exact_wellposedness,
    record_seed,
    route_margin,
    run_registered,
    structured_hellinger_bound,
)


ROOT = Path(__file__).resolve().parent


def config() -> dict[str, object]:
    return json.loads((ROOT / "config_v0_81.json").read_text(encoding="utf-8"))


def rounded_population_rows(cfg: dict[str, object]) -> list[dict[str, object]]:
    samples = int(cfg["samples_per_query"])
    rows = []
    for candidate in build_candidates(cfg):
        for beta_value in cfg["betas"]:  # type: ignore[union-attr]
            beta = float(beta_value)
            probability = choice_probability(float(candidate.target_margin), beta)
            rows.append(
                {
                    "context": candidate.context,
                    "split": candidate.split,
                    "arm": candidate.arm,
                    "beta": beta,
                    "samples": samples,
                    "successes": round(samples * probability),
                    "empirical_probability": round(samples * probability) / samples,
                    "target_margin": float(candidate.target_margin),
                }
            )
    return rows


def test_exact_target_and_offset_object_is_live() -> None:
    cfg = config()
    wellposed = exact_wellposedness(cfg)
    assert wellposed["pass"] is True
    offsets = {arm: float(route_margin(ARM_DELTAS[arm])) for arm in cfg["decoder_arm_offsets"]}  # type: ignore[index]
    assert offsets == {"base": 0.0, "nongauge_minus": -2.0, "nongauge_plus": 2.0}


def test_structured_robust_bound_has_positive_margin() -> None:
    bound = structured_hellinger_bound(config())
    assert bound["decoder_samples_per_context"] == 4608
    assert bound["hellinger_union_bound"] < 1e-10
    assert 0.045 < bound["accumulated_tv_penalty"] < 0.046
    assert bound["robustified_bound"] < bound["threshold"]
    assert bound["pass"] is True


def test_population_rounding_passes_all_scientific_gates() -> None:
    cfg = config()
    result = analyze(cfg, build_candidates(cfg), rounded_population_rows(cfg))
    assert all(result["gates"][gate]["pass"] for gate in ("W0", "D0", "R0", "L0", "M0"))
    assert result["gates"]["R0"]["maximum_absolute_margin_error"] < 0.01


def test_wrong_registered_offset_fails_decoder_admission() -> None:
    cfg = config()
    cfg["decoder_arm_offsets"]["nongauge_plus"] = 1.5  # type: ignore[index]
    result = analyze(cfg, build_candidates(cfg), rounded_population_rows(cfg))
    assert result["gates"]["D0"]["registered_offsets_exact"] is False
    assert result["gates"]["D0"]["pass"] is False


def test_fresh_seed_namespace_differs_from_v080() -> None:
    new = record_seed(8101, "v081|holdout_low|base|beta=1")
    old = record_seed(8001, "holdout_low|base|beta=1")
    assert new != old


def test_registered_run_is_byte_replayable(tmp_path: Path) -> None:
    cfg = config()
    first = tmp_path / "first"
    second = tmp_path / "second"
    run_registered(cfg, first)
    run_registered(cfg, second)
    for name in ("response_rows.jsonl", "result.json", "run_receipt.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_output_directory_is_write_once(tmp_path: Path) -> None:
    cfg = config()
    output = tmp_path / "run"
    run_registered(cfg, output)
    with pytest.raises(FileExistsError):
        run_registered(cfg, output)

