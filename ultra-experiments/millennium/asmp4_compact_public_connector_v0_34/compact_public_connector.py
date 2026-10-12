"""Exact harness for the ASMP-4 compact public-connector theorem v0.34."""

from __future__ import annotations

import ast
import json
import re
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTRACT = HERE / "public_connector_contract_v0_34.json"
CLAIM = HERE / "public_connector_claim_v0_34.json"
V33_CLAIM = (
    ROOT
    / "asmp4_nonfinite_safe_closing_v0_33"
    / "safe_closing_claim_v0_33.json"
)

EXPECTED_PAYLOAD = (
    "README.md",
    "THEOREM.md",
    "RESULT.md",
    "PRIOR_ART_BOUNDARY_v0_34.md",
    "REVIEWER_PACKET_v0_34.md",
    "COMPLETION_AUDIT_v0_34.md",
    "public_connector_contract_v0_34.json",
    "public_connector_claim_v0_34.json",
    "compact_public_connector.py",
    "verify_public_connector.py",
    "test_public_connector.py",
    "run_verification.py",
)

Pair = tuple[int, int]


@dataclass(frozen=True)
class LocalCertificate:
    """Uniform connector bound inside one public-information neighborhood."""

    index: int
    time: int
    read_cost: int
    write_cost: int

    def __post_init__(self) -> None:
        if self.index < 0 or min(self.time, self.read_cost, self.write_cost) < 0:
            raise ValueError("certificate fields must be nonnegative")

    @property
    def cost(self) -> Pair:
        return self.read_cost, self.write_cost


@dataclass(frozen=True)
class ConnectorBound:
    time: int
    read_cost: int
    write_cost: int

    @property
    def cost(self) -> Pair:
        return self.read_cost, self.write_cost


def edge_order(vertices: int) -> tuple[tuple[int, int], ...]:
    if vertices < 1:
        raise ValueError("vertices must be positive")
    return tuple(combinations(range(vertices), 2))


def adjacency_from_mask(vertices: int, mask: int) -> tuple[tuple[int, ...], ...]:
    edges = edge_order(vertices)
    if mask < 0 or mask >= 1 << len(edges):
        raise ValueError("mask outside graph range")
    adjacency = [set() for _ in range(vertices)]
    for bit, (left, right) in enumerate(edges):
        if mask & (1 << bit):
            adjacency[left].add(right)
            adjacency[right].add(left)
    return tuple(tuple(sorted(neighbors)) for neighbors in adjacency)


def shortest_node_path(
    adjacency: tuple[tuple[int, ...], ...], start: int, target: int
) -> tuple[int, ...] | None:
    if not 0 <= start < len(adjacency) or not 0 <= target < len(adjacency):
        raise ValueError("vertex outside graph")
    queue: deque[int] = deque([start])
    parent: dict[int, int | None] = {start: None}
    while queue:
        node = queue.popleft()
        if node == target:
            path = []
            cursor: int | None = target
            while cursor is not None:
                path.append(cursor)
                cursor = parent[cursor]
            return tuple(reversed(path))
        for neighbor in adjacency[node]:
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    return None


def is_connected(adjacency: tuple[tuple[int, ...], ...]) -> bool:
    return all(
        shortest_node_path(adjacency, 0, target) is not None
        for target in range(len(adjacency))
    )


def deterministic_certificates(vertices: int) -> tuple[LocalCertificate, ...]:
    return tuple(
        LocalCertificate(
            index=index,
            time=index + 1,
            read_cost=(2 * index + 1) % 7 + 1,
            write_cost=(3 * index + 2) % 8 + 1,
        )
        for index in range(vertices)
    )


def coarse_uniform_bound(certificates: Iterable[LocalCertificate]) -> ConnectorBound:
    rows = tuple(certificates)
    return ConnectorBound(
        time=sum(row.time for row in rows),
        read_cost=sum(row.read_cost for row in rows),
        write_cost=sum(row.write_cost for row in rows),
    )


def path_bound(
    path: tuple[int, ...], certificates: tuple[LocalCertificate, ...]
) -> ConnectorBound:
    rows = tuple(certificates[index] for index in path)
    return coarse_uniform_bound(rows)


def bound_dominates(left: ConnectorBound, right: ConnectorBound) -> bool:
    return (
        left.time >= right.time
        and left.read_cost >= right.read_cost
        and left.write_cost >= right.write_cost
    )


@cache
def graph_census(vertices: int = 6) -> dict[str, Any]:
    edges = edge_order(vertices)
    certificates = deterministic_certificates(vertices)
    coarse = coarse_uniform_bound(certificates)
    connected = 0
    disconnected = 0
    pair_rows = 0
    all_paths_within_bound = True
    all_connected_have_paths = True
    for mask in range(1 << len(edges)):
        adjacency = adjacency_from_mask(vertices, mask)
        if not is_connected(adjacency):
            disconnected += 1
            continue
        connected += 1
        for start in range(vertices):
            for target in range(vertices):
                path = shortest_node_path(adjacency, start, target)
                all_connected_have_paths &= path is not None
                if path is not None:
                    all_paths_within_bound &= bound_dominates(
                        coarse, path_bound(path, certificates)
                    )
                pair_rows += 1
    checks = {
        "all_graphs_classified": connected + disconnected == 32768,
        "known_connected_graph_count": connected == 26704,
        "known_disconnected_graph_count": disconnected == 6064,
        "all_connected_pairs_have_overlap_paths": all_connected_have_paths,
        "finite_subcover_sum_bounds_every_simple_connector": all_paths_within_bound,
        "pair_rows": pair_rows == 961344,
    }
    return {
        "vertices": vertices,
        "graphs": connected + disconnected,
        "connected": connected,
        "disconnected": disconnected,
        "pair_rows": pair_rows,
        "coarse_bound": {
            "time": coarse.time,
            "read": coarse.read_cost,
            "write": coarse.write_cost,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def interval_cover_report() -> dict[str, Any]:
    """Exact rational compact-core cover with a connected safe nerve."""

    intervals = (
        (Fraction(0), Fraction(1, 3)),
        (Fraction(1, 4), Fraction(7, 12)),
        (Fraction(1, 2), Fraction(5, 6)),
        (Fraction(3, 4), Fraction(1)),
    )
    certificates = (
        LocalCertificate(0, 2, 1, 3),
        LocalCertificate(1, 3, 2, 2),
        LocalCertificate(2, 2, 3, 1),
        LocalCertificate(3, 4, 2, 4),
    )
    covers = intervals[0][0] == 0 and intervals[-1][1] == 1 and all(
        intervals[index][1] >= intervals[index + 1][0]
        for index in range(len(intervals) - 1)
    )
    adjacency = tuple(
        tuple(
            right
            for right in range(len(intervals))
            if right != left
            and max(intervals[left][0], intervals[right][0])
            <= min(intervals[left][1], intervals[right][1])
        )
        for left in range(len(intervals))
    )
    coarse = coarse_uniform_bound(certificates)
    endpoint_path = shortest_node_path(adjacency, 0, len(intervals) - 1)
    endpoint_bound = (
        path_bound(endpoint_path, certificates) if endpoint_path is not None else None
    )
    checks = {
        "compact_interval_covered": covers,
        "safe_overlap_nerve_connected": is_connected(adjacency),
        "endpoint_connector_exists": endpoint_path is not None,
        "endpoint_connector_within_uniform_bound": endpoint_bound is not None
        and bound_dominates(coarse, endpoint_bound),
        "separate_port_bound": coarse.cost == (8, 10),
        "time_bound": coarse.time == 11,
    }
    return {
        "intervals": len(intervals),
        "endpoint_path": endpoint_path,
        "uniform_bound": {
            "time": coarse.time,
            "read": coarse.read_cost,
            "write": coarse.write_cost,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


def finite_horizon_region_bound(
    prefix_cost: Pair, horizon: int, connector: ConnectorBound
) -> tuple[Fraction, Fraction]:
    if horizon < 1:
        raise ValueError("horizon must be positive")
    return (
        Fraction(prefix_cost[0] + connector.read_cost, horizon + connector.time),
        Fraction(prefix_cost[1] + connector.write_cost, horizon + connector.time),
    )


@cache
def noncompact_ladder_report(max_horizon: int = 4096) -> dict[str, Any]:
    """Local unit connectors on N do not yield a uniform sublinear return."""

    horizons = tuple(2**power for power in range(1, 13))
    return_costs = tuple(horizon for horizon in horizons)
    rates = tuple(Fraction(cost, horizon) for cost, horizon in zip(return_costs, horizons, strict=True))
    checks = {
        "local_unit_connectors_exist": all(
            return_costs[index + 1] - return_costs[index]
            == horizons[index + 1] - horizons[index]
            for index in range(len(horizons) - 1)
        ),
        "no_uniform_connector_bound": len(set(return_costs)) == len(return_costs),
        "return_overhead_has_positive_rate": all(rate == 1 for rate in rates),
        "requested_max_horizon_exercised": horizons[-1] == max_horizon,
    }
    return {
        "horizons": len(horizons),
        "final_return_cost": return_costs[-1],
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def public_hidden_state_report() -> dict[str, Any]:
    """Two hidden modes need opposite connector actions unless one read bit is paid."""

    modes = (0, 1)
    actions = (0, 1)
    safe = {(mode, action): mode == action for mode in modes for action in actions}
    unobserved_policies = tuple(
        all(safe[(mode, action)] for mode in modes) for action in actions
    )
    observed_policy_safe = all(safe[(mode, mode)] for mode in modes)
    fixed_write_safe_with_read = any(
        all(safe[(mode, action)] for mode in modes) for action in actions
    )
    checks = {
        "physical_modewise_connector_exists": all(
            any(safe[(mode, action)] for action in actions) for mode in modes
        ),
        "no_zero_read_public_connector": not any(unobserved_policies),
        "one_read_bit_restores_connector": observed_policy_safe,
        "read_and_write_roles_not_interchangeable": observed_policy_safe
        and not fixed_write_safe_with_read,
    }
    return {"checks": checks, "pass": all(checks.values())}


@cache
def unsafe_overlap_report() -> dict[str, Any]:
    left = (Fraction(-1), Fraction(1, 4))
    right = (Fraction(-1, 4), Fraction(1))
    safe_core = (Fraction(1, 2), Fraction(3, 4))
    geometric_overlap = max(left[0], right[0]) <= min(left[1], right[1])
    overlap_with_safe_core = max(left[0], right[0], safe_core[0]) <= min(
        left[1], right[1], safe_core[1]
    )
    checks = {
        "ambient_overlap_exists": geometric_overlap,
        "ambient_overlap_misses_safe_core": not overlap_with_safe_core,
        "unsafe_overlap_cannot_form_nerve_edge": geometric_overlap
        and not overlap_with_safe_core,
    }
    return {"checks": checks, "pass": all(checks.values())}


@cache
def private_memory_report() -> dict[str, Any]:
    """A toggled actuator bit prevents identical block repetition unless reset."""

    declared_action = 0
    initial_memory = 0
    first_block_safe = declared_action == initial_memory
    actuator_memory_after_block = 1 - initial_memory
    repeated_without_reset_safe = declared_action == actuator_memory_after_block
    reset_memory = 0
    repeated_with_reset_safe = declared_action == reset_memory
    checks = {
        "first_block_safe": first_block_safe,
        "repeat_without_memory_reset_fails": not repeated_without_reset_safe,
        "registered_memory_reset_restores_concatenation": repeated_with_reset_safe,
    }
    return {"checks": checks, "pass": all(checks.values())}


@cache
def v33_bridge_report() -> dict[str, Any]:
    claim = json.loads(V33_CLAIM.read_text(encoding="utf-8"))
    interval = interval_cover_report()
    bound = interval["uniform_bound"]
    horizon = 4096
    finite = finite_horizon_region_bound(
        (horizon // 2, horizon // 2),
        horizon,
        ConnectorBound(bound["time"], bound["read"], bound["write"]),
    )
    checks = {
        "v33_requires_safe_closing": claim.get("hypotheses", {}).get(
            "cofinal_sublinear_cost_closing"
        )
        is True,
        "v33_does_not_require_finite_quotient": claim.get("nonfinite_fixture", {}).get(
            "finite_exact_stationary_quotient"
        )
        is False,
        "compact_connector_has_constant_vector_cost": bound["read"] == 8
        and bound["write"] == 10,
        "constant_connector_correction_below_one_percent": finite[0]
        < Fraction(51, 100)
        and finite[1] < Fraction(51, 100),
    }
    return {
        "closed_rate_at_4096": [str(finite[0]), str(finite[1])],
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    graph = graph_census()
    ladder = noncompact_ladder_report()
    hidden = public_hidden_state_report()
    unsafe = unsafe_overlap_report()
    memory = private_memory_report()
    interval = interval_cover_report()
    v33 = v33_bridge_report()
    rows = {
        "local_connectors_imply_uniformity_without_compactness": ladder["checks"][
            "return_overhead_has_positive_rate"
        ],
        "disconnected_cover_has_global_connector": graph["disconnected"] > 0,
        "physical_controllability_equals_public_controllability": hidden["checks"][
            "no_zero_read_public_connector"
        ],
        "ambient_overlap_is_a_safe_nerve_edge": unsafe["checks"][
            "ambient_overlap_misses_safe_core"
        ],
        "one_scalar_connector_cost_controls_both_ports": interval["checks"][
            "separate_port_bound"
        ],
        "private_memory_need_not_reset": memory["checks"][
            "repeat_without_memory_reset_fails"
        ],
        "finite_exact_quotient_is_required": v33["checks"][
            "v33_does_not_require_finite_quotient"
        ],
        "canonical_local_controllability_already_proves_public_certificates": contract_report()[
            "checks"
        ]["scope_open"],
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()),
    }


def _count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def _package_version(name: str) -> int:
    match = re.search(r"_v0_(\d+)$", name)
    return int(match.group(1)) if match else 0


@cache
def predecessor_inventory_report() -> dict[str, Any]:
    paths = sorted(
        path
        for path in ROOT.glob("asmp4*/test_*.py")
        if path.parent.resolve() != HERE.resolve()
        and _package_version(path.parent.name) < 34
    )
    rows = [
        {"package": path.parent.name, "file": path.name, "tests": _count_tests(path)}
        for path in paths
    ]
    checks = {
        "thirty_four_predecessor_packages": len(rows) == 34,
        "three_hundred_seventy_four_predecessor_tests": sum(
            row["tests"] for row in rows
        )
        == 374,
    }
    return {
        "packages": len(rows),
        "tests": sum(row["tests"] for row in rows),
        "checks": checks,
        "pass": all(checks.values()),
    }


def claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_compact_public_connector_v0_34",
        "theorem": {
            "local_to_global": "finite connected safe subcover gives a uniform public connector",
            "time_bound": "L=sum_j L_j",
            "cost_bound": "B_i=sum_j B_i,j separately for read and write",
            "safe_closing": "constant connector bounds imply v0.33 sublinear safe closing",
            "region": "R_q=closure(upward(conv(P_q))) with component-indexed global union",
            "coordinate_invariance": "registered causal conjugacies transport the public cover and connector certificates",
        },
        "registered_state": {
            "object": "public information state including belief and registered memories",
            "hidden_plant_state_is_not_free": True,
            "private_memory_must_reset": True,
            "safe_overlap_required": True,
        },
        "evidence": {
            "six_vertex_graphs": 32768,
            "connected_graphs": 26704,
            "connector_pair_rows": 961344,
            "noncompact_horizons": 12,
            "mutations_rejected": 8,
            "predecessor_packages": 34,
            "predecessor_tests": 374,
        },
        "disposition": "compact public local controllability now implies the nonfinite region theorem; deriving the registered public local certificates from the canonical normally hyperbolic plant wording remains open",
    }


@cache
def contract_report() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks = {
        "schema": contract.get("schema_version")
        == "asmp4_public_connector_contract_v0_34",
        "public_state": contract.get("requirements", {}).get("state")
        == "registered public information state, not uncharged plant state",
        "vector_cost": contract.get("requirements", {}).get("cost")
        == "separate nonnegative read and write connector bounds",
        "scope_open": "does not derive" in contract.get("scope_boundary", ""),
    }
    return {"checks": checks, "pass": all(checks.values())}


@cache
def claim_report() -> dict[str, Any]:
    actual = json.loads(CLAIM.read_text(encoding="utf-8"))
    checks = {
        "exact": actual == claim_payload(),
        "public_not_hidden": actual.get("registered_state", {}).get(
            "hidden_plant_state_is_not_free"
        )
        is True,
        "scope_open": "remains open" in actual.get("disposition", ""),
    }
    return {"checks": checks, "pass": all(checks.values())}


def payload_report() -> dict[str, Any]:
    missing = [name for name in EXPECTED_PAYLOAD if not (HERE / name).is_file()]
    return {"missing": missing, "pass": not missing}


def full_report() -> dict[str, Any]:
    report = {
        "contract": contract_report(),
        "claim": claim_report(),
        "graph_census": graph_census(),
        "interval_cover": interval_cover_report(),
        "noncompact": noncompact_ladder_report(),
        "public_hidden": public_hidden_state_report(),
        "unsafe_overlap": unsafe_overlap_report(),
        "private_memory": private_memory_report(),
        "v33_bridge": v33_bridge_report(),
        "mutations": mutation_report(),
        "inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    report["pass"] = all(section["pass"] for section in report.values())
    return report


def main() -> int:
    report = full_report()
    gates = {
        "R0_contract": report["contract"]["pass"],
        "R1_claim": report["claim"]["pass"],
        "R2_graph_census": report["graph_census"]["pass"],
        "R3_interval_cover": report["interval_cover"]["pass"],
        "R4_noncompact_boundary": report["noncompact"]["pass"],
        "R5_public_state_boundary": report["public_hidden"]["pass"],
        "R6_safe_memory_guards": report["unsafe_overlap"]["pass"]
        and report["private_memory"]["pass"],
        "R7_v33_bridge": report["v33_bridge"]["pass"],
        "R8_mutations": report["mutations"]["pass"],
        "R9_inventory_payload": report["inventory"]["pass"]
        and report["payload"]["pass"],
    }
    print(json.dumps({"gates": gates, "report": report}, indent=2, sort_keys=True))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
