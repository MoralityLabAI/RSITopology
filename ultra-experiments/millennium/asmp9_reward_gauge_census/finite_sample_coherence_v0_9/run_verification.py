from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from scipy.stats import beta

from experiment import (
    named_graphs,
    run_floor_control,
    run_forest_control,
    run_graph_cells,
)
from finite_sample_coherence import hoeffding_probability_radius


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ALLOWED_STATUSES = {
    "certified_coherent_within_tolerance",
    "certified_incoherent",
    "inconclusive",
    "unavailable_no_cycles",
    "unavailable_probability_floor",
    "unavailable_no_edges",
}


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


def one_sided_exact_lower(
    successes: int, trials: int, tail_probability: float
) -> float:
    if trials < 1 or not 0 <= successes <= trials:
        raise ValueError("invalid binomial counts")
    if successes == 0:
        return 0.0
    return float(beta.ppf(tail_probability, successes, trials - successes + 1))


def status_count(cell: dict[str, Any], arm: str, status: str) -> int:
    return int(cell[f"{arm}_status_counts"].get(status, 0))


def bound_is_minimal(
    result: dict[str, Any], protocol: dict[str, Any]
) -> bool:
    bound = int(result["sufficient_samples_per_edge"])
    edge_count = int(result["metadata"]["edge_count"])
    maximum_length = int(result["metadata"]["maximum_cycle_length"])
    eta = float(protocol["probability_floor"])
    delta = float(protocol["planted_circulation"])
    incoherent = float(protocol["incoherent_margin"])
    coherent = float(protocol["coherent_tolerance"])
    cycle_allowed = (
        min(coherent, delta - incoherent)
        * eta
        * (1.0 - eta)
        / (2.0 * maximum_length)
    )
    allowed = min(float(result["interior_margin"]) / 2.0, cycle_allowed)

    def clears(samples: int) -> bool:
        return (
            hoeffding_probability_radius(
                edge_count, samples, float(protocol["alpha"])
            )
            <= allowed
        )

    return clears(bound) and (bound == 1 or not clears(bound - 1))


def all_statuses(result: dict[str, Any]) -> set[str]:
    found: set[str] = set()
    for graph in result["graphs"]:
        for cell in graph["cells"]:
            for arm in ("coherent", "positive", "negative"):
                found.update(cell[f"{arm}_status_counts"])
    found.update(result["forest_control"]["status_counts"])
    found.update(result["floor_control"]["status_counts"])
    return found


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# ASMP-9 finite-sample coherence verification v0.9",
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
            "## Graph-dependent sufficient bounds",
            "",
            "| graph | beta_1 | k_max | samples per edge |",
            "|---|---:|---:|---:|",
        ]
    )
    for graph in result["graphs"]:
        lines.append(
            f"| {graph['graph_name']} | {graph['metadata']['beta_1']} | "
            f"{graph['metadata']['maximum_cycle_length']} | "
            f"{graph['sufficient_samples_per_edge']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The registered simultaneous certificate distinguishes a declared",
            "near-coherent region, a separated circulation alternative, and",
            "an inconclusive region without turning non-rejection into scalar",
            "coherence. Forests and probability-boundary violations remain",
            "unavailable by construction.",
            "",
            "## Claim boundary",
            "",
            "Independent fixed-count Bernoulli comparisons on six planted",
            "finite graphs; not minimax sample complexity, adaptive allocation,",
            "human-response modeling, general IRL, or an ASMP-9 resolution.",
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
    graph_universe = named_graphs()
    graphs = []
    graph_arithmetic = []
    for spec in protocol["graphs"]:
        vertex_count, edges = graph_universe[spec["name"]]
        result = run_graph_cells(
            graph_name=spec["name"],
            vertex_count=vertex_count,
            edges=edges,
            seed=int(spec["seed"]),
            replicates=int(protocol["replicates"]),
            multipliers=tuple(map(float, protocol["multipliers"])),
            alpha=float(protocol["alpha"]),
            probability_floor=float(protocol["probability_floor"]),
            coherent_tolerance=float(protocol["coherent_tolerance"]),
            incoherent_margin=float(protocol["incoherent_margin"]),
            planted_circulation=float(protocol["planted_circulation"]),
        )
        graphs.append(result)
        graph_arithmetic.append(
            result["metadata"]["beta_1"] == spec["expected_beta_1"]
            and result["metadata"]["maximum_cycle_length"]
            == spec["expected_maximum_cycle_length"]
            and bound_is_minimal(result, protocol)
        )

    controls = protocol["controls"]
    forest = run_forest_control(
        replicates=int(controls["replicates"]),
        samples_per_edge=int(controls["samples_per_edge"]),
        seed=int(controls["forest_seed"]),
        alpha=float(protocol["alpha"]),
        probability_floor=float(protocol["probability_floor"]),
        coherent_tolerance=float(protocol["coherent_tolerance"]),
        incoherent_margin=float(protocol["incoherent_margin"]),
    )
    floor = run_floor_control(
        replicates=int(controls["replicates"]),
        samples_per_edge=int(controls["samples_per_edge"]),
        seed=int(controls["floor_seed"]),
        alpha=float(protocol["alpha"]),
        probability_floor=float(protocol["probability_floor"]),
        coherent_tolerance=float(protocol["coherent_tolerance"]),
        incoherent_margin=float(protocol["incoherent_margin"]),
    )

    monte = protocol["monte_carlo_gates"]
    low_checks = []
    high_checks = []
    safety_checks = []
    bound_checks = []
    mirror_checks = []
    lcb_records = []
    for graph in graphs:
        for cell in graph["cells"]:
            mirror_checks.append(cell["mirror_status_match"])
            safety_checks.extend(
                cell["unsafe_on_event_counts"].get(arm, 0) == 0
                for arm in ("coherent", "positive", "negative")
            )
            if cell["multiplier"] >= monte["high_multiplier_floor"]:
                bound_checks.extend(
                    cell["unsafe_on_event_counts"].get(
                        f"{arm}_bound_miss", 0
                    )
                    == 0
                    for arm in ("coherent", "positive", "negative")
                )
            for arm in ("coherent", "positive", "negative"):
                expected = (
                    "certified_coherent_within_tolerance"
                    if arm == "coherent"
                    else "certified_incoherent"
                )
                if cell["multiplier"] == monte["low_multiplier"]:
                    success = status_count(cell, arm, "inconclusive")
                    lower = one_sided_exact_lower(
                        success,
                        int(protocol["replicates"]),
                        float(monte["tail_probability"]),
                    )
                    low_checks.append(
                        lower > monte["minimum_low_inconclusive_lcb"]
                    )
                    lcb_records.append(
                        {
                            "graph": graph["graph_name"],
                            "arm": arm,
                            "multiplier": cell["multiplier"],
                            "target": "inconclusive",
                            "successes": success,
                            "lower_99": lower,
                        }
                    )
                if cell["multiplier"] >= monte["high_multiplier_floor"]:
                    success = status_count(cell, arm, expected)
                    lower = one_sided_exact_lower(
                        success,
                        int(protocol["replicates"]),
                        float(monte["tail_probability"]),
                    )
                    high_checks.append(
                        lower > monte["minimum_high_expected_lcb"]
                    )
                    lcb_records.append(
                        {
                            "graph": graph["graph_name"],
                            "arm": arm,
                            "multiplier": cell["multiplier"],
                            "target": expected,
                            "successes": success,
                            "lower_99": lower,
                        }
                    )

    partial_result = {
        "graphs": graphs,
        "forest_control": forest,
        "floor_control": floor,
    }
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_graph_and_bound_arithmetic": all(graph_arithmetic),
        "G2_forest_nonvacuity": forest["status_counts"]
        == {"unavailable_no_cycles": int(controls["replicates"])},
        "G3_probability_floor_admission": floor["nonunavailable_on_event"] == 0,
        "G4_certificate_safety": all(safety_checks),
        "G5_sufficient_bound_liveness": all(bound_checks),
        "G6_low_budget_inconclusiveness": all(low_checks),
        "G7_high_budget_decisiveness": all(high_checks),
        "G8_sign_mirror": all(mirror_checks),
        "G9_status_closure": all_statuses(partial_result)
        <= ALLOWED_STATUSES,
    }
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "finite_sample_cycle_coherence_certificate_not_verified"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "elapsed_seconds": time.perf_counter() - started,
        "binding_checks": binding,
        **partial_result,
        "monte_carlo_lcbs": lcb_records,
        "gates": gates,
        "verdict": verdict,
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_9.json"
    report_path = args.output_dir / "RESULT_v0_9.md"
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
    write_json(args.output_dir / "receipt_v0_9.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
