"""Gauge-invariant soft-atlas measurements and fixed-sequence gate logic.

This module deliberately separates instrument validity from scientific
evidence.  A gate with a non-valid instrument can never emit a scientific
pass, fail, or inconclusive decision: it is ``not_evaluated``.  Earlier gate
records remain immutable when a downstream instrument fails.

The Qwen measurement construction works in the shared twelve-dimensional
probe-response space.  For one prompt/replica/checkpoint cell, module
signatures are concatenated conceptually and represented by their Gram matrix

    G = sum_m S_m S_m^T.

The canonical positive-semidefinite square root ``A_hat = sqrt(G)`` removes
the arbitrary right-coordinate gauge of every signature.  Soft projectors
``P(lambda) = G (G + lambda I)^-1`` then provide a continuous alternative to
hard singular-band cuts.  This is a behavioral response-geometry instrument;
it does not recover coordinated weight-space edit coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np


Array = np.ndarray
Cell = tuple[str, str, int]


VALID_INSTRUMENT = "valid"
NOT_ASSESSED = "not_assessed_due_to_upstream_stop"
DECISIONS = {"pass", "fail", "inconclusive", "not_evaluated"}


def _finite_square(matrix: Array, *, name: str) -> Array:
    value = np.asarray(matrix, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.isfinite(value).all():
        raise ValueError(f"{name} must be finite")
    return value


def psd_square_root(matrix: Array, *, atol: float = 1e-10) -> Array:
    """Return the symmetric PSD square root after a strict PSD check."""

    value = _finite_square(matrix, name="PSD matrix")
    value = (value + value.T) / 2.0
    eigenvalues, eigenvectors = np.linalg.eigh(value)
    scale = max(float(np.max(np.abs(eigenvalues))), 1.0)
    if float(np.min(eigenvalues)) < -atol * scale:
        raise ValueError("matrix is not positive semidefinite")
    clipped = np.clip(eigenvalues, 0.0, None)
    return (eigenvectors * np.sqrt(clipped)) @ eigenvectors.T


def response_gram(signatures: Sequence[Array]) -> Array:
    """Aggregate module signatures without choosing their right-side gauges."""

    if not signatures:
        raise ValueError("at least one signature is required")
    matrices = [np.asarray(item, dtype=np.float64) for item in signatures]
    row_counts = {item.shape[0] for item in matrices if item.ndim == 2}
    if len(row_counts) != 1 or len(matrices) != len(
        [item for item in matrices if item.ndim == 2]
    ):
        raise ValueError("signatures must be matrices with one shared row dimension")
    if any(not np.isfinite(item).all() for item in matrices):
        raise ValueError("signatures must be finite")
    gram = sum((item @ item.T for item in matrices), np.zeros((matrices[0].shape[0],) * 2))
    return (gram + gram.T) / 2.0


def soft_projector(gram: Array, regularization: float) -> Array:
    """Return ``G (G + lambda I)^-1`` using its stable eigendecomposition."""

    value = _finite_square(gram, name="Gram matrix")
    if not np.isfinite(regularization) or regularization <= 0.0:
        raise ValueError("regularization must be finite and positive")
    value = (value + value.T) / 2.0
    eigenvalues, eigenvectors = np.linalg.eigh(value)
    scale = max(float(np.max(np.abs(eigenvalues))), 1.0)
    if float(np.min(eigenvalues)) < -1e-10 * scale:
        raise ValueError("Gram matrix is not positive semidefinite")
    eigenvalues = np.clip(eigenvalues, 0.0, None)
    weights = eigenvalues / (eigenvalues + regularization)
    return (eigenvectors * weights) @ eigenvectors.T


def soft_similarity(left: Array, right: Array) -> float:
    """Hilbert-Schmidt cosine between two nonzero PSD operators."""

    a = _finite_square(left, name="left operator")
    b = _finite_square(right, name="right operator")
    if a.shape != b.shape:
        raise ValueError("operators must share a shape")
    denominator = float(np.linalg.norm(a, "fro") * np.linalg.norm(b, "fro"))
    if denominator <= np.finfo(float).tiny:
        return 0.0
    return float(np.clip(np.sum(a * b) / denominator, 0.0, 1.0))


def effective_dimension(operator: Array) -> float:
    return float(np.trace(_finite_square(operator, name="operator")))


def spectral_anisotropy(operator: Array) -> float:
    """Dimension-honest spectral non-flatness in [0, 1]."""

    value = _finite_square(operator, name="operator")
    dimension = value.shape[0]
    trace = float(np.trace(value))
    squared_trace = float(np.sum(value * value))
    if squared_trace <= np.finfo(float).tiny:
        return 0.0
    participation_rank = min(float(trace * trace / squared_trace), float(dimension))
    return float(np.sqrt(max(0.0, 1.0 - participation_rank / dimension)))


def measurement_edges(
    prompts: Sequence[str], replicas: Sequence[str], checkpoints: Sequence[int]
) -> tuple[tuple[Cell, Cell], ...]:
    """Registered within-prompt replica/checkpoint measurement edges.

    The four replicas are paired as (0,1) and (2,3).  For each prompt this
    gives eight adjacent-checkpoint edges and six within-half replica edges.
    """

    if len(replicas) != 4 or len(set(replicas)) != 4:
        raise ValueError("measurement design requires four unique replicas")
    if len(checkpoints) < 2 or len(set(checkpoints)) != len(checkpoints):
        raise ValueError("measurement design requires unique ordered checkpoints")
    ordered_checkpoints = tuple(int(value) for value in checkpoints)
    result: list[tuple[Cell, Cell]] = []
    for prompt in prompts:
        for replica in replicas:
            result.extend(
                (
                    (str(prompt), str(replica), left),
                    (str(prompt), str(replica), right),
                )
                for left, right in zip(ordered_checkpoints[:-1], ordered_checkpoints[1:])
            )
        for left_replica, right_replica in (
            (replicas[0], replicas[1]),
            (replicas[2], replicas[3]),
        ):
            result.extend(
                (
                    (str(prompt), str(left_replica), checkpoint),
                    (str(prompt), str(right_replica), checkpoint),
                )
                for checkpoint in ordered_checkpoints
            )
    return tuple(result)


def measurement_noise_scale(
    canonical_operators: Mapping[Cell, Array],
    edges: Sequence[tuple[Cell, Cell]],
    *,
    quantile: float = 0.95,
) -> tuple[float, list[float]]:
    """Compute the registered gauge-invariant measurement noise scale."""

    if not 0.0 < quantile < 1.0:
        raise ValueError("quantile must lie strictly between zero and one")
    if not edges:
        raise ValueError("measurement edge set must be nonempty")
    values: list[float] = []
    for left, right in edges:
        if left not in canonical_operators or right not in canonical_operators:
            raise ValueError("measurement edge references an unknown cell")
        delta = np.asarray(canonical_operators[left]) - np.asarray(
            canonical_operators[right]
        )
        energy = delta.T @ delta
        values.append(float(np.max(np.linalg.eigvalsh((energy + energy.T) / 2.0))))
    scale = float(np.quantile(np.asarray(values), quantile))
    if not np.isfinite(scale) or scale <= 0.0:
        raise ValueError("measurement noise scale is not finite and positive")
    return scale, values


def regularization_grid(noise_scale: float, exponents: Sequence[int]) -> Array:
    if not np.isfinite(noise_scale) or noise_scale <= 0.0:
        raise ValueError("noise scale must be finite and positive")
    values = np.asarray([noise_scale * 10.0 ** (int(j) / 4.0) for j in exponents])
    if len(values) != len(set(int(item) for item in exponents)):
        raise ValueError("regularization exponents must be unique")
    return values


def quadrant_cells(
    *,
    prompt_halves: Mapping[str, Sequence[str]],
    replica_halves: Mapping[str, Sequence[str]],
    checkpoints: Sequence[int],
) -> dict[str, tuple[Cell, ...]]:
    if set(prompt_halves) != {"P0", "P1"} or set(replica_halves) != {"S0", "S1"}:
        raise ValueError("registered halves must be P0/P1 and S0/S1")
    result: dict[str, tuple[Cell, ...]] = {}
    for p_index in (0, 1):
        for s_index in (0, 1):
            name = f"Q{p_index}{s_index}"
            result[name] = tuple(
                (str(prompt), str(replica), int(checkpoint))
                for prompt in prompt_halves[f"P{p_index}"]
                for replica in replica_halves[f"S{s_index}"]
                for checkpoint in checkpoints
            )
    flattened = [cell for cells in result.values() for cell in cells]
    if len(flattened) != len(set(flattened)):
        raise ValueError("quadrants must be disjoint")
    return result


def crossfit_pairs() -> tuple[tuple[str, str], ...]:
    return (("Q00", "Q11"), ("Q11", "Q00"), ("Q01", "Q10"), ("Q10", "Q01"))


def soft_profile(
    grams: Mapping[Cell, Array],
    lambdas: Sequence[float],
    quadrants: Mapping[str, Sequence[Cell]],
) -> tuple[list[dict[str, Any]], dict[float, dict[Cell, Array]]]:
    """Compute cross-fit soft persistence, dimension, and anisotropy curves."""

    universe = set(grams)
    if set(cell for cells in quadrants.values() for cell in cells) != universe:
        raise ValueError("quadrants must exactly cover the Gram universe")
    projector_cache: dict[float, dict[Cell, Array]] = {}
    rows: list[dict[str, Any]] = []
    for regularization in lambdas:
        lam = float(regularization)
        projectors = {cell: soft_projector(gram, lam) for cell, gram in grams.items()}
        projector_cache[lam] = projectors
        similarities: list[float] = []
        fold_receipts: list[dict[str, Any]] = []
        for fit_name, evaluation_name in crossfit_pairs():
            fitted = np.mean([projectors[cell] for cell in quadrants[fit_name]], axis=0)
            values = [
                soft_similarity(fitted, projectors[cell])
                for cell in quadrants[evaluation_name]
            ]
            similarities.extend(values)
            fold_receipts.append(
                {
                    "fit": fit_name,
                    "evaluation": evaluation_name,
                    "minimum_similarity": float(np.min(values)),
                    "median_similarity": float(np.median(values)),
                }
            )
        dimensions = [effective_dimension(value) for value in projectors.values()]
        anisotropies = [spectral_anisotropy(value) for value in projectors.values()]
        rows.append(
            {
                "lambda": lam,
                "minimum_soft_similarity": float(np.min(similarities)),
                "median_soft_similarity": float(np.median(similarities)),
                "median_effective_dimension": float(np.median(dimensions)),
                "minimum_effective_dimension": float(np.min(dimensions)),
                "maximum_effective_dimension": float(np.max(dimensions)),
                "median_spectral_anisotropy": float(np.median(anisotropies)),
                "informative_fraction_anisotropy_ge_0_10": float(
                    np.mean(np.asarray(anisotropies) >= 0.10)
                ),
                "folds": fold_receipts,
            }
        )
    return rows, projector_cache


def _haar_batch(
    rng: np.random.Generator, draws: int, block_sizes: Sequence[int]
) -> Array:
    dimension = int(sum(block_sizes))
    result = np.zeros((draws, dimension, dimension), dtype=np.float64)
    offset = 0
    for block_size in block_sizes:
        if int(block_size) <= 0:
            raise ValueError("null blocks must be positive")
        matrices = rng.normal(size=(draws, int(block_size), int(block_size)))
        orthogonal, upper = np.linalg.qr(matrices)
        signs = np.sign(np.diagonal(upper, axis1=-2, axis2=-1))
        signs[signs == 0.0] = 1.0
        orthogonal *= signs[:, np.newaxis, :]
        stop = offset + int(block_size)
        result[:, offset:stop, offset:stop] = orthogonal
        offset = stop
    return result


def structured_soft_null(
    projectors_by_lambda: Mapping[float, Mapping[Cell, Array]],
    quadrants: Mapping[str, Sequence[Cell]],
    *,
    draws: int,
    seed: int,
    block_sizes: Sequence[int] = (4, 4, 4),
) -> dict[float, Array]:
    """Matched null that breaks quadrant identity while preserving spectra."""

    if draws < 100:
        raise ValueError("at least 100 null draws are required")
    if not projectors_by_lambda:
        raise ValueError("projector family must be nonempty")
    dimension = next(iter(next(iter(projectors_by_lambda.values())).values())).shape[0]
    if sum(block_sizes) != dimension:
        raise ValueError("null blocks must sum to the probe dimension")
    rng = np.random.default_rng(seed)
    rotations = {
        quadrant: _haar_batch(rng, draws, block_sizes) for quadrant in sorted(quadrants)
    }
    result: dict[float, Array] = {}
    for regularization, projectors in projectors_by_lambda.items():
        draw_minimum = np.full(draws, np.inf, dtype=np.float64)
        for fit_name, evaluation_name in crossfit_pairs():
            fitted = np.mean([projectors[cell] for cell in quadrants[fit_name]], axis=0)
            fitted_norm = float(np.linalg.norm(fitted, "fro"))
            relative = np.einsum(
                "dji,djk->dik",
                rotations[fit_name],
                rotations[evaluation_name],
                optimize=True,
            )
            # Move the fitted operator into each draw's evaluation frame once,
            # then compare all evaluation cells by a batched Frobenius product.
            fitted_in_evaluation_frame = np.einsum(
                "dji,jk,dkl->dil", relative, fitted, relative, optimize=True
            )
            evaluation_stack = np.stack(
                [projectors[cell] for cell in quadrants[evaluation_name]]
            )
            numerators = np.einsum(
                "dij,eij->de",
                fitted_in_evaluation_frame,
                evaluation_stack,
                optimize=True,
            )
            denominators = fitted_norm * np.linalg.norm(
                evaluation_stack, axis=(1, 2)
            )
            similarities = np.clip(
                numerators / np.maximum(denominators[np.newaxis, :], 1e-300),
                0.0,
                1.0,
            )
            draw_minimum = np.minimum(draw_minimum, np.min(similarities, axis=1))
        result[float(regularization)] = draw_minimum
    return result


def prompt_cluster_simultaneous_band(
    values_by_lambda_and_cell: Mapping[float, Mapping[Cell, float]],
    *,
    draws: int,
    seed: int,
    alpha: float,
) -> dict[str, Any]:
    """Prompt-cluster bootstrap with a max-absolute-deviation band."""

    if not values_by_lambda_and_cell:
        raise ValueError("bootstrap values must be nonempty")
    lambdas = tuple(sorted(values_by_lambda_and_cell))
    universe = set(values_by_lambda_and_cell[lambdas[0]])
    if any(set(values_by_lambda_and_cell[lam]) != universe for lam in lambdas):
        raise ValueError("every lambda must share one cell universe")
    prompts = tuple(sorted({cell[0] for cell in universe}))
    if len(prompts) < 4:
        raise ValueError("at least four prompt clusters are required")
    point = np.asarray(
        [np.median(list(values_by_lambda_and_cell[lam].values())) for lam in lambdas],
        dtype=np.float64,
    )
    rng = np.random.default_rng(seed)
    curves = np.empty((draws, len(lambdas)), dtype=np.float64)
    cells_by_prompt = {
        prompt: sorted(cell for cell in universe if cell[0] == prompt)
        for prompt in prompts
    }
    for draw in range(draws):
        sampled = rng.choice(prompts, size=len(prompts), replace=True)
        sampled_cells = [cell for prompt in sampled for cell in cells_by_prompt[str(prompt)]]
        for index, lam in enumerate(lambdas):
            curves[draw, index] = float(
                np.median([values_by_lambda_and_cell[lam][cell] for cell in sampled_cells])
            )
    maximum_deviation = np.max(np.abs(curves - point[np.newaxis, :]), axis=1)
    radius = float(np.quantile(maximum_deviation, 1.0 - alpha))
    return {
        "lambdas": list(lambdas),
        "point": point.tolist(),
        "simultaneous_lower": (point - radius).tolist(),
        "simultaneous_upper": (point + radius).tolist(),
        "max_abs_deviation_radius": radius,
        "draws": int(draws),
        "seed": int(seed),
        "cluster_unit": "prompt",
        "alpha": float(alpha),
    }


def resolve_gate_record(
    *,
    gate_id: str,
    execution_status: str,
    instrument_status: str | None,
    evidential_decision: str | None,
    stop_reason: str | None = None,
) -> dict[str, Any]:
    """Apply the total instrument-to-decision mapping for one gate."""

    if execution_status == "not_reached":
        return {
            "gate_id": gate_id,
            "execution_status": "not_reached",
            "instrument_status": NOT_ASSESSED,
            "gate_decision": "not_evaluated",
            "stop_reason": stop_reason or "stopped_by_upstream_gate",
        }
    if execution_status != "evaluated":
        raise ValueError("execution_status must be evaluated or not_reached")
    if not instrument_status:
        raise ValueError("evaluated gates require instrument_status")
    if instrument_status != VALID_INSTRUMENT:
        return {
            "gate_id": gate_id,
            "execution_status": "evaluated",
            "instrument_status": str(instrument_status),
            "gate_decision": "not_evaluated",
            "stop_reason": stop_reason or f"instrument_not_valid:{instrument_status}",
        }
    if evidential_decision not in {"pass", "fail", "inconclusive"}:
        raise ValueError("a valid instrument requires pass, fail, or inconclusive")
    return {
        "gate_id": gate_id,
        "execution_status": "evaluated",
        "instrument_status": VALID_INSTRUMENT,
        "gate_decision": evidential_decision,
        "stop_reason": None if evidential_decision == "pass" else (
            stop_reason or f"gate_{evidential_decision}"
        ),
    }


def fixed_sequence(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Evaluate ordered per-gate inputs without revising earlier records."""

    output: list[dict[str, Any]] = []
    stopped_by: str | None = None
    for raw in records:
        gate_id = str(raw["gate_id"])
        if stopped_by is not None:
            output.append(
                resolve_gate_record(
                    gate_id=gate_id,
                    execution_status="not_reached",
                    instrument_status=None,
                    evidential_decision=None,
                    stop_reason=f"stopped_by:{stopped_by}",
                )
            )
            continue
        record = resolve_gate_record(
            gate_id=gate_id,
            execution_status=str(raw["execution_status"]),
            instrument_status=(
                None if raw.get("instrument_status") is None else str(raw["instrument_status"])
            ),
            evidential_decision=(
                None if raw.get("evidential_decision") is None else str(raw["evidential_decision"])
            ),
            stop_reason=(None if raw.get("stop_reason") is None else str(raw["stop_reason"])),
        )
        output.append(record)
        if record["gate_decision"] != "pass":
            stopped_by = gate_id
    return output


@dataclass(frozen=True)
class PromptFamilySufficiency:
    minimum_family_count: int = 4
    minimum_prompts_per_family: int = 4
    minimum_independent_replicas_per_prompt: int = 4
    minimum_unordered_prompt_pairs_per_family: int = 6
    minimum_valid_deviation_rows_per_family: int = 16


def evaluate_prompt_family_sufficiency(
    assignments: Mapping[str, str],
    *,
    prompt_universe: Sequence[str],
    independent_replicas_per_prompt: Mapping[str, int],
    criteria: PromptFamilySufficiency = PromptFamilySufficiency(),
) -> dict[str, Any]:
    """Evaluate the frozen prompt-scale availability criterion exactly."""

    prompts = tuple(str(item) for item in prompt_universe)
    assignment_keys = set(assignments)
    universe = set(prompts)
    if assignment_keys - universe:
        raise ValueError("family manifest contains prompts outside the registered universe")
    families: dict[str, list[str]] = {}
    for prompt in prompts:
        if prompt not in assignments:
            continue
        families.setdefault(str(assignments[prompt]), []).append(prompt)
    family_rows: list[dict[str, Any]] = []
    for family, members in sorted(families.items()):
        pair_count = len(members) * (len(members) - 1) // 2
        replica_floor = min(
            (int(independent_replicas_per_prompt.get(prompt, 0)) for prompt in members),
            default=0,
        )
        deviation_rows = sum(
            int(independent_replicas_per_prompt.get(prompt, 0)) for prompt in members
        )
        passed = bool(
            len(members) >= criteria.minimum_prompts_per_family
            and pair_count >= criteria.minimum_unordered_prompt_pairs_per_family
            and replica_floor >= criteria.minimum_independent_replicas_per_prompt
            and deviation_rows >= criteria.minimum_valid_deviation_rows_per_family
        )
        family_rows.append(
            {
                "family_id": family,
                "prompt_count": len(members),
                "unordered_prompt_pairs": pair_count,
                "independent_replica_floor": replica_floor,
                "valid_deviation_rows": deviation_rows,
                "passed": passed,
            }
        )
    passed_family_count = sum(bool(row["passed"]) for row in family_rows)
    complete_assignment = assignment_keys == universe
    available = bool(
        complete_assignment
        and passed_family_count >= criteria.minimum_family_count
    )
    return {
        "status": "available" if available else "unavailable_insufficient_prompt_families",
        "available": available,
        "complete_assignment": complete_assignment,
        "registered_prompt_count": len(prompts),
        "assigned_prompt_count": len(assignment_keys),
        "family_count": len(family_rows),
        "passing_family_count": passed_family_count,
        "criteria": {
            "minimum_family_count": criteria.minimum_family_count,
            "minimum_prompts_per_family": criteria.minimum_prompts_per_family,
            "minimum_independent_replicas_per_prompt": criteria.minimum_independent_replicas_per_prompt,
            "minimum_unordered_prompt_pairs_per_family": criteria.minimum_unordered_prompt_pairs_per_family,
            "minimum_valid_deviation_rows_per_family": criteria.minimum_valid_deviation_rows_per_family,
        },
        "families": family_rows,
    }
