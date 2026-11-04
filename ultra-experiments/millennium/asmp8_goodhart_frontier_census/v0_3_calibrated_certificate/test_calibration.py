from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from calibration import (
    calibration_radii,
    clopper_pearson_upper,
    error_populations,
    policy_coordinates,
    policy_registry,
    run_experiment,
)


HERE = Path(__file__).resolve().parent


def protocol():
    return json.loads((HERE / "protocol_v0_3.json").read_text(encoding="utf-8"))


def test_error_populations_obey_cap_and_rare_tail_is_live():
    populations = error_populations(64)
    assert set(populations) == {
        "diffuse_low_error",
        "heteroskedastic_proxy_coupled",
        "rare_top_tail",
    }
    assert all(np.max(np.abs(values)) <= 1 for values in populations.values())
    assert np.count_nonzero(populations["rare_top_tail"]) == 2


def test_policy_registry_is_normalized_proxy_improving_and_has_four_families():
    proxy = np.linspace(-0.5, 0.5, 64)
    policies = policy_registry(proxy, protocol())
    assert len(policies) == 20
    assert len({record["family"] for record in policies}) == 4
    assert all(abs(np.sum(record["policy"]) - 1) < 1e-12 for record in policies)
    assert all(record["proxy_gain"] > 0 for record in policies)


def test_dual_coordinates_match_direct_coupling_bound():
    spec = protocol()
    proxy = np.linspace(-0.5, 0.5, 64)
    p0 = np.full(64, 1 / 64)
    errors = error_populations(64)["heteroskedastic_proxy_coupled"]
    for record in policy_registry(proxy, spec):
        coordinates = policy_coordinates(record, p0)
        coupling = float(np.dot(record["policy"] - p0, errors))
        assert abs(coupling) <= np.mean(np.abs(errors)) * coordinates["movement_linf"] + 1e-12
        assert abs(coupling) <= np.sqrt(np.mean(errors**2)) * coordinates["movement_l2"] + 1e-12
        assert abs(coupling) <= np.max(np.abs(errors)) * coordinates["movement_l1"] + 1e-12


def test_calibration_is_seed_deterministic_and_bounded():
    errors = error_populations(64)["diffuse_low_error"]
    first = calibration_radii(errors, 32, 16, 7, 0.025)
    second = calibration_radii(errors, 32, 16, 7, 0.025)
    assert np.array_equal(first["delta_1"], second["delta_1"])
    assert np.array_equal(first["delta_2"], second["delta_2"])
    assert np.all((0 <= first["delta_1"]) & (first["delta_1"] <= 1))
    assert np.all((0 <= first["delta_2"]) & (first["delta_2"] <= 1))


def test_clopper_pearson_upper_boundary():
    assert 0 < clopper_pearson_upper(0, 100) < 0.04
    assert clopper_pearson_upper(100, 100) == 1


def test_small_replay_preserves_soundness_implication():
    result, conditions, rows, risks = run_experiment(protocol(), replicates_override=64)
    assert len(conditions) == 9
    assert len(rows) == 180
    assert len(risks) == 1260
    assert result["gates"]["G2_certificate_soundness"]["pass"]
    assert result["gates"]["G2_certificate_soundness"]["conditional_false_safe_count"] == 0
