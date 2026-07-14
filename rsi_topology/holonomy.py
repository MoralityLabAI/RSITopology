"""Gauge-invariant holonomy diagnostics for prompt/checkpoint bundles.

The existing lineage statistic keeps the singular values of ``U_b.T @ U_a``.
Those values measure local subspace retention but discard the polar factor that
transports signed coordinates.  Products of the polar transports around a
closed loop expose the missing phase: a monitor can have excellent lineage on
every edge and still return globally rotated.

This module is deliberately small and model-free.  It supplies a rank-two
Grassmannian control in R^4 plus general transport and loop functions that can
later consume bases emitted by spectral-bundle discovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Sequence

import numpy as np
from scipy.linalg import expm


Array = np.ndarray
Mode = Literal["flat", "curved"]


@dataclass(frozen=True)
class LoopHolonomy:
    """Holonomy and edge-retention data for one closed loop."""

    matrix: Array
    edge_squared_singular_values: tuple[Array, ...]

    @property
    def mean_edge_chordal_lineage(self) -> float:
        values = np.concatenate(self.edge_squared_singular_values)
        return float(np.mean(values))

    @property
    def minimum_edge_worst_direction_retention(self) -> float:
        values = np.concatenate(self.edge_squared_singular_values)
        return float(np.min(values))

    @property
    def mean_edge_lineage(self) -> float:
        """Deprecated alias for ``mean_edge_chordal_lineage``."""

        return self.mean_edge_chordal_lineage

    @property
    def minimum_edge_lineage(self) -> float:
        """Deprecated alias for ``minimum_edge_worst_direction_retention``."""

        return self.minimum_edge_worst_direction_retention

    @property
    def mean_signed_monitor_return(self) -> float:
        return float(np.trace(self.matrix) / self.matrix.shape[0])

    @property
    def identity_loss(self) -> float:
        return holonomy_score(self.matrix)


@dataclass(frozen=True)
class GrassmannLoop:
    """A sampled boundary in a two-parameter family of subspaces."""

    mode: Mode
    points: tuple[tuple[float, float], ...]
    frames: tuple[Array, ...]
    context_generator: Array
    training_generator: Array
    steps: int
    step_size: float

    @property
    def commutator_norm(self) -> float:
        commutator = (
            self.context_generator @ self.training_generator
            - self.training_generator @ self.context_generator
        )
        return float(np.linalg.norm(commutator, ord="fro"))


def _validated_frame(frame: Array) -> Array:
    value = np.asarray(frame, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] < value.shape[1] or value.shape[1] == 0:
        raise ValueError("a frame must be a nonempty tall matrix")
    if not np.all(np.isfinite(value)):
        raise ValueError("frame entries must be finite")
    gram = value.T @ value
    if not np.allclose(gram, np.eye(value.shape[1]), atol=1e-9):
        raise ValueError("frame columns must be orthonormal")
    return value


def procrustes_transport(source_basis: Array, target_basis: Array) -> tuple[Array, Array]:
    """Return the closest orthogonal coordinate transport, source to target.

    If ``x = source_basis @ c``, the raw target coordinates are
    ``target_basis.T @ source_basis @ c``.  Its polar factor is the norm-
    preserving transport; the singular values are the ordinary principal-angle
    lineage retained by the current program.
    """

    source = _validated_frame(source_basis)
    target = _validated_frame(target_basis)
    if source.shape != target.shape:
        raise ValueError("source and target frames must share ambient dimension and rank")
    overlap = target.T @ source
    left, singular_values, right_t = np.linalg.svd(overlap)
    transport = left @ right_t
    return transport, np.clip(singular_values, 0.0, 1.0)


def loop_holonomy(frames: Iterable[Array]) -> LoopHolonomy:
    """Compose Procrustes transports around a closed loop of unique vertices."""

    values = tuple(_validated_frame(frame) for frame in frames)
    if len(values) < 3:
        raise ValueError("a holonomy loop needs at least three vertices")
    shape = values[0].shape
    if any(frame.shape != shape for frame in values[1:]):
        raise ValueError("all loop frames must share ambient dimension and rank")
    product = np.eye(shape[1], dtype=np.float64)
    edge_values: list[Array] = []
    targets = values[1:] + values[:1]
    for source, target in zip(values, targets):
        transport, singular_values = procrustes_transport(source, target)
        product = transport @ product
        edge_values.append(singular_values**2)
    return LoopHolonomy(
        matrix=product,
        edge_squared_singular_values=tuple(edge_values),
    )


def holonomy_score(matrix: Array) -> float:
    """Average signed-monitor identity loss, ``1 - trace(H) / rank``."""

    value = np.asarray(matrix, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] != value.shape[1] or value.shape[0] == 0:
        raise ValueError("holonomy must be a nonempty square matrix")
    if not np.allclose(value.T @ value, np.eye(value.shape[0]), atol=1e-8):
        raise ValueError("holonomy must be orthogonal")
    return float(1.0 - np.trace(value) / value.shape[0])


def holonomy_orientation_receipt(matrix: Array) -> dict:
    """Report the discrete O(r) component before any SO(r) angle summary."""

    value = np.asarray(matrix, dtype=np.float64)
    holonomy_score(value)  # validates orthogonality and shape
    determinant = float(np.linalg.det(value))
    orientation_reversing = determinant < 0.0
    return {
        "holonomy_determinant": determinant,
        "orientation_component": "reversing" if orientation_reversing else "preserving",
        "orientation_reversal_flag": orientation_reversing,
        "canonical_angle_status": (
            "superseded_by_orientation_reversal"
            if orientation_reversing
            else "reported_for_special_orthogonal_component"
        ),
    }


def holonomy_phase_degrees(matrix: Array) -> float:
    """Signed phase for rank two; largest canonical rotation otherwise."""

    value = np.asarray(matrix, dtype=np.float64)
    holonomy_score(value)  # validates the matrix
    if value.shape == (2, 2) and np.linalg.det(value) > 0:
        numerator = value[1, 0] - value[0, 1]
        denominator = value[0, 0] + value[1, 1]
        return float(np.degrees(np.arctan2(numerator, denominator)))
    angles = canonical_rotation_angles_degrees(value)
    return float(max(angles, default=0.0))


def canonical_rotation_angles_degrees(matrix: Array) -> tuple[float, ...]:
    """Return the gauge-invariant rotation-plane angles of an SO(r) matrix.

    An even-dimensional special-orthogonal matrix has ``r / 2`` canonical
    rotation planes.  Odd rank has one additional fixed axis.  The returned
    angles lie in ``[0, 180]`` and include zero-angle planes, so rank six emits
    exactly three values.  These angles, rather than individual matrix entries,
    are the portable summary of a holonomy conjugacy class.
    """

    value = np.asarray(matrix, dtype=np.float64)
    holonomy_score(value)  # validates orthogonality and shape
    determinant = float(np.linalg.det(value))
    if determinant < 1.0 - 1e-7:
        raise ValueError("canonical rotation angles require special orthogonal holonomy")

    eigenvalues = np.linalg.eigvals(value)
    tolerance = 1e-7
    angles: list[float] = []
    positive_fixed = 0
    negative_fixed = 0
    for eigenvalue in eigenvalues:
        if abs(float(np.imag(eigenvalue))) > tolerance:
            if float(np.imag(eigenvalue)) > 0.0:
                angles.append(float(abs(np.angle(eigenvalue))))
        elif float(np.real(eigenvalue)) < 0.0:
            negative_fixed += 1
        else:
            positive_fixed += 1
    if negative_fixed % 2:
        raise ValueError("SO(r) holonomy has an unpaired negative fixed direction")
    angles.extend([np.pi] * (negative_fixed // 2))
    zero_planes = positive_fixed // 2
    angles.extend([0.0] * zero_planes)
    expected = value.shape[0] // 2
    if len(angles) != expected:
        raise ValueError("could not resolve the canonical rotation planes")
    return tuple(sorted(float(np.degrees(angle)) for angle in angles))


def resample_subspace_frames(
    frames: Iterable[Array],
    *,
    noise_scale: float,
    seed: int,
) -> tuple[Array, ...]:
    """Independently perturb estimated subspaces in their tangent directions."""

    if not np.isfinite(noise_scale) or noise_scale < 0.0:
        raise ValueError("noise_scale must be finite and nonnegative")
    values = tuple(_validated_frame(frame) for frame in frames)
    rng = np.random.default_rng(seed)
    output: list[Array] = []
    for frame in values:
        ambient_projector = np.eye(frame.shape[0]) - frame @ frame.T
        tangent_noise = ambient_projector @ rng.normal(size=frame.shape)
        basis, triangular = np.linalg.qr(
            frame + noise_scale * tangent_noise, mode="reduced"
        )
        signs = np.where(np.diag(triangular) >= 0.0, 1.0, -1.0)
        output.append(basis * signs)
    return tuple(output)


def analytic_origin_curvature(
    context_generator: Array,
    training_generator: Array,
    base_frame: Array,
) -> dict:
    """Return the exact Grassmann curvature at the registered origin frame."""

    context = np.asarray(context_generator, dtype=np.float64)
    training = np.asarray(training_generator, dtype=np.float64)
    base = _validated_frame(base_frame)
    if context.shape != (base.shape[0], base.shape[0]):
        raise ValueError("context generator and base frame disagree")
    if training.shape != context.shape:
        raise ValueError("training generator and context generator disagree")
    if not np.allclose(context.T, -context, atol=1e-10):
        raise ValueError("context generator must be skew-symmetric")
    if not np.allclose(training.T, -training, atol=1e-10):
        raise ValueError("training generator must be skew-symmetric")

    projector = base @ base.T
    context_derivative = context @ projector - projector @ context
    training_derivative = training @ projector - projector @ training
    curvature_ambient = (
        context_derivative @ training_derivative
        - training_derivative @ context_derivative
    )
    curvature = base.T @ curvature_ambient @ base
    eigenvalues = np.linalg.eigvals(curvature)
    rates = sorted(
        float(np.degrees(np.imag(value)))
        for value in eigenvalues
        if float(np.imag(value)) > 1e-9
    )
    return {
        "curvature_matrix": curvature.tolist(),
        "canonical_rotation_rates_degrees_per_unit_area": rates,
        "maximum_canonical_rotation_rate_degrees_per_unit_area": float(
            max(rates, default=0.0)
        ),
    }


def _linear_fit_receipt(x: Array, y: Array) -> dict:
    coefficients = np.polyfit(x, y, deg=1)
    prediction = np.polyval(coefficients, x)
    denominator = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = (
        1.0
        if denominator <= 1e-30
        else 1.0 - float(np.sum((y - prediction) ** 2)) / denominator
    )
    return {
        "slope": float(coefficients[0]),
        "intercept": float(coefficients[1]),
        "r_squared": r_squared,
    }


def evaluate_perimeter_area_control(
    *,
    steps_grid: Sequence[int] = (2, 4, 6, 8, 10, 12),
    step_size: float = 0.02,
    noise_scale: float = 0.0195,
    replicates: int = 128,
    seed: int = 20260711,
    matched_minimum_worst_direction_retention: float = 0.9900332889206206,
) -> dict:
    """Separate curvature's area law from flat estimation noise's perimeter law."""

    steps_values = tuple(int(value) for value in steps_grid)
    if not steps_values or any(value < 1 for value in steps_values):
        raise ValueError("steps_grid must contain positive integers")
    if replicates < 3:
        raise ValueError("at least three noise replicates are required")

    noise_rows: list[dict] = []
    curvature_rows: list[dict] = []
    for steps in steps_values:
        flat = build_grassmann_loop("flat", steps=steps, step_size=step_size)
        signed_phases: list[float] = []
        minimum_lineages: list[float] = []
        mean_lineages: list[float] = []
        orientation_reversal_count = 0
        for replicate in range(replicates):
            replicate_seed = seed + steps * 100_000 + replicate
            sampled = resample_subspace_frames(
                flat.frames, noise_scale=noise_scale, seed=replicate_seed
            )
            result = loop_holonomy(sampled)
            orientation = holonomy_orientation_receipt(result.matrix)
            if orientation["orientation_reversal_flag"]:
                orientation_reversal_count += 1
                continue
            signed_phases.append(holonomy_phase_degrees(result.matrix))
            minimum_lineages.append(
                result.minimum_edge_worst_direction_retention
            )
            mean_lineages.append(result.mean_edge_chordal_lineage)
        if not signed_phases:
            raise ValueError("every noise-null replicate reversed orientation")
        noise_rows.append(
            {
                "steps_per_side": steps,
                "perimeter_edges": 4 * steps,
                "phase_mean_degrees": float(np.mean(signed_phases)),
                "phase_variance_degrees_squared": float(
                    np.var(signed_phases, ddof=1)
                ),
                "phase_rms_degrees": float(
                    np.sqrt(np.mean(np.asarray(signed_phases) ** 2))
                ),
                "orientation_reversal_count": orientation_reversal_count,
                "mean_minimum_edge_worst_direction_retention": float(
                    np.mean(minimum_lineages)
                ),
                "mean_edge_chordal_lineage": float(np.mean(mean_lineages)),
            }
        )

        curved = build_grassmann_loop("curved", steps=steps, step_size=step_size)
        curved_result = loop_holonomy(curved.frames)
        curved_orientation = holonomy_orientation_receipt(curved_result.matrix)
        if curved_orientation["orientation_reversal_flag"]:
            raise ValueError("planted curvature control unexpectedly reversed orientation")
        angles = canonical_rotation_angles_degrees(curved_result.matrix)
        curvature_rows.append(
            {
                "steps_per_side": steps,
                "enclosed_area": float((steps * step_size) ** 2),
                "maximum_canonical_rotation_degrees": float(max(angles, default=0.0)),
                "holonomy_determinant": curved_orientation["holonomy_determinant"],
                "minimum_edge_worst_direction_retention": (
                    curved_result.minimum_edge_worst_direction_retention
                ),
            }
        )

    perimeter = np.asarray(
        [row["perimeter_edges"] for row in noise_rows], dtype=np.float64
    )
    phase_variance = np.asarray(
        [row["phase_variance_degrees_squared"] for row in noise_rows],
        dtype=np.float64,
    )
    area = np.asarray(
        [row["enclosed_area"] for row in curvature_rows], dtype=np.float64
    )
    curvature_phase = np.asarray(
        [row["maximum_canonical_rotation_degrees"] for row in curvature_rows],
        dtype=np.float64,
    )
    reference_noise_row = min(
        noise_rows, key=lambda row: abs(row["steps_per_side"] - 10)
    )
    curved_origin = build_grassmann_loop("curved", steps=1, step_size=step_size)
    analytic = analytic_origin_curvature(
        curved_origin.context_generator,
        curved_origin.training_generator,
        curved_origin.frames[0],
    )
    analytic_rate = analytic[
        "maximum_canonical_rotation_rate_degrees_per_unit_area"
    ]
    area_fit = _linear_fit_receipt(area, curvature_phase)
    return {
        "noise_model": "independent_tangent_subspace_resampling_on_flat_connection",
        "noise_scale": noise_scale,
        "replicates": replicates,
        "seed": seed,
        "step_size": step_size,
        "steps_grid": list(steps_values),
        "matched_minimum_edge_worst_direction_retention_target": (
            matched_minimum_worst_direction_retention
        ),
        "reference_noise_mean_minimum_edge_worst_direction_retention": reference_noise_row[
            "mean_minimum_edge_worst_direction_retention"
        ],
        "reference_worst_direction_retention_absolute_error": abs(
            reference_noise_row["mean_minimum_edge_worst_direction_retention"]
            - matched_minimum_worst_direction_retention
        ),
        "noise_rows": noise_rows,
        "curvature_rows": curvature_rows,
        "noise_variance_vs_perimeter_fit": _linear_fit_receipt(
            perimeter, phase_variance
        ),
        "curvature_phase_vs_area_fit": area_fit,
        "analytic_origin_curvature": analytic,
        "curvature_fit_slope_absolute_error_from_analytic_origin": abs(
            area_fit["slope"] - analytic_rate
        ),
        "curvature_fit_slope_relative_error_from_analytic_origin": (
            abs(area_fit["slope"] - analytic_rate) / max(analytic_rate, 1e-30)
        ),
    }


def _plane_generator(i: int, j: int, scale: float = 1.0) -> Array:
    value = np.zeros((4, 4), dtype=np.float64)
    value[i, j] = scale
    value[j, i] = -scale
    return value


def build_grassmann_loop(
    mode: Mode,
    *,
    steps: int = 10,
    step_size: float = 0.1,
) -> GrassmannLoop:
    """Build matched flat or curved rank-two loops in ``Gr(2, 4)``."""

    if mode not in ("flat", "curved"):
        raise ValueError("mode must be 'flat' or 'curved'")
    if steps < 1:
        raise ValueError("steps must be positive")
    if not np.isfinite(step_size) or step_size <= 0.0:
        raise ValueError("step_size must be finite and positive")

    context = _plane_generator(0, 2) + 0.7 * _plane_generator(1, 3)
    if mode == "flat":
        training = 0.7 * _plane_generator(0, 2) - _plane_generator(1, 3)
    else:
        training = 0.7 * _plane_generator(0, 3) - _plane_generator(1, 2)

    side = steps * step_size
    points: list[tuple[float, float]] = [
        (index * step_size, 0.0) for index in range(steps + 1)
    ]
    points.extend((side, index * step_size) for index in range(1, steps + 1))
    points.extend(
        (index * step_size, side) for index in range(steps - 1, -1, -1)
    )
    points.extend((0.0, index * step_size) for index in range(steps - 1, 0, -1))

    base = np.eye(4, dtype=np.float64)[:, :2]
    frames = tuple(expm(s * context + t * training) @ base for s, t in points)
    return GrassmannLoop(
        mode=mode,
        points=tuple(points),
        frames=frames,
        context_generator=context,
        training_generator=training,
        steps=steps,
        step_size=step_size,
    )


def evaluate_grassmann_loop(
    mode: Mode,
    *,
    steps: int = 10,
    step_size: float = 0.1,
) -> dict:
    """Return a JSON-safe receipt for one synthetic loop."""

    fixture = build_grassmann_loop(mode, steps=steps, step_size=step_size)
    result = loop_holonomy(fixture.frames)
    monitor = np.zeros(result.matrix.shape[0], dtype=np.float64)
    monitor[0] = 1.0
    returned = result.matrix @ monitor
    orientation = holonomy_orientation_receipt(result.matrix)
    orientation_reversing = orientation["orientation_reversal_flag"]
    canonical_angles = (
        None
        if orientation_reversing
        else canonical_rotation_angles_degrees(result.matrix)
    )
    phase = None if orientation_reversing else holonomy_phase_degrees(result.matrix)
    receipt = {
        "mode": mode,
        "ambient_dimension": int(fixture.frames[0].shape[0]),
        "rank": int(fixture.frames[0].shape[1]),
        "steps_per_side": steps,
        "step_size": step_size,
        "edge_count": len(fixture.frames),
        "commutator_frobenius_norm": fixture.commutator_norm,
        "mean_edge_chordal_lineage": result.mean_edge_chordal_lineage,
        "minimum_edge_worst_direction_retention": (
            result.minimum_edge_worst_direction_retention
        ),
        "holonomy_phase_degrees": phase,
        "canonical_rotation_angles_degrees": (
            None if canonical_angles is None else list(canonical_angles)
        ),
        "maximum_canonical_rotation_degrees": (
            None
            if canonical_angles is None
            else float(max(canonical_angles, default=0.0))
        ),
        "mean_canonical_rotation_degrees": (
            None
            if canonical_angles is None
            else float(np.mean(canonical_angles) if canonical_angles else 0.0)
        ),
        "holonomy_identity_loss": result.identity_loss,
        "mean_signed_monitor_return": result.mean_signed_monitor_return,
        "first_monitor_return": float(monitor @ returned),
        "block_energy_return": float(returned @ returned),
        "holonomy_matrix": result.matrix.tolist(),
    }
    receipt.update(orientation)
    return receipt
