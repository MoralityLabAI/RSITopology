from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.recursive_gate import (
    NOT_ASSESSED,
    PromptFamilySufficiency,
    effective_dimension,
    evaluate_prompt_family_sufficiency,
    fixed_sequence,
    measurement_edges,
    measurement_noise_scale,
    psd_square_root,
    resolve_gate_record,
    response_gram,
    soft_projector,
    soft_similarity,
    spectral_anisotropy,
    structured_soft_null,
)


def test_response_gram_and_square_root_are_right_gauge_invariant() -> None:
    rng = np.random.default_rng(7)
    signature = rng.normal(size=(5, 3))
    rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    left = response_gram([signature])
    right = response_gram([signature @ rotation])
    assert np.allclose(left, right, atol=1e-12)
    root = psd_square_root(left)
    assert np.allclose(root @ root, left, atol=1e-10)


def test_soft_projector_has_continuous_dimension_and_flatness_gate() -> None:
    gram = np.diag([9.0, 4.0, 1.0, 0.0])
    projector = soft_projector(gram, 1.0)
    assert effective_dimension(projector) == pytest.approx(0.9 + 0.8 + 0.5)
    assert soft_similarity(projector, projector) == pytest.approx(1.0)
    assert spectral_anisotropy(np.eye(4) * 0.8) == pytest.approx(0.0)
    assert spectral_anisotropy(np.diag([1.0, 0.0, 0.0, 0.0])) > 0.8


def test_measurement_edge_universe_and_noise_scale() -> None:
    prompts = ["p0", "p1"]
    replicas = ["a0", "a1", "b0", "b1"]
    checkpoints = [1, 4, 8]
    edges = measurement_edges(prompts, replicas, checkpoints)
    assert len(edges) == 28
    cells = {
        (prompt, replica, checkpoint): np.eye(2) * (1.0 + 0.01 * checkpoint)
        for prompt in prompts
        for replica in replicas
        for checkpoint in checkpoints
    }
    scale, values = measurement_noise_scale(cells, edges)
    assert len(values) == 28
    assert scale > 0.0


def test_total_mapping_forces_invalid_instrument_to_not_evaluated() -> None:
    record = resolve_gate_record(
        gate_id="G3",
        execution_status="evaluated",
        instrument_status="invalid_provenance",
        evidential_decision="pass",
    )
    assert record["gate_decision"] == "not_evaluated"
    assert record["instrument_status"] == "invalid_provenance"


def test_fixed_sequence_preserves_earlier_pass_and_stops_downstream() -> None:
    records = fixed_sequence(
        [
            {
                "gate_id": "G1",
                "execution_status": "evaluated",
                "instrument_status": "valid",
                "evidential_decision": "pass",
            },
            {
                "gate_id": "G2",
                "execution_status": "evaluated",
                "instrument_status": "invalid_provenance",
                "evidential_decision": None,
            },
            {
                "gate_id": "G3",
                "execution_status": "evaluated",
                "instrument_status": "valid",
                "evidential_decision": "pass",
            },
        ]
    )
    assert records[0]["gate_decision"] == "pass"
    assert records[1]["gate_decision"] == "not_evaluated"
    assert records[2]["instrument_status"] == NOT_ASSESSED
    assert records[2]["gate_decision"] == "not_evaluated"


def test_prompt_family_availability_is_numeric_and_total() -> None:
    prompts = [f"p{i}" for i in range(16)]
    assignments = {prompt: f"b{index // 4}" for index, prompt in enumerate(prompts)}
    replicas = {prompt: 4 for prompt in prompts}
    passed = evaluate_prompt_family_sufficiency(
        assignments,
        prompt_universe=prompts,
        independent_replicas_per_prompt=replicas,
        criteria=PromptFamilySufficiency(),
    )
    assert passed["available"] is True
    failed = evaluate_prompt_family_sufficiency(
        {},
        prompt_universe=prompts[:8],
        independent_replicas_per_prompt={prompt: 4 for prompt in prompts[:8]},
    )
    assert failed["status"] == "unavailable_insufficient_prompt_families"


def test_structured_soft_null_is_seeded_and_spectrum_matched() -> None:
    quadrants = {
        "Q00": (("p0", "a0", 1),),
        "Q01": (("p0", "b0", 1),),
        "Q10": (("p1", "a0", 1),),
        "Q11": (("p1", "b0", 1),),
    }
    projectors = {
        cell: np.diag([0.95, 0.8, 0.2, 0.05])
        for cells in quadrants.values()
        for cell in cells
    }
    first = structured_soft_null(
        {1.0: projectors}, quadrants, draws=100, seed=19, block_sizes=(2, 2)
    )[1.0]
    second = structured_soft_null(
        {1.0: projectors}, quadrants, draws=100, seed=19, block_sizes=(2, 2)
    )[1.0]
    assert first.shape == (100,)
    assert np.array_equal(first, second)
    assert np.all((first >= 0.0) & (first <= 1.0))
