"""Spectral FRC controls, including a high-frequency failure invisible to the eval."""
from __future__ import annotations

import numpy as np
import pytest

from HarmonicConsciousness.frc_calibration import (
    cycle_graph_laplacian, high_frequency_trigger, spectral_projector,
    choose_certified_band, tail_upper_bound, spectral_error_receipt,
    calibrate_step, simulate_calibration, verify_synthetic,
)


def test_synthetic_receipt_has_all_checks_and_sealed_high_frequency_failure():
    receipt = verify_synthetic()
    assert receipt["all_passed"], receipt["checks"]
    assert receipt["self_confirming"]["final_external_squared_error"] == pytest.approx(1)
    assert receipt["spectral_audit"]["final_external_squared_error"] < .002
    assert receipt["real_models_run"] == 0


def test_cycle_spectrum_psd_and_zero_mode():
    l = cycle_graph_laplacian(12)
    assert np.allclose(l.sum(axis=0), 0, atol=1e-12)
    assert np.min(np.linalg.eigvalsh(l)) > -1e-12
    assert np.linalg.eigvalsh(l)[-1] == pytest.approx(4)


def test_degenerate_eigenvalue_blocks_cannot_be_split():
    l = cycle_graph_laplacian(12)
    with pytest.raises(ValueError):
        spectral_projector(l, 2)
    g = spectral_projector(l, 3)
    assert g.rank == 3
    assert np.trace(g.projector) == pytest.approx(3)
    assert np.linalg.norm(g.projector @ g.projector - g.projector) < 1e-12
    assert g.next_eigenvalue > 0


def test_registered_selector_never_reads_the_hidden_error():
    l = cycle_graph_laplacian(12)
    band = choose_certified_band(l, 4.0, .05)
    band2 = choose_certified_band(l, 4.0, .05)
    assert band.rank == band2.rank
    assert band.rank == 12  # bound 4/lambda <= .05 cannot hold before full rank.
    assert tail_upper_bound(4, band.next_eigenvalue) == 0
    assert choose_certified_band(l, 0, .05).rank == 1


def test_modal_query_cost_is_distinct_from_point_query_complexity():
    l = cycle_graph_laplacian(12)
    e = high_frequency_trigger(12)
    low = simulate_calibration(l,e,strategy="self_confirming",generations=4,
                               rate=.25,registered_budget=4,tail_tolerance=.05,fixed_low_rank=3)
    rich = simulate_calibration(l,e,strategy="spectral_audit",generations=4,
                                rate=.25,registered_budget=4,tail_tolerance=.05)
    assert low["total_modal_queries"] == 12
    assert rich["total_modal_queries"] == 48
    assert low["final_external_squared_error"] == pytest.approx(1)
    assert rich["final_external_squared_error"] == pytest.approx(.75**8)


def test_high_mode_appears_perfect_to_the_low_mode_probe():
    l = cycle_graph_laplacian(12)
    high = high_frequency_trigger(12)
    band = spectral_projector(l, 3)
    receipt = spectral_error_receipt(l, high, band, 4)
    assert receipt["observed_band_squared_error"] < 1e-20
    assert receipt["external_squared_error"] == pytest.approx(1)
    assert receipt["hidden_tail_squared_error"] == pytest.approx(1)
    assert receipt["bound_covers_hidden_tail"]


def test_false_registered_smoothness_is_explicitly_detected_on_audit():
    l = cycle_graph_laplacian(12)
    high = high_frequency_trigger(12)
    low = spectral_projector(l, 3)
    invalid = spectral_error_receipt(l, high, low, .01)
    assert invalid["smoothness_assumption_verified_by_audit"] is False
    assert invalid["bound_covers_hidden_tail"] is False


def test_time_step_prediction_is_locally_exact_while_global_remains_wrong():
    l = cycle_graph_laplacian(12)
    high = high_frequency_trigger(12)
    low = spectral_projector(l, 3)
    nxt, rec = calibrate_step(l, high, low, .25, 4)
    assert np.allclose(nxt, high, atol=1e-10)
    assert rec["predicted_error_reduction"] == pytest.approx(rec["actual_external_error_reduction"],abs=1e-10)
    assert rec["self_predicted_remaining_error"] < 1e-20
    assert rec["actual_remaining_external_error"] == pytest.approx(1)


def test_spectral_tail_bound_is_exact_for_laplacian_eigenmode_at_boundary():
    l = cycle_graph_laplacian(12)
    band = spectral_projector(l, 11)
    e = high_frequency_trigger(12)
    obs = spectral_error_receipt(l, e, band, 4)
    assert obs["hidden_tail_squared_error"] == pytest.approx(1)
    assert obs["certified_tail_bound"] == pytest.approx(1)
    assert obs["bound_covers_hidden_tail"]


def test_orthogonal_coordinate_change_preserves_certificate_and_training():
    rng = np.random.default_rng(20261027)
    l = cycle_graph_laplacian(12)
    e = high_frequency_trigger(12)
    q, _ = np.linalg.qr(rng.normal(size=(12,12)))
    l2, e2 = q@l@q.T, q@e
    g1,g2 = spectral_projector(l,3),spectral_projector(l2,3)
    obs1,obs2 = spectral_error_receipt(l,e,g1,4),spectral_error_receipt(l2,e2,g2,4)
    for key in ("observed_band_squared_error","hidden_tail_squared_error", "external_squared_error", "spectral_roughness"):
        assert obs1[key] == pytest.approx(obs2[key], abs=1e-9)
    u1,_=calibrate_step(l,e,g1,.5,4)
    u2,_=calibrate_step(l2,e2,g2,.5,4)
    assert np.allclose(q@u1,u2,atol=1e-10)


def test_fail_closed_bad_operator_and_inputs():
    with pytest.raises(ValueError):
        spectral_projector(np.diag([1,-1]),1)
    with pytest.raises(ValueError):
        spectral_projector(np.array([[1.,1.],[0.,1.]]),1)
    with pytest.raises(ValueError):
        choose_certified_band(cycle_graph_laplacian(12),4,-.1)
    with pytest.raises(ValueError):
        simulate_calibration(cycle_graph_laplacian(12),high_frequency_trigger(12),
            strategy="bad",generations=2,rate=.2,registered_budget=4,tail_tolerance=.1)
    with pytest.raises(ValueError):
        tail_upper_bound(-1,1)


def test_isospectral_but_different_operator_cannot_substitute_its_band():
    rng = np.random.default_rng(5)
    l = cycle_graph_laplacian(12)
    g = spectral_projector(l, 3)
    q, _ = np.linalg.qr(rng.normal(size=(12,12)))
    rotated = q @ l @ q.T
    with pytest.raises(ValueError, match="different registered operator"):
        spectral_error_receipt(rotated, q @ high_frequency_trigger(12), g, 4)


def test_adaptive_eval_designer_uses_only_previous_measured_coefficients():
    from HarmonicConsciousness.frc_calibration import simulate_adaptive_band
    l = cycle_graph_laplacian(12)
    e = high_frequency_trigger(12)
    adaptive = simulate_adaptive_band(l, e, generations=12, rate=.25,
                                      registered_budget=4, tail_tolerance=.05)
    fixed = simulate_calibration(l, e, strategy="spectral_audit", generations=12,
                                 rate=.25, registered_budget=4, tail_tolerance=.05)
    assert adaptive["total_modal_queries"] < fixed["total_modal_queries"]
    assert adaptive["ranks"][0] == 12
    assert adaptive["ranks"][-1] < 12
    assert adaptive["all_budget_checks_passed"]
    assert adaptive["final_external_squared_error"] <= .05
    assert adaptive["final_external_squared_error"] >= fixed["final_external_squared_error"]
    assert all(row["predicted_error_reduction"] == pytest.approx(row["actual_external_error_reduction"],abs=1e-9)
               for row in adaptive["history"])


def test_invalid_adaptive_budget_detected_by_external_audit():
    from HarmonicConsciousness.frc_calibration import simulate_adaptive_band
    l = cycle_graph_laplacian(12)
    e = high_frequency_trigger(12)
    outcome = simulate_adaptive_band(l, e, generations=5, rate=.25,
                                     registered_budget=.01, tail_tolerance=.1)
    assert outcome["all_budget_checks_passed"] is False


def test_fresh_isotropic_baseline_measures_high_mode_at_same_query_cost():
    from HarmonicConsciousness.frc_calibration import random_equal_cost_control
    error = high_frequency_trigger(12)
    result = random_equal_cost_control(error, rank=3, generations=12, rate=.25,
                                       replicates=256, seed=20261027)
    duplicate = random_equal_cost_control(error, rank=3, generations=12, rate=.25,
                                          replicates=256, seed=20261027)
    assert result == duplicate
    assert result["scalar_linear_queries_per_replica"] == 36
    assert result["independent_tail_certificate"] is False
    assert result["analytic_isotropic_expected_squared_error"] == pytest.approx(
        (1-(2*.25-.25**2)*3/12)**12)
    assert result["mean_final_squared_error"] < .5
    assert abs(result["mean_final_squared_error"] - result["analytic_isotropic_expected_squared_error"]) < .07


def test_roughness_update_law_on_generic_nondegenerate_psd_operators():
    rng=np.random.default_rng(12)
    for n in (3,5,8):
        q,_=np.linalg.qr(rng.normal(size=(n,n)))
        l=q@np.diag(np.arange(1,n+1))@q.T
        e=rng.normal(size=n)
        for r in range(1,n+1):
            g=spectral_projector(l,r)
            coords=g.basis.T@e
            for eta in (.0,.13,.5,1.):
                enext=e-eta*g.projector@e
                r0=e@l@e
                r1=enext@l@enext
                removed=(2*eta-eta**2)*np.sum(g.eigenvalues[:r]*coords[:r]**2)
                assert r1 == pytest.approx(r0-removed,abs=1e-9)


def test_on_band_signal_is_where_spectral_design_wins_at_same_probe_budget():
    from HarmonicConsciousness.frc_calibration import random_equal_cost_control
    l = cycle_graph_laplacian(12)
    signal = spectral_projector(l,3).basis[:,1]
    low = simulate_calibration(l,signal,strategy="self_confirming",generations=12,
                               rate=.25,registered_budget=4,tail_tolerance=.05,fixed_low_rank=3)
    random = random_equal_cost_control(signal,rank=3,generations=12,rate=.25,replicates=256)
    assert low["total_modal_queries"] == random["scalar_linear_queries_per_replica"]
    assert low["final_external_squared_error"] == pytest.approx(.75**24, abs=1e-10)
    assert random["mean_final_squared_error"] > .15
