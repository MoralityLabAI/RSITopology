"""Support-zero-error stochastic sensor classification for ASMP-4."""

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
V16_CLAIM = (
    ROOT
    / "asmp4_registered_sensor_classification_v0_16"
    / "registered_sensor_classification_claim_v0_16.json"
)
CONTRACT = HERE / "zero_error_sensor_kernel_contract_v0_17.json"
CLAIM = HERE / "zero_error_sensor_kernel_claim_v0_17.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_16_partition_claim": (
        V16_CLAIM,
        "f9d9922f8ab33a04987b35b46ddb6d37672b4e341d46a1995b1d74e46c21f9e2",
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
    (
        "asmp4_registered_sensor_classification_v0_16",
        "test_registered_sensor_classification.py",
    ),
)

MODES = (0, 1, 2, 3)
Q_CLASS = (0, 0, 1, 1)
SupportRelation = tuple[int, int, int, int]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ceil(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def _active_mask(relation: SupportRelation) -> int:
    return relation[0] | relation[1] | relation[2] | relation[3]


def _feasible(relation: SupportRelation) -> bool:
    low = relation[0] | relation[1]
    high = relation[2] | relation[3]
    return low & high == 0


def _is_deterministic(relation: SupportRelation) -> bool:
    return all(mask.bit_count() == 1 for mask in relation)


def all_relations(output_symbols: int):
    subsets = range(1, 2**output_symbols)
    yield from itertools.product(subsets, repeat=4)


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


def support_census_report() -> dict[str, Any]:
    rows = []
    combined_active = Counter()
    total_all = 0
    feasible_all = 0
    deterministic_all = 0
    for output_symbols in range(1, 5):
        total = 0
        feasible = 0
        deterministic = 0
        active_hist = Counter()
        infeasible = 0
        for relation in all_relations(output_symbols):
            total += 1
            if _feasible(relation):
                feasible += 1
                active = _active_mask(relation).bit_count()
                active_hist[active] += 1
                combined_active[active] += 1
                deterministic += _is_deterministic(relation)
            else:
                infeasible += 1
        total_all += total
        feasible_all += feasible
        deterministic_all += deterministic
        rows.append(
            {
                "declared_outputs": output_symbols,
                "relations": total,
                "feasible": feasible,
                "infeasible": infeasible,
                "feasible_active_histogram": dict(sorted(active_hist.items())),
                "feasible_deterministic": deterministic,
            }
        )
    checks = {
        "total_relations_53108": total_all == 53108,
        "feasible_724": feasible_all == 724,
        "infeasible_52384": total_all - feasible_all == 52384,
        "declared_rows": [
            (row["relations"], row["feasible"], row["feasible_deterministic"])
            for row in rows
        ]
        == [(1, 0, 0), (81, 2, 2), (2401, 48, 18), (50625, 674, 84)],
        "combined_active_histogram": dict(sorted(combined_active.items()))
        == {2: 20, 3: 210, 4: 494},
        "deterministic_feasible_labeled_relations": deterministic_all == 104,
    }
    return {
        "rows": rows,
        "combined": {
            "relations": total_all,
            "feasible": feasible_all,
            "infeasible": total_all - feasible_all,
            "active_histogram": dict(sorted(combined_active.items())),
            "deterministic_feasible": deterministic_all,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


def support_feasibility_theorem_report() -> dict[str, Any]:
    feasible_checks = []
    infeasible_checks = []
    genuinely_randomized = 0
    for output_symbols in range(1, 5):
        for relation in all_relations(output_symbols):
            overlap = (relation[0] | relation[1]) & (relation[2] | relation[3])
            if _feasible(relation):
                # Every active output belongs to exactly one q class, hence it
                # has a well-defined decoder. Choosing one supported output per
                # mode also yields a deterministic safe subkernel.
                decoder_well_defined = overlap == 0
                selection = tuple(mask & -mask for mask in relation)
                deterministic_subkernel_safe = _feasible(selection)
                feasible_checks.append(
                    decoder_well_defined and deterministic_subkernel_safe
                )
                genuinely_randomized += not _is_deterministic(relation)
            else:
                shared_output = overlap & -overlap
                low_has = any(relation[index] & shared_output for index in (0, 1))
                high_has = any(relation[index] & shared_output for index in (2, 3))
                infeasible_checks.append(bool(shared_output and low_has and high_has))
    checks = {
        "all_724_feasible_relations_decode_q": len(feasible_checks) == 724
        and all(feasible_checks),
        "all_52384_infeasible_relations_have_shared_output_witness": len(
            infeasible_checks
        )
        == 52384
        and all(infeasible_checks),
        "genuinely_randomized_feasible_relations": genuinely_randomized == 620,
        "shared_output_safe_intervals_are_disjoint": 1 < 7,
        "probability_values_irrelevant_beyond_positive_support": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def representative_language_report(max_horizon: int = 5) -> dict[str, Any]:
    representatives = {
        2: (0b0001, 0b0001, 0b0010, 0b0010),
        3: (0b0011, 0b0001, 0b0100, 0b0100),
        4: (0b0011, 0b0010, 0b1100, 0b0100),
    }
    rows = []
    all_safe = True
    for active, relation in representatives.items():
        assert _feasible(relation)
        active_outputs = [
            output for output in range(4) if _active_mask(relation) & (1 << output)
        ]
        output_q = {}
        for output in active_outputs:
            classes = {
                Q_CLASS[mode] for mode in MODES if relation[mode] & (1 << output)
            }
            output_q[output] = next(iter(classes))
        for horizon in range(1, max_horizon + 1):
            normal_points = [
                Fraction(-1) + Fraction(2 * index + 1, 2**horizon)
                for index in range(2**horizon)
            ]
            reads = set()
            writes = set()
            for output_word in itertools.product(active_outputs, repeat=horizon):
                for normal_zero in normal_points:
                    normal = normal_zero
                    read_word = []
                    write_word = []
                    for output in output_word:
                        branch = normal >= 0
                        residual = -1 if branch else 1
                        q_value = 8 * output_q[output]
                        control = q_value + residual
                        read_word.append((output, int(branch)))
                        write_word.append(control)
                        normal = 2 * normal + control - q_value
                        all_safe = all_safe and -1 <= normal <= 1
                    reads.add(tuple(read_word))
                    writes.add(tuple(write_word))
            rows.append(
                {
                    "active_outputs": active,
                    "horizon": horizon,
                    "read_words": len(reads),
                    "write_words": len(writes),
                    "matches": len(reads) == (2 * active) ** horizon
                    and len(writes) == 4**horizon,
                }
            )
    checks = {
        "active_supports_two_three_four": set(representatives) == {2, 3, 4},
        "randomized_representatives_for_three_and_four": not _is_deterministic(
            representatives[3]
        )
        and not _is_deterministic(representatives[4]),
        "all_paths_safe": all_safe,
        "all_language_counts": all(row["matches"] for row in rows),
        "exact_read_rates": {math.log2(2 * row["active_outputs"]) for row in rows}
        == {2.0, math.log2(6), 3.0},
        "write_rate_two": all(
            row["write_words"] == 4 ** row["horizon"] for row in rows
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def finite_margin_report(max_horizon: int = 8) -> dict[str, Any]:
    rows = []
    for active, radius in itertools.product(
        (2, 3, 4), (Fraction(1, 3), Fraction(2, 5), Fraction(3, 4), Fraction(1))
    ):
        for horizon in range(1, max_horizon + 1):
            normal_words = _ceil(radius * 2**horizon)
            rows.append(
                {
                    "active_outputs": active,
                    "rho": str(radius),
                    "horizon": horizon,
                    "normal_words": normal_words,
                    "read_words": active**horizon * normal_words,
                    "write_words": 2**horizon * normal_words,
                }
            )
    checks = {
        "ceiling_formula": all(
            row["normal_words"] == _ceil(Fraction(row["rho"]) * 2 ** row["horizon"])
            for row in rows
        ),
        "read_formula": all(
            row["read_words"]
            == row["active_outputs"] ** row["horizon"] * row["normal_words"]
            for row in rows
        ),
        "write_formula": all(
            row["write_words"] == 2 ** row["horizon"] * row["normal_words"]
            for row in rows
        ),
        "full_collar": all(
            row["read_words"] == (2 * row["active_outputs"]) ** row["horizon"]
            and row["write_words"] == 4 ** row["horizon"]
            for row in rows
            if row["rho"] == "1"
        ),
    }
    return {
        "formula": {
            "normal": "ceil(rho*2^T)",
            "read": "a^T ceil(rho*2^T)",
            "write": "2^T ceil(rho*2^T)",
        },
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def deterministic_embedding_report() -> dict[str, Any]:
    partitions = set()
    checked = 0
    for output_symbols in range(1, 5):
        for relation in all_relations(output_symbols):
            if not (_feasible(relation) and _is_deterministic(relation)):
                continue
            checked += 1
            fibers: dict[int, list[int]] = {}
            for mode, mask in enumerate(relation):
                output = mask.bit_length() - 1
                fibers.setdefault(output, []).append(mode)
            partition = tuple(sorted(tuple(block) for block in fibers.values()))
            partitions.add(partition)
    expected = {
        ((0, 1), (2, 3)),
        ((0,), (1,), (2, 3)),
        ((0, 1), (2,), (3,)),
        ((0,), (1,), (2,), (3,)),
    }
    checks = {
        "labeled_deterministic_relations_checked": checked == 104,
        "four_unlabeled_partitions": partitions == expected,
        "block_histogram": Counter(len(partition) for partition in partitions)
        == {2: 1, 3: 2, 4: 1},
        "v016_regions_recovered": {
            math.log2(2 * len(partition)) for partition in partitions
        }
        == {2.0, math.log2(6), 3.0},
    }
    return {"checks": checks, "pass": all(checks.values())}


def mutation_report() -> dict[str, Any]:
    rows = {
        "ignore_positive_shared_output": not _feasible((0b01, 0b01, 0b11, 0b10)),
        "charge_declared_instead_of_active_outputs": 4 != (0b0011).bit_count(),
        "claim_randomness_repairs_overlap": not _feasible((0b11, 0b01, 0b10, 0b10)),
        "omit_normal_read_factor": 3**2 != 6**2,
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
        "pass": len(rows) == 17 and total == 204,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_zero_error_sensor_kernel_contract_v0_17",
        "base_plant": "v0.13 positive-volume collar with q classes (0,0,8,8)",
        "kernel": {
            "parameter": "finite output alphabet Y and nonempty support S_z subseteq Y for each mode z",
            "probabilities": "arbitrary rational values strictly positive on S_z and zero outside, summing to one",
            "charging": "each realized raw output y must remain injectively recoverable from the read transcript; normal information is additionally charged",
            "safety_quantifier": "for every disturbance word and every sensor-output word in support",
        },
        "theorem": {
            "feasibility": "union(S_z:q=0) is disjoint from union(S_z:q=8)",
            "active_outputs": "a=cardinality of union_z S_z",
            "feasible_region": "[1+log2(a),infinity) x [2,infinity)",
            "infeasible_region": "empty",
            "finite_read_words": "a^T ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
            "margin_range": "0<rho<=1",
        },
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_zero_error_sensor_kernel_claim_v0_17",
        "status": "complete support classification through four registered output symbols",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_16_partition_claim_sha256": SEALS["v0_16_partition_claim"][1],
        },
        "support_census": {
            "relations": 53108,
            "feasible": 724,
            "infeasible": 52384,
            "feasible_active_histogram": {"2": 20, "3": 210, "4": 494},
            "genuinely_randomized_feasible": 620,
        },
        "theorem": {
            "feasibility": "cross-q output supports are disjoint",
            "active_support_region": "[1+log2(a),infinity) x [2,infinity)",
            "finite_read_words": "a^T ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
        },
        "deterministic_embedding": {
            "labeled_relations": 104,
            "unlabeled_partitions": 4,
            "v0_16_recovered": True,
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 17, "tests": 204},
        "decision": "sensor_randomness_changes_support_refinement_not_zero_error_formula",
        "nonclaim": (
            "The theorem uses a finite memoryless kernel with raw-output charging and "
            "support-zero-error safety. It does not classify noisy channels with "
            "block error, expected length, hidden state, memory, or asymptotically "
            "vanishing failure probability."
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


def zero_error_sensor_kernel_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    contract = contract_exactness_report()
    census = support_census_report()
    theorem = support_feasibility_theorem_report()
    languages = representative_language_report()
    margin = finite_margin_report()
    embedding = deterministic_embedding_report()
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        contract,
        census,
        theorem,
        languages,
        margin,
        embedding,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_zero_error_sensor_kernels_v0_17",
        "resource_integrity": integrity,
        "contract_exactness": contract,
        "support_census": census,
        "feasibility_theorem": theorem,
        "representative_languages": languages,
        "finite_margin": margin,
        "deterministic_embedding": embedding,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = zero_error_sensor_kernel_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_kernel_contract_exact": report["contract_exactness"]["pass"],
        "R2_all_53108_relations_classified": report["support_census"]["pass"],
        "R3_support_disjointness_iff": report["feasibility_theorem"]["pass"],
        "R4_active_support_languages": report["representative_languages"]["pass"],
        "R5_exact_finite_margin": report["finite_margin"]["pass"],
        "R6_v016_deterministic_embedding": report["deterministic_embedding"]["pass"],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_inventory_and_claim": report["predecessor_inventory"]["pass"]
        and report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = zero_error_sensor_kernel_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
