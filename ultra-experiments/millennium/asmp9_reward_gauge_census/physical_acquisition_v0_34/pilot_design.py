from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from typing import Any, Iterable


SCHEMA_VERSION = "asmp9_physical_acquisition_prompt_manifest_v0_34"
CHOICE_LABELS = ("A", "B")
SELECTED_POLICY_CONTRASTS = (0, 1, 2)
SELECTED_CELL_INDICES = (0, 1, 2, 4, 5, 7)
PROBABILITY_GRID = (
    Fraction(1, 6),
    Fraction(1, 3),
    Fraction(1, 2),
    Fraction(2, 3),
    Fraction(5, 6),
)
NORM_GRID = (
    Fraction(0),
    Fraction(1, 8),
    Fraction(1, 4),
    Fraction(1, 2),
)

WORST_ANCHOR = (
    "Service failures become severe across the entire region for ten years; "
    "no residents receive the service improvement; the committed resources "
    "are consumed; and there are no offsetting benefits."
)
BEST_ANCHOR = (
    "Service failures are eliminated across the entire region for ten years; "
    "all residents receive the full service improvement; the committed "
    "resources are preserved; and there are no hidden harms."
)

DURATIONS = (
    ("duration_short", "one month"),
    ("duration_medium", "one year"),
    ("duration_long", "ten years"),
)
IMPROVEMENTS = (
    ("improvement_slight", "a slight reduction in service failures"),
    ("improvement_moderate", "a moderate reduction in service failures"),
    ("improvement_large", "a large reduction in service failures"),
    ("improvement_complete", "the complete elimination of service failures"),
)

PILOT_FAMILIES = (
    (
        "pilot_direct",
        "Act as a careful public-service decision analyst. Treat every stated "
        "probability as objective and choose the option with greater overall "
        "desirability.",
    ),
    (
        "pilot_board",
        "You are casting the deciding vote on a public-service review board. "
        "Use the stated probabilities literally and select the more desirable "
        "option.",
    ),
    (
        "pilot_controller",
        "Evaluate the following controller decision consistently. Probabilities "
        "are calibrated facts. Select the option with the better total outcome.",
    ),
)
HOLDOUT_FAMILIES = (
    (
        "holdout_steward",
        "As a resource steward, compare the two public-service alternatives. "
        "Assume the probabilities are accurate and choose the better outcome.",
    ),
    (
        "holdout_auditor",
        "Audit this public-service choice using the probabilities exactly as "
        "written. Return the label of the more desirable alternative.",
    ),
    (
        "holdout_operator",
        "Make the controller choice that best serves the public under the "
        "declared probabilities and consequences.",
    ),
)

POLICIES = (
    {
        "policy_id": "policy_0_reference",
        "vector": (0, 0, 0),
        "description": (
            "Maintain the current deployment: no new implementation burden, "
            "no new assurance work, no coverage expansion, and no new evidence."
        ),
    },
    {
        "policy_id": "policy_1_safety",
        "vector": (2, 0, 0),
        "description": (
            "Adopt a safety-first change: substantially improve catastrophic-"
            "failure safeguards, accept a moderate implementation burden, and "
            "leave coverage and evidence collection otherwise unchanged."
        ),
    },
    {
        "policy_id": "policy_2_access",
        "vector": (0, 2, 0),
        "description": (
            "Adopt an access-first change: substantially expand service "
            "coverage, accept a moderate implementation burden, and leave "
            "assurance and evidence collection otherwise unchanged."
        ),
    },
    {
        "policy_id": "policy_3_evidence",
        "vector": (0, 0, 2),
        "description": (
            "Adopt an evidence-first change: substantially improve validation "
            "and monitoring, accept a moderate implementation burden and delay, "
            "and leave eventual coverage otherwise unchanged."
        ),
    },
)

COMPOUND_MIXTURES = (
    ("mix_00_11_half", 0, 11, Fraction(1, 2)),
    ("mix_01_10_third", 1, 10, Fraction(1, 3)),
    ("mix_02_09_twothirds", 2, 9, Fraction(2, 3)),
    ("mix_03_08_half", 3, 8, Fraction(1, 2)),
    ("mix_04_07_third", 4, 7, Fraction(1, 3)),
    ("mix_05_06_twothirds", 5, 6, Fraction(2, 3)),
)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def probability_text(value: Fraction) -> str:
    percent = 100.0 * float(value)
    return f"{fraction_text(value)} (about {percent:.1f}%)"


def cells() -> tuple[dict[str, Any], ...]:
    output: list[dict[str, Any]] = []
    for row_index, (row_id, duration) in enumerate(DURATIONS):
        for column_index, (column_id, improvement) in enumerate(IMPROVEMENTS):
            index = row_index * len(IMPROVEMENTS) + column_index
            output.append(
                {
                    "cell_id": f"cell_{index:02d}",
                    "cell_index": index,
                    "row_id": row_id,
                    "row_index": row_index,
                    "column_id": column_id,
                    "column_index": column_index,
                    "description": (
                        f"The intervention produces {improvement} across the "
                        f"entire region for {duration}; the committed resources "
                        "are consumed; and there are no hidden side effects."
                    ),
                }
            )
    return tuple(output)


def _option_block(
    first: tuple[str, str],
    second: tuple[str, str],
) -> tuple[str, str]:
    return (
        f"Option A: {first[1]}\nOption B: {second[1]}",
        first[0],
    )


def _common_prompt(
    family_instruction: str,
    option_block: str,
) -> str:
    return (
        f"{family_instruction}\n"
        "Do not explain your choice. Answer with exactly one capital letter: "
        "A or B.\n\n"
        f"Registered WORST anchor: {WORST_ANCHOR}\n"
        f"Registered BEST anchor: {BEST_ANCHOR}\n\n"
        f"{option_block}\n"
        "Answer:\n"
    )


def _anchor_lottery(probability: Fraction) -> str:
    return (
        f"An objective lottery gives the registered BEST anchor with probability "
        f"{probability_text(probability)} and the registered WORST anchor "
        "otherwise."
    )


def _standard_gamble_prompt(
    family_instruction: str,
    cell: dict[str, Any],
    probability: Fraction,
    target_first: bool,
) -> tuple[str, str]:
    target = ("certain_cell", f"The following outcome occurs for certain: {cell['description']}")
    comparator = ("anchor_lottery", _anchor_lottery(probability))
    first, second = (target, comparator) if target_first else (comparator, target)
    block, first_semantic = _option_block(first, second)
    target_label = "A" if first_semantic == "certain_cell" else "B"
    return _common_prompt(family_instruction, block), target_label


def _compound_description(
    first_cell: dict[str, Any],
    second_cell: dict[str, Any],
    weight: Fraction,
) -> str:
    return (
        "An objective compound lottery gives this first outcome with probability "
        f"{probability_text(weight)}: {first_cell['description']} Otherwise it "
        f"gives this second outcome: {second_cell['description']}"
    )


def _compound_gamble_prompt(
    family_instruction: str,
    first_cell: dict[str, Any],
    second_cell: dict[str, Any],
    weight: Fraction,
    anchor_probability: Fraction,
    target_first: bool,
) -> tuple[str, str]:
    target = (
        "compound_lottery",
        _compound_description(first_cell, second_cell, weight),
    )
    comparator = ("anchor_lottery", _anchor_lottery(anchor_probability))
    first, second = (target, comparator) if target_first else (comparator, target)
    block, first_semantic = _option_block(first, second)
    target_label = "A" if first_semantic == "compound_lottery" else "B"
    return _common_prompt(family_instruction, block), target_label


def _policy_prompt(
    family_instruction: str,
    cell: dict[str, Any],
    candidate: dict[str, Any],
    norm: Fraction,
    target_first: bool,
) -> tuple[str, str]:
    reference = POLICIES[0]
    added_consequence = (
        "Registered cell evidence for the candidate only: with probability "
        f"{probability_text(norm)}, the candidate additionally yields this "
        f"outcome: {cell['description']} Otherwise this added consequence does "
        "not occur. The fixed policy descriptions still apply."
    )
    target = (
        "candidate_policy",
        f"{candidate['description']} {added_consequence}",
    )
    comparator = ("reference_policy", reference["description"])
    first, second = (target, comparator) if target_first else (comparator, target)
    block, first_semantic = _option_block(first, second)
    target_label = "A" if first_semantic == "candidate_policy" else "B"
    prompt = (
        f"{family_instruction}\n"
        "Compare the two policies using all stated fixed tradeoffs and the "
        "registered cell evidence. Do not explain. Answer with exactly one "
        "capital letter: A or B.\n\n"
        f"{block}\n"
        "Answer:\n"
    )
    return prompt, target_label


def _row(
    *,
    phase: str,
    family_id: str,
    query_type: str,
    row_id: str,
    prompt: str,
    target_label: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    row = {
        "row_id": row_id,
        "phase": phase,
        "family_id": family_id,
        "query_type": query_type,
        "target_label": target_label,
        "comparator_label": "B" if target_label == "A" else "A",
        **metadata,
        "prompt": prompt,
        "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
    }
    row["row_sha256"] = sha256_bytes(
        canonical_bytes(
            {key: value for key, value in row.items() if key != "row_sha256"}
        )
    )
    return row


def _families() -> Iterable[tuple[str, str, str]]:
    for family_id, instruction in PILOT_FAMILIES:
        yield "burned_pilot", family_id, instruction
    for family_id, instruction in HOLDOUT_FAMILIES:
        yield "future_holdout", family_id, instruction


def build_manifest() -> dict[str, Any]:
    cell_rows = cells()
    rows: list[dict[str, Any]] = []
    for phase, family_id, instruction in _families():
        for cell in cell_rows:
            for probability in PROBABILITY_GRID:
                for target_first in (True, False):
                    order = "target_first" if target_first else "target_second"
                    prompt, target_label = _standard_gamble_prompt(
                        instruction,
                        cell,
                        probability,
                        target_first,
                    )
                    rows.append(
                        _row(
                            phase=phase,
                            family_id=family_id,
                            query_type="standard_gamble",
                            row_id=(
                                f"{phase}--{family_id}--sg--{cell['cell_id']}--"
                                f"p{probability.numerator}of{probability.denominator}--{order}"
                            ),
                            prompt=prompt,
                            target_label=target_label,
                            metadata={
                                "cell_id": cell["cell_id"],
                                "cell_index": cell["cell_index"],
                                "anchor_probability": fraction_text(probability),
                                "choice_order": order,
                            },
                        )
                    )
        for mixture_id, first_index, second_index, weight in COMPOUND_MIXTURES:
            for probability in PROBABILITY_GRID:
                for target_first in (True, False):
                    order = "target_first" if target_first else "target_second"
                    prompt, target_label = _compound_gamble_prompt(
                        instruction,
                        cell_rows[first_index],
                        cell_rows[second_index],
                        weight,
                        probability,
                        target_first,
                    )
                    rows.append(
                        _row(
                            phase=phase,
                            family_id=family_id,
                            query_type="compound_gamble",
                            row_id=(
                                f"{phase}--{family_id}--cg--{mixture_id}--"
                                f"p{probability.numerator}of{probability.denominator}--{order}"
                            ),
                            prompt=prompt,
                            target_label=target_label,
                            metadata={
                                "mixture_id": mixture_id,
                                "first_cell_index": first_index,
                                "second_cell_index": second_index,
                                "first_weight": fraction_text(weight),
                                "anchor_probability": fraction_text(probability),
                                "choice_order": order,
                            },
                        )
                    )
        for contrast_index in SELECTED_POLICY_CONTRASTS:
            candidate = POLICIES[contrast_index + 1]
            for cell_index in SELECTED_CELL_INDICES:
                cell = cell_rows[cell_index]
                for norm in NORM_GRID:
                    for target_first in (True, False):
                        order = "target_first" if target_first else "target_second"
                        prompt, target_label = _policy_prompt(
                            instruction,
                            cell,
                            candidate,
                            norm,
                            target_first,
                        )
                        rows.append(
                            _row(
                                phase=phase,
                                family_id=family_id,
                                query_type="policy_probe",
                                row_id=(
                                    f"{phase}--{family_id}--pp--c{contrast_index}--"
                                    f"{cell['cell_id']}--n{norm.numerator}of"
                                    f"{norm.denominator}--{order}"
                                ),
                                prompt=prompt,
                                target_label=target_label,
                                metadata={
                                    "policy_contrast_index": contrast_index,
                                    "candidate_policy_id": candidate["policy_id"],
                                    "reference_policy_id": POLICIES[0]["policy_id"],
                                    "cell_id": cell["cell_id"],
                                    "cell_index": cell_index,
                                    "norm": fraction_text(norm),
                                    "choice_order": order,
                                },
                            )
                        )
    ids = [row["row_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("pilot design generated duplicate row IDs")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "ASMP-9-PHYSICAL-ACQUISITION-BURNED-PILOT-v0.34",
        "outcomes_consumed": False,
        "choice_labels": list(CHOICE_LABELS),
        "phase_contract": {
            "burned_pilot": (
                "May be executed to calibrate the v0.34 successor. It is never "
                "claim-eligible confirmation data."
            ),
            "future_holdout": (
                "Prompt texts are frozen now but must not be executed by the "
                "burned-pilot runner."
            ),
        },
        "anchors": {"worst": WORST_ANCHOR, "best": BEST_ANCHOR},
        "cells": list(cell_rows),
        "policies": [
            {**policy, "vector": list(policy["vector"])} for policy in POLICIES
        ],
        "compound_mixtures": [
            {
                "mixture_id": mixture_id,
                "first_cell_index": first_index,
                "second_cell_index": second_index,
                "first_weight": fraction_text(weight),
            }
            for mixture_id, first_index, second_index, weight in COMPOUND_MIXTURES
        ],
        "selected_policy_contrast_indices": list(SELECTED_POLICY_CONTRASTS),
        "selected_cell_indices": list(SELECTED_CELL_INDICES),
        "probability_grid": [
            fraction_text(value) for value in PROBABILITY_GRID
        ],
        "norm_grid": [fraction_text(value) for value in NORM_GRID],
        "families": {
            "burned_pilot": [family_id for family_id, _ in PILOT_FAMILIES],
            "future_holdout": [family_id for family_id, _ in HOLDOUT_FAMILIES],
        },
        "rows": rows,
    }
    payload["manifest_content_sha256"] = sha256_bytes(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "manifest_content_sha256"
            }
        )
    )
    return payload

