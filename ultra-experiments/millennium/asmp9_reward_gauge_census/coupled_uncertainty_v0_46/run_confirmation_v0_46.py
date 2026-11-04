"""Execute the sealed ASMP-9 v0.46 coupled-uncertainty confirmation."""

from __future__ import annotations

import argparse
from dataclasses import is_dataclass
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
V45 = HERE.parent / "sample_allocation_v0_45"
for path in (HERE, V45):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from allocation_design import (  # noqa: E402
    optimize_constructive_upper,
    positive_allocations,
)
from audit_formula_universe import (  # noqa: E402
    _audit_one,
    _initialize_worker,
    audit_mode,
)
from coupled_uncertainty import (  # noqa: E402
    exp_neg_fraction_bounds,
    flip_probability_bounds,
    optimize_coupled_minimax_classification,
    optimize_coupled_root_group,
    product_box_control,
    qstr,
    symbolic_classification_policies,
)


PROTOCOL_ID = "asmp9-coupled-shared-channel-v0.46"
VERSION = "0.46"
TOTAL_BUDGET = 66
ALLOCATION_COUNT = 2080
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


def jsonable(value: object) -> object:
    if isinstance(value, Q):
        return qstr(value)
    if hasattr(value, "jsonable"):
        return jsonable(value.jsonable())
    if is_dataclass(value):
        raise TypeError(f"dataclass lacks jsonable(): {type(value)}")
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"not JSON serializable: {type(value)}")


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
        str(HERE / "test_coupled_uncertainty.py"),
    ]
    completed = subprocess.run(
        command,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
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


def _clean_rectangle_audit(row: dict) -> dict:
    result = dict(row)
    result.pop("elapsed_seconds", None)
    result.pop("workers", None)
    return result


def _exact_rectangle_row(
    mode: str, allocation: tuple[int, int, int]
) -> dict:
    _initialize_worker(mode)
    return _audit_one(allocation)


def _classification_summary(result: dict) -> dict:
    candidate = result["candidate"]
    lower = result["candidate_exact_lower"]["risk"]
    upper = result["candidate_exact_upper"]["risk"]
    uniform_lower = result["uniform_exact_lower"]["risk"]
    uniform_upper = result["uniform_exact_upper"]["risk"]
    return {
        "allocation_universe": result["evaluated_allocations"],
        "policy_count": result["candidate_exact_upper"]["policy_count"],
        "rows_sha256": result["rows_sha256"],
        "optimum": list(candidate.allocation),
        "optimum_interval": [qstr(lower), qstr(upper)],
        "optimum_interval_width": qstr(upper - lower),
        "unique_certified": result["unique_certified"],
        "certified_unique_gap": qstr(
            result["certified_unique_gap"]
        ),
        "ambiguous_before_sharpening": result[
            "ambiguous_before_sharpening"
        ],
        "sharpened_allocations": [
            list(row["allocation"]) for row in result["sharpened"]
        ],
        "uniform": list(result["uniform"].allocation),
        "uniform_interval": [
            qstr(uniform_lower),
            qstr(uniform_upper),
        ],
        "relative_improvement_lower": float(
            result["relative_improvement_lower"]
        ),
        "exact_optimum_prior_lower": [
            qstr(value)
            for value in result["candidate_exact_lower"]["prior"]
        ],
        "exact_optimum_prior_upper": [
            qstr(value)
            for value in result["candidate_exact_upper"]["prior"]
        ],
    }


def _group_summary(result: dict) -> dict:
    candidate_allocation, candidate_lower, candidate_upper = result[
        "candidate"
    ]
    uniform_allocation, uniform_lower, uniform_upper = result["uniform"]
    return {
        "allocation_universe": result["evaluated_allocations"],
        "rows_sha256": result["rows_sha256"],
        "optimum": list(candidate_allocation),
        "optimum_interval": [
            qstr(candidate_lower),
            qstr(candidate_upper),
        ],
        "optimum_interval_width": qstr(
            candidate_upper - candidate_lower
        ),
        "unique_certified": result["unique_certified"],
        "certified_unique_gap": qstr(
            result["certified_unique_gap"]
        ),
        "uniform": list(uniform_allocation),
        "uniform_interval": [
            qstr(uniform_lower),
            qstr(uniform_upper),
        ],
        "relative_improvement_lower": float(
            result["relative_improvement_lower"]
        ),
    }


def build_scientific_payload(
    workers: int = WORKERS,
) -> tuple[dict, dict, dict]:
    classification = optimize_coupled_minimax_classification(
        TOTAL_BUDGET
    )
    group = optimize_coupled_root_group(TOTAL_BUDGET)

    coupled_rows = {
        "schema": "asmp9-v0.46-coupled-allocation-rows-v1",
        "total_budget": TOTAL_BUDGET,
        "classification": [
            row.jsonable() for row in classification["rows"]
        ],
        "root_group": [
            {
                "allocation": list(allocation),
                "lower": qstr(lower),
                "upper": qstr(upper),
            }
            for allocation, lower, upper in group["rows"]
        ],
    }

    rectangle_audits = {
        mode: _clean_rectangle_audit(
            audit_mode(mode, TOTAL_BUDGET, workers)
        )
        for mode in ("branch_classification", "root_group")
    }
    class_allocation = classification["candidate"].allocation
    group_allocation = group["candidate"][0]
    rectangle_rows = {
        "branch_classification_at_coupled_optimum": (
            _exact_rectangle_row(
                "branch_classification", class_allocation
            )
        ),
        "root_group_at_coupled_optimum": _exact_rectangle_row(
            "root_group", group_allocation
        ),
    }
    rectangle_payload = {
        "schema": "asmp9-v0.46-rectangle-audit-v1",
        "total_budget": TOTAL_BUDGET,
        "audits": rectangle_audits,
        "coupled_optimum_rows": rectangle_rows,
    }

    classification_summary = _classification_summary(classification)
    group_summary = _group_summary(group)
    product = jsonable(product_box_control())

    class_rectangle_opt = Q(
        rectangle_rows[
            "branch_classification_at_coupled_optimum"
        ]["exact_upper"]
    )
    group_rectangle_opt = Q(
        rectangle_rows[
            "root_group_at_coupled_optimum"
        ]["exact_upper"]
    )
    class_rectangle_uniform = Q(
        rectangle_audits["branch_classification"][
            "exact_uniform_upper"
        ]
    )
    group_rectangle_uniform = Q(
        rectangle_audits["root_group"]["exact_uniform_upper"]
    )
    class_coupled_opt_upper = Q(
        classification_summary["optimum_interval"][1]
    )
    group_coupled_opt_upper = Q(
        group_summary["optimum_interval"][1]
    )
    class_coupled_uniform_upper = Q(
        classification_summary["uniform_interval"][1]
    )
    group_coupled_uniform_upper = Q(
        group_summary["uniform_interval"][1]
    )

    exponential_checks = []
    for samples in range(1, TOTAL_BUDGET + 1):
        bounds = flip_probability_bounds(samples)
        exp_lower, exp_upper = exp_neg_fraction_bounds(bounds.kappa)
        exponential_checks.append(
            {
                "samples": samples,
                "exp_width": qstr(exp_upper - exp_lower),
                "probability_width": qstr(
                    bounds.upper - bounds.lower
                ),
                "exp_width_ok": (
                    exp_upper - exp_lower <= Q(1, 10**15)
                ),
                "probability_width_ok": (
                    bounds.upper - bounds.lower <= Q(1, 10**12)
                ),
            }
        )

    allocation_comparison = {
        "branch_classification": {
            "coupled": classification_summary["optimum"],
            "rectangular": rectangle_audits[
                "branch_classification"
            ]["exact_optima"],
            "changed": (
                rectangle_audits["branch_classification"][
                    "exact_optima"
                ]
                != [classification_summary["optimum"]]
            ),
        },
        "root_group": {
            "coupled": group_summary["optimum"],
            "rectangular": rectangle_audits["root_group"][
                "exact_optima"
            ],
            "changed": (
                rectangle_audits["root_group"]["exact_optima"]
                != [group_summary["optimum"]]
            ),
        },
    }

    scientific = {
        "total_budget": TOTAL_BUDGET,
        "query_order": ["root", "left", "right"],
        "allocation_universe_per_problem": len(
            positive_allocations(TOTAL_BUDGET, 3)
        ),
        "shared_flip_parameters": 3,
        "symbolic_policy_count": int(
            symbolic_classification_policies().shape[0]
        ),
        "coupled": {
            "branch_classification": classification_summary,
            "root_group": group_summary,
        },
        "rectangular": rectangle_payload,
        "strict_conservatism": {
            "branch_classification_optimum": (
                class_coupled_opt_upper < class_rectangle_opt
            ),
            "root_group_optimum": (
                group_coupled_opt_upper < group_rectangle_opt
            ),
            "branch_classification_uniform": (
                class_coupled_uniform_upper
                < class_rectangle_uniform
            ),
            "root_group_uniform": (
                group_coupled_uniform_upper
                < group_rectangle_uniform
            ),
            "gaps": {
                "branch_classification_optimum": qstr(
                    class_rectangle_opt - class_coupled_opt_upper
                ),
                "root_group_optimum": qstr(
                    group_rectangle_opt - group_coupled_opt_upper
                ),
                "branch_classification_uniform": qstr(
                    class_rectangle_uniform
                    - class_coupled_uniform_upper
                ),
                "root_group_uniform": qstr(
                    group_rectangle_uniform
                    - group_coupled_uniform_upper
                ),
            },
        },
        "allocation_comparison": allocation_comparison,
        "product_control": product,
        "exponential_checks": exponential_checks,
        "coupled_rows_sha256": sha256_bytes(
            canonical_json_bytes(coupled_rows)
        ),
        "rectangle_payload_sha256": sha256_bytes(
            canonical_json_bytes(rectangle_payload)
        ),
    }
    return scientific, coupled_rows, rectangle_payload


def scientific_gates(scientific: dict) -> dict[str, bool]:
    classification = scientific["coupled"]["branch_classification"]
    group = scientific["coupled"]["root_group"]
    rectangle = scientific["rectangular"]["audits"]
    comparison = scientific["allocation_comparison"]
    return {
        "U0": (
            scientific["total_budget"] == 66
            and scientific["query_order"]
            == ["root", "left", "right"]
            and scientific["allocation_universe_per_problem"]
            == ALLOCATION_COUNT
            and classification["allocation_universe"]
            == ALLOCATION_COUNT
            and group["allocation_universe"] == ALLOCATION_COUNT
        ),
        "E0": scientific["symbolic_policy_count"] == 3748,
        "X0": all(
            row["exp_width_ok"] and row["probability_width_ok"]
            for row in scientific["exponential_checks"]
        ),
        "B0": (
            classification["unique_certified"]
            and Q(classification["certified_unique_gap"]) > 0
            and group["unique_certified"]
            and Q(group["certified_unique_gap"]) > 0
        ),
        "C0": classification["optimum"] == [28, 19, 19],
        "G0": group["optimum"] == [64, 1, 1],
        "R0": (
            rectangle["branch_classification"]["exact_optima"]
            == [[28, 19, 19]]
            and rectangle["root_group"]["exact_optima"]
            == [[64, 1, 1]]
        ),
        "K0": all(scientific["strict_conservatism"].values())
        if all(
            isinstance(value, bool)
            for value in scientific["strict_conservatism"].values()
        )
        else all(
            scientific["strict_conservatism"][name]
            for name in (
                "branch_classification_optimum",
                "root_group_optimum",
                "branch_classification_uniform",
                "root_group_uniform",
            )
        ),
        "O0": (
            not comparison["branch_classification"]["changed"]
            and not comparison["root_group"]["changed"]
        ),
        "PC0": (
            scientific["product_control"]["vertices"] == 16
            and scientific["product_control"]["match"]
        ),
    }


def total_status(gates: dict[str, bool]) -> str:
    instrument = ("P0", "S0", "U0", "E0", "X0", "B0", "PC0")
    if not all(gates.get(name, False) for name in instrument):
        return "invalid_coupled_instrument"
    if all(gates.values()):
        return (
            "coupled_image_conservatism_established_"
            "allocation_unchanged"
        )
    return "coupled_prediction_not_established"


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
        default=HERE / "registration_v0_46.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE / "artifacts_v0_46",
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
        scientific, coupled_rows, rectangle_payload = (
            build_scientific_payload(WORKERS)
        )
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
    output_dir = args.output_dir.resolve()
    compare_or_write(
        output_dir / "coupled_rows_v0_46.json",
        canonical_json_bytes(coupled_rows),
    )
    compare_or_write(
        output_dir / "rectangle_audit_v0_46.json",
        canonical_json_bytes(rectangle_payload),
    )
    compare_or_write(
        output_dir / "result_v0_46.json",
        canonical_json_bytes(payload),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(payload["status"] == "invalid_coupled_instrument")


if __name__ == "__main__":
    main()

