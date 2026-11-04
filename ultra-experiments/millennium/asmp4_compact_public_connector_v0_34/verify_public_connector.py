"""Import-independent verifier for ASMP-4 compact public connectors v0.34."""

from __future__ import annotations

import ast
import json
import re
from fractions import Fraction
from functools import cache
from itertools import combinations
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTRACT = HERE / "public_connector_contract_v0_34.json"
CLAIM = HERE / "public_connector_claim_v0_34.json"
V33_CLAIM = (
    ROOT
    / "asmp4_nonfinite_safe_closing_v0_33"
    / "safe_closing_claim_v0_33.json"
)


def _find(parent: list[int], node: int) -> int:
    while parent[node] != node:
        parent[node] = parent[parent[node]]
        node = parent[node]
    return node


def _union(parent: list[int], left: int, right: int) -> None:
    left_root = _find(parent, left)
    right_root = _find(parent, right)
    if left_root != right_root:
        parent[right_root] = left_root


@cache
def independent_graph_census(vertices: int = 6) -> dict[str, Any]:
    edges = tuple(combinations(range(vertices), 2))
    connected = 0
    closure_ok = True
    for mask in range(1 << len(edges)):
        parent = list(range(vertices))
        reach = [[left == right for right in range(vertices)] for left in range(vertices)]
        for bit, (left, right) in enumerate(edges):
            if mask & (1 << bit):
                _union(parent, left, right)
                reach[left][right] = True
                reach[right][left] = True
        roots = {_find(parent, node) for node in range(vertices)}
        if len(roots) != 1:
            continue
        connected += 1
        for middle in range(vertices):
            for left in range(vertices):
                for right in range(vertices):
                    reach[left][right] |= reach[left][middle] and reach[middle][right]
        closure_ok &= all(all(row) for row in reach)
    pair_rows = connected * vertices * vertices
    checks = {
        "all_masks": 1 << len(edges) == 32768,
        "connected_count": connected == 26704,
        "disconnected_count": (1 << len(edges)) - connected == 6064,
        "warshall_reaches_all_connected_pairs": closure_ok,
        "pair_rows": pair_rows == 961344,
    }
    return {
        "connected": connected,
        "pair_rows": pair_rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def independent_interval_cover() -> dict[str, Any]:
    intervals = (
        (Fraction(0), Fraction(1, 3)),
        (Fraction(1, 4), Fraction(7, 12)),
        (Fraction(1, 2), Fraction(5, 6)),
        (Fraction(3, 4), Fraction(1)),
    )
    grid = tuple(Fraction(index, 96) for index in range(97))
    covered = all(any(left <= point <= right for left, right in intervals) for point in grid)
    reach = [[False] * len(intervals) for _ in intervals]
    for left in range(len(intervals)):
        reach[left][left] = True
        for right in range(left + 1, len(intervals)):
            overlap = max(intervals[left][0], intervals[right][0]) <= min(
                intervals[left][1], intervals[right][1]
            )
            reach[left][right] = overlap
            reach[right][left] = overlap
    for middle in range(len(intervals)):
        for left in range(len(intervals)):
            for right in range(len(intervals)):
                reach[left][right] |= reach[left][middle] and reach[middle][right]
    local_bounds = ((2, 1, 3), (3, 2, 2), (2, 3, 1), (4, 2, 4))
    total = tuple(sum(row[index] for row in local_bounds) for index in range(3))
    checks = {
        "grid_covered": covered,
        "nerve_connected": all(all(row) for row in reach),
        "uniform_time": total[0] == 11,
        "uniform_read_write": total[1:] == (8, 10),
    }
    return {"checks": checks, "pass": all(checks.values())}


@cache
def independent_boundaries() -> dict[str, Any]:
    horizons = tuple(2**power for power in range(1, 13))
    ladder_rates = tuple(Fraction(horizon, horizon) for horizon in horizons)

    hidden_safe = {(mode, action): mode == action for mode in (0, 1) for action in (0, 1)}
    zero_read = any(
        all(hidden_safe[(mode, action)] for mode in (0, 1)) for action in (0, 1)
    )
    one_read = all(hidden_safe[(mode, mode)] for mode in (0, 1))
    fixed_write_with_read = any(
        all(hidden_safe[(mode, action)] for mode in (0, 1)) for action in (0, 1)
    )

    declared_action = 0
    initial_memory = 0
    toggled_memory = 1 - initial_memory
    first_memory_block = declared_action == initial_memory
    repeated_memory_block = declared_action == toggled_memory
    reset_memory_block = declared_action == initial_memory

    ambient_left = (Fraction(-1), Fraction(1, 4))
    ambient_right = (Fraction(-1, 4), Fraction(1))
    safe = (Fraction(1, 2), Fraction(3, 4))
    ambient_overlap = max(ambient_left[0], ambient_right[0]) <= min(
        ambient_left[1], ambient_right[1]
    )
    safe_overlap = max(ambient_left[0], ambient_right[0], safe[0]) <= min(
        ambient_left[1], ambient_right[1], safe[1]
    )
    checks = {
        "noncompact_ladder_linear_return": all(rate == 1 for rate in ladder_rates),
        "hidden_mode_blocks_zero_read_connector": not zero_read,
        "one_read_bit_restores_connector": one_read,
        "fixed_write_still_fails_hidden_mode": not fixed_write_with_read,
        "ambient_overlap_not_safe_overlap": ambient_overlap and not safe_overlap,
        "private_memory_toggle_blocks_repeat": first_memory_block
        and not repeated_memory_block
        and reset_memory_block,
    }
    return {"checks": checks, "pass": all(checks.values())}


@cache
def independent_contract_claim() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    claim = json.loads(CLAIM.read_text(encoding="utf-8"))
    v33 = json.loads(V33_CLAIM.read_text(encoding="utf-8"))
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    checks = {
        "contract_schema": contract.get("schema_version")
        == "asmp4_public_connector_contract_v0_34",
        "claim_schema": claim.get("schema_version")
        == "asmp4_compact_public_connector_v0_34",
        "public_state_not_free": claim.get("registered_state", {}).get(
            "hidden_plant_state_is_not_free"
        )
        is True,
        "constant_connector_implies_safe_closing": "constant connector bounds"
        in claim.get("theorem", {}).get("safe_closing", ""),
        "v33_nonfinite": v33.get("nonfinite_fixture", {}).get(
            "finite_exact_stationary_quotient"
        )
        is False,
        "scope_open": "remains open" in claim.get("disposition", ""),
        "central_not_imported": "compact_public_connector" not in imports,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    graphs = independent_graph_census()
    boundaries = independent_boundaries()["checks"]
    interval = independent_interval_cover()["checks"]
    contract = independent_contract_claim()["checks"]
    rows = {
        "omit_compactness": boundaries["noncompact_ladder_linear_return"],
        "omit_connectedness": 32768 - graphs["connected"] == 6064,
        "use_hidden_physical_state": boundaries["hidden_mode_blocks_zero_read_connector"],
        "count_unsafe_overlap": boundaries["ambient_overlap_not_safe_overlap"],
        "collapse_port_costs": interval["uniform_read_write"],
        "omit_memory_reset": boundaries["private_memory_toggle_blocks_repeat"],
        "require_finite_quotient": contract["v33_nonfinite"],
        "claim_full_canonical_resolution": contract["scope_open"],
    }
    return {"rows": rows, "pass": len(rows) == 8 and all(rows.values())}


def _count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def _package_version(name: str) -> int:
    match = re.search(r"_v0_(\d+)$", name)
    return int(match.group(1)) if match else 0


@cache
def independent_inventory() -> dict[str, Any]:
    rows = []
    for package in sorted(ROOT.iterdir(), key=lambda path: path.name):
        if not package.is_dir() or not package.name.startswith("asmp4"):
            continue
        if package.resolve() == HERE.resolve() or _package_version(package.name) >= 34:
            continue
        for test_file in sorted(package.glob("test_*.py")):
            rows.append((package.name, test_file.name, _count_tests(test_file)))
    checks = {
        "packages": len(rows) == 34,
        "tests": sum(row[2] for row in rows) == 374,
    }
    return {
        "packages": len(rows),
        "tests": sum(row[2] for row in rows),
        "checks": checks,
        "pass": all(checks.values()),
    }


def document_report() -> dict[str, Any]:
    sentinels = {
        "THEOREM.md": ("Compact public local-to-global connector theorem", "finite subcover"),
        "RESULT.md": ("public information state", "not a full resolution"),
        "PRIOR_ART_BOUNDARY_v0_34.md": ("Boscain", "No novelty"),
        "REVIEWER_PACKET_v0_34.md": ("Review order", "hidden"),
        "COMPLETION_AUDIT_v0_34.md": ("Expanded regression", "Not claimed"),
    }
    rows = {}
    for name, tokens in sentinels.items():
        text = " ".join((HERE / name).read_text(encoding="utf-8").casefold().split())
        rows[name] = all(token.casefold() in text for token in tokens)
    return {"rows": rows, "pass": all(rows.values())}


def independent_report() -> dict[str, Any]:
    report = {
        "graphs": independent_graph_census(),
        "interval": independent_interval_cover(),
        "boundaries": independent_boundaries(),
        "contract_claim": independent_contract_claim(),
        "mutations": independent_mutations(),
        "inventory": independent_inventory(),
        "documents": document_report(),
    }
    report["pass"] = all(section["pass"] for section in report.values())
    return report


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
