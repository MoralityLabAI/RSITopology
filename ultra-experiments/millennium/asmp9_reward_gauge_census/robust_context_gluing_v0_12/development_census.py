"""Unregistered two-context conditioning census for ASMP-9 v0.12."""

from __future__ import annotations

import argparse
import json
from itertools import combinations, product
from pathlib import Path

from exact_certificate import smallest_conditioning_witness
from robust_gluing import (
    cycle_design_census,
    local_global_incidence,
    quotient_basis,
    simple_cycle_vectors,
)


def edge_universe(item_count: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations(range(item_count), 2))


def graph_from_mask(
    item_count: int, mask: int
) -> tuple[tuple[int, int], ...]:
    return tuple(
        edge
        for index, edge in enumerate(edge_universe(item_count))
        if mask & (1 << index)
    )


def design_record(design: object | None) -> dict[str, object] | None:
    if design is None:
        return None
    return {
        "indices": list(design.indices),
        "sigma_min": design.sigma_min,
        "amplification": design.amplification,
        "total_support": design.total_support,
    }


def run_census(maximum_items: int = 4) -> dict[str, object]:
    cells = []
    summaries: dict[str, dict[str, object]] = {}
    for item_count in range(2, maximum_items + 1):
        graph_count = 1 << len(edge_universe(item_count))
        summary: dict[str, object] = {
            "ordered_graph_pair_count": graph_count**2,
            "live_pair_count": 0,
            "suboptimal_shortest_pair_count": 0,
            "by_obstruction_dimension": {},
        }
        for first_mask, second_mask in product(
            range(graph_count), repeat=2
        ):
            contexts = (
                graph_from_mask(item_count, first_mask),
                graph_from_mask(item_count, second_mask),
            )
            local, shared, labelled = local_global_incidence(
                item_count, contexts
            )
            quotient = quotient_basis(local, shared)
            if quotient.shape[1] == 0:
                continue
            cycles = simple_cycle_vectors(item_count, labelled)
            census = cycle_design_census(cycles, quotient)
            if census.e_optimal is None or census.shortest_best is None:
                raise AssertionError("live quotient lacks a simple-cycle basis")
            ratio = (
                census.shortest_best.amplification
                / census.e_optimal.amplification
            )
            suboptimal = ratio > 1.0 + 1e-9
            cell = {
                "item_count": item_count,
                "masks": [first_mask, second_mask],
                "edge_count": len(labelled),
                "obstruction_dimension": census.obstruction_dimension,
                "candidate_count": census.candidate_count,
                "spanning_design_count": census.spanning_design_count,
                "minimum_total_support": census.minimum_total_support,
                "shortest_best": design_record(census.shortest_best),
                "e_optimal": design_record(census.e_optimal),
                "amplification_ratio": ratio,
                "shortest_is_condition_optimal": not suboptimal,
            }
            cells.append(cell)
            summary["live_pair_count"] += 1
            summary["suboptimal_shortest_pair_count"] += int(suboptimal)
            by_dimension = summary["by_obstruction_dimension"]
            dimension = str(census.obstruction_dimension)
            bucket = by_dimension.setdefault(
                dimension,
                {
                    "count": 0,
                    "suboptimal_shortest_count": 0,
                    "maximum_amplification_ratio": 0.0,
                },
            )
            bucket["count"] += 1
            bucket["suboptimal_shortest_count"] += int(suboptimal)
            bucket["maximum_amplification_ratio"] = max(
                bucket["maximum_amplification_ratio"], ratio
            )
        summaries[str(item_count)] = summary
    suboptimal_cells = [
        cell for cell in cells if not cell["shortest_is_condition_optimal"]
    ]
    smallest = min(
        suboptimal_cells,
        key=lambda cell: (
            cell["item_count"],
            cell["edge_count"],
            cell["masks"],
        ),
        default=None,
    )
    maximum = max(
        cells, key=lambda cell: cell["amplification_ratio"], default=None
    )
    return {
        "status": "unregistered_development_only",
        "context_count": 2,
        "maximum_items": maximum_items,
        "summaries": summaries,
        "smallest_suboptimal_shortest_basis": smallest,
        "maximum_observed_amplification_ratio": maximum,
        "exact_smallest_witness_certificate": smallest_conditioning_witness(),
        "claim_boundary": (
            "Unregistered finite numerical census with one exact rational "
            "counterexample certificate; not a claim-eligible theorem."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_census()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
