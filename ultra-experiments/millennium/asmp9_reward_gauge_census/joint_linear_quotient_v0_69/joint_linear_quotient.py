"""Exact finite linear quotient tools for ASMP-9 v0.69.

The target parameter is a reward vector ``r`` in R^n.  ``G`` spans licensed
reward-gauge directions, ``A`` is a linear physical measurement channel, and
``N`` spans additive measurement-nuisance directions.  A reward-quotient
analysis must discard both ``N`` and the visible image ``A(G)``.  The resulting
effective channel is represented in exact rational arithmetic.

This is theorem-development code.  It does not model a human or language
model and does not establish that any particular reward gauge is physically
licensed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import sympy as sp


def rational_matrix(rows: Sequence[Sequence[object]]) -> sp.Matrix:
    """Build a SymPy matrix with exact rational entries."""

    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def _basis_matrix(vectors: Iterable[sp.Matrix], ambient_dim: int) -> sp.Matrix:
    columns = list(vectors)
    if not columns:
        return sp.zeros(ambient_dim, 0)
    # SymPy's ``columnspace`` and ``nullspace`` already return independent
    # column vectors, so no second reduction is needed here.
    return sp.Matrix.hstack(*columns)


def _column_basis(matrix: sp.Matrix) -> sp.Matrix:
    return _basis_matrix(matrix.columnspace(), matrix.rows)


def _orthogonal_complement(matrix: sp.Matrix) -> sp.Matrix:
    """Return an exact basis for the standard-inner-product complement."""

    return _basis_matrix(matrix.T.nullspace(), matrix.rows)


def _in_span(vector: sp.Matrix, basis: sp.Matrix) -> bool:
    if basis.cols == 0:
        return vector.is_zero_matrix
    return basis.row_join(vector).rank() == basis.rank()


@dataclass(frozen=True)
class JointQuotientAnalysis:
    reward_dimension: int
    measurement_dimension: int
    gauge_rank: int
    physical_nuisance_rank: int
    visible_gauge_rank: int
    joint_output_nuisance_rank: int
    target_quotient_dimension: int
    effective_output_dimension: int
    effective_rank: int
    joint_kernel_dimension: int
    exactly_identifies_reward_quotient: bool
    gauge_respecting_before_forced_quotient: bool
    effective_map: sp.Matrix
    joint_kernel_basis: sp.Matrix
    non_gauge_witness: sp.Matrix | None
    identified_estimand_basis: sp.Matrix

    def to_jsonable(self) -> dict[str, object]:
        def rows(matrix: sp.Matrix | None) -> list[list[str]] | None:
            if matrix is None:
                return None
            return [
                [str(matrix[i, j]) for j in range(matrix.cols)]
                for i in range(matrix.rows)
            ]

        return {
            "reward_dimension": self.reward_dimension,
            "measurement_dimension": self.measurement_dimension,
            "gauge_rank": self.gauge_rank,
            "physical_nuisance_rank": self.physical_nuisance_rank,
            "visible_gauge_rank": self.visible_gauge_rank,
            "joint_output_nuisance_rank": self.joint_output_nuisance_rank,
            "target_quotient_dimension": self.target_quotient_dimension,
            "effective_output_dimension": self.effective_output_dimension,
            "effective_rank": self.effective_rank,
            "joint_kernel_dimension": self.joint_kernel_dimension,
            "exactly_identifies_reward_quotient": (
                self.exactly_identifies_reward_quotient
            ),
            "gauge_respecting_before_forced_quotient": (
                self.gauge_respecting_before_forced_quotient
            ),
            "effective_map": rows(self.effective_map),
            "joint_kernel_basis": rows(self.joint_kernel_basis),
            "non_gauge_witness": rows(self.non_gauge_witness),
            "identified_estimand_basis": rows(self.identified_estimand_basis),
        }


def analyze_joint_quotient(
    measurement: sp.Matrix,
    gauge_basis: sp.Matrix,
    nuisance_basis: sp.Matrix,
) -> JointQuotientAnalysis:
    """Analyze the representative-insensitive reward measurement quotient.

    ``measurement`` has shape ``(m, n)``, ``gauge_basis`` has ``n`` rows, and
    ``nuisance_basis`` has ``m`` rows.  Columns need not be independent.
    """

    if gauge_basis.rows != measurement.cols:
        raise ValueError("gauge basis must live in reward space")
    if nuisance_basis.rows != measurement.rows:
        raise ValueError("nuisance basis must live in measurement space")

    gauge = _column_basis(gauge_basis)
    nuisance = _column_basis(nuisance_basis)
    gauge_image = _column_basis(measurement * gauge)
    joint_output_nuisance = _column_basis(
        nuisance.row_join(gauge_image)
    )

    reward_complement = _orthogonal_complement(gauge)
    output_annihilator = _orthogonal_complement(joint_output_nuisance)
    effective = output_annihilator.T * measurement * reward_complement
    full_invariant_map = output_annihilator.T * measurement
    kernel = _basis_matrix(
        full_invariant_map.nullspace(), measurement.cols
    )
    identified_estimands = _column_basis(full_invariant_map.T)

    witness = None
    for vector in kernel.columnspace():
        if not _in_span(vector, gauge):
            witness = vector
            break

    gauge_respecting = all(
        _in_span(vector, nuisance) for vector in gauge_image.columnspace()
    )
    quotient_dimension = measurement.cols - gauge.rank()
    effective_rank = effective.rank()
    exact = (
        kernel.rank() == gauge.rank()
        and effective_rank == quotient_dimension
    )

    return JointQuotientAnalysis(
        reward_dimension=measurement.cols,
        measurement_dimension=measurement.rows,
        gauge_rank=gauge.rank(),
        physical_nuisance_rank=nuisance.rank(),
        visible_gauge_rank=(
            nuisance.row_join(gauge_image).rank() - nuisance.rank()
        ),
        joint_output_nuisance_rank=joint_output_nuisance.rank(),
        target_quotient_dimension=quotient_dimension,
        effective_output_dimension=(
            measurement.rows - joint_output_nuisance.rank()
        ),
        effective_rank=effective_rank,
        joint_kernel_dimension=kernel.rank(),
        exactly_identifies_reward_quotient=exact,
        gauge_respecting_before_forced_quotient=gauge_respecting,
        effective_map=effective,
        joint_kernel_basis=kernel,
        non_gauge_witness=witness,
        identified_estimand_basis=identified_estimands,
    )


def _numeric_orthogonal_complement(matrix: np.ndarray) -> np.ndarray:
    if matrix.shape[1] == 0:
        return np.eye(matrix.shape[0])
    u, singular, _ = np.linalg.svd(matrix, full_matrices=True)
    tolerance = (
        max(matrix.shape)
        * np.finfo(float).eps
        * (singular[0] if singular.size else 0.0)
    )
    rank = int(np.sum(singular > tolerance))
    return u[:, rank:]


def stability_certificate(
    measurement: sp.Matrix,
    gauge_basis: sp.Matrix,
    nuisance_basis: sp.Matrix,
) -> dict[str, object]:
    """Return the Euclidean quotient stability certificate.

    The smallest singular value is computed only after exact injectivity has
    been established.  Its reciprocal is the sharp Lipschitz constant for
    gauge-fixed least-squares recovery under additive disturbance in the
    admitted output quotient.
    """

    analysis = analyze_joint_quotient(
        measurement, gauge_basis, nuisance_basis
    )
    a = np.asarray(measurement, dtype=float)
    g = np.asarray(_column_basis(gauge_basis), dtype=float)
    n = np.asarray(_column_basis(nuisance_basis), dtype=float)
    joint = np.concatenate((n, a @ g), axis=1)
    x_basis = _numeric_orthogonal_complement(g)
    y_basis = _numeric_orthogonal_complement(joint)
    effective = y_basis.T @ a @ x_basis
    singular = np.linalg.svd(effective, compute_uv=False)
    singular = np.sort(singular)[::-1]

    sigma_min = None
    inverse_lipschitz = None
    if analysis.exactly_identifies_reward_quotient:
        sigma_min = float(singular[-1])
        inverse_lipschitz = float(1.0 / sigma_min)

    return {
        "exactly_identifies_reward_quotient": (
            analysis.exactly_identifies_reward_quotient
        ),
        "singular_values": [float(value) for value in singular],
        "sigma_min": sigma_min,
        "sharp_inverse_lipschitz_constant": inverse_lipschitz,
    }


def canonical_fixtures() -> dict[str, tuple[sp.Matrix, sp.Matrix, sp.Matrix]]:
    """Small exact fixtures covering full, leaking, and confounded channels."""

    # Reward space R^3 modulo a global constant.  Measuring all three scores
    # with a common-mode physical offset identifies both independent contrasts.
    full = (
        sp.eye(3),
        rational_matrix([[1], [1], [1]]),
        rational_matrix([[1], [1], [1]]),
    )

    # Two raw scores with one common offset provide only one contrast, so the
    # two-dimensional reward quotient cannot be identified.
    partial = (
        rational_matrix([[1, 0, 0], [0, 1, 0]]),
        rational_matrix([[1], [1], [1]]),
        rational_matrix([[1], [1]]),
    )

    # A distinct gauge coordinate is physically visible.  The raw channel is
    # representative-sensitive, but quotienting A(G) recovers all three
    # non-gauge coordinates.
    leaking_but_complete = (
        rational_matrix(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 0],
            ]
        ),
        rational_matrix([[0], [0], [0], [1]]),
        rational_matrix([[0], [0], [0], [0], [1]]),
    )

    # The third substantive coordinate is aliased with the first two.  The
    # exact non-gauge kernel witness is proportional to (-1,-1,1,0).
    confounded = (
        rational_matrix(
            [
                [1, 0, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 1],
            ]
        ),
        rational_matrix([[0], [0], [0], [1]]),
        rational_matrix([[0], [0], [1]]),
    )

    return {
        "full_common_mode": full,
        "partial_common_mode": partial,
        "gauge_leaking_but_complete": leaking_but_complete,
        "non_gauge_confounded": confounded,
    }
