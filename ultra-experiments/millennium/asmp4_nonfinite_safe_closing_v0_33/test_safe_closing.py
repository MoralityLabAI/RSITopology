from __future__ import annotations

from fractions import Fraction

import safe_closing_variational as central
import verify_safe_closing as independent


def test_contract_claim_and_payload_are_exact() -> None:
    assert central.contract_report()["pass"]
    assert central.claim_report()["pass"]
    assert central.payload_report()["pass"]


def test_two_thue_morse_constructions_agree() -> None:
    word = independent.substitution_word(4096)
    assert all(central.thue_morse_bit(index) == word[index] for index in range(4096))
    assert central.thue_morse_report()["pass"]
    assert independent.independent_prefix_report()["pass"]


def test_bounded_aperiodicity_census_is_reproduced() -> None:
    central_report = central.bounded_aperiodicity_report()
    independent_report = independent.independent_aperiodicity()
    assert central_report["pass"]
    assert independent_report["pass"]
    assert central_report["rejected"] == independent_report["witnesses"] == 8320


def test_aperiodic_closed_blocks_converge_to_exact_corners() -> None:
    horizon = 4096
    for variant in ("balanced", "left", "right"):
        block = central.closed_block(horizon, variant)
        corner = central.theoretical_corner(variant)
        error = Fraction(1, 2 * (horizon + 1))
        assert block.rate[0] - corner[0] == error
        assert block.rate[1] - corner[1] == error


def test_component_disjunction_rejects_false_convex_midpoint() -> None:
    assert central.component_formula_report()["pass"]
    assert independent.independent_component_report()["pass"]
    midpoint = (Fraction(1), Fraction(1))
    assert not central.upward_contains_corner(central.theoretical_corner("left"), midpoint)
    assert not central.upward_contains_corner(central.theoretical_corner("right"), midpoint)


def test_exact_finite_closing_correction_is_vector_valued() -> None:
    assert central.finite_correction_report()["pass"]
    assert independent.independent_correction_report()["pass"]
    exact, coarse = central.finite_closing_bound(
        prefix=(17, 29),
        horizon=31,
        time_overhead=3,
        overhead=(2, 5),
        weight=Fraction(7, 13),
    )
    assert exact <= coarse


def test_linear_cost_overhead_cannot_be_erased() -> None:
    report = central.finite_correction_report()
    assert report["checks"]["linear_cost_overhead_has_positive_rate"]
    assert report["final_linear_overhead"] == "1/4"


def test_registered_limsup_and_margin_guards_are_load_bearing() -> None:
    assert central.burst_liminf_limsup_report()["pass"]
    assert independent.independent_burst_report()["pass"]
    assert central.shadow_margin_certificate(Fraction(1), Fraction(3, 4))
    assert not central.shadow_margin_certificate(Fraction(1), Fraction(1))


def test_eight_hostile_mutations_are_rejected_twice() -> None:
    assert central.mutation_report()["pass"]
    assert independent.independent_mutations()["pass"]


def test_independent_documents_inventory_and_full_reports_pass() -> None:
    assert central.predecessor_inventory_report()["pass"]
    assert independent.independent_inventory()["pass"]
    assert independent.document_report()["pass"]
    assert central.full_report()["pass"]
    assert independent.independent_report()["pass"]
