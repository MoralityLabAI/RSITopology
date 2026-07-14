"""Planted and null controls for spectral-bundle discovery."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm
from scipy.sparse import csr_matrix, diags


@dataclass(frozen=True)
class SyntheticFixture:
    laplacians: dict[str, np.ndarray | csr_matrix]
    vectors: np.ndarray
    baseline_covariates: np.ndarray
    outcomes: np.ndarray
    groups: np.ndarray
    planted_basis: np.ndarray
    planted_direction: np.ndarray


def build_fixture(
    *,
    seed: int = 20260711,
    contexts: int = 10,
    candidates_per_context: int = 96,
    dimension: int = 48,
    planted_rank: int = 12,
    geometry_noise: float = 0.015,
    lineage_rotation_radians: float = 0.0,
    outcome_signal: bool = True,
) -> SyntheticFixture:
    if not 2 <= planted_rank < dimension:
        raise ValueError("planted_rank must lie between two and dimension")
    rng = np.random.default_rng(seed)
    base_frame = np.linalg.qr(rng.normal(size=(dimension, dimension)))[0]
    planted = base_frame[:, :planted_rank]
    if not 0.0 <= lineage_rotation_radians <= np.pi / 2:
        raise ValueError("lineage_rotation_radians must lie in [0, pi/2]")
    if lineage_rotation_radians > 0 and 2 * planted_rank > dimension:
        raise ValueError("lineage rotation requires dimension >= 2 * planted_rank")
    common_rotation = None
    if lineage_rotation_radians > 0:
        coordinate_rotation = np.eye(dimension, dtype=np.float64)
        cosine = np.cos(lineage_rotation_radians)
        sine = np.sin(lineage_rotation_radians)
        for index in range(planted_rank):
            partner = planted_rank + index
            coordinate_rotation[index, index] = cosine
            coordinate_rotation[index, partner] = -sine
            coordinate_rotation[partner, index] = sine
            coordinate_rotation[partner, partner] = cosine
        common_rotation = base_frame @ coordinate_rotation @ base_frame.T
    direct = planted @ rng.normal(size=planted_rank)
    direct /= np.linalg.norm(direct)
    eigenvalues = np.concatenate(
        (
            np.linspace(0.04, 0.20, planted_rank),
            np.linspace(0.35, 0.62, (dimension - planted_rank) // 2),
            np.linspace(
                0.72,
                1.0,
                dimension - planted_rank - (dimension - planted_rank) // 2,
            ),
        )
    )
    laplacians: dict[str, np.ndarray] = {}
    rows = []
    baselines = []
    outcomes = []
    groups = []
    nuisance_direction = base_frame[:, -1]
    for context in range(contexts):
        skew = rng.normal(size=(dimension, dimension))
        skew = skew - skew.T
        rotation = expm(geometry_noise * skew / np.sqrt(dimension))
        frame = rotation @ base_frame
        if common_rotation is not None:
            frame = common_rotation @ frame
        laplacians[f"context-{context:02d}"] = (
            frame @ np.diag(eigenvalues) @ frame.T
        )
        for _ in range(candidates_per_context):
            norm = rng.uniform(0.25, 1.0)
            vector = rng.normal(size=dimension)
            vector *= norm / np.linalg.norm(vector)
            j_visibility = float((nuisance_direction @ vector) ** 2)
            nuisance = rng.normal()
            energy = float(np.sum((planted.T @ vector) ** 2) / (norm**2))
            signed = float(direct @ vector) / norm
            if outcome_signal:
                outcome = 1.4 * energy + 0.8 * signed + 0.25 * j_visibility
            else:
                outcome = 0.25 * j_visibility
            outcome += 0.15 * nuisance + 0.08 * rng.normal()
            rows.append(vector)
            baselines.append([norm, j_visibility, nuisance])
            outcomes.append(outcome)
            groups.append(f"context-{context:02d}")
    return SyntheticFixture(
        laplacians=laplacians,
        vectors=np.asarray(rows),
        baseline_covariates=np.asarray(baselines),
        outcomes=np.asarray(outcomes),
        groups=np.asarray(groups),
        planted_basis=planted,
        planted_direction=direct,
    )


def build_sparse_fixture(
    *,
    seed: int = 20260711,
    contexts: int = 8,
    candidates_per_context: int = 96,
    dimension: int = 384,
    planted_rank: int = 32,
    shuffle_low_space: bool = False,
    outcome_signal: bool = True,
    geometry_noise: float = 0.0,
) -> SyntheticFixture:
    """Large sparse control with an exactly known coordinate spectral bundle.

    ``geometry_noise=0`` preserves the frozen v0.2 random-number stream exactly.
    Positive noise levels draw an additional skew matrix and therefore share a
    different stream. A graded positive-noise sweep must use its smallest
    positive level as the paired reference; the zero point is a compatibility
    baseline, not a paired member of that sweep.
    """

    if not 2 <= planted_rank < dimension // 2:
        raise ValueError("planted_rank must be between two and half the dimension")
    if geometry_noise < 0:
        raise ValueError("geometry_noise must be nonnegative")
    rng = np.random.default_rng(seed)
    planted = np.eye(dimension, planted_rank, dtype=np.float64)
    direct = planted @ rng.normal(size=planted_rank)
    direct /= np.linalg.norm(direct)
    laplacians: dict[str, csr_matrix] = {}
    vectors = []
    baselines = []
    outcomes = []
    groups = []
    for context in range(contexts):
        if shuffle_low_space:
            low_indices = rng.choice(dimension, size=planted_rank, replace=False)
        else:
            low_indices = np.arange(planted_rank)
        diagonal = rng.uniform(0.65, 1.0, size=dimension)
        diagonal[low_indices] = rng.uniform(0.03, 0.18, size=planted_rank)
        laplacian = diags(diagonal, format="csr")
        if geometry_noise > 0:
            block_dim = 2 * planted_rank
            skew = rng.normal(size=(block_dim, block_dim))
            skew = skew - skew.T
            rotation = expm(geometry_noise * skew / np.sqrt(block_dim))
            block = rotation @ np.diag(diagonal[:block_dim]) @ rotation.T
            laplacian = laplacian.tolil()
            laplacian[:block_dim, :block_dim] = block
            laplacian = laplacian.tocsr()
            laplacian.eliminate_zeros()
        laplacians[f"context-{context:02d}"] = laplacian
        for _ in range(candidates_per_context):
            norm = rng.uniform(0.25, 1.0)
            vector = rng.normal(size=dimension)
            vector *= norm / np.linalg.norm(vector)
            j_visibility = float(vector[-1] ** 2 / (norm**2))
            nuisance = rng.normal()
            energy = float(np.sum(vector[:planted_rank] ** 2) / (norm**2))
            signed = float(direct @ vector) / norm
            outcome = 0.2 * j_visibility
            if outcome_signal:
                outcome += 3.0 * energy + 1.1 * signed
            outcome += 0.12 * nuisance + 0.06 * rng.normal()
            vectors.append(vector)
            baselines.append([norm, j_visibility, nuisance])
            outcomes.append(outcome)
            groups.append(f"context-{context:02d}")
    return SyntheticFixture(
        laplacians=laplacians,
        vectors=np.asarray(vectors),
        baseline_covariates=np.asarray(baselines),
        outcomes=np.asarray(outcomes),
        groups=np.asarray(groups),
        planted_basis=planted,
        planted_direction=direct,
    )
