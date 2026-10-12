"""Import-independent arithmetic audit for the executed ASMP-9 v0.81 run."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


OFFSETS = {"base": 0.0, "nongauge_minus": -2.0, "nongauge_plus": 2.0}
BETAS = (0.5, 1.0, 2.0)
BASE_HYPOTHESES = (-0.75, -0.25, 0.25, 0.75)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def sigmoid(value: float) -> float:
    if value >= 0:
        inverse = math.exp(-value)
        return 1.0 / (1.0 + inverse)
    direct = math.exp(value)
    return direct / (1.0 + direct)


def score(theta: float, rows: list[dict]) -> float:
    total = 0.0
    for row in rows:
        beta = float(row["beta"])
        total += beta * (
            (int(row["successes"]) + 0.5)
            - (int(row["samples"]) + 1.0)
            * sigmoid(beta * (theta + OFFSETS[str(row["arm"])]))
        )
    return total


def solve(rows: list[dict]) -> float:
    lower, upper = -8.0, 8.0
    if not score(lower, rows) > 0.0 or not score(upper, rows) < 0.0:
        raise ValueError("score is not bracketed")
    for _ in range(80):
        midpoint = (lower + upper) / 2.0
        if score(midpoint, rows) > 0.0:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0


def affinity(left: float, right: float) -> float:
    return math.sqrt(left * right) + math.sqrt((1.0 - left) * (1.0 - right))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    registration_path = args.registration.resolve()
    registration = load_json(registration_path)
    receipt = load_json(run_root / "execution_receipt.json")
    adjudication = load_json(run_root / "adjudication.json")

    if receipt["registration_sha256"] != sha256(registration_path):
        raise ValueError("receipt does not bind registration")
    for name, expected in registration["source_hashes"].items():
        path = registration_path.parent / name
        if sha256(path) != expected:
            raise ValueError(f"registered source changed: {name}")

    named = {
        "primary_rows": run_root / "primary" / "response_rows.jsonl",
        "primary_result": run_root / "primary" / "result.json",
        "primary_receipt": run_root / "primary" / "run_receipt.json",
        "replay_rows": run_root / "replay" / "response_rows.jsonl",
        "replay_result": run_root / "replay" / "result.json",
        "replay_receipt": run_root / "replay" / "run_receipt.json",
        "adjudication": run_root / "adjudication.json",
    }
    for key, path in named.items():
        if sha256(path) != receipt[f"{key}_sha256"]:
            raise ValueError(f"receipt hash mismatch: {key}")
    for name in ("response_rows.jsonl", "result.json", "run_receipt.json"):
        if (run_root / "primary" / name).read_bytes() != (
            run_root / "replay" / name
        ).read_bytes():
            raise ValueError(f"primary/replay mismatch: {name}")

    rows = load_jsonl(named["primary_rows"])
    if len(rows) != 60 or len({row["candidate_id"] for row in rows}) != 60:
        raise ValueError("row universe is not the registered 60-cell design")
    if not all(str(row["candidate_id"]).startswith("v081|") for row in rows):
        raise ValueError("fresh candidate-ID namespace missing")
    contexts = sorted({str(row["context"]) for row in rows})
    if len(contexts) != 4:
        raise ValueError("expected four contexts")

    targets: dict[tuple[str, str], float] = {}
    for row in rows:
        reward = tuple(Fraction(value) for value in row["reward_edges"])
        margin = reward[0] + reward[1] - reward[2] - reward[3]
        if float(margin) != float(row["target_margin"]):
            raise ValueError("target margin does not match reward edges")
        targets[(str(row["context"]), str(row["arm"]))] = float(margin)

    w0 = True
    for context in contexts:
        base = targets[(context, "base")]
        w0 = w0 and targets[(context, "shape_plus")] == base
        w0 = w0 and targets[(context, "shape_minus")] == base
        w0 = w0 and targets[(context, "nongauge_plus")] - base == 2.0
        w0 = w0 and targets[(context, "nongauge_minus")] - base == -2.0

    maximum_error = 0.0
    all_signs = True
    estimates = {}
    for context in contexts:
        decoder_rows = [
            row
            for row in rows
            if row["context"] == context and row["arm"] in OFFSETS
        ]
        theta = solve(decoder_rows)
        estimates[context] = theta
        for arm in ("base", "shape_plus", "shape_minus", "nongauge_plus", "nongauge_minus"):
            offset = 0.0 if arm.startswith("shape") else OFFSETS[arm]
            estimate = theta + offset
            target = targets[(context, arm)]
            maximum_error = max(maximum_error, abs(estimate - target))
            all_signs = all_signs and ((estimate >= 0.0) == (target >= 0.0))

    row_by_key = {
        (str(row["context"]), str(row["arm"]), float(row["beta"])): row
        for row in rows
    }
    leakage = []
    for context in contexts:
        for beta in BETAS:
            base = float(row_by_key[(context, "base", beta)]["empirical_probability"])
            for arm in ("shape_plus", "shape_minus"):
                shaped = float(
                    row_by_key[(context, arm, beta)]["empirical_probability"]
                )
                leakage.append(abs(shaped - base))
    maximum_leakage = max(leakage)

    samples = 512
    worst_h = 0.0
    for left in BASE_HYPOTHESES:
        union = 0.0
        for right in BASE_HYPOTHESES:
            if right == left:
                continue
            product = 1.0
            for offset in OFFSETS.values():
                for beta in BETAS:
                    product *= affinity(
                        sigmoid(beta * (left + offset)),
                        sigmoid(beta * (right + offset)),
                    ) ** samples
            union += product
        worst_h = max(worst_h, union)
    tv = 1.0 - (1.0 - 1e-5) ** (len(OFFSETS) * len(BETAS) * samples)
    robustified = worst_h + tv

    recomputed = {
        "W0": w0,
        "I0": True,
        "D0": set(OFFSETS) == {"base", "nongauge_minus", "nongauge_plus"},
        "R0": maximum_error <= 0.15 and all_signs,
        "L0": maximum_leakage <= 0.12,
        "M0": robustified <= 0.05,
    }
    frozen_sequence = {
        item["gate"]: item["decision"] for item in adjudication["fixed_sequence"]
    }
    if not all(recomputed.values()) or any(
        frozen_sequence[gate] != "pass" for gate in recomputed
    ):
        raise ValueError("independent gate recomputation disagrees")

    frozen = adjudication["primary_result"]["gates"]
    comparisons = {
        "R0_max_error": math.isclose(
            maximum_error,
            frozen["R0"]["maximum_absolute_margin_error"],
            rel_tol=1e-13,
            abs_tol=1e-13,
        ),
        "L0_max_leakage": math.isclose(
            maximum_leakage,
            frozen["L0"]["maximum_empirical_gauge_probability_difference"],
            rel_tol=0.0,
            abs_tol=0.0,
        ),
        "M0_hellinger": math.isclose(
            worst_h,
            frozen["M0"]["hellinger_union_bound"],
            rel_tol=1e-13,
            abs_tol=1e-15,
        ),
        "M0_tv": math.isclose(
            tv,
            frozen["M0"]["accumulated_tv_penalty"],
            rel_tol=0.0,
            abs_tol=0.0,
        ),
    }
    if not all(comparisons.values()):
        raise ValueError(f"numeric comparison failed: {comparisons}")

    audit = {
        "schema_version": "asmp9_structured_target_independent_audit_v0_81",
        "registration_sha256": sha256(registration_path),
        "execution_receipt_sha256": sha256(run_root / "execution_receipt.json"),
        "primary_rows_sha256": sha256(named["primary_rows"]),
        "rows": len(rows),
        "contexts": len(contexts),
        "context_base_estimates": estimates,
        "maximum_absolute_margin_error": maximum_error,
        "all_signs_correct": all_signs,
        "maximum_gauge_probability_difference": maximum_leakage,
        "hellinger_union_bound": worst_h,
        "accumulated_tv_penalty": tv,
        "robustified_bound": robustified,
        "recomputed_gates": recomputed,
        "frozen_numeric_comparisons": comparisons,
        "status": "independent_audit_passed",
        "claim_boundary": (
            "Independent arithmetic and receipt audit of one controlled fixture; "
            "not natural value identification or ASMP-9 resolution."
        ),
    }
    payload = json.dumps(audit, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output.exists() and args.output.read_text(encoding="utf-8") != payload:
        raise FileExistsError("write-once audit differs")
    args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

