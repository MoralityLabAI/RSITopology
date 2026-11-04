"""Import-independent exact audit for ASMP-9 dynamic response v0.66."""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product
import json


def branch(outputs, transitions, belief, query):
    buckets = {}
    for initial, current in belief:
        observed = outputs[current][query]
        buckets.setdefault(observed, []).append(
            (initial, transitions[current][query])
        )
    return tuple(
        tuple(sorted(items))
        for _, items in sorted(buckets.items())
    )


def reachable(outputs, transitions, start):
    query_count = len(outputs[0])
    found = {start}
    pending = [start]
    while pending:
        belief = pending.pop()
        for query in range(query_count):
            for child in branch(
                outputs,
                transitions,
                belief,
                query,
            ):
                if child not in found:
                    found.add(child)
                    pending.append(child)
    return found


def wins(outputs, transitions, distortion, budget, start):
    beliefs = reachable(outputs, transitions, start)
    winning = {
        belief
        for belief in beliefs
        if len(belief) == 1
        and distortion[belief[0][0]][belief[0][1]] <= budget
    }
    while True:
        additions = set()
        for belief in beliefs - winning:
            currents = [current for _, current in belief]
            if len(currents) != len(set(currents)):
                continue
            for query in range(len(outputs[0])):
                children = branch(
                    outputs,
                    transitions,
                    belief,
                    query,
                )
                if all(child in winning for child in children):
                    additions.add(belief)
                    break
        if not additions:
            break
        winning |= additions
    return start in winning, len(beliefs)


def classify(outputs, transitions):
    n = len(outputs)
    start = tuple((state, state) for state in range(n))
    ordinary = tuple(tuple(0 for _ in range(n)) for _ in range(n))
    identity = tuple(
        tuple(
            0 if initial == current else 1
            for current in range(n)
        )
        for initial in range(n)
    )
    identified, _ = wins(
        outputs,
        transitions,
        ordinary,
        0,
        start,
    )
    restored, _ = wins(
        outputs,
        transitions,
        identity,
        0,
        start,
    )
    if not identified:
        assert not restored
        return "unidentifiable"
    if restored:
        return "identify_and_restore"
    return "identify_only_altering"


def all_binary_machines():
    for output_flat in product(range(2), repeat=4):
        outputs = (
            output_flat[:2],
            output_flat[2:],
        )
        for transition_flat in product(range(2), repeat=4):
            transitions = (
                transition_flat[:2],
                transition_flat[2:],
            )
            yield outputs, transitions


def transition_is_permutation(transitions, query):
    n = len(transitions)
    return {
        transitions[state][query]
        for state in range(n)
    } == set(range(n))


def main():
    classification = Counter()
    inverse_closed_classification = Counter()
    safe_implies_identification_checks = 0
    inverse_closed_checks = 0
    machine_count = 0

    for outputs, transitions in all_binary_machines():
        status = classify(outputs, transitions)
        classification[status] += 1
        safe_implies_identification_checks += 1
        if all(
            transition_is_permutation(transitions, query)
            for query in range(2)
        ):
            inverse_closed_classification[status] += 1
            assert status != "identify_only_altering"
            inverse_closed_checks += 1
        machine_count += 1

    assert machine_count == 256
    assert classification == {
        "identify_and_restore": 152,
        "identify_only_altering": 40,
        "unidentifiable": 64,
    }
    assert inverse_closed_classification == {
        "identify_and_restore": 48,
        "unidentifiable": 16,
    }
    assert inverse_closed_checks == 64

    pairwise_outputs = (
        (0, 0),
        (1, 0),
        (1, 1),
    )
    pairwise_transitions = (
        (0, 0),
        (1, 0),
        (1, 2),
    )
    zero3 = tuple(tuple(0 for _ in range(3)) for _ in range(3))
    pair_checks = 0
    for pair in combinations(range(3), 2):
        start = tuple((state, state) for state in pair)
        assert wins(
            pairwise_outputs,
            pairwise_transitions,
            zero3,
            0,
            start,
        )[0]
        pair_checks += 1
    full = tuple((state, state) for state in range(3))
    assert not wins(
        pairwise_outputs,
        pairwise_transitions,
        zero3,
        0,
        full,
    )[0]

    print(
        json.dumps(
            {
                "binary_machine_classification": dict(
                    sorted(classification.items())
                ),
                "binary_machines": machine_count,
                "inverse_closed_classification": dict(
                    sorted(inverse_closed_classification.items())
                ),
                "inverse_closed_checks": inverse_closed_checks,
                "pairwise_but_not_global_pair_checks": pair_checks,
                "registered": False,
                "safe_implies_identification_checks":
                    safe_implies_identification_checks,
                "status": "development_checks_passed",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
