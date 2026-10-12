"""Execute the sealed deterministic ASMP-9 v0.43 confirmation."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import time

import psutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V41 = HERE.parent / "sequential_risk_access_v0_41"
for path in (HERE, V41):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rate_theorem import (  # noqa: E402
    no_linear_horizon_witness_ratio,
    required_block_samples,
    sentinel_deficiency,
    two_point_certificate,
    qstr,
)
from sequential_access import (  # noqa: E402
    QueryChannel,
    adaptive_upper_generators,
    classification_problem,
    directed_upper_deficiency,
)


PROTOCOL_ID = "asmp9-finite-horizon-rate-v0.43"
VERSION = "0.43"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def sentinel_query(p: Q) -> QueryChannel:
    return QueryChannel(
        "sentinel",
        (
            (Q(1), Q(0)),
            (Q(1) - p, p),
        ),
    )


def compiler_rows() -> list[dict]:
    rows = []
    for horizon in (1, 2, 3, 4, 5, 6):
        for p in (Q(0), Q(1, 8), Q(1, 4), Q(1, 3), Q(1)):
            source = adaptive_upper_generators(
                (sentinel_query(p),),
                classification_problem(2),
                horizon,
            )
            compiled = directed_upper_deficiency(
                source, ((Q(0), Q(0)),)
            ).epsilon
            formula = sentinel_deficiency(horizon, p)
            rows.append(
                {
                    "horizon": horizon,
                    "p": qstr(p),
                    "compiled_deficiency": qstr(compiled),
                    "formula_deficiency": qstr(formula),
                    "exact_match": compiled == formula,
                }
            )
    return rows


def lower_bound_rows() -> list[dict]:
    rows = []
    for horizon in (2, 3, 4, 8, 16, 32, 64, 128):
        for epsilon in (Q(1, 32), Q(1, 16), Q(1, 8), Q(1, 4)):
            row = two_point_certificate(horizon, epsilon).jsonable()
            gap = Q(row["deficiency_gap"])
            chi_square = Q(row["chi_square_upper_on_kl"])
            row["gap_bounds_pass"] = epsilon / 16 <= gap <= epsilon
            row["chi_square_bound_pass"] = (
                chi_square <= 4 * epsilon**2 / horizon
            )
            rows.append(row)
    return rows


def no_witness_rows() -> list[dict]:
    return [
        {
            "horizon": horizon,
            "kl_quadratic_constant": 4.0,
            "risk_gap_over_h_delta_upper": (
                no_linear_horizon_witness_ratio(horizon, 4.0)
            ),
        }
        for horizon in (2, 8, 32, 128)
    ]


def upper_bound_rows() -> list[dict]:
    return [
        required_block_samples(horizon, gap, 0.05)
        for gap in (1 / 32, 1 / 16, 1 / 8)
        for horizon in (8, 16, 32, 64, 128)
    ]


def build_scientific_payload() -> dict:
    compiler = compiler_rows()
    lower = lower_bound_rows()
    no_witness = no_witness_rows()
    upper = upper_bound_rows()
    return {
        "compiler_agreement": compiler,
        "two_point_lower_bounds": lower,
        "no_linear_witness": no_witness,
        "block_upper_bounds": upper,
    }


def scientific_gates(scientific: dict) -> dict[str, bool]:
    compiler = scientific["compiler_agreement"]
    lower = scientific["two_point_lower_bounds"]
    no_witness = scientific["no_linear_witness"]
    upper = scientific["block_upper_bounds"]

    ratios = [
        row["risk_gap_over_h_delta_upper"] for row in no_witness
    ]
    k0 = (
        all(left > right for left, right in zip(ratios, ratios[1:]))
        and ratios[-1] <= ratios[0] / 8
    )

    u0 = True
    for gap in (1 / 32, 1 / 16, 1 / 8):
        rows = [row for row in upper if row["gap"] == gap]
        u0 = u0 and len({row["blocks"] for row in rows}) == 1
        u0 = u0 and all(
            row["raw_samples"] == row["horizon"] * row["blocks"]
            and row["radius"] < gap
            for row in rows
        )
        normalized = {
            round(row["normalized_samples_gap_squared_over_h"], 14)
            for row in rows
        }
        u0 = u0 and len(normalized) == 1

    return {
        "E0": len(compiler) == 30
        and all(row["exact_match"] for row in compiler),
        "L0": len(lower) == 32
        and all(
            row["gap_bounds_pass"] and row["chi_square_bound_pass"]
            for row in lower
        ),
        "K0": k0,
        "U0": u0,
        "R0": (
            len(compiler) == 30
            and len(lower) == 32
            and len(no_witness) == 4
            and len(upper) == 15
        ),
    }


def validate_source_hashes(registration: dict) -> tuple[bool, list[dict]]:
    rows = []
    all_match = True
    for relative, expected in sorted(
        registration["source_sha256"].items()
    ):
        path = REPO / relative
        actual = sha256_file(path) if path.is_file() else None
        match = actual == expected
        rows.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "match": match,
            }
        )
        all_match = all_match and match
    return all_match, rows


def run_registered_tests(registration: dict) -> dict:
    command = registration["test_command"]
    completed = subprocess.run(
        command,
        cwd=REPO,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=registration["resource_ceiling"]["seconds"],
    )
    match = re.search(r"(\d+) passed", completed.stdout)
    passed = int(match.group(1)) if match else None
    return {
        "command": command,
        "returncode": completed.returncode,
        "passed": passed,
        "expected_passed": registration["expected_test_count"],
        "match": (
            completed.returncode == 0
            and passed == registration["expected_test_count"]
        ),
        "stdout_tail": completed.stdout[-2000:],
    }


class MemorySampler:
    def __init__(self) -> None:
        self.stop = threading.Event()
        self.peak = 0
        self.thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        process = psutil.Process()
        while not self.stop.is_set():
            total = 0
            try:
                total += process.memory_info().rss
                for child in process.children(recursive=True):
                    try:
                        total += child.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            self.peak = max(self.peak, total)
            self.stop.wait(0.01)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop.set()
        self.thread.join()


def total_status(gates: dict[str, bool]) -> str:
    if not gates["S0"]:
        return "invalid_provenance"
    if not gates["RESOURCE"]:
        return "resource_gate_failed"
    if all(gates.values()):
        return "finite_horizon_rate_characterization_established"
    return "theorem_or_implementation_failure"


def execute(registration_path: Path, output_path: Path) -> dict:
    start = time.perf_counter()
    with MemorySampler() as sampler:
        registration_bytes = registration_path.read_bytes()
        registration = json.loads(registration_bytes)
        if registration["protocol_id"] != PROTOCOL_ID:
            raise ValueError("wrong protocol_id")
        if registration["version"] != VERSION:
            raise ValueError("wrong protocol version")

        source_match, source_rows = validate_source_hashes(registration)
        tests = run_registered_tests(registration)
        scientific = build_scientific_payload()
        gates = scientific_gates(scientific)
        gates["P0"] = tests["match"]
        gates["S0"] = source_match

    elapsed = time.perf_counter() - start
    gates["RESOURCE"] = (
        elapsed <= registration["resource_ceiling"]["seconds"]
        and sampler.peak
        <= registration["resource_ceiling"]["peak_working_set_bytes"]
    )
    payload = {
        "protocol_id": PROTOCOL_ID,
        "version": VERSION,
        "registration_sha256": sha256_bytes(registration_bytes),
        "status": total_status(gates),
        "gates": dict(sorted(gates.items())),
        "scientific": scientific,
        "provenance": {
            "source_checks": source_rows,
            "tests": tests,
        },
        "resource": {
            "elapsed_seconds": elapsed,
            "peak_working_set_bytes": sampler.peak,
            "ceiling": registration["resource_ceiling"],
        },
        "claim_boundary": registration["claim_boundary"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_json_bytes(payload)
    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, dir=output_path.parent
    ) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, output_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_43.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "artifacts_v0_43" / "RESULT_v0_43.json",
    )
    args = parser.parse_args()
    payload = execute(
        args.registration.resolve(), args.output.resolve()
    )
    print(json.dumps(
        {
            "status": payload["status"],
            "gates": payload["gates"],
            "output": str(args.output.resolve()),
        },
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
