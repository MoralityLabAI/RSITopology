"""Import-independent development audit for ASMP-9 v0.65."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations, product
import json
from math import comb, factorial


Q = Fraction


def rankings(n):
    return tuple(permutations(range(n)))


def top_on(order, menu):
    menu = set(menu)
    return next(item for item in order if item in menu)


def strict(types, outcome_map):
    for index, order in enumerate(types):
        position = {item: rank for rank, item in enumerate(order)}
        own = position[outcome_map[index]]
        if any(
            own >= position[outcome]
            for other_index, outcome in enumerate(outcome_map)
            if other_index != index
        ):
            return False
    return True


def formula(types):
    n = len(types[0])
    return max(
        len({top_on(order, menu) for order in types})
        for size in range(1, n + 1)
        for menu in combinations(range(n), size)
    )


def brute(types):
    n = len(types[0])
    for size in range(min(len(types), n), 0, -1):
        for selected in combinations(types, size):
            for outcome_map in product(range(n), repeat=size):
                if strict(selected, outcome_map):
                    return size
    raise AssertionError


def pair_regret(true_order, report_order, utilities, weights):
    return sum(
        (
            weight
            * (
                utilities[top_on(true_order, pair)]
                - utilities[top_on(report_order, pair)]
            )
            for pair, weight in weights.items()
        ),
        Q(0),
    )


def main():
    counts = {
        "full_domain_rankings": 0,
        "missing_pair_witness_checks": 0,
        "pair_lottery_report_checks": 0,
        "revealed_pair_class_checks": 0,
        "small_type_domains": 0,
        "small_direct_maps": 0,
        "top_rule_best_response_checks": 0,
        "uniform_margin_checks": 0,
    }

    for n in range(2, 8):
        types = rankings(n)
        assert formula(types) == n
        counts["full_domain_rankings"] += len(types)

        top_map = tuple(order[0] for order in types)
        for order in types:
            best = min(
                range(len(types)),
                key=lambda index: order.index(top_map[index]),
            )
            best_rank = order.index(top_map[best])
            best_set = tuple(
                index
                for index, outcome in enumerate(top_map)
                if order.index(outcome) == best_rank
            )
            assert len(best_set) == factorial(n - 1)
            counts["top_rule_best_response_checks"] += 1

    for n in (2, 3):
        types = rankings(n)
        for size in range(1, len(types) + 1):
            for selected_indices in combinations(range(len(types)), size):
                domain = tuple(types[index] for index in selected_indices)
                counts["small_type_domains"] += 1
                counts["small_direct_maps"] += n ** len(domain)
                assert formula(domain) == brute(domain)

    for n in range(2, 6):
        types = rankings(n)
        pairs = tuple(combinations(range(n), 2))
        weights = {pair: Q(1, len(pairs)) for pair in pairs}
        for true_order in types:
            utilities = [Q(0) for _ in range(n)]
            for position, outcome in enumerate(true_order):
                utilities[outcome] = Q(n - position, n)
            for report_order in types:
                regret = pair_regret(
                    true_order,
                    report_order,
                    utilities,
                    weights,
                )
                assert regret >= 0
                assert (regret == 0) == (report_order == true_order)
                counts["pair_lottery_report_checks"] += 1

    for n in range(3, 8):
        pairs = tuple(combinations(range(n), 2))
        for missing in pairs:
            retained = tuple(pair for pair in pairs if pair != missing)
            weights = {
                pair: Q(1, len(retained))
                for pair in retained
            }
            first, second = missing
            remainder = tuple(
                outcome
                for outcome in range(n)
                if outcome not in missing
            )
            true_order = (first, second, *remainder)
            report_order = (second, first, *remainder)
            utilities = [Q(0) for _ in range(n)]
            for position, outcome in enumerate(true_order):
                utilities[outcome] = Q(n - position, n)
            assert (
                pair_regret(
                    true_order,
                    report_order,
                    utilities,
                    weights,
                )
                == 0
            )
            counts["missing_pair_witness_checks"] += 1

    for n in range(2, 8):
        pairs = tuple(combinations(range(n), 2))
        weights = {pair: Q(1, len(pairs)) for pair in pairs}
        true_order = tuple(range(n))
        report_order = (1, 0, *range(2, n))
        utilities = tuple(Q(n - outcome, n) for outcome in range(n))
        gap = Q(1, n)
        assert (
            pair_regret(
                true_order,
                report_order,
                utilities,
                weights,
            )
            == gap / comb(n, 2)
        )
        counts["uniform_margin_checks"] += 1

        answer_class_size = factorial(n) // 2
        assert (answer_class_size > 1) == (n >= 3)
        counts["revealed_pair_class_checks"] += 1

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
