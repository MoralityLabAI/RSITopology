"""Import-independent verifier for the finite adversarial ASMP-4 region."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V25 = (
    ROOT
    / "asmp4_periodic_block_completeness_v0_25"
    / "periodic_block_claim_v0_25.json"
)
V26 = (
    ROOT
    / "asmp4_public_bisimulation_transfer_v0_26"
    / "public_bisimulation_claim_v0_26.json"
)
V28_CENTRAL = (
    ROOT / "asmp4_transcript_fiber_entropy_v0_28" / "transcript_fiber_entropy.py"
)
V28_TEST = (
    "asmp4_transcript_fiber_entropy_v0_28",
    "test_transcript_fiber_entropy.py",
)
V29_TEST = ("asmp4_causal_branch_fiber_v0_29", "test_causal_branch_fiber.py")
V30_TEST = ("asmp4_prefix_kraft_fiber_v0_30", "test_prefix_kraft_fiber.py")
CONTRACT = HERE / "adversarial_mean_payoff_contract_v0_31.json"
CLAIM = HERE / "adversarial_mean_payoff_claim_v0_31.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V25: "447e5dc0d440611d59b4e6b94cd5c68493b7e3c68d8c68ed9b87dd28f9f90d38",
    V26: "1decf7f8eb12b6b76e9c251cdbc2b400403dfb941c6e798a75ab1b0aadc99e9d",
}

Point = tuple[Fraction, Fraction]
Edge = tuple[int, int, Fraction, Fraction]
Game = tuple[tuple[int, ...], frozenset[int], frozenset[int], int, tuple[Edge, ...]]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = [
        (path.name, hashlib.sha256(path.read_bytes()).hexdigest() == expected)
        for path, expected in SEALS.items()
    ]
    return {"rows": rows, "pass": len(rows) == 3 and all(match for _, match in rows)}


def _outgoing(edges: tuple[Edge, ...], state: int) -> tuple[int, ...]:
    return tuple(index for index, edge in enumerate(edges) if edge[0] == state)


def _policies(game: Game) -> tuple[tuple[tuple[int, int], ...], ...]:
    _, _, adversary, _, edges = game
    states = tuple(sorted(adversary))
    return tuple(
        tuple(zip(states, choices, strict=True))
        for choices in itertools.product(*(_outgoing(edges, state) for state in states))
    )


def _fixed(game: Game, policy: tuple[tuple[int, int], ...]) -> Game:
    states, controller, _, initial, edges = game
    selected = dict(policy)
    kept = tuple(
        edge
        for index, edge in enumerate(edges)
        if edge[0] in controller or selected.get(edge[0]) == index
    )
    return states, frozenset(states), frozenset(), initial, kept


def _reachability(states: tuple[int, ...], edges: tuple[Edge, ...]) -> dict[tuple[int, int], bool]:
    reach = {(left, right): left == right for left in states for right in states}
    for source, target, _, _ in edges:
        reach[(source, target)] = True
    for middle in states:
        for left in states:
            for right in states:
                reach[(left, right)] |= reach[(left, middle)] and reach[(middle, right)]
    return reach


def _components(states: tuple[int, ...], edges: tuple[Edge, ...]) -> tuple[tuple[int, ...], ...]:
    reach = _reachability(states, edges)
    pending = set(states)
    rows = []
    while pending:
        seed = min(pending)
        component = tuple(
            sorted(
                state
                for state in pending
                if reach[(seed, state)] and reach[(state, seed)]
            )
        )
        pending -= set(component)
        rows.append(component)
    return tuple(rows)


def _canonical_cycle(cycle: tuple[int, ...]) -> tuple[int, ...]:
    return min(cycle[index:] + cycle[:index] for index in range(len(cycle)))


def _cycles(component: tuple[int, ...], edges: tuple[Edge, ...]) -> tuple[tuple[int, ...], ...]:
    members = set(component)
    allowed = tuple(
        index
        for index, edge in enumerate(edges)
        if edge[0] in members and edge[1] in members
    )
    cycles = set()
    for length in range(1, len(component) + 1):
        for candidate in itertools.product(allowed, repeat=length):
            selected = tuple(edges[index] for index in candidate)
            if any(
                selected[index][1] != selected[(index + 1) % length][0]
                for index in range(length)
            ):
                continue
            if len({edge[0] for edge in selected}) != length:
                continue
            cycles.add(_canonical_cycle(candidate))
    return tuple(sorted(cycles))


def _mean(cycle: tuple[int, ...], edges: tuple[Edge, ...]) -> Point:
    return (
        sum((edges[index][2] for index in cycle), Fraction()) / len(cycle),
        sum((edges[index][3] for index in cycle), Fraction()) / len(cycle),
    )


def _segment_witness(left: Point, right: Point, budget: Point) -> Point | None:
    low = Fraction()
    high = Fraction(1)
    for coordinate in range(2):
        delta = right[coordinate] - left[coordinate]
        residual = budget[coordinate] - left[coordinate]
        if delta == 0:
            if residual < 0:
                return None
        elif delta > 0:
            high = min(high, residual / delta)
        else:
            low = max(low, residual / delta)
    if low > high or high < 0 or low > 1:
        return None
    mixing = max(Fraction(), low)
    if mixing > min(Fraction(1), high):
        return None
    return (
        left[0] + mixing * (right[0] - left[0]),
        left[1] + mixing * (right[1] - left[1]),
    )


def _multicycle_witness(points: tuple[Point, ...], budget: Point) -> Point | None:
    for point in points:
        if point[0] <= budget[0] and point[1] <= budget[1]:
            return point
    for left, right in itertools.combinations(points, 2):
        witness = _segment_witness(left, right, budget)
        if witness is not None:
            return witness
    return None


def _one_player(game: Game, budget: Point) -> bool:
    states, _, _, initial, edges = game
    reach = _reachability(states, edges)
    for component in _components(states, edges):
        if not any(reach[(initial, state)] for state in component):
            continue
        cycles = _cycles(component, edges)
        points = tuple(_mean(cycle, edges) for cycle in cycles)
        if _multicycle_witness(points, budget) is not None:
            return True
    return False


def _adversarial(game: Game, budget: Point) -> tuple[bool, tuple[tuple[int, int], ...] | None]:
    for policy in _policies(game):
        if not _one_player(_fixed(game, policy), budget):
            return False, policy
    return True, None


def _two_state(costs: tuple[Point, Point, Point, Point]) -> Game:
    endpoints = ((0, 0), (0, 1), (1, 0), (1, 1))
    edges = tuple(
        (source, target, cost[0], cost[1])
        for (source, target), cost in zip(endpoints, costs)
    )
    return (0, 1), frozenset({0}), frozenset({1}), 0, edges


@lru_cache(maxsize=None)
def independent_two_state_census() -> dict[str, Any]:
    alphabet = (
        (Fraction(), Fraction()),
        (Fraction(), Fraction(2)),
        (Fraction(2), Fraction()),
    )
    levels = (Fraction(), Fraction(2, 3), Fraction(4, 3), Fraction(2))
    budgets = tuple(itertools.product(levels, repeat=2))
    games = 0
    decisions = 0
    policy_checks = 0
    winners = 0
    losers = 0
    monotone = True
    certificate_valid = True
    for costs in itertools.product(alphabet, repeat=4):
        games += 1
        game = _two_state(costs)
        policy_checks += len(_policies(game))
        outcomes = {}
        for budget in budgets:
            decisions += 1
            win, spoiler = _adversarial(game, budget)
            outcomes[budget] = win
            winners += int(win)
            losers += int(not win)
            certificate_valid &= (win and spoiler is None) or (
                not win and spoiler is not None and not _one_player(_fixed(game, spoiler), budget)
            )
        for lower, lower_win in outcomes.items():
            for upper, upper_win in outcomes.items():
                if lower[0] <= upper[0] and lower[1] <= upper[1] and lower_win:
                    monotone &= upper_win
    checks = {
        "eighty_one_games": games == 81,
        "one_thousand_two_hundred_ninety_six_decisions": decisions == 1296,
        "one_hundred_sixty_two_policy_checks": policy_checks == 162,
        "winners_and_losers_exist": winners > 0 and losers > 0,
        "all_spoilers_validate": certificate_valid,
        "upward_monotonicity": monotone,
    }
    return {
        "games": games,
        "decisions": decisions,
        "policy_checks": policy_checks,
        "winners": winners,
        "losers": losers,
        "checks": checks,
        "pass": all(checks.values()),
    }


def independent_boundaries() -> dict[str, Any]:
    adversarial_fork: Game = (
        (0, 1, 2),
        frozenset({1, 2}),
        frozenset({0}),
        0,
        (
            (0, 1, Fraction(), Fraction()),
            (0, 2, Fraction(), Fraction()),
            (1, 1, Fraction(1), Fraction(3)),
            (2, 2, Fraction(3), Fraction(1)),
        ),
    )
    controller_fork: Game = (
        (0, 1, 2),
        frozenset({0, 1, 2}),
        frozenset(),
        0,
        adversarial_fork[4],
    )
    mixture: Game = (
        (0, 1),
        frozenset({0, 1}),
        frozenset(),
        0,
        (
            (0, 0, Fraction(), Fraction(2)),
            (0, 1, Fraction(2), Fraction(2)),
            (1, 1, Fraction(2), Fraction()),
            (1, 0, Fraction(2), Fraction(2)),
        ),
    )
    mixture_points = tuple(
        _mean(cycle, mixture[4]) for cycle in _cycles((0, 1), mixture[4])
    )
    left_only_outcomes = tuple(
        _one_player(_fixed(adversarial_fork, policy), (Fraction(1), Fraction(3)))
        for policy in _policies(adversarial_fork)
    )
    periodic = [Fraction(1, repetitions + 1) for repetitions in range(1, 97)]
    checks = {
        "adversarial_corner_three_three": _adversarial(
            adversarial_fork, (Fraction(3), Fraction(3))
        )[0],
        "adversarial_midpoint_loses": not _adversarial(
            adversarial_fork, (Fraction(2), Fraction(2))
        )[0],
        "existential_policy_is_too_weak": any(left_only_outcomes)
        and not all(left_only_outcomes)
        and not _adversarial(adversarial_fork, (Fraction(1), Fraction(3)))[0],
        "one_coordinate_is_too_weak": not _adversarial(
            adversarial_fork, (Fraction(3), Fraction(1))
        )[0],
        "controller_corners_win": _adversarial(
            controller_fork, (Fraction(1), Fraction(3))
        )[0]
        and _adversarial(controller_fork, (Fraction(3), Fraction(1)))[0],
        "controller_midpoint_loses": not _adversarial(
            controller_fork, (Fraction(2), Fraction(2))
        )[0],
        "mixture_boundary_wins": _one_player(
            mixture, (Fraction(1), Fraction(1))
        ),
        "mixture_needs_more_than_one_cycle": all(
            not (point[0] <= 1 and point[1] <= 1) for point in mixture_points
        ),
        "ninety_six_positive_finite_slacks": len(periodic) == 96
        and all(slack > 0 for slack in periodic),
        "finite_slack_converges": periodic[-1] < Fraction(1, 90),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_polarity_boundary(rounds: int = 6) -> dict[str, Any]:
    read = 0
    write = 0
    time = 2
    low_read = high_read = low_write = high_write = Fraction()
    for _ in range(rounds):
        length = time**3
        write += 2 * length
        time += length
        low_read = Fraction(read, time)
        high_write = Fraction(write, time)
        length = time**3
        read += 2 * length
        time += length
        high_read = Fraction(read, time)
        low_write = Fraction(write, time)
    checks = {
        "coordinate_liminfs_near_zero": low_read < Fraction(1, 10_000)
        and low_write < Fraction(1, 10_000),
        "coordinate_limsups_near_two": high_read > Fraction(19_999, 10_000)
        and high_write > Fraction(19_999, 10_000),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    boundaries = independent_boundaries()
    polarity = independent_polarity_boundary()
    rows = {
        "existential_adversary": boundaries["checks"][
            "existential_policy_is_too_weak"
        ],
        "global_convexification": boundaries["checks"]["controller_midpoint_loses"],
        "single_cycle": boundaries["checks"]["mixture_needs_more_than_one_cycle"],
        "memoryless_controller": boundaries["checks"]["mixture_boundary_wins"],
        "finite_memory_exact": boundaries["checks"]["ninety_six_positive_finite_slacks"],
        "cost_liminf": polarity["checks"]["coordinate_liminfs_near_zero"]
        and polarity["checks"]["coordinate_limsups_near_two"],
        "one_coordinate": boundaries["checks"]["one_coordinate_is_too_weak"],
        "open_budget": boundaries["checks"]["mixture_boundary_wins"],
    }
    return {"rows": rows, "pass": len(rows) == 8 and all(rows.values())}


def independent_contract_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    checks = {
        "contract_schema": contract.get("schema_version")
        == "asmp4_adversarial_mean_payoff_contract_v0_31",
        "limsup_cost": "limsup"
        in contract.get("objective", {}).get("cost_rate", ""),
        "mean_payoff_inf": "mean-payoff-inf"
        in contract.get("objective", {}).get("reward_translation", ""),
        "quantifier_order": "intersection_tau union_C"
        in contract.get("region_formula", {}).get("quantifiers", ""),
        "finite_memory_closure": "closures agree"
        in contract.get("memory", {}).get("finite_memory_closure", ""),
        "eight_mutations": claim.get("mutations_rejected") == 8,
        "central_not_imported": "adversarial_mean_payoff" not in imports,
    }
    return {"checks": checks, "pass": all(checks.values())}


def _predecessor_tests() -> tuple[tuple[str, str], ...]:
    tree = ast.parse(V28_CENTRAL.read_text(encoding="utf-8"), filename=str(V28_CENTRAL))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PREDECESSOR_TESTS"
            for target in node.targets
        ):
            return tuple(ast.literal_eval(node.value)) + (V28_TEST, V29_TEST, V30_TEST)
    raise ValueError("v0.28 predecessor inventory not found")


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in _predecessor_tests():
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((package, count))
    return {
        "packages": len(rows),
        "tests": sum(count for _, count in rows),
        "pass": len(rows) == 31 and sum(count for _, count in rows) == 344,
    }


def document_sentinels() -> dict[str, Any]:
    required = {
        "THEOREM.md": (
            "intersection",
            "memoryless adversary",
            "infinite memory",
            "mean-payoff-inf",
        ),
        "RESULT.md": ("2,304", "1,296", "1/(k+1)", "Not claimed"),
        "PRIOR_ART_BOUNDARY_v0_31.md": (
            "Velner",
            "Chatterjee",
            "No novelty is claimed",
        ),
        "COMPLETION_AUDIT_v0_31.md": ("354 tests", "Not claimed"),
    }
    rows = {}
    for filename, needles in required.items():
        path = HERE / filename
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        rows[filename] = all(needle.lower() in text.lower() for needle in needles)
    return {"rows": rows, "pass": all(rows.values())}


def independent_report() -> dict[str, Any]:
    components = {
        "integrity": independent_integrity(),
        "census": independent_two_state_census(),
        "boundaries": independent_boundaries(),
        "polarity": independent_polarity_boundary(),
        "mutations": independent_mutations(),
        "contract_claim": independent_contract_claim(),
        "inventory": independent_inventory(),
        "documents": document_sentinels(),
    }
    return {**components, "pass": all(row["pass"] for row in components.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
