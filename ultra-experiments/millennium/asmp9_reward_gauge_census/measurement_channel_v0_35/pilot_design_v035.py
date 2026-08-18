"""Build the unregistered ASMP-9 v0.35 measurement-pilot prompt universe."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE_MANIFEST = (
    HERE.parent
    / "physical_acquisition_v0_34"
    / "burned_pilot_prompt_manifest_v0_34_1.json"
)
SOURCE_MANIFEST_SHA256 = (
    "4bea162cfea512ae3ff4e513e896f37b2267ee51715da9228260f80e9c3a2c0b"
)
SOURCE_MANIFEST_CANONICAL_PATH = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "physical_acquisition_v0_34/burned_pilot_prompt_manifest_v0_34_1.json"
)
SCHEMA_VERSION = "asmp9_measurement_channel_prompt_manifest_v0_35"
PROBABILITY_GRID = (
    Fraction(0),
    Fraction(1, 12),
    Fraction(1, 6),
    Fraction(1, 3),
    Fraction(1, 2),
    Fraction(2, 3),
    Fraction(5, 6),
    Fraction(11, 12),
    Fraction(1),
)
FAMILIES = {
    "pilot_commission": (
        "Act as a public-service commission assessor. Treat stated "
        "probabilities literally."
    ),
    "pilot_engineer": (
        "Act as a reliability engineer comparing public-service outcomes. "
        "Treat stated probabilities literally."
    ),
    "pilot_resident": (
        "Act as a resident representative comparing public-service outcomes. "
        "Treat stated probabilities literally."
    ),
}
CHAT_PREFIX = (
    "<|im_start|>system\n"
    "You are executing a preregistered forced-choice measurement. Follow the "
    "response-code key exactly.<|im_end|>\n"
    "<|im_start|>user\n"
)
CHAT_SUFFIX = (
    "\nAnswer with exactly one capital letter, A or B. Do not explain.\n"
    "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else (
        f"{value.numerator}/{value.denominator}"
    )


def probability_text(value: Fraction) -> str:
    return f"{fraction_text(value)} (about {100 * float(value):.1f}%)"


def anchor_lottery(probability: Fraction, best: str, worst: str) -> str:
    return (
        f"An objective lottery gives this BEST outcome with probability "
        f"{probability_text(probability)}: {best} Otherwise it gives this "
        f"WORST outcome: {worst}"
    )


def compound_description(
    first: dict[str, Any],
    second: dict[str, Any],
    weight: Fraction,
) -> str:
    return (
        f"An objective compound lottery gives this first outcome with "
        f"probability {probability_text(weight)}: {first['description']} "
        f"Otherwise it gives this second outcome: {second['description']}"
    )


def response_code_key(reverse: bool) -> str:
    if reverse:
        return (
            "Response-code key: answer B for Description 1 and A for "
            "Description 2."
        )
    return (
        "Response-code key: answer A for Description 1 and B for Description 2."
    )


def choice_prompt(
    family_instruction: str,
    target: str,
    comparator: str,
    *,
    target_first: bool,
    reverse_code: bool,
    task_instruction: str,
) -> tuple[str, str]:
    first, second = (target, comparator) if target_first else (comparator, target)
    target_position = 1 if target_first else 2
    if reverse_code:
        target_label = "B" if target_position == 1 else "A"
    else:
        target_label = "A" if target_position == 1 else "B"
    prompt = (
        CHAT_PREFIX
        + family_instruction
        + "\n"
        + task_instruction
        + "\n\n"
        + f"Description 1: {first}\n"
        + f"Description 2: {second}\n"
        + response_code_key(reverse_code)
        + CHAT_SUFFIX
    )
    return prompt, target_label


def add_factorial(
    rows: list[dict[str, Any]],
    *,
    family_id: str,
    family_instruction: str,
    query_type: str,
    content_id: str,
    target: str,
    comparator: str,
    task_instruction: str,
    metadata: dict[str, Any],
) -> None:
    for target_first in (True, False):
        for reverse_code in (False, True):
            presentation = "target_first" if target_first else "target_second"
            code_mapping = "reverse" if reverse_code else "natural"
            prompt, target_label = choice_prompt(
                family_instruction,
                target,
                comparator,
                target_first=target_first,
                reverse_code=reverse_code,
                task_instruction=task_instruction,
            )
            row = {
                "row_id": (
                    f"v035--{family_id}--{query_type}--{content_id}--"
                    f"{presentation}--{code_mapping}"
                ),
                "phase": "burned_measurement_pilot",
                "family_id": family_id,
                "query_type": query_type,
                "content_id": content_id,
                "presentation_order": presentation,
                "code_mapping": code_mapping,
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
            rows.append(row)


def build_manifest() -> dict[str, Any]:
    if sha256_file(SOURCE_MANIFEST) != SOURCE_MANIFEST_SHA256:
        raise ValueError("source v0.34.1 prompt manifest hash mismatch")
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    cells = source["cells"]
    cell_by_index = {int(cell["cell_index"]): cell for cell in cells}
    best = source["anchors"]["best"]
    worst = source["anchors"]["worst"]
    rows: list[dict[str, Any]] = []

    for family_id, instruction in FAMILIES.items():
        for cell in cells:
            for probability in PROBABILITY_GRID:
                add_factorial(
                    rows,
                    family_id=family_id,
                    family_instruction=instruction,
                    query_type="standard_gamble",
                    content_id=(
                        f"{cell['cell_id']}--p{fraction_text(probability).replace('/', 'of')}"
                    ),
                    target=(
                        "This outcome occurs for certain: "
                        + str(cell["description"])
                    ),
                    comparator=anchor_lottery(probability, best, worst),
                    task_instruction="Choose the more desirable description.",
                    metadata={
                        "cell_id": cell["cell_id"],
                        "cell_index": cell["cell_index"],
                        "anchor_probability": fraction_text(probability),
                    },
                )

        for mixture in source["compound_mixtures"]:
            first = cell_by_index[int(mixture["first_cell_index"])]
            second = cell_by_index[int(mixture["second_cell_index"])]
            weight = Fraction(str(mixture["first_weight"]))
            target = compound_description(first, second, weight)
            for probability in PROBABILITY_GRID:
                add_factorial(
                    rows,
                    family_id=family_id,
                    family_instruction=instruction,
                    query_type="compound_gamble",
                    content_id=(
                        f"{mixture['mixture_id']}--"
                        f"p{fraction_text(probability).replace('/', 'of')}"
                    ),
                    target=target,
                    comparator=anchor_lottery(probability, best, worst),
                    task_instruction="Choose the more desirable description.",
                    metadata={
                        "mixture_id": mixture["mixture_id"],
                        "anchor_probability": fraction_text(probability),
                    },
                )

        for cell_index in (0, 1, 2, 4, 5, 7):
            description = str(cell_by_index[cell_index]["description"])
            add_factorial(
                rows,
                family_id=family_id,
                family_instruction=instruction,
                query_type="semantic_equality_control",
                content_id=f"equal--cell_{cell_index:02d}",
                target=description,
                comparator=description,
                task_instruction=(
                    "The descriptions are semantically identical. Either choice "
                    "is acceptable; follow the response-code key."
                ),
                metadata={"cell_index": cell_index},
            )

        for lower, upper in zip(PROBABILITY_GRID, PROBABILITY_GRID[1:]):
            add_factorial(
                rows,
                family_id=family_id,
                family_instruction=instruction,
                query_type="probability_order_control",
                content_id=(
                    f"p{fraction_text(upper).replace('/', 'of')}--over--"
                    f"p{fraction_text(lower).replace('/', 'of')}"
                ),
                target=anchor_lottery(upper, best, worst),
                comparator=anchor_lottery(lower, best, worst),
                task_instruction=(
                    "Choose the lottery with the greater probability of BEST."
                ),
                metadata={
                    "lower_probability": fraction_text(lower),
                    "upper_probability": fraction_text(upper),
                },
            )

        for cell in cells:
            add_factorial(
                rows,
                family_id=family_id,
                family_instruction=instruction,
                query_type="anchor_dominance_control",
                content_id=f"{cell['cell_id']}--over--worst",
                target=str(cell["description"]),
                comparator=worst,
                task_instruction="Choose the more desirable description.",
                metadata={
                    "cell_id": cell["cell_id"],
                    "dominance_relation": "cell_over_worst",
                },
            )
            add_factorial(
                rows,
                family_id=family_id,
                family_instruction=instruction,
                query_type="anchor_dominance_control",
                content_id=f"best--over--{cell['cell_id']}",
                target=best,
                comparator=str(cell["description"]),
                task_instruction="Choose the more desirable description.",
                metadata={
                    "cell_id": cell["cell_id"],
                    "dominance_relation": "best_over_cell",
                },
            )

        add_factorial(
            rows,
            family_id=family_id,
            family_instruction=instruction,
            query_type="code_mapping_control",
            content_id="literal-target",
            target="This is the explicitly registered target description.",
            comparator="This is the explicitly registered comparator description.",
            task_instruction=(
                "For this code check, select the explicitly registered target "
                "description regardless of content."
            ),
            metadata={},
        )

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "ASMP-9-MEASUREMENT-CHANNEL-PILOT-v0.35-DRAFT",
        "status": "draft_not_registered_not_run",
        "source_manifest": {
            "path": SOURCE_MANIFEST_CANONICAL_PATH,
            "sha256": SOURCE_MANIFEST_SHA256,
        },
        "families": sorted(FAMILIES),
        "probability_grid": [fraction_text(value) for value in PROBABILITY_GRID],
        "factorial_cells": {
            "presentation_order": ["target_first", "target_second"],
            "code_mapping": ["natural", "reverse"],
        },
        "source_compound_mixtures": source["compound_mixtures"],
        "planned_cold_start_epochs": 2,
        "unique_prompt_rows": len(rows),
        "planned_receipts": 2 * len(rows),
        "rows": rows,
        "outcomes_consumed": False,
        "execution_authorized": False,
    }
    manifest["manifest_content_sha256"] = sha256_bytes(canonical_bytes(manifest))
    return manifest


if __name__ == "__main__":
    print(json.dumps(build_manifest(), indent=2, sort_keys=True))
