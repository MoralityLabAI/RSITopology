from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import subprocess
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from unknown_link import (
    complete_pairwise_law,
    explicit_counterexample,
    interpolated_matching_link,
    labeled_difference_order_key,
    positive_affine_equivalent,
    rational_symmetric_link,
    recover_scaled_utility,
    same_labeled_difference_order,
    temperature_law,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def validate_registration(
    path: Path, registration: dict[str, Any]
) -> tuple[str, dict[str, bool]]:
    relative = path.resolve().relative_to(REPO).as_posix()
    registration_commit = git("log", "-1", "--format=%H", "--", relative)
    checks = {
        "head_is_registration_commit": git("rev-parse", "HEAD")
        == registration_commit,
        "tracked_tree_clean": not git(
            "status", "--porcelain", "--untracked-files=no"
        ),
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
    }
    for relative_path, expected in registration["sealed_files"].items():
        checks[f"hash:{relative_path}"] = sha256(REPO / relative_path) == expected
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"registration validation failed: {failed!r}")
    return registration_commit, checks


def run_known_link(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    mismatch_count = 0
    edge_count = 0
    for _ in range(int(spec["count"])):
        item_count = rng.randint(
            int(spec["minimum_items"]), int(spec["maximum_items"])
        )
        utility = tuple(
            Fraction(rng.randint(-50, 50), rng.randint(1, 11))
            for _ in range(item_count)
        )
        beta = Fraction(rng.randint(1, 30), rng.randint(1, 30))
        law = temperature_law(utility, beta)
        recovered = recover_scaled_utility(item_count, law)
        expected = tuple(beta * (value - utility[0]) for value in utility)
        mismatch_count += int(recovered != expected)
        edge_count += len(law)
    return {
        **spec,
        "edge_count": edge_count,
        "mismatch_count": mismatch_count,
    }


def run_explicit_witness() -> dict[str, Any]:
    record = explicit_counterexample()
    passed = (
        record["same_law"]
        and record["same_difference_order"]
        and not record["positive_affine_equivalent"]
        and record["source_law"]
        == {
            (0, 1): Fraction(3, 4),
            (0, 2): Fraction(7, 8),
            (1, 2): Fraction(5, 6),
        }
    )
    return {
        "source_utility": [int(value) for value in record["source_utility"]],
        "target_utility": [int(value) for value in record["target_utility"]],
        "shared_law": {
            f"{left},{right}": [value.numerator, value.denominator]
            for (left, right), value in record["source_law"].items()
        },
        "passed": passed,
    }


def run_primitive_shell(spec: dict[str, Any]) -> dict[str, Any]:
    groups: dict[tuple[int, ...], list[tuple[Fraction, ...]]] = {}
    equality_count = 0
    for last in range(
        int(spec["minimum_last_coordinate"]),
        int(spec["maximum_last_coordinate"]) + 1,
    ):
        for middle in range(1, last):
            if math.gcd(middle, last) != 1:
                continue
            utility = tuple(map(Fraction, (0, middle, last)))
            groups.setdefault(
                labeled_difference_order_key(utility), []
            ).append(utility)
            equality_count += int(2 * middle == last)
    class_sizes = sorted(len(group) for group in groups.values())
    nonaffine_mismatches = 0
    for group in groups.values():
        reference = group[0]
        nonaffine_mismatches += sum(
            positive_affine_equivalent(reference, other)
            for other in group[1:]
        )
    return {
        **spec,
        "ray_count": sum(class_sizes),
        "class_count": len(groups),
        "class_sizes": class_sizes,
        "equality_count": equality_count,
        "nonaffine_mismatch_count": nonaffine_mismatches,
    }


def random_strict_gap_pair(
    rng: random.Random, maximum_gap: int
) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    while True:
        first = rng.randint(1, maximum_gap)
        second = rng.randint(1, maximum_gap)
        third = rng.randint(1, maximum_gap)
        fourth = rng.randint(1, maximum_gap)
        if first == second or third == fourth:
            continue
        if (first < second) != (third < fourth):
            continue
        source = tuple(map(Fraction, (0, first, first + second)))
        target = tuple(map(Fraction, (0, third, third + fourth)))
        if not positive_affine_equivalent(source, target):
            return source, target


def link_probe_passes(link: Any) -> bool:
    knots = link.knots
    points = {Fraction(0)}
    for (left_x, _), (right_x, _) in zip(knots, knots[1:]):
        points.update((left_x, (left_x + right_x) / 2, right_x))
    last_x = knots[-1][0]
    points.update((last_x + 1, last_x + 10, last_x + 1000))
    positive = sorted(points)
    values = [link(point) for point in positive]
    strict = all(left < right for left, right in zip(values, values[1:]))
    symmetric = all(link(-point) == 1 - link(point) for point in positive)
    bounded = all(Fraction(0) < value < Fraction(1) for value in values)
    return strict and symmetric and bounded


def run_ambiguity_pairs(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    same_order_mismatches = 0
    affine_mismatches = 0
    matching_law_mismatches = 0
    known_link_separation_mismatches = 0
    link_probe_mismatches = 0
    for _ in range(int(spec["count"])):
        source, target = random_strict_gap_pair(
            rng, int(spec["maximum_gap"])
        )
        same_order_mismatches += int(
            not same_labeled_difference_order(source, target)
        )
        affine_mismatches += int(positive_affine_equivalent(source, target))
        target_link = interpolated_matching_link(source, target)
        source_law = complete_pairwise_law(source, rational_symmetric_link)
        matching_law_mismatches += int(
            source_law != complete_pairwise_law(target, target_link)
        )
        known_link_separation_mismatches += int(
            source_law == complete_pairwise_law(
                target, rational_symmetric_link
            )
        )
        link_probe_mismatches += int(not link_probe_passes(target_link))
    return {
        **spec,
        "same_order_mismatch_count": same_order_mismatches,
        "affine_mismatch_count": affine_mismatches,
        "matching_law_mismatch_count": matching_law_mismatches,
        "known_link_separation_mismatch_count": (
            known_link_separation_mismatches
        ),
        "link_probe_mismatch_count": link_probe_mismatches,
    }


def run_two_item_controls(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    mismatch_count = 0
    for _ in range(int(spec["count"])):
        left = (
            Fraction(rng.randint(-1000, 1000)),
            Fraction(rng.randint(-1000, 1000)),
        )
        while left[0] == left[1]:
            left = (left[0], Fraction(rng.randint(-1000, 1000)))
        right = (
            Fraction(rng.randint(-1000, 1000)),
            Fraction(rng.randint(-1000, 1000)),
        )
        while right[0] == right[1]:
            right = (right[0], Fraction(rng.randint(-1000, 1000)))
        if (left[1] > left[0]) != (right[1] > right[0]):
            right = (right[1], right[0])
        mismatch_count += int(not positive_affine_equivalent(left, right))
    return {**spec, "mismatch_count": mismatch_count}


def run_order_mismatch_controls(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    missed_rejection_count = 0
    for _ in range(int(spec["count"])):
        first = rng.randint(1, int(spec["maximum_gap"]))
        second = rng.randint(first + 1, int(spec["maximum_gap"]) + first)
        third = rng.randint(2, int(spec["maximum_gap"]))
        fourth = rng.randint(1, third - 1)
        source = tuple(map(Fraction, (0, first, first + second)))
        target = tuple(map(Fraction, (0, third, third + fourth)))
        try:
            interpolated_matching_link(source, target)
        except ValueError:
            continue
        missed_rejection_count += 1
    return {**spec, "missed_rejection_count": missed_rejection_count}


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# ASMP-9 unknown response-link verification v0.8",
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
            "## Exact result",
            "",
            "A known injective link with unknown positive temperature recovers",
            "the utility ray exactly. An unrestricted unknown monotone link",
            "does not: non-affine three-item utilities can induce identical",
            "complete pairwise probability laws.",
            "",
            "## Claim boundary",
            "",
            "Finite population-law design obstruction; not finite-sample",
            "semiparametric estimation, general IRL, or a complete ASMP-9",
            "resolution. Novelty is not claimed.",
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
    known = run_known_link(protocol["known_link"])
    witness = run_explicit_witness()
    shell = run_primitive_shell(protocol["primitive_shell"])
    ambiguity = run_ambiguity_pairs(protocol["ambiguity_pairs"])
    two_item = run_two_item_controls(protocol["two_item_controls"])
    mismatch = run_order_mismatch_controls(
        protocol["order_mismatch_controls"]
    )
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_known_link_recovery": known["mismatch_count"] == 0,
        "G2_explicit_witness": witness["passed"],
        "G3_primitive_shell": (
            shell["class_count"] == 2
            and min(shell["class_sizes"]) > 1
            and shell["equality_count"] == 0
            and shell["nonaffine_mismatch_count"] == 0
        ),
        "G4_unknown_link_matching": (
            ambiguity["same_order_mismatch_count"] == 0
            and ambiguity["affine_mismatch_count"] == 0
            and ambiguity["matching_law_mismatch_count"] == 0
        ),
        "G5_known_link_separation": (
            ambiguity["known_link_separation_mismatch_count"] == 0
        ),
        "G6_link_validity": ambiguity["link_probe_mismatch_count"] == 0,
        "G7_two_item_minimality": two_item["mismatch_count"] == 0,
        "G8_order_mismatch_rejection": mismatch[
            "missed_rejection_count"
        ]
        == 0,
    }
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "unknown_link_finite_design_nonidentifiability_not_verified"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "elapsed_seconds": time.perf_counter() - started,
        "binding_checks": binding,
        "known_link": known,
        "explicit_witness": witness,
        "primitive_shell": shell,
        "ambiguity_pairs": ambiguity,
        "two_item_controls": two_item,
        "order_mismatch_controls": mismatch,
        "gates": gates,
        "verdict": verdict,
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_8.json"
    report_path = args.output_dir / "RESULT_v0_8.md"
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
    write_json(args.output_dir / "receipt_v0_8.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
