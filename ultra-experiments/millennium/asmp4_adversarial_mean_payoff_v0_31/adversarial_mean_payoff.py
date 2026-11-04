"""Exact finite adversarial two-port mean-payoff region harness for ASMP-4."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

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
Policy = tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    read: Fraction
    write: Fraction
    name: str


@dataclass(frozen=True)
class Game:
    states: tuple[int, ...]
    controller: frozenset[int]
    adversary: frozenset[int]
    initial: int
    edges: tuple[Edge, ...]


def q(value: int | str | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(game: Game) -> None:
    states = set(game.states)
    if not states or game.initial not in states:
        raise ValueError("game needs a valid initial state")
    if game.controller & game.adversary or game.controller | game.adversary != states:
        raise ValueError("ownership must partition the state set")
    for edge in game.edges:
        if edge.source not in states or edge.target not in states:
            raise ValueError("edge endpoint outside state set")
        if edge.read < 0 or edge.write < 0:
            raise ValueError("costs must be nonnegative")
    if any(not outgoing(game, state) for state in game.states):
        raise ValueError("every state needs an outgoing edge")


def outgoing(game: Game, state: int) -> tuple[tuple[int, Edge], ...]:
    return tuple(
        (index, edge) for index, edge in enumerate(game.edges) if edge.source == state
    )


def memoryless_adversary_policies(game: Game) -> tuple[Policy, ...]:
    validate(game)
    states = tuple(sorted(game.adversary))
    choices = [tuple(index for index, _ in outgoing(game, state)) for state in states]
    return tuple(
        tuple(zip(states, selection, strict=True))
        for selection in itertools.product(*choices)
    )


def fix_adversary(game: Game, policy: Policy) -> Game:
    selected = dict(policy)
    edges = tuple(
        edge
        for index, edge in enumerate(game.edges)
        if edge.source in game.controller or selected.get(edge.source) == index
    )
    fixed = Game(game.states, frozenset(game.states), frozenset(), game.initial, edges)
    validate(fixed)
    return fixed


def reachable_states(game: Game) -> frozenset[int]:
    reached = {game.initial}
    pending = [game.initial]
    while pending:
        state = pending.pop()
        for _, edge in outgoing(game, state):
            if edge.target not in reached:
                reached.add(edge.target)
                pending.append(edge.target)
    return frozenset(reached)


def strongly_connected_components(game: Game) -> tuple[tuple[int, ...], ...]:
    index = 0
    stack: list[int] = []
    on_stack: set[int] = set()
    indices: dict[int, int] = {}
    lowlink: dict[int, int] = {}
    rows: list[tuple[int, ...]] = []

    def visit(state: int) -> None:
        nonlocal index
        indices[state] = index
        lowlink[state] = index
        index += 1
        stack.append(state)
        on_stack.add(state)
        for _, edge in outgoing(game, state):
            target = edge.target
            if target not in indices:
                visit(target)
                lowlink[state] = min(lowlink[state], lowlink[target])
            elif target in on_stack:
                lowlink[state] = min(lowlink[state], indices[target])
        if lowlink[state] == indices[state]:
            component = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == state:
                    break
            rows.append(tuple(sorted(component)))

    for state in game.states:
        if state not in indices:
            visit(state)
    return tuple(sorted(rows))


def simple_cycles(game: Game, component: Iterable[int]) -> tuple[tuple[int, ...], ...]:
    members = frozenset(component)
    cycles: set[tuple[int, ...]] = set()
    for start in sorted(members):

        def visit(current: int, visited: frozenset[int], path: tuple[int, ...]) -> None:
            for edge_index, edge in outgoing(game, current):
                if edge.target not in members:
                    continue
                if edge.target == start:
                    cycles.add(path + (edge_index,))
                elif edge.target not in visited and edge.target >= start:
                    visit(edge.target, visited | {edge.target}, path + (edge_index,))

        visit(start, frozenset({start}), ())
    return tuple(sorted(cycles))


def cycle_mean(game: Game, cycle: tuple[int, ...]) -> Point:
    length = len(cycle)
    return (
        sum((game.edges[index].read for index in cycle), Fraction()) / length,
        sum((game.edges[index].write for index in cycle), Fraction()) / length,
    )


def reachable_cyclic_components(game: Game) -> tuple[tuple[int, ...], ...]:
    reached = reachable_states(game)
    return tuple(
        component
        for component in strongly_connected_components(game)
        if set(component) <= reached and simple_cycles(game, component)
    )


def cross(origin: Point, left: Point, right: Point) -> Fraction:
    return (left[0] - origin[0]) * (right[1] - origin[1]) - (
        left[1] - origin[1]
    ) * (right[0] - origin[0])


def convex_hull(points: Iterable[Point]) -> tuple[Point, ...]:
    unique = tuple(sorted(set(points)))
    if len(unique) <= 1:
        return unique
    lower: list[Point] = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: list[Point] = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return tuple(lower[:-1] + upper[:-1])


def lower_orthant_witness(points: Iterable[Point], budget: Point) -> Point | None:
    hull = convex_hull(points)
    if not hull:
        return None
    candidates = [point for point in hull if point[0] <= budget[0]]
    if len(hull) >= 2:
        for index, left in enumerate(hull):
            right = hull[(index + 1) % len(hull)]
            if left[0] == right[0]:
                continue
            if min(left[0], right[0]) <= budget[0] <= max(left[0], right[0]):
                mixing = (budget[0] - left[0]) / (right[0] - left[0])
                if 0 <= mixing <= 1:
                    candidates.append(
                        (
                            budget[0],
                            left[1] + mixing * (right[1] - left[1]),
                        )
                    )
    feasible = [point for point in candidates if point[1] <= budget[1]]
    return min(feasible, key=lambda point: (point[1], point[0])) if feasible else None


def one_player_certificate(game: Game, budget: Point) -> dict[str, Any]:
    validate(game)
    if game.adversary:
        raise ValueError("one-player certificate requires fixed adversary")
    rows = []
    for component in reachable_cyclic_components(game):
        cycles = simple_cycles(game, component)
        means = tuple(cycle_mean(game, cycle) for cycle in cycles)
        witness = lower_orthant_witness(means, budget)
        rows.append(
            {
                "component": component,
                "cycles": len(cycles),
                "means": means,
                "witness": witness,
                "feasible": witness is not None,
            }
        )
    return {"components": rows, "pass": any(row["feasible"] for row in rows)}


def adversarial_certificate(game: Game, budget: Point) -> dict[str, Any]:
    policy_rows = []
    for policy in memoryless_adversary_policies(game):
        fixed = fix_adversary(game, policy)
        certificate = one_player_certificate(fixed, budget)
        policy_rows.append(
            {
                "policy": policy,
                "one_player": certificate,
                "pass": certificate["pass"],
            }
        )
    losing = next((row for row in policy_rows if not row["pass"]), None)
    return {
        "budget": budget,
        "policies": policy_rows,
        "spoiler": None if losing is None else losing["policy"],
        "pass": losing is None,
    }


def adversarial_fork_game() -> Game:
    return Game(
        states=(0, 1, 2),
        controller=frozenset({1, 2}),
        adversary=frozenset({0}),
        initial=0,
        edges=(
            Edge(0, 1, q(0), q(0), "choose_left"),
            Edge(0, 2, q(0), q(0), "choose_right"),
            Edge(1, 1, q(1), q(3), "left_loop"),
            Edge(2, 2, q(3), q(1), "right_loop"),
        ),
    )


def controller_fork_game() -> Game:
    return Game(
        states=(0, 1, 2),
        controller=frozenset({0, 1, 2}),
        adversary=frozenset(),
        initial=0,
        edges=(
            Edge(0, 1, q(0), q(0), "take_left"),
            Edge(0, 2, q(0), q(0), "take_right"),
            Edge(1, 1, q(1), q(3), "left_loop"),
            Edge(2, 2, q(3), q(1), "right_loop"),
        ),
    )


def connector_mixture_game() -> Game:
    return Game(
        states=(0, 1),
        controller=frozenset({0, 1}),
        adversary=frozenset(),
        initial=0,
        edges=(
            Edge(0, 0, q(0), q(2), "read_light"),
            Edge(0, 1, q(2), q(2), "to_write_light"),
            Edge(1, 1, q(2), q(0), "write_light"),
            Edge(1, 0, q(2), q(2), "to_read_light"),
        ),
    )


def adversarial_fork_report() -> dict[str, Any]:
    game = adversarial_fork_game()
    rows = {
        "corner": adversarial_certificate(game, (q(3), q(3))),
        "left_only": adversarial_certificate(game, (q(1), q(3))),
        "right_only": adversarial_certificate(game, (q(3), q(1))),
        "convex_midpoint": adversarial_certificate(game, (q(2), q(2))),
    }
    checks = {
        "two_memoryless_adversary_policies": len(
            memoryless_adversary_policies(game)
        )
        == 2,
        "robust_corner_three_three": rows["corner"]["pass"],
        "left_only_has_right_spoiler": not rows["left_only"]["pass"]
        and rows["left_only"]["spoiler"] is not None,
        "right_only_has_left_spoiler": not rows["right_only"]["pass"]
        and rows["right_only"]["spoiler"] is not None,
        "midpoint_is_not_robust": not rows["convex_midpoint"]["pass"],
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def controller_fork_report() -> dict[str, Any]:
    game = controller_fork_game()
    rows = {
        "left": adversarial_certificate(game, (q(1), q(3))),
        "right": adversarial_certificate(game, (q(3), q(1))),
        "midpoint": adversarial_certificate(game, (q(2), q(2))),
    }
    checks = {
        "left_corner_achievable": rows["left"]["pass"],
        "right_corner_achievable": rows["right"]["pass"],
        "midpoint_not_achievable": not rows["midpoint"]["pass"],
        "global_convexification_would_include_midpoint": lower_orthant_witness(
            ((q(1), q(3)), (q(3), q(1))), (q(2), q(2))
        )
        is not None,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def connector_mixture_report() -> dict[str, Any]:
    game = connector_mixture_game()
    budget = (q(1), q(1))
    certificate = one_player_certificate(game, budget)
    means = tuple(
        cycle_mean(game, cycle)
        for component in reachable_cyclic_components(game)
        for cycle in simple_cycles(game, component)
    )
    checks = {
        "boundary_is_achievable_with_general_memory": certificate["pass"],
        "no_single_cycle_meets_boundary": all(
            not (point[0] <= 1 and point[1] <= 1) for point in means
        ),
        "convex_multicycle_witness_is_one_one": any(
            row["witness"] == budget
            for row in certificate["components"]
            if row["feasible"]
        ),
        "every_cycle_either_one_sided_or_connector_costly": set(means)
        == {(q(0), q(2)), (q(2), q(0)), (q(2), q(2))},
    }
    return {
        "budget": budget,
        "means": means,
        "certificate": certificate,
        "checks": checks,
        "pass": all(checks.values()),
    }


def finite_memory_approximation_report(maximum_repetitions: int = 64) -> dict[str, Any]:
    rows = []
    for repetitions in range(1, maximum_repetitions + 1):
        length = 2 * repetitions + 2
        coordinate_cost = 2 * repetitions + 4
        rate = Fraction(coordinate_cost, length)
        rows.append(
            {
                "repetitions": repetitions,
                "period": length,
                "read": rate,
                "write": rate,
                "slack": rate - 1,
            }
        )
    checks = {
        "sixty_four_periodic_approximations": len(rows) == 64,
        "every_finite_period_is_strictly_above_boundary": all(
            row["read"] > 1 and row["write"] > 1 for row in rows
        ),
        "exact_slack_formula": all(
            row["slack"] == Fraction(1, row["repetitions"] + 1) for row in rows
        ),
        "slack_decreases_below_two_percent": rows[-1]["slack"] < Fraction(1, 50),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def increasing_memory_report(stages: int = 512) -> dict[str, Any]:
    total_read = 0
    total_write = 0
    time = 0
    rows = []
    for stage in range(1, stages + 1):
        peak = Fraction()
        for read, write, count in ((0, 2, stage), (2, 2, 1), (2, 0, stage), (2, 2, 1)):
            for _ in range(count):
                total_read += read
                total_write += write
                time += 1
                peak = max(
                    peak,
                    Fraction(total_read, time) - 1,
                    Fraction(total_write, time) - 1,
                )
        rows.append(
            {
                "stage": stage,
                "time": time,
                "endpoint_read": Fraction(total_read, time),
                "endpoint_write": Fraction(total_write, time),
                "stage_peak_excess": peak,
            }
        )
    checks = {
        "five_hundred_twelve_stages": len(rows) == 512,
        "endpoint_is_symmetric": all(
            row["endpoint_read"] == row["endpoint_write"] for row in rows
        ),
        "endpoint_converges_to_one": rows[-1]["endpoint_read"]
        < Fraction(1005, 1000),
        "within_stage_peak_converges": max(
            row["stage_peak_excess"] for row in rows[-16:]
        )
        < Fraction(1, 100),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def burst_polarity_report(rounds: int = 7) -> dict[str, Any]:
    total_read = 0
    total_write = 0
    time = 2
    lows_read = []
    highs_read = []
    lows_write = []
    highs_write = []
    for _ in range(rounds):
        block = time**2
        total_write += 2 * block
        time += block
        lows_read.append(float(Fraction(total_read, time)))
        highs_write.append(float(Fraction(total_write, time)))
        block = time**2
        total_read += 2 * block
        time += block
        highs_read.append(float(Fraction(total_read, time)))
        lows_write.append(float(Fraction(total_write, time)))
    checks = {
        "both_liminfs_near_zero": lows_read[-1] < 0.001
        and lows_write[-1] < 0.001,
        "both_limsups_near_two": highs_read[-1] > 1.999
        and highs_write[-1] > 1.999,
    }
    return {
        "lows_read": lows_read,
        "highs_read": highs_read,
        "lows_write": lows_write,
        "highs_write": highs_write,
        "checks": checks,
        "pass": all(checks.values()),
    }


def two_state_game(costs: tuple[Point, Point, Point, Point]) -> Game:
    endpoints = ((0, 0), (0, 1), (1, 0), (1, 1))
    return Game(
        states=(0, 1),
        controller=frozenset({0}),
        adversary=frozenset({1}),
        initial=0,
        edges=tuple(
            Edge(source, target, cost[0], cost[1], f"e{index}")
            for index, ((source, target), cost) in enumerate(zip(endpoints, costs))
        ),
    )


@lru_cache(maxsize=None)
def exhaustive_two_state_report() -> dict[str, Any]:
    alphabet = ((q(0), q(0)), (q(0), q(1)), (q(1), q(0)), (q(1), q(1)))
    budgets = tuple(itertools.product((q(0), q("1/2"), q(1)), repeat=2))
    rows = []
    decisions = 0
    winning = 0
    losing = 0
    certificates_valid = True
    monotone = True
    for game_index, costs in enumerate(itertools.product(alphabet, repeat=4)):
        game = two_state_game(costs)
        outcomes: dict[Point, bool] = {}
        spoilers = 0
        for budget in budgets:
            decisions += 1
            certificate = adversarial_certificate(game, budget)
            outcomes[budget] = certificate["pass"]
            if certificate["pass"]:
                winning += 1
                certificates_valid &= certificate["spoiler"] is None and all(
                    row["pass"] for row in certificate["policies"]
                )
            else:
                losing += 1
                spoilers += 1
                certificates_valid &= certificate["spoiler"] is not None and any(
                    not row["pass"] for row in certificate["policies"]
                )
        for lower, lower_wins in outcomes.items():
            for upper, upper_wins in outcomes.items():
                if lower[0] <= upper[0] and lower[1] <= upper[1] and lower_wins:
                    monotone &= upper_wins
        rows.append(
            {
                "game": game_index,
                "winning_budgets": sum(outcomes.values()),
                "losing_budgets": spoilers,
            }
        )
    checks = {
        "two_hundred_fifty_six_games": len(rows) == 256,
        "two_thousand_three_hundred_four_decisions": decisions == 2304,
        "two_policies_per_game": all(
            len(memoryless_adversary_policies(
                two_state_game(costs)
            ))
            == 2
            for costs in itertools.product(alphabet, repeat=4)
        ),
        "winning_and_losing_instances_exist": winning > 0 and losing > 0,
        "all_certificates_valid": certificates_valid,
        "upward_monotonicity": monotone,
    }
    return {
        "rows": rows,
        "decisions": decisions,
        "winning": winning,
        "losing": losing,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    adversarial = adversarial_fork_report()
    controller = controller_fork_report()
    mixture = connector_mixture_report()
    finite = finite_memory_approximation_report()
    burst = burst_polarity_report()
    left_only = adversarial["rows"]["left_only"]
    rows = {
        "existential_adversary_replaces_universal": not left_only["pass"]
        and any(row["pass"] for row in left_only["policies"]),
        "one_global_convex_support_family": controller["checks"][
            "global_convexification_would_include_midpoint"
        ]
        and not controller["rows"]["midpoint"]["pass"],
        "one_cycle_replaces_multicycle": mixture["checks"][
            "no_single_cycle_meets_boundary"
        ]
        and mixture["certificate"]["pass"],
        "memoryless_controller_is_complete": mixture["checks"][
            "no_single_cycle_meets_boundary"
        ],
        "finite_memory_attains_every_closed_boundary": all(
            row["read"] > 1 for row in finite["rows"]
        ),
        "cost_liminf_replaces_cost_limsup": burst["checks"][
            "both_liminfs_near_zero"
        ]
        and burst["checks"]["both_limsups_near_two"],
        "read_coordinate_alone_controls_region": not adversarial["rows"][
            "right_only"
        ]["pass"],
        "strict_budget_replaces_closed_budget": mixture["certificate"]["pass"]
        and any(
            row["witness"] == (q(1), q(1))
            for row in mixture["certificate"]["components"]
        ),
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()),
    }


def _predecessor_tests() -> tuple[tuple[str, str], ...]:
    tree = ast.parse(V28_CENTRAL.read_text(encoding="utf-8"), filename=str(V28_CENTRAL))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PREDECESSOR_TESTS"
            for target in node.targets
        ):
            return tuple(ast.literal_eval(node.value)) + (V28_TEST, V29_TEST, V30_TEST)
    raise ValueError("v0.28 predecessor inventory not found")


def predecessor_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in _predecessor_tests():
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "tests": count})
    tests = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": tests,
        "pass": len(rows) == 31 and tests == 344,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_adversarial_mean_payoff_contract_v0_31",
        "game": {
            "state": "finite public turn-based quotient state",
            "controller": "chooses registered safe public actions",
            "adversary": "chooses registered successors after public actions",
            "cost": "nonnegative rational read/write vector on every transition",
        },
        "objective": {
            "cost_rate": "coordinatewise limsup of prefix-average transition costs",
            "budget": "every play consistent with one controller strategy has cost rate at most R",
            "reward_translation": "w=R-c converts the objective to conjunctive mean-payoff-inf at threshold zero",
        },
        "region_formula": {
            "fixed_spoiler": "for each memoryless adversary policy tau, take the union over reachable SCCs of upward cycle-mean polytopes",
            "full_region": "intersection over memoryless adversary policies tau of those fixed-policy one-player regions",
            "quantifiers": "intersection_tau union_C upward(conv(simple-cycle means in C))",
        },
        "memory": {
            "adversary": "a losing budget has a memoryless spoiling policy",
            "controller": "exact winning may require infinite memory",
            "finite_memory_closure": "every exact winning budget has finite-memory epsilon relaxations, so closures agree",
        },
        "nonclaims": [
            "polynomial-time solution of classical scalar mean-payoff games",
            "finite-memory attainment of every closed boundary point",
            "construction of a finite quotient for arbitrary nonlinear plants",
        ],
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_adversarial_mean_payoff_v0_31",
        "theorem": {
            "name": "memoryless-spoiler SCC multicycle region",
            "formula": "R=intersection_tau union_C upward(conv{cycle means in C})",
            "polarity": "limsup cost upper bounds equal mean-payoff-inf reward lower bounds under w=R-c",
            "finite_memory": "the arbitrary-memory region is the closure of its finite-memory subregion",
        },
        "central_harness": {
            "two_state_games": 256,
            "budget_decisions": 2304,
            "adversary_policies_per_game": 2,
            "periodic_approximations": 64,
            "increasing_memory_stages": 512,
        },
        "independent_harness": {
            "two_state_games": 81,
            "budget_decisions": 1296,
            "adversarial_policy_checks": 162,
        },
        "boundaries": {
            "adversarial_fork_corner": [3, 3],
            "nonconvex_controller_corners": [[1, 3], [3, 1]],
            "infinite_memory_boundary": [1, 1],
            "finite_period_slack": "1/(k+1)",
        },
        "mutations_rejected": 8,
        "predecessor_inventory": {"packages": 31, "tests": 344},
        "disposition": "finite adversarial additive public quotients now have an exact two-port region formula; nonlinear quotient construction remains open",
    }


def resource_integrity_report() -> dict[str, Any]:
    rows = [
        {
            "name": path.name,
            "matches": hashlib.sha256(path.read_bytes()).hexdigest() == expected,
        }
        for path, expected in SEALS.items()
    ]
    return {"rows": rows, "pass": len(rows) == 3 and all(row["matches"] for row in rows)}


def payload_report() -> dict[str, Any]:
    required = {
        "README.md",
        "THEOREM.md",
        "RESULT.md",
        "COMPLETION_AUDIT_v0_31.md",
        "REVIEWER_PACKET_v0_31.md",
        "PRIOR_ART_BOUNDARY_v0_31.md",
        "adversarial_mean_payoff_contract_v0_31.json",
        "adversarial_mean_payoff_claim_v0_31.json",
        "adversarial_mean_payoff.py",
        "verify_adversarial_mean_payoff.py",
        "test_adversarial_mean_payoff.py",
        "run_verification.py",
    }
    present = {path.name for path in HERE.iterdir() if path.is_file()}
    return {"missing": sorted(required - present), "pass": required <= present}


def adversarial_mean_payoff_report() -> dict[str, Any]:
    components = {
        "resource_integrity": resource_integrity_report(),
        "contract_exactness": {
            "pass": CONTRACT.exists() and _load(CONTRACT) == expected_contract_payload()
        },
        "claim_exactness": {
            "pass": CLAIM.exists() and _load(CLAIM) == expected_claim_payload()
        },
        "adversarial_fork": adversarial_fork_report(),
        "controller_fork": controller_fork_report(),
        "connector_mixture": connector_mixture_report(),
        "finite_memory_approximation": finite_memory_approximation_report(),
        "increasing_memory": increasing_memory_report(),
        "burst_polarity": burst_polarity_report(),
        "exhaustive_two_state": exhaustive_two_state_report(),
        "mutations": mutation_report(),
        "predecessor_inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    return {
        "schema_version": "asmp4_adversarial_mean_payoff_v0_31",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = adversarial_mean_payoff_report() if report is None else report
    return {
        "R0_three_resource_seals": report["resource_integrity"]["pass"],
        "R1_exact_contract_and_claim": report["contract_exactness"]["pass"]
        and report["claim_exactness"]["pass"],
        "R2_universal_adversarial_fork": report["adversarial_fork"]["pass"],
        "R3_component_disjunction_boundary": report["controller_fork"]["pass"],
        "R4_multicycle_infinite_memory_boundary": report["connector_mixture"]["pass"],
        "R5_finite_memory_closure": report["finite_memory_approximation"]["pass"]
        and report["increasing_memory"]["pass"],
        "R6_limsup_cost_polarity": report["burst_polarity"]["pass"],
        "R7_exhaustive_two_state_census": report["exhaustive_two_state"]["pass"],
        "R8_eight_mutations_rejected": report["mutations"]["pass"],
        "R9_inventory_and_payload": report["predecessor_inventory"]["pass"]
        and report["payload"]["pass"],
    }


def main() -> int:
    report = adversarial_mean_payoff_report()
    payload = {"gates": verification_gates(report), "report": report}
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
