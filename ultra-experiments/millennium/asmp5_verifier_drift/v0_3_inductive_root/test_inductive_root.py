from inductive_root import (
    ROOT_CHECKER,
    robustness_probes,
    rooted_liveness_cycle,
    theorem_cell,
    transition_allowed,
    unrooted_witness,
)


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


def test_metric_robustness_pack_passes():
    probes = robustness_probes()
    assert set(probes) == {"invariance", "sensitivity", "monotonicity", "anti_gaming", "clean_control"}
    assert all(record["pass"] for record in probes.values())
