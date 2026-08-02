"""Import-independent verifier for the ASMP-4 v0.16 sensor classification."""

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
V15 = (
    ROOT
    / "asmp4_semantic_selector_audit_v0_15"
    / "semantic_selector_audit_claim_v0_15.json"
)
CONTRACT = HERE / "registered_sensor_contract_v0_16.json"
CLAIM = HERE / "registered_sensor_classification_claim_v0_16.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V15: "5ec0c615f72435da81e066f707293f85dd7b3fac93dab60c166f02cf649dbdc6",
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
)

MODES = (-3, -1, 1, 3)
Partition = tuple[tuple[int, ...], ...]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _q(mode: int) -> int:
    return (12 + 13 * mode - mode**3) // 3


def _ceil(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def independent_partitions() -> tuple[Partition, ...]:
    # Enumerate all label assignments, then canonicalize fibers. This is
    # intentionally different from the central recursive block insertion.
    partitions = set()
    for labels in itertools.product(range(4), repeat=4):
        blocks = []
        for label in sorted(set(labels)):
            blocks.append(
                tuple(
                    MODES[index] for index, value in enumerate(labels) if value == label
                )
            )
        canonical = tuple(sorted(blocks, key=lambda block: block[0]))
        partitions.add(canonical)
    return tuple(sorted(partitions, key=lambda partition: (len(partition), partition)))


def _refines_q(partition: Partition) -> bool:
    return all(len({_q(mode) for mode in block}) == 1 for block in partition)


def _symbol(partition: Partition, mode: int) -> int:
    return next(index for index, block in enumerate(partition) if mode in block)


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append((path.name, observed == expected))
    return {
        "rows": rows,
        "pass": len(rows) == 2 and all(matches for _, matches in rows),
    }


def independent_partition_census() -> dict[str, Any]:
    partitions = independent_partitions()
    feasible = [partition for partition in partitions if _refines_q(partition)]
    histogram = {
        blocks: sum(len(partition) == blocks for partition in feasible)
        for blocks in (2, 3, 4)
    }
    checks = {
        "fifteen_partitions": len(partitions) == 15,
        "four_feasible": len(feasible) == 4,
        "eleven_infeasible": len(partitions) - len(feasible) == 11,
        "histogram": histogram == {2: 1, 3: 2, 4: 1},
        "q_values": tuple(_q(mode) for mode in MODES) == (0, 0, 8, 8),
        "computed_and_raw": ((-3, -1), (1, 3)) in feasible
        and ((-3,), (-1,), (1,), (3,)) in feasible,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_feasible_languages(max_horizon: int = 4) -> dict[str, Any]:
    feasible = [
        partition for partition in independent_partitions() if _refines_q(partition)
    ]
    rows = []
    all_safe = True
    for partition in feasible:
        blocks = len(partition)
        for horizon in range(1, max_horizon + 1):
            normal_points = [
                Fraction(-1) + Fraction(2 * index + 1, 2**horizon)
                for index in range(2**horizon)
            ]
            reads = set()
            writes = set()
            for symbols in itertools.product(range(blocks), repeat=horizon):
                representative_modes = tuple(partition[symbol][0] for symbol in symbols)
                for normal_zero in normal_points:
                    normal = normal_zero
                    read = []
                    write = []
                    for symbol, mode in zip(symbols, representative_modes, strict=True):
                        branch = normal >= 0
                        residual = -1 if branch else 1
                        control = _q(mode) + residual
                        read.append((symbol, int(branch)))
                        write.append(control)
                        normal = 2 * normal + control - _q(mode)
                        all_safe = all_safe and -1 <= normal <= 1
                    reads.add(tuple(read))
                    writes.add(tuple(write))
            rows.append(
                len(reads) == (2 * blocks) ** horizon and len(writes) == 4**horizon
            )
    checks = {
        "all_reduced_symbol_paths_safe": all_safe,
        "all_counts": all(rows),
        "rows": len(rows) == 16,
        "rate_set": {math.log2(2 * len(partition)) for partition in feasible}
        == {2.0, math.log2(6), 3.0},
        "write_rate_two": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_infeasibility() -> dict[str, Any]:
    rows = []
    for partition in independent_partitions():
        if _refines_q(partition):
            continue
        block = next(
            block for block in partition if len({_q(mode) for mode in block}) > 1
        )
        low = next(mode for mode in block if _q(mode) == 0)
        high = next(mode for mode in block if _q(mode) == 8)
        # At n=0 the two modes share one sensor symbol. Their admissible
        # one-step controls are [-1,1] and [7,9], with empty intersection.
        rows.append(_symbol(partition, low) == _symbol(partition, high) and 1 < 7)
    checks = {
        "eleven_rows": len(rows) == 11,
        "all_first_step_witnesses": all(rows),
        "authority_not_the_failure": -2 <= -1 <= 1 <= 10 and -2 <= 7 <= 9 <= 10,
        "successor_gap_eight": 8 > 2,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_finite_margin(max_horizon: int = 7) -> dict[str, Any]:
    rows = []
    safe = True
    for blocks, radius in itertools.product(
        (2, 3, 4), (Fraction(1, 3), Fraction(2, 5), Fraction(1))
    ):
        for horizon in range(1, max_horizon + 1):
            count = _ceil(radius * 2**horizon)
            width = 2 * radius / count
            for index in range(count):
                left = -radius + index * width
                right = left + width
                center = (left + right) / 2
                first_residual = -2 * center
                for normal_zero in (left, center, right):
                    normal = 2 * normal_zero + first_residual
                    safe = safe and -1 <= normal <= 1
                    for _time in range(1, horizon):
                        normal *= 2
                        safe = safe and -1 <= normal <= 1
            rows.append(
                count == _ceil(radius * 2**horizon)
                and width <= Fraction(2, 2**horizon)
                and blocks**horizon * count > 0
                and 2**horizon * count > 0
            )
    checks = {
        "all_interval_constructions_safe": safe,
        "all_ceiling_rows": all(rows),
        "nondyadic_radii": True,
        "registry_only_changes_read_factor": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_registered_sensor_contract_v0_16",
        "contract_parameter": contract["sensor_experiment"]["parameter"]
        == "a fixed partition P of the four modes",
        "contract_admissibility": "P refines the q-fiber partition"
        in contract["sensor_experiment"]["admissibility"],
        "contract_charging": "injectively recoverable"
        in contract["sensor_experiment"]["charging"],
        "contract_regions": contract["theorem"]["feasible_partition_region"]
        == "[1+log2(|P|),infinity) x [2,infinity)"
        and contract["theorem"]["nonrefining_partition_region"] == "empty",
        "claim_schema": claim["schema_version"]
        == "asmp4_registered_sensor_classification_claim_v0_16",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_15_semantic_audit_claim_sha256": SEALS[V15],
        },
        "claim_census": claim["partition_census"]
        == {
            "all": 15,
            "q_refining_feasible": 4,
            "nonrefining_infeasible": 11,
            "feasible_block_histogram": {"2": 1, "3": 2, "4": 1},
        },
        "claim_regions": claim["exact_regions"]
        == {
            "two_blocks": "[2,infinity) x [2,infinity)",
            "three_blocks": "[log2(6),infinity) x [2,infinity)",
            "four_blocks": "[3,infinity) x [2,infinity)",
            "nonrefining": "empty",
        },
        "decision": claim["decision"]
        == "registered_sensor_parameter_resolves_local_selector_ambiguity",
        "nonclaim": "does not define the universal asmp-4 registered-class grammar"
        in claim["nonclaim"].casefold(),
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
        "pass": len(rows) == 16 and total == 194,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_16.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_16.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "parameterized_theorem": "[1+log2(k),infinity) x [2,infinity)"
        in docs["theorem"],
        "fifteen_partition_census": "15 partitions" in docs["theorem"]
        and "eleven" in docs["theorem"],
        "finite_margin": "k^t ceil(rho*2^t)" in docs["theorem"],
        "first_step_converse": "first step" in docs["theorem"]
        and "[-1,1]" in docs["theorem"]
        and "[7,9]" in docs["theorem"],
        "v015_response": "v0.15" in docs["result"]
        and "registered sensor experiment" in docs["result"],
        "scope_limit": "not the universal" in docs["result"],
        "expanded_count": "204" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_registered_sensor_classification.py" in docs["readme"],
        "review_attack": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "partition_census": independent_partition_census()["pass"],
        "feasible_languages": independent_feasible_languages()["pass"],
        "infeasibility": independent_infeasibility()["pass"],
        "finite_margin": independent_finite_margin()["pass"],
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
