from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from discounted_shaping import (
    balanced_component_count,
    boundary_signature,
    predicted_rank,
    quotient_dimension,
    rational_rank,
    shaping_pairing,
    twisted_incidence,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def validate_registration(
    path: Path, registration: dict[str, Any]
) -> tuple[str, dict[str, bool]]:
    relative = path.resolve().relative_to(REPO).as_posix()
    registration_commit = git("log", "-1", "--format=%H", "--", relative)
    checks = {
        "head_is_registration_commit": (
            git("rev-parse", "HEAD") == registration_commit
        ),
        "tracked_tree_clean": not git(
            "status", "--porcelain", "--untracked-files=no"
        ),
        "implementation_is_ancestor": subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                registration["implementation_commit"],
                registration_commit,
            ],
            cwd=REPO,
            check=False,
        ).returncode
        == 0,
    }
    for relative_path, expected in registration["sealed_files"].items():
        checks[f"hash:{relative_path}"] = (
            sha256(REPO / relative_path) == expected
        )
    if not all(checks.values()):
        raise RuntimeError(
            "registration validation failed: "
            + repr([name for name, passed in checks.items() if not passed])
        )
    return registration_commit, checks


def random_simple_edges(
    vertex_count: int, rng: random.Random
) -> tuple[tuple[int, int], ...]:
    edges = []
    for left in range(vertex_count):
        for right in range(left + 1, vertex_count):
            state = rng.randrange(3)
            if state == 1:
                edges.append((left, right))
            elif state == 2:
                edges.append((right, left))
    return tuple(edges)


def random_multigraph_edges(
    vertex_count: int, rng: random.Random
) -> tuple[tuple[int, int], ...]:
    edge_count = rng.randint(0, 3 * vertex_count)
    return tuple(
        (rng.randrange(vertex_count), rng.randrange(vertex_count))
        for _ in range(edge_count)
    )


def rank_record(
    vertex_count: int,
    edges: tuple[tuple[int, int], ...],
    gamma: Fraction,
) -> tuple[int, int]:
    actual = rational_rank(twisted_incidence(vertex_count, edges, gamma))
    expected = predicted_rank(vertex_count, edges, gamma)
    return actual, expected


def run_rank_cells(
    spec: dict[str, Any], *, multigraph: bool
) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    vertex_count = int(spec["vertex_count"])
    gammas = [Fraction(*pair) for pair in spec["gammas"]]
    mismatches = 0
    endpoint_mismatches = 0
    balanced_histogram: dict[int, int] = {}
    quotient_histogram: dict[int, int] = {}
    for _ in range(int(spec["count"])):
        edges = (
            random_multigraph_edges(vertex_count, rng)
            if multigraph
            else random_simple_edges(vertex_count, rng)
        )
        balanced = balanced_component_count(vertex_count, edges)
        balanced_histogram[balanced] = (
            balanced_histogram.get(balanced, 0) + 1
        )
        quotient = quotient_dimension(vertex_count, edges, gammas[0])
        quotient_histogram[quotient] = (
            quotient_histogram.get(quotient, 0) + 1
        )
        for gamma in gammas:
            actual, expected = rank_record(vertex_count, edges, gamma)
            mismatches += int(actual != expected)
        for gamma in (Fraction(0), Fraction(1)):
            actual, expected = rank_record(vertex_count, edges, gamma)
            endpoint_mismatches += int(actual != expected)
    return {
        **spec,
        "multigraph": multigraph,
        "rank_mismatch_count": mismatches,
        "endpoint_mismatch_count": endpoint_mismatches,
        "balanced_component_histogram": balanced_histogram,
        "quotient_dimension_histogram": quotient_histogram,
    }


def random_trajectory(
    vertex_count: int, maximum_length: int, rng: random.Random
) -> tuple[int, ...]:
    length = rng.randint(0, maximum_length)
    return tuple(
        rng.randrange(vertex_count) for _ in range(length + 1)
    )


def run_trajectory_cells(spec: dict[str, Any]) -> dict[str, Any]:
    gammas = [Fraction(*pair) for pair in spec["gammas"]]
    random_rng = random.Random(int(spec["random_seed"]))
    telescope_mismatches = 0
    for _ in range(int(spec["random_count"])):
        vertex_count = random_rng.randint(2, 12)
        trajectory = random_trajectory(vertex_count, 32, random_rng)
        potential = [
            Fraction(random_rng.randint(-20, 20), random_rng.randint(1, 9))
            for _ in range(vertex_count)
        ]
        gamma = gammas[random_rng.randrange(len(gammas))]
        boundary = boundary_signature(trajectory, vertex_count, gamma)
        expected = sum(
            coefficient * value
            for coefficient, value in zip(boundary, potential)
        )
        actual = shaping_pairing(trajectory, potential, gamma)
        telescope_mismatches += int(actual != expected)

    matched_rng = random.Random(int(spec["matched_seed"]))
    matched_mismatches = 0
    for _ in range(int(spec["matched_count"])):
        vertex_count = matched_rng.randint(3, 12)
        length = matched_rng.randint(2, 16)
        start = matched_rng.randrange(vertex_count)
        end = matched_rng.randrange(vertex_count)
        left = (start,) + tuple(
            matched_rng.randrange(vertex_count) for _ in range(length - 1)
        ) + (end,)
        right = (start,) + tuple(
            matched_rng.randrange(vertex_count) for _ in range(length - 1)
        ) + (end,)
        potential = [
            Fraction(matched_rng.randint(-20, 20), matched_rng.randint(1, 9))
            for _ in range(vertex_count)
        ]
        gamma = gammas[matched_rng.randrange(len(gammas))]
        matched_mismatches += int(
            boundary_signature(left, vertex_count, gamma)
            != boundary_signature(right, vertex_count, gamma)
            or shaping_pairing(left, potential, gamma)
            != shaping_pairing(right, potential, gamma)
        )

    mismatch_rng = random.Random(int(spec["mismatched_seed"]))
    missing_witnesses = 0
    for _ in range(int(spec["mismatched_count"])):
        vertex_count = mismatch_rng.randint(3, 12)
        short_length = mismatch_rng.randint(1, 8)
        long_length = short_length + mismatch_rng.randint(1, 8)
        start = mismatch_rng.randrange(vertex_count)
        end = mismatch_rng.randrange(vertex_count)
        short = (start,) + tuple(
            mismatch_rng.randrange(vertex_count)
            for _ in range(short_length - 1)
        ) + (end,)
        long = (start,) + tuple(
            mismatch_rng.randrange(vertex_count)
            for _ in range(long_length - 1)
        ) + (end,)
        gamma = gammas[mismatch_rng.randrange(len(gammas))]
        potential = [Fraction(0) for _ in range(vertex_count)]
        potential[end] = 1
        missing_witnesses += int(
            boundary_signature(short, vertex_count, gamma)
            == boundary_signature(long, vertex_count, gamma)
            or shaping_pairing(short, potential, gamma)
            == shaping_pairing(long, potential, gamma)
        )
    return {
        **spec,
        "telescoping_mismatch_count": telescope_mismatches,
        "matched_boundary_mismatch_count": matched_mismatches,
        "unequal_horizon_missing_witness_count": missing_witnesses,
    }


def cycle_edges(length: int) -> tuple[tuple[int, int], ...]:
    return tuple((index, (index + 1) % length) for index in range(length))


def route_graph(
    left_length: int, right_length: int
) -> tuple[int, tuple[tuple[int, int], ...]]:
    # Two internally disjoint routes from root to terminal.
    next_vertex = 1
    routes: list[list[int]] = []
    for length in (left_length, right_length):
        internal = list(range(next_vertex, next_vertex + length - 1))
        next_vertex += length - 1
        routes.append([0, *internal])
    terminal = next_vertex
    edges: list[tuple[int, int]] = []
    for route in routes:
        route.append(terminal)
        edges.extend(zip(route, route[1:]))
    return terminal + 1, tuple(edges)


def run_planted(spec: dict[str, Any]) -> dict[str, int]:
    gamma = Fraction(2, 3)
    cycle_failures = 0
    for length in range(
        int(spec["cycle_lengths"][0]),
        int(spec["cycle_lengths"][1]) + 1,
    ):
        edges = cycle_edges(length)
        cycle_failures += int(
            quotient_dimension(length, edges, gamma) != 0
            or quotient_dimension(length, edges, Fraction(1)) != 1
        )
    diamond_failures = 0
    shortcut_failures = 0
    for path_length in range(
        int(spec["diamond_path_lengths"][0]),
        int(spec["diamond_path_lengths"][1]) + 1,
    ):
        vertex_count, diamond = route_graph(path_length, path_length)
        vertex_count_short, shortcut = route_graph(
            path_length, path_length - 1
        )
        diamond_dimension = quotient_dimension(
            vertex_count, diamond, gamma
        )
        shortcut_dimension = quotient_dimension(
            vertex_count_short, shortcut, gamma
        )
        diamond_failures += int(diamond_dimension != 1)
        shortcut_failures += int(shortcut_dimension != 0)
    return {
        "cycle_failure_count": cycle_failures,
        "diamond_failure_count": diamond_failures,
        "shortcut_failure_count": shortcut_failures,
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# ASMP-9 discounted-shaping verification v0.6",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "## Gates",
        "",
    ]
    for name, passed in result["gates"].items():
        lines.append(f"- **{name}:** {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Rank checks",
            "",
            "| family | graphs | vertices | rational-rank mismatches | endpoint mismatches |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for family in ("simple_rank", "multigraph_rank"):
        row = result[family]
        lines.append(
            f"| {family} | {row['count']} | {row['vertex_count']} | "
            f"{row['rank_mismatch_count']} | {row['endpoint_mismatch_count']} |"
        )
    trajectory = result["trajectory"]
    lines.extend(
        [
            "",
            "## Trajectory checks",
            "",
            f"- exact telescoping mismatches: `{trajectory['telescoping_mismatch_count']}`",
            f"- matched-boundary mismatches: `{trajectory['matched_boundary_mismatch_count']}`",
            f"- unequal-horizon missing witnesses: `{trajectory['unequal_horizon_missing_witness_count']}`",
            "",
            "## Interpretation",
            "",
            "Discounting replaces the ordinary cycle quotient with a",
            "gain-graph quotient. Unbalanced components lose one invariant",
            "dimension, and finite trajectory comparisons require matching",
            "discounted boundary signatures.",
            "",
            "## Claim boundary",
            "",
            "Classical gain-graph and potential-shaping specialization; not",
            "policy-based IRL, all reward invariances, a human model, or a",
            "complete ASMP-9 resolution.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    started = time.perf_counter()
    registration_commit, binding = validate_registration(
        registration_path, registration
    )
    simple = run_rank_cells(protocol["simple_rank"], multigraph=False)
    multi = run_rank_cells(protocol["multigraph_rank"], multigraph=True)
    trajectory = run_trajectory_cells(protocol["trajectory"])
    planted = run_planted(protocol["planted"])
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_simple_rank": simple["rank_mismatch_count"] == 0,
        "G2_multigraph_rank": multi["rank_mismatch_count"] == 0,
        "G3_endpoint_ranks": (
            simple["endpoint_mismatch_count"] == 0
            and multi["endpoint_mismatch_count"] == 0
        ),
        "G4_trajectory_telescoping": (
            trajectory["telescoping_mismatch_count"] == 0
        ),
        "G5_matched_boundary": (
            trajectory["matched_boundary_mismatch_count"] == 0
        ),
        "G6_unequal_horizon_witness": (
            trajectory["unequal_horizon_missing_witness_count"] == 0
        ),
        "G7_planted_access_controls": all(
            value == 0 for value in planted.values()
        ),
    }
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "discounted_shaping_gain_quotient_not_verified"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "elapsed_seconds": time.perf_counter() - started,
        "binding_checks": binding,
        "simple_rank": simple,
        "multigraph_rank": multi,
        "trajectory": trajectory,
        "planted": planted,
        "gates": gates,
        "verdict": verdict,
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_6.json"
    report_path = args.output_dir / "RESULT_v0_6.md"
    write_json(result_path, result)
    write_text(report_path, render_report(result))
    receipt = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "implementation_commit": registration["implementation_commit"],
        "elapsed_seconds": result["elapsed_seconds"],
        "output_hashes": {
            result_path.name: sha256(result_path),
            report_path.name: sha256(report_path),
        },
    }
    write_json(args.output_dir / "receipt_v0_6.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
