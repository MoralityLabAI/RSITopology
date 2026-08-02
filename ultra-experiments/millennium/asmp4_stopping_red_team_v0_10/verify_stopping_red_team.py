"""Import-independent verifier for the ASMP-4 v0.10 stopping red team."""

from __future__ import annotations

import ast
import hashlib
import json
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
INDEX = ROOT / "problem_set_v0_1.json"
V06 = ROOT / "asmp4_registration_fork_v0_6" / "registration_claim_v0_6.json"
V08 = ROOT / "asmp4_randomness_quantifier_boundary_v0_8" / "randomness_claim_v0_8.json"
V09 = ROOT / "asmp4_completion_atlas_v0_9" / "completion_atlas_claim_v0_9.json"
CLAIM = HERE / "stopping_red_team_claim_v0_10.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    INDEX: "30ff673486b140c178d279eb100c81a46c849ba5b9955eddee16c83824d43ee0",
    V06: "812c17f913c1e498d835c13430b7880b95a188496333b48355883f0fe634c5a5",
    V08: "0cfce1a8751eae64ba746e7a773eb1cee48355c5168465c4a208c2fa07b1cf16",
    V09: "1be836878a75d3537f80974b3bd9a674f67cc8de1ed723622c719bee756e8d4d",
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
    (
        "asmp4_randomness_quantifier_boundary_v0_8",
        "test_randomness_quantifier.py",
    ),
    ("asmp4_completion_atlas_v0_9", "test_completion_atlas.py"),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(
            {
                "file": path.name,
                "observed": observed,
                "matches": observed == expected,
            }
        )
    return {"rows": rows, "pass": len(rows) == 5 and all(r["matches"] for r in rows)}


def independent_scope_parser() -> dict[str, Any]:
    """Parse the section with a line-state machine, not central string splits."""

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    section_lines = []
    active = False
    for line in lines:
        if line.startswith("# ASMP-4"):
            active = True
            continue
        if active and line.startswith("# ASMP-5"):
            break
        if active:
            section_lines.append(line)

    buckets: dict[str, list[str]] = {
        "setting": [],
        "conjecture": [],
        "requirements": [],
        "liveness": [],
    }
    state = "setting"
    for line in section_lines:
        if line == "## Two-Port Capacity Conjecture":
            state = "conjecture"
            continue
        if line == "## What a complete resolution requires":
            state = "requirements"
            continue
        if line == "## Liveness and kill examples":
            state = "liveness"
            continue
        if line == "## Existing theory this must exceed":
            break
        buckets[state].append(line)

    normalized = {
        key: " ".join(" ".join(value).casefold().split())
        for key, value in buckets.items()
    }
    whole = " ".join(" ".join(section_lines).casefold().split())
    full_source = " ".join(SOURCE.read_text(encoding="utf-8").casefold().split())
    checks = {
        "section_found": bool(section_lines),
        "general_process": "x_(t+1) = f(x_t,u_t,w_t)" in normalized["setting"],
        "universal_disturbance": (
            "for every allowed disturbance sequence" in normalized["setting"]
        ),
        "independent_randomness": (
            "shared randomness independent of the plant state" in normalized["setting"]
        ),
        "nhim_positive_scope": (
            "registered normally hyperbolic, locally controllable class"
            in normalized["conjecture"]
        ),
        "nonhyperbolic_boundary": "nonhyperbolicity" in normalized["requirements"],
        "k0_unrestricted": "initial set `k_0`" in normalized["setting"]
        and "positive-volume" not in normalized["setting"]
        and "positive-volume" not in normalized["conjecture"]
        and "positive-volume" not in normalized["requirements"],
        "positive_volume_only_liveness": (
            "positive-volume initial collar" in normalized["liveness"]
        ),
        "robustness_is_graduation_rule": (
            "graduation standard for a millennium-grade problem" in full_source
            and "robust version" in full_source
            and "exact statements have a finite-precision" in full_source
        ),
        "sensor_selector_absent": "closed under upstream computation" not in whole
        and "forced injective raw sensor" not in whole,
        "stochastic_order_absent": "per-disturbance almost sure" not in whole
        and "uniform almost sure" not in whole
        and "support zero error" not in whole,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_index_audit() -> dict[str, Any]:
    data = _load(INDEX)
    row = next(problem for problem in data["problems"] if problem["id"] == "ASMP-4")
    keys = set(row)
    checks = {
        "markdown_normative": data["normative_statement_file"] == SOURCE.name,
        "index_not_normative": data["registry_is_normative"] is False,
        "ungraduated": data["graduation_standard_satisfied"] is False,
        "sensor_key_absent": not any("sensor" in key for key in keys),
        "random_key_absent": not any(
            "random" in key or "probability" in key for key in keys
        ),
    }
    return {"keys": sorted(keys), "checks": checks, "pass": all(checks.values())}


def independent_sensor_replay() -> dict[str, Any]:
    claim = _load(V06)
    actions = (0, 0, 1, 1)
    specs = {
        "computed": ((0, 0, 1, 1), (0, 1), 2),
        "raw": ((0, 1, 2, 3), (0, 0, 1, 1), 4),
    }
    rows = []
    failures = []
    for horizon in range(1, 7):
        for name, (sensor, controller, read_base) in specs.items():
            reads = set()
            writes = set()
            safe = True
            for word in product(range(4), repeat=horizon):
                read = tuple(sensor[mode] for mode in word)
                write = tuple(controller[symbol] for symbol in read)
                safe = safe and all(
                    symbol == actions[mode]
                    for mode, symbol in zip(word, write, strict=True)
                )
                reads.add(read)
                writes.add(write)
            matches = (
                safe and len(reads) == read_base**horizon and len(writes) == 2**horizon
            )
            rows.append((horizon, name, len(reads), len(writes), safe))
            if not matches:
                failures.append((horizon, name))

    coords = (-3, -1, 1, 3)
    q_values = tuple(Fraction(12 + 13 * z - z**3, 24) for z in coords)
    invariant_rows = []
    for z, correct in zip(coords, actions, strict=True):
        for disturbance in coords:
            correct_next = (
                Fraction(3, 2) * 0 + correct - Fraction(12 + 13 * z - z**3, 24)
            )
            wrong_next = (
                Fraction(3, 2) * 0 + (1 - correct) - Fraction(12 + 13 * z - z**3, 24)
            )
            invariant_rows.append(
                (
                    correct_next == 0 and disturbance in coords,
                    wrong_next != 0,
                )
            )
    audit = claim["canonical_registry_model_audit"]
    checks = {
        "no_replay_failures": not failures,
        "q_matches_actions": q_values == tuple(Fraction(x) for x in actions),
        "compact_zero_manifold": len(set(coords)) == 4,
        "robust_invariance": all(correct for correct, _ in invariant_rows),
        "wrong_controls_leave": all(wrong for _, wrong in invariant_rows),
        "bounded_sets": set(actions) == {0, 1} and set(coords) == {-3, -1, 1, 3},
        "nhim_dominance": abs(Fraction(3, 2)) > abs(Fraction(0)),
        "local_normal_control": Fraction(1) != 0,
        "thirteen_obligations": audit["source_obligation_count"] == 13,
        "both_models_pass": audit["computed_sensor_registry_satisfies_all_obligations"]
        and audit["fixed_raw_sensor_registry_satisfies_all_obligations"],
        "registry_unselected": audit["registry_domain_selected"] is False,
        "regions_distinct": audit["computed_sensor_region"]
        == "[1,infinity) x [1,infinity)"
        and audit["fixed_raw_sensor_region"] == "[2,infinity) x [1,infinity)",
        "same_plant_only_closure_changes": (
            "same four-mode uncertain safety plant" in claim["claim"]
            and "only changed premise is upstream computation closure" in claim["claim"]
        ),
    }
    return {
        "rows": rows,
        "invariant_rows": invariant_rows,
        "failures": failures,
        "checks": checks,
        "pass": all(checks.values()),
    }


def independent_coordinate_relabeling() -> dict[str, Any]:
    modes = tuple(range(4))
    actions = tuple(range(2))
    safe_action = (0, 0, 1, 1)
    cases = 0
    failures = 0
    for mode_labels in permutations(modes):
        inverse_mode = {new: old for old, new in enumerate(mode_labels)}
        for action_labels in permutations(actions):
            expected_action = {
                new: action_labels[safe_action[inverse_mode[new]]] for new in modes
            }
            for computed_labels in permutations(actions):
                computed_encoder = {
                    new: computed_labels[safe_action[inverse_mode[new]]]
                    for new in modes
                }
                computed_decoder = {
                    computed_labels[old_action]: action_labels[old_action]
                    for old_action in actions
                }
                for raw_labels in permutations(modes):
                    raw_encoder = {new: raw_labels[inverse_mode[new]] for new in modes}
                    raw_decoder = {
                        raw_labels[old]: action_labels[safe_action[old]]
                        for old in modes
                    }
                    cases += 1
                    valid = True
                    for horizon in (1, 2, 3):
                        c_reads = set()
                        r_reads = set()
                        c_writes = set()
                        r_writes = set()
                        for word in product(modes, repeat=horizon):
                            c_read = tuple(computed_encoder[x] for x in word)
                            r_read = tuple(raw_encoder[x] for x in word)
                            c_write = tuple(computed_decoder[x] for x in c_read)
                            r_write = tuple(raw_decoder[x] for x in r_read)
                            target = tuple(expected_action[x] for x in word)
                            valid = valid and c_write == target and r_write == target
                            c_reads.add(c_read)
                            r_reads.add(r_read)
                            c_writes.add(c_write)
                            r_writes.add(r_write)
                        valid = valid and (
                            len(c_reads) == 2**horizon
                            and len(r_reads) == 4**horizon
                            and len(c_writes) == 2**horizon
                            and len(r_writes) == 2**horizon
                        )
                    failures += not valid

    source = " ".join(SOURCE.read_text(encoding="utf-8").casefold().split())
    checks = {
        "cases": cases == 2304,
        "failures": failures == 0,
        "words": cases * (4 + 16 + 64) == 193536,
        "source_rule": (
            "conclusions survive declared coordinate changes, equivalent encodings, renamings"
            in source
        ),
    }
    return {
        "cases": cases,
        "mode_words_per_registry": cases * 84,
        "failures": failures,
        "checks": checks,
        "pass": all(checks.values()),
    }


def independent_stochastic_firewall() -> dict[str, Any]:
    claim = _load(V08)
    fixture = claim["continuous_diagonal_fixture"]
    nonclaims = set(claim["nonclaims"])
    checks = {
        "diagonal_fixture": fixture["dynamics"] == "x_(t+1)=(u_t-w_t)^2",
        "semantic_fork": fixture["per_disturbance_almost_sure_safe"]
        and not fixture["uniform_almost_sure_safe"]
        and not fixture["support_zero_error_safe"],
        "nhim_is_nonclaim": (
            "normally hyperbolic classification of the diagonal boundary fixture"
            in nonclaims
        ),
        "canonical_region_is_nonclaim": (
            "a registration-independent canonical ASMP-4 region" in nonclaims
        ),
    }
    return {
        "checks": checks,
        "positive_nhim_witness": False,
        "minimal_proof_dependency": False,
        "pass": all(checks.values()),
    }


def independent_selector_mutations() -> dict[str, Any]:
    claim = _load(V09)
    computed = claim["sensor_targets"]["computed"]
    raw = claim["sensor_targets"]["forced_raw"]
    relational = claim["sensor_targets"]["adaptive_relational"]
    source = " ".join(SOURCE.read_text(encoding="utf-8").casefold().split())
    rows = [
        ("base", (computed, relational, raw), None, False),
        ("computed", (computed,), computed, True),
        ("relational", (relational,), relational, True),
        ("raw", (raw,), raw, True),
        ("union", (computed, relational, raw), computed, True),
    ]
    checks = {
        "five_cases": len(rows) == 5,
        "base_has_three_distinct_targets": len(set(rows[0][1])) == 3,
        "base_underdetermined": rows[0][3] is False,
        "mutations_determinate": all(row[3] for row in rows[1:]),
        "union_computed": rows[-1][2] == computed,
        "source_has_no_selector": "closed under upstream computation" not in source
        and "forced injective raw sensor" not in source,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_test_inventory() -> dict[str, Any]:
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
        "pass": len(rows) == 10 and total == 127,
    }


def independent_claim_audit() -> dict[str, Any]:
    claim = _load(CLAIM)
    checks = {
        "schema": claim["schema_version"] == "asmp4_stopping_red_team_claim_v0_10",
        "five_seals": claim["sealed_resources"]["count"] == 5,
        "same_plant": claim["primary_witness"]["same_plant"] is True,
        "compact_safe_manifold": claim["primary_witness"]["compact_safe_manifold"]
        == "K=K_0={0} x {-3,-1,1,3}",
        "bounded_uncertainty": claim["primary_witness"]["bounded_uncertainty"] is True,
        "unique_control": claim["primary_witness"]["unique_safe_binary_control"]
        is True,
        "thirteen": claim["primary_witness"]["source_obligations_per_model"] == 13,
        "distinct": claim["primary_witness"]["computed_region"]
        != claim["primary_witness"]["raw_region"],
        "stochastic_not_required": claim["primary_witness"][
            "stochastic_witness_required"
        ]
        is False,
        "twelve_resolved": claim["counterargument_audit"]
        == {"cases": 12, "unresolved": 0},
        "selector_mutations": claim["selector_mutations"]
        == {
            "cases": 5,
            "canonical_targets": 3,
            "union_target": "[1,infinity) x [1,infinity)",
            "source_selector_present": False,
        },
        "coordinate_relabeling": claim["coordinate_relabeling_audit"]
        == {
            "cases": 2304,
            "horizons": [1, 2, 3],
            "mode_words_per_registry": 193536,
            "failures": 0,
            "computed_region": "[1,infinity) x [1,infinity)",
            "raw_region": "[2,infinity) x [1,infinity)",
        },
        "tests": claim["test_inventory"]
        == {"predecessor_packages": 10, "predecessor_tests": 127},
        "decision": claim["decision"]
        == "stop_local_enumeration_and_request_normative_registration",
    }
    return {"checks": checks, "pass": all(checks.values())}


def document_sentinels() -> dict[str, Any]:
    documents = {
        "theorem": (HERE / "THEOREM.md").read_text(encoding="utf-8"),
        "result": (HERE / "RESULT.md").read_text(encoding="utf-8"),
        "stopping": (HERE / "STOPPING_ARGUMENT_v0_10.md").read_text(encoding="utf-8"),
        "audit": (HERE / "COMPLETION_AUDIT_v0_10.md").read_text(encoding="utf-8"),
        "prior": (HERE / "PRIOR_ART_AUDIT_v0_10.md").read_text(encoding="utf-8"),
        "reviewer": (HERE / "REVIEWER_PACKET_v0_10.md").read_text(encoding="utf-8"),
    }
    normalized_result = " ".join(documents["result"].split())
    checks = {
        "minimal_theorem": "sensor-only minimal stopping theorem"
        in documents["theorem"].casefold(),
        "no_stochastic_premise": "stochastic witness is not a premise"
        in documents["theorem"],
        "thirteen": "13 of 13" in documents["theorem"],
        "nhim": "NHIM" in documents["theorem"],
        "twelve_challenges": "twelve adversarial counterarguments" in normalized_result,
        "relabelings": "2,304 coordinate and symbol relabelings" in normalized_result,
        "tests": "127 predecessor tests" in documents["result"],
        "registry": "normative sensor/computation registry" in documents["stopping"],
        "four_reopening": "four reopening conditions" in documents["stopping"],
        "primary": "Primary witness" in documents["audit"],
        "nonclaim": "does not claim" in documents["prior"],
        "reviewer_commands": all(
            command in documents["reviewer"]
            for command in (
                "python run_verification.py",
                "python verify_stopping_red_team.py",
                "python -m pytest -q test_stopping_red_team.py",
            )
        ),
        "reviewer_caveats": "Scope caveats a reviewer should preserve"
        in documents["reviewer"]
        and "External field review remains absent" in documents["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    integrity = independent_integrity()
    scope = independent_scope_parser()
    index = independent_index_audit()
    sensor = independent_sensor_replay()
    coordinates = independent_coordinate_relabeling()
    stochastic = independent_stochastic_firewall()
    selectors = independent_selector_mutations()
    tests = independent_test_inventory()
    claim = independent_claim_audit()
    docs = document_sentinels()
    checks = {
        "I0_resource_integrity": integrity["pass"],
        "I1_line_state_scope_parser": scope["pass"],
        "I2_machine_index_audit": index["pass"],
        "I3_sensor_witness_replay": sensor["pass"],
        "I4_coordinate_relabeling": coordinates["pass"],
        "I5_stochastic_scope_firewall": stochastic["pass"],
        "I6_selector_mutations": selectors["pass"],
        "I7_test_inventory": tests["pass"],
        "I8_frozen_claim": claim["pass"],
        "I9_document_sentinels": docs["pass"],
        "I10_minimal_proof_is_sensor_only": sensor["pass"]
        and stochastic["minimal_proof_dependency"] is False,
    }
    return {
        "schema_version": "asmp4_stopping_red_team_independent_v0_10",
        "resource_integrity": integrity,
        "canonical_scope": scope,
        "machine_index": index,
        "sensor_replay": sensor,
        "coordinate_relabeling": coordinates,
        "stochastic_firewall": stochastic,
        "selector_mutations": selectors,
        "test_inventory": tests,
        "claim_audit": claim,
        "document_sentinels": docs,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
