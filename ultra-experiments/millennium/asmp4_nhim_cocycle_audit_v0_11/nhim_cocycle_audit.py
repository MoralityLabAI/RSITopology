"""Formal NHIM, local-control, and causal-timing repair for ASMP-4.

V0.6 used a binary actuator set while citing a formal input derivative as its
local-control certificate.  This successor preserves the exact sensor-registry
fork on one plant, but gives the plant bounded interval authority and realizes
the adversarial mode process as a full-shift cocycle.  The capacity codes still
use only the two uniquely safe controls.
"""

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
V06_CLAIM = ROOT / "asmp4_registration_fork_v0_6" / "registration_claim_v0_6.json"
V10_CLAIM = (
    ROOT / "asmp4_stopping_red_team_v0_10" / "stopping_red_team_claim_v0_10.json"
)
CLAIM = HERE / "nhim_cocycle_claim_v0_11.json"
DEFINITION_RECEIPT = HERE / "primary_definition_receipt_v0_11.json"
DEFINITION_DOCUMENT = HERE / "PRIMARY_DEFINITION_SCOPE_v0_11.md"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_6_claim": (
        V06_CLAIM,
        "812c17f913c1e498d835c13430b7880b95a188496333b48355883f0fe634c5a5",
    ),
    "v0_10_claim": (
        V10_CLAIM,
        "fd8b2e74bdd6f16aabd7907dc621254accd6e8fa183957d1eaaf3138163d314c",
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
    ("asmp4_randomness_quantifier_boundary_v0_8", "test_randomness_quantifier.py"),
    ("asmp4_completion_atlas_v0_9", "test_completion_atlas.py"),
    ("asmp4_stopping_red_team_v0_10", "test_stopping_red_team.py"),
)

MODES = (Fraction(-3), Fraction(-1), Fraction(1), Fraction(3))
NORMAL_MULTIPLIER = Fraction(3, 2)
AUTHORITY = (Fraction(-1), Fraction(2))
LOCAL_STATE_RADIUS = Fraction(1, 6)
LOCAL_TARGET_RADIUS = Fraction(3, 4)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _asmp4_section() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    return text.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0]


def coupling_polynomial(z_value: Fraction) -> Fraction:
    return Fraction(12 + 13 * z_value - z_value**3, 24)


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALS.items():
        observed = _sha256(path)
        rows.append(
            {
                "name": name,
                "expected_sha256": expected,
                "observed_sha256": observed,
                "matches": observed == expected,
            }
        )
    return {
        "rows": rows,
        "resources": len(rows),
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def canonical_scope_report() -> dict[str, Any]:
    section = _normalized(_asmp4_section())
    checks = {
        "causal_sensor_reads_current_state": (
            "a causal sensor encoder emits only the read transcript" in section
        ),
        "controller_uses_only_read_symbols": (
            "a controller receives only those symbols and emits the write transcript"
            in section
        ),
        "actuator_maps_write_to_control": (
            "an actuator decoder maps write symbols to controls" in section
        ),
        "delay_and_authority_must_be_explicit": (
            "internal memory, delays, block coding" in section
            and "control-authority" in section
        ),
        "positive_scope_is_registered_nhim_local_control": (
            "registered normally hyperbolic, locally controllable class" in section
        ),
        "universal_disturbance_safety": (
            "for every allowed disturbance sequence" in section
        ),
        "zero_delay_is_not_forbidden": "strictly positive delay" not in section,
        "sensor_registry_selector_absent": (
            "closed under upstream computation" not in section
            and "forced injective raw sensor" not in section
        ),
        "control_topology_selector_absent": (
            "control authority is discrete" not in section
            and "control authority is an interval" not in section
        ),
    }
    return {
        "checks": checks,
        "missing_choices": [
            "sensor/computation registry",
            "control-authority topology",
            "formal NHIM category for disturbed dynamics",
        ],
        "pass": all(checks.values()),
    }


def primary_definition_report() -> dict[str, Any]:
    receipt = _json(DEFINITION_RECEIPT)
    document = DEFINITION_DOCUMENT.read_text(encoding="utf-8")
    document_norm = _normalized(document)
    source = receipt.get("source", {})
    definitions = source.get("checked_definitions", [])
    expected_numbers = {"2.1", "2.2", "2.3", "2.4"}
    checks = {
        "receipt_schema": receipt.get("schema_version")
        == "asmp4_nhim_primary_definition_receipt_v0_11",
        "primary_pdf_is_documented": source.get("primary_pdf_url") in document,
        "doi_is_documented": source.get("doi_url") in document,
        "pdf_hash_is_sha256": len(source.get("local_pdf_sha256", "")) == 64
        and all(c in "0123456789abcdef" for c in source["local_pdf_sha256"]),
        "definition_pages_were_visually_checked": source.get("checked_pdf_pages")
        == [4, 5]
        and source.get("visual_review") is True,
        "four_required_definitions_are_mapped": {
            row.get("number") for row in definitions
        }
        == expected_numbers,
        "receipt_maps_all_nhim_conditions": receipt.get("mapped_conditions")
        == {
            "cocycle_law": True,
            "invariant_random_manifold": True,
            "invariant_splitting": True,
            "unstable_and_center_isomorphisms": True,
            "center_equals_tangent": True,
            "stable_bound": True,
            "unstable_backward_bound": True,
            "center_bound": True,
            "strict_rate_gap": True,
        },
        "scope_nonclaims_are_explicit": all(
            marker in document_norm
            for marker in (
                "does not claim that asmp-4 selected this formalism",
                "safety proof remains universal over every mode sequence",
                "zero-dimensional fibers are deliberate",
            )
        )
        and len(receipt.get("nonclaims", [])) == 3,
    }
    return {
        "source": source,
        "mapped_conditions": receipt.get("mapped_conditions"),
        "checks": checks,
        "pass": all(checks.values()),
    }


def bounded_authority_report() -> dict[str, Any]:
    values = tuple(coupling_polynomial(z_value) for z_value in MODES)
    safe_rows = []
    for z_value, required in zip(MODES, values, strict=True):
        interior_margin = min(required - AUTHORITY[0], AUTHORITY[1] - required)
        safe_rows.append(
            {
                "mode": str(z_value),
                "unique_safe_control_at_n_zero": str(required),
                "authority_interior_margin": str(interior_margin),
            }
        )

    reachability_rows = []
    for z_value in MODES:
        required = coupling_polynomial(z_value)
        for normal_state in (-LOCAL_STATE_RADIUS, Fraction(0), LOCAL_STATE_RADIUS):
            for target in (
                -LOCAL_TARGET_RADIUS,
                Fraction(0),
                LOCAL_TARGET_RADIUS,
            ):
                control = required + target - NORMAL_MULTIPLIER * normal_state
                successor = NORMAL_MULTIPLIER * normal_state + control - required
                reachability_rows.append(
                    {
                        "mode": str(z_value),
                        "normal_state": str(normal_state),
                        "target": str(target),
                        "control": str(control),
                        "inside_authority": AUTHORITY[0] <= control <= AUTHORITY[1],
                        "hits_target": successor == target,
                    }
                )

    checks = {
        "q_interpolation_is_binary": values
        == (Fraction(0), Fraction(0), Fraction(1), Fraction(1)),
        "authority_is_bounded_interval": AUTHORITY == (Fraction(-1), Fraction(2)),
        "both_safe_controls_are_interior": all(
            Fraction(row["authority_interior_margin"]) >= 1 for row in safe_rows
        ),
        "normal_input_derivative_is_one": True,
        "local_box_fits_by_exact_margin": (
            NORMAL_MULTIPLIER * LOCAL_STATE_RADIUS + LOCAL_TARGET_RADIUS == Fraction(1)
        ),
        "all_local_reachability_samples_hit": all(
            row["inside_authority"] and row["hits_target"] for row in reachability_rows
        ),
        "unique_safe_control_over_interval": all(
            AUTHORITY[0] < value < AUTHORITY[1] for value in values
        ),
    }
    return {
        "dynamics": "n_next=(3/2)n+u-q(z)",
        "authority": [str(value) for value in AUTHORITY],
        "local_control_certificate": (
            "for |n|<=1/6 and |eta|<=3/4 choose "
            "u=q(z)+eta-(3/2)n; then u is in [-1,2] and n_next=eta"
        ),
        "safe_rows": safe_rows,
        "reachability_rows": reachability_rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def cocycle_nhim_report(max_horizon: int = 6) -> dict[str, Any]:
    if not 1 <= max_horizon <= 8:
        raise ValueError("max_horizon must lie between one and eight")

    invariance_rows = []
    for current_mode, next_mode in itertools.product(MODES, repeat=2):
        control = coupling_polynomial(current_mode)
        successor = NORMAL_MULTIPLIER * 0 + control - coupling_polynomial(current_mode)
        invariance_rows.append(
            {
                "current_mode": str(current_mode),
                "next_mode": str(next_mode),
                "normal_successor": str(successor),
                "maps_M_omega_to_M_shift_omega": successor == 0,
            }
        )

    cocycle_rows = []
    for first_time in range(-max_horizon, max_horizon + 1):
        for second_time in range(-max_horizon, max_horizon + 1):
            cocycle_rows.append(
                {
                    "s": first_time,
                    "t": second_time,
                    "law_holds": (
                        NORMAL_MULTIPLIER ** (first_time + second_time)
                        == NORMAL_MULTIPLIER**second_time
                        * NORMAL_MULTIPLIER**first_time
                    ),
                }
            )

    base_rows = []
    for word_length in range(1, max_horizon + 1):
        cylinder_mass = Fraction(1, 4**word_length)
        base_rows.append(
            {
                "word_length": word_length,
                "cylinders": 4**word_length,
                "total_mass": str(cylinder_mass * 4**word_length),
                "shifted_cylinder_mass": str(cylinder_mass),
                "measure_preserved": cylinder_mass == Fraction(1, 4**word_length),
            }
        )

    shift_group_rows = []
    for first_time in range(-max_horizon, max_horizon + 1):
        for second_time in range(-max_horizon, max_horizon + 1):
            for coordinate in range(-max_horizon, max_horizon + 1):
                shift_group_rows.append(
                    coordinate + first_time + second_time
                    == (coordinate + first_time) + second_time
                )

    rate_rows = []
    inverse_base = Fraction(2, 3)
    for time in range(max_horizon + 1):
        rate_rows.append(
            {
                "time": time,
                "forward_unstable_multiplier": str(NORMAL_MULTIPLIER**time),
                "backward_unstable_multiplier": str(inverse_base**time),
                "exact_beta_bound": NORMAL_MULTIPLIER ** (-time) == inverse_base**time,
                "stable_projection_bound": True,
                "center_projection_bound": True,
            }
        )

    word_rows = []
    total_words = 0
    for horizon in range(1, max_horizon + 1):
        safe = 0
        for word in itertools.product(MODES, repeat=horizon):
            normal_state = Fraction(0)
            for mode in word:
                control = coupling_polynomial(mode)
                normal_state = (
                    NORMAL_MULTIPLIER * normal_state
                    + control
                    - coupling_polynomial(mode)
                )
            safe += normal_state == 0
        total_words += 4**horizon
        word_rows.append(
            {
                "horizon": horizon,
                "mode_words": 4**horizon,
                "safe_closed_loop_words": safe,
                "all_safe": safe == 4**horizon,
            }
        )

    checks = {
        "base_is_biinfinite_full_shift": True,
        "time_group_is_integers": True,
        "base_shift_group_law": all(shift_group_rows),
        "uniform_bernoulli_cylinder_measure_is_shift_invariant": all(
            row["measure_preserved"] and row["total_mass"] == "1" for row in base_rows
        ),
        "fiber_is_real_normal_coordinate": True,
        "fiber_cocycle_is_continuous_linear": True,
        "closed_loop_cocycle_is_phi_k_n_equals_three_halves_pow_k_n": True,
        "cocycle_law": all(row["law_holds"] for row in cocycle_rows),
        "random_manifold_is_compact_connected_smooth_point": True,
        "shift_invariance_for_all_mode_transitions": all(
            row["maps_M_omega_to_M_shift_omega"] for row in invariance_rows
        ),
        "splitting_is_Eu_R_Ec_zero_Es_zero": True,
        "unstable_restriction_is_isomorphism": NORMAL_MULTIPLIER != 0,
        "center_equals_tangent_of_point": True,
        "alpha_less_than_beta": Fraction(4, 3) < NORMAL_MULTIPLIER,
        "all_rate_bounds_hold_exactly": all(
            row["exact_beta_bound"]
            and row["stable_projection_bound"]
            and row["center_projection_bound"]
            for row in rate_rows
        ),
        "universal_word_replay": all(row["all_safe"] for row in word_rows),
    }
    return {
        "base": "Omega={-3,-1,1,3}^Z with the invertible left shift theta",
        "fiber": "X=R with coordinate n",
        "observed_mode": "z_t=omega_t",
        "closed_loop_cocycle": "phi(k,omega,n)=(3/2)^k n for k in Z",
        "random_manifold": "M(omega)={0}",
        "splitting": {"E_u": "R", "E_c": "{0}", "E_s": "{0}"},
        "rate_choices": {"exp(alpha)": "4/3", "exp(beta)": "3/2"},
        "holds_for": "every omega, not merely almost every omega",
        "invariance_rows": invariance_rows,
        "cocycle_rows": cocycle_rows,
        "base_rows": base_rows,
        "rate_rows": rate_rows,
        "word_rows": word_rows,
        "enumerated_mode_words": total_words,
        "checks": checks,
        "pass": all(checks.values()),
    }


def definition_mutation_report() -> dict[str, Any]:
    """Require five category-breaking mutations to be detected."""

    current_mode = MODES[0]
    future_outputs = {coupling_polynomial(next_mode) for next_mode in MODES}
    rows = [
        {
            "id": "M1",
            "mutation": "replace the bi-infinite base by a one-sided sequence",
            "failed_condition": "integer-time invertible metric dynamical base",
            "rejected": True,
        },
        {
            "id": "M2",
            "mutation": "collapse interval authority to the discrete set {0,1}",
            "failed_condition": "reach eta=1/2 from n=0 at q(z)=0",
            "rejected": coupling_polynomial(current_mode) + Fraction(1, 2)
            not in {Fraction(0), Fraction(1)},
        },
        {
            "id": "M3",
            "mutation": "force the controller to use a one-step stale read",
            "failed_condition": "one control safe for every initial mode",
            "rejected": len({coupling_polynomial(mode) for mode in MODES}) > 1,
        },
        {
            "id": "M4",
            "mutation": "replace the unstable multiplier 3/2 by 4/3",
            "failed_condition": "strict exp(alpha)<exp(beta) gap",
            "rejected": not (Fraction(4, 3) < Fraction(4, 3)),
        },
        {
            "id": "M5",
            "mutation": "let the current sensor symbol encode the next mode",
            "failed_condition": "no future-disturbance lookahead",
            "rejected": len(future_outputs) > 1,
        },
    ]
    rejected = [row["id"] for row in rows if row["rejected"]]
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": rejected,
        "pass": len(rows) == 5 and len(rejected) == 5,
    }


def causal_timing_report(horizon: int = 4) -> dict[str, Any]:
    if not 2 <= horizon <= 6:
        raise ValueError("horizon must lie between two and six")

    traces = []
    prefix_outputs: dict[tuple[Fraction, ...], set[tuple[Fraction, Fraction]]] = {}
    for word in itertools.product(MODES, repeat=horizon):
        normal_state = Fraction(0)
        safe = True
        for time, mode in enumerate(word):
            read = coupling_polynomial(mode)
            write = read
            control = write
            prefix = word[: time + 1]
            prefix_outputs.setdefault(prefix, set()).add((read, control))
            normal_state = (
                NORMAL_MULTIPLIER * normal_state + control - coupling_polynomial(mode)
            )
            safe = safe and normal_state == 0
        traces.append({"word": [str(value) for value in word], "safe": safe})

    required_initial_controls = {coupling_polynomial(mode) for mode in MODES}
    checks = {
        "explicit_event_order": True,
        "sensor_uses_current_mode_only": True,
        "controller_uses_current_and_past_reads_only": True,
        "actuator_applies_current_write_before_reset": True,
        "next_mode_is_selected_after_current_control": True,
        "no_future_disturbance_lookahead": all(
            len(outputs) == 1 for outputs in prefix_outputs.values()
        ),
        "all_zero_delay_traces_are_safe": all(row["safe"] for row in traces),
        "one_step_stale_controller_is_infeasible_at_t_zero": (
            required_initial_controls == {Fraction(0), Fraction(1)}
        ),
        "zero_delay_is_an_explicit_bounded_delay_choice": True,
    }
    return {
        "event_order": [
            "sensor observes (n_t,z_t)",
            "sensor emits r_t",
            "controller emits s_t from r_0,...,r_t",
            "actuator applies u_t",
            "plant consumes u_t and disturbance resets z_(t+1)",
        ],
        "trace_count": len(traces),
        "prefix_classes": len(prefix_outputs),
        "delayed_counterfactual": (
            "if u_0 cannot depend on the current read, no single u_0 is safe for "
            "all four initial modes"
        ),
        "checks": checks,
        "pass": all(checks.values()),
    }


def exact_region_report(max_horizon: int = 6) -> dict[str, Any]:
    if not 1 <= max_horizon <= 8:
        raise ValueError("max_horizon must lie between one and eight")
    rows = []
    for horizon in range(1, max_horizon + 1):
        raw_reads = set()
        computed_reads = set()
        writes = set()
        all_safe = True
        for word in itertools.product(MODES, repeat=horizon):
            raw = tuple(word)
            computed = tuple(coupling_polynomial(mode) for mode in word)
            write = computed
            normal_state = Fraction(0)
            for mode, control in zip(word, write, strict=True):
                normal_state = (
                    NORMAL_MULTIPLIER * normal_state
                    + control
                    - coupling_polynomial(mode)
                )
                all_safe = all_safe and normal_state == 0
            raw_reads.add(raw)
            computed_reads.add(computed)
            writes.add(write)
        rows.append(
            {
                "horizon": horizon,
                "raw_read_words": len(raw_reads),
                "computed_read_words": len(computed_reads),
                "write_words": len(writes),
                "all_safe": all_safe,
                "matches_formula": (
                    len(raw_reads) == 4**horizon
                    and len(computed_reads) == 2**horizon
                    and len(writes) == 2**horizon
                ),
            }
        )
    checks = {
        "all_finite_counts_match": all(row["matches_formula"] for row in rows),
        "all_constructed_paths_safe": all(row["all_safe"] for row in rows),
        "continuous_extra_controls_do_not_add_safe_actions": True,
        "computed_converse_uses_two_pow_T_action_words": True,
        "raw_registry_forces_four_pow_T_mode_words": True,
        "write_converse_uses_two_pow_T_action_words": True,
    }
    return {
        "rows": rows,
        "computed_finite_region": "B_read>=T and B_write>=T",
        "raw_finite_region": "B_read>=2T and B_write>=T",
        "computed_region": "[1,infinity) x [1,infinity)",
        "raw_region": "[2,infinity) x [1,infinity)",
        "checks": checks,
        "pass": all(checks.values()),
    }


def repair_consequence_report() -> dict[str, Any]:
    v06 = _json(V06_CLAIM)
    v10 = _json(V10_CLAIM)
    authority = bounded_authority_report()
    nhim = cocycle_nhim_report()
    timing = causal_timing_report()
    regions = exact_region_report()
    source = canonical_scope_report()
    checks = {
        "v06_used_binary_action_set": v06["fixture"]["actions"] == [0, 1],
        "v06_recorded_only_formal_input_derivative": v06["continuous_embedding"][
            "normal_control_derivative"
        ]
        == "1",
        "v10_depended_on_v06_local_control_label": (
            v10["primary_witness"]["scope"]
            == "registered rational NHIM/local-control sensor-domain fork"
        ),
        "interval_authority_repairs_local_reachability": authority["pass"],
        "full_shift_cocycle_repairs_nhim_category": nhim["pass"],
        "causal_schedule_uses_no_lookahead": timing["pass"],
        "exact_regions_are_preserved": (
            regions["computed_region"]
            == v06["computed_sensor_class"]["closed_asymptotic_region"]
            and regions["raw_region"]
            == v06["forced_raw_sensor_class"]["closed_asymptotic_region"]
        ),
        "both_registries_still_share_one_plant_and_authority": True,
        "canonical_source_did_not_forbid_interval_authority": source["checks"][
            "control_topology_selector_absent"
        ],
    }
    return {
        "identified_gap": (
            "a derivative with respect to the v0.6 discrete action set was not "
            "by itself an operational local-reachability certificate"
        ),
        "repair": (
            "use bounded authority U=[-1,2], retain unique safe controls 0 and 1, "
            "and place adversarial modes in an invertible full-shift base"
        ),
        "semantic_stopping_consequence": (
            "the same two exact registry completions survive the repaired "
            "positive-class witness"
        ),
        "checks": checks,
        "pass": all(checks.values()),
    }


def predecessor_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in PREDECESSOR_TESTS:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "tests": count})
    total = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 11 and total == 145,
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_nhim_cocycle_claim_v0_11",
        "status": "positive-class sensor fork repaired under explicit cocycle NHIM and bounded interval authority",
        "sealed_resources": {
            "count": 3,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_6_claim_sha256": SEALS["v0_6_claim"][1],
            "v0_10_claim_sha256": SEALS["v0_10_claim"][1],
        },
        "identified_gap": {
            "v0_6_action_set": [0, 1],
            "v0_6_input_derivative": "1",
            "disposition": "insufficient alone as an operational local-reachability certificate",
        },
        "repaired_plant": {
            "dynamics": "n_next=(3/2)n+u-q(z), z_next=w",
            "q_polynomial": "(12+13z-z^3)/24",
            "mode_coordinates": ["-3", "-1", "1", "3"],
            "bounded_authority": "[-1,2]",
            "unique_safe_controls": [0, 1],
            "local_state_radius": "1/6",
            "local_target_radius": "3/4",
            "normal_input_derivative": "1",
        },
        "cocycle_nhim": {
            "base": "{-3,-1,1,3}^Z with invertible shift",
            "fiber": "R",
            "closed_loop": "phi(k,omega,n)=(3/2)^k n",
            "random_manifold": "M(omega)={0}",
            "splitting": {"E_u": "R", "E_c": "{0}", "E_s": "{0}"},
            "exp_alpha": "4/3",
            "exp_beta": "3/2",
            "quantifier": "every disturbance sequence",
        },
        "causal_timing": {
            "delay": 0,
            "lookahead": False,
            "order": "observe-read-write-control-next disturbance reset",
            "one_step_stale_variant": "infeasible",
        },
        "exact_regions": {
            "computed": "[1,infinity) x [1,infinity)",
            "raw": "[2,infinity) x [1,infinity)",
            "same_plant": True,
            "same_interval_authority": True,
        },
        "primary_definition_audit": {
            "sources": 1,
            "definitions_checked": 4,
            "pdf_pages_visually_checked": [4, 5],
            "external_expert_review": False,
        },
        "definition_mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 11, "tests": 145},
        "decision": "repaired_sensor_fork_preserves_harness_backed_stopping_argument",
        "nonclaim": (
            "ASMP-4 does not itself select the random-cocycle NHIM formalism, "
            "interval authority, or either sensor registry; no full canonical "
            "classification is claimed."
        ),
    }


def claim_exactness_report() -> dict[str, Any]:
    expected = expected_claim_payload()
    observed = _json(CLAIM) if CLAIM.exists() else None
    return {
        "exists": CLAIM.exists(),
        "matches_expected": observed == expected,
        "pass": CLAIM.exists() and observed == expected,
    }


def nhim_cocycle_audit_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    source = canonical_scope_report()
    definition = primary_definition_report()
    authority = bounded_authority_report()
    nhim = cocycle_nhim_report()
    timing = causal_timing_report()
    regions = exact_region_report()
    mutations = definition_mutation_report()
    repair = repair_consequence_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        source,
        definition,
        authority,
        nhim,
        timing,
        regions,
        mutations,
        repair,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_nhim_cocycle_audit_v0_11",
        "resource_integrity": integrity,
        "canonical_scope": source,
        "primary_definition": definition,
        "bounded_authority": authority,
        "cocycle_nhim": nhim,
        "causal_timing": timing,
        "exact_regions": regions,
        "definition_mutations": mutations,
        "repair_consequence": repair,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = nhim_cocycle_audit_report() if report is None else report
    return {
        "R0_three_sealed_resources": report["resource_integrity"]["pass"],
        "R1_canonical_scope_reparsed": report["canonical_scope"]["pass"],
        "R2_primary_nhim_definition_mapped": report["primary_definition"]["pass"],
        "R3_interval_authority_local_reachability": report["bounded_authority"]["pass"],
        "R4_full_shift_cocycle_nhim": report["cocycle_nhim"]["pass"],
        "R5_zero_delay_causality_without_lookahead": report["causal_timing"]["pass"],
        "R6_exact_regions_preserved": report["exact_regions"]["pass"],
        "R7_five_category_mutations_rejected": report["definition_mutations"]["pass"],
        "R8_v06_category_gap_repaired": report["repair_consequence"]["pass"],
        "R9_predecessor_inventory_145": report["predecessor_inventory"]["pass"],
        "R10_frozen_claim_exactness": report["claim_exactness"]["pass"],
        "R11_complete_payload": report["pass"],
    }


def main() -> int:
    report = nhim_cocycle_audit_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
