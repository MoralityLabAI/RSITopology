from __future__ import annotations

from experiment import cycle_graph, run_graph_cells
from run_verification import bound_is_minimal, one_sided_exact_lower


PROTOCOL = {
    "alpha": 0.05,
    "probability_floor": 0.1,
    "coherent_tolerance": 0.5,
    "incoherent_margin": 0.6,
    "planted_circulation": 1.2,
}


def test_exact_lower_gate_has_frozen_margin() -> None:
    assert one_sided_exact_lower(0, 4096, 0.01) == 0.0
    assert one_sided_exact_lower(4096, 4096, 0.01) > 0.99


def test_registered_bound_is_minimal_integer() -> None:
    vertex_count, edges = cycle_graph(3)
    result = run_graph_cells(
        graph_name="test",
        vertex_count=vertex_count,
        edges=edges,
        seed=99,
        replicates=1,
        multipliers=(1.0,),
        alpha=PROTOCOL["alpha"],
        probability_floor=PROTOCOL["probability_floor"],
        coherent_tolerance=PROTOCOL["coherent_tolerance"],
        incoherent_margin=PROTOCOL["incoherent_margin"],
        planted_circulation=PROTOCOL["planted_circulation"],
    )
    assert bound_is_minimal(result, PROTOCOL)
