"""Frozen CPU fixtures and gates for edit sectioning."""

from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any, Literal

import numpy as np

from .sectioning import (
    GridEdgeReceipt,
    PlaquetteReceipt,
    SectioningInput,
    persistence_curve,
    rank_audit_placements,
    section_edits,
)


def _rotation(angle: float) -> tuple[tuple[float, ...], ...]:
    return (
        (float(np.cos(angle)), float(-np.sin(angle))),
        (float(np.sin(angle)), float(np.cos(angle))),
    )


def build_sectioning_fixture(
    mode: Literal["mixed_curvature", "uniformly_curved", "audit_incomplete"]
) -> SectioningInput:
    columns = 9
    low_loss, high_loss = 0.01, 0.20
    if mode == "mixed_curvature" or mode == "audit_incomplete":
        losses = [low_loss] * 4 + [high_loss] + [low_loss] * 4
    elif mode == "uniformly_curved":
        losses = [high_loss] * columns
    else:
        raise ValueError("unknown fixture mode")

    edges: list[GridEdgeReceipt] = []
    for row in range(2):
        for column in range(columns):
            loss = 0.0 if row == 0 else losses[column]
            angle = float(np.arccos(1.0 - loss))
            edges.append(
                GridEdgeReceipt(
                    edge_id=f"h-{row}-{column}",
                    source_node=f"n-{row}-{column}",
                    target_node=f"n-{row}-{column + 1}",
                    transport_matrix=_rotation(angle),
                    mean_edge_chordal_lineage=0.995,
                    minimum_edge_worst_direction_retention=0.9900332889206206,
                )
            )
    for column in range(columns + 1):
        edges.append(
            GridEdgeReceipt(
                edge_id=f"v-{column}",
                source_node=f"n-0-{column}",
                target_node=f"n-1-{column}",
                transport_matrix=_rotation(0.0),
                mean_edge_chordal_lineage=0.995,
                minimum_edge_worst_direction_retention=0.9900332889206206,
            )
        )

    cells = []
    for column, loss in enumerate(losses):
        measured = not (mode == "audit_incomplete" and column in (3, 4, 5))
        if measured:
            lower = max(0.0, loss - 0.002)
            upper = min(2.0, loss + 0.002)
        elif column == 4:
            lower, upper = 0.02, 0.24
        else:
            lower, upper = 0.005, 0.08
        cells.append(
            PlaquetteReceipt(
                plaquette_id=f"p-{column}",
                row=0,
                column=column,
                node_ids=(
                    f"n-0-{column}",
                    f"n-0-{column + 1}",
                    f"n-1-{column + 1}",
                    f"n-1-{column}",
                ),
                edge_ids=(f"h-0-{column}", f"v-{column + 1}", f"h-1-{column}", f"v-{column}"),
                measured=measured,
                identity_loss=loss if measured else None,
                identity_loss_lower_bound=lower,
                identity_loss_upper_bound=upper,
                det_h_flag=False,
                determinant_reversal_probability=0.0 if measured else (0.02 if column != 4 else 0.10),
            )
        )
    return SectioningInput(
        grid_id=f"sectioning-{mode}-v1",
        rank=2,
        edges=tuple(edges),
        plaquettes=tuple(cells),
        reference_coordinate=(1.0, 0.0),
    )


def _utility_gate(plan: dict[str, Any], *, replicates: int = 128, seed: int = 20260712) -> dict[str, Any]:
    eligible_cells = [cell for patch in plan["patches"] for cell in patch["plaquette_ids"]]
    patch_for_cell = {
        cell: patch["patch_id"] for patch in plan["patches"] for cell in patch["plaquette_ids"]
    }
    true = {
        cell: (np.array([1.0, 0.0]) if int(cell.split("-")[1]) < 4 else np.array([0.0, 1.0]))
        for cell in eligible_cells
    }
    rng = np.random.default_rng(seed)
    rows = []
    scale = 1.0 / np.sqrt(len(eligible_cells))
    for replicate in range(replicates):
        observed = {}
        for cell in eligible_cells:
            vector = true[cell] + 0.8 * rng.normal(size=2)
            observed[cell] = vector / np.linalg.norm(vector)
        global_vector = np.sum(list(observed.values()), axis=0)
        global_vector /= np.linalg.norm(global_vector)
        patch_vectors = {}
        for patch_id in sorted(set(patch_for_cell.values())):
            vector = np.sum(
                [observed[cell] for cell in eligible_cells if patch_for_cell[cell] == patch_id], axis=0
            )
            patch_vectors[patch_id] = vector / np.linalg.norm(vector)
        estimates = {
            "patch_plan": {cell: patch_vectors[patch_for_cell[cell]] for cell in eligible_cells},
            "one_global_edit": {cell: global_vector for cell in eligible_cells},
            "per_context_independent": observed,
        }
        utilities = {}
        norms = {}
        for name, estimate in estimates.items():
            utilities[name] = -float(
                sum(np.sum((scale * estimate[cell] - scale * true[cell]) ** 2) for cell in eligible_cells)
            )
            norms[name] = float(sum(np.sum((scale * estimate[cell]) ** 2) for cell in eligible_cells))
        rows.append(
            {
                "heldout_group": replicate,
                **utilities,
                "patch_minus_global": utilities["patch_plan"] - utilities["one_global_edit"],
                "patch_minus_independent": utilities["patch_plan"] - utilities["per_context_independent"],
                "norms": norms,
            }
        )
    margins = {}
    for name in ("patch_minus_global", "patch_minus_independent"):
        values = np.array([row[name] for row in rows])
        boot = np.random.default_rng(seed + (1 if name.endswith("global") else 2)).choice(
            values, size=(4096, len(values)), replace=True
        ).mean(axis=1)
        margins[name] = {
            "mean": float(np.mean(values)),
            "bootstrap_95_ci": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
        }
    total_rank = len(eligible_cells)
    return {
        "group_count": replicates,
        "matched_total_rank": {
            "patch_plan": total_rank,
            "one_global_edit": total_rank,
            "per_context_independent": total_rank,
            "patch_padding_rule": "allocate total rank across patches proportional to cell count; only the registered signed coordinate is active",
        },
        "matched_total_squared_norm": 1.0,
        "maximum_observed_norm_error": max(
            abs(row["norms"][name] - 1.0) for row in rows for name in row["norms"]
        ),
        "utility_margins": margins,
        "gate_pass": all(item["bootstrap_95_ci"][0] > 0.0 for item in margins.values()),
    }


def run_frozen_sectioning_gates() -> dict[str, Any]:
    budget = 0.05
    mixed = build_sectioning_fixture("mixed_curvature")
    mixed_plan = section_edits(mixed, budget)
    utility = _utility_gate(mixed_plan)

    negative = build_sectioning_fixture("uniformly_curved")
    negative_plan = section_edits(negative, budget)
    negative_pass = (
        negative_plan["status"] == "no_admissible_multi_patch_section"
        and negative_plan["edit_count"] == 0
    )

    rng = np.random.default_rng(20260712)
    counts = []
    for _ in range(128):
        noisy_cells = []
        noisy_edges = list(mixed.edges)
        for item in mixed.plaquettes:
            perturbation = float(rng.normal(scale=0.004))
            center = float(np.clip(item.identity_loss + perturbation, 0.0, 2.0))
            noisy_cells.append(
                replace(
                    item,
                    identity_loss=center,
                    identity_loss_lower_bound=max(0.0, center - 0.002),
                    identity_loss_upper_bound=min(2.0, center + 0.002),
                )
            )
            edge_id = f"h-1-{item.column}"
            edge_index = next(index for index, edge in enumerate(noisy_edges) if edge.edge_id == edge_id)
            noisy_edges[edge_index] = replace(
                noisy_edges[edge_index],
                transport_matrix=_rotation(float(np.arccos(1.0 - center))),
            )
        counts.append(
            section_edits(
                replace(mixed, edges=tuple(noisy_edges), plaquettes=tuple(noisy_cells)), budget
            )["edit_count"]
        )
    band = [int(np.quantile(counts, 0.025)), int(np.quantile(counts, 0.975))]
    noise_pass = band[0] <= mixed_plan["edit_count"] <= band[1]

    incomplete = build_sectioning_fixture("audit_incomplete")
    audit = rank_audit_placements(incomplete, budget)
    curve = persistence_curve(mixed, (0.0, 0.005, 0.012, 0.02, 0.05, 0.10, 0.202, 0.25))
    gates = {
        "mixed_patch_count": mixed_plan["edit_count"],
        "mixed_patch_status": mixed_plan["status"],
        "utility": utility,
        "uniformly_curved_negative_control": {
            "status": negative_plan["status"],
            "edit_count": negative_plan["edit_count"],
            "gate_pass": negative_pass,
        },
        "estimation_noise_stability": {
            "replicates": 128,
            "seed": 20260712,
            "patch_count_exceedance_band": band,
            "observed_patch_count": mixed_plan["edit_count"],
            "gate_pass": noise_pass,
        },
    }
    return {
        "schema_version": "1.0.0",
        "protocol_id": "edit_sectioning_synthetic_v0_1",
        "gates": gates,
        "all_gates_pass": utility["gate_pass"] and negative_pass and noise_pass and mixed_plan["edit_count"] == 2,
        "mixed_plan": mixed_plan,
        "negative_control_plan": negative_plan,
        "persistence": curve,
        "audit_placement": audit,
        "claim_boundary": "CPU synthetic fixtures only; no transformer or improvement claim.",
    }
