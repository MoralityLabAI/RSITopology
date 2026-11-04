"""Import-independent verifier for ASMP-4 v0.21 support quotient."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V20 = (
    ROOT
    / "asmp4_sensor_refinement_inflation_stop_v0_20"
    / "sensor_refinement_stop_claim_v0_20.json"
)
CONTRACT = HERE / "support_incidence_quotient_contract_v0_21.json"
CLAIM = HERE / "support_incidence_quotient_claim_v0_21.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V20: "b06213d846b53cf7f2262b7f0cf3dea89f22ca5f679ec8e87d5fd88e13de7d8f",
}

TEST_FILES = (
    ("asmp4_capacity_definition_audit", "test_capacity_definition_audit.py"),
    ("asmp4_two_port_game", "test_two_port_game.py"),
    ("asmp4_serial_collapse_theorem_v0_2", "test_serial_capacity.py"),
    ("asmp4_metric_robust_collapse_v0_3", "test_metric_harness.py"),
    ("asmp4_heterogeneous_port_costs_v0_4", "test_heterogeneous_frontier.py"),
    ("asmp4_adaptive_history_collapse_v0_5", "test_adaptive_frontier.py"),
    ("asmp4_registration_fork_v0_6", "test_registration_fork.py"),
    ("asmp4_relational_action_frontier_v0_7", "test_relational_frontier.py"),
    ("asmp4_randomness_quantifier_boundary_v0_8", "test_randomness_quantifier.py"),
    ("asmp4_completion_atlas_v0_9", "test_completion_atlas.py"),
    ("asmp4_stopping_red_team_v0_10", "test_stopping_red_team.py"),
    ("asmp4_nhim_cocycle_audit_v0_11", "test_nhim_cocycle_audit.py"),
    ("asmp4_positive_dimensional_nhim_v0_12", "test_positive_dimensional_nhim.py"),
    ("asmp4_positive_volume_collar_v0_13", "test_positive_volume_collar.py"),
    (
        "asmp4_positive_volume_stop_certificate_v0_14",
        "test_positive_volume_stop.py",
    ),
    ("asmp4_semantic_selector_audit_v0_15", "test_semantic_selector_audit.py"),
    (
        "asmp4_registered_sensor_classification_v0_16",
        "test_registered_sensor_classification.py",
    ),
    (
        "asmp4_zero_error_sensor_kernels_v0_17",
        "test_zero_error_sensor_kernels.py",
    ),
    (
        "asmp4_finite_state_sensor_transducers_v0_18",
        "test_finite_state_sensor_transducers.py",
    ),
    (
        "asmp4_uncertain_initial_sensor_state_v0_19",
        "test_uncertain_initial_sensor_state.py",
    ),
    (
        "asmp4_sensor_refinement_inflation_stop_v0_20",
        "test_sensor_refinement_inflation_stop.py",
    ),
)

Event = tuple[int, int]
Support = dict[tuple[int, int], tuple[Event, ...]]
Signature = tuple[tuple[int, int, int], ...]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ceil(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append((path.name, observed == expected))
    return {"rows": rows, "pass": all(match for _, match in rows)}


def _signatures(
    support: Support, outputs: tuple[int, ...], states: tuple[int, ...]
) -> dict[int, Signature]:
    result = {}
    for output in outputs:
        incidence = {
            (state, q_value, successor)
            for state in states
            for q_value in (0, 1)
            for emitted, successor in support[(state, q_value)]
            if emitted == output
        }
        if incidence:
            result[output] = tuple(sorted(incidence))
    return result


def _quotient(
    support: Support, outputs: tuple[int, ...], states: tuple[int, ...]
) -> tuple[Support, tuple[int, ...], tuple[Signature, ...]]:
    signatures = _signatures(support, outputs, states)
    classes = tuple(sorted(set(signatures.values())))
    index = {signature: position for position, signature in enumerate(classes)}
    mapping = {output: index[signature] for output, signature in signatures.items()}
    quotient = {
        key: tuple(
            sorted({(mapping[emitted], successor) for emitted, successor in events})
        )
        for key, events in support.items()
    }
    return quotient, tuple(range(len(classes))), classes


def _clone(
    support: Support, outputs: tuple[int, ...], colors: int
) -> tuple[Support, tuple[int, ...]]:
    cloned = {
        key: tuple(
            (emitted * colors + color, successor)
            for emitted, successor in events
            for color in range(colors)
        )
        for key, events in support.items()
    }
    cloned_outputs = tuple(
        emitted * colors + color for emitted in outputs for color in range(colors)
    )
    return cloned, cloned_outputs


def _observer(
    support: Support,
    outputs: tuple[int, ...],
    states: tuple[int, ...],
    horizon: int,
) -> dict[str, Any]:
    start = 1
    pending = deque((start,))
    seen = {start}
    edges: dict[tuple[int, int], int] = {}
    mixed = []
    while pending:
        mask = pending.popleft()
        for output in outputs:
            target = 0
            q_mask = 0
            for state in states:
                if not mask & (1 << state):
                    continue
                for q_value in (0, 1):
                    for emitted, successor in support[(state, q_value)]:
                        if emitted == output:
                            target |= 1 << successor
                            q_mask |= 1 << q_value
            if not target:
                continue
            edges[(mask, output)] = target
            if q_mask == 3:
                mixed.append((mask, output))
            if target not in seen:
                seen.add(target)
                pending.append(target)
    paths = {start: 1}
    counts = []
    for _ in range(horizon):
        following: Counter[int] = Counter()
        for mask, multiplicity in paths.items():
            for output in outputs:
                target = edges.get((mask, output))
                if target is not None:
                    following[target] += multiplicity
        paths = dict(following)
        counts.append(sum(paths.values()))
    ordered = sorted(seen)
    adjacency = [
        [sum(edges.get((source, y)) == target for y in outputs) for target in ordered]
        for source in ordered
    ]
    return {
        "feasible": not mixed,
        "beliefs": ordered,
        "counts": counts,
        "adjacency": adjacency,
    }


def independent_quotient_theorem(horizon: int = 7) -> dict[str, Any]:
    computed: Support = {
        (0, 0): ((0, 0),),
        (0, 1): ((1, 0),),
    }
    golden: Support = {}
    for state, q_value in itertools.product((0, 1), repeat=2):
        golden[(state, q_value)] = (
            ((2 * q_value, 0), (2 * q_value + 1, 1))
            if state == 0
            else ((2 * q_value, 0),)
        )
    duplicate: Support = {
        (0, 0): ((0, 0), (1, 0)),
        (0, 1): ((2, 0), (3, 0)),
    }
    fixtures = {
        "computed": (computed, (0, 1), (0,)),
        "golden": (golden, (0, 1, 2, 3), (0, 1)),
        "duplicate": (duplicate, (0, 1, 2, 3), (0,)),
    }
    checks = []
    rows = []
    for name, (support, outputs, states) in fixtures.items():
        quotient, quotient_outputs, classes = _quotient(support, outputs, states)
        base_semantic = _observer(quotient, quotient_outputs, states, horizon)
        quotient_signatures = _signatures(quotient, quotient_outputs, states)
        local = {
            "idempotent": len(set(quotient_signatures.values())) == len(classes),
            "minimal_exact": all(
                bool(set(left) ^ set(right))
                for left, right in itertools.combinations(classes, 2)
            ),
        }
        for colors in (2, 3, 5, 8):
            cloned, cloned_outputs = _clone(support, outputs, colors)
            clone_quotient, clone_outputs, clone_classes = _quotient(
                cloned, cloned_outputs, states
            )
            clone_semantic = _observer(clone_quotient, clone_outputs, states, horizon)
            local[f"clone_{colors}"] = (
                len(clone_classes) == len(classes) and clone_semantic == base_semantic
            )
        rows.append((name, len(classes), local))
        checks.extend(local.values())
    duplicate_row = next(row for row in rows if row[0] == "duplicate")
    special = {
        "duplicate_two_classes": duplicate_row[1] == 2,
        "computed_two_classes": next(row for row in rows if row[0] == "computed")[1]
        == 2,
        "golden_four_classes": next(row for row in rows if row[0] == "golden")[1] == 4,
    }
    return {
        "rows": rows,
        "special": special,
        "pass": len(rows) == 3 and all(checks) and all(special.values()),
    }


def independent_column_census() -> dict[str, Any]:
    allowed_columns = (0, 1, 2, 3, 4, 8, 12)
    joint = Counter()
    semantic = Counter()
    raw = Counter()
    per_declared = []
    feasible = 0
    for declared in range(1, 5):
        row_feasible = 0
        row_joint = Counter()
        for columns in itertools.product(allowed_columns, repeat=declared):
            covered = 0
            for column in columns:
                covered |= column
            if covered != 0b1111:
                continue
            row_feasible += 1
            feasible += 1
            active = [column for column in columns if column]
            raw_count = len(active)
            semantic_count = len(set(active))
            row_joint[(raw_count, semantic_count)] += 1
            joint[(raw_count, semantic_count)] += 1
            raw[raw_count] += 1
            semantic[semantic_count] += 1
        per_declared.append((row_feasible, dict(row_joint)))
    checks = {
        "total_relations": sum((2**declared - 1) ** 4 for declared in range(1, 5))
        == 53108,
        "feasible": feasible == 724,
        "infeasible": 53108 - feasible == 52384,
        "per_declared": [row[0] for row in per_declared] == [0, 2, 48, 674],
        "raw_histogram": raw == {2: 20, 3: 210, 4: 494},
        "semantic_histogram": semantic == {2: 64, 3: 396, 4: 264},
        "joint_histogram": joint
        == {
            (2, 2): 20,
            (3, 2): 30,
            (3, 3): 180,
            (4, 2): 14,
            (4, 3): 216,
            (4, 4): 264,
        },
        "duplicates": sum(
            count
            for (raw_count, sem_count), count in joint.items()
            if sem_count < raw_count
        )
        == 260,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_embedding_and_margin(horizon: int = 7) -> dict[str, Any]:
    deterministic = 0
    signature_reduced = True
    for declared in range(1, 5):
        for assignment in itertools.product(range(declared), repeat=4):
            if not {assignment[0], assignment[1]}.isdisjoint(
                {assignment[2], assignment[3]}
            ):
                continue
            deterministic += 1
            signatures = [
                sum(
                    (assigned == output) << mode
                    for mode, assigned in enumerate(assignment)
                )
                for output in set(assignment)
            ]
            signature_reduced &= len(signatures) == len(set(signatures))
    safe = True
    rows = []
    for classes in (2, 3, 4):
        for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
            for time in range(1, horizon + 1):
                normal = _ceil(radius * 2**time)
                safe &= 2 * radius / normal <= Fraction(2, 2**time)
                rows.append((classes**time * normal, 2**time * normal))
    checks = {
        "deterministic_104": deterministic == 104,
        "deterministic_signature_reduced": signature_reduced,
        "safe_normal_cells": safe,
        "positive_products": all(read > 0 and write > 0 for read, write in rows),
        "semantic_corners": {1 + math.log2(k) for k in (2, 3, 4)}
        == {2.0, 1 + math.log2(3), 3.0},
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_support_incidence_quotient_contract_v0_21",
        "signature": contract["signature"]["definition"]
        == "sigma(y)={(s,z,s'): (y,s') in E(s,z)}",
        "active_only": contract["signature"]["active_only"],
        "minimality": "coarsest quotient" in contract["quotient"]["minimality"],
        "semantic_formula": contract["semantic_rate"]["finite_read_words"]
        == "L_T_sem ceil(rho*2^T)",
        "scope": "not a proved minimal control-sufficient quotient"
        in contract["scope"],
        "claim_schema": claim["schema_version"]
        == "asmp4_support_incidence_quotient_claim_v0_21",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_20_refinement_stop_claim_sha256": SEALS[V20],
        },
        "claim_histograms": claim["memoryless_census"]["raw_active_histogram"]
        == {"2": 20, "3": 210, "4": 494}
        and claim["memoryless_census"]["semantic_class_histogram"]
        == {"2": 64, "3": 396, "4": 264},
        "claim_scope": "not proved minimal for safety control" in claim["nonclaim"]
        and "does not select" in claim["nonclaim"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in TEST_FILES:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((package, count))
    total = sum(count for _, count in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 21 and total == 244,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_21.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_21.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "signature": "sigma(y)" in docs["theorem"]
        and "(s,z,s_next)" in docs["theorem"],
        "invariances": "renaming" in docs["theorem"] and "clone" in docs["theorem"],
        "census": "53,108" in docs["result"]
        and "260" in docs["result"]
        and "64,396,264" in docs["result"],
        "scope": "not minimal for control" in docs["result"],
        "expanded_count": "254" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_support_incidence_quotient.py" in docs["readme"],
        "review_attack": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "quotient_theorem": independent_quotient_theorem()["pass"],
        "column_census": independent_column_census()["pass"],
        "embedding_and_margin": independent_embedding_and_margin()["pass"],
        "contract_and_claim": independent_contract_and_claim()["pass"],
        "inventory": independent_inventory()["pass"],
        "documents": document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
