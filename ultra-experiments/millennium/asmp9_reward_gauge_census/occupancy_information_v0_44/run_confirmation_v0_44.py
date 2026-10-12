"""Execute the sealed deterministic ASMP-9 v0.44 confirmation."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
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

from occupancy_information import (  # noqa: E402
    enumerate_policy_envelopes,
    information_radii,
    policy_specific_interval,
    qstr,
    query_chi_square_costs,
    robust_directed_deficiency_interval,
    uniform_information_interval,
)
from sequential_access import (  # noqa: E402
    ADAPTIVITY_GAP_QUERIES,
    QueryChannel,
    adaptive_upper_generators,
    binary_group_problem,
    classification_problem,
    directed_upper_deficiency,
)


PROTOCOL_ID = "asmp9-policy-specific-information-v0.44"
VERSION = "0.44"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def perturbed_queries(eta: Q) -> tuple[QueryChannel, ...]:
    result = []
    for query in ADAPTIVITY_GAP_QUERIES:
        if query.name == "root":
            result.append(query)
            continue
        result.append(
            QueryChannel(
                query.name,
                tuple(
                    (
                        (Q(1) - eta, eta)
                        if row[0] == 1
                        else (eta, Q(1) - eta)
                    )
                    for row in query.rows
                ),
            )
        )
    return tuple(result)


def problem_fixture(eta: Q, problem):
    center = ADAPTIVITY_GAP_QUERIES
    actual = perturbed_queries(eta)
    costs = query_chi_square_costs(center, actual)
    envelopes = enumerate_policy_envelopes(
        center, problem, 2, costs
    )
    reference = (tuple([Q(0)] * problem.target_count),)
    return center, actual, costs, envelopes, reference


def center_rows() -> list[dict]:
    rows = []
    for problem in (
        classification_problem(4),
        binary_group_problem(
            "root_group", (0, 0, 1, 1), false_positive_cost=Q(1)
        ),
    ):
        center, _, costs, envelopes, _ = problem_fixture(
            Q(1, 20), problem
        )
        compiler = tuple(
            adaptive_upper_generators(center, problem, 2)
        )
        envelope_risks = tuple(
            sorted({envelope.risk for envelope in envelopes})
        )
        left = directed_upper_deficiency(
            envelope_risks, compiler
        ).epsilon
        right = directed_upper_deficiency(
            compiler, envelope_risks
        ).epsilon
        supremum = tuple(
            max(envelope.information[target] for envelope in envelopes)
            for target in range(problem.target_count)
        )
        expected = tuple(
            Q(2)
            * max(
                costs[(target, query.name)] for query in center
            )
            for target in range(problem.target_count)
        )
        rows.append(
            {
                "problem": problem.name,
                "envelopes": len(envelopes),
                "unique_risks": len(envelope_risks),
                "compiler_generators": len(compiler),
                "envelopes_to_compiler_deficiency": qstr(left),
                "compiler_to_envelopes_deficiency": qstr(right),
                "center_equivalent": left == right == 0,
                "information_supremum": [
                    qstr(value) for value in supremum
                ],
                "h_max_information": [
                    qstr(value) for value in expected
                ],
                "supremum_collapse_exact": supremum == expected,
            }
        )
    return rows


def decision_rows(problem) -> list[dict]:
    rows = []
    for eta in (Q(1, 100), Q(1, 50), Q(1, 20), Q(1, 10)):
        center, actual, costs, envelopes, reference = problem_fixture(
            eta, problem
        )
        policy = policy_specific_interval(
            envelopes, problem, reference
        )
        uniform = uniform_information_interval(
            envelopes, problem, center, costs, 2, reference
        )
        actual_deficiency = directed_upper_deficiency(
            adaptive_upper_generators(actual, problem, 2),
            reference,
        ).epsilon
        zero_risk_information = min(
            (
                max(envelope.information)
                for envelope in envelopes
                if all(value == 0 for value in envelope.risk)
            ),
            default=None,
        )
        rows.append(
            {
                "problem": problem.name,
                "eta": qstr(eta),
                "chi_square_cost": qstr(
                    costs[(0, "left")]
                ),
                "envelopes": len(envelopes),
                "actual_deficiency": qstr(actual_deficiency),
                "policy_specific": policy.jsonable(),
                "uniform": uniform.jsonable(),
                "zero_risk_policy_max_information": (
                    qstr(zero_risk_information)
                    if zero_risk_information is not None
                    else None
                ),
                "actual_contained": (
                    policy.lower <= actual_deficiency <= policy.upper
                ),
                "strictly_sharper": policy.upper < uniform.upper,
            }
        )
    return rows


def selected_source_box_rows() -> list[dict]:
    source = ((Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1, 4)))
    radii = ((Q(1, 20), Q(1, 10)), (Q(1, 10), Q(1, 20)))
    reference = ((Q(0), Q(0)),)
    zero = ((Q(0), Q(0)),)
    interval = robust_directed_deficiency_interval(
        source, radii, reference, zero
    )
    patterns = (
        (-1, -1, -1, -1),
        (-1, -1, 1, 1),
        (-1, 1, -1, 1),
        (-1, 1, 1, -1),
        (1, -1, -1, 1),
        (1, -1, 1, -1),
        (1, 1, -1, -1),
        (1, 1, 1, 1),
    )
    rows = []
    for signs in patterns:
        actual = (
            (
                source[0][0] + signs[0] * radii[0][0],
                source[0][1] + signs[1] * radii[0][1],
            ),
            (
                source[1][0] + signs[2] * radii[1][0],
                source[1][1] + signs[3] * radii[1][1],
            ),
        )
        deficiency = directed_upper_deficiency(
            actual, reference
        ).epsilon
        rows.append(
            {
                "signs": list(signs),
                "deficiency": qstr(deficiency),
                "interval": interval.jsonable(),
                "contained": interval.lower <= deficiency <= interval.upper,
            }
        )
    return rows


def source_reference_box_rows() -> list[dict]:
    source = ((Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1, 4)))
    source_radii = (
        (Q(1, 20), Q(1, 10)),
        (Q(1, 10), Q(1, 20)),
    )
    reference = ((Q(1, 20), Q(1, 20)),)
    reference_radii = ((Q(1, 100), Q(1, 50)),)
    interval = robust_directed_deficiency_interval(
        source, source_radii, reference, reference_radii
    )
    rows = []
    for mask in range(64):
        signs = tuple(
            1 if mask & (1 << bit) else -1 for bit in range(6)
        )
        actual_source = (
            (
                source[0][0] + signs[0] * source_radii[0][0],
                source[0][1] + signs[1] * source_radii[0][1],
            ),
            (
                source[1][0] + signs[2] * source_radii[1][0],
                source[1][1] + signs[3] * source_radii[1][1],
            ),
        )
        actual_reference = (
            (
                reference[0][0]
                + signs[4] * reference_radii[0][0],
                reference[0][1]
                + signs[5] * reference_radii[0][1],
            ),
        )
        deficiency = directed_upper_deficiency(
            actual_source, actual_reference
        ).epsilon
        rows.append(
            {
                "mask": mask,
                "signs": list(signs),
                "deficiency": qstr(deficiency),
                "interval": interval.jsonable(),
                "contained": interval.lower <= deficiency <= interval.upper,
            }
        )
    return rows


def query_budget_row() -> dict:
    problem = classification_problem(4)
    center = (ADAPTIVITY_GAP_QUERIES[1],)
    actual = (perturbed_queries(Q(1, 20))[1],)
    costs = query_chi_square_costs(center, actual)
    repeatable = enumerate_policy_envelopes(
        center, problem, 2, costs
    )
    once = enumerate_policy_envelopes(
        center,
        problem,
        2,
        costs,
        query_budgets={"left": 1},
    )
    repeatable_max = max(
        max(row.information) for row in repeatable
    )
    once_max = max(max(row.information) for row in once)
    return {
        "repeatable_max_information": qstr(repeatable_max),
        "one_use_max_information": qstr(once_max),
        "expected_repeatable": "2/19",
        "expected_one_use": "1/19",
        "exact_match": (
            repeatable_max == Q(2, 19)
            and once_max == Q(1, 19)
        ),
    }


def build_scientific_payload() -> dict:
    return {
        "center_controls": center_rows(),
        "classification": decision_rows(classification_problem(4)),
        "root_group": decision_rows(
            binary_group_problem(
                "root_group",
                (0, 0, 1, 1),
                false_positive_cost=Q(1),
            )
        ),
        "selected_source_box_vertices": selected_source_box_rows(),
        "source_reference_box_vertices": source_reference_box_rows(),
        "query_budget": query_budget_row(),
    }


def scientific_gates(scientific: dict) -> dict[str, bool]:
    center = scientific["center_controls"]
    classification = scientific["classification"]
    group = scientific["root_group"]
    source_box = scientific["selected_source_box_vertices"]
    both_box = scientific["source_reference_box_vertices"]
    budget = scientific["query_budget"]
    return {
        "C0": len(center) == 2
        and all(row["center_equivalent"] for row in center),
        "X0": len(center) == 2
        and all(row["supremum_collapse_exact"] for row in center),
        "B0": (
            len(source_box) == 8
            and len(both_box) == 64
            and all(row["contained"] for row in source_box + both_box)
        ),
        "Q0": budget["exact_match"],
        "I0": len(classification) == 4
        and all(
            row["actual_contained"] and row["strictly_sharper"]
            for row in classification
        ),
        "D0": len(group) == 4
        and all(
            row["actual_deficiency"] == "0"
            and row["policy_specific"]["lower"] == "0"
            and row["policy_specific"]["upper"] == "0"
            and Q(row["uniform"]["upper"]) > 0
            for row in group
        ),
        "R0": (
            len(center) == 2
            and len(classification) == 4
            and len(group) == 4
            and len(source_box) == 8
            and len(both_box) == 64
            and isinstance(budget, dict)
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
    completed = subprocess.run(
        registration["test_command"],
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
        "command": registration["test_command"],
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
        return "policy_specific_information_containment_established"
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
        default=HERE / "registration_v0_44.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "artifacts_v0_44" / "RESULT_v0_44.json",
    )
    args = parser.parse_args()
    payload = execute(
        args.registration.resolve(), args.output.resolve()
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "gates": payload["gates"],
                "output": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
