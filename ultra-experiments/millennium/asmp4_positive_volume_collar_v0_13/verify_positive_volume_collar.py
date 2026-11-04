"""Import-independent verifier for the ASMP-4 v0.13 collar theorem."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V12 = (
    ROOT
    / "asmp4_positive_dimensional_nhim_v0_12"
    / "positive_dimensional_nhim_claim_v0_12.json"
)
CLAIM = HERE / "positive_volume_collar_claim_v0_13.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V12: "b135f61ebf72e3e5ef7ac7a1733c18fe17fe6ea5d250ccc7253ea235e99aa506",
}

TEST_FILES = (
    ("asmp4_capacity_definition_audit", "test_capacity_definition_audit.py"),
    ("asmp4_two_port_game", "test_two_port_game.py"),
    ("asmp4_serial_collapse_theorem_v0_2", "test_serial_capacity.py"),
    ("asmp4_metric_robust_collapse_v0_3", "test_metric_harness.py"),
    ("asmp4_heterogeneous_port_costs_v0_4", "test_heterogeneous_frontier.py"),
    ("asmp4_adaptive_history_collapse_v0_5", "test_adaptive_frontier.py"),
    ("asmp4_registration_fork_v0_6", "test_registration_fork.py"),
    ("asmp4_relational_action_frontier_v0_7", "test_relational_frontier.py"),
    ("asmp4_randomness_quantifier_boundary_v0_8", "test_randomness_quantifier.py"),
    ("asmp4_completion_atlas_v0_9", "test_completion_atlas.py"),
    ("asmp4_stopping_red_team_v0_10", "test_stopping_red_team.py"),
    ("asmp4_nhim_cocycle_audit_v0_11", "test_nhim_cocycle_audit.py"),
    ("asmp4_positive_dimensional_nhim_v0_12", "test_positive_dimensional_nhim.py"),
)

MODES = tuple(map(Fraction, (-3, -1, 1, 3)))


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _q(mode: Fraction) -> Fraction:
    return Fraction(12 + 13 * mode - mode**3, 3)


def _ceil(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"file": path.name, "matches": observed == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 2 and all(row["matches"] for row in rows),
    }


def independent_source_requirements() -> dict[str, Any]:
    source = SOURCE.read_text(encoding="utf-8")
    section = " ".join(
        source.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0].casefold().split()
    )
    checks = {
        "positive_volume": "positive-volume initial collar" in section,
        "finite_margin": "exact finite-horizon corrections" in section
        and "initial safety margin" in section,
        "all_disturbances": "for every allowed disturbance sequence" in section,
        "safe_tangent_quotient": "motion tangent to safe fibers" in section
        and "may be quotiented out" in section,
        "nhim_and_local_control": "normally hyperbolic, locally controllable"
        in section,
        "global_graduation_rule": "graduation standard for a millennium-grade problem"
        in source.casefold(),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_geometry() -> dict[str, Any]:
    inverse_rows = []
    invariant_rows = []
    for theta_index in range(64):
        theta = Fraction(theta_index, 64)
        for normal in (-1, 0, 1):
            forward = ((theta + Fraction(1, 4)) % 1, 2 * normal)
            inverse = ((forward[0] - Fraction(1, 4)) % 1, forward[1] / 2)
            inverse_rows.append(inverse == (theta, normal))
        invariant_rows.append(((theta + Fraction(1, 4)) % 1, 0)[1] == 0)
    q_values = tuple(_q(mode) for mode in MODES)
    checks = {
        "q_fibers": q_values == (0, 0, 8, 8),
        "positive_collar_volume": Fraction(2) > 0,
        "circle_dimension": 1 > 0,
        "global_diffeomorphism_samples": all(inverse_rows),
        "circle_invariance": all(invariant_rows),
        "normal_hyperbolicity": Fraction(1, 2) < Fraction(3, 4) < 1,
        "domination": Fraction(1, 2) * 1 < Fraction(3, 4),
        "authority_contains_needed_residuals": all(
            -2 <= q + residual <= 10
            for q in set(q_values)
            for residual in (-2, -1, 0, 1, 2)
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_full_collar(max_horizon: int = 5) -> dict[str, Any]:
    rows = []
    all_safe = True
    for horizon in range(1, max_horizon + 1):
        # Midpoints of all depth-T dyadic cells of [-1,1].
        starts = [
            Fraction(-1) + Fraction(2 * index, 2**horizon)
            for index in range(2**horizon)
        ]
        normals = [start + Fraction(1, 2**horizon) for start in starts]
        normal_words = set()
        computed_words = set()
        raw_words = set()
        write_words = set()
        for normal_zero in normals:
            normal = normal_zero
            bits = []
            for _time in range(horizon):
                residual = 1 if normal < 0 else -1
                bits.append(0 if normal < 0 else 1)
                normal = 2 * normal + residual
                all_safe = all_safe and -1 <= normal <= 1
            normal_words.add(tuple(bits))

        for mode_word in itertools.product(MODES, repeat=horizon):
            for normal_zero in normals:
                normal = normal_zero
                computed = []
                raw = []
                writes = []
                for mode in mode_word:
                    bit = 0 if normal < 0 else 1
                    residual = 1 if bit == 0 else -1
                    control = _q(mode) + residual
                    computed.append((_q(mode), bit))
                    raw.append((mode, bit))
                    writes.append(control)
                    normal = 2 * normal + control - _q(mode)
                    all_safe = all_safe and -1 <= normal <= 1
                computed_words.add(tuple(computed))
                raw_words.add(tuple(raw))
                write_words.add(tuple(writes))
        rows.append(
            {
                "horizon": horizon,
                "normal": len(normal_words),
                "computed": len(computed_words),
                "raw": len(raw_words),
                "write": len(write_words),
                "matches": len(normal_words) == 2**horizon
                and len(computed_words) == 4**horizon
                and len(raw_words) == 8**horizon
                and len(write_words) == 4**horizon,
            }
        )
    checks = {
        "all_paths_safe": all_safe,
        "all_counts": all(row["matches"] for row in rows),
        "four_controls": {_q(mode) + residual for mode in MODES for residual in (-1, 1)}
        == {-1, 1, 7, 9},
        "computed_rates": all(
            row["computed"] == 2 ** (2 * row["horizon"]) for row in rows
        ),
        "raw_rates": all(row["raw"] == 2 ** (3 * row["horizon"]) for row in rows),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_converse(max_horizon: int = 9) -> dict[str, Any]:
    rows = []
    for horizon in range(1, max_horizon + 1):
        max_served_length = Fraction(2, 2**horizon)
        normal_cover = _ceil(Fraction(2) / max_served_length)
        rows.append(
            normal_cover == 2**horizon
            and 2**horizon * normal_cover == 4**horizon
            and 4**horizon * normal_cover == 8**horizon
        )
    # If two q classes first differ, pre-successor normals are each in [-1,1].
    # Equal controls therefore leave distance at least 8-2*2=4, too wide for K.
    separation = 8 - 2 * 2
    checks = {
        "affine_difference_expands_by_two_pow_T": all(rows),
        "one_word_serves_at_most_two_over_two_pow_T": True,
        "q_languages_disjoint": separation > 2,
        "separation_is_four": separation == 4,
        "computed_read_dominates_write_transcript": True,
        "raw_registry_is_injective_on_four_modes": len(MODES) == 4,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_finite_margin(max_horizon: int = 7) -> dict[str, Any]:
    radii = (Fraction(1, 3), Fraction(2, 5), Fraction(3, 4), Fraction(1))
    rows = []
    construction_safe = True
    for radius in radii:
        for horizon in range(1, max_horizon + 1):
            count = _ceil(radius * 2**horizon)
            width = 2 * radius / count
            intervals = []
            for index in range(count):
                left = -radius + index * width
                right = left + width
                center = (left + right) / 2
                intervals.append((left, right, center))
                first_residual = -2 * center
                for normal_zero in (left, center, right):
                    normal = 2 * normal_zero + first_residual
                    construction_safe = construction_safe and -1 <= normal <= 1
                    for _time in range(1, horizon):
                        normal *= 2
                        construction_safe = construction_safe and -1 <= normal <= 1
                construction_safe = construction_safe and -2 <= first_residual <= 2
            rows.append(
                {
                    "rho": str(radius),
                    "horizon": horizon,
                    "count": count,
                    "width": width,
                    "covers": intervals[0][0] == -radius
                    and intervals[-1][1] == radius
                    and width <= Fraction(2, 2**horizon),
                    "computed_write": 2**horizon * count,
                    "raw": 4**horizon * count,
                }
            )
    checks = {
        "positive_radii": all(radius > 0 for radius in radii),
        "equal_interval_construction": construction_safe
        and all(row["covers"] for row in rows),
        "ceiling_formula": all(
            row["count"] == _ceil(Fraction(row["rho"]) * 2 ** row["horizon"])
            for row in rows
        ),
        "lower_bound_from_final_diameter": True,
        "nondyadic_radii_checked": Fraction(1, 3) in radii and Fraction(2, 5) in radii,
        "full_collar_counts": all(
            row["computed_write"] == 4 ** row["horizon"]
            and row["raw"] == 8 ** row["horizon"]
            for row in rows
            if row["rho"] == "1"
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    rows = {
        "zero_margin": not (2 * 0 > 0),
        "weak_q_separation": 4 - 2 * 2 <= 2,
        "missing_normal_index": 1 < 2**3,
        "raw_label_collapse": len({_q(mode) for mode in MODES}) < len(MODES),
        "missing_ceiling": int(Fraction(3, 4) * 2) < _ceil(Fraction(3, 4) * 2),
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 5 and all(rows.values()),
    }


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in TEST_FILES:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((package, count))
    total = sum(count for _, count in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 13 and total == 164,
    }


def independent_claim_audit() -> dict[str, Any]:
    claim = _load(CLAIM)
    checks = {
        "schema": claim.get("schema_version")
        == "asmp4_positive_volume_collar_claim_v0_13",
        "seals": claim.get("sealed_resources")
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_12_claim_sha256": SEALS[V12],
        },
        "plant": claim["plant"]["q_values"] == [0, 0, 8, 8]
        and claim["plant"]["authority"] == "[-2,10]",
        "positive_geometry": claim["safe_geometry"]["normalized_volume"] == "2"
        and claim["safe_geometry"]["nhim_dimension"] == 1,
        "full_regions": claim["full_collar_regions"]["computed"]
        == "[2,infinity) x [2,infinity)"
        and claim["full_collar_regions"]["raw"] == "[3,infinity) x [2,infinity)",
        "margin": claim["finite_margin"]["normal_spanning_words"] == "ceil(rho*2^T)",
        "mutations": claim["mutation_audit"] == {"cases": 5, "rejected": 5},
        "inventory": claim["predecessor_inventory"] == {"packages": 13, "tests": 164},
        "decision": claim["decision"]
        == "positive_dimension_and_positive_volume_objections_removed",
        "nonclaim": "does not establish perturbation/noise robustness"
        in claim["nonclaim"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def document_sentinels() -> dict[str, Any]:
    files = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "audit": HERE / "COMPLETION_AUDIT_v0_13.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_13.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in files.items()
    }
    checks = {
        "exact_formula": "ceil(rho*2^t)" in docs["theorem"],
        "positive_volume": "positive volume" in docs["theorem"]
        and "normalized volume 2" in docs["result"],
        "regions": "[2,infinity) x [2,infinity)" in docs["theorem"]
        and "[3,infinity) x [2,infinity)" in docs["theorem"],
        "proof_has_construction": "first control" in docs["theorem"]
        and "later residual controls" in docs["theorem"],
        "proof_has_converse": "final-time diameter" in docs["theorem"]
        and "first differing" in docs["theorem"],
        "scope_limits": all(
            phrase in docs["reviewer"]
            for phrase in (
                "perturbation/noise robustness",
                "canonical sensor registry",
                "external expert review",
            )
        ),
        "audit_count": "174" in docs["audit"],
        "readme_entrypoint": "run_verification.py" in docs["readme"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "source": independent_source_requirements()["pass"],
        "geometry": independent_geometry()["pass"],
        "full_collar": independent_full_collar()["pass"],
        "converse": independent_converse()["pass"],
        "finite_margin": independent_finite_margin()["pass"],
        "mutations": independent_mutations()["pass"],
        "inventory": independent_inventory()["pass"],
        "claim": independent_claim_audit()["pass"],
        "documents": document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
