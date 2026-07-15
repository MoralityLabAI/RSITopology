"""Discover stable high-dimensional structures and test their utility.

Protocol v0.3 uses the cross-fitted top-r eigenspace of between-class scatter
as its primary lineage object.  The older covariance/Gram/Laplacian consensus
path remains executable for v0.2.2 compatibility, but every such receipt is
marked ``reported_ungated`` for v0.3 and is never consumed by the v0.3 object
gate.

The legacy geometric object is a cross-context consensus eigenspace of a frozen
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
from typing import Any, Iterable, Mapping, Sequence

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


@dataclass(frozen=True)
class CrossFittedLineageObject:
    """Cross-fitted high-dimensional lineage object and target-blind nulls."""

    object_kind: str
    gate_role: str
    rank: int
    basis_by_half: tuple[Array, Array]
    eigenvalues_by_half: tuple[Array, Array]
    lineage: Mapping[str, float | int]
    bootstrap_retentions: Array
    permutation_null_retentions: Array
    retention_lower_95: float
    permutation_null_retention_upper_95: float
    null_margin: float
    minimum_strict_margin: float
    passed: bool

    def receipt(self) -> dict[str, Any]:
        output = {
            "object_kind": self.object_kind,
            "gate_role": self.gate_role,
            "gate_eligible": self.gate_role == "primary",
            "rank": self.rank,
            "basis_by_half_sha256": [
                hashlib.sha256(np.asarray(basis, dtype="<f8").tobytes()).hexdigest()
                for basis in self.basis_by_half
            ],
            "eigenvalues_by_half": [values.tolist() for values in self.eigenvalues_by_half],
            "lineage": dict(self.lineage),
            "retention_statistic": "minimum_edge_worst_direction_retention",
            "retention_lower_95": self.retention_lower_95,
            "permutation_null_retention_upper_95": (
                self.permutation_null_retention_upper_95
            ),
            "null_margin": self.null_margin,
            "minimum_strict_margin": self.minimum_strict_margin,
            "pass_rule": "retention_lower_95 - permutation_null_retention_upper_95 > minimum_strict_margin",
            "passed": self.passed,
            "bootstrap_replicates": int(len(self.bootstrap_retentions)),
            "permutation_replicates": int(len(self.permutation_null_retentions)),
        }
        if self.gate_role == "matched_random_label_negative_control":
            output["random_family_retention_lower_95"] = self.retention_lower_95
        return output


@dataclass(frozen=True)
class PhaseOneLineageObjectsV03:
    """Primary v0.3 object, mandatory control, and legacy ungated report."""

    primary: CrossFittedLineageObject
    matched_random_label_negative_control: CrossFittedLineageObject
    covariance_gram_report: Mapping[str, Any]
    passed: bool

    def receipt(self) -> dict[str, Any]:
        return {
            "protocol_object_version": "spectral_bundle_discovery_v0_3",
            "primary": self.primary.receipt(),
            "matched_random_label_negative_control": (
                self.matched_random_label_negative_control.receipt()
            ),
            "covariance_gram": dict(self.covariance_gram_report),
            "passed": self.passed,
            "decision_rule": "primary and matched_random_label_negative_control must both pass; covariance_gram is reported_ungated",
        }


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


def _between_class_scatter_basis(
    features: Array,
    labels: Array,
    rank: int,
) -> tuple[Array, Array]:
    """Return the frozen top-r eigenspace of equally weighted class means."""

    values = np.asarray(features, dtype=np.float64)
    class_values = np.asarray(labels)
    if values.ndim != 2 or len(values) != len(class_values):
        raise ValueError("features must be a matrix with one label per row")
    if not np.all(np.isfinite(values)):
        raise ValueError("features must be finite")
    classes = np.unique(class_values)
    if len(classes) < 2:
        raise ValueError("between-class scatter requires at least two classes")
    maximum_rank = min(values.shape[1], len(classes) - 1)
    if rank < 1 or rank > maximum_rank:
        raise ValueError(
            f"rank must be between one and min(d, classes-1)={maximum_rank}"
        )
    means = np.vstack([np.mean(values[class_values == label], axis=0) for label in classes])
    centered = means - np.mean(means, axis=0, keepdims=True)
    scatter = centered.T @ centered / len(classes)
    eigenvalues, eigenvectors = np.linalg.eigh(scatter)
    order = np.argsort(eigenvalues)[::-1]
    selected = order[:rank]
    return eigenvectors[:, selected], np.maximum(eigenvalues[selected], 0.0)


def _validate_construction_halves(
    features: Array,
    labels: Sequence[Any],
    construction_halves: Sequence[Any],
) -> tuple[Array, Array, Array, tuple[Any, Any]]:
    values = np.asarray(features, dtype=np.float64)
    class_values = np.asarray(tuple(labels))
    half_values = np.asarray(tuple(construction_halves))
    if values.ndim != 2:
        raise ValueError("features must be a matrix")
    if not (len(values) == len(class_values) == len(half_values)):
        raise ValueError("features, labels, and construction_halves must align")
    halves = tuple(np.unique(half_values).tolist())
    if len(halves) != 2:
        raise ValueError("exactly two disjoint construction halves are required")
    class_sets = [set(np.unique(class_values[half_values == half]).tolist()) for half in halves]
    if class_sets[0] != class_sets[1]:
        raise ValueError("both construction halves must contain the same frozen classes")
    for half in halves:
        half_mask = half_values == half
        for label in class_sets[0]:
            if int(np.sum(half_mask & (class_values == label))) < 2:
                raise ValueError("each class needs at least two rows in each construction half")
    return values, class_values, half_values, halves


def _bootstrap_within_classes(
    features: Array,
    labels: Array,
    rng: np.random.Generator,
) -> tuple[Array, Array]:
    indices: list[int] = []
    for label in np.unique(labels):
        members = np.flatnonzero(labels == label)
        indices.extend(rng.choice(members, size=len(members), replace=True).tolist())
    selected = np.asarray(indices, dtype=np.int64)
    return features[selected], labels[selected]


def discover_between_class_scatter_object(
    *,
    features: Array,
    family_labels: Sequence[Any],
    construction_halves: Sequence[Any],
    rank: int,
    object_kind: str = "between_class_scatter",
    gate_role: str = "primary",
    replicates: int = 256,
    seed: int = 20260715,
    minimum_strict_margin: float = 0.02,
) -> CrossFittedLineageObject:
    """Build the v0.3 primary object and its cross-fitted permutation null.

    Outcomes are never accepted by this function. Bootstrap resampling occurs
    within frozen classes and halves. The permutation null independently
    shuffles class labels inside each half, preserving the real feature
    spectrum and every class count.
    """

    if gate_role not in {"primary", "matched_random_label_negative_control"}:
        raise ValueError("gate_role must name a registered v0.3 lineage role")
    if replicates < 32:
        raise ValueError("at least 32 bootstrap/permutation replicates are required")
    if not np.isfinite(minimum_strict_margin) or minimum_strict_margin < 0.0:
        raise ValueError("minimum_strict_margin must be finite and nonnegative")
    values, labels, half_values, halves = _validate_construction_halves(
        features, family_labels, construction_halves
    )
    half_masks = (half_values == halves[0], half_values == halves[1])
    half_features = (values[half_masks[0]], values[half_masks[1]])
    half_labels = (labels[half_masks[0]], labels[half_masks[1]])
    first_basis, first_eigenvalues = _between_class_scatter_basis(
        half_features[0], half_labels[0], rank
    )
    second_basis, second_eigenvalues = _between_class_scatter_basis(
        half_features[1], half_labels[1], rank
    )
    lineage = subspace_lineage(first_basis, second_basis)

    rng = np.random.default_rng(seed)
    bootstrap_retentions = np.empty(replicates, dtype=np.float64)
    permutation_retentions = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        boot_first_x, boot_first_y = _bootstrap_within_classes(
            half_features[0], half_labels[0], rng
        )
        boot_second_x, boot_second_y = _bootstrap_within_classes(
            half_features[1], half_labels[1], rng
        )
        boot_first, _ = _between_class_scatter_basis(
            boot_first_x, boot_first_y, rank
        )
        boot_second, _ = _between_class_scatter_basis(
            boot_second_x, boot_second_y, rank
        )
        bootstrap_retentions[replicate] = subspace_lineage(
            boot_first, boot_second
        )["worst_direction_retention"]

        perm_first_y = half_labels[0][rng.permutation(len(half_labels[0]))]
        perm_second_y = half_labels[1][rng.permutation(len(half_labels[1]))]
        perm_first, _ = _between_class_scatter_basis(
            half_features[0], perm_first_y, rank
        )
        perm_second, _ = _between_class_scatter_basis(
            half_features[1], perm_second_y, rank
        )
        permutation_retentions[replicate] = subspace_lineage(
            perm_first, perm_second
        )["worst_direction_retention"]

    lower = float(np.quantile(bootstrap_retentions, 0.05, method="linear"))
    null_upper = float(
        np.quantile(permutation_retentions, 0.95, method="linear")
    )
    margin = lower - null_upper
    return CrossFittedLineageObject(
        object_kind=object_kind,
        gate_role=gate_role,
        rank=rank,
        basis_by_half=(first_basis, second_basis),
        eigenvalues_by_half=(first_eigenvalues, second_eigenvalues),
        lineage=lineage,
        bootstrap_retentions=bootstrap_retentions,
        permutation_null_retentions=permutation_retentions,
        retention_lower_95=lower,
        permutation_null_retention_upper_95=null_upper,
        null_margin=margin,
        minimum_strict_margin=minimum_strict_margin,
        passed=bool(margin - minimum_strict_margin > 1e-12),
    )


def discover_lineage_objects_v03(
    *,
    features: Array,
    family_labels: Sequence[Any],
    construction_halves: Sequence[Any],
    negative_control_features: Array,
    negative_control_labels: Sequence[Any],
    negative_control_halves: Sequence[Any],
    rank: int,
    covariance_gram_output: Mapping[str, Any] | DiscoveryResult | None = None,
    replicates: int = 256,
    seed: int = 20260715,
    minimum_strict_margin: float = 0.02,
) -> PhaseOneLineageObjectsV03:
    """Construct all v0.3 Phase-1 objects without consuming outcomes."""

    primary = discover_between_class_scatter_object(
        features=features,
        family_labels=family_labels,
        construction_halves=construction_halves,
        rank=rank,
        object_kind="cross_fitted_between_class_scatter",
        gate_role="primary",
        replicates=replicates,
        seed=seed,
        minimum_strict_margin=minimum_strict_margin,
    )
    control = discover_between_class_scatter_object(
        features=negative_control_features,
        family_labels=negative_control_labels,
        construction_halves=negative_control_halves,
        rank=rank,
        object_kind="matched_random_label_between_class_scatter",
        gate_role="matched_random_label_negative_control",
        replicates=replicates,
        seed=seed + 1,
        minimum_strict_margin=minimum_strict_margin,
    )
    if isinstance(covariance_gram_output, DiscoveryResult):
        legacy: Mapping[str, Any] = asdict(covariance_gram_output)
    else:
        legacy = covariance_gram_output or {}
    covariance_report = {
        "object_kind": "covariance_gram_consensus",
        "status": "reported_ungated",
        "gate_eligible": False,
        "legacy_output": dict(legacy),
    }
    return PhaseOneLineageObjectsV03(
        primary=primary,
        matched_random_label_negative_control=control,
        covariance_gram_report=covariance_report,
        passed=bool(primary.passed and control.passed),
    )


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
    """Run the legacy v0.2.2 covariance/Gram path.

    Results retain their legacy pass fields for replay compatibility, while
    explicit v0.3 fields prohibit their use in any v0.3 gate.
    """

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
                "object_kind": "covariance_gram_consensus",
                "v0_3_status": "reported_ungated",
                "v0_3_gate_eligible": False,
                "bands": _band_receipts(bands),
                "band_occupancy_margins": _band_margin_receipts(
                    bands, config.consensus_occupancy
                ),
                "failure": "not_established_by_no_stable_high_rank_band",
            },
            policy={
                "passed": False,
                "status": "stopped_by_geometry_gate",
                "v0_3_status": "reported_ungated",
                "v0_3_gate_eligible": False,
            },
            direct_edit={
                "passed": False,
                "status": "stopped_by_geometry_gate",
                "v0_3_status": "reported_ungated",
                "v0_3_gate_eligible": False,
            },
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
            "object_kind": "covariance_gram_consensus",
            "v0_3_status": "reported_ungated",
            "v0_3_gate_eligible": False,
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
            "v0_3_status": "reported_ungated",
            "v0_3_gate_eligible": False,
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
            "v0_3_status": "reported_ungated",
            "v0_3_gate_eligible": False,
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
