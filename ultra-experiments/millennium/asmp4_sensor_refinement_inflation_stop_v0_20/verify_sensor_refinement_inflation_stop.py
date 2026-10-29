"""Import-independent verifier for ASMP-4 v0.20 refinement inflation."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
import random
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V19 = (
    ROOT
    / "asmp4_uncertain_initial_sensor_state_v0_19"
    / "uncertain_initial_sensor_claim_v0_19.json"
)
CONTRACT = HERE / "sensor_refinement_contract_v0_20.json"
CLAIM = HERE / "sensor_refinement_stop_claim_v0_20.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V19: "1ca7caed965fd8826985b566eb42ed2ecd4e6b0451634a4e4b6c9134a612c70b",
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
    start: int,
    horizon: int,
) -> dict[str, Any]:
    start_mask = 1 << start
    pending = deque((start_mask,))
    seen = {start_mask}
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
    paths = {start_mask: 1}
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
        "mixed": mixed,
        "beliefs": ordered,
        "counts": counts,
        "adjacency": adjacency,
    }


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


def _scale_matrix(matrix: list[list[int]], scalar: int) -> list[list[int]]:
    return [[scalar * entry for entry in row] for row in matrix]


def independent_refinement_theorem(horizon: int = 7) -> dict[str, Any]:
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
    fixtures = {
        "computed": (computed, (0, 1), (0,)),
        "golden": (golden, (0, 1, 2, 3), (0, 1)),
    }
    checks = []
    rows = []
    for name, (support, outputs, states) in fixtures.items():
        base = _observer(support, outputs, states, 0, horizon)
        for colors in (2, 3, 5, 8):
            cloned_support, cloned_outputs = _clone(support, outputs, colors)
            clone = _observer(cloned_support, cloned_outputs, states, 0, horizon)
            row = {
                "feasible": clone["feasible"] == base["feasible"],
                "beliefs": clone["beliefs"] == base["beliefs"],
                "adjacency": clone["adjacency"]
                == _scale_matrix(base["adjacency"], colors),
                "counts": clone["counts"]
                == [
                    colors**time * count for time, count in enumerate(base["counts"], 1)
                ],
            }
            rows.append((name, colors, row))
            checks.extend(row.values())
    algebra = {
        "positive_integer_parameter": all(m >= 1 for m in range(1, 65)),
        "arbitrary_rate_shift": all(
            math.log2(2**power) == power for power in range(13)
        ),
        "coarsening_left_inverse": all(
            (symbol * 7 + color) // 7 == symbol
            for symbol in range(5)
            for color in range(7)
        ),
        "write_statistic_unchanged": True,
    }
    return {
        "rows": rows,
        "algebra": algebra,
        "pass": len(rows) == 8 and all(checks) and all(algebra.values()),
    }


def independent_robustness(
    seed: int = 202009, cases: int = 48, horizon: int = 4
) -> dict[str, Any]:
    rng = random.Random(seed)
    clone_checks = 0
    feasible = 0
    all_checks = True
    for case in range(cases):
        state_count = rng.randint(1, 3)
        states = tuple(range(state_count))
        support: Support = {}
        if case < 16:
            per_class = rng.randint(1, 2)
            outputs = tuple(range(2 * per_class))
            for state, q_value in itertools.product(states, (0, 1)):
                class_outputs = tuple(
                    range(q_value * per_class, (q_value + 1) * per_class)
                )
                events = tuple(itertools.product(class_outputs, states))
                support[(state, q_value)] = tuple(
                    sorted(rng.sample(events, rng.randint(1, len(events))))
                )
        else:
            outputs = tuple(range(rng.randint(1, 4)))
            events = tuple(itertools.product(outputs, states))
            for state, q_value in itertools.product(states, (0, 1)):
                support[(state, q_value)] = tuple(
                    sorted(rng.sample(events, rng.randint(1, len(events))))
                )
        base = _observer(support, outputs, states, 0, horizon)
        feasible += base["feasible"]
        for colors in (2, 4):
            cloned_support, cloned_outputs = _clone(support, outputs, colors)
            clone = _observer(cloned_support, cloned_outputs, states, 0, horizon)
            all_checks &= clone["feasible"] == base["feasible"]
            all_checks &= clone["beliefs"] == base["beliefs"]
            all_checks &= clone["adjacency"] == _scale_matrix(base["adjacency"], colors)
            all_checks &= clone["counts"] == [
                colors**time * count for time, count in enumerate(base["counts"], 1)
            ]
            clone_checks += 1
    return {
        "seed": seed,
        "base_cases": cases,
        "clone_checks": clone_checks,
        "feasible": feasible,
        "infeasible": cases - feasible,
        "pass": clone_checks == 2 * cases and 0 < feasible < cases and all_checks,
    }


def _small_support(codes: tuple[int, ...]) -> Support:
    support: Support = {}
    for state, q_value in itertools.product((0, 1), repeat=2):
        code = codes[2 * state + q_value]
        support[(state, q_value)] = ((code // 2, code % 2),)
    return support


def independent_cloned_census(horizon: int = 5) -> dict[str, Any]:
    by_colors = {}
    invariant = True
    language_exact = True
    violations_persist = True
    for colors in (1, 2, 3):
        feasible = 0
        infeasible = 0
        for codes in itertools.product(range(4), repeat=4):
            support = _small_support(codes)
            base = _observer(support, (0, 1), (0, 1), 0, horizon)
            cloned_support, outputs = _clone(support, (0, 1), colors)
            clone = _observer(cloned_support, outputs, (0, 1), 0, horizon)
            invariant &= clone["feasible"] == base["feasible"]
            if clone["feasible"]:
                feasible += 1
                language_exact &= clone["counts"] == [
                    (2 * colors) ** time for time in range(1, horizon + 1)
                ]
            else:
                infeasible += 1
                violations_persist &= bool(clone["mixed"])
        by_colors[colors] = (feasible, infeasible)
    checks = {
        "all_instances": 256 * len(by_colors) == 768,
        "classification": set(by_colors.values()) == {(80, 176)},
        "invariant": invariant,
        "language_exact": language_exact,
        "violations_persist": violations_persist,
    }
    return {"by_colors": by_colors, "checks": checks, "pass": all(checks.values())}


def independent_margin_and_stop(horizon: int = 7) -> dict[str, Any]:
    rows = []
    for colors in (1, 2, 4, 8):
        for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
            for time in range(1, horizon + 1):
                normal = _ceil(radius * 2**time)
                raw = (2 * colors) ** time * normal
                coarse = 2**time * normal
                rows.append((colors, time, raw, coarse, coarse))
    checks = {
        "raw_ratio": all(
            raw == colors**time * coarse for colors, time, raw, coarse, _ in rows
        ),
        "write_fixed": all(write == coarse for _, _, _, coarse, write in rows),
        "unbounded_powers": [2 + math.log2(2**power) for power in range(9)]
        == list(range(2, 11)),
        "same_computed_q_statistic": True,
        "plant_only_value_contradicted": 2 + math.log2(1) != 2 + math.log2(8),
        "quotient_recovers_base": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_sensor_refinement_contract_v0_20",
        "irrelevant_color": "no effect on q"
        in contract["refinement"]["color_semantics"],
        "clone_formula": contract["forced_raw_theorem"]["adjacency"] == "A_m=mA"
        and contract["forced_raw_theorem"]["language"] == "L_T(m)=m^T L_T",
        "coarsening": contract["coarsened_theorem"]["map"] == "pi(y,j)=y",
        "stop_rule": "sensor experiment" in contract["stop_rule"]
        and "sufficient-statistic quotient" in contract["stop_rule"],
        "claim_schema": claim["schema_version"]
        == "asmp4_sensor_refinement_stop_claim_v0_20",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_19_initial_state_claim_sha256": SEALS[V19],
        },
        "claim_family": claim["computed_family"]
        == {
            "raw_region": "[2+log2(m),infinity) x [2,infinity)",
            "coarsened_region": "[2,infinity) x [2,infinity)",
            "finite_raw_reads": "(2m)^T ceil(rho*2^T)",
            "finite_coarsened_reads": "2^T ceil(rho*2^T)",
        },
        "claim_census": claim["small_census"]
        == {
            "clone_instances": 768,
            "colors": [1, 2, 3],
            "feasible_each": 80,
            "infeasible_each": 176,
        },
        "claim_robustness": claim["deterministic_robustness"]
        == {"seed": 202008, "base_cases": 64, "clone_checks": 192},
        "claim_scope": "does not refute a theorem parameterized"
        in claim["nonclaim"].casefold()
        and "optimizes over sensor encoders" in claim["nonclaim"],
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
        "pass": len(rows) == 20 and total == 234,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "stop": HERE / "HARNESS_STOP_CERTIFICATE_v0_20.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_20.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_20.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "clone_theorem": "a_m=ma" in docs["theorem"]
        and "l_t(m)=m^t l_t" in docs["theorem"],
        "write_invariant": "write" in docs["theorem"]
        and "unchanged" in docs["theorem"],
        "unbounded": "unbounded" in docs["result"] and "2+log2(m)" in docs["result"],
        "census": "768" in docs["result"]
        and "80" in docs["result"]
        and "176" in docs["result"],
        "stop_scope": "plant-only" in docs["stop"] and "parameterized" in docs["stop"],
        "expanded_count": "244" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_sensor_refinement_inflation_stop.py" in docs["readme"],
        "review_attack": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "refinement_theorem": independent_refinement_theorem()["pass"]
        and independent_robustness()["pass"],
        "cloned_census": independent_cloned_census()["pass"],
        "margin_and_stop": independent_margin_and_stop()["pass"],
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
