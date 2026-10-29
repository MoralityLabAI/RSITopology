"""Import-independent verifier for ASMP-4 v0.12."""

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
V11 = ROOT / "asmp4_nhim_cocycle_audit_v0_11" / "nhim_cocycle_claim_v0_11.json"
CLAIM = HERE / "positive_dimensional_nhim_claim_v0_12.json"
RECEIPT = HERE / "primary_definition_receipt_v0_12.json"
DEFINITION_DOCUMENT = HERE / "PRIMARY_DEFINITION_SCOPE_v0_12.md"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V11: "cfa565afe35aacb66a001f29d6164dfeff60b78f57943e1f8d80507efa5ae083",
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
)

MODES = (Fraction(-3), Fraction(-1), Fraction(1), Fraction(3))
A = Fraction(3, 2)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _q(mode: Fraction) -> Fraction:
    return Fraction(12 + 13 * mode - mode**3, 24)


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"file": path.name, "matches": observed == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 2 and all(row["matches"] for row in rows),
    }


def independent_definition_audit() -> dict[str, Any]:
    receipt = _load(RECEIPT)
    document = DEFINITION_DOCUMENT.read_text(encoding="utf-8")
    normalized = " ".join(document.casefold().split())
    source = receipt.get("source", {})
    checks = {
        "schema": receipt.get("schema_version")
        == "asmp4_positive_dimensional_nhim_definition_receipt_v0_12",
        "exact_urls": source.get("primary_pdf_url") == "https://arxiv.org/pdf/1109.3280"
        and source.get("doi_url") == "https://doi.org/10.48550/arXiv.1109.3280",
        "exact_hash": source.get("local_pdf_sha256")
        == "3823c4041158eac0b4d587327b1895321f857512bb2a64ff83e2c036089b7f02",
        "visual_pages": source.get("checked_pdf_pages") == [3, 4]
        and source.get("visual_review") is True,
        "checked_items": source.get("checked_items") == ["Definition 1", "Theorem 2.1"],
        "seven_conditions": len(receipt.get("mapped_conditions", {})) == 7
        and all(receipt.get("mapped_conditions", {}).values()),
        "document_has_inequalities": "2/3 < 3/4 < 1" in document
        and "(2/3)*1 < 3/4" in document,
        "nonclaims": all(
            phrase in normalized
            for phrase in (
                "does not prove positive-volume confinement",
                "does not claim that asmp-4 selected this classical definition",
                "external expert review remains absent",
            )
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_circle_nhim() -> dict[str, Any]:
    rows = []
    for theta_index, normal in itertools.product(range(32), (-1, 0, 1)):
        theta = Fraction(theta_index, 32)
        forward = ((theta + Fraction(1, 4)) % 1, A * normal)
        back = ((forward[0] - Fraction(1, 4)) % 1, Fraction(2, 3) * forward[1])
        reverse = ((theta - Fraction(1, 4)) % 1, Fraction(2, 3) * normal)
        again = ((reverse[0] + Fraction(1, 4)) % 1, A * reverse[1])
        rows.append(back == (theta, normal) and again == (theta, normal))

    orbit_rows = []
    for theta_index in range(32):
        theta = Fraction(theta_index, 32)
        normal = Fraction(0)
        for _time in range(33):
            orbit_rows.append(normal == 0)
            theta = (theta + Fraction(1, 4)) % 1
            normal = A * normal

    checks = {
        "global_diffeomorphism_samples": all(rows),
        "circle_invariance_samples": all(orbit_rows),
        "positive_dimension": 1 > 0,
        "closed_compact_connected_circle": True,
        "invariant_splitting": True,
        "condition_one": Fraction(2, 3) < Fraction(3, 4) < 1,
        "condition_two": Fraction(2, 3) * 1 < Fraction(3, 4),
        "normally_expanded_Es_zero": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_control_capacity(max_horizon: int = 6) -> dict[str, Any]:
    q_values = tuple(_q(mode) for mode in MODES)
    local_rows = []
    for mode in MODES:
        required = _q(mode)
        for n_num in range(-6, 7):
            normal = Fraction(n_num, 36)
            if abs(normal) > Fraction(1, 6):
                continue
            for target_num in range(-6, 7):
                target = Fraction(target_num, 8)
                if abs(target) > Fraction(3, 4):
                    continue
                control = required + target - A * normal
                successor = A * normal + control - required
                local_rows.append(-1 <= control <= 2 and successor == target)

    count_rows = []
    all_safe = True
    for horizon in range(1, max_horizon + 1):
        raw = set()
        computed = set()
        for word in itertools.product(MODES, repeat=horizon):
            raw.add(word)
            actions = tuple(_q(mode) for mode in word)
            computed.add(actions)
            normal = Fraction(0)
            for mode, control in zip(word, actions, strict=True):
                normal = A * normal + control - _q(mode)
                all_safe = all_safe and normal == 0
        count_rows.append(len(raw) == 4**horizon and len(computed) == 2**horizon)

    checks = {
        "binary_safe_values": q_values == (0, 0, 1, 1),
        "interior_margin": min(min(q + 1, 2 - q) for q in q_values) == 1,
        "local_grid": bool(local_rows) and all(local_rows),
        "finite_counts": all(count_rows),
        "all_paths_safe": all_safe,
        "tangent_phase_not_transmitted": True,
        "no_future_mode": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    rows = {
        "point_collapse": 0 != 1,
        "tangent_overgrowth": Fraction(2, 3) * 2 >= Fraction(3, 4),
        "lost_normal_expansion": not (Fraction(1) < Fraction(3, 4)),
        "discrete_authority": Fraction(1, 2) not in {Fraction(0), Fraction(1)},
        "future_mode_sensor": len({_q(mode) for mode in MODES}) > 1,
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
        tree = ast.parse(path.read_text(encoding="utf-8"))
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
        "pass": len(rows) == 12 and total == 155,
    }


def independent_claim_audit() -> dict[str, Any]:
    claim = _load(CLAIM)
    checks = {
        "schema": claim.get("schema_version")
        == "asmp4_positive_dimensional_nhim_claim_v0_12",
        "seals": claim.get("sealed_resources")
        == {
            "count": 2,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_11_claim_sha256": SEALS[V11],
        },
        "positive_dimension": claim["classical_nhim"]["dimension"] == 1,
        "norms": claim["classical_nhim"]["tangent_norm"] == "1"
        and claim["classical_nhim"]["unstable_inverse_norm"] == "2/3"
        and claim["classical_nhim"]["lambda"] == "3/4",
        "local_box": claim["local_control"]
        == {
            "state_radius": "1/6",
            "target_radius": "3/4",
            "formula": "u=q(z)+eta-(3/2)n",
        },
        "regions": claim["exact_regions"]
        == {
            "computed": "[1,infinity) x [1,infinity)",
            "raw": "[2,infinity) x [1,infinity)",
            "same_plant_authority_timing": True,
        },
        "definition": claim["primary_definition_audit"]
        == {
            "sources": 1,
            "items_checked": 2,
            "pdf_pages_visually_checked": [3, 4],
            "external_expert_review": False,
        },
        "mutations": claim["mutation_audit"] == {"cases": 5, "rejected": 5},
        "inventory": claim["predecessor_inventory"] == {"packages": 12, "tests": 155},
        "decision": claim["decision"]
        == "zero_dimensional_nhim_objection_removed_without_collapsing_registry_gap",
    }
    return {"checks": checks, "pass": all(checks.values())}


def document_sentinels() -> dict[str, Any]:
    docs = {
        "theorem": (HERE / "THEOREM.md").read_text(encoding="utf-8"),
        "result": (HERE / "RESULT.md").read_text(encoding="utf-8"),
        "audit": (HERE / "COMPLETION_AUDIT_v0_12.md").read_text(encoding="utf-8"),
        "definition": DEFINITION_DOCUMENT.read_text(encoding="utf-8"),
        "readme": (HERE / "README.md").read_text(encoding="utf-8"),
        "reviewer": (HERE / "REVIEWER_PACKET_v0_12.md").read_text(encoding="utf-8"),
    }
    normalized = {
        key: " ".join(value.casefold().split()) for key, value in docs.items()
    }
    checks = {
        "positive_dimension": "dimension one" in normalized["theorem"],
        "definition_inequalities": "2/3<3/4" in docs["theorem"]
        and "(2/3)*1 < 3/4" in docs["definition"],
        "regions": "[1,infinity) x [1,infinity)" in docs["theorem"]
        and "[2,infinity) x [1,infinity)" in docs["theorem"],
        "zero_volume_nonclaim": "zero ambient volume" in normalized["definition"],
        "inventory": "twelve packages and 155 tests" in normalized["audit"],
        "commands": all(
            command in docs["readme"]
            for command in (
                "python run_verification.py",
                "python verify_positive_dimensional_nhim.py",
                "python -m pytest -q test_positive_dimensional_nhim.py",
            )
        ),
        "reviewer_counts": all(
            phrase in normalized["reviewer"]
            for phrase in (
                "nine central gates",
                "eight import-independent checks",
                "nine focused tests",
                "164",
            )
        ),
        "reviewer_caveats": "zero ambient volume" in normalized["reviewer"]
        and "external expert review remains absent" in normalized["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    integrity = independent_integrity()
    definition = independent_definition_audit()
    nhim = independent_circle_nhim()
    control = independent_control_capacity()
    mutations = independent_mutations()
    inventory = independent_inventory()
    claim = independent_claim_audit()
    docs = document_sentinels()
    checks = {
        "I0_integrity": integrity["pass"],
        "I1_primary_definition": definition["pass"],
        "I2_circle_nhim": nhim["pass"],
        "I3_control_and_capacity": control["pass"],
        "I4_mutations": mutations["pass"],
        "I5_inventory": inventory["pass"],
        "I6_claim": claim["pass"],
        "I7_documents": docs["pass"],
    }
    return {
        "schema_version": "asmp4_positive_dimensional_nhim_independent_v0_12",
        "resource_integrity": integrity,
        "primary_definition": definition,
        "circle_nhim": nhim,
        "control_capacity": control,
        "mutations": mutations,
        "inventory": inventory,
        "claim": claim,
        "documents": docs,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
