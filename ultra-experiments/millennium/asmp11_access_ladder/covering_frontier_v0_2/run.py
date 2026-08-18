from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import time
from fractions import Fraction
from math import comb
from pathlib import Path

import scipy

from covering_frontier import find_exact_design, solve_covering, verify_cover


ROOT = Path(__file__).resolve().parent
REGISTRATION = ROOT / "registration_v0_2.json"
PROTOCOL = ROOT / "PROTOCOL_v0_2.md"
OUTPUT = ROOT / "artifacts_v0_2"
N_GRID = (13, 15, 17)
K_GRID = (3, 4)
FLIP_GRID = (Fraction(1, 20), Fraction(3, 20), Fraction(1, 4))
ALPHA = Fraction(1, 20)
TARGET_POWER = Fraction(9, 10)
SAMPLE_CAP = 4096
SOLVER_SECONDS = 120.0
RANDOM_CONTROL_DRAWS = 256


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def widths(n: int, k: int) -> tuple[int, ...]:
    if k == 3:
        return (n - 3, n - 2, n - 1, n)
    if k == 4:
        return (n - 2, n - 1, n)
    raise ValueError("degree outside frozen grid")


def verify_registration() -> dict[str, object]:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    for relative, expected in registration["source_hashes"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"registration mismatch for {relative}")
    return registration


def matched_random_complete_rate(
    n: int, block_size: int, support_size: int, family_size: int
) -> Fraction:
    universe = list(__import__("itertools").combinations(range(n), block_size))
    complete = 0
    seed = int.from_bytes(
        hashlib.sha256(f"{n}:{block_size}:{support_size}:{family_size}".encode()).digest()[:8],
        "big",
    )
    rng = random.Random(seed)
    for _ in range(RANDOM_CONTROL_DRAWS):
        family = rng.sample(universe, family_size)
        complete += int(verify_cover(n, block_size, support_size, family))
    return Fraction(complete, RANDOM_CONTROL_DRAWS)


def main() -> int:
    registration = verify_registration()
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise FileExistsError(f"write-once output is not empty: {OUTPUT}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    started = time.time()

    solutions = []
    witnesses = []
    for n in N_GRID:
        for k in K_GRID:
            for block_size in widths(n, k):
                solution = solve_covering(
                    n,
                    block_size,
                    k,
                    time_limit_seconds=SOLVER_SECONDS,
                )
                solutions.append(solution)
                witnesses.append(
                    {
                        "n": n,
                        "block_size": block_size,
                        "support_size": k,
                        "optimum": solution.optimum,
                        "selected_blocks": [list(block) for block in solution.selected_blocks],
                    }
                )

    power_cache = {}
    rows = []
    crossovers = []
    for n in N_GRID:
        for k in K_GRID:
            pure_q = comb(n, k)
            for flip_rate in FLIP_GRID:
                pure_key = (pure_q, flip_rate)
                if pure_key not in power_cache:
                    power_cache[pure_key] = find_exact_design(
                        pure_q, flip_rate, ALPHA, TARGET_POWER, SAMPLE_CAP
                    )
                pure_design = power_cache[pure_key]
                if pure_design is None:
                    raise RuntimeError("pure observation exceeded sample cap")
                condition_rows = []
                for solution in [item for item in solutions if item.n == n and item.support_size == k]:
                    key = (solution.optimum, flip_rate)
                    if key not in power_cache:
                        power_cache[key] = find_exact_design(
                            solution.optimum,
                            flip_rate,
                            ALPHA,
                            TARGET_POWER,
                            SAMPLE_CAP,
                        )
                    design = power_cache[key]
                    if design is None:
                        raise RuntimeError("covering design exceeded sample cap")
                    random_rate = matched_random_complete_rate(
                        n, solution.block_size, k, solution.optimum
                    )
                    row = {
                        "n": n,
                        "k": k,
                        "block_size": solution.block_size,
                        "flip_rate": str(flip_rate),
                        "covering_number": solution.optimum,
                        "counting_lower_bound": solution.counting_lower_bound,
                        "schoenheim_lower_bound": solution.schoenheim_lower_bound,
                        "mip_gap": solution.mip_gap,
                        "mip_dual_bound": solution.mip_dual_bound,
                        "mip_node_count": solution.mip_node_count,
                        "samples_per_query": design.samples_per_query,
                        "total_samples": design.total_samples,
                        "fwer_upper": str(design.familywise_error_upper),
                        "power_lower": str(design.signal_power_lower),
                        "pure_observation_queries": pure_q,
                        "pure_observation_samples": pure_design.total_samples,
                        "sample_ratio": design.total_samples / pure_design.total_samples,
                        "beats_pure_observation": int(design.total_samples < pure_design.total_samples),
                        "random_complete_rate": str(random_rate),
                    }
                    rows.append(row)
                    condition_rows.append(row)
                first = next(
                    (
                        row
                        for row in sorted(condition_rows, key=lambda item: int(item["block_size"]))
                        if row["beats_pure_observation"]
                    ),
                    None,
                )
                crossovers.append(
                    {
                        "n": n,
                        "k": k,
                        "flip_rate": str(flip_rate),
                        "first_crossover_width": first["block_size"] if first else None,
                        "first_crossover_ratio": first["sample_ratio"] if first else None,
                    }
                )

    monotone = True
    lower_sane = True
    optimality = True
    endpoint = True
    liveness = True
    for n in N_GRID:
        for k in K_GRID:
            sequence = sorted(
                (item for item in solutions if item.n == n and item.support_size == k),
                key=lambda item: item.block_size,
            )
            monotone &= [item.optimum for item in sequence] == sorted(
                [item.optimum for item in sequence], reverse=True
            )
            endpoint &= sequence[-1].block_size == n and sequence[-1].optimum == 1
            for solution in sequence:
                lower_sane &= (
                    solution.counting_lower_bound <= solution.optimum
                    and solution.schoenheim_lower_bound <= solution.optimum
                )
                optimality &= (
                    solution.solver_status == 0
                    and solution.mip_gap <= 1e-12
                    and abs(solution.mip_dual_bound - solution.optimum) <= 1e-7
                    and verify_cover(
                        solution.n,
                        solution.block_size,
                        solution.support_size,
                        solution.selected_blocks,
                    )
                )
                liveness &= any(
                    not verify_cover(
                        solution.n,
                        solution.block_size,
                        solution.support_size,
                        solution.selected_blocks[:index] + solution.selected_blocks[index + 1 :],
                    )
                    for index in range(len(solution.selected_blocks))
                )

    finite_calibration = all(
        Fraction(row["fwer_upper"]) <= ALPHA
        and Fraction(row["power_lower"]) >= TARGET_POWER
        and int(row["samples_per_query"]) <= SAMPLE_CAP
        for row in rows
    )
    strata = {}
    for k in K_GRID:
        for flip_rate in FLIP_GRID:
            relevant = [
                item for item in crossovers if item["k"] == k and item["flip_rate"] == str(flip_rate)
            ]
            strata[(k, flip_rate)] = sum(item["first_crossover_width"] is not None for item in relevant) >= 2
    crossover_pass = any(strata.values())

    gates = {
        "G0_registration_binding": all(
            sha256(ROOT / relative) == expected
            for relative, expected in registration["source_hashes"].items()
        ),
        "G1_covering_validity": optimality,
        "G2_endpoint_controls": endpoint,
        "G3_lower_bound_and_monotonicity": lower_sane and monotone,
        "G4_exact_finite_sample_calibration": finite_calibration,
        "G5_all_negative_path_liveness": liveness,
        "G6_crossover": crossover_pass,
    }
    core_valid = all(gates[name] for name in gates if name != "G6_crossover")
    verdict = (
        "finite_covering_frontier_with_sample_crossover_established"
        if core_valid and gates["G6_crossover"]
        else "finite_covering_frontier_established_cost_inversion_not_established"
        if core_valid
        else "invalid_or_not_established"
    )

    csv_path = OUTPUT / "frontier.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    crossover_path = OUTPUT / "crossovers.csv"
    with crossover_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(crossovers[0]))
        writer.writeheader()
        writer.writerows(crossovers)
    witness_path = OUTPUT / "covering_witnesses.json"
    witness_path.write_text(canonical_json(witnesses), encoding="utf-8")
    result = {
        "schema_version": "asmp11_covering_frontier_result_v0_2",
        "verdict": verdict,
        "gates": gates,
        "counts": {
            "covering_cells": len(solutions),
            "finite_sample_cells": len(rows),
            "crossover_strata": sum(strata.values()),
        },
        "registered_probability": {
            "alpha": fraction_record(ALPHA),
            "target_power": fraction_record(TARGET_POWER),
        },
        "claim_boundary": "Solver-certified finite covering designs and exact rational power for a transparent parity oracle only.",
    }
    result_path = OUTPUT / "result.json"
    result_path.write_text(canonical_json(result), encoding="utf-8")
    receipt = {
        "schema_version": "asmp11_covering_frontier_receipt_v0_2",
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(PROTOCOL),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "elapsed_seconds": time.time() - started,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "scipy": scipy.__version__,
        },
        "outputs": {
            "covering_witnesses.json": sha256(witness_path),
            "crossovers.csv": sha256(crossover_path),
            "frontier.csv": sha256(csv_path),
            "result.json": sha256(result_path),
        },
    }
    (OUTPUT / "receipt.json").write_text(canonical_json(receipt), encoding="utf-8")
    print(canonical_json({"verdict": verdict, "gates": gates, "output": str(OUTPUT)}), end="")
    return 0 if core_valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
