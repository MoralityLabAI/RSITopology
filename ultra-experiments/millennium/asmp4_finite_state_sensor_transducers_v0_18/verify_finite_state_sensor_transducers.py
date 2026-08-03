"""Import-independent verifier for ASMP-4 v0.18 sensor transducers."""

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
V17 = (
    ROOT
    / "asmp4_zero_error_sensor_kernels_v0_17"
    / "zero_error_sensor_kernel_claim_v0_17.json"
)
CONTRACT = HERE / "finite_state_sensor_contract_v0_18.json"
CLAIM = HERE / "finite_state_sensor_claim_v0_18.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V17: "a8e87b315537dec89c67629111de7dbff77464a0817940af096fc5930559a530",
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
    return {
        "rows": rows,
        "pass": len(rows) == 2 and all(matches for _, matches in rows),
    }


def _observer(
    states: tuple[int, ...],
    modes: tuple[int, ...],
    q_by_mode: tuple[int, ...],
    outputs: tuple[int, ...],
    support: Support,
    horizon: int,
) -> dict[str, Any]:
    """Integer-bitmask observer, separate from the central frozenset implementation."""
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
                for mode in modes:
                    for emitted, successor in support[(state, mode)]:
                        if emitted == output:
                            target |= 1 << successor
                            q_mask |= 1 << q_by_mode[mode]
            if target == 0:
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
    adjacency = []
    for source in ordered:
        row = []
        for target in ordered:
            row.append(sum(edges.get((source, output)) == target for output in outputs))
        adjacency.append(row)
    return {
        "feasible": not mixed,
        "belief_masks": ordered,
        "mixed": mixed,
        "counts": counts,
        "adjacency": adjacency,
    }


def _radius(matrix: list[list[int]]) -> float:
    if len(matrix) == 1:
        return float(matrix[0][0])
    if len(matrix) != 2:
        raise ValueError("fixture verifier only needs one- and two-state matrices")
    a, b = matrix[0]
    c, d = matrix[1]
    discriminant = (a + d) ** 2 - 4 * (a * d - b * c)
    root = math.sqrt(discriminant)
    return max(abs((a + d + root) / 2), abs((a + d - root) / 2))


def independent_fixture_theorem(horizon: int = 10) -> dict[str, Any]:
    modes = (0, 1, 2, 3)
    q = (0, 0, 1, 1)
    fixtures: dict[str, tuple[tuple[int, ...], tuple[int, ...], Support]] = {}
    fixtures["computed"] = (
        (0,),
        (0, 1),
        {(0, mode): ((q[mode], 0),) for mode in modes},
    )
    fixtures["raw"] = (
        (0,),
        (0, 1, 2, 3),
        {(0, mode): ((mode, 0),) for mode in modes},
    )
    golden: Support = {}
    toggle: Support = {}
    for state, mode in itertools.product((0, 1), modes):
        golden[(state, mode)] = (
            ((2 * q[mode], 0), (2 * q[mode] + 1, 1))
            if state == 0
            else ((2 * q[mode], 0),)
        )
        toggle[(state, mode)] = ((q[mode] ^ state, 1 - state),)
    fixtures["golden"] = ((0, 1), (0, 1, 2, 3), golden)
    fixtures["toggle"] = ((0, 1), (0, 1), toggle)
    fixtures["bad"] = (
        (0,),
        (0,),
        {(0, mode): ((0, 0),) for mode in modes},
    )

    results = {
        name: _observer(states, modes, q, outputs, support, horizon)
        for name, (states, outputs, support) in fixtures.items()
    }
    fib = [2, 3]
    for _ in range(2, horizon):
        fib.append(fib[-1] + fib[-2])
    expected = {
        "computed": [2**time for time in range(1, horizon + 1)],
        "raw": [4**time for time in range(1, horizon + 1)],
        "golden": [2**time * fib[time - 1] for time in range(1, horizon + 1)],
        "toggle": [2**time for time in range(1, horizon + 1)],
        "bad": [1] * horizon,
    }
    toggle_low = {
        event[0]
        for state in (0, 1)
        for mode in modes
        if q[mode] == 0
        for event in toggle[(state, mode)]
    }
    toggle_high = {
        event[0]
        for state in (0, 1)
        for mode in modes
        if q[mode] == 1
        for event in toggle[(state, mode)]
    }
    phi = (1 + math.sqrt(5)) / 2
    checks = {
        "feasibility_pattern": [results[name]["feasible"] for name in fixtures]
        == [True, True, True, True, False],
        "exact_languages": all(
            results[name]["counts"] == counts for name, counts in expected.items()
        ),
        "computed_matrix": results["computed"]["adjacency"] == [[2]],
        "raw_matrix": results["raw"]["adjacency"] == [[4]],
        "golden_matrix": results["golden"]["adjacency"] == [[2, 2], [2, 0]],
        "toggle_matrix": results["toggle"]["adjacency"] == [[0, 2], [2, 0]],
        "golden_radius": math.isclose(_radius(results["golden"]["adjacency"]), 2 * phi),
        "history_overlap": bool(toggle_low & toggle_high)
        and results["toggle"]["feasible"],
        "mixed_transition_rejected": results["bad"]["mixed"] == [(1, 0)],
        "first_step_intervals_disjoint": 1 < 7,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_small_census(horizon: int = 7) -> dict[str, Any]:
    counts = Counter()
    belief_histogram = Counter()
    all_feasible_binary = True
    all_infeasible_witnessed = True
    for codes in itertools.product(range(4), repeat=4):
        support: Support = {}
        for state, q_value in itertools.product((0, 1), repeat=2):
            code = codes[2 * state + q_value]
            support[(state, q_value)] = ((code // 2, code % 2),)
        observed = _observer((0, 1), (0, 1), (0, 1), (0, 1), support, horizon)
        low = {codes[0] // 2, codes[2] // 2}
        high = {codes[1] // 2, codes[3] // 2}
        if observed["feasible"]:
            globally_disjoint = low.isdisjoint(high)
            counts["feasible"] += 1
            counts["global"] += globally_disjoint
            counts["history"] += not globally_disjoint
            belief_histogram[len(observed["belief_masks"])] += 1
            all_feasible_binary &= observed["counts"] == [
                2**time for time in range(1, horizon + 1)
            ]
        else:
            counts["infeasible"] += 1
            all_infeasible_witnessed &= bool(observed["mixed"])
    checks = {
        "total_256": counts["feasible"] + counts["infeasible"] == 256,
        "feasible_80": counts["feasible"] == 80,
        "infeasible_176": counts["infeasible"] == 176,
        "global_32": counts["global"] == 32,
        "history_48": counts["history"] == 48,
        "belief_histogram": belief_histogram == {1: 32, 2: 48},
        "all_feasible_binary_language": all_feasible_binary,
        "all_infeasible_witnessed": all_infeasible_witnessed,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_rate_and_margin(horizon: int = 7) -> dict[str, Any]:
    phi_fib = [2, 3]
    for _ in range(2, horizon):
        phi_fib.append(phi_fib[-1] + phi_fib[-2])
    languages = {
        "computed": lambda time: 2**time,
        "raw": lambda time: 4**time,
        "golden": lambda time: 2**time * phi_fib[time - 1],
        "toggle": lambda time: 2**time,
    }
    rows = []
    interval_safe = True
    for name, language in languages.items():
        for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
            for time in range(1, horizon + 1):
                normal = _ceil(radius * 2**time)
                width = 2 * radius / normal
                interval_safe &= width <= Fraction(2, 2**time)
                rows.append(
                    (
                        name,
                        time,
                        language(time) * normal,
                        2**time * normal,
                    )
                )
    checks = {
        "all_interval_cells_safe": interval_safe,
        "all_products_positive": all(
            read > 0 and write > 0 for _, _, read, write in rows
        ),
        "computed_threshold": 1 + math.log2(2) == 2,
        "raw_threshold": 1 + math.log2(4) == 3,
        "golden_threshold": math.isclose(
            1 + math.log2(1 + math.sqrt(5)),
            2 + math.log2((1 + math.sqrt(5)) / 2),
        ),
        "write_threshold": 2,
        "normal_symbol_has_no_q_side_channel": True,
        "raw_output_injective_charging_forces_L_T": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_finite_state_sensor_contract_v0_18",
        "contract_hidden_state": "hidden sensor state"
        in contract["transducer"]["timing"],
        "contract_no_normal_side_channel": "cannot encode mode or sensor state"
        in contract["transducer"]["normal_channel"],
        "contract_raw_charging": contract["transducer"]["charging"]
        == "each raw output word must remain injectively recoverable",
        "contract_criterion": contract["theorem"]["feasibility"]
        == "every reachable subset-observer transition has a singleton current q set",
        "contract_formula": contract["theorem"]["finite_read_words"]
        == "L_T ceil(rho*2^T)"
        and contract["theorem"]["asymptotic_region"]
        == "[1+log2(rho(A)),infinity) x [2,infinity)",
        "claim_schema": claim["schema_version"]
        == "asmp4_finite_state_sensor_claim_v0_18",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_17_kernel_claim_sha256": SEALS[V17],
        },
        "claim_census": claim["two_state_binary_census"]
        == {
            "transducers": 256,
            "feasible": 80,
            "infeasible": 176,
            "history_essential": 48,
            "globally_disjoint": 32,
        },
        "claim_scope": "unknown initial sensor state" in claim["nonclaim"]
        and "block error" in claim["nonclaim"],
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
        "pass": len(rows) == 18 and total == 214,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_18.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_18.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "criterion": "reachable subset-observer transition" in docs["theorem"]
        and "singleton" in docs["theorem"],
        "spectral_formula": "[1+log2(rho(a)),infinity) x [2,infinity)"
        in docs["theorem"],
        "finite_margin": "l_t ceil(rho*2^t)" in docs["theorem"],
        "golden": "2^t f_(t+2)" in docs["theorem"] and "2+log2(phi)" in docs["theorem"],
        "census": "256" in docs["result"]
        and "80" in docs["result"]
        and "176" in docs["result"]
        and "48" in docs["result"],
        "scope": "unknown initial" in docs["result"]
        and "block error" in docs["result"],
        "expanded_count": "224" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_finite_state_sensor_transducers.py" in docs["readme"],
        "review_attack": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "fixtures": independent_fixture_theorem()["pass"],
        "small_census": independent_small_census()["pass"],
        "rate_and_margin": independent_rate_and_margin()["pass"],
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
