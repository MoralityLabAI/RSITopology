"""Execute the sealed ASMP-9 v0.45 allocation confirmation."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

import psutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V41 = HERE.parent / "sequential_risk_access_v0_41"
for path in (HERE, V41):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from allocation_design import (  # noqa: E402
    method_of_types_kl_upper,
    optimize_constructive_upper,
    optimize_serial_control,
    qstr,
    two_point_radius_lower,
)
from audit_formula_universe import audit_mode  # noqa: E402


PROTOCOL_ID = "asmp9-decision-directed-sample-allocation-v0.45"
VERSION = "0.45"
TOTAL_BUDGET = 60
WORKERS = 4
EXPECTED_TESTS = 21


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def validate_source_hashes(registration: dict) -> tuple[bool, list[dict]]:
    rows = []
    for relative, expected in sorted(
        registration["source_sha256"].items()
    ):
        path = REPO / relative
        actual = sha256_file(path) if path.is_file() else None
        rows.append(
            {
                "path": relative,
                "expected": expected,
                "actual": actual,
                "match": actual == expected,
            }
        )
    return all(row["match"] for row in rows), rows


def run_tests() -> dict:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        str(HERE / "test_allocation_design.py"),
    ]
    completed = subprocess.run(
        command,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    output = completed.stdout + completed.stderr
    matches = re.findall(r"(\d+) passed", output)
    count = int(matches[-1]) if matches else 0
    return {
        "command": command,
        "returncode": completed.returncode,
        "passed": count,
        "expected": EXPECTED_TESTS,
        "ok": completed.returncode == 0 and count == EXPECTED_TESTS,
        "output": output.strip(),
    }


def _clean_audit(row: dict) -> dict:
    result = dict(row)
    result.pop("elapsed_seconds", None)
    result.pop("workers", None)
    return result


def _allocation_summary(audit: dict) -> dict:
    best = Q(audit["exact_best_upper"])
    uniform = Q(audit["exact_uniform_upper"])
    improvement = uniform - best
    return {
        "exact_optima": audit["exact_optima"],
        "exact_best_upper": qstr(best),
        "uniform_allocation": audit["uniform_allocation"],
        "exact_uniform_upper": qstr(uniform),
        "absolute_improvement": qstr(improvement),
        "relative_improvement": (
            float(improvement / uniform) if uniform else 0.0
        ),
        "constructive_optima": audit["formula_optima"],
        "constructive_best_upper": audit["formula_best_upper"],
        "constructive_mismatch_count": audit["mismatch_count"],
        "constructive_underbound_count": audit[
            "constructive_underbound_count"
        ],
        "maximum_constructive_excess": audit[
            "maximum_formula_excess"
        ],
        "row_universe_sha256": audit["rows_sha256"],
    }


def build_scientific_payload(workers: int = WORKERS) -> dict:
    audits = {
        mode: _clean_audit(
            audit_mode(mode, TOTAL_BUDGET, workers)
        )
        for mode in (
            "branch_classification",
            "root_group",
        )
    }
    allocations = {
        mode: _allocation_summary(audit)
        for mode, audit in audits.items()
    }
    constructive = {
        mode: {
            "optimum": list(
                optimize_constructive_upper(
                    TOTAL_BUDGET, mode
                )["optimum"]
            ),
            "best_upper": qstr(
                optimize_constructive_upper(
                    TOTAL_BUDGET, mode
                )["best_upper"]
            ),
            "uniform": list(
                optimize_constructive_upper(
                    TOTAL_BUDGET, mode
                )["uniform"]
            ),
            "uniform_upper": qstr(
                optimize_constructive_upper(
                    TOTAL_BUDGET, mode
                )["uniform_upper"]
            ),
        }
        for mode in (
            "branch_classification",
            "root_group",
        )
    }
    serial = optimize_serial_control(TOTAL_BUDGET, 3)
    serial_payload = {
        "optima": [list(row) for row in serial["optima"]],
        "uniform": list(serial["uniform"]),
        "uniform_is_optimal": serial["uniform_is_optimal"],
        "best_information": qstr(serial["best_information"]),
        "evaluated_allocations": serial["evaluated_allocations"],
    }
    counts = sorted(
        {
            value
            for row in (
                allocations["branch_classification"]["exact_optima"]
                + allocations["root_group"]["exact_optima"]
                + [
                    allocations["branch_classification"][
                        "uniform_allocation"
                    ],
                    allocations["root_group"][
                        "uniform_allocation"
                    ],
                ]
            )
            for value in row
        }
    )
    lower_rows = []
    for samples in counts:
        row = two_point_radius_lower(samples)
        lower_rows.append(
            {
                "samples": samples,
                "alpha": qstr(row["alpha"]),
                "grid_denominator": row["grid_denominator"],
                "radius_lower": qstr(row["radius_lower"]),
                "bayes_error": qstr(row["bayes_error"]),
                "next_grid_error": qstr(row["next_grid_error"]),
            }
        )
    tolls = [
        method_of_types_kl_upper(n, 3, "0.05")
        for n in range(1, TOTAL_BUDGET + 1)
    ]
    return {
        "total_budget": TOTAL_BUDGET,
        "query_order": ["root", "left", "right"],
        "allocation_universe_per_problem": 1711,
        "alpha": "1/20",
        "method_of_types": {
            "formula": "log(3*(n+1)/0.05)/n",
            "decimal_digits": 12,
            "rows": len(tolls),
            "first": qstr(tolls[0]),
            "last": qstr(tolls[-1]),
            "positive": all(value > 0 for value in tolls),
            "strictly_decreasing": all(
                left > right
                for left, right in zip(tolls, tolls[1:])
            ),
        },
        "audits": audits,
        "allocations": allocations,
        "constructive_predictions": constructive,
        "serial_control": serial_payload,
        "two_point_lower": lower_rows,
    }


def scientific_gates(scientific: dict) -> dict[str, bool]:
    classification = scientific["allocations"][
        "branch_classification"
    ]
    group = scientific["allocations"]["root_group"]
    audits = scientific["audits"]
    lower = scientific["two_point_lower"]
    return {
        "U0": (
            scientific["total_budget"] == 60
            and scientific["query_order"]
            == ["root", "left", "right"]
            and all(
                row["allocations"] == 1711
                for row in audits.values()
            )
        ),
        "K0": (
            scientific["method_of_types"]["rows"] == 60
            and scientific["method_of_types"]["positive"]
            and scientific["method_of_types"][
                "strictly_decreasing"
            ]
        ),
        "E0": sum(
            row["allocations"] for row in audits.values()
        )
        == 3422,
        "B0": all(
            row["constructive_underbound_count"] == 0
            for row in audits.values()
        ),
        "A0": (
            classification["exact_optima"] == [[26, 17, 17]]
            and classification["relative_improvement"] > 0.01
        ),
        "D0": (
            group["exact_optima"] == [[58, 1, 1]]
            and group["relative_improvement"] > 0.35
        ),
        "C0": (
            scientific["serial_control"]["optima"]
            == [[20, 20, 20]]
            and scientific["serial_control"][
                "uniform_is_optimal"
            ]
        ),
        "L0": bool(lower)
        and all(
            Q(row["bayes_error"]) > Q(1, 20)
            and Q(row["next_grid_error"]) <= Q(1, 20)
            for row in lower
        ),
        "R0": (
            classification["exact_optima"]
            != group["exact_optima"]
        ),
    }


def total_status(gates: dict[str, bool]) -> str:
    if not gates.get("S0", False):
        return "invalid_provenance"
    if not gates.get("B0", False):
        return "theorem_or_implementation_failure"
    if all(gates.values()):
        return "decision_directed_sample_allocation_established"
    return "decision_directed_allocation_not_established"


class ResourceMonitor:
    def __init__(self) -> None:
        self.process = psutil.Process()
        self.peak = 0
        self.stop = threading.Event()
        self.thread = threading.Thread(
            target=self._sample, daemon=True
        )

    def _sample(self) -> None:
        while not self.stop.is_set():
            processes = [self.process]
            try:
                processes.extend(
                    self.process.children(recursive=True)
                )
            except psutil.Error:
                pass
            total = 0
            for process in processes:
                try:
                    total += process.memory_info().rss
                except psutil.Error:
                    pass
            self.peak = max(self.peak, total)
            self.stop.wait(0.02)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.stop.set()
        self.thread.join(timeout=2)


def compare_or_write(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError(f"write-once mismatch: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_45.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "artifacts_v0_45" / "RESULT_v0_45.json",
    )
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    started = time.perf_counter()
    with ResourceMonitor() as monitor:
        source_match, source_checks = validate_source_hashes(
            registration
        )
        tests = run_tests()
        scientific = build_scientific_payload(WORKERS)
    elapsed = time.perf_counter() - started
    resource = {
        "elapsed_seconds": elapsed,
        "peak_aggregate_working_set_bytes": monitor.peak,
        "worker_processes": WORKERS,
        "seconds_ceiling": registration["resource_ceiling"][
            "seconds"
        ],
        "bytes_ceiling": registration["resource_ceiling"][
            "peak_aggregate_working_set_bytes"
        ],
    }
    gates = scientific_gates(scientific)
    gates["P0"] = tests["ok"]
    gates["S0"] = source_match
    gates["RESOURCE"] = (
        elapsed <= resource["seconds_ceiling"]
        and monitor.peak <= resource["bytes_ceiling"]
        and WORKERS
        == registration["resource_ceiling"]["worker_processes"]
    )
    payload = {
        "protocol_id": PROTOCOL_ID,
        "version": VERSION,
        "registration_sha256": sha256_bytes(registration_bytes),
        "status": total_status(gates),
        "gates": gates,
        "scientific": scientific,
        "tests": tests,
        "source_checks": source_checks,
        "resource": resource,
    }
    compare_or_write(args.output.resolve(), canonical_json_bytes(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(
        payload["status"]
        != "decision_directed_sample_allocation_established"
    )


if __name__ == "__main__":
    main()
