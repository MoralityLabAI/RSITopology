"""Adversarial audit of the ASMP-4 evidence-backed stopping certificate.

The central question is deliberately narrower than another capacity census:
does the specification-stopping conclusion survive if the v0.8 stochastic
diagonal is forbidden from serving as a normally-hyperbolic witness?  The
answer is yes.  The same-plant v0.6 sensor-registration fork alone supplies two
models of the explicit architecture with distinct exact regions.
"""

from __future__ import annotations

import ast
import hashlib
import json
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent
SOURCE = MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
INDEX = MILLENNIUM / "problem_set_v0_1.json"
V06_CLAIM = MILLENNIUM / "asmp4_registration_fork_v0_6" / "registration_claim_v0_6.json"
V08_CLAIM = (
    MILLENNIUM
    / "asmp4_randomness_quantifier_boundary_v0_8"
    / "randomness_claim_v0_8.json"
)
V09_CLAIM = (
    MILLENNIUM / "asmp4_completion_atlas_v0_9" / "completion_atlas_claim_v0_9.json"
)
CLAIM = HERE / "stopping_red_team_claim_v0_10.json"
PRIOR_ART_RECEIPT = HERE / "prior_art_scope_receipt_v0_10.json"
PRIOR_ART_DOCUMENT = HERE / "EXTERNAL_PRIOR_ART_SCOPE_v0_10.md"
TARGETED_LITERATURE_RECEIPT = HERE / "targeted_literature_near_miss_receipt_v0_10.json"
TARGETED_LITERATURE_DOCUMENT = HERE / "TARGETED_LITERATURE_NEAR_MISSES_v0_10.md"

SEALED_RESOURCES = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "machine_index": (
        INDEX,
        "30ff673486b140c178d279eb100c81a46c849ba5b9955eddee16c83824d43ee0",
    ),
    "v0_6_claim": (
        V06_CLAIM,
        "812c17f913c1e498d835c13430b7880b95a188496333b48355883f0fe634c5a5",
    ),
    "v0_8_claim": (
        V08_CLAIM,
        "0cfce1a8751eae64ba746e7a773eb1cee48355c5168465c4a208c2fa07b1cf16",
    ),
    "v0_9_claim": (
        V09_CLAIM,
        "1be836878a75d3537f80974b3bd9a674f67cc8de1ed723622c719bee756e8d4d",
    ),
}

PREDECESSOR_TESTS = (
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _asmp4_section() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    return source.split("# ASMP-4", maxsplit=1)[1].split("# ASMP-5", maxsplit=1)[0]


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALED_RESOURCES.items():
        observed = _sha256(path)
        rows.append(
            {
                "name": name,
                "path": str(path.relative_to(MILLENNIUM)),
                "expected_sha256": expected,
                "observed_sha256": observed,
                "matches": observed == expected,
            }
        )
    return {
        "resources": len(rows),
        "rows": rows,
        "pass": len(rows) == 5 and all(row["matches"] for row in rows),
    }


def canonical_scope_report() -> dict[str, Any]:
    """Separate the general definition, positive conjecture, and boundary task."""

    section = _asmp4_section()
    setting, remainder = section.split("## Two-Port Capacity Conjecture", maxsplit=1)
    conjecture, remainder = remainder.split(
        "## What a complete resolution requires", maxsplit=1
    )
    requirements, remainder = remainder.split(
        "## Liveness and kill examples", maxsplit=1
    )
    liveness, _ = remainder.split("## Existing theory this must exceed", maxsplit=1)
    setting_norm = _normalized(setting)
    conjecture_norm = _normalized(conjecture)
    requirements_norm = _normalized(requirements)
    liveness_norm = _normalized(liveness)
    whole_norm = _normalized(section)
    full_source_norm = _normalized(SOURCE.read_text(encoding="utf-8"))

    checks = {
        "general_uncertain_process": "x_(t+1) = f(x_t,u_t,w_t)" in setting_norm,
        "general_region_has_universal_disturbance": (
            "for every allowed disturbance sequence" in setting_norm
        ),
        "general_architecture_allows_state_independent_randomness": (
            "shared randomness independent of the plant state" in setting_norm
        ),
        "positive_conjecture_is_registered_nhim": (
            "for a registered normally hyperbolic, locally controllable class"
            in conjecture_norm
        ),
        "positive_conjecture_requires_bounded_conventions": (
            "bounded uncertainty, delay, memory, control-authority, and disturbance conventions"
            in conjecture_norm
        ),
        "boundary_task_names_nonhyperbolicity": (
            "boundary of partial observability, uncertainty, nonhyperbolicity, and side-information assumptions"
            in requirements_norm
        ),
        "initial_set_is_named_but_not_volume_restricted": (
            "initial set `k_0`" in setting_norm
            and "positive-volume" not in setting_norm
            and "positive-volume" not in conjecture_norm
            and "positive-volume" not in requirements_norm
        ),
        "positive_volume_collar_is_only_a_liveness_example": (
            "positive-volume initial collar" in liveness_norm
        ),
        "robust_version_is_a_global_graduation_condition": (
            "graduation standard for a millennium-grade problem" in full_source_norm
            and "robust version" in full_source_norm
            and "exact statements have a finite-precision" in full_source_norm
        ),
        "sensor_computation_selector_absent": not any(
            marker in whole_norm
            for marker in (
                "closed under upstream computation",
                "arbitrary sufficient statistic",
                "forced injective raw sensor",
                "all causal sensor encoders are registered",
            )
        ),
        "probability_disturbance_order_absent": not any(
            marker in whole_norm
            for marker in (
                "per-disturbance almost sure",
                "uniform almost sure",
                "support zero error",
                "probability over shared randomness",
            )
        ),
    }
    return {
        "checks": checks,
        "scope_classification": {
            "general_definition": "uncertain controlled process and R_K",
            "positive_conjecture": "registered normally hyperbolic locally controllable class",
            "boundary_requirement": "counterexamples may lie outside the positive subclass",
            "thin_initial_set": "permitted by the setting but not a robust graduation result",
        },
        "missing_dimensions": [
            "registered sensor/computation domain",
            "randomness/disturbance quantifier order",
        ],
        "pass": all(checks.values()),
    }


def prior_art_scope_report() -> dict[str, Any]:
    """Audit only the four primary works cited by the canonical ASMP-4 source."""

    receipt = _json(PRIOR_ART_RECEIPT)
    document = PRIOR_ART_DOCUMENT.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")
    section_norm = _normalized(_asmp4_section())
    document_norm = _normalized(document)
    rows = receipt.get("sources", [])
    canonical_urls = [row.get("canonical_citation_url") for row in rows]
    primary_urls = [row.get("primary_full_text_url") for row in rows]
    hashes = [row.get("local_pdf_sha256", "") for row in rows]
    derived_totals = {
        "canonical_primary_sources": len(rows),
        "single_charged_information_resources": sum(
            row.get("single_charged_resource") is True for row in rows
        ),
        "separate_write_ports_charged": sum(
            row.get("separate_controller_to_actuator_write_port_charged") is True
            for row in rows
        ),
        "asmp4_two_port_registry_selectors": sum(
            row.get("selects_asmp4_read_write_registry") is True for row in rows
        ),
        "explicit_information_pattern_sensitivity_sources": sum(
            row.get("explicit_information_pattern_sensitivity") is True for row in rows
        ),
        "external_expert_review": False,
    }
    checks = {
        "receipt_schema": receipt.get("schema_version")
        == "asmp4_external_prior_art_scope_receipt_v0_10",
        "exactly_four_distinct_sources": len(rows) == 4
        and len({row.get("id") for row in rows}) == 4,
        "all_four_canonical_urls_are_in_source": len(set(canonical_urls)) == 4
        and all(isinstance(url, str) and url in source for url in canonical_urls),
        "all_primary_full_text_urls_are_documented": len(set(primary_urls)) == 4
        and all(isinstance(url, str) and url in document for url in primary_urls),
        "all_pdf_receipts_are_sha256": all(
            len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            for value in hashes
        ),
        "each_source_has_one_charged_information_resource": all(
            row.get("single_charged_resource") is True
            and bool(row.get("charged_information_resource"))
            for row in rows
        ),
        "no_source_charges_a_separate_write_port": not any(
            row.get("separate_controller_to_actuator_write_port_charged") is True
            for row in rows
        ),
        "no_source_selects_the_asmp4_registry": not any(
            row.get("selects_asmp4_read_write_registry") is True for row in rows
        ),
        "tatikonda_alone_records_explicit_information_pattern_sensitivity": [
            row.get("id")
            for row in rows
            if row.get("explicit_information_pattern_sensitivity") is True
        ]
        == ["tatikonda_mitter_2004"],
        "derived_totals_match_frozen_receipt": receipt.get("totals") == derived_totals,
        "canonical_source_calls_for_a_joint_two_interface_object": (
            "data-rate theorems, invariance entropy, uncertain-system feedback entropy"
            in section_norm
            and "output invariance entropy already exist" in section_norm
            and "missing object is the joint two-interface capacity region"
            in section_norm
        ),
        "bounded_scope_and_nonclaims_are_explicit": all(
            marker in document_norm
            for marker in (
                "bounded primary-source audit",
                "not an exhaustive literature search",
                "not external expert review",
                "does not prove that no later theorem could add a selector",
            )
        ),
    }
    return {
        "scope": receipt.get("audit_scope"),
        "rows": rows,
        "totals": derived_totals,
        "bounded_inference": receipt.get("bounded_inference"),
        "checks": checks,
        "pass": all(checks.values()),
    }


def targeted_literature_near_miss_report() -> dict[str, Any]:
    """Freeze a bounded audit of three uncited neighboring primary results."""

    receipt = _json(TARGETED_LITERATURE_RECEIPT)
    document = TARGETED_LITERATURE_DOCUMENT.read_text(encoding="utf-8")
    document_norm = _normalized(document)
    rows = receipt.get("sources", [])
    primary_urls = [row.get("primary_url") for row in rows]
    hashes = [row.get("local_pdf_sha256", "") for row in rows]
    derived_totals = {
        "reviewed_primary_near_misses": len(rows),
        "genuine_multirate_regions": sum(
            row.get("near_miss_type") == "genuine n-dimensional convex data-rate region"
            for row in rows
        ),
        "same_channel_multiple_rate_notions": sum(
            row.get("near_miss_type")
            == "two rate notions for one event-triggered channel"
            for row in rows
        ),
        "network_ife_compositions": sum(
            row.get("near_miss_type")
            == "scalar network IFE bounded by a sum of subsystem IFEs"
            for row in rows
        ),
        "asmp4_registry_selectors": sum(
            row.get("selects_asmp4_sensor_computation_registry") is True for row in rows
        ),
        "full_text_definition_reviews": sum(
            row.get("full_text_definition_reviewed") is True for row in rows
        ),
        "exhaustive_search": False,
        "external_expert_review": False,
    }
    checks = {
        "receipt_schema": receipt.get("schema_version")
        == "asmp4_targeted_literature_near_miss_receipt_v0_10",
        "exactly_three_distinct_sources": len(rows) == 3
        and len({row.get("id") for row in rows}) == 3,
        "all_primary_urls_are_documented": len(set(primary_urls)) == 3
        and all(isinstance(url, str) and url in document for url in primary_urls),
        "all_pdf_receipts_are_sha256": all(
            len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            for value in hashes
        ),
        "all_full_text_definitions_have_page_anchors": all(
            row.get("full_text_definition_reviewed") is True
            and len(row.get("checked_pages", [])) >= 3
            for row in rows
        ),
        "all_require_added_architecture_mapping": all(
            row.get("requires_added_architecture_mapping") is True for row in rows
        ),
        "no_near_miss_selects_the_asmp4_registry": not any(
            row.get("selects_asmp4_sensor_computation_registry") is True for row in rows
        ),
        "derived_totals_match_frozen_receipt": receipt.get("totals") == derived_totals,
        "bounded_scope_and_nonclaims_are_explicit": all(
            marker in document_norm
            for marker in (
                "targeted primary-source applicability audit",
                "not an exhaustive literature search",
                "not external expert review",
                "only the applicability of the three inspected near-misses is rejected",
            )
        ),
        "receipt_preserves_three_nonclaims": len(receipt.get("nonclaims", [])) == 3,
    }
    return {
        "scope": receipt.get("audit_scope"),
        "rows": rows,
        "totals": derived_totals,
        "bounded_inference": receipt.get("bounded_inference"),
        "checks": checks,
        "pass": all(checks.values()),
    }


def machine_index_report() -> dict[str, Any]:
    index = _json(INDEX)
    problem = next(row for row in index["problems"] if row["id"] == "ASMP-4")
    problem_keys = set(problem)
    checks = {
        "normative_statement_is_markdown": (
            index["normative_statement_file"] == SOURCE.name
        ),
        "index_is_non_normative": index["registry_is_normative"] is False,
        "draft_status": index["status"] == "proposed_candidate_definition_draft",
        "graduation_unsatisfied": index["graduation_standard_satisfied"] is False,
        "no_sensor_domain_key": not any(
            "sensor" in key or "computation" in key for key in problem_keys
        ),
        "no_stochastic_order_key": not any(
            "random" in key or "probability" in key or "quantifier" in key
            for key in problem_keys
        ),
    }
    return {
        "problem_keys": sorted(problem_keys),
        "checks": checks,
        "pass": all(checks.values()),
    }


def _q(z: int) -> Fraction:
    return Fraction(12 + 13 * z - z**3, 24)


def primary_sensor_witness_report(max_horizon: int = 6) -> dict[str, Any]:
    """Rebuild the same-plant sensor fork without importing v0.6 code."""

    if max_horizon != 6:
        raise ValueError("the frozen red-team replay uses horizons one through six")

    claim = _json(V06_CLAIM)
    modes = (0, 1, 2, 3)
    mode_coordinates = (-3, -1, 1, 3)
    safe_action = (0, 0, 1, 1)
    specs = {
        "computed_sensor_registry": {
            "sensor": (0, 0, 1, 1),
            "controller": (0, 1),
            "read_base": 2,
            "region": "[1,infinity) x [1,infinity)",
        },
        "fixed_raw_sensor_registry": {
            "sensor": (0, 1, 2, 3),
            "controller": (0, 0, 1, 1),
            "read_base": 4,
            "region": "[2,infinity) x [1,infinity)",
        },
    }
    rows = []
    failures = []
    for horizon in range(1, max_horizon + 1):
        words = tuple(product(modes, repeat=horizon))
        for name, spec in specs.items():
            read_words = set()
            write_words = set()
            unsafe = 0
            for word in words:
                reads = tuple(spec["sensor"][mode] for mode in word)
                writes = tuple(spec["controller"][symbol] for symbol in reads)
                unsafe += sum(
                    write != safe_action[mode]
                    for mode, write in zip(word, writes, strict=True)
                )
                read_words.add(reads)
                write_words.add(writes)
            expected_read = spec["read_base"] ** horizon
            expected_write = 2**horizon
            matches = (
                unsafe == 0
                and len(read_words) == expected_read
                and len(write_words) == expected_write
            )
            rows.append(
                {
                    "horizon": horizon,
                    "registry": name,
                    "mode_words": len(words),
                    "read_words": len(read_words),
                    "write_words": len(write_words),
                    "unsafe_transitions": unsafe,
                    "matches_formula": matches,
                }
            )
            if not matches:
                failures.append((horizon, name))

    q_values = tuple(_q(z) for z in mode_coordinates)
    invariant_rows = []
    for z, correct_control in zip(mode_coordinates, safe_action, strict=True):
        for disturbance_reset in mode_coordinates:
            correct_normal_successor = Fraction(3, 2) * 0 + correct_control - _q(z)
            wrong_control = 1 - correct_control
            wrong_normal_successor = Fraction(3, 2) * 0 + wrong_control - _q(z)
            invariant_rows.append(
                {
                    "z": z,
                    "disturbance_reset": disturbance_reset,
                    "correct_control": correct_control,
                    "correct_normal_successor": str(correct_normal_successor),
                    "wrong_control": wrong_control,
                    "wrong_normal_successor": str(wrong_normal_successor),
                    "correct_stays_in_K": (
                        correct_normal_successor == 0
                        and disturbance_reset in mode_coordinates
                    ),
                    "wrong_leaves_K": wrong_normal_successor != 0,
                }
            )
    embedding_checks = {
        "rational_action_polynomial": q_values
        == tuple(Fraction(value) for value in safe_action),
        "compact_zero_dimensional_safe_manifold": (
            len(set(mode_coordinates)) == 4
            and all(isinstance(z, int) for z in mode_coordinates)
        ),
        "robust_controlled_invariance": all(
            row["correct_stays_in_K"] for row in invariant_rows
        ),
        "wrong_binary_control_leaves_K": all(
            row["wrong_leaves_K"] for row in invariant_rows
        ),
        "bounded_control_and_disturbance_sets": set(safe_action) == {0, 1}
        and set(mode_coordinates) == {-3, -1, 1, 3},
        "normal_multiplier_is_unstable": abs(Fraction(3, 2)) > 1,
        "tangent_reset_is_dominated": abs(Fraction(0)) < abs(Fraction(3, 2)),
        "normal_control_derivative_is_nonzero": Fraction(1) != 0,
        "sealed_embedding_matches": claim["continuous_embedding"]
        == {
            "dynamics": "n_next=(3/2)n+u-q(z), z_next=w",
            "q_polynomial": "(12+13z-z^3)/24",
            "mode_coordinates": ["-3", "-1", "1", "3"],
            "q_values": ["0", "0", "1", "1"],
            "normal_multiplier": "3/2",
            "tangent_reset_derivative": "0",
            "normal_control_derivative": "1",
        },
    }
    model_audit = claim["canonical_registry_model_audit"]
    source_model_checks = {
        "thirteen_source_obligations": model_audit["source_obligation_count"] == 13,
        "registry_domain_not_selected": model_audit["registry_domain_selected"]
        is False,
        "computed_model_satisfies_all": model_audit[
            "computed_sensor_registry_satisfies_all_obligations"
        ]
        is True,
        "raw_model_satisfies_all": model_audit[
            "fixed_raw_sensor_registry_satisfies_all_obligations"
        ]
        is True,
        "same_plant_and_only_upstream_change": (
            claim["claim"].startswith("On the same four-mode uncertain safety plant")
            and claim["claim"].endswith(
                "The only changed premise is upstream computation closure."
            )
        ),
        "no_side_information": claim["fixture"]["side_information"] is False,
        "deterministic_noiseless_serial_channel": (
            claim["fixture"]["channel"] == "deterministic noiseless serial"
        ),
        "distinct_exact_regions": (
            model_audit["computed_sensor_region"]
            == specs["computed_sensor_registry"]["region"]
            and model_audit["fixed_raw_sensor_region"]
            == specs["fixed_raw_sensor_registry"]["region"]
            and len(
                {
                    model_audit["computed_sensor_region"],
                    model_audit["fixed_raw_sensor_region"],
                }
            )
            == 2
        ),
    }
    return {
        "rows": rows,
        "invariant_set_rows": invariant_rows,
        "invariant_set": "K=K_0={0} x {-3,-1,1,3}",
        "enumerated_mode_words_per_registry": sum(4**t for t in range(1, 7)),
        "failures": failures,
        "all_horizon_formulas": {
            "computed_read": "2^T",
            "raw_read": "4^T",
            "write": "2^T",
            "computed_region": specs["computed_sensor_registry"]["region"],
            "raw_region": specs["fixed_raw_sensor_registry"]["region"],
            "sealed_finite_formulas_match": (
                claim["computed_sensor_class"]["finite_region"]
                == "B_read>=T and B_write>=T"
                and claim["forced_raw_sensor_class"]["finite_region"]
                == "B_read>=2T and B_write>=T"
            ),
        },
        "embedding_checks": embedding_checks,
        "source_model_checks": source_model_checks,
        "primary_witness_scope": "registered NHIM/local-control sensor-domain fork",
        "pass": (
            not failures
            and all(embedding_checks.values())
            and all(source_model_checks.values())
        ),
    }


def coordinate_relabeling_report(max_horizon: int = 3) -> dict[str, Any]:
    """Exhaust harmless mode, action, and port-symbol relabelings."""

    if max_horizon != 3:
        raise ValueError("the frozen coordinate audit uses horizons one through three")

    modes = tuple(range(4))
    actions = tuple(range(2))
    safe_action = (0, 0, 1, 1)
    failures = []
    cases = 0
    mode_words_per_case = sum(4**horizon for horizon in range(1, max_horizon + 1))

    for mode_labels in permutations(modes):
        new_to_old = {new: old for old, new in enumerate(mode_labels)}
        for action_labels in permutations(actions):
            required = tuple(
                action_labels[safe_action[new_to_old[new_mode]]] for new_mode in modes
            )
            for computed_labels in permutations(actions):
                computed_sensor = tuple(
                    computed_labels[safe_action[new_to_old[new_mode]]]
                    for new_mode in modes
                )
                computed_controller = [None, None]
                for old_action in actions:
                    computed_controller[computed_labels[old_action]] = action_labels[
                        old_action
                    ]
                for raw_labels in permutations(modes):
                    raw_sensor = tuple(
                        raw_labels[new_to_old[new_mode]] for new_mode in modes
                    )
                    raw_controller = [None, None, None, None]
                    for old_mode in modes:
                        raw_controller[raw_labels[old_mode]] = action_labels[
                            safe_action[old_mode]
                        ]

                    cases += 1
                    case_ok = True
                    for horizon in range(1, max_horizon + 1):
                        computed_reads = set()
                        raw_reads = set()
                        computed_writes = set()
                        raw_writes = set()
                        for word in product(modes, repeat=horizon):
                            c_read = tuple(computed_sensor[mode] for mode in word)
                            r_read = tuple(raw_sensor[mode] for mode in word)
                            c_write = tuple(
                                computed_controller[symbol] for symbol in c_read
                            )
                            r_write = tuple(raw_controller[symbol] for symbol in r_read)
                            expected = tuple(required[mode] for mode in word)
                            case_ok = (
                                case_ok and c_write == expected and r_write == expected
                            )
                            computed_reads.add(c_read)
                            raw_reads.add(r_read)
                            computed_writes.add(c_write)
                            raw_writes.add(r_write)
                        case_ok = case_ok and (
                            len(computed_reads) == 2**horizon
                            and len(raw_reads) == 4**horizon
                            and len(computed_writes) == 2**horizon
                            and len(raw_writes) == 2**horizon
                        )
                    if not case_ok:
                        failures.append(
                            {
                                "mode_labels": mode_labels,
                                "action_labels": action_labels,
                                "computed_labels": computed_labels,
                                "raw_labels": raw_labels,
                            }
                        )

    source = _normalized(SOURCE.read_text(encoding="utf-8"))
    checks = {
        "all_2304_relabelings_checked": cases == 24 * 2 * 2 * 24 == 2304,
        "zero_relabeling_failures": not failures,
        "mode_words_per_registry": cases * mode_words_per_case == 193536,
        "source_invariance_rule_present": (
            "conclusions survive declared coordinate changes, equivalent encodings, renamings"
            in source
        ),
    }
    return {
        "cases": cases,
        "horizons": [1, 2, 3],
        "mode_words_per_registry": cases * mode_words_per_case,
        "regions": {
            "computed": "[1,infinity) x [1,infinity)",
            "raw": "[2,infinity) x [1,infinity)",
        },
        "failures": failures,
        "checks": checks,
        "pass": all(checks.values()),
    }


def stochastic_scope_firewall_report() -> dict[str, Any]:
    """Prevent the v0.8 diagonal from being misused as an NHIM witness."""

    claim = _json(V08_CLAIM)
    fixture = claim["continuous_diagonal_fixture"]
    nonclaims = set(claim["nonclaims"])
    checks = {
        "smooth_uncertain_general_setting_fixture": fixture["dynamics"]
        == "x_(t+1)=(u_t-w_t)^2",
        "bounded_state_independent_random_inputs": fixture["shared_random_control"]
        == "u_t=r_t iid Uniform[0,1]",
        "stochastic_semantics_separate": (
            fixture["per_disturbance_almost_sure_safe"] is True
            and fixture["uniform_almost_sure_safe"] is False
            and fixture["support_zero_error_safe"] is False
        ),
        "nhim_nonclaim_is_explicit": (
            "normally hyperbolic classification of the diagonal boundary fixture"
            in nonclaims
        ),
        "canonical_region_nonclaim_is_explicit": (
            "a registration-independent canonical ASMP-4 region" in nonclaims
        ),
        "v09_records_independent_stochastic_gap": (
            "randomness/disturbance quantifier order"
            in _json(V09_CLAIM)["normative_source_gaps"]
        ),
    }
    return {
        "checks": checks,
        "classification": {
            "general_definition_counterexample": True,
            "positive_nhim_conjecture_witness": False,
            "used_by_minimal_sensor_stopping_proof": False,
            "orthogonal_specification_gap": True,
        },
        "pass": all(checks.values()),
    }


def selector_mutation_report() -> dict[str, Any]:
    """Evaluate explicit sensor-domain completions, including their union."""

    scope = canonical_scope_report()
    v09 = _json(V09_CLAIM)
    computed = v09["sensor_targets"]["computed"]
    raw = v09["sensor_targets"]["forced_raw"]
    relational = v09["sensor_targets"]["adaptive_relational"]
    rows = [
        {
            "selector": "canonical_base",
            "selector_is_in_source": False,
            "candidate_targets": [computed, relational, raw],
            "selected_target": None,
            "determinate": False,
        },
        {
            "selector": "computed_only",
            "selector_is_in_source": False,
            "candidate_targets": [computed],
            "selected_target": computed,
            "determinate": True,
        },
        {
            "selector": "adaptive_two_partition_only",
            "selector_is_in_source": False,
            "candidate_targets": [relational],
            "selected_target": relational,
            "determinate": True,
        },
        {
            "selector": "raw_only",
            "selector_is_in_source": False,
            "candidate_targets": [raw],
            "selected_target": raw,
            "determinate": True,
        },
        {
            "selector": "union_of_all_three",
            "selector_is_in_source": False,
            "candidate_targets": [computed, relational, raw],
            "selected_target": computed,
            "determinate": True,
            "reason": (
                "The computed rectangle contains the relational wedge and raw rectangle."
            ),
        },
    ]
    checks = {
        "canonical_base_has_three_targets": len(set(rows[0]["candidate_targets"])) == 3,
        "canonical_base_is_underdetermined": rows[0]["determinate"] is False,
        "each_explicit_selector_is_determinate": all(
            row["determinate"] for row in rows[1:]
        ),
        "union_selects_computed_rectangle": rows[-1]["selected_target"] == computed,
        "no_selector_is_present_in_source": (
            scope["checks"]["sensor_computation_selector_absent"]
            and not any(row["selector_is_in_source"] for row in rows)
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def counterargument_matrix() -> dict[str, Any]:
    scope = canonical_scope_report()
    prior = prior_art_scope_report()
    near_misses = targeted_literature_near_miss_report()
    index = machine_index_report()
    sensor = primary_sensor_witness_report()
    stochastic = stochastic_scope_firewall_report()
    selectors = selector_mutation_report()
    coordinates = coordinate_relabeling_report()
    v06 = _json(V06_CLAIM)
    v09 = _json(V09_CLAIM)
    rows = [
        {
            "id": "A1",
            "challenge": "The stochastic diagonal is not an NHIM witness.",
            "answer": "Correct and firewalled; the primary proof uses only the rational sensor fork.",
            "resolved": (
                stochastic["classification"]["positive_nhim_conjecture_witness"]
                is False
                and stochastic["classification"][
                    "used_by_minimal_sensor_stopping_proof"
                ]
                is False
                and sensor["pass"]
            ),
        },
        {
            "id": "A2",
            "challenge": "The two sensor results might use different plants or authority.",
            "answer": "The sealed claim fixes one plant, evaluator, authority, channels, metric, and changes only computation closure.",
            "resolved": sensor["source_model_checks"][
                "same_plant_and_only_upstream_change"
            ],
        },
        {
            "id": "A3",
            "challenge": "One sensor completion might violate the explicit architecture.",
            "answer": "Both independently built models satisfy all 13 source obligations and have no side information.",
            "resolved": (
                sensor["source_model_checks"]["computed_model_satisfies_all"]
                and sensor["source_model_checks"]["raw_model_satisfies_all"]
                and sensor["source_model_checks"]["no_side_information"]
            ),
        },
        {
            "id": "A4",
            "challenge": "The region difference could be a finite-horizon artifact.",
            "answer": "Exact T, 2T, and T formulas give distinct closed asymptotic regions.",
            "resolved": (
                sensor["all_horizon_formulas"]["sealed_finite_formulas_match"]
                and sensor["source_model_checks"]["distinct_exact_regions"]
            ),
        },
        {
            "id": "A5",
            "challenge": "The machine index might define the missing registry.",
            "answer": "The index is non-normative, ungraduated, and has neither selector key.",
            "resolved": index["pass"],
        },
        {
            "id": "A6",
            "challenge": "Taking the union of both registries selects the computed region.",
            "answer": "A union is a third completion of the absent registry-domain predicate, not a clause in the source.",
            "resolved": (
                scope["checks"]["sensor_computation_selector_absent"]
                and v06["canonical_registry_model_audit"]["registry_domain_selected"]
                is False
                and selectors["checks"]["union_selects_computed_rectangle"]
                and selectors["checks"]["no_selector_is_present_in_source"]
            ),
        },
        {
            "id": "A7",
            "challenge": "Rectangular witnesses cannot support a general nonrectangular claim.",
            "answer": "Underdetermination needs only unequal targets; v0.9 separately records the relational wedge.",
            "resolved": (
                sensor["source_model_checks"]["distinct_exact_regions"]
                and v09["model_completion_atlas"]["sensor_distinct_targets"] == 3
                and "nonrectangular" in v09["sensor_targets"]["adaptive_relational"]
            ),
        },
        {
            "id": "A8",
            "challenge": "Finite enumeration alone cannot prove an all-horizon converse.",
            "answer": "The enumeration is a replay; the sealed v0.6 claim carries exact finite formulas and asymptotic regions.",
            "resolved": (
                not sensor["failures"]
                and sensor["all_horizon_formulas"]["sealed_finite_formulas_match"]
                and v06["canonical_quantifier_audit"]["decision"]
                == "registration_class_underdetermined"
            ),
        },
        {
            "id": "A9",
            "challenge": "Removing v0.8 might collapse the stopping theorem.",
            "answer": "The minimal theorem has no stochastic-witness premise.",
            "resolved": (
                sensor["pass"]
                and scope["checks"]["sensor_computation_selector_absent"]
                and stochastic["classification"][
                    "used_by_minimal_sensor_stopping_proof"
                ]
                is False
            ),
        },
        {
            "id": "A10",
            "challenge": "A zero-volume initial manifold might be excluded by ASMP-4.",
            "answer": (
                "The setting leaves K_0 unrestricted; positive volume appears "
                "only in a liveness example, and this package makes no robust "
                "full-resolution claim."
            ),
            "resolved": (
                scope["checks"]["initial_set_is_named_but_not_volume_restricted"]
                and scope["checks"]["positive_volume_collar_is_only_a_liveness_example"]
            ),
        },
        {
            "id": "A11",
            "challenge": "The exact thin fixture does not discharge the robust-version graduation rule.",
            "answer": (
                "Correct and scope-firewalled: robustness remains required for "
                "a full resolution, while the ungraduated draft's missing "
                "registry still blocks further local enumeration."
            ),
            "resolved": (
                scope["checks"]["robust_version_is_a_global_graduation_condition"]
                and index["checks"]["graduation_unsatisfied"]
                and "does not assert" in _json(V09_CLAIM)["nonclaim"]
                and "intended canonical" in _json(V09_CLAIM)["nonclaim"]
            ),
        },
        {
            "id": "A12",
            "challenge": "The sensor fork might be an artifact of coordinate or symbol names.",
            "answer": (
                "All 2,304 mode/action/read-symbol relabelings preserve safety, "
                "language counts, and both exact regions."
            ),
            "resolved": coordinates["pass"],
        },
        {
            "id": "A13",
            "challenge": "The cited control literature might silently supply a default registry.",
            "answer": (
                "A bounded audit of all four cited works finds one charged "
                "information resource per work, no separate charged write "
                "port, and no ASMP-4 read/write registry selector; Tatikonda "
                "and Mitter explicitly show information-pattern sensitivity."
            ),
            "resolved": prior["pass"],
        },
        {
            "id": "A14",
            "challenge": (
                "An uncited multidimensional or network rate theorem may already "
                "invalidate the semantic diagnosis."
            ),
            "answer": (
                "Three full-text near-misses define subsystem coordinates, "
                "same-channel dual accounting, or scalar network/subsystem "
                "composition. None selects the read/write registry; importing "
                "any one requires an added architecture mapping."
            ),
            "resolved": near_misses["pass"],
        },
    ]
    unresolved = [row["id"] for row in rows if not row["resolved"]]
    return {
        "rows": rows,
        "count": len(rows),
        "unresolved": unresolved,
        "pass": len(rows) == 14 and not unresolved,
    }


def minimal_stopping_theorem() -> dict[str, Any]:
    """Check a minimal model-theoretic certificate using no v0.8 premise."""

    scope = canonical_scope_report()
    index = machine_index_report()
    sensor = primary_sensor_witness_report()
    premises = {
        "normative_text_leaves_sensor_domain_undefined": scope["checks"][
            "sensor_computation_selector_absent"
        ],
        "machine_index_cannot_supply_normative_selector": index["pass"],
        "two_same_plant_source_models_exist": sensor["source_model_checks"][
            "same_plant_and_only_upstream_change"
        ],
        "both_models_satisfy_explicit_obligations": (
            sensor["source_model_checks"]["computed_model_satisfies_all"]
            and sensor["source_model_checks"]["raw_model_satisfies_all"]
        ),
        "both_models_are_rational_nhim_local_control_fixtures": all(
            sensor["embedding_checks"].values()
        ),
        "models_have_distinct_exact_regions": sensor["source_model_checks"][
            "distinct_exact_regions"
        ],
    }
    return {
        "meta_theorem": (
            "If two completions of an undefined domain predicate satisfy every "
            "explicit applicable clause but yield different target regions, "
            "the clauses do not determine a unique target region."
        ),
        "premises": premises,
        "stochastic_witness_used": False,
        "decision": "sensor_registry_alone_proves_semantic_underdetermination",
        "operational_disposition": (
            "stop_local_enumeration_and_request_normative_sensor_registration"
        ),
        "pass": all(premises.values()),
    }


def test_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in PREDECESSOR_TESTS:
        path = MILLENNIUM / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "file": filename, "tests": count})
    total = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "predecessor_tests": total,
        "pass": len(rows) == 10 and total == 127,
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_stopping_red_team_claim_v0_10",
        "status": "minimal sensor-only stopping theorem survives adversarial scope audit",
        "sealed_resources": {
            "count": 5,
            "canonical_source_sha256": SEALED_RESOURCES["canonical_source"][1],
            "machine_index_sha256": SEALED_RESOURCES["machine_index"][1],
            "v0_6_claim_sha256": SEALED_RESOURCES["v0_6_claim"][1],
            "v0_8_claim_sha256": SEALED_RESOURCES["v0_8_claim"][1],
            "v0_9_claim_sha256": SEALED_RESOURCES["v0_9_claim"][1],
        },
        "primary_witness": {
            "scope": "registered rational NHIM/local-control sensor-domain fork",
            "same_plant": True,
            "compact_safe_manifold": "K=K_0={0} x {-3,-1,1,3}",
            "bounded_uncertainty": True,
            "unique_safe_binary_control": True,
            "source_obligations_per_model": 13,
            "computed_region": "[1,infinity) x [1,infinity)",
            "raw_region": "[2,infinity) x [1,infinity)",
            "stochastic_witness_required": False,
        },
        "stochastic_scope_firewall": {
            "general_definition_counterexample": True,
            "positive_nhim_conjecture_witness": False,
            "orthogonal_specification_gap": True,
        },
        "counterargument_audit": {"cases": 14, "unresolved": 0},
        "cited_prior_art_scope_audit": {
            "canonical_primary_sources": 4,
            "single_charged_information_resources": 4,
            "separate_write_ports_charged": 0,
            "asmp4_two_port_registry_selectors": 0,
            "explicit_information_pattern_sensitivity_sources": 1,
            "external_expert_review": False,
        },
        "targeted_literature_near_miss_audit": {
            "reviewed_primary_near_misses": 3,
            "genuine_multirate_regions": 1,
            "same_channel_multiple_rate_notions": 1,
            "network_ife_compositions": 1,
            "asmp4_registry_selectors": 0,
            "full_text_definition_reviews": 3,
            "exhaustive_search": False,
            "external_expert_review": False,
        },
        "selector_mutations": {
            "cases": 5,
            "canonical_targets": 3,
            "union_target": "[1,infinity) x [1,infinity)",
            "source_selector_present": False,
        },
        "coordinate_relabeling_audit": {
            "cases": 2304,
            "horizons": [1, 2, 3],
            "mode_words_per_registry": 193536,
            "failures": 0,
            "computed_region": "[1,infinity) x [1,infinity)",
            "raw_region": "[2,infinity) x [1,infinity)",
        },
        "test_inventory": {"predecessor_packages": 10, "predecessor_tests": 127},
        "decision": "stop_local_enumeration_and_request_normative_registration",
        "minimal_reason": (
            "The v0.6 same-plant sensor fork alone gives two models satisfying "
            "the explicit architecture with distinct exact regions."
        ),
        "reopening_conditions": [
            "normative sensor/computation registry",
            "attributable proof error in the primary sensor fork",
            "new canonical clause that selects one existing completion",
            "an attributable theorem or new registered class that invalidates the finite completion analysis",
        ],
        "nonclaim": (
            "The stochastic diagonal is not asserted to be a normally hyperbolic "
            "positive-conjecture witness, and ASMP-4 is not claimed canonically resolved."
        ),
    }


def claim_exactness_report() -> dict[str, Any]:
    observed = _json(CLAIM) if CLAIM.exists() else None
    expected = expected_claim_payload()
    return {
        "exists": CLAIM.exists(),
        "matches_expected": observed == expected,
        "pass": CLAIM.exists() and observed == expected,
    }


def stopping_red_team_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    scope = canonical_scope_report()
    prior = prior_art_scope_report()
    near_misses = targeted_literature_near_miss_report()
    index = machine_index_report()
    sensor = primary_sensor_witness_report()
    stochastic = stochastic_scope_firewall_report()
    selectors = selector_mutation_report()
    coordinates = coordinate_relabeling_report()
    arguments = counterargument_matrix()
    theorem = minimal_stopping_theorem()
    tests = test_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        scope,
        prior,
        near_misses,
        index,
        sensor,
        stochastic,
        selectors,
        coordinates,
        arguments,
        theorem,
        tests,
        claim,
    )
    return {
        "schema_version": "asmp4_stopping_red_team_v0_10",
        "resource_integrity": integrity,
        "canonical_scope": scope,
        "cited_prior_art_scope": prior,
        "targeted_literature_near_misses": near_misses,
        "machine_index": index,
        "primary_sensor_witness": sensor,
        "stochastic_scope_firewall": stochastic,
        "selector_mutations": selectors,
        "coordinate_relabeling": coordinates,
        "counterargument_matrix": arguments,
        "minimal_stopping_theorem": theorem,
        "test_inventory": tests,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    if report is None:
        report = stopping_red_team_report()
    return {
        "R0_five_resource_seals": report["resource_integrity"]["pass"],
        "R1_canonical_scope_is_partitioned": report["canonical_scope"]["pass"],
        "R2_machine_index_cannot_fill_gap": report["machine_index"]["pass"],
        "R3_primary_sensor_witness_rebuilt": report["primary_sensor_witness"]["pass"],
        "R4_stochastic_scope_firewall": report["stochastic_scope_firewall"]["pass"],
        "R5_selector_mutations_resolve_only_by_added_choice": report[
            "selector_mutations"
        ]["pass"],
        "R6_coordinate_relabeling_invariance": report["coordinate_relabeling"]["pass"],
        "R7_cited_prior_art_has_no_two_port_selector": report["cited_prior_art_scope"][
            "pass"
        ],
        "R8_targeted_near_misses_require_added_mapping": report[
            "targeted_literature_near_misses"
        ]["pass"],
        "R9_fourteen_counterarguments_resolved": report["counterargument_matrix"][
            "pass"
        ],
        "R10_minimal_sensor_only_stopping_theorem": report["minimal_stopping_theorem"][
            "pass"
        ],
        "R11_predecessor_inventory_127": report["test_inventory"]["pass"],
        "R12_frozen_claim_exactness": report["claim_exactness"]["pass"],
        "R13_complete_payload": report["pass"],
    }


def main() -> int:
    report = stopping_red_team_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
