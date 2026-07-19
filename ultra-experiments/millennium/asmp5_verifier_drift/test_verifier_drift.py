import inspect

from run import (
    candidate_edges,
    certified_reachability,
    checker_accepts,
    checker_neighbors,
    edge_is_certified,
    semantic_label_table,
    swap_behavior_coordinates,
)


CLASSES = {0: 0, 1: 1, 2: 0, 3: 1}


def test_semantic_labels_are_absent_from_generation_and_reachability_signatures():
    assert "label" not in str(inspect.signature(candidate_edges))
    assert "label" not in str(inspect.signature(certified_reachability))


def test_root_checker_accepts_exactly_hazard_free_inputs():
    for proof_class in (0, 1):
        assert checker_accepts(3, 0, proof_class)
        assert not checker_accepts(3, 1, proof_class)


def test_checker_neighbor_counts_are_closed_form():
    assert len(checker_neighbors(3, 0)) == 1
    assert len(checker_neighbors(3, 1)) == 5
    assert len(checker_neighbors(3, 2)) == 11


def test_candidate_graph_changes_behavior_and_progress_is_external():
    state = (0, 3, 0)
    edges = list(candidate_edges(state, width=4, radius=0, proof_tokens=(0, 1, 2, 3)))
    assert len(edges) == 16
    assert all((state[0] ^ edge[0]).bit_count() == 1 for edge in edges)
    assert all(edge[1] == 3 for edge in edges)


def test_root_arm_retains_installed_checker_but_does_not_activate_it():
    state = (0, 7, 1)
    unsafe_edge = (1, 7, 0)
    assert edge_is_certified(state, unsafe_edge, regime="adaptive", rule="self_endorsement", root_checker=3, proof_classes=CLASSES)
    assert not edge_is_certified(state, unsafe_edge, regime="frozen_root", rule="self_endorsement", root_checker=3, proof_classes=CLASSES)


def test_root_refinement_rejects_acceptance_set_expansion():
    state = (0, 3, 0)
    safe_but_expanding = (2, 7, 0)
    assert edge_is_certified(state, safe_but_expanding, regime="adaptive", rule="self_endorsement", root_checker=3, proof_classes=CLASSES)
    assert not edge_is_certified(state, safe_but_expanding, regime="adaptive", rule="root_refinement", root_checker=3, proof_classes=CLASSES)


def test_width_four_has_insufficient_distinct_safe_behavior_capacity():
    assert sum(semantic_label_table(4).values()) == 8
    assert sum(semantic_label_table(6).values()) == 32


def test_nonhazard_coordinate_swap_is_an_involution_and_preserves_hazard():
    for behavior in range(64):
        swapped = swap_behavior_coordinates(behavior, 1, 2)
        assert (swapped & 1) == (behavior & 1)
        assert swap_behavior_coordinates(swapped, 1, 2) == behavior
