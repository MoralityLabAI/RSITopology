import importlib.util
from pathlib import Path

from verifier_drift import (
    accepted_proof,
    certified_reachability,
    checker_neighbors,
    semantic_label_table,
    universe_receipt,
)


HERE = Path(__file__).resolve().parent
V1_PATH = HERE.parent / "run.py"
spec = importlib.util.spec_from_file_location("asmp5_v1_reference", V1_PATH)
v1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(v1)

TOKENS = (0, 1, 2, 3)
CLASSES = {0: 0, 1: 1, 2: 0, 3: 1}


def projected_v1_layers(width, radius, horizon, regime, rule):
    levels, _ = v1.certified_reachability(
        width=width,
        radius=radius,
        horizon=horizon,
        regime=regime,
        rule=rule,
        root_checker=3,
        proof_tokens=TOKENS,
        proof_classes=CLASSES,
    )
    return [tuple((behavior, checker) for behavior, checker, _depth in level) for level in levels]


def test_quotient_matches_unquotiented_reference_on_disjoint_fixtures():
    for width in (3, 5):
        for radius in (0, 1):
            for regime in ("adaptive", "frozen_root"):
                for rule in ("self_endorsement", "pairwise_agreement", "root_refinement"):
                    levels, _ = certified_reachability(
                        width=width,
                        radius=radius,
                        horizon=3,
                        regime=regime,
                        rule=rule,
                        root_checker=3,
                        proof_tokens=TOKENS,
                        proof_classes=CLASSES,
                    )
                    assert levels == projected_v1_layers(width, radius, 3, regime, rule)


def test_universe_count_matches_closed_form():
    record = universe_receipt(6, 2, 8, TOKENS)
    assert record["candidate_edge_count"] == 8 * 64 * 16 * 6 * 4 * 11


def test_checker_neighbors_match_registered_hamming_balls():
    assert [len(checker_neighbors(3, radius)) for radius in (0, 1, 2)] == [1, 5, 11]


def test_root_and_adaptive_differ_only_by_active_checker():
    state = (0, 7)
    assert accepted_proof(
        state,
        1,
        7,
        regime="adaptive",
        rule="self_endorsement",
        root_checker=3,
        tokens_by_class={0: 0, 1: 1},
    ) is not None
    assert accepted_proof(
        state,
        1,
        7,
        regime="frozen_root",
        rule="self_endorsement",
        root_checker=3,
        tokens_by_class={0: 0, 1: 1},
    ) is None


def test_width_four_liveness_capacity_is_unavailable():
    assert sum(semantic_label_table(4).values()) == 8
    assert sum(semantic_label_table(6).values()) == 32
