from __future__ import annotations

import json
import numpy as np
from scipy.sparse import csr_matrix
from types import SimpleNamespace

from rsi_topology.discovery import (
    DiscoveryConfig,
    discover_consensus_bands,
    evaluate_discovery,
    subspace_lineage,
    write_result,
)
from rsi_topology.jspace_bridge import load_operator_bundle, sha256_file, write_operator_bundle
from rsi_topology.synthetic import build_fixture, build_sparse_fixture


def test_consensus_recovers_planted_high_dimensional_band() -> None:
    fixture = build_fixture(
        seed=11,
        contexts=6,
        candidates_per_context=32,
        dimension=32,
        planted_rank=8,
    )
    config = DiscoveryConfig(minimum_consensus_rank=6, maximum_consensus_rank=16)
    band = discover_consensus_bands(fixture.laplacians, config)["low"]
    overlap = np.linalg.norm(fixture.planted_basis.T @ band.basis, ord="fro") ** 2
    overlap /= max(band.rank, 1)

    assert band.rank >= 8
    assert band.minimum_occupancy >= config.consensus_occupancy
    assert overlap > 0.9


def test_common_rotation_preserves_occupancy_and_has_cosine_squared_shape() -> None:
    common = dict(
        seed=13,
        contexts=4,
        candidates_per_context=16,
        dimension=24,
        planted_rank=6,
        geometry_noise=0.08,
    )
    reference = build_fixture(**common, lineage_rotation_radians=0.0)
    halfway = build_fixture(**common, lineage_rotation_radians=np.pi / 4)
    rotated = build_fixture(**common, lineage_rotation_radians=np.pi / 2)
    config = DiscoveryConfig(minimum_consensus_rank=4, maximum_consensus_rank=12)
    reference_low = discover_consensus_bands(reference.laplacians, config)["low"]
    halfway_low = discover_consensus_bands(halfway.laplacians, config)["low"]
    rotated_low = discover_consensus_bands(rotated.laplacians, config)["low"]
    halfway_lineage = subspace_lineage(reference_low.basis, halfway_low.basis)
    lineage = subspace_lineage(reference_low.basis, rotated_low.basis)

    assert np.array_equal(reference.vectors, halfway.vectors)
    assert np.array_equal(reference.outcomes, halfway.outcomes)
    assert np.array_equal(reference.vectors, rotated.vectors)
    assert np.array_equal(reference.outcomes, rotated.outcomes)
    assert reference_low.rank == rotated_low.rank
    assert np.allclose(reference_low.occupancies, halfway_low.occupancies, atol=1e-12)
    assert np.allclose(reference_low.occupancies, rotated_low.occupancies, atol=1e-12)
    assert abs(halfway_lineage["mean_chordal_lineage"] - 0.5) < 0.01
    assert lineage["mean_chordal_lineage"] < 0.01
    assert lineage["worst_direction_retention"] < 0.01
    assert lineage["maximum_principal_angle_degrees"] > 85.0


def test_planted_signal_passes_but_outcome_null_does_not() -> None:
    config = DiscoveryConfig(
        minimum_consensus_rank=6,
        maximum_consensus_rank=16,
        chunk_rows=32,
    )
    signal = build_fixture(
        seed=23,
        contexts=6,
        candidates_per_context=64,
        dimension=32,
        planted_rank=8,
        outcome_signal=True,
    )
    planted = evaluate_discovery(
        laplacians=signal.laplacians,
        vectors=signal.vectors,
        baseline_covariates=signal.baseline_covariates,
        outcomes=signal.outcomes,
        groups=signal.groups,
        config=config,
    )
    null_fixture = build_fixture(
        seed=23,
        contexts=6,
        candidates_per_context=64,
        dimension=32,
        planted_rank=8,
        outcome_signal=False,
    )
    null = evaluate_discovery(
        laplacians=null_fixture.laplacians,
        vectors=null_fixture.vectors,
        baseline_covariates=null_fixture.baseline_covariates,
        outcomes=null_fixture.outcomes,
        groups=null_fixture.groups,
        config=config,
    )

    assert planted.geometry["passed"]
    assert planted.policy["passed"]
    assert planted.direct_edit["passed"]
    assert null.geometry["passed"]
    assert not null.policy["passed"]
    assert not null.direct_edit["passed"]
    assert planted.policy["maximum_kl"] <= config.policy_kl_cap + 1e-9
    assert planted.policy["mean_realized_ic"] > 0
    assert planted.policy["realized_ic_role"] == (
        "descriptive_cap_sensitivity_not_primary_gate"
    )
    assert "consensus_occupancy_margin" in planted.geometry
    assert planted.geometry["occupancy_margin_band"] == planted.geometry[
        "selected_band"
    ]
    assert set(planted.geometry["band_occupancy_margins"]) == {
        "low",
        "middle",
        "high",
    }


def test_no_stable_high_rank_band_stops_downstream_claims() -> None:
    fixture = build_fixture(
        seed=41,
        contexts=5,
        candidates_per_context=24,
        dimension=24,
        planted_rank=6,
        geometry_noise=1.0,
    )
    config = DiscoveryConfig(
        consensus_occupancy=0.98,
        minimum_consensus_rank=12,
        maximum_consensus_rank=16,
    )
    result = evaluate_discovery(
        laplacians=fixture.laplacians,
        vectors=fixture.vectors,
        baseline_covariates=fixture.baseline_covariates,
        outcomes=fixture.outcomes,
        groups=fixture.groups,
        config=config,
    )

    assert not result.geometry["passed"]
    assert result.policy["status"] == "stopped_by_geometry_gate"
    assert result.direct_edit["status"] == "stopped_by_geometry_gate"


def test_sparse_high_dimensional_backend_uses_low_band_only() -> None:
    fixture = build_fixture(
        seed=53,
        contexts=5,
        candidates_per_context=16,
        dimension=40,
        planted_rank=10,
    )
    config = DiscoveryConfig(minimum_consensus_rank=8, maximum_consensus_rank=16)
    sparse = {key: csr_matrix(value) for key, value in fixture.laplacians.items()}
    bands = discover_consensus_bands(sparse, config)

    assert bands["low"].rank >= 10
    assert bands["middle"].rank == 0
    assert bands["high"].rank == 0


def test_sparse_signal_and_shuffled_transport_null_separate() -> None:
    config = DiscoveryConfig(minimum_consensus_rank=8, maximum_consensus_rank=16)
    stable = build_sparse_fixture(
        seed=67,
        contexts=6,
        candidates_per_context=32,
        dimension=96,
        planted_rank=12,
    )
    stable_result = evaluate_discovery(
        laplacians=stable.laplacians,
        vectors=stable.vectors,
        baseline_covariates=stable.baseline_covariates,
        outcomes=stable.outcomes,
        groups=stable.groups,
        config=config,
    )
    shuffled = build_sparse_fixture(
        seed=67,
        contexts=6,
        candidates_per_context=32,
        dimension=96,
        planted_rank=12,
        shuffle_low_space=True,
    )
    shuffled_result = evaluate_discovery(
        laplacians=shuffled.laplacians,
        vectors=shuffled.vectors,
        baseline_covariates=shuffled.baseline_covariates,
        outcomes=shuffled.outcomes,
        groups=shuffled.groups,
        config=config,
    )

    assert stable_result.geometry["passed"]
    assert stable_result.policy["passed"]
    assert stable_result.direct_edit["passed"]
    assert not shuffled_result.geometry["passed"]


def test_sparse_geometry_noise_zero_is_bit_identical_and_positive_noise_moves_space() -> None:
    common = dict(
        seed=71,
        contexts=3,
        candidates_per_context=8,
        dimension=32,
        planted_rank=6,
    )
    default = build_sparse_fixture(**common)
    explicit_zero = build_sparse_fixture(**common, geometry_noise=0.0)
    noisy = build_sparse_fixture(**common, geometry_noise=0.2)

    assert np.array_equal(default.vectors, explicit_zero.vectors)
    assert np.array_equal(default.outcomes, explicit_zero.outcomes)
    for key in default.laplacians:
        assert np.array_equal(
            default.laplacians[key].toarray(),
            explicit_zero.laplacians[key].toarray(),
        )
    assert any(
        not np.array_equal(
            default.laplacians[key].toarray(), noisy.laplacians[key].toarray()
        )
        for key in default.laplacians
    )


def test_result_receipt_records_environment(tmp_path) -> None:
    fixture = build_fixture(
        seed=79,
        contexts=4,
        candidates_per_context=24,
        dimension=24,
        planted_rank=6,
    )
    config = DiscoveryConfig(minimum_consensus_rank=4, maximum_consensus_rank=12)
    result = evaluate_discovery(
        laplacians=fixture.laplacians,
        vectors=fixture.vectors,
        baseline_covariates=fixture.baseline_covariates,
        outcomes=fixture.outcomes,
        groups=fixture.groups,
        config=config,
    )
    path = tmp_path / "result.json"
    write_result(path, result, config)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["receipt_environment"]["python_version"]
    assert set(payload["receipt_environment"]["packages"]) == {
        "numpy",
        "scipy",
        "scikit-learn",
    }


def _fake_operator(prompt: str, dimension: int = 6):
    vertex_ids = ("v0", "v1")
    sheaf = SimpleNamespace(
        vertex_ids=vertex_ids,
        vertex_dims={"v0": dimension // 2, "v1": dimension - dimension // 2},
        vertex_slices={"v0": slice(0, dimension // 2), "v1": slice(dimension // 2, dimension)},
        total_vertex_dim=dimension,
        edges=(SimpleNamespace(edge_id="e0"),),
    )
    return SimpleNamespace(
        prompt_id=prompt,
        norm=0.25,
        sheaf=sheaf,
        laplacian=csr_matrix(np.diag(np.linspace(0.0, 1.0, dimension))),
        largest_eigenvalue=1.0,
        naturality_defect=0.0,
    )


def test_jspace_operator_bundle_is_write_once_and_common_space_checked(tmp_path) -> None:
    protocol = tmp_path / "protocol.json"
    protocol.write_text('{"version":"test"}\n', encoding="utf-8")
    operators = [_fake_operator(f"prompt-{index}") for index in range(3)]
    bundle = tmp_path / "operators.npz"
    manifest = write_operator_bundle(
        bundle,
        operators,
        candidate_sites=["v1"],
        source_protocol_path=protocol,
    )
    loaded_manifest, matrices = load_operator_bundle(
        bundle, expected_sha256=sha256_file(bundle)
    )

    assert loaded_manifest == manifest
    assert len(matrices) == 3
    assert all(matrix.shape == (6, 6) for matrix in matrices.values())
    with np.testing.assert_raises(FileExistsError):
        write_operator_bundle(
            bundle,
            operators,
            candidate_sites=["v1"],
            source_protocol_path=protocol,
        )
    mixed = [*operators[:2], _fake_operator("prompt-x", dimension=8)]
    with np.testing.assert_raises(ValueError):
        write_operator_bundle(
            tmp_path / "mixed.npz",
            mixed,
            candidate_sites=["v1"],
            source_protocol_path=protocol,
        )
