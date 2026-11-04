"""Import-independent development audit for ASMP-9 v0.64."""

from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations, permutations
import json
from math import comb


def pairs(n):
    return tuple(combinations(range(n), 2))


def winner(order, pair):
    positions = {item: index for index, item in enumerate(order)}
    return min(pair, key=positions.__getitem__)


def signature(order, queries):
    return tuple(winner(order, pair) for pair in queries)


def attainable(order, consideration_family):
    return frozenset(
        winner(order, considered)
        for considered in consideration_family
    )


def separates(left, right, consideration_family):
    return attainable(left, consideration_family).isdisjoint(
        attainable(right, consideration_family)
    )


def main():
    counts = {
        "collapse_rankings": 0,
        "complete_signatures": 0,
        "compliance_pair_checks": 0,
        "graph_cells": 0,
        "missing_edge_witnesses": 0,
    }

    for n in range(2, 7):
        menu = tuple(range(n))
        probabilities = tuple(
            Q(index + 1, n * (n + 1) // 2)
            for index in range(n)
        )
        assert sum(probabilities, Q(0)) == 1
        for order in permutations(range(n)):
            observed = tuple(
                probability
                for chosen, probability in zip(menu, probabilities)
                if winner(order, (chosen,)) == chosen
            )
            assert observed == probabilities
            counts["collapse_rankings"] += 1

    for n in range(2, 8):
        complete = pairs(n)
        orders = tuple(permutations(range(n)))
        signatures = {signature(order, complete) for order in orders}
        assert len(signatures) == len(orders)
        assert len(complete) == comb(n, 2)
        counts["complete_signatures"] += len(signatures)

    for n in range(2, 9):
        complete = set(pairs(n))
        for missing in complete:
            x, y = missing
            other = tuple(item for item in range(n) if item not in missing)
            split = len(other) // 2
            left = other[:split] + (x, y) + other[split:]
            right = other[:split] + (y, x) + other[split:]
            queries = tuple(sorted(complete - {missing}))
            assert signature(left, queries) == signature(right, queries)
            assert signature(left, (missing,)) != signature(right, (missing,))
            counts["missing_edge_witnesses"] += 1

    for n in range(2, 6):
        edge_list = pairs(n)
        orders = tuple(permutations(range(n)))
        full_signatures = tuple(
            signature(order, edge_list)
            for order in orders
        )
        for mask in range(1 << len(edge_list)):
            queries = tuple(
                edge
                for index, edge in enumerate(edge_list)
                if mask & (1 << index)
            )
            selected_indices = tuple(
                index
                for index in range(len(edge_list))
                if mask & (1 << index)
            )
            observed_rows = tuple(
                tuple(row[index] for index in selected_indices)
                for row in full_signatures
            )
            observed = set(observed_rows)
            injective = len(observed) == len(orders)
            assert injective == (len(queries) == len(edge_list))

            separated = True
            for left_index, left_row in enumerate(observed_rows):
                for right_row in observed_rows[left_index + 1 :]:
                    pair_separated = left_row != right_row
                    counts["compliance_pair_checks"] += 1
                    separated = separated and pair_separated
            assert separated == injective
            counts["graph_cells"] += 1

    print(
        json.dumps(
            {
                **counts,
                "registered": False,
                "status": "development_checks_passed",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
