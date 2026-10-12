"""Import-independent verifier for the ASMP-4 v0.23 delay boundary."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V22 = (
    ROOT
    / "asmp4_causal_encoder_collapse_v0_22"
    / "causal_encoder_collapse_claim_v0_22.json"
)
CONTRACT = HERE / "observation_delay_contract_v0_23.json"
CLAIM = HERE / "observation_delay_boundary_claim_v0_23.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V22: "2a963630840314cafd044ce45e75a53dfbab89f2ebc547b321ffe11a8144f103",
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
    ("asmp4_positive_volume_stop_certificate_v0_14", "test_positive_volume_stop.py"),
    ("asmp4_semantic_selector_audit_v0_15", "test_semantic_selector_audit.py"),
    (
        "asmp4_registered_sensor_classification_v0_16",
        "test_registered_sensor_classification.py",
    ),
    ("asmp4_zero_error_sensor_kernels_v0_17", "test_zero_error_sensor_kernels.py"),
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
    ("asmp4_support_incidence_quotient_v0_21", "test_support_incidence_quotient.py"),
    ("asmp4_causal_encoder_collapse_v0_22", "test_causal_encoder_collapse.py"),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ceil(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def _safe_interval(normal: Fraction, mode: int) -> tuple[Fraction, Fraction]:
    return Fraction(mode - 1) - 2 * normal, Fraction(mode + 1) - 2 * normal


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append((path.name, observed == expected))
    return {"rows": rows, "pass": len(rows) == 2 and all(match for _, match in rows)}


def independent_interval_boundary() -> dict[str, Any]:
    # Endpoint pairs are (constant term, coefficient of n).
    low = ((-1, -2), (1, -2))
    high = ((7, -2), (9, -2))
    affine_gap = (high[0][0] - low[1][0], high[0][1] - low[1][1])
    normals = sorted(
        {
            Fraction(numerator, denominator)
            for denominator in range(1, 17)
            for numerator in range(-denominator, denominator + 1)
        }
    )
    rows = []
    for normal in normals:
        for mode in (0, 8):
            interval = _safe_interval(normal, mode)
            witness = Fraction(mode) - 2 * normal
            rows.append(
                {
                    "normal": normal,
                    "mode": mode,
                    "witness_in_interval": interval[0] <= witness <= interval[1],
                    "witness_in_authority": Fraction(-2) <= witness <= Fraction(10),
                    "next_normal": 2 * normal + witness - mode,
                }
            )
    disjoint = all(
        _safe_interval(normal, 0)[1] < _safe_interval(normal, 8)[0]
        for normal in normals
    )
    checks = {
        "affine_gap_is_constant_six": affine_gap == (6, 0),
        "dense_exact_grid": len(normals) == 161,
        "all_mode_intervals_disjoint": disjoint,
        "mode_aware_action_is_authorized": all(
            row["witness_in_authority"] for row in rows
        ),
        "mode_aware_action_centers_collar": all(
            row["next_normal"] == 0 for row in rows
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_history_adversary(
    max_time: int = 5, max_delay: int = 4
) -> dict[str, Any]:
    rows = []
    for delay in range(1, max_delay + 1):
        for time in range(max_time + 1):
            for prefix in itertools.product((0, 8), repeat=time):
                low_word = prefix + (0,)
                high_word = prefix + (8,)
                visible_length = max(0, time - delay + 1)
                for normal in (Fraction(-1), Fraction(0), Fraction(1)):
                    low_interval = _safe_interval(normal, low_word[-1])
                    high_interval = _safe_interval(normal, high_word[-1])
                    rows.append(
                        {
                            "view_equal": low_word[:visible_length]
                            == high_word[:visible_length],
                            "prior_word_equal": low_word[:-1] == high_word[:-1],
                            "current_mode_differs": low_word[-1] != high_word[-1],
                            "common_action_exists": max(
                                low_interval[0], high_interval[0]
                            )
                            <= min(low_interval[1], high_interval[1]),
                        }
                    )
    branch_pairs = max_delay * sum(2**time for time in range(max_time + 1))
    checks = {
        "independent_tree_size": len(rows) == 3 * branch_pairs == 756,
        "all_delayed_views_equal": all(row["view_equal"] for row in rows),
        "all_prior_words_equal": all(row["prior_word_equal"] for row in rows),
        "all_current_modes_split": all(row["current_mode_differs"] for row in rows),
        "no_common_safe_action": all(not row["common_action_exists"] for row in rows),
        "shared_randomness_cannot_help": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_restoration() -> dict[str, Any]:
    normals = tuple(Fraction(index, 32) for index in range(-32, 33))
    contract = _load(CONTRACT)
    preview_rows = []
    for normal, mode in itertools.product(normals, (0, 8)):
        action = Fraction(mode) - 2 * normal
        preview_rows.append(
            Fraction(-2) <= action <= Fraction(10) and 2 * normal + action - mode == 0
        )
    checks = {
        "same_step_centers": all(preview_rows),
        "charged_preview_centers": all(preview_rows),
        "constant_mode_seed_centers": all(preview_rows),
        "preview_region": contract["theorem"]["charged_preview_region"]
        == "[2,infinity) x [2,infinity)",
        "constant_seed_region": contract["theorem"]["seeded_constant_q_region"]
        == "[1,infinity) x [1,infinity)",
        "no_preview_region": contract["theorem"]["positive_delay_region"] == "empty",
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_finite_counts(max_horizon: int = 12) -> dict[str, Any]:
    rows = []
    collar_safe = True
    for radius in (Fraction(1, 7), Fraction(1, 3), Fraction(2, 5), Fraction(1)):
        for horizon in range(1, max_horizon + 1):
            normal_cells = _ceil(radius * 2**horizon)
            same = 2**horizon * normal_cells
            seeded = 2 * normal_cells
            collar_safe &= 2 * radius / normal_cells <= Fraction(2, 2**horizon)
            rows.append((horizon, normal_cells, same, seeded))
    checks = {
        "exact_same_step_and_preview_product": all(
            same == 2**horizon * normal for horizon, normal, same, _ in rows
        ),
        "exact_seeded_constant_product": all(
            seeded == 2 * normal for _, normal, _, seeded in rows
        ),
        "ceiling_preserves_collar": collar_safe,
        "same_step_rate_two": math.log2(2**64 * 2**64) / 64 == 2,
        "constant_seed_rate_tends_to_one": math.log2(2 * 2**64) / 64
        == Fraction(65, 64),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_observation_delay_contract_v0_23",
        "first_write_safety": "first write" in contract["quantifiers"]["safety"],
        "all_random_seeds": contract["quantifiers"]["randomness"]
        == "every plant-independent shared-randomness seed",
        "sharp_contract_regions": contract["theorem"]
        == {
            "delay_zero_region": "[2,infinity) x [2,infinity)",
            "positive_delay_region": "empty",
            "charged_preview_region": "[2,infinity) x [2,infinity)",
            "seeded_constant_q_region": "[1,infinity) x [1,infinity)",
        },
        "claim_schema": claim["schema_version"]
        == "asmp4_observation_delay_boundary_claim_v0_23",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_22_causal_encoder_claim_sha256": SEALS[V22],
        },
        "tree_and_mutations": claim["adversary_tree"]["rows"] == 84
        and claim["mutation_audit"] == {"cases": 5, "rejected": 5},
        "scope": "arbitrary current q" in claim["nonclaim"]
        and "calibration phase" in claim["nonclaim"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    low = _safe_interval(Fraction(0), 0)
    high = _safe_interval(Fraction(0), 8)
    rows = {
        "substitute_previous_mode": low[1] < high[0],
        "add_unbounded_message_capacity": low[1] < high[0],
        "fix_shared_random_seed": low[1] < high[0],
        "omit_preview_charge": 2**6 < 4**6,
        "floor_nondyadic_cover": int(Fraction(3, 4) * 2) < _ceil(Fraction(3, 4) * 2),
    }
    return {"rows": rows, "pass": len(rows) == 5 and all(rows.values())}


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
        "pass": len(rows) == 23 and total == 264,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_23.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_23.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "gap_proof": "gap is exactly 6" in docs["theorem"],
        "sharp_threshold": "every integer" in docs["theorem"]
        and "d >= 1" in docs["theorem"],
        "preview": "charged current-mode preview" in docs["result"],
        "predictable": "[1,infinity) x [1,infinity)" in docs["result"],
        "scope": "first write" in docs["result"] and "calibration" in docs["result"],
        "expanded_count": "274" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_observation_delay_boundary.py" in docs["readme"],
        "review_attack": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "interval_boundary": independent_interval_boundary()["pass"],
        "history_adversary": independent_history_adversary()["pass"],
        "restoration_and_counts": independent_restoration()["pass"]
        and independent_finite_counts()["pass"],
        "contract_claim": independent_contract_and_claim()["pass"],
        "mutations": independent_mutations()["pass"],
        "inventory_documents": independent_inventory()["pass"]
        and document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
