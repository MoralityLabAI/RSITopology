"""Total component-to-composite mapping for proposal-recursion gate v2.

Each component state already includes its own instrument validity:

* pass, fail, and inconclusive are scientific decisions from valid instruments;
* unavailable means the registered component was never measurable; and
* invalid means the component instrument failed validation.

A composite gate is a conjunction of two necessary components.  One valid
component failure is therefore sufficient to fail the conjunction even when
the other component is unavailable or invalid.  Consequences remain a list;
the evaluator never selects or invents one "dominant" component.
"""

from __future__ import annotations

from itertools import product
from typing import Any, Mapping, Sequence


COMPONENT_STATES = ("pass", "fail", "inconclusive", "unavailable", "invalid")

STATE_CONSEQUENCES: dict[str, dict[str, str]] = {
    "pass": {
        "evidence": "valid_component_pass",
        "extension_right": "preserve_pass_no_component_retest",
    },
    "fail": {
        "evidence": "valid_component_fail",
        "extension_right": "new_protocol_or_hypothesis_with_fresh_holdout",
    },
    "inconclusive": {
        "evidence": "valid_component_inconclusive",
        "extension_right": "versioned_fresh_disjoint_holdout_for_component_no_pooling",
    },
    "unavailable": {
        "evidence": "component_not_measured",
        "extension_right": "preregister_missing_component_instrument_and_collect_first_measurement",
    },
    "invalid": {
        "evidence": "component_instrument_invalid",
        "extension_right": "repair_instrument_under_versioned_prereveal_artifact_and_rerun_component",
    },
}


def composite_decision(left: str, right: str) -> str:
    """Return the registered decision for every ordered pair of states."""

    states = (str(left), str(right))
    if any(state not in COMPONENT_STATES for state in states):
        raise ValueError(f"unknown component state: {states}")
    if "fail" in states:
        return "fail"
    if states == ("pass", "pass"):
        return "pass"
    if "unavailable" in states or "invalid" in states:
        return "not_evaluated"
    return "inconclusive"


def composite_record(components: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Materialize a composite record without consequence ranking."""

    if len(components) != 2:
        raise ValueError("v2 composite gates require exactly two components")
    ids = [str(item["component_id"]) for item in components]
    if len(set(ids)) != 2:
        raise ValueError("component ids must be unique")
    states = [str(item["state"]) for item in components]
    decision = composite_decision(states[0], states[1])
    consequences = [
        {
            "component_id": component_id,
            "state": state,
            **STATE_CONSEQUENCES[state],
        }
        for component_id, state in zip(ids, states)
    ]
    stop_reasons = [
        f"{component_id}_{state}" for component_id, state in zip(ids, states) if state != "pass"
    ]
    return {
        "component_records": [
            {"component_id": component_id, "state": state}
            for component_id, state in zip(ids, states)
        ],
        "composite_decision": decision,
        "sequence_action": "advance" if decision == "pass" else "stop",
        "stop_reasons": stop_reasons,
        "component_consequences": consequences,
        "consequence_ranking_applied": False,
    }


def total_mapping_table() -> list[dict[str, str]]:
    """Return all 25 ordered state cells in frozen lexical state order."""

    return [
        {
            "left_state": left,
            "right_state": right,
            "composite_decision": composite_decision(left, right),
            "sequence_action": (
                "advance" if composite_decision(left, right) == "pass" else "stop"
            ),
        }
        for left, right in product(COMPONENT_STATES, repeat=2)
    ]
