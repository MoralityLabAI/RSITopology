"""Execute the sealed ASMP-9 v0.48 evidence-ordering confirmation."""

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
V46 = HERE.parent / "coupled_uncertainty_v0_46"
V47 = HERE.parent / "sharp_atom_modulus_v0_47"
for path in (HERE, V46, V47):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from coupled_uncertainty import (  # noqa: E402
    qstr,
    symbolic_classification_policies,
)
from ordering_modulus import (  # noqa: E402
    buehler_subset_bounds,
    coverage_by_parameter,
    dynamic_cross_audit,
    dynamic_ordering_census,
    experiment_rows,
    ordered_bound_vector,
    prefix_probability_tables,
    uniform_parameter_mixture,
)
from sharp_atom_modulus import (  # noqa: E402
    classification_risks,
    parameter_grid,
)


PROTOCOL_ID = "asmp9-decision-dependent-ordering-v0.48"
VERSION = "0.48"
WORKERS = 4
EXPECTED_TESTS = 13
ALPHA = Q(1, 10)
ALLOCATION = (2, 1, 1)
LEVELS = (Q(0), Q(3, 20), Q(7, 20))
BURNED_ALPHA = Q(1, 10)
BURNED_ALLOCATION = (1, 1, 1)
BURNED_LEVELS = (Q(0), Q(1, 5), Q(2, 5))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def validate_source_hashes(
    registration: dict,
) -> tuple[bool, list[dict]]:
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
        str(HERE / "test_ordering_modulus.py"),
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


def _parameter_row(parameter) -> list[str]:
    return [qstr(value) for value in parameter]


def build_fixture(
    levels: tuple[Q, ...],
    allocation: tuple[int, int, int],
    alpha: Q,
    risk_table: dict,
) -> tuple[dict, dict, dict]:
    parameters = parameter_grid(levels)
    risks = {
        parameter: risk_table[parameter] for parameter in parameters
    }
    root_risks = {
        parameter: parameter[0] for parameter in parameters
    }
    outcomes, probabilities = experiment_rows(
        parameters, allocation
    )
    reference = uniform_parameter_mixture(probabilities)
    subsets = prefix_probability_tables(probabilities)
    class_bounds = buehler_subset_bounds(risks, subsets, alpha)
    root_bounds = buehler_subset_bounds(
        root_risks, subsets, alpha
    )
    class_census = dynamic_ordering_census(
        class_bounds, reference
    )
    root_census = dynamic_ordering_census(root_bounds, reference)
    cross = dynamic_cross_audit(
        class_bounds, root_bounds, reference
    )

    class_reported = ordered_bound_vector(
        class_census.lexicographic_optimizer, class_bounds
    )
    root_reported = ordered_bound_vector(
        root_census.lexicographic_optimizer, root_bounds
    )
    class_coverage = coverage_by_parameter(
        risks, probabilities, class_reported
    )
    root_coverage = coverage_by_parameter(
        root_risks, probabilities, root_reported
    )
    zero = tuple([0] * len(allocation))
    zero_index = outcomes.index(zero)
    singleton_mask = 1 << zero_index
    class_atom = max(
        risks[parameter]
        for parameter in parameters
        if probabilities[parameter][zero_index] > alpha
    )
    root_atom = max(
        root_risks[parameter]
        for parameter in parameters
        if probabilities[parameter][zero_index] > alpha
    )

    summary = {
        "levels": [qstr(value) for value in levels],
        "allocation": list(allocation),
        "alpha": qstr(alpha),
        "parameter_count": len(parameters),
        "outcome_count": len(outcomes),
        "implicit_order_count": class_census.order_count,
        "outcomes": [list(outcome) for outcome in outcomes],
        "reference_weights": [qstr(value) for value in reference],
        "reference_sums_to_one": sum(reference, Q(0)) == 1,
        "experiment_rows_sum_to_one": all(
            sum(row, Q(0)) == 1 for row in probabilities.values()
        ),
        "classification_risk_range": [
            qstr(min(risks.values())),
            qstr(max(risks.values())),
        ],
        "root_risk_range": [
            qstr(min(root_risks.values())),
            qstr(max(root_risks.values())),
        ],
        "classification_bound_value_count": len(set(class_bounds)),
        "root_bound_value_count": len(set(root_bounds)),
        "classification": class_census.jsonable(outcomes),
        "root_group": root_census.jsonable(outcomes),
        "cross_audit": cross,
        "coverage": {
            "classification_minimum": qstr(
                min(class_coverage.values())
            ),
            "root_group_minimum": qstr(
                min(root_coverage.values())
            ),
        },
        "all_zero_control": {
            "outcome_index": zero_index,
            "classification_singleton_bound": qstr(
                class_bounds[singleton_mask]
            ),
            "classification_direct_atom": qstr(class_atom),
            "classification_match": (
                class_bounds[singleton_mask] == class_atom
            ),
            "root_singleton_bound": qstr(
                root_bounds[singleton_mask]
            ),
            "root_direct_atom": qstr(root_atom),
            "root_match": root_bounds[singleton_mask] == root_atom,
        },
    }
    experiment_payload = {
        "schema": "asmp9-v0.48-experiment-rows-v1",
        "levels": summary["levels"],
        "allocation": list(allocation),
        "outcomes": summary["outcomes"],
        "rows": [
            {
                "parameter": _parameter_row(parameter),
                "probabilities": [
                    qstr(value) for value in probabilities[parameter]
                ],
                "classification_risk": qstr(risks[parameter]),
                "root_group_risk": qstr(root_risks[parameter]),
            }
            for parameter in parameters
        ],
    }
    subset_payload = {
        "schema": "asmp9-v0.48-subset-bounds-v1",
        "classification": [qstr(value) for value in class_bounds],
        "root_group": [qstr(value) for value in root_bounds],
    }
    return summary, experiment_payload, subset_payload


def build_scientific_payload(
    workers: int = WORKERS,
) -> tuple[dict, dict, dict]:
    primary_parameters = set(parameter_grid(LEVELS))
    burned_parameters = set(parameter_grid(BURNED_LEVELS))
    risk_table = classification_risks(
        primary_parameters.union(burned_parameters),
        workers=workers,
    )
    primary, experiment_payload, subset_payload = build_fixture(
        LEVELS, ALLOCATION, ALPHA, risk_table
    )
    burned, _, _ = build_fixture(
        BURNED_LEVELS,
        BURNED_ALLOCATION,
        BURNED_ALPHA,
        risk_table,
    )
    scientific = {
        "primary": primary,
        "burned_replay": {
            "classification_optimum": burned["classification"][
                "optimum"
            ],
            "classification_optimizer_count": burned[
                "classification"
            ]["optimizer_count"],
            "root_optimum": burned["root_group"]["optimum"],
            "root_optimizer_count": burned["root_group"][
                "optimizer_count"
            ],
            "cross_audit": burned["cross_audit"],
        },
        "symbolic_policy_count": int(
            symbolic_classification_policies().shape[0]
        ),
        "exact_risk_points": len(risk_table),
        "experiment_payload_sha256": sha256_bytes(
            canonical_json_bytes(experiment_payload)
        ),
        "subset_payload_sha256": sha256_bytes(
            canonical_json_bytes(subset_payload)
        ),
    }
    return scientific, experiment_payload, subset_payload


def scientific_gates(scientific: dict) -> dict[str, bool]:
    primary = scientific["primary"]
    replay = scientific["burned_replay"]
    cross = primary["cross_audit"]
    return {
        "U0": (
            primary["levels"] == ["0", "3/20", "7/20"]
            and primary["allocation"] == [2, 1, 1]
            and primary["alpha"] == "1/10"
            and primary["parameter_count"] == 27
            and primary["outcome_count"] == 12
            and primary["implicit_order_count"] == 479001600
            and primary["reference_sums_to_one"]
            and primary["experiment_rows_sum_to_one"]
        ),
        "E0": scientific["symbolic_policy_count"] == 3748,
        "D0": (
            replay["classification_optimum"] == "1984/3125"
            and replay["classification_optimizer_count"] == 5040
            and replay["root_optimum"] == "246/625"
            and replay["root_optimizer_count"] == 5040
            and replay["cross_audit"]["common_optimizer_count"] == 0
            and replay["cross_audit"]["first_cross_regret"]
            == "4/3125"
            and replay["cross_audit"]["second_cross_regret"]
            == "2/625"
        ),
        "L0": (
            primary["classification_risk_range"][0]
            != primary["classification_risk_range"][1]
            and primary["root_risk_range"][0]
            != primary["root_risk_range"][1]
            and primary["classification_bound_value_count"] > 1
            and primary["root_bound_value_count"] > 1
        ),
        "C0": (
            Q(primary["coverage"]["classification_minimum"])
            >= Q(9, 10)
            and Q(primary["coverage"]["root_group_minimum"])
            >= Q(9, 10)
        ),
        "A0": (
            primary["all_zero_control"]["classification_match"]
            and primary["all_zero_control"]["root_match"]
        ),
        "X0": (
            cross["common_optimizer_count"] == 0
            and Q(cross["first_cross_regret"]) > 0
            and Q(cross["second_cross_regret"]) > 0
        ),
    }


def total_status(gates: dict[str, bool]) -> str:
    instrument = ("P0", "S0", "U0", "E0", "D0", "L0", "C0", "A0")
    if not all(gates.get(name, False) for name in instrument):
        return "invalid_ordering_instrument"
    if all(gates.values()):
        return "decision_dependent_evidence_ordering_established"
    return "decision_dependent_ordering_not_established"


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
        default=HERE / "registration_v0_48.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE / "artifacts_v0_48",
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
        scientific, experiment_payload, subset_payload = (
            build_scientific_payload(WORKERS)
        )
    elapsed = time.perf_counter() - started
    resource = {
        "elapsed_seconds": elapsed,
        "peak_aggregate_working_set_bytes": monitor.peak,
        "worker_processes": WORKERS,
        "seconds_ceiling": registration["resource_ceiling"]["seconds"],
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
        output_dir / "experiment_rows_v0_48.json",
        canonical_json_bytes(experiment_payload),
    )
    compare_or_write(
        output_dir / "subset_bounds_v0_48.json",
        canonical_json_bytes(subset_payload),
    )
    compare_or_write(
        output_dir / "result_v0_48.json",
        canonical_json_bytes(payload),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(payload["status"] == "invalid_ordering_instrument")


if __name__ == "__main__":
    main()
