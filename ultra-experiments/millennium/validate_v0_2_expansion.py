"""Structural checks for the additive ASMP v0.2 scope-expansion draft."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOC = ROOT / "V0_2_SCOPE_EXPANSION_DRAFT.md"
REGISTRY = ROOT / "problem_set_v0_2_expansion_draft.json"
INPUT_RECEIPT = ROOT / "V0_2_INPUT_RECEIPT.json"
PARENT_DOC = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
PARENT_REGISTRY = ROOT / "problem_set_v0_1.json"

EXPECTED = {
    "A": ("ASMP-8", "partial_extension"),
    "B": ("ASMP-9", "partial_extension"),
    "C": ("ASMP-10", "distinct"),
    "D": ("ASMP-5A", "subproblem"),
    "E": ("ASMP-11", "partial_extension"),
    "F": ("ASMP-12", "partial_extension"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_utf8(path: Path) -> str:
    payload = path.read_bytes()
    text = payload.decode("utf-8", errors="strict")
    require("\ufffd" not in text, f"replacement character in {path.name}")
    return text


def main() -> int:
    text = read_utf8(DOC)
    registry = json.loads(read_utf8(REGISTRY))
    input_receipt = json.loads(read_utf8(INPUT_RECEIPT))
    parent_text = read_utf8(PARENT_DOC)
    parent_registry = json.loads(read_utf8(PARENT_REGISTRY))

    require(parent_registry["set_id"] == "ASMP-CANDIDATE-SET-v0.1", "wrong parent")
    require(parent_registry["problem_count"] == 7, "parent universe changed")
    parent_headings = re.findall(r"^# ASMP-[1-7] ", parent_text, flags=re.MULTILINE)
    require(len(parent_headings) == 7, "parent Markdown universe changed")
    require(registry["preserves_frozen_parent"] == parent_registry["set_id"], "parent not preserved")
    require(registry["normative"] is False, "draft must not be normative")
    require(registry["supersedes"] is None, "draft must not supersede v0.1")
    require(registry["proposed_top_level_count_after_adoption"] == 12, "top-level count mismatch")
    require(len(registry["proposals"]) == 6, "six proposals required")

    seen_ids: set[str] = set()
    for proposal in registry["proposals"]:
        label = proposal["source_label"]
        require(label in EXPECTED, f"unknown proposal label {label}")
        expected_id, expected_disposition = EXPECTED[label]
        require(proposal["proposed_id"] == expected_id, f"{label} ID mismatch")
        require(proposal["disposition"] == expected_disposition, f"{label} disposition mismatch")
        require(proposal["proposed_id"] not in seen_ids, "duplicate proposed ID")
        seen_ids.add(proposal["proposed_id"])
        require(proposal["canonical_target"], f"{label} lacks target")
        require(proposal["prior_art_correction"], f"{label} lacks correction")
        require(proposal["title"] in text, f"{label} title missing from document")

    bounded_tiling = next(item for item in registry["proposals"] if item["source_label"] == "D")
    require(bounded_tiling["parent_id"] == "ASMP-5", "bounded tiling must remain under ASMP-5")
    require(
        "initial “black-box versus white-box” novelty claim is false" in text.lower(),
        "white-box correction missing",
    )
    require("already proves" in text.lower(), "program-equilibrium correction missing")
    require("prior-art query freeze" in text.lower(), "prior-art-first gate missing")
    require("proves no" in text.lower(), "epistemic boundary missing")
    require(input_receipt["source_bytes"] == 14868, "source byte count changed")
    require(
        input_receipt["source_sha256"]
        == "2006468EAC4758D6DB3FC4914DB76A81AF3E59E1E3B4572A46FBE868B5E1C366",
        "source hash changed",
    )
    require(input_receipt["source_sha256"] in text, "source provenance missing from draft")

    print("ASMP v0.2 scope-expansion validation passed")
    print("proposals=6 proposed_top_level=5 subproblems=1 parent_v0_1_preserved=true")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, UnicodeError) as error:
        print(f"ASMP v0.2 scope-expansion validation failed: {error}")
        raise SystemExit(1)
