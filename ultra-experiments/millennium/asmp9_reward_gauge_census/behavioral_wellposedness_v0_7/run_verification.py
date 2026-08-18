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

from behavioral_access import (
    adaptive_interval,
    bridge_indices,
    coherence_only_query_indices,
    fundamental_residuals,
    gradient_scores,
    is_coherent,
    least_squares_projection,
    nonadaptive_cells,
    optimal_nonadaptive_thresholds,
    reconstruct_from_forest,
    residual_is_orthogonal,
    spanning_forest_indices,
    weak_components,
    worst_cell_width,
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
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def validate_registration(
    path: Path, registration: dict[str, Any]
) -> tuple[str, dict[str, bool]]:
    relative = path.resolve().relative_to(REPO).as_posix()
    registration_commit = git("log", "-1", "--format=%H", "--", relative)
    checks = {
        "head_is_registration_commit": git("rev-parse", "HEAD")
        == registration_commit,
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
        checks[f"hash:{relative_path}"] = sha256(REPO / relative_path) == expected
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"registration validation failed: {failed!r}")
    return registration_commit, checks


def random_simple_edges(
    vertex_count: int, rng: random.Random
) -> tuple[tuple[int, int], ...]:
    edges: list[tuple[int, int]] = []
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
    return tuple(
        (rng.randrange(vertex_count), rng.randrange(vertex_count))
        for _ in range(rng.randint(0, 3 * vertex_count))
    )


def random_utility(
    vertex_count: int, rng: random.Random
) -> tuple[Fraction, ...]:
    return tuple(
        Fraction(rng.randint(-20, 20), rng.randint(1, 9))
        for _ in range(vertex_count)
    )


def run_graph_cells(
    spec: dict[str, Any], *, multigraph: bool
) -> dict[str, Any]:
    graph_rng = random.Random(int(spec["seed"]))
    score_rng = random.Random(int(spec["score_seed"]) + int(multigraph))
    vertex_count = int(spec["vertex_count"])
    ledger_mismatches = 0
    reconstruction_mismatches = 0
    nonbridge_corruption_mismatches = 0
    bridge_change_mismatches = 0
    nonbridge_corruption_count = 0
    bridge_change_count = 0
    triplet_histogram: dict[str, int] = {}
    for _ in range(int(spec["count"])):
        edges = (
            random_multigraph_edges(vertex_count, graph_rng)
            if multigraph
            else random_simple_edges(vertex_count, graph_rng)
        )
        component_count = len(weak_components(vertex_count, edges))
        forest = spanning_forest_indices(vertex_count, edges)
        bridges = bridge_indices(vertex_count, edges)
        nonbridges = coherence_only_query_indices(vertex_count, edges)
        beta = len(edges) - vertex_count + component_count
        ledger_mismatches += int(
            len(forest) != vertex_count - component_count
            or len(edges) - len(forest) != beta
            or len(bridges) + len(nonbridges) != len(edges)
        )
        key = f"{len(forest)},{len(nonbridges)},{beta}"
        triplet_histogram[key] = triplet_histogram.get(key, 0) + 1

        utility = random_utility(vertex_count, score_rng)
        scores = gradient_scores(utility, edges)
        recovered = reconstruct_from_forest(vertex_count, edges, scores, forest)
        reconstruction_mismatches += int(
            gradient_scores(recovered, edges) != scores
            or not is_coherent(vertex_count, edges, scores)
        )
        if nonbridges:
            nonbridge_corruption_count += 1
            index = nonbridges[score_rng.randrange(len(nonbridges))]
            corrupted = list(scores)
            corrupted[index] += Fraction(
                score_rng.choice((-1, 1)) * score_rng.randint(1, 9),
                score_rng.randint(1, 9),
            )
            nonbridge_corruption_mismatches += int(
                is_coherent(vertex_count, edges, tuple(corrupted))
            )
        if bridges:
            bridge_change_count += 1
            index = bridges[score_rng.randrange(len(bridges))]
            changed = list(scores)
            changed[index] += Fraction(
                score_rng.choice((-1, 1)) * score_rng.randint(1, 9),
                score_rng.randint(1, 9),
            )
            bridge_change_mismatches += int(
                not is_coherent(vertex_count, edges, tuple(changed))
            )
    return {
        **spec,
        "multigraph": multigraph,
        "ledger_mismatch_count": ledger_mismatches,
        "reconstruction_mismatch_count": reconstruction_mismatches,
        "nonbridge_corruption_count": nonbridge_corruption_count,
        "nonbridge_corruption_mismatch_count": nonbridge_corruption_mismatches,
        "bridge_change_count": bridge_change_count,
        "bridge_change_mismatch_count": bridge_change_mismatches,
        "access_triplet_histogram": triplet_histogram,
    }


def run_hodge_cells(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    vertex_count = int(spec["vertex_count"])
    orthogonality_mismatches = 0
    zero_equivalence_mismatches = 0
    nonzero_residual_count = 0
    for _ in range(int(spec["count"])):
        edges = random_multigraph_edges(vertex_count, rng)
        scores = tuple(
            Fraction(rng.randint(-12, 12), rng.randint(1, 7))
            for _ in edges
        )
        _, residual = least_squares_projection(vertex_count, edges, scores)
        orthogonality_mismatches += int(
            not residual_is_orthogonal(vertex_count, edges, residual)
        )
        residual_zero = all(value == 0 for value in residual)
        coherent = is_coherent(vertex_count, edges, scores)
        zero_equivalence_mismatches += int(residual_zero != coherent)
        nonzero_residual_count += int(not residual_zero)
    return {
        **spec,
        "orthogonality_mismatch_count": orthogonality_mismatches,
        "zero_equivalence_mismatch_count": zero_equivalence_mismatches,
        "nonzero_residual_count": nonzero_residual_count,
    }


def run_cycle_cells(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    bound_mismatches = 0
    coherence_mismatches = 0
    nonzero_circulation_count = 0
    for _ in range(int(spec["count"])):
        length = rng.randint(
            int(spec["minimum_length"]), int(spec["maximum_length"])
        )
        edges = tuple((index, (index + 1) % length) for index in range(length))
        scores = tuple(
            Fraction(rng.randint(-10, 10), rng.randint(1, 7))
            for _ in edges
        )
        circulation = sum(scores, Fraction(0))
        _, residual = least_squares_projection(length, edges, scores)
        squared = sum((value * value for value in residual), Fraction(0))
        maximum = max((abs(value) for value in residual), default=Fraction(0))
        bound_mismatches += int(
            squared < circulation * circulation / length
            or maximum < abs(circulation) / length
        )
        coherent = is_coherent(length, edges, scores)
        coherence_mismatches += int(coherent != (circulation == 0))
        nonzero_circulation_count += int(circulation != 0)
    return {
        **spec,
        "bound_mismatch_count": bound_mismatches,
        "coherence_mismatch_count": coherence_mismatches,
        "nonzero_circulation_count": nonzero_circulation_count,
    }


def run_policy_cells(spec: dict[str, Any]) -> dict[str, Any]:
    adaptive_mismatches = 0
    minimum_adaptive_width: Fraction | None = None
    theta = Fraction(1, 3)
    for query_count in range(int(spec["adaptive_max_k"]) + 1):
        lower, upper = adaptive_interval(theta, query_count)
        width = upper - lower
        adaptive_mismatches += int(width != Fraction(1, 2**query_count))
        minimum_adaptive_width = (
            width
            if minimum_adaptive_width is None
            else min(minimum_adaptive_width, width)
        )

    nonadaptive_mismatches = 0
    minimum_nonadaptive_width: Fraction | None = None
    for query_count in range(int(spec["nonadaptive_max_k"]) + 1):
        width = worst_cell_width(
            nonadaptive_cells(optimal_nonadaptive_thresholds(query_count))
        )
        nonadaptive_mismatches += int(
            width != Fraction(1, query_count + 1)
        )
        minimum_nonadaptive_width = (
            width
            if minimum_nonadaptive_width is None
            else min(minimum_nonadaptive_width, width)
        )

    rng = random.Random(int(spec["random_seed"]))
    random_bound_mismatches = 0
    for _ in range(int(spec["random_design_count"])):
        query_count = rng.randint(1, int(spec["random_max_k"]))
        denominator = 10_000_019
        thresholds = {
            Fraction(rng.randint(1, denominator - 1), denominator)
            for _ in range(query_count)
        }
        width = worst_cell_width(nonadaptive_cells(tuple(thresholds)))
        random_bound_mismatches += int(
            width < Fraction(1, len(thresholds) + 1)
        )
    return {
        **spec,
        "adaptive_mismatch_count": adaptive_mismatches,
        "nonadaptive_mismatch_count": nonadaptive_mismatches,
        "random_bound_mismatch_count": random_bound_mismatches,
        "minimum_adaptive_width": [
            minimum_adaptive_width.numerator,
            minimum_adaptive_width.denominator,
        ],
        "minimum_nonadaptive_width": [
            minimum_nonadaptive_width.numerator,
            minimum_nonadaptive_width.denominator,
        ],
    }


def run_inconsistent_control() -> dict[str, Any]:
    edges = ((0, 1), (1, 2), (2, 0))
    scores = (Fraction(1), Fraction(1), Fraction(1))
    fundamental = fundamental_residuals(3, edges, scores)
    _, residual = least_squares_projection(3, edges, scores)
    return {
        "coherent": is_coherent(3, edges, scores),
        "fundamental_residuals": [
            [value.numerator, value.denominator] for value in fundamental
        ],
        "hodge_residuals": [
            [value.numerator, value.denominator] for value in residual
        ],
        "passed": (
            not is_coherent(3, edges, scores)
            and max(abs(value) for value in fundamental) == 3
            and any(value != 0 for value in residual)
        ),
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# ASMP-9 behavioral well-posedness verification v0.7",
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
            "## Access ledger",
            "",
            "| family | graphs | ledger mismatches | reconstruction mismatches | non-bridge misses | bridge false alarms |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for family in ("simple_graphs", "multigraphs"):
        row = result[family]
        lines.append(
            f"| {family} | {row['count']} | "
            f"{row['ledger_mismatch_count']} | "
            f"{row['reconstruction_mismatch_count']} | "
            f"{row['nonbridge_corruption_mismatch_count']} | "
            f"{row['bridge_change_mismatch_count']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A spanning forest reconstructs a scalar only under a coherence",
            "promise. Non-bridge edges are the exact coherence-only audit",
            "universe; querying the remaining chords after a forest adds",
            "beta_1 model checks. Deterministic policy observations retain a",
            "positive ambiguity interval at every finite query count.",
            "",
            "## Claim boundary",
            "",
            "Classical finite graph/Hodge and threshold-search specialization;",
            "not finite-sample Bradley-Terry estimation, general IRL, a human",
            "model, or a complete ASMP-9 resolution.",
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
    simple = run_graph_cells(protocol["simple_graphs"], multigraph=False)
    multi = run_graph_cells(protocol["multigraphs"], multigraph=True)
    hodge = run_hodge_cells(protocol["hodge"])
    cycles = run_cycle_cells(protocol["cycles"])
    policy = run_policy_cells(protocol["policy"])
    inconsistent = run_inconsistent_control()

    graph_fields = (
        "ledger_mismatch_count",
        "reconstruction_mismatch_count",
        "nonbridge_corruption_mismatch_count",
        "bridge_change_mismatch_count",
    )
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_simple_graph_access": all(simple[name] == 0 for name in graph_fields),
        "G2_multigraph_access": all(multi[name] == 0 for name in graph_fields),
        "G3_hodge_projection": (
            hodge["orthogonality_mismatch_count"] == 0
            and hodge["zero_equivalence_mismatch_count"] == 0
        ),
        "G4_cycle_bounds": (
            cycles["bound_mismatch_count"] == 0
            and cycles["coherence_mismatch_count"] == 0
            and cycles["nonzero_circulation_count"] > 0
        ),
        "G5_inconsistent_control": inconsistent["passed"],
        "G6_adaptive_policy_width": policy["adaptive_mismatch_count"] == 0,
        "G7_nonadaptive_policy_width": (
            policy["nonadaptive_mismatch_count"] == 0
            and policy["random_bound_mismatch_count"] == 0
        ),
        "G8_finite_policy_ambiguity": (
            policy["minimum_adaptive_width"][0] > 0
            and policy["minimum_nonadaptive_width"][0] > 0
        ),
    }
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "behavioral_reconstruction_model_checking_split_not_verified"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "elapsed_seconds": time.perf_counter() - started,
        "binding_checks": binding,
        "simple_graphs": simple,
        "multigraphs": multi,
        "hodge": hodge,
        "cycles": cycles,
        "policy": policy,
        "inconsistent_control": inconsistent,
        "gates": gates,
        "verdict": verdict,
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_7.json"
    report_path = args.output_dir / "RESULT_v0_7.md"
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
    write_json(args.output_dir / "receipt_v0_7.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
