"""Execute the sealed ASMP-9 v0.47 sharp atom-modulus confirmation."""

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
V46 = HERE.parent / "coupled_uncertainty_v0_46"
for path in (HERE, V45, V46):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from audit_formula_universe import (  # noqa: E402
    _audit_one,
    _initialize_worker,
)
from coupled_uncertainty import (  # noqa: E402
    qstr,
    symbolic_classification_policies,
)
from sharp_atom_modulus import (  # noqa: E402
    all_zero_probability,
    boundary_parameters,
    classification_risks,
    mandatory_atom_region,
    method_of_types_coupled_upper,
    parameter_grid,
    root_group_risk_table,
    sharp_atom_modulus,
    total_error_cdf,
)


PROTOCOL_ID = "asmp9-sharp-atom-modulus-v0.47"
VERSION = "0.47"
ALPHA = Q(1, 20)
TOTAL_BUDGET = 72
WORKERS = 4
EXPECTED_TESTS = 15
LEVELS = (
    Q(0),
    Q(1, 50),
    Q(1, 25),
    Q(1, 20),
    Q(3, 50),
    Q(2, 25),
    Q(1, 10),
    Q(3, 25),
    Q(13, 100),
    Q(7, 50),
    Q(3, 20),
)
CLASS_DIRECTED = (30, 21, 21)
ROOT_DIRECTED = (70, 1, 1)
UNIFORM = (24, 24, 24)
EXPECTED_MANDATORY_COUNTS = {
    CLASS_DIRECTED: 113,
    ROOT_DIRECTED: 281,
    UNIFORM: 111,
}
CONTROL_PARAMETERS = (
    (Q(1, 10), Q(0), Q(0)),
    (Q(1, 10), Q(1, 10), Q(1, 10)),
)


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
        str(HERE / "test_sharp_atom_modulus.py"),
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


def _parameter_text(parameter: tuple[Q, Q, Q]) -> str:
    return ",".join(qstr(value) for value in parameter)


def _allocation_key(allocation: tuple[int, int, int]) -> str:
    return ",".join(str(value) for value in allocation)


def _rectangle_rows() -> dict:
    result = {}
    for mode, allocations in (
        ("branch_classification", (CLASS_DIRECTED, UNIFORM)),
        ("root_group", (ROOT_DIRECTED, UNIFORM)),
    ):
        _initialize_worker(mode)
        result[mode] = {
            _allocation_key(allocation): _audit_one(allocation)
            for allocation in allocations
        }
    return result


def _modulus_payload(
    modulus,
    coupled_upper: Q,
    rectangle_upper: Q,
) -> dict:
    payload = modulus.jsonable()
    payload["method_of_types_coupled_upper"] = qstr(coupled_upper)
    payload["rectangle_upper"] = qstr(rectangle_upper)
    payload["coupled_minus_sharp"] = qstr(
        coupled_upper - modulus.upper
    )
    payload["rectangle_minus_coupled"] = qstr(
        rectangle_upper - coupled_upper
    )
    return payload


def build_scientific_payload(
    workers: int = WORKERS,
) -> tuple[dict, dict, dict]:
    parameters = parameter_grid(LEVELS)
    mandatory_by_allocation = {
        allocation: mandatory_atom_region(
            parameters, allocation, ALPHA
        )
        for allocation in (CLASS_DIRECTED, ROOT_DIRECTED, UNIFORM)
    }
    classification_parameters = set(
        mandatory_by_allocation[CLASS_DIRECTED]
    )
    classification_parameters.update(
        mandatory_by_allocation[UNIFORM]
    )
    classification_parameters.update(CONTROL_PARAMETERS)
    class_risks = classification_risks(
        classification_parameters, workers=workers
    )
    root_risks = root_group_risk_table(LEVELS)

    class_directed = sharp_atom_modulus(
        class_risks,
        CLASS_DIRECTED,
        ALPHA,
        parameter_universe=parameters,
    )
    class_uniform = sharp_atom_modulus(
        class_risks,
        UNIFORM,
        ALPHA,
        parameter_universe=parameters,
    )
    root_directed = sharp_atom_modulus(
        root_risks,
        ROOT_DIRECTED,
        ALPHA,
        parameter_universe=parameters,
    )
    root_uniform = sharp_atom_modulus(
        root_risks,
        UNIFORM,
        ALPHA,
        parameter_universe=parameters,
    )

    rectangles = _rectangle_rows()
    coupled = {
        "branch_classification": {
            allocation: method_of_types_coupled_upper(
                allocation, "branch_classification"
            )
            for allocation in (CLASS_DIRECTED, UNIFORM)
        },
        "root_group": {
            allocation: method_of_types_coupled_upper(
                allocation, "root_group"
            )
            for allocation in (ROOT_DIRECTED, UNIFORM)
        },
    }

    moduli = {
        "branch_classification": {
            _allocation_key(CLASS_DIRECTED): _modulus_payload(
                class_directed,
                coupled["branch_classification"][CLASS_DIRECTED],
                Q(
                    rectangles["branch_classification"][
                        _allocation_key(CLASS_DIRECTED)
                    ]["exact_upper"]
                ),
            ),
            _allocation_key(UNIFORM): _modulus_payload(
                class_uniform,
                coupled["branch_classification"][UNIFORM],
                Q(
                    rectangles["branch_classification"][
                        _allocation_key(UNIFORM)
                    ]["exact_upper"]
                ),
            ),
        },
        "root_group": {
            _allocation_key(ROOT_DIRECTED): _modulus_payload(
                root_directed,
                coupled["root_group"][ROOT_DIRECTED],
                Q(
                    rectangles["root_group"][
                        _allocation_key(ROOT_DIRECTED)
                    ]["exact_upper"]
                ),
            ),
            _allocation_key(UNIFORM): _modulus_payload(
                root_uniform,
                coupled["root_group"][UNIFORM],
                Q(
                    rectangles["root_group"][
                        _allocation_key(UNIFORM)
                    ]["exact_upper"]
                ),
            ),
        },
    }

    boundaries = {
        _allocation_key(allocation): len(
            boundary_parameters(parameters, allocation, ALPHA)
        )
        for allocation in (CLASS_DIRECTED, ROOT_DIRECTED, UNIFORM)
    }
    cdf_checks = []
    for mode, rows in (
        (
            "branch_classification",
            (
                (CLASS_DIRECTED, class_directed),
                (UNIFORM, class_uniform),
            ),
        ),
        (
            "root_group",
            (
                (ROOT_DIRECTED, root_directed),
                (UNIFORM, root_uniform),
            ),
        ),
    ):
        for allocation, modulus in rows:
            for witness in modulus.witnesses:
                cdf = total_error_cdf(witness, allocation)
                cdf_checks.append(
                    {
                        "mode": mode,
                        "allocation": list(allocation),
                        "parameter": [
                            qstr(value) for value in witness
                        ],
                        "cdf_at_zero": qstr(cdf[0]),
                        "atom_probability": qstr(
                            all_zero_probability(
                                witness, allocation
                            )
                        ),
                        "cdf_terminal": qstr(cdf[-1]),
                        "minimum_atom_match": (
                            cdf[0]
                            == all_zero_probability(
                                witness, allocation
                            )
                        ),
                    }
                )

    controls = {
        "radius_insufficiency": {
            "common_linf_radius": "1/10",
            "root_only_parameter": ["1/10", "0", "0"],
            "root_only_risk": qstr(
                class_risks[CONTROL_PARAMETERS[0]]
            ),
            "symmetric_parameter": ["1/10", "1/10", "1/10"],
            "symmetric_risk": qstr(
                class_risks[CONTROL_PARAMETERS[1]]
            ),
        },
        "analytic_root": {
            "all_witnesses_equal_root_coordinate": all(
                root_risks[witness] == witness[0]
                for modulus in (root_directed, root_uniform)
                for witness in modulus.witnesses
            )
        },
        "total_error_cdf": cdf_checks,
    }

    risk_rows = {
        "schema": "asmp9-v0.47-exact-risk-rows-v1",
        "classification": [
            {
                "parameter": [
                    qstr(value) for value in parameter
                ],
                "risk": qstr(risk),
            }
            for parameter, risk in sorted(class_risks.items())
        ],
        "root_group_formula": "risk(p)=p_root",
        "parameter_universe": len(parameters),
    }
    comparator_rows = {
        "schema": "asmp9-v0.47-comparator-rows-v1",
        "rectangular": rectangles,
        "method_of_types_coupled": {
            mode: {
                _allocation_key(allocation): qstr(value)
                for allocation, value in rows.items()
            }
            for mode, rows in coupled.items()
        },
    }
    scientific = {
        "total_budget": TOTAL_BUDGET,
        "alpha": qstr(ALPHA),
        "query_order": ["root", "left", "right"],
        "levels": [qstr(value) for value in LEVELS],
        "parameter_count": len(parameters),
        "symbolic_policy_count": int(
            symbolic_classification_policies().shape[0]
        ),
        "classification_risk_points": len(class_risks),
        "mandatory_counts": {
            _allocation_key(allocation): len(rows)
            for allocation, rows in mandatory_by_allocation.items()
        },
        "boundary_equalities": boundaries,
        "moduli": moduli,
        "controls": controls,
        "risk_rows_sha256": sha256_bytes(
            canonical_json_bytes(risk_rows)
        ),
        "comparator_rows_sha256": sha256_bytes(
            canonical_json_bytes(comparator_rows)
        ),
    }
    return scientific, risk_rows, comparator_rows


def scientific_gates(scientific: dict) -> dict[str, bool]:
    class_rows = scientific["moduli"]["branch_classification"]
    root_rows = scientific["moduli"]["root_group"]
    class_directed = class_rows[_allocation_key(CLASS_DIRECTED)]
    class_uniform = class_rows[_allocation_key(UNIFORM)]
    root_directed = root_rows[_allocation_key(ROOT_DIRECTED)]
    root_uniform = root_rows[_allocation_key(UNIFORM)]
    rows = (
        class_directed,
        class_uniform,
        root_directed,
        root_uniform,
    )
    return {
        "U0": (
            scientific["total_budget"] == TOTAL_BUDGET
            and scientific["alpha"] == qstr(ALPHA)
            and scientific["query_order"]
            == ["root", "left", "right"]
            and scientific["levels"]
            == [qstr(value) for value in LEVELS]
            and scientific["parameter_count"] == 1331
            and scientific["mandatory_counts"]
            == {
                _allocation_key(allocation): count
                for allocation, count in EXPECTED_MANDATORY_COUNTS.items()
            }
        ),
        "E0": scientific["symbolic_policy_count"] == 3748,
        "B0": all(
            count == 0
            for count in scientific["boundary_equalities"].values()
        ),
        "C0": all(
            row["matched"]
            and Q(row["lower"]) == Q(row["upper"])
            and Q(row["minimum_spike_coverage"]) >= Q(19, 20)
            for row in rows
        ),
        "L0": all(Q(row["upper"]) > 0 for row in rows),
        "A0": (
            Q(class_uniform["upper"]) < Q(class_directed["upper"])
            and Q(root_directed["upper"]) < Q(root_uniform["upper"])
        ),
        "K0": all(
            Q(row["method_of_types_coupled_upper"])
            > Q(row["upper"])
            for row in rows
        ),
        "R0": all(
            Q(row["rectangle_upper"])
            > Q(row["method_of_types_coupled_upper"])
            for row in rows
        ),
        "N0": (
            scientific["controls"]["radius_insufficiency"][
                "root_only_risk"
            ]
            == "1/10"
            and scientific["controls"]["radius_insufficiency"][
                "symmetric_risk"
            ]
            == "19/100"
        ),
        "T0": (
            scientific["controls"]["analytic_root"][
                "all_witnesses_equal_root_coordinate"
            ]
            and all(
                row["minimum_atom_match"]
                and row["cdf_terminal"] == "1"
                for row in scientific["controls"]["total_error_cdf"]
            )
        ),
    }


def total_status(gates: dict[str, bool]) -> str:
    instrument = ("P0", "S0", "U0", "E0", "B0", "C0", "N0", "T0")
    if not all(gates.get(name, False) for name in instrument):
        return "invalid_sharp_atom_instrument"
    if all(gates.values()):
        return "sharp_atom_modulus_established_allocation_ranking_changed"
    return "sharp_atom_prediction_not_established"


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
        default=HERE / "registration_v0_47.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE / "artifacts_v0_47",
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
        scientific, risk_rows, comparator_rows = (
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
        output_dir / "exact_risk_rows_v0_47.json",
        canonical_json_bytes(risk_rows),
    )
    compare_or_write(
        output_dir / "comparator_rows_v0_47.json",
        canonical_json_bytes(comparator_rows),
    )
    compare_or_write(
        output_dir / "result_v0_47.json",
        canonical_json_bytes(payload),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(
        payload["status"] == "invalid_sharp_atom_instrument"
    )


if __name__ == "__main__":
    main()
