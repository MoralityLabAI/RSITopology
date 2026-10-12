"""Execute the prospectively registered ASMP-9 v0.37 census."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from run_development import run_grid


Q = Fraction
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRATION_SCHEMA = "asmp9_stochastic_experiment_registration_v0_37"
RESULT_SCHEMA = "asmp9_stochastic_experiment_result_v0_37"
CONFIRMATION_GRID = (Q(1, 4), Q(1, 3), Q(2, 3), Q(3, 4))


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (REPO / path).resolve()


def load_registration(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != REGISTRATION_SCHEMA:
        raise ValueError("unexpected registration schema")
    if (
        payload.get("status") != "registered_not_run"
        or payload.get("outcomes_consumed") is not False
    ):
        raise ValueError("registration is not prereveal")
    expected = str(payload["registration_content_sha256"])
    actual = hashlib.sha256(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "registration_content_sha256"
            }
        )
    ).hexdigest()
    if actual != expected:
        raise ValueError("registration content hash mismatch")
    for group_name in ("implementation", "documents"):
        for name, item in payload[group_name].items():
            candidate = resolve_path(str(item["path"]))
            if not candidate.is_file():
                raise FileNotFoundError(candidate)
            if sha256_file(candidate) != str(item["sha256"]):
                raise ValueError(
                    f"registered {group_name} hash mismatch: {name}"
                )
    return payload


def gate_records(census: Mapping[str, Any]) -> list[dict[str, str]]:
    anchors = census["anchors"]
    sample = census["sampled_transcript_oracle"]
    population = census["population_law_oracle"]
    gates = [
        {
            "gate": "E0",
            "decision": (
                "pass"
                if (
                    census["experiments"] == 4096
                    and len(census["decisions"]) == 4
                    and census["grid"]
                    == ["1/4", "1/3", "2/3", "3/4"]
                )
                else "fail"
            ),
        },
        {
            "gate": "B0",
            "decision": (
                "pass"
                if anchors["blackwell_anchor"]
                == {
                    "informative_to_uninformative": "0",
                    "uninformative_to_informative": "1/4",
                }
                else "fail"
            ),
        },
        {
            "gate": "R0",
            "decision": (
                "pass"
                if (
                    anchors["risk_transfer"]["comparisons"] == 100
                    and anchors["risk_transfer"]["violations"] == 0
                    and Q(
                        anchors["risk_transfer"][
                            "minimum_bound_minus_gap"
                        ]
                    )
                    >= 0
                )
                else "fail"
            ),
        },
        {
            "gate": "S0",
            "decision": (
                "pass"
                if all(
                    row["classes_with_multiple_risk_profiles"] > 0
                    and Q(row["maximum_within_quotient_risk_spread"])
                    > 0
                    for row in (sample, population)
                )
                else "fail"
            ),
        },
        {
            "gate": "C0",
            "decision": (
                "pass"
                if (
                    anchors["conservatism_witness"][
                        "expanded_parameter_deficiency"
                    ]
                    == "1/2"
                    and anchors["conservatism_witness"][
                        "maximum_registered_target_only_risk_gap"
                    ]
                    == "0"
                )
                else "fail"
            ),
        },
    ]
    return gates


def compute_result(registration: Mapping[str, Any]) -> dict[str, Any]:
    census = run_grid(CONFIRMATION_GRID)
    gates = gate_records(census)
    passed = all(row["decision"] == "pass" for row in gates)
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA,
        "status": (
            "finite_stochastic_access_ledger_established"
            if passed
            else "finite_stochastic_access_ledger_not_established"
        ),
        **census,
        "gates": gates,
        "registration": {
            "content_sha256": registration[
                "registration_content_sha256"
            ],
            "git_commit_before_registration": registration[
                "git_commit_before_registration"
            ],
        },
        "claim_boundary": registration["claim_boundary"],
    }
    result["result_content_sha256"] = hashlib.sha256(
        canonical_bytes(result)
    ).hexdigest()
    return result


def verify_chronology(registration_path: Path, registration: Mapping[str, Any]) -> None:
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=REPO, text=True
    ).strip():
        raise RuntimeError("runner requires a clean registered worktree")
    current = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()
    before = str(registration["git_commit_before_registration"])
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", before, current],
        cwd=REPO,
        check=False,
    ).returncode:
        raise RuntimeError("implementation commit is not an ancestor of HEAD")
    relative = registration_path.relative_to(REPO).as_posix()
    committed = subprocess.check_output(
        ["git", "show", f"HEAD:{relative}"], cwd=REPO
    )
    if hashlib.sha256(committed).hexdigest() != sha256_file(
        registration_path
    ):
        raise RuntimeError("working registration differs from committed bytes")


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing unequal result: {path}")
        return
    path.write_bytes(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registration_path = args.registration.resolve()
    registration = load_registration(registration_path)
    verify_chronology(registration_path, registration)
    result = compute_result(registration)
    result["registration"]["file_sha256"] = sha256_file(registration_path)
    result["result_content_sha256"] = hashlib.sha256(
        canonical_bytes(
            {
                key: value
                for key, value in result.items()
                if key != "result_content_sha256"
            }
        )
    ).hexdigest()
    write_once(args.output.resolve(), canonical_bytes(result))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
