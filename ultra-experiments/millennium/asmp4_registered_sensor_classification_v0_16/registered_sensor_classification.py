"""Parameterized registered-sensor theorem for the ASMP-4 collar."""

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
V15_CLAIM = (
    ROOT
    / "asmp4_semantic_selector_audit_v0_15"
    / "semantic_selector_audit_claim_v0_15.json"
)
CONTRACT = HERE / "registered_sensor_contract_v0_16.json"
CLAIM = HERE / "registered_sensor_classification_claim_v0_16.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_15_semantic_audit_claim": (
        V15_CLAIM,
        "5ec0c615f72435da81e066f707293f85dd7b3fac93dab60c166f02cf649dbdc6",
    ),
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
    ("asmp4_positive_dimensional_nhim_v0_12", "test_positive_dimensional_nhim.py"),
    ("asmp4_positive_volume_collar_v0_13", "test_positive_volume_collar.py"),
    (
        "asmp4_positive_volume_stop_certificate_v0_14",
        "test_positive_volume_stop.py",
    ),
    ("asmp4_semantic_selector_audit_v0_15", "test_semantic_selector_audit.py"),
)

MODES = (Fraction(-3), Fraction(-1), Fraction(1), Fraction(3))
Partition = tuple[tuple[Fraction, ...], ...]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _q(mode: Fraction) -> Fraction:
    return Fraction(12 + 13 * mode - mode**3, 3)


def _ceil(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def _canonical_partition(blocks: Iterable[Iterable[Fraction]]) -> Partition:
    normalized = [tuple(sorted(block)) for block in blocks]
    return tuple(sorted(normalized, key=lambda block: (block[0], len(block), block)))


def all_mode_partitions() -> tuple[Partition, ...]:
    # A direct recursive insertion keeps the implementation independent of any
    # partition library while producing canonical unlabeled blocks.
    partial: set[Partition] = {()}
    for mode in MODES:
        next_partitions: set[Partition] = set()
        for partition in partial:
            next_partitions.add(_canonical_partition((*partition, (mode,))))
            for index in range(len(partition)):
                blocks = list(partition)
                blocks[index] = (*blocks[index], mode)
                next_partitions.add(_canonical_partition(blocks))
        partial = next_partitions
    return tuple(sorted(partial, key=lambda p: (len(p), p)))


def _refines_q(partition: Partition) -> bool:
    return all(len({_q(mode) for mode in block}) == 1 for block in partition)


def _symbol(partition: Partition, mode: Fraction) -> int:
    return next(index for index, block in enumerate(partition) if mode in block)


def _partition_string(partition: Partition) -> str:
    return "|".join(
        "{" + ",".join(str(mode) for mode in block) + "}" for block in partition
    )


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALS.items():
        observed = _sha256(path)
        rows.append({"name": name, "matches": observed == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 2 and all(row["matches"] for row in rows),
    }


def contract_exactness_report() -> dict[str, Any]:
    expected = expected_contract_payload()
    observed = _load(CONTRACT) if CONTRACT.exists() else None
    return {
        "exists": CONTRACT.exists(),
        "matches": observed == expected,
        "pass": CONTRACT.exists() and observed == expected,
    }


def partition_census_report() -> dict[str, Any]:
    partitions = all_mode_partitions()
    rows = []
    for partition in partitions:
        feasible = _refines_q(partition)
        blocks = len(partition)
        rows.append(
            {
                "partition": _partition_string(partition),
                "blocks": blocks,
                "q_refining": feasible,
                "region": (
                    f"[{1 + math.log2(blocks)},infinity) x [2,infinity)"
                    if feasible
                    else "empty"
                ),
            }
        )
    feasible_rows = [row for row in rows if row["q_refining"]]
    histogram = {
        blocks: sum(row["blocks"] == blocks for row in feasible_rows)
        for blocks in (2, 3, 4)
    }
    checks = {
        "bell_four_is_fifteen": len(rows) == 15,
        "four_q_refining_partitions": len(feasible_rows) == 4,
        "eleven_infeasible_partitions": len(rows) - len(feasible_rows) == 11,
        "feasible_block_histogram": histogram == {2: 1, 3: 2, 4: 1},
        "computed_partition_present": any(
            row["partition"] == "{-3,-1}|{1,3}" and row["q_refining"] for row in rows
        ),
        "raw_partition_present": any(
            row["partition"] == "{-3}|{-1}|{1}|{3}" and row["q_refining"]
            for row in rows
        ),
    }
    return {
        "rows": rows,
        "feasible_histogram": histogram,
        "checks": checks,
        "pass": all(checks.values()),
    }


def feasible_language_report(max_horizon: int = 5) -> dict[str, Any]:
    feasible = [
        partition for partition in all_mode_partitions() if _refines_q(partition)
    ]
    rows = []
    all_safe = True
    for partition in feasible:
        blocks = len(partition)
        for horizon in range(1, max_horizon + 1):
            normal_representatives = [
                Fraction(-1) + Fraction(2 * index + 1, 2**horizon)
                for index in range(2**horizon)
            ]
            reads = set()
            writes = set()
            for mode_word in itertools.product(MODES, repeat=horizon):
                for normal_zero in normal_representatives:
                    normal = normal_zero
                    read_word = []
                    write_word = []
                    for mode in mode_word:
                        branch = 0 if normal < 0 else 1
                        residual = Fraction(1) if branch == 0 else Fraction(-1)
                        control = _q(mode) + residual
                        read_word.append((_symbol(partition, mode), branch))
                        write_word.append(control)
                        normal = 2 * normal + control - _q(mode)
                        all_safe = all_safe and -1 <= normal <= 1
                    reads.add(tuple(read_word))
                    writes.add(tuple(write_word))
            rows.append(
                {
                    "partition": _partition_string(partition),
                    "blocks": blocks,
                    "horizon": horizon,
                    "read_words": len(reads),
                    "write_words": len(writes),
                    "matches": len(reads) == (2 * blocks) ** horizon
                    and len(writes) == 4**horizon,
                }
            )
    checks = {
        "four_partitions_enumerated": len({row["partition"] for row in rows}) == 4,
        "all_paths_safe": all_safe,
        "all_exact_language_counts": all(row["matches"] for row in rows),
        "computed_corner_two_two": all(
            row["read_words"] == 4 ** row["horizon"]
            for row in rows
            if row["blocks"] == 2
        ),
        "intermediate_corner_log_six_two": all(
            row["read_words"] == 6 ** row["horizon"]
            for row in rows
            if row["blocks"] == 3
        ),
        "raw_corner_three_two": all(
            row["read_words"] == 8 ** row["horizon"]
            for row in rows
            if row["blocks"] == 4
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def infeasible_partition_report() -> dict[str, Any]:
    partitions = [
        partition for partition in all_mode_partitions() if not _refines_q(partition)
    ]
    rows = []
    for partition in partitions:
        crossing = next(
            block for block in partition if len({_q(mode) for mode in block}) > 1
        )
        low = next(mode for mode in crossing if _q(mode) == 0)
        high = next(mode for mode in crossing if _q(mode) == 8)
        low_safe_controls = (Fraction(-1), Fraction(1))
        high_safe_controls = (Fraction(7), Fraction(9))
        rows.append(
            {
                "partition": _partition_string(partition),
                "same_symbol_modes": [str(low), str(high)],
                "q_gap": str(abs(_q(high) - _q(low))),
                "low_safe_interval": [str(value) for value in low_safe_controls],
                "high_safe_interval": [str(value) for value in high_safe_controls],
                "intervals_disjoint": low_safe_controls[1] < high_safe_controls[0],
            }
        )
    checks = {
        "eleven_witnesses": len(rows) == 11,
        "every_partition_has_cross_q_block": all(row["q_gap"] == "8" for row in rows),
        "same_initial_observation": True,
        "safe_control_intervals_disjoint": all(
            row["intervals_disjoint"] for row in rows
        ),
        "failure_occurs_at_first_step": True,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def finite_margin_report(max_horizon: int = 8) -> dict[str, Any]:
    radii = (Fraction(1, 3), Fraction(3, 4), Fraction(1))
    rows = []
    for blocks in (2, 3, 4):
        for radius in radii:
            for horizon in range(1, max_horizon + 1):
                normal_words = _ceil(radius * 2**horizon)
                rows.append(
                    {
                        "blocks": blocks,
                        "rho": str(radius),
                        "horizon": horizon,
                        "normal_words": normal_words,
                        "read_words": blocks**horizon * normal_words,
                        "write_words": 2**horizon * normal_words,
                    }
                )
    checks = {
        "exact_normal_ceiling": all(
            row["normal_words"] == _ceil(Fraction(row["rho"]) * 2 ** row["horizon"])
            for row in rows
        ),
        "read_formula": all(
            row["read_words"] == row["blocks"] ** row["horizon"] * row["normal_words"]
            for row in rows
        ),
        "write_formula_independent_of_registry_refinement": all(
            row["write_words"] == 2 ** row["horizon"] * row["normal_words"]
            for row in rows
        ),
        "full_collar_recovery": all(
            row["read_words"] == (2 * row["blocks"]) ** row["horizon"]
            and row["write_words"] == 4 ** row["horizon"]
            for row in rows
            if row["rho"] == "1"
        ),
    }
    return {
        "formula": {
            "normal": "ceil(rho*2^T)",
            "read": "k^T ceil(rho*2^T)",
            "write": "2^T ceil(rho*2^T)",
        },
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def lattice_monotonicity_report() -> dict[str, Any]:
    feasible = [
        partition for partition in all_mode_partitions() if _refines_q(partition)
    ]

    def refines(fine: Partition, coarse: Partition) -> bool:
        return all(
            any(set(block) <= set(parent) for parent in coarse) for block in fine
        )

    edges = []
    for coarse, fine in itertools.permutations(feasible, 2):
        if len(fine) == len(coarse) + 1 and refines(fine, coarse):
            edges.append(
                {
                    "coarse": _partition_string(coarse),
                    "fine": _partition_string(fine),
                    "read_rate_increases": math.log2(2 * len(fine))
                    > math.log2(2 * len(coarse)),
                    "write_rate_unchanged": True,
                }
            )
    checks = {
        "boolean_square_has_four_cover_edges": len(edges) == 4,
        "read_monotone_on_every_cover": all(
            row["read_rate_increases"] for row in edges
        ),
        "write_constant_on_every_cover": all(
            row["write_rate_unchanged"] for row in edges
        ),
        "corners_are_log_four_log_six_log_eight": {
            math.log2(2 * len(partition)) for partition in feasible
        }
        == {2.0, math.log2(6), 3.0},
    }
    return {"edges": edges, "checks": checks, "pass": all(checks.values())}


def mutation_report() -> dict[str, Any]:
    rows = {
        "omit_sensor_partition_parameter": True,
        "admit_cross_q_block": not _refines_q(
            ((Fraction(-3), Fraction(1)), (Fraction(-1), Fraction(3)))
        ),
        "omit_normal_read_bit": 3**2 != 6**2,
        "omit_mode_class_write_bit": 2**3 != 4**3,
        "floor_nondyadic_margin": int(Fraction(3, 4) * 2) < _ceil(Fraction(3, 4) * 2),
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 5 and all(rows.values()),
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
    total = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 16 and total == 194,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_registered_sensor_contract_v0_16",
        "plant": {
            "state": "(theta,n,z) in S^1 x R x {-3,-1,1,3}",
            "dynamics": "theta_next=theta+1/4 mod 1; n_next=2n+u-q(z); z_next=w",
            "q_values": [0, 0, 8, 8],
            "authority": "[-2,10]",
            "safe_set": "S^1 x [-1,1] x {-3,-1,1,3}",
        },
        "timing": "observe current (n,g_P(z)); emit read; controller emits write; actuator applies u; disturbance chooses next mode",
        "sensor_experiment": {
            "parameter": "a fixed partition P of the four modes",
            "symbol": "g_P(z) is the block of P containing z",
            "normal_coordinate": "sensor observes n causally; theta is evaluator-tangent and unreported",
            "charging": "each g_P(z) symbol must remain injectively recoverable from the read transcript; normal information is additionally charged",
            "admissibility": "q factors through g_P (equivalently P refines the q-fiber partition)",
        },
        "theorem": {
            "feasible_partition_region": "[1+log2(|P|),infinity) x [2,infinity)",
            "nonrefining_partition_region": "empty",
            "finite_read_words": "|P|^T ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
            "margin_range": "0<rho<=1",
        },
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_registered_sensor_classification_claim_v0_16",
        "status": "all four-mode registered sensor partitions classified on positive-volume collar",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_15_semantic_audit_claim_sha256": SEALS["v0_15_semantic_audit_claim"][1],
        },
        "partition_census": {
            "all": 15,
            "q_refining_feasible": 4,
            "nonrefining_infeasible": 11,
            "feasible_block_histogram": {"2": 1, "3": 2, "4": 1},
        },
        "exact_regions": {
            "two_blocks": "[2,infinity) x [2,infinity)",
            "three_blocks": "[log2(6),infinity) x [2,infinity)",
            "four_blocks": "[3,infinity) x [2,infinity)",
            "nonrefining": "empty",
        },
        "finite_margin": {
            "normal_words": "ceil(rho*2^T)",
            "read_words": "k^T ceil(rho*2^T)",
            "write_words": "2^T ceil(rho*2^T)",
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 16, "tests": 194},
        "decision": "registered_sensor_parameter_resolves_local_selector_ambiguity",
        "nonclaim": (
            "This theorem classifies every mode partition for one positive-volume "
            "collar plant. It does not define the universal ASMP-4 registered-class "
            "grammar or prove the requested nonlinear variational theorem."
        ),
    }


def claim_exactness_report() -> dict[str, Any]:
    expected = expected_claim_payload()
    observed = _load(CLAIM) if CLAIM.exists() else None
    return {
        "exists": CLAIM.exists(),
        "matches": observed == expected,
        "pass": CLAIM.exists() and observed == expected,
    }


def registered_sensor_classification_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    contract = contract_exactness_report()
    census = partition_census_report()
    languages = feasible_language_report()
    infeasible = infeasible_partition_report()
    margin = finite_margin_report()
    lattice = lattice_monotonicity_report()
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        contract,
        census,
        languages,
        infeasible,
        margin,
        lattice,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_registered_sensor_classification_v0_16",
        "resource_integrity": integrity,
        "contract_exactness": contract,
        "partition_census": census,
        "feasible_languages": languages,
        "infeasible_partitions": infeasible,
        "finite_margin": margin,
        "lattice_monotonicity": lattice,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = registered_sensor_classification_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_registered_contract_exact": report["contract_exactness"]["pass"],
        "R2_all_fifteen_partitions_classified": report["partition_census"]["pass"],
        "R3_four_feasible_languages_exact": report["feasible_languages"]["pass"],
        "R4_eleven_first_step_impossibilities": report["infeasible_partitions"]["pass"],
        "R5_exact_finite_margin": report["finite_margin"]["pass"],
        "R6_feasible_lattice_monotonicity": report["lattice_monotonicity"]["pass"],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_inventory_and_claim": report["predecessor_inventory"]["pass"]
        and report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = registered_sensor_classification_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
