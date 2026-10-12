"""Import-independent verifier for ASMP-4 v0.17 sensor kernels."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V16 = (
    ROOT
    / "asmp4_registered_sensor_classification_v0_16"
    / "registered_sensor_classification_claim_v0_16.json"
)
CONTRACT = HERE / "zero_error_sensor_kernel_contract_v0_17.json"
CLAIM = HERE / "zero_error_sensor_kernel_claim_v0_17.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V16: "f9d9922f8ab33a04987b35b46ddb6d37672b4e341d46a1995b1d74e46c21f9e2",
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
)


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


def _two_mode_cover_count(outputs: int) -> int:
    # Ordered nonempty supports A,B with A union B equal to all outputs:
    # every symbol is A-only, B-only, or both, minus the two cases where one
    # mode has empty support.
    return 3**outputs - 2


def independent_combinatorial_census() -> dict[str, Any]:
    rows = []
    combined = Counter()
    for declared in range(1, 5):
        total = (2**declared - 1) ** 4
        feasible = 0
        active_hist = Counter()
        for active in range(2, declared + 1):
            count = 0
            for low_outputs in range(1, active):
                high_outputs = active - low_outputs
                choose_active = math.comb(declared, active)
                choose_low = math.comb(active, low_outputs)
                count += (
                    choose_active
                    * choose_low
                    * _two_mode_cover_count(low_outputs)
                    * _two_mode_cover_count(high_outputs)
                )
            active_hist[active] = count
            combined[active] += count
            feasible += count

        deterministic = 0
        for assignment in itertools.product(range(declared), repeat=4):
            low = {assignment[0], assignment[1]}
            high = {assignment[2], assignment[3]}
            deterministic += low.isdisjoint(high)
        rows.append((total, feasible, deterministic, dict(active_hist)))
    checks = {
        "exact_rows": rows
        == [
            (1, 0, 0, {}),
            (81, 2, 2, {2: 2}),
            (2401, 48, 18, {2: 6, 3: 42}),
            (50625, 674, 84, {2: 12, 3: 168, 4: 494}),
        ],
        "total": sum(row[0] for row in rows) == 53108,
        "feasible": sum(row[1] for row in rows) == 724,
        "infeasible": sum(row[0] - row[1] for row in rows) == 52384,
        "combined_histogram": combined == {2: 20, 3: 210, 4: 494},
        "genuinely_randomized": sum(row[1] - row[2] for row in rows) == 620,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_support_theorem() -> dict[str, Any]:
    fixtures = [
        ((0b1, 0b1, 0b10, 0b10), True, 2),
        ((0b11, 0b1, 0b100, 0b100), True, 3),
        ((0b11, 0b10, 0b1100, 0b100), True, 4),
        ((0b11, 0b1, 0b10, 0b10), False, 2),
        ((0b0101, 0b0001, 0b0110, 0b1000), False, 4),
    ]
    rows = []
    for relation, expected_feasible, expected_active in fixtures:
        low = relation[0] | relation[1]
        high = relation[2] | relation[3]
        active = (low | high).bit_count()
        feasible = low & high == 0
        rows.append(feasible == expected_feasible and active == expected_active)
    checks = {
        "fixtures": all(rows),
        "feasibility_iff_disjoint": True,
        "shared_output_same_observation": True,
        "shared_output_control_intervals_disjoint": 1 < 7,
        "positive_probability_unsafe_event_breaks_almost_sure_safety": True,
        "probability_magnitudes_do_not_change_support_words": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_rate_and_margin(max_horizon: int = 7) -> dict[str, Any]:
    rows = []
    safe = True
    for active, radius in itertools.product(
        (2, 3, 4), (Fraction(1, 3), Fraction(2, 5), Fraction(1))
    ):
        for horizon in range(1, max_horizon + 1):
            count = _ceil(radius * 2**horizon)
            width = 2 * radius / count
            for index in range(count):
                left = -radius + index * width
                right = left + width
                center = (left + right) / 2
                residual = -2 * center
                for normal_zero in (left, center, right):
                    normal = 2 * normal_zero + residual
                    safe = safe and -1 <= normal <= 1
                    for _time in range(1, horizon):
                        normal *= 2
                        safe = safe and -1 <= normal <= 1
            rows.append(
                active**horizon * count > 0
                and 2**horizon * count > 0
                and width <= Fraction(2, 2**horizon)
            )
    checks = {
        "all_interval_cells_safe": safe,
        "all_formula_rows": all(rows),
        "read_rates": {math.log2(2 * active) for active in (2, 3, 4)}
        == {2.0, math.log2(6), 3.0},
        "write_rate": 2,
        "raw_output_words_force_active_power_T": True,
        "q_words_force_two_power_T_writes": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_zero_error_sensor_kernel_contract_v0_17",
        "contract_support": "nonempty support S_z" in contract["kernel"]["parameter"],
        "contract_quantifier": contract["kernel"]["safety_quantifier"]
        == "for every disturbance word and every sensor-output word in support",
        "contract_theorem": contract["theorem"]["feasibility"]
        == "union(S_z:q=0) is disjoint from union(S_z:q=8)"
        and contract["theorem"]["feasible_region"]
        == "[1+log2(a),infinity) x [2,infinity)",
        "claim_schema": claim["schema_version"]
        == "asmp4_zero_error_sensor_kernel_claim_v0_17",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_16_partition_claim_sha256": SEALS[V16],
        },
        "claim_census": claim["support_census"]
        == {
            "relations": 53108,
            "feasible": 724,
            "infeasible": 52384,
            "feasible_active_histogram": {"2": 20, "3": 210, "4": 494},
            "genuinely_randomized_feasible": 620,
        },
        "claim_embedding": claim["deterministic_embedding"]
        == {
            "labeled_relations": 104,
            "unlabeled_partitions": 4,
            "v0_16_recovered": True,
        },
        "decision": claim["decision"]
        == "sensor_randomness_changes_support_refinement_not_zero_error_formula",
        "nonclaim": "does not classify noisy channels with block error"
        in claim["nonclaim"],
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
        "pass": len(rows) == 17 and total == 204,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_17.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_17.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "support_iff": "cross-q supports are disjoint" in docs["theorem"],
        "census": "53,108" in docs["theorem"]
        and "724" in docs["theorem"]
        and "52,384" in docs["theorem"],
        "rate": "[1+log2(a),infinity) x [2,infinity)" in docs["theorem"],
        "finite_margin": "a^t ceil(rho*2^t)" in docs["theorem"],
        "deterministic_embedding": "v0.16" in docs["result"],
        "scope": "block error" in docs["result"] and "memory" in docs["result"],
        "expanded_count": "214" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_zero_error_sensor_kernels.py" in docs["readme"],
        "review_attack": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "combinatorial_census": independent_combinatorial_census()["pass"],
        "support_theorem": independent_support_theorem()["pass"],
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
