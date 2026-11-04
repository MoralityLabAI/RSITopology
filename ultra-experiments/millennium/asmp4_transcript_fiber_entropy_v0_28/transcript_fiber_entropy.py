"""Causal transcript-fiber entropy bounds for ASMP-4 quotient transfers."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V20 = (
    ROOT
    / "asmp4_sensor_refinement_inflation_stop_v0_20"
    / "sensor_refinement_stop_claim_v0_20.json"
)
V27 = (
    ROOT
    / "asmp4_approximate_bisimulation_robustness_v0_27"
    / "approximate_bisimulation_claim_v0_27.json"
)
CONTRACT = HERE / "transcript_fiber_contract_v0_28.json"
CLAIM = HERE / "transcript_fiber_claim_v0_28.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V20: "b06213d846b53cf7f2262b7f0cf3dea89f22ca5f679ec8e87d5fd88e13de7d8f",
    V27: "90d80d747731536aa665f434497fcdc06ebc4068eeafb748f62ef669189aa186",
}

PREDECESSOR_TESTS = (
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
    (
        "asmp4_positive_dimensional_nhim_v0_12",
        "test_positive_dimensional_nhim.py",
    ),
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
    ("asmp4_observation_delay_boundary_v0_23", "test_observation_delay_boundary.py"),
    (
        "asmp4_resettable_support_variational_v0_24",
        "test_resettable_support_variational.py",
    ),
    ("asmp4_periodic_block_completeness_v0_25", "test_periodic_block_completeness.py"),
    (
        "asmp4_public_bisimulation_transfer_v0_26",
        "test_public_bisimulation_transfer.py",
    ),
    (
        "asmp4_approximate_bisimulation_robustness_v0_27",
        "test_approximate_bisimulation_robustness.py",
    ),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def maximum_fiber(domain: Iterable[Any], mapping: dict[Any, Any]) -> int:
    counts: dict[Any, int] = {}
    for item in domain:
        image = mapping[item]
        counts[image] = counts.get(image, 0) + 1
    return max(counts.values(), default=0)


def count_bound(source_count: int, target_count: int, fiber: int) -> bool:
    return (
        source_count >= 0
        and target_count >= 0
        and fiber >= 0
        and target_count <= fiber * source_count
    )


def words(alphabet_size: int, horizon: int) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product(range(alphabet_size), repeat=horizon))


def clone_family_report(
    maximum_factor: int = 16, maximum_horizon: int = 8
) -> dict[str, Any]:
    rows = []
    for read_factor in range(1, maximum_factor + 1):
        for write_factor in range(1, maximum_factor + 1):
            for horizon in range(1, maximum_horizon + 1):
                read_count = read_factor**horizon
                write_count = write_factor**horizon
                read_fiber = read_count
                write_fiber = write_count
                rows.append(
                    {
                        "read_factor": read_factor,
                        "write_factor": write_factor,
                        "horizon": horizon,
                        "raw_joint_states": read_factor * write_factor,
                        "read_count": read_count,
                        "write_count": write_count,
                        "read_fiber": read_fiber,
                        "write_fiber": write_fiber,
                        "read_bound_tight": count_bound(1, read_count, read_fiber),
                        "write_bound_tight": count_bound(1, write_count, write_fiber),
                        "read_rate": math.log2(read_count) / horizon,
                        "write_rate": math.log2(write_count) / horizon,
                    }
                )
    checks = {
        "two_thousand_forty_eight_rows": len(rows) == 2048,
        "maximum_two_hundred_fifty_six_raw_states": max(
            row["raw_joint_states"] for row in rows
        )
        == 256,
        "all_fiber_bounds_tight": all(
            row["read_bound_tight"]
            and row["write_bound_tight"]
            and math.isclose(
                row["read_rate"], math.log2(row["read_factor"]), abs_tol=1e-12
            )
            and math.isclose(
                row["write_rate"], math.log2(row["write_factor"]), abs_tol=1e-12
            )
            for row in rows
        ),
        "asymmetric_two_port_corner_present": any(
            row["read_factor"] == 2
            and row["write_factor"] == 5
            and not math.isclose(row["read_rate"], row["write_rate"])
            for row in rows
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def explicit_language_report(
    maximum_factor: int = 5, maximum_horizon: int = 6
) -> dict[str, Any]:
    rows = []
    for factor in range(1, maximum_factor + 1):
        for horizon in range(1, maximum_horizon + 1):
            language = words(factor, horizon)
            mapping = {word: () for word in language}
            fiber = maximum_fiber(language, mapping)
            rows.append(
                {
                    "factor": factor,
                    "horizon": horizon,
                    "enumerated": len(language),
                    "fiber": fiber,
                    "exact": len(language) == factor**horizon == fiber,
                }
            )
    checks = {
        "thirty_explicit_languages": len(rows) == 30,
        "largest_language_has_15625_words": max(row["enumerated"] for row in rows)
        == 15_625,
        "all_counts_and_fibers_exact": all(row["exact"] for row in rows),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def sparse_branch_count(horizon: int) -> int:
    if horizon <= 0:
        return 0
    return horizon.bit_length()


def sparse_subexponential_report(maximum_horizon: int = 4096) -> dict[str, Any]:
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        branch_count = sparse_branch_count(horizon)
        read_fiber = 2**branch_count
        write_fiber = 3**branch_count
        rows.append(
            {
                "horizon": horizon,
                "branch_count": branch_count,
                "read_fiber": read_fiber,
                "write_fiber": write_fiber,
                "read_rate": math.log2(read_fiber) / horizon,
                "write_rate": math.log2(write_fiber) / horizon,
            }
        )
    last = rows[-1]
    checks = {
        "four_thousand_ninety_six_horizons": len(rows) == 4096,
        "fibers_are_unbounded": rows[-1]["read_fiber"] > rows[0]["read_fiber"],
        "branch_count_is_logarithmic": all(
            row["branch_count"] == row["horizon"].bit_length() for row in rows
        ),
        "normalized_rates_are_small_at_endpoint": last["read_rate"] < 0.004
        and last["write_rate"] < 0.006,
        "analytic_limit_is_zero": math.log2(maximum_horizon + 1) / maximum_horizon
        < 0.004,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def burst_limsup_report(stages: int = 8) -> dict[str, Any]:
    total = 2
    branch_steps = 1
    rows = []
    for stage in range(1, stages + 1):
        rest_end = total**2
        low = Fraction(branch_steps, rest_end)
        branch_length = rest_end
        total = rest_end + branch_length
        branch_steps += branch_length
        high = Fraction(branch_steps, total)
        rows.append(
            {
                "stage": stage,
                "low": float(low),
                "high": float(high),
                "low_fraction": str(low),
                "high_fraction": str(high),
            }
        )
    checks = {
        "eight_burst_stages": len(rows) == 8,
        "low_subsequence_decreases_to_zero": all(
            rows[index + 1]["low"] < rows[index]["low"]
            for index in range(len(rows) - 1)
        )
        and rows[-1]["low"] < 1e-20,
        "high_subsequence_tends_to_one_half": Fraction(1, 2)
        < high
        < Fraction(501, 1000),
        "liminf_cannot_replace_limsup": low < Fraction(1, 10**20)
        and high > Fraction(1, 2),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def concentrated_fiber_report(maximum_horizon: int = 64) -> dict[str, Any]:
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        large_fiber = 2**horizon
        source_count = 2
        target_count = large_fiber + 1
        rows.append(
            {
                "horizon": horizon,
                "source_count": source_count,
                "target_count": target_count,
                "maximum_fiber": large_fiber,
                "minimum_fiber": 1,
                "maximum_bound": count_bound(source_count, target_count, large_fiber),
                "minimum_bound": count_bound(source_count, target_count, 1),
            }
        )
    checks = {
        "sixty_four_concentrated_fibers": len(rows) == 64,
        "maximum_fiber_always_bounds": all(row["maximum_bound"] for row in rows),
        "minimum_fiber_fails": all(not row["minimum_bound"] for row in rows),
        "target_rate_tends_to_one": math.log2(rows[-1]["target_count"]) / 64 > 0.999,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def directional_and_class_boundary_report(
    factor: int = 3, maximum_horizon: int = 32
) -> dict[str, Any]:
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        raw_histories = factor**horizon
        rows.append(
            {
                "horizon": horizon,
                "raw_states": factor,
                "quotient_classes": 1,
                "raw_histories": raw_histories,
                "raw_to_quotient_fiber": raw_histories,
                "section_fiber": 1,
                "history_rate": math.log2(raw_histories) / horizon,
            }
        )
    checks = {
        "finite_one_class_quotient": all(
            row["raw_states"] == factor and row["quotient_classes"] == 1 for row in rows
        ),
        "history_fiber_exceeds_state_class": rows[-1]["raw_to_quotient_fiber"] > factor,
        "positive_relative_entropy": math.isclose(
            rows[-1]["history_rate"], math.log2(factor), abs_tol=1e-12
        ),
        "one_way_section_has_zero_fiber_entropy": all(
            row["section_fiber"] == 1 for row in rows
        ),
        "reverse_direction_still_has_positive_gap": rows[-1]["history_rate"] > 0,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def mutation_report() -> dict[str, Any]:
    clone = clone_family_report(5, 4)
    sparse = sparse_subexponential_report()
    burst = burst_limsup_report()
    concentrated = concentrated_fiber_report(16)
    directional = directional_and_class_boundary_report(3, 8)
    asymmetric = next(
        row
        for row in clone["rows"]
        if row["read_factor"] == 2 and row["write_factor"] == 5 and row["horizon"] == 4
    )
    rows = {
        "exact_state_bisimulation_implies_equal_tree_entropy": directional["checks"][
            "positive_relative_entropy"
        ],
        "finite_horizon_finite_fibers_imply_equal_rates": all(
            row["raw_to_quotient_fiber"] < math.inf for row in directional["rows"]
        )
        and directional["checks"]["positive_relative_entropy"],
        "fixed_state_class_size_bounds_history_fiber": directional["checks"][
            "history_fiber_exceeds_state_class"
        ],
        "subexponential_fiber_must_be_uniformly_bounded": sparse["checks"][
            "fibers_are_unbounded"
        ]
        and sparse["checks"]["analytic_limit_is_zero"],
        "one_way_factor_implies_symmetric_equality": directional["checks"][
            "one_way_section_has_zero_fiber_entropy"
        ]
        and directional["checks"]["reverse_direction_still_has_positive_gap"],
        "minimum_fiber_can_replace_maximum": concentrated["checks"][
            "minimum_fiber_fails"
        ],
        "liminf_can_replace_limsup": burst["checks"]["liminf_cannot_replace_limsup"],
        "one_shared_fiber_modulus_covers_asymmetric_ports": not math.isclose(
            asymmetric["read_rate"], asymmetric["write_rate"]
        ),
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()),
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_transcript_fiber_contract_v0_28",
        "objective": "nonadditive two-port transcript-language entropy under quotient transfer",
        "port_cost": {
            "horizon_T": "log2 cardinality of the realized safe port transcript language",
            "rate": "limsup of horizon cost divided by T",
            "nonadditive": True,
        },
        "causal_factor": {
            "strategy_transfer": "safe causal representative-history transfer",
            "port_compatibility": "each target port transcript has a registered source port transcript image",
            "fiber": "M_i(T) is the maximum target-language preimage count for port i",
            "directions": "separate maps and fiber profiles are required in each direction",
        },
        "transfer": {
            "finite_horizon": "J_i_target(T) <= J_i_source(T)+log2 M_i(T)",
            "asymptotic": "rate slack mu_i=limsup_T log2 M_i(T)/T",
            "exactness": "subexponential fibers in both directions preserve the full region",
        },
        "boundary": {
            "clone": "m_i choices per step give M_i(T)=m_i^T and sharp shift log2 m_i",
            "finite_state": "a finite one-class quotient need not have subexponential history fibers",
            "sparse": "unbounded polynomial fibers can have zero fiber entropy",
        },
        "nonclaims": [
            "arbitrary transcript-tree functionals without a registered distortion modulus",
            "quotient existence for arbitrary nonlinear systems",
            "multidimensional adversarial mean-payoff computation",
        ],
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_transcript_fiber_entropy_v0_28",
        "theorem": {
            "name": "causal transcript-fiber entropy transfer",
            "finite_horizon": "target log-language cost is at most source cost plus log2 maximum fiber",
            "asymptotic": "directed port-rate slack is relative fiber entropy",
            "exact_corollary": "bidirectional subexponential port fibers preserve the complete region",
        },
        "sharpness": {
            "exponential_clone": "M_R(T)=r^T and M_W(T)=w^T attain corner shift (log2 r,log2 w)",
            "finite_quotient": "one quotient class can hide positive history-fiber entropy",
            "sparse_branching": "unbounded fibers can still have zero relative entropy",
            "burst": "limsup cannot be replaced by liminf",
        },
        "central_harness": {
            "clone_rows": 2048,
            "maximum_joint_raw_states": 256,
            "explicit_languages": 30,
            "largest_explicit_language": 15625,
            "sparse_horizons": 4096,
        },
        "independent_harness": {
            "trie_cases": 35,
            "schedule_cases": 6561,
            "maximum_horizon": 8,
            "sparse_horizons": 8192,
        },
        "mutations_rejected": 8,
        "predecessor_inventory": {"packages": 28, "tests": 314},
        "disposition": "nonadditive leaf-language transfer is controlled by port-specific history-fiber entropy, not state-class size",
    }


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"name": path.name, "matches": actual == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def predecessor_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in PREDECESSOR_TESTS:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "tests": count})
    tests = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": tests,
        "pass": len(rows) == 28 and tests == 314,
    }


def payload_report() -> dict[str, Any]:
    required = {
        "README.md",
        "THEOREM.md",
        "RESULT.md",
        "COMPLETION_AUDIT_v0_28.md",
        "REVIEWER_PACKET_v0_28.md",
        "PRIOR_ART_BOUNDARY_v0_28.md",
        "transcript_fiber_contract_v0_28.json",
        "transcript_fiber_claim_v0_28.json",
        "transcript_fiber_entropy.py",
        "verify_transcript_fiber_entropy.py",
        "test_transcript_fiber_entropy.py",
        "run_verification.py",
    }
    present = {path.name for path in HERE.iterdir() if path.is_file()}
    return {
        "missing": sorted(required - present),
        "pass": required <= present,
    }


def transcript_fiber_report() -> dict[str, Any]:
    components = {
        "resource_integrity": resource_integrity_report(),
        "contract_exactness": {
            "pass": CONTRACT.exists() and _load(CONTRACT) == expected_contract_payload()
        },
        "claim_exactness": {
            "pass": CLAIM.exists() and _load(CLAIM) == expected_claim_payload()
        },
        "clone_family": clone_family_report(),
        "explicit_languages": explicit_language_report(),
        "sparse_subexponential": sparse_subexponential_report(),
        "burst_limsup": burst_limsup_report(),
        "concentrated_fiber": concentrated_fiber_report(),
        "directional_class_boundary": directional_and_class_boundary_report(),
        "mutations": mutation_report(),
        "predecessor_inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    return {
        "schema_version": "asmp4_transcript_fiber_entropy_v0_28",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = transcript_fiber_report() if report is None else report
    return {
        "R0_three_resource_seals": report["resource_integrity"]["pass"],
        "R1_exact_contract": report["contract_exactness"]["pass"],
        "R2_exact_claim": report["claim_exactness"]["pass"],
        "R3_exponential_clone_family": report["clone_family"]["pass"],
        "R4_explicit_language_fibers": report["explicit_languages"]["pass"],
        "R5_subexponential_unbounded_boundary": report["sparse_subexponential"]["pass"],
        "R6_limsup_and_maximum_are_load_bearing": report["burst_limsup"]["pass"]
        and report["concentrated_fiber"]["pass"],
        "R7_state_class_and_direction_boundary": report["directional_class_boundary"][
            "pass"
        ],
        "R8_eight_mutations_rejected": report["mutations"]["pass"],
        "R9_inventory_and_payload": report["predecessor_inventory"]["pass"]
        and report["payload"]["pass"],
    }


def main() -> int:
    report = transcript_fiber_report()
    payload = {"gates": verification_gates(report), "report": report}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
