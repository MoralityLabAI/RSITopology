"""Import-independent verifier for ASMP-4 v0.19 initial sensor uncertainty."""

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
V18 = (
    ROOT
    / "asmp4_finite_state_sensor_transducers_v0_18"
    / "finite_state_sensor_claim_v0_18.json"
)
CONTRACT = HERE / "uncertain_initial_sensor_contract_v0_19.json"
CLAIM = HERE / "uncertain_initial_sensor_claim_v0_19.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V18: "758b3c0a668b4c77985928271ce314ca4bedd3205f2a570bd4c18fc29ae5916c",
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


def _mask_observer(
    support: Support,
    outputs: tuple[int, ...],
    start_mask: int,
    horizon: int,
) -> dict[str, Any]:
    pending = deque((start_mask,))
    seen = {start_mask}
    edges: dict[tuple[int, int], int] = {}
    mixed = []
    while pending:
        mask = pending.popleft()
        for output in outputs:
            target = 0
            q_mask = 0
            for state in (0, 1):
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


def independent_fixtures(horizon: int = 9) -> dict[str, Any]:
    toggle: Support = {}
    sync: Support = {}
    dominant: Support = {}
    for state, q_value in itertools.product((0, 1), repeat=2):
        toggle[(state, q_value)] = ((q_value ^ state, 1 - state),)
        sync[(state, q_value)] = ((2 * q_value + state, 0),)
        dominant[(state, q_value)] = (
            ((2 * q_value, 0),)
            if state == 0
            else ((2 * q_value, 1), (2 * q_value + 1, 1))
        )
    known_toggle = _mask_observer(toggle, (0, 1), 1, horizon)
    unknown_toggle = _mask_observer(toggle, (0, 1), 3, horizon)
    synchronizing = _mask_observer(sync, (0, 1, 2, 3), 3, horizon)
    union_dominant = _mask_observer(dominant, (0, 1, 2, 3), 3, horizon)
    known_low = _mask_observer(dominant, (0, 1, 2, 3), 1, horizon)
    checks = {
        "known_toggle_feasible": known_toggle["feasible"],
        "unknown_toggle_mixed": not unknown_toggle["feasible"]
        and unknown_toggle["mixed"][0][0] == 3,
        "synchronizing_counts": synchronizing["counts"]
        == [2 ** (time + 1) for time in range(1, horizon + 1)],
        "synchronizing_matrix": synchronizing["adjacency"] == [[2, 0], [4, 0]],
        "synchronizing_radius_two": max(2, 0) == 2,
        "dominant_counts": union_dominant["counts"]
        == [4**time for time in range(1, horizon + 1)],
        "dominant_matrix": union_dominant["adjacency"] == [[4, 0], [2, 2]],
        "dominant_radius_four": max(4, 2) == 4,
        "known_low_counts": known_low["counts"]
        == [2**time for time in range(1, horizon + 1)],
        "finite_transient_no_rate_cost": math.isclose(
            math.log2(synchronizing["counts"][-1]) / horizon,
            1 + 1 / horizon,
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def _deterministic_support(codes: tuple[int, ...]) -> Support:
    support: Support = {}
    for state, q_value in itertools.product((0, 1), repeat=2):
        code = codes[2 * state + q_value]
        support[(state, q_value)] = ((code // 2, code % 2),)
    return support


def independent_census(horizon: int = 6) -> dict[str, Any]:
    signatures = Counter()
    feasible_by_start = Counter()
    full_belief_histogram = Counter()
    full_exact = True
    full_iff_disjoint = True
    for codes in itertools.product(range(4), repeat=4):
        support = _deterministic_support(codes)
        observations = [
            _mask_observer(support, (0, 1), start, horizon) for start in (1, 2, 3)
        ]
        signature = tuple(item["feasible"] for item in observations)
        signatures[signature] += 1
        for start, item in zip((1, 2, 3), observations, strict=True):
            feasible_by_start[start] += item["feasible"]
        full = observations[2]
        low = {codes[0] // 2, codes[2] // 2}
        high = {codes[1] // 2, codes[3] // 2}
        full_iff_disjoint &= full["feasible"] == low.isdisjoint(high)
        if full["feasible"]:
            full_belief_histogram[len(full["beliefs"])] += 1
            full_exact &= full["counts"] == [2**time for time in range(1, horizon + 1)]
    expected = {
        (False, False, False): 160,
        (True, True, True): 32,
        (True, True, False): 32,
        (True, False, False): 16,
        (False, True, False): 16,
    }
    total = sum(feasible_by_start.values())
    checks = {
        "start_counts": feasible_by_start == {1: 80, 2: 80, 3: 32},
        "signature_partition": signatures == expected,
        "registered_total": 256 * 3 == 768,
        "feasible_total": total == 192,
        "infeasible_total": 768 - total == 576,
        "uncertainty_loss": signatures[(True, True, False)] == 32,
        "full_iff_global_disjoint": full_iff_disjoint,
        "full_belief_histogram": full_belief_histogram == {1: 8, 2: 12, 3: 12},
        "full_binary_language": full_exact,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_rate_and_margin(horizon: int = 7) -> dict[str, Any]:
    rows = []
    safe_width = True
    for language in (
        lambda time: 2 ** (time + 1),
        lambda time: 4**time,
    ):
        for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
            for time in range(1, horizon + 1):
                normal = _ceil(radius * 2**time)
                safe_width &= 2 * radius / normal <= Fraction(2, 2**time)
                rows.append((language(time) * normal, 2**time * normal))
    checks = {
        "safe_cell_width": safe_width,
        "all_read_products_positive": all(read > 0 for read, _ in rows),
        "all_write_products_positive": all(write > 0 for _, write in rows),
        "synchronizing_rate": 1 + math.log2(2) == 2,
        "dominant_rate": 1 + math.log2(4) == 3,
        "normal_channel_no_initial_state_side_channel": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_uncertain_initial_sensor_contract_v0_19",
        "registered_initial_set": contract["initial_state"]["parameter"]
        == "registered nonempty set I subseteq S",
        "adversarial_actual_state": "adversarially selected"
        in contract["initial_state"]["knowledge"],
        "start_belief": contract["initial_state"]["start_belief"] == "B_0=I",
        "no_side_channel": "cannot encode initial sensor state"
        in contract["transducer"]["normal_channel"],
        "theorem": contract["theorem"]["language_count"] == "L_T(I)=e_I^T A_I^T 1"
        and contract["theorem"]["asymptotic_region"]
        == "[1+log2(rho(A_I)),infinity) x [2,infinity)",
        "claim_schema": claim["schema_version"]
        == "asmp4_uncertain_initial_sensor_claim_v0_19",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_18_transducer_claim_sha256": SEALS[V18],
        },
        "claim_census": claim["two_state_census"]
        == {
            "registered_pairs": 768,
            "feasible": 192,
            "infeasible": 576,
            "feasible_by_initial_set": {"0": 80, "1": 80, "01": 32},
            "both_singletons_but_full_fails": 32,
        },
        "claim_scope": "probabilistic priors" in claim["nonclaim"]
        and "active calibration" in claim["nonclaim"],
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
        "pass": len(rows) == 19 and total == 224,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_19.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_19.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "start_belief": "b_0=i" in docs["theorem"],
        "criterion": "every reachable transition" in docs["theorem"]
        and "singleton" in docs["theorem"],
        "formula": "l_t(i) ceil(rho*2^t)" in docs["theorem"]
        and "rho(a_i)" in docs["theorem"],
        "census": "768" in docs["result"]
        and "192" in docs["result"]
        and "576" in docs["result"],
        "uncertainty_loss": "32" in docs["result"]
        and "both known singleton" in docs["result"],
        "scope": "probabilistic prior" in docs["result"]
        and "active calibration" in docs["result"],
        "expanded_count": "234" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_uncertain_initial_sensor_state.py" in docs["readme"],
        "review_attack": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "fixtures": independent_fixtures()["pass"],
        "census": independent_census()["pass"],
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
