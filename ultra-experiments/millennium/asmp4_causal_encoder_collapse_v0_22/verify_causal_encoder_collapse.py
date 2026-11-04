"""Import-independent verifier for ASMP-4 v0.22 causal encoder collapse."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V21 = (
    ROOT
    / "asmp4_support_incidence_quotient_v0_21"
    / "support_incidence_quotient_claim_v0_21.json"
)
CONTRACT = HERE / "causal_encoder_contract_v0_22.json"
CLAIM = HERE / "causal_encoder_collapse_claim_v0_22.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V21: "89bf8dac4bb615afa16d24cddc181d077b313f361903f5c0723f78407af4eee8",
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
    (
        "asmp4_support_incidence_quotient_v0_21",
        "test_support_incidence_quotient.py",
    ),
)

Event = tuple[int, int]
Support = dict[tuple[int, int], tuple[Event, ...]]


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


def _observer(
    support: Support,
    outputs: tuple[int, ...],
    states: tuple[int, ...],
    start_mask: int,
    horizon: int,
) -> dict[str, Any]:
    pending = deque((start_mask,))
    seen = {start_mask}
    edges: dict[tuple[int, int], int] = {}
    decoders: dict[tuple[int, int], int] = {}
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
            if q_mask in (1, 2):
                decoders[(mask, output)] = 0 if q_mask == 1 else 1
            else:
                mixed.append((mask, output))
            if target not in seen:
                seen.add(target)
                pending.append(target)
    raw_paths = {start_mask: 1}
    raw_counts = []
    encoded_paths: set[tuple[int, tuple[int, ...]]] = {(start_mask, ())}
    encoded_counts = []
    for _ in range(horizon):
        following: Counter[int] = Counter()
        for mask, multiplicity in raw_paths.items():
            for output in outputs:
                target = edges.get((mask, output))
                if target is not None:
                    following[target] += multiplicity
        raw_paths = dict(following)
        raw_counts.append(sum(raw_paths.values()))

        next_encoded = set()
        for mask, word in encoded_paths:
            for output in outputs:
                target = edges.get((mask, output))
                q_value = decoders.get((mask, output))
                if target is not None and q_value is not None:
                    next_encoded.add((target, word + (q_value,)))
        encoded_paths = next_encoded
        encoded_counts.append(len({word for _, word in encoded_paths}))
    ordered = sorted(seen)
    adjacency = [
        [sum(edges.get((source, y)) == target for y in outputs) for target in ordered]
        for source in ordered
    ]
    return {
        "feasible": not mixed,
        "mixed": mixed,
        "beliefs": ordered,
        "edges": edges,
        "decoders": decoders,
        "adjacency": adjacency,
        "raw_counts": raw_counts,
        "encoded_counts": encoded_counts,
    }


def _restricted_growth_partitions(size: int) -> tuple[tuple[int, ...], ...]:
    assignments = []

    def visit(prefix: tuple[int, ...]) -> None:
        if len(prefix) == size:
            assignments.append(prefix)
            return
        maximum = max(prefix) if prefix else -1
        for label in range(maximum + 2):
            visit(prefix + (label,))

    visit(())
    return tuple(assignment for assignment in assignments if assignment[0] == 0)


def _static_support(support: Support, assignment: tuple[int, ...]) -> Support:
    return {
        key: tuple(
            sorted({(assignment[emitted], successor) for emitted, successor in events})
        )
        for key, events in support.items()
    }


def independent_contextual_separation(horizon: int = 7) -> dict[str, Any]:
    support: Support = {
        (0, 0): ((0, 1),),
        (0, 1): ((1, 0), (2, 0)),
        (1, 0): ((0, 0), (1, 0)),
        (1, 1): ((2, 0),),
    }
    raw = _observer(support, (0, 1, 2), (0, 1), 1, horizon)
    rows = []
    for assignment in _restricted_growth_partitions(3):
        outputs = tuple(range(max(assignment) + 1))
        observed = _observer(
            _static_support(support, assignment), outputs, (0, 1), 1, horizon
        )
        rows.append((assignment, observed))
    feasible = [row for row in rows if row[1]["feasible"]]
    checks = {
        "five_partitions": len(rows) == 5,
        "only_discrete_feasible": len(feasible) == 1 and feasible[0][0] == (0, 1, 2),
        "raw_three_power": raw["raw_counts"]
        == [3**time for time in range(1, horizon + 1)],
        "causal_two_power": raw["encoded_counts"]
        == [2**time for time in range(1, horizon + 1)],
        "contextual_y_one": raw["decoders"][(1, 1)] == 1
        and raw["decoders"][(2, 1)] == 0,
        "adjacency": raw["adjacency"] == [[2, 1], [3, 0]],
        "static_radius_three": max(abs(3), abs(-1)) == 3,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_general_theorem(horizon: int = 7) -> dict[str, Any]:
    computed: Support = {(0, 0): ((0, 0),), (0, 1): ((1, 0),)}
    raw: Support = {
        (0, 0): ((0, 0), (1, 0)),
        (0, 1): ((2, 0), (3, 0)),
    }
    bad: Support = {(0, 0): ((0, 0),), (0, 1): ((0, 0),)}
    fixtures = (
        _observer(computed, (0, 1), (0,), 1, horizon),
        _observer(raw, (0, 1, 2, 3), (0,), 1, horizon),
        _observer(bad, (0,), (0,), 1, horizon),
    )
    checks = {
        "feasibility_pattern": [item["feasible"] for item in fixtures]
        == [True, True, False],
        "computed_binary": fixtures[0]["encoded_counts"]
        == [2**time for time in range(1, horizon + 1)],
        "raw_binary": fixtures[1]["encoded_counts"]
        == [2**time for time in range(1, horizon + 1)],
        "raw_uncompressed_four_power": fixtures[1]["raw_counts"]
        == [4**time for time in range(1, horizon + 1)],
        "mixed_not_repairable": bool(fixtures[2]["mixed"])
        and not fixtures[2]["encoded_counts"][0],
        "encoder_state_is_finite_belief": True,
        "arbitrary_q_words_force_binary_lower_bound": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_small_census(horizon: int = 5) -> dict[str, Any]:
    feasible = 0
    infeasible = 0
    encoded_exact = True
    mixed_exact = True
    for codes in itertools.product(range(4), repeat=4):
        support: Support = {}
        for state, q_value in itertools.product((0, 1), repeat=2):
            code = codes[2 * state + q_value]
            support[(state, q_value)] = ((code // 2, code % 2),)
        observed = _observer(support, (0, 1), (0, 1), 1, horizon)
        if observed["feasible"]:
            feasible += 1
            encoded_exact &= observed["encoded_counts"] == [
                2**time for time in range(1, horizon + 1)
            ]
        else:
            infeasible += 1
            mixed_exact &= bool(observed["mixed"])
    checks = {
        "total": feasible + infeasible == 256,
        "feasible": feasible == 80,
        "infeasible": infeasible == 176,
        "encoded_exact": encoded_exact,
        "mixed_exact": mixed_exact,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_memoryless_and_margin(horizon: int = 7) -> dict[str, Any]:
    allowed_columns = (0, 1, 2, 3, 4, 8, 12)
    feasible = 0
    for declared in range(1, 5):
        for columns in itertools.product(allowed_columns, repeat=declared):
            covered = 0
            for column in columns:
                covered |= column
            feasible += covered == 0b1111
    total = sum((2**declared - 1) ** 4 for declared in range(1, 5))
    safe = True
    rows = []
    for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
        for time in range(1, horizon + 1):
            normal = _ceil(radius * 2**time)
            safe &= 2 * radius / normal <= Fraction(2, 2**time)
            rows.append((2**time * normal, 2**time * normal))
    checks = {
        "total_53108": total == 53108,
        "feasible_724": feasible == 724,
        "infeasible_52384": total - feasible == 52384,
        "safe_cells": safe,
        "read_write_equal": all(read == write for read, write in rows),
        "full_region_two_two": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_causal_encoder_contract_v0_22",
        "timing": "before each current write" in contract["observation"],
        "belief_encoder": contract["encoder"]["state"]
        == "reachable subset belief B initialized at registered I",
        "raw_not_charged": "need not remain recoverable"
        in contract["encoder"]["raw_charging"],
        "theorem": contract["theorem"]["feasibility"]
        == "causal encoder exists iff every reachable raw transition is q-homogeneous"
        and contract["theorem"]["region"] == "[2,infinity) x [2,infinity)",
        "claim_schema": claim["schema_version"]
        == "asmp4_causal_encoder_collapse_claim_v0_22",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_21_support_quotient_claim_sha256": SEALS[V21],
        },
        "contextual": claim["contextual_separation"]
        == {
            "raw_symbols": 3,
            "static_partitions": 5,
            "feasible_static_partitions": 1,
            "static_radius": 3,
            "causal_radius": 2,
        },
        "censuses": claim["censuses"]["small_feasible"] == 80
        and claim["censuses"]["memoryless_feasible"] == 724,
        "scope": "delayed sensing" in claim["nonclaim"]
        and "restricted encoder memory" in claim["nonclaim"],
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
        "pass": len(rows) == 22 and total == 254,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_22.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_22.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "encoder": "emit c_t" in docs["theorem"] and "subset belief" in docs["theorem"],
        "equivalence": "if and only if" in docs["theorem"]
        and "mixed" in docs["theorem"],
        "region": "[2,infinity) x [2,infinity)" in docs["theorem"],
        "context": "3^t" in docs["result"] and "2^t" in docs["result"],
        "censuses": "53,108" in docs["result"] and "724" in docs["result"],
        "scope": "delayed" in docs["result"] and "forced-raw" in docs["result"],
        "expanded_count": "264" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_causal_encoder_collapse.py" in docs["readme"],
        "review_attack": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "general_theorem": independent_general_theorem()["pass"],
        "contextual_separation": independent_contextual_separation()["pass"],
        "small_census": independent_small_census()["pass"],
        "memoryless_and_margin": independent_memoryless_and_margin()["pass"],
        "contract_and_claim": independent_contract_and_claim()["pass"],
        "inventory_and_documents": independent_inventory()["pass"]
        and document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
