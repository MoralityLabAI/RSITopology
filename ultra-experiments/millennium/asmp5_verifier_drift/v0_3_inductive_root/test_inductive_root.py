import json
from pathlib import Path

import inductive_root as primary
import verify_independent as independent
from inductive_root import (
    ROOT_CHECKER,
    compile_result,
    load_protocol,
    robustness_probes,
    rooted_induction_certificate,
    rooted_liveness_cycle,
    theorem_cell,
    transition_allowed,
    unrooted_witness,
)


HERE = Path(__file__).resolve().parent


def test_rooted_induction_is_all_depth_and_live():
    for width in (2, 3, 6, 9):
        for radius in (0, 1, 2, 4):
            cell = theorem_cell(width, radius, "root_refinement")
            assert cell["all_depth_safety"]
            assert cell["unsafe_depth"] is None
            assert cell["arbitrary_time_liveness"]
            assert rooted_liveness_cycle(width, radius)


def test_width_one_is_safe_but_not_live():
    cell = theorem_cell(1, 4, "root_refinement")
    assert cell["all_depth_safety"]
    assert not cell["arbitrary_time_liveness"]


def test_unrooted_rules_have_exact_two_step_witness():
    for rule in ("self_endorsement", "pairwise_agreement"):
        for width in (2, 4, 8):
            for radius in (1, 2, 4):
                witness = unrooted_witness(width, radius, rule)
                assert witness is not None
                assert witness[-1]["to_behavior"] & 1
                assert theorem_cell(width, radius, rule)["unsafe_depth"] == 2


def test_radius_zero_clean_control_has_no_unsafe_witness():
    for rule in ("self_endorsement", "pairwise_agreement"):
        assert unrooted_witness(6, 0, rule) is None
        assert theorem_cell(6, 0, rule)["unsafe_depth"] is None


def test_hazard_mutation_is_detected():
    mutated = ROOT_CHECKER | (1 << 2)
    assert transition_allowed(
        behavior=0,
        checker=mutated,
        next_behavior=1,
        next_checker=mutated,
        width=2,
        radius=0,
        rule="root_refinement",
        root_checker=mutated,
    )


def test_checker_domain_rejects_negative_and_high_bit_values():
    # Every case would otherwise be an accepting safe edge under
    # self-endorsement; the only reason to reject it is the checker domain.
    for checker, next_checker in ((-1, 3), (19, 3), (3, 19), (3, -1)):
        assert not transition_allowed(
            behavior=0,
            checker=checker,
            next_behavior=2,
            next_checker=next_checker,
            width=2,
            radius=4,
            rule="self_endorsement",
        )
        assert not independent.allowed(
            (0, checker),
            (2, next_checker),
            width=2,
            radius=4,
            rule="self_endorsement",
            root=ROOT_CHECKER,
        )


def test_behavior_and_root_domains_reject_out_of_grammar_values():
    for behavior, next_behavior in ((-2, -4), (4, 6)):
        assert not transition_allowed(
            behavior=behavior,
            checker=ROOT_CHECKER,
            next_behavior=next_behavior,
            next_checker=ROOT_CHECKER,
            width=2,
            radius=0,
            rule="self_endorsement",
        )
        assert not independent.allowed(
            (behavior, ROOT_CHECKER),
            (next_behavior, ROOT_CHECKER),
            width=2,
            radius=0,
            rule="self_endorsement",
            root=ROOT_CHECKER,
        )
    assert not transition_allowed(
        behavior=0,
        checker=ROOT_CHECKER,
        next_behavior=2,
        next_checker=ROOT_CHECKER,
        width=2,
        radius=0,
        rule="root_refinement",
        root_checker=-1,
    )
    assert not independent.allowed(
        (0, ROOT_CHECKER), (2, ROOT_CHECKER), 2, 0, "root_refinement", 16
    )


def test_primary_inductive_closure_uses_actual_transition_relation():
    certificate = rooted_induction_certificate()
    assert certificate["pass"]
    assert certificate["transition_truth_table"]["row_count"] == 10240
    assert len(certificate["transition_truth_table"]["sha256"]) == 64
    assert all(record["checked_edges"] == 256 for record in certificate["closures"])


def test_allow_all_primary_mutation_is_rejected(monkeypatch):
    protocol = load_protocol(HERE / "protocol_v0_3.json")
    monkeypatch.setattr(primary, "transition_allowed", lambda **_kwargs: True)
    result = compile_result(protocol)
    assert not result["gates"]["G1_inductive_safety"]
    assert not result["gates"]["G4_metric_robustness"]
    assert result["task_result"] == "not_established"

    verification = independent.verify_payload(protocol, result)
    assert not verification["pass"]
    assert not verification["transition_digest_matches"]


def test_metric_robustness_pack_passes():
    probes = robustness_probes()
    assert set(probes) == {"invariance", "sensitivity", "monotonicity", "anti_gaming", "clean_control"}
    assert all(record["pass"] for record in probes.values())


def test_final_synthesis_binds_artifacts_and_conclusion_layers():
    verification = independent.verify()
    assert verification["pass"]
    synthesis = independent.build_synthesis(
        HERE / "protocol_v0_3.json",
        HERE / "artifacts_v0_3" / "result_v0_3.json",
        HERE / "artifacts_v0_3" / "verification_v0_3.json",
    )
    assert synthesis["pass"]
    assert synthesis["binding_match"]
    assert set(synthesis["conclusion_layers"]) == {
        "task_result",
        "measurement_reliability",
        "claim_support",
        "operational_decision",
        "metric_robustness",
    }
    on_disk = json.loads(
        (HERE / "artifacts_v0_3" / "synthesis_receipt_v0_3.json").read_text(encoding="utf-8")
    )
    assert on_disk == synthesis


def test_final_synthesis_rejects_tampered_verification_binding(tmp_path):
    protocol_path = HERE / "protocol_v0_3.json"
    result_path = HERE / "artifacts_v0_3" / "result_v0_3.json"
    verification = independent.verify()
    verification["bindings"]["result_v0_3.json"] = "0" * 64
    verification_path = tmp_path / "verification_v0_3.json"
    verification_path.write_text(independent.canonical_json(verification), encoding="utf-8")

    synthesis = independent.build_synthesis(protocol_path, result_path, verification_path)
    assert not synthesis["pass"]
    assert not synthesis["binding_match"]
    assert synthesis["conclusion_layers"]["task_result"] == "not_established"
