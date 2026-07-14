"""Discover stable high-dimensional spectral structures and test their utility.

The geometric object is a cross-context consensus eigenspace of a frozen
spectral band of the normalized, reliability-weighted sheaf Laplacian.  If
``P_{c,b}`` is the band projector for context ``c`` and band ``b``, the mean
projector

    M_b = (1 / C) sum_c P_{c,b}

has eigenvalues in [0, 1].  Its high-occupancy eigenspace is a Grassmannian
consensus: directions retained in the same band across prompts.  No dense
``d x d`` mean projector is materialized; a LinearOperator applies it through
the context bases.

Outcomes are used only after this geometry has been frozen.  Two downstream
uses are evaluated independently on leave-one-context-out folds:

* a KL-bounded exponential tilt over candidates (RL sampling policy);
* signed coordinates in the consensus basis (direct-edit proposal model).

Neither branch applies an edit or trains a model.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
from scipy.sparse import csr_matrix, issparse, spmatrix
from scipy.sparse.linalg import LinearOperator, eigsh
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler


Array = np.ndarray


@dataclass(frozen=True)
class DiscoveryConfig:
    spectral_bands: tuple[tuple[str, float, float], ...] = (
        ("low", 0.0, 0.25),
        ("middle", 0.25, 0.65),
        ("high", 0.65, 1.000001),
    )
    consensus_occupancy: float = 0.75
    minimum_consensus_rank: int = 8
    maximum_consensus_rank: int = 32
    ridge_alpha: float = 1.0
    policy_kl_cap: float = 0.05
    policy_min_mse_improvement: float = 0.05
    policy_min_standardized_return_uplift: float = 0.10
    edit_min_mse_improvement: float = 0.05
    edit_min_haar_advantage: float = 0.02
    haar_seed: int = 20260711
    chunk_rows: int = 64


@dataclass(frozen=True)
class ConsensusBand:
    name: str
    low: float
    high: float
    basis: Array
    occupancies: Array
    context_ranks: tuple[int, ...]

    @property
    def rank(self) -> int:
        return int(self.basis.shape[1])

    @property
    def minimum_occupancy(self) -> float:
        return float(np.min(self.occupancies)) if self.rank else 0.0


@dataclass(frozen=True)
class DiscoveryResult:
    geometry: dict
    policy: dict
    direct_edit: dict
    claim_boundary: str


def subspace_lineage(reference_basis: Array, current_basis: Array) -> dict:
    """Target-blind principal-angle lineage between orthonormal subspaces."""

    reference = np.asarray(reference_basis, dtype=np.float64)
    current = np.asarray(current_basis, dtype=np.float64)
    if reference.ndim != 2 or current.ndim != 2:
        raise ValueError("lineage bases must be matrices")
    if reference.shape[0] != current.shape[0]:
        raise ValueError("lineage bases must share one ambient edit space")
    reference_rank = int(reference.shape[1])
    current_rank = int(current.shape[1])
    if reference_rank == 0 or current_rank == 0:
        return {
            "rank_reference": reference_rank,
            "rank_current": current_rank,
            "mean_chordal_lineage": 0.0,
            "reference_recall": 0.0,
            "current_precision": 0.0,
            "worst_direction_retention": 0.0,
            "log_volume_retention": float(math.log(1e-8)),
            "maximum_principal_angle_degrees": 90.0,
        }
    singular_values = np.linalg.svd(reference.T @ current, compute_uv=False)
    singular_values = np.clip(singular_values, 0.0, 1.0)
    squared = singular_values**2
    shared = float(np.sum(squared))
    padded_reference = np.zeros(reference_rank, dtype=np.float64)
    padded_reference[: len(squared)] = squared
    return {
        "rank_reference": reference_rank,
        "rank_current": current_rank,
        "mean_chordal_lineage": shared / min(reference_rank, current_rank),
        "reference_recall": shared / reference_rank,
        "current_precision": shared / current_rank,
        "worst_direction_retention": float(np.min(padded_reference)),
        "log_volume_retention": float(np.mean(np.log(padded_reference + 1e-8))),
        "maximum_principal_angle_degrees": float(
            np.degrees(np.arccos(np.sqrt(np.min(padded_reference))))
        ),
    }


def _validate_laplacian(matrix: Array | spmatrix) -> Array | csr_matrix:
    if issparse(matrix):
        value = csr_matrix(matrix, dtype=np.float64)
        if value.shape[0] != value.shape[1]:
            raise ValueError("each Laplacian must be square")
        asymmetry = value - value.T
        if asymmetry.nnz and float(np.max(np.abs(asymmetry.data))) > 1e-9:
            raise ValueError("each Laplacian must be symmetric")
        dimension = value.shape[0]
        if dimension < 3:
            raise ValueError("edit space must have dimension at least three")
        smallest = float(eigsh(value, k=1, which="SA", return_eigenvectors=False)[0])
        if smallest < -1e-8:
            raise ValueError("each Laplacian must be positive semidefinite")
        scale = max(
            float(eigsh(value, k=1, which="LA", return_eigenvectors=False)[0]),
            1e-12,
        )
        return value / scale
    value = np.asarray(matrix, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("each Laplacian must be square")
    if not np.allclose(value, value.T, atol=1e-9):
        raise ValueError("each Laplacian must be symmetric")
    eigenvalues = np.linalg.eigvalsh(value)
    if eigenvalues[0] < -1e-8:
        raise ValueError("each Laplacian must be positive semidefinite")
    scale = max(float(eigenvalues[-1]), 1e-12)
    return value / scale


def _band_basis(
    matrix: Array | spmatrix,
    low: float,
    high: float,
    *,
    final: bool,
    solver_rank: int,
) -> Array:
    if issparse(matrix) or matrix.shape[0] > 512:
        k = min(solver_rank, matrix.shape[0] - 1)
        eigenvalues, eigenvectors = eigsh(matrix, k=k, which="SA", tol=1e-8)
        order = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[order]
        eigenvectors = eigenvectors[:, order]
    else:
        eigenvalues, eigenvectors = np.linalg.eigh(np.asarray(matrix))
    if final:
        mask = (eigenvalues >= low) & (eigenvalues <= high)
    else:
        mask = (eigenvalues >= low) & (eigenvalues < high)
    return eigenvectors[:, mask]


def _mean_projector_operator(bases: tuple[Array, ...], dimension: int) -> LinearOperator:
    def matvec(vector: Array) -> Array:
        value = np.asarray(vector, dtype=np.float64)
        total = np.zeros_like(value)
        for basis in bases:
            if basis.shape[1]:
                total += basis @ (basis.T @ value)
        return total / len(bases)

    def matmat(matrix: Array) -> Array:
        value = np.asarray(matrix, dtype=np.float64)
        total = np.zeros_like(value)
        for basis in bases:
            if basis.shape[1]:
                total += basis @ (basis.T @ value)
        return total / len(bases)

    return LinearOperator(
        (dimension, dimension), dtype=np.float64, matvec=matvec, matmat=matmat
    )


def discover_consensus_bands(
    laplacians: Mapping[str, Array | spmatrix], config: DiscoveryConfig
) -> dict[str, ConsensusBand]:
    if len(laplacians) < 3:
        raise ValueError("at least three prompt/context Laplacians are required")
    normalized = {key: _validate_laplacian(value) for key, value in laplacians.items()}
    dimensions = {value.shape[0] for value in normalized.values()}
    if len(dimensions) != 1:
        raise ValueError("all Laplacians must act on the same registered edit space")
    dimension = dimensions.pop()
    if dimension < 3:
        raise ValueError("edit space must have dimension at least three")
    output: dict[str, ConsensusBand] = {}
    for index, (name, low, high) in enumerate(config.spectral_bands):
        # For large/sparse operators, only the frozen low-frequency band is
        # admissible: eigsh computes it matrix-free. Reporting a partial
        # interior/high band as complete would be a spectral-selection bug.
        if index > 0 and any(issparse(value) or value.shape[0] > 512 for value in normalized.values()):
            bases = tuple(
                np.zeros((dimension, 0), dtype=np.float64) for _ in normalized.values()
            )
        else:
            bases = tuple(
                _band_basis(
                    value,
                    low,
                    high,
                    final=index == len(config.spectral_bands) - 1,
                    solver_rank=config.maximum_consensus_rank,
                )
                for value in normalized.values()
            )
        if not any(basis.shape[1] for basis in bases):
            output[name] = ConsensusBand(
                name=name,
                low=low,
                high=high,
                basis=np.zeros((dimension, 0), dtype=np.float64),
                occupancies=np.zeros(0, dtype=np.float64),
                context_ranks=tuple(0 for _ in bases),
            )
            continue
        operator = _mean_projector_operator(bases, dimension)
        k = min(config.maximum_consensus_rank, dimension - 1)
        values, vectors = eigsh(operator, k=k, which="LA", tol=1e-8)
        order = np.argsort(values)[::-1]
        values = np.clip(values[order], 0.0, 1.0)
        vectors = vectors[:, order]
        keep = values >= config.consensus_occupancy
        output[name] = ConsensusBand(
            name=name,
            low=low,
            high=high,
            basis=vectors[:, keep],
            occupancies=values[keep],
            context_ranks=tuple(int(basis.shape[1]) for basis in bases),
        )
    return output


def band_energy(vectors: Array, basis: Array, *, chunk_rows: int) -> Array:
    values = np.asarray(vectors, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != basis.shape[0]:
        raise ValueError("candidate vectors and band basis disagree")
    output = np.empty(values.shape[0], dtype=np.float64)
    for start in range(0, len(values), chunk_rows):
        stop = min(start + chunk_rows, len(values))
        block = values[start:stop]
        denominator = np.maximum(np.sum(block * block, axis=1), 1e-30)
        coordinates = block @ basis
        output[start:stop] = np.sum(coordinates * coordinates, axis=1) / denominator
    return output


def _fit_predict(train_x: Array, train_y: Array, test_x: Array, alpha: float) -> Array:
    scaler = StandardScaler().fit(train_x)
    model = Ridge(alpha=alpha).fit(scaler.transform(train_x), train_y)
    return model.predict(scaler.transform(test_x))


def _bounded_tilt(scores: Array, kl_cap: float) -> tuple[Array, float, float]:
    centered = np.asarray(scores, dtype=np.float64) - float(np.mean(scores))
    if np.max(np.abs(centered)) < 1e-12:
        weights = np.full(len(centered), 1.0 / len(centered))
        return weights, 0.0, 0.0

    def distribution(eta: float) -> tuple[Array, float]:
        logits = eta * centered
        logits -= float(np.max(logits))
        weights = np.exp(logits)
        weights /= float(np.sum(weights))
        kl = float(np.sum(weights * np.log(np.maximum(weights * len(weights), 1e-30))))
        return weights, kl

    low, high = 0.0, 1.0
    while distribution(high)[1] < kl_cap and high < 1e6:
        high *= 2.0
    for _ in range(60):
        midpoint = (low + high) / 2.0
        if distribution(midpoint)[1] <= kl_cap:
            low = midpoint
        else:
            high = midpoint
    weights, kl = distribution(low)
    return weights, float(low), kl


def _grouped_metrics(
    *,
    vectors: Array,
    baseline: Array,
    energy: Array,
    basis: Array,
    outcomes: Array,
    groups: Array,
    config: DiscoveryConfig,
) -> tuple[list[dict], Array]:
    folds: list[dict] = []
    edit_directions: list[Array] = []
    for group in np.unique(groups):
        test = groups == group
        train = ~test
        if int(np.sum(test)) < 2 or int(np.sum(train)) < 10:
            continue
        baseline_prediction = _fit_predict(
            baseline[train], outcomes[train], baseline[test], config.ridge_alpha
        )
        policy_train = np.column_stack((baseline[train], energy[train]))
        policy_test = np.column_stack((baseline[test], energy[test]))
        policy_prediction = _fit_predict(
            policy_train, outcomes[train], policy_test, config.ridge_alpha
        )
        base_mse = mean_squared_error(outcomes[test], baseline_prediction)
        policy_mse = mean_squared_error(outcomes[test], policy_prediction)
        weights, eta, kl = _bounded_tilt(
            policy_prediction - baseline_prediction, config.policy_kl_cap
        )
        return_uplift = float(weights @ outcomes[test] - np.mean(outcomes[test]))
        outcome_scale = max(float(np.std(outcomes[test], ddof=0)), 1e-12)
        standardized_uplift = return_uplift / outcome_scale
        realized_ic = (
            None
            if kl <= 1e-12
            else standardized_uplift / math.sqrt(2.0 * kl)
        )

        coordinates_train = vectors[train] @ basis
        coordinates_test = vectors[test] @ basis
        edit_train = np.column_stack((baseline[train], coordinates_train))
        edit_test = np.column_stack((baseline[test], coordinates_test))
        edit_prediction = _fit_predict(
            edit_train, outcomes[train], edit_test, config.ridge_alpha
        )
        edit_mse = mean_squared_error(outcomes[test], edit_prediction)

        baseline_scaler = StandardScaler().fit(baseline[train])
        baseline_model = Ridge(alpha=config.ridge_alpha).fit(
            baseline_scaler.transform(baseline[train]), outcomes[train]
        )
        residual = outcomes[train] - baseline_model.predict(
            baseline_scaler.transform(baseline[train])
        )
        coordinate_model = Ridge(alpha=config.ridge_alpha).fit(
            coordinates_train, residual
        )
        direction = basis @ coordinate_model.coef_
        direction /= max(float(np.linalg.norm(direction)), 1e-30)
        edit_directions.append(direction)
        folds.append(
            {
                "held_out_group": str(group),
                "baseline_mse": float(base_mse),
                "policy_mse": float(policy_mse),
                "policy_relative_mse_improvement": float(
                    (base_mse - policy_mse) / max(base_mse, 1e-30)
                ),
                "policy_return_uplift": return_uplift,
                "policy_return_uplift_standardized": standardized_uplift,
                "policy_realized_ic": realized_ic,
                "heldout_outcome_standard_deviation": outcome_scale,
                "policy_eta": eta,
                "policy_kl": kl,
                "edit_mse": float(edit_mse),
                "edit_relative_mse_improvement": float(
                    (base_mse - edit_mse) / max(base_mse, 1e-30)
                ),
            }
        )
    if not folds:
        raise ValueError("no valid grouped folds")
    proposal = np.mean(edit_directions, axis=0)
    proposal /= max(float(np.linalg.norm(proposal)), 1e-30)
    return folds, proposal


def _haar_basis(dimension: int, rank: int, seed: int) -> Array:
    rng = np.random.default_rng(seed)
    matrix = rng.normal(size=(dimension, rank))
    return np.linalg.qr(matrix, mode="reduced")[0]


def evaluate_discovery(
    *,
    laplacians: Mapping[str, Array],
    vectors: Array,
    baseline_covariates: Array,
    outcomes: Array,
    groups: Iterable[str],
    config: DiscoveryConfig = DiscoveryConfig(),
) -> DiscoveryResult:
    values = np.asarray(vectors, dtype=np.float64)
    baseline = np.asarray(baseline_covariates, dtype=np.float64)
    target = np.asarray(outcomes, dtype=np.float64)
    group_values = np.asarray(tuple(groups))
    if not (len(values) == len(baseline) == len(target) == len(group_values)):
        raise ValueError("candidate arrays must have the same row count")
    bands = discover_consensus_bands(laplacians, config)
    eligible = [
        band for band in bands.values() if band.rank >= config.minimum_consensus_rank
    ]
    geometry_passed = bool(eligible)
    if not geometry_passed:
        return DiscoveryResult(
            geometry={
                "passed": False,
                "bands": _band_receipts(bands),
                "band_occupancy_margins": _band_margin_receipts(
                    bands, config.consensus_occupancy
                ),
                "failure": "not_established_by_no_stable_high_rank_band",
            },
            policy={"passed": False, "status": "stopped_by_geometry_gate"},
            direct_edit={"passed": False, "status": "stopped_by_geometry_gate"},
            claim_boundary=_claim_boundary(),
        )

    # The hypothesis is specifically about approximate sections: select the
    # lowest-frequency eligible band in the frozen protocol order. Choosing a
    # favorable band by outcomes would violate the pre-reveal boundary.
    selected = eligible[0]
    energy = band_energy(values, selected.basis, chunk_rows=config.chunk_rows)
    folds, proposal = _grouped_metrics(
        vectors=values,
        baseline=baseline,
        energy=energy,
        basis=selected.basis,
        outcomes=target,
        groups=group_values,
        config=config,
    )
    haar = _haar_basis(values.shape[1], selected.rank, config.haar_seed)
    haar_energy = band_energy(values, haar, chunk_rows=config.chunk_rows)
    haar_folds, _ = _grouped_metrics(
        vectors=values,
        baseline=baseline,
        energy=haar_energy,
        basis=haar,
        outcomes=target,
        groups=group_values,
        config=config,
    )
    policy_mse = float(np.mean([row["policy_relative_mse_improvement"] for row in folds]))
    policy_uplift = float(np.mean([row["policy_return_uplift"] for row in folds]))
    policy_uplift_standardized = float(
        np.mean([row["policy_return_uplift_standardized"] for row in folds])
    )
    realized_ic_values = [
        float(row["policy_realized_ic"])
        for row in folds
        if row["policy_realized_ic"] is not None
    ]
    mean_realized_ic = (
        None if not realized_ic_values else float(np.mean(realized_ic_values))
    )
    max_kl = float(np.max([row["policy_kl"] for row in folds]))
    edit_mse = float(np.mean([row["edit_relative_mse_improvement"] for row in folds]))
    haar_edit_mse = float(
        np.mean([row["edit_relative_mse_improvement"] for row in haar_folds])
    )
    occupancy_margin = selected.minimum_occupancy - config.consensus_occupancy
    return DiscoveryResult(
        geometry={
            "passed": True,
            "selected_band": selected.name,
            "selected_rank": selected.rank,
            "minimum_occupancy": selected.minimum_occupancy,
            "consensus_occupancy_margin": occupancy_margin,
            "occupancy_margin_band": selected.name,
            "low_occupancy_margin_warning": occupancy_margin < 0.10,
            "bands": _band_receipts(bands),
            "band_occupancy_margins": _band_margin_receipts(
                bands, config.consensus_occupancy
            ),
        },
        policy={
            "passed": bool(
                policy_mse >= config.policy_min_mse_improvement
                and policy_uplift_standardized
                >= config.policy_min_standardized_return_uplift
                and max_kl <= config.policy_kl_cap + 1e-9
            ),
            "mean_relative_mse_improvement": policy_mse,
            "mean_heldout_return_uplift": policy_uplift,
            "mean_standardized_heldout_return_uplift": policy_uplift_standardized,
            "mean_realized_ic": mean_realized_ic,
            "realized_ic_role": "descriptive_cap_sensitivity_not_primary_gate",
            "maximum_kl": max_kl,
            "folds": folds,
        },
        direct_edit={
            "passed": bool(
                edit_mse >= config.edit_min_mse_improvement
                and edit_mse - haar_edit_mse >= config.edit_min_haar_advantage
            ),
            "mean_relative_mse_improvement": edit_mse,
            "matched_rank_haar_improvement": haar_edit_mse,
            "haar_advantage": edit_mse - haar_edit_mse,
            "proposal_direction_sha256": hashlib.sha256(
                np.asarray(proposal, dtype="<f8").tobytes()
            ).hexdigest(),
            "proposal_direction": proposal.tolist(),
            "status": "proposal_only_not_applied",
        },
        claim_boundary=_claim_boundary(),
    )


def _band_receipts(bands: Mapping[str, ConsensusBand]) -> dict:
    return {
        name: {
            "rank": band.rank,
            "minimum_occupancy": band.minimum_occupancy,
            "occupancies": band.occupancies.tolist(),
            "context_ranks": list(band.context_ranks),
            "interval": [band.low, band.high],
        }
        for name, band in bands.items()
    }


def _band_margin_receipts(
    bands: Mapping[str, ConsensusBand], threshold: float
) -> dict:
    return {
        name: {
            "band": name,
            "rank": band.rank,
            "minimum_occupancy": band.minimum_occupancy,
            "consensus_occupancy_margin": band.minimum_occupancy - threshold,
            "low_occupancy_margin_warning": (
                band.minimum_occupancy - threshold < 0.10
            ),
        }
        for name, band in bands.items()
    }


def _claim_boundary() -> str:
    return (
        "Synthetic/offline evidence only. A passing result identifies a stable spectral "
        "bundle that improves grouped prediction and bounded candidate allocation. It does "
        "not establish real-model self-improvement, apply a weight edit, or demonstrate RSI."
    )


def write_result(path: Path, result: DiscoveryResult, config: DiscoveryConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    packages = {}
    for name in ("numpy", "scipy", "scikit-learn"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "not-installed"
    payload = {
        "receipt_environment": {
            "python_version": sys.version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "packages": packages,
        },
        "config": asdict(config),
        **asdict(result),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
