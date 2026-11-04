from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
import time
from pathlib import Path
from typing import Any

from finite_sample import (
    channel_capacity,
    farey_adjacency_audit,
    fano_fixed_budget_lower_bound,
    full_signature,
    identify_ray,
    logical_query_bound,
    nonadaptive_farey_lower_bound,
    primitive_rays,
    repetitions_required,
    theorem_width,
    vector_gcd,
)
from information_design import solve_information_design


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


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


def random_ray(
    dimension: int, bound: int, rng: random.Random
) -> tuple[int, ...]:
    while True:
        vector = tuple(
            rng.randint(-bound, bound) for _ in range(dimension)
        )
        if any(vector) and vector_gcd(vector) == 1:
            return vector


def validate_registration(
    registration_path: Path, registration: dict[str, Any]
) -> tuple[str, dict[str, bool]]:
    relative = registration_path.resolve().relative_to(REPO).as_posix()
    registration_commit = git("log", "-1", "--format=%H", "--", relative)
    head = git("rev-parse", "HEAD")
    checks = {
        "head_is_registration_commit": head == registration_commit,
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
        "tracked_tree_clean": not git(
            "status", "--porcelain", "--untracked-files=no"
        ),
    }
    for relative_path, expected in registration["sealed_files"].items():
        checks[f"hash:{relative_path}"] = (
            sha256(REPO / relative_path) == expected
        )
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"registration validation failed: {failed}")
    return registration_commit, checks


def run_exact_cells(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for block in protocol["exact_cells"]:
        dimension = int(block["dimension"])
        for bound in block["bounds"]:
            bound = int(bound)
            rays = primitive_rays(dimension, bound)
            failures = 0
            maximum_queries = 0
            maximum_width = 0
            for vector in rays:
                estimate, queries, width = identify_ray(
                    vector, bound, exact_oracle=True
                )
                failures += int(estimate != vector)
                maximum_queries = max(maximum_queries, queries)
                maximum_width = max(maximum_width, width)
            witness_left = (bound, bound - 1) + (0,) * (dimension - 2)
            witness_right = (bound - 1, bound - 2) + (0,) * (
                dimension - 2
            )
            critical = theorem_width(bound)
            collision_below = full_signature(
                witness_left, critical - 1
            ) == full_signature(witness_right, critical - 1)
            records.append(
                {
                    "dimension": dimension,
                    "bound": bound,
                    "ray_count": len(rays),
                    "failure_count": failures,
                    "maximum_logical_queries": maximum_queries,
                    "logical_query_bound": logical_query_bound(
                        dimension, bound
                    ),
                    "maximum_width": maximum_width,
                    "theorem_width": critical,
                    "lower_witness_collision_below": collision_below,
                }
            )
    return records


def run_random_cells(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for cell in protocol["random_cells"]:
        rng = random.Random(int(cell["seed"]))
        failures = 0
        maximum_queries = 0
        maximum_width = 0
        for _ in range(int(cell["count"])):
            vector = random_ray(
                int(cell["dimension"]), int(cell["bound"]), rng
            )
            estimate, queries, width = identify_ray(
                vector, int(cell["bound"]), exact_oracle=True
            )
            failures += int(estimate != vector)
            maximum_queries = max(maximum_queries, queries)
            maximum_width = max(maximum_width, width)
        records.append(
            {
                **cell,
                "failure_count": failures,
                "maximum_logical_queries": maximum_queries,
                "logical_query_bound": logical_query_bound(
                    int(cell["dimension"]), int(cell["bound"])
                ),
                "maximum_width": maximum_width,
                "theorem_width": theorem_width(int(cell["bound"])),
            }
        )
    return records


def run_noisy_cells(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for cell in protocol["noisy_cells"]:
        ray_rng = random.Random(int(cell["seed"]))
        failures = 0
        maximum_responses = 0
        maximum_width = 0
        dimension = int(cell["dimension"])
        bound = int(cell["bound"])
        eta = float(cell["eta"])
        alpha = float(cell["alpha"])
        logical = logical_query_bound(dimension, bound)
        repetitions = repetitions_required(eta, alpha, logical)
        response_bound = logical * repetitions
        for index in range(int(cell["count"])):
            vector = random_ray(dimension, bound, ray_rng)
            estimate, responses, width = identify_ray(
                vector,
                bound,
                eta=eta,
                alpha=alpha,
                seed=int(cell["seed"]) * 1_000_003 + index,
            )
            failures += int(estimate != vector)
            maximum_responses = max(maximum_responses, responses)
            maximum_width = max(maximum_width, width)
        count = int(cell["count"])
        records.append(
            {
                **cell,
                "failure_count": failures,
                "error_rate": failures / count,
                "repetitions_per_logical_query": repetitions,
                "maximum_responses": maximum_responses,
                "response_bound": response_bound,
                "maximum_width": maximum_width,
                "theorem_width": theorem_width(bound),
                "fano_lower_bound": fano_fixed_budget_lower_bound(
                    dimension, bound, eta, alpha
                ),
                "channel_capacity_bits": channel_capacity(eta),
            }
        )
    return records


def run_information_cells(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    spec = protocol["information_design"]
    records = []
    for bound in spec["bounds"]:
        critical = theorem_width(int(bound))
        for eta in spec["etas"]:
            below = solve_information_design(
                int(spec["dimension"]), int(bound), critical - 1, float(eta)
            )
            at = solve_information_design(
                int(spec["dimension"]), int(bound), critical, float(eta)
            )
            records.append(
                {
                    "dimension": int(spec["dimension"]),
                    "bound": int(bound),
                    "eta": float(eta),
                    "below_width": critical - 1,
                    "below_minimum_information": (
                        below.minimum_information
                    ),
                    "at_width": critical,
                    "at_minimum_information": at.minimum_information,
                    "at_support_size": at.support_size,
                }
            )
    return records


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# ASMP-9 finite-sample verification v0.5",
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
            "## Fresh exact cells",
            "",
            "| d | B | rays | failures | max queries / bound | max width / theorem | collision below |",
            "|---:|---:|---:|---:|---:|---:|:---:|",
        ]
    )
    for row in result["exact_cells"]:
        lines.append(
            f"| {row['dimension']} | {row['bound']} | {row['ray_count']} | "
            f"{row['failure_count']} | {row['maximum_logical_queries']} / "
            f"{row['logical_query_bound']} | {row['maximum_width']} / "
            f"{row['theorem_width']} | {row['lower_witness_collision_below']} |"
        )
    lines.extend(
        [
            "",
            "## Seeded noisy calibration",
            "",
            "| d | B | eta | trials | errors | error rate | max responses / bound |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in result["noisy_cells"]:
        lines.append(
            f"| {row['dimension']} | {row['bound']} | {row['eta']:.2f} | "
            f"{row['count']} | {row['failure_count']} | "
            f"{row['error_rate']:.6f} | {row['maximum_responses']} / "
            f"{row['response_bound']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The run verifies the implementation consequences of a finite-sample",
            "access theorem: below the exact coefficient width the stochastic",
            "laws remain indistinguishable; at the width, adaptive Farey search",
            "recovers the bounded primitive ray. The fresh adjacency cells also",
            "verify the combinatorial certificate behind the nonadaptive",
            "quadratic penalty.",
            "",
            "The noisy cells are seeded calibration only. The written proof,",
            "not their observed error, carries the probability guarantee.",
            "",
            "## Claim boundary",
            "",
            "Known independent sign-and-tie channel after shaping quotient;",
            "not Bradley-Terry learning, behavioral IRL, discounted shaping,",
            "human-consistency evidence, or a full ASMP-9 resolution.",
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
    exact_cells = run_exact_cells(protocol)
    random_cells = run_random_cells(protocol)
    noisy_cells = run_noisy_cells(protocol)
    information_cells = run_information_cells(protocol)
    adjacency_cells = [
        farey_adjacency_audit(bound)
        for bound in range(
            int(protocol["farey_adjacency_bounds"]["minimum"]),
            int(protocol["farey_adjacency_bounds"]["maximum"]) + 1,
        )
    ]
    info_spec = protocol["information_design"]
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_exact_constructor": all(
            row["failure_count"] == 0 for row in exact_cells
        ),
        "G2_width_liveness": all(
            row["maximum_width"] <= row["theorem_width"]
            and row["maximum_logical_queries"] <= row["logical_query_bound"]
            and row["lower_witness_collision_below"]
            for row in exact_cells
        ),
        "G3_high_dimensional_constructor": all(
            row["failure_count"] == 0
            and row["maximum_width"] <= row["theorem_width"]
            and row["maximum_logical_queries"] <= row["logical_query_bound"]
            for row in random_cells
        ),
        "G4_noisy_calibration": all(
            row["error_rate"] <= row["alpha"]
            and row["maximum_responses"] <= row["response_bound"]
            and row["maximum_width"] <= row["theorem_width"]
            for row in noisy_cells
        ),
        "G5_information_phase": all(
            row["below_minimum_information"]
            <= float(info_spec["zero_tolerance"])
            and row["at_minimum_information"]
            > float(info_spec["positive_tolerance"])
            for row in information_cells
        ),
        "G6_farey_adjacency": all(
            bool(row["valid"]) for row in adjacency_cells
        ),
        "G7_bound_sanity": all(
            math.isfinite(row["fano_lower_bound"])
            and row["fano_lower_bound"] > 0
            and row["response_bound"] >= row["fano_lower_bound"]
            and nonadaptive_farey_lower_bound(
                int(row["bound"]), float(row["eta"]), float(row["alpha"])
            )
            > 0
            for row in noisy_cells
            if int(row["bound"]) >= 3
        ),
    }
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "finite_sample_theorem_implementation_not_verified"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "elapsed_seconds": time.perf_counter() - started,
        "binding_checks": binding,
        "exact_cells": exact_cells,
        "random_cells": random_cells,
        "noisy_cells": noisy_cells,
        "information_cells": information_cells,
        "adjacency_cells": adjacency_cells,
        "gates": gates,
        "verdict": verdict,
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_5.json"
    report_path = args.output_dir / "RESULT_v0_5.md"
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
    write_json(args.output_dir / "receipt_v0_5.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
