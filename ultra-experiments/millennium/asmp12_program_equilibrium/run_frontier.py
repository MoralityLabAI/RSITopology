#!/usr/bin/env python3
"""Exact finite source-table program-equilibrium frontier census."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parent
PROGRAM_COUNT = 3

GAMES = {
    "prisoners_dilemma": {(1, 1): (3, 3), (1, 0): (0, 5), (0, 1): (5, 0), (0, 0): (1, 1)},
    "stag_hunt": {(1, 1): (4, 4), (1, 0): (0, 3), (0, 1): (3, 0), (0, 0): (2, 2)},
    "chicken": {(1, 1): (3, 3), (1, 0): (1, 4), (0, 1): (4, 1), (0, 0): (0, 0)},
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def rows() -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product((0, 1), repeat=PROGRAM_COUNT))


def catalogs() -> Iterable[tuple[tuple[int, ...], ...]]:
    return itertools.product(rows(), repeat=PROGRAM_COUNT)


def actions(catalog: Sequence[Sequence[int]], row_program: int, column_program: int) -> tuple[int, int]:
    return catalog[row_program][column_program], catalog[column_program][row_program]


def payoff(catalog: Sequence[Sequence[int]], game: str, row_program: int, column_program: int) -> tuple[int, int]:
    return GAMES[game][actions(catalog, row_program, column_program)]


def admitted(costs: Sequence[int], budget: int) -> tuple[int, ...]:
    return tuple(index for index, cost in enumerate(costs) if cost <= budget)


def pure_equilibria(
    catalog: Sequence[Sequence[int]], game: str, programs: Sequence[int]
) -> tuple[tuple[int, int], ...]:
    equilibria: list[tuple[int, int]] = []
    for row_program in programs:
        for column_program in programs:
            current = payoff(catalog, game, row_program, column_program)
            row_profitable = any(
                payoff(catalog, game, alternative, column_program)[0] > current[0]
                for alternative in programs
            )
            column_profitable = any(
                payoff(catalog, game, row_program, alternative)[1] > current[1]
                for alternative in programs
            )
            if not row_profitable and not column_profitable:
                equilibria.append((row_program, column_program))
    return tuple(equilibria)


def equilibrium_record(
    catalog: Sequence[Sequence[int]], game: str, costs: Sequence[int], budget: int
) -> dict[str, object]:
    programs = admitted(costs, budget)
    profiles = pure_equilibria(catalog, game, programs)
    payoff_set = sorted({payoff(catalog, game, *profile) for profile in profiles})
    cooperative = sorted(profile for profile in profiles if actions(catalog, *profile) == (1, 1))
    return {
        "programs": list(programs),
        "profiles": [list(profile) for profile in profiles],
        "payoffs": [list(value) for value in payoff_set],
        "cooperative_profiles": [list(profile) for profile in cooperative],
    }


def extensional_on_duplicates(catalog: Sequence[Sequence[int]]) -> bool:
    for left in range(PROGRAM_COUNT):
        for right in range(left + 1, PROGRAM_COUNT):
            if tuple(catalog[left]) != tuple(catalog[right]):
                continue
            if any(catalog[observer][left] != catalog[observer][right] for observer in range(PROGRAM_COUNT)):
                return False
    return True


def source_blind(catalog: Sequence[Sequence[int]]) -> bool:
    return all(len(set(row)) == 1 for row in catalog)


def profitable_new_deviations(
    catalog: Sequence[Sequence[int]], game: str, profile: tuple[int, int], new_program: int
) -> list[dict[str, object]]:
    row_program, column_program = profile
    current = payoff(catalog, game, row_program, column_program)
    out: list[dict[str, object]] = []
    row_value = payoff(catalog, game, new_program, column_program)[0]
    if row_value > current[0]:
        older_matches = [
            older for older in range(new_program)
            if tuple(catalog[older]) == tuple(catalog[new_program])
        ]
        out.append(
            {
                "player": 0,
                "gain": row_value - current[0],
                "older_equivalent_programs": older_matches,
                "opponent_distinguishes_equivalent": any(
                    catalog[column_program][older] != catalog[column_program][new_program]
                    for older in older_matches
                ),
            }
        )
    column_value = payoff(catalog, game, row_program, new_program)[1]
    if column_value > current[1]:
        older_matches = [
            older for older in range(new_program)
            if tuple(catalog[older]) == tuple(catalog[new_program])
        ]
        out.append(
            {
                "player": 1,
                "gain": column_value - current[1],
                "older_equivalent_programs": older_matches,
                "opponent_distinguishes_equivalent": any(
                    catalog[row_program][older] != catalog[row_program][new_program]
                    for older in older_matches
                ),
            }
        )
    return out


def transitions(catalog: Sequence[Sequence[int]], game: str) -> list[dict[str, object]]:
    costs = (1, 2, 3)
    out: list[dict[str, object]] = []
    for budget in (1, 2):
        before = equilibrium_record(catalog, game, costs, budget)
        after = equilibrium_record(catalog, game, costs, budget + 1)
        after_profiles = {tuple(profile) for profile in after["profiles"]}
        for profile_list in before["cooperative_profiles"]:
            profile = tuple(profile_list)
            if profile in after_profiles:
                continue
            deviations = profitable_new_deviations(catalog, game, profile, budget)
            syntax = any(
                item["older_equivalent_programs"] and item["opponent_distinguishes_equivalent"]
                for item in deviations
            )
            out.append(
                {
                    "kind": "cooperative_profile_death",
                    "from_budget": budget,
                    "to_budget": budget + 1,
                    "profile": list(profile),
                    "syntax_equivalence_exploited": syntax,
                    "deviations": deviations,
                }
            )
        before_payoffs = {tuple(value) for value in before["payoffs"]}
        after_payoffs = {tuple(value) for value in after["payoffs"]}
        for value in sorted(before_payoffs - after_payoffs):
            out.append(
                {
                    "kind": "payoff_death",
                    "from_budget": budget,
                    "to_budget": budget + 1,
                    "payoff": list(value),
                }
            )
        for value in sorted(after_payoffs - before_payoffs):
            out.append(
                {
                    "kind": "payoff_birth",
                    "from_budget": budget,
                    "to_budget": budget + 1,
                    "payoff": list(value),
                }
            )
    return out


def canonical_catalog() -> tuple[tuple[int, ...], ...]:
    return ((0, 0, 0), (0, 1, 1), (0, 0, 0))


def repaired_catalog() -> tuple[tuple[int, ...], ...]:
    return ((0, 0, 0), (0, 1, 0), (0, 0, 0))


def run_census() -> dict[str, object]:
    counts = {
        game: {
            "catalogs": 0,
            "catalogs_with_cooperative_death": 0,
            "catalogs_with_payoff_death": 0,
            "catalogs_with_syntax_equivalence_death": 0,
            "extensional_catalogs": 0,
            "extensional_syntax_equivalence_deaths": 0,
            "source_blind_catalogs": 0,
            "source_blind_syntax_equivalence_deaths": 0,
        }
        for game in GAMES
    }
    first_witnesses: dict[str, object] = {}
    padding_exact = True
    catalog_count = 0
    for catalog in catalogs():
        catalog_count += 1
        extensional = extensional_on_duplicates(catalog)
        blind = source_blind(catalog)
        for game in GAMES:
            summary = counts[game]
            summary["catalogs"] += 1
            if extensional:
                summary["extensional_catalogs"] += 1
            if blind:
                summary["source_blind_catalogs"] += 1
            events = transitions(catalog, game)
            coop_deaths = [event for event in events if event["kind"] == "cooperative_profile_death"]
            payoff_deaths = [event for event in events if event["kind"] == "payoff_death"]
            syntax_deaths = [event for event in coop_deaths if event["syntax_equivalence_exploited"]]
            summary["catalogs_with_cooperative_death"] += bool(coop_deaths)
            summary["catalogs_with_payoff_death"] += bool(payoff_deaths)
            summary["catalogs_with_syntax_equivalence_death"] += bool(syntax_deaths)
            if extensional:
                summary["extensional_syntax_equivalence_deaths"] += bool(syntax_deaths)
            if blind:
                summary["source_blind_syntax_equivalence_deaths"] += bool(syntax_deaths)
            if syntax_deaths and game not in first_witnesses:
                first_witnesses[game] = {
                    "catalog": [list(row) for row in catalog],
                    "event": syntax_deaths[0],
                }
            for budget in (1, 2, 3):
                primary = equilibrium_record(catalog, game, (1, 2, 3), budget)
                padded = equilibrium_record(catalog, game, (3, 4, 5), budget + 2)
                padding_exact = padding_exact and primary == padded

    canonical_events = transitions(canonical_catalog(), "prisoners_dilemma")
    repaired_before = equilibrium_record(repaired_catalog(), "prisoners_dilemma", (1, 2, 3), 2)
    repaired_after = equilibrium_record(repaired_catalog(), "prisoners_dilemma", (1, 2, 3), 3)
    canonical_syntax = [
        event for event in canonical_events
        if event["kind"] == "cooperative_profile_death"
        and event["from_budget"] == 2
        and event["profile"] == [1, 1]
        and event["syntax_equivalence_exploited"]
    ]
    canonical_payoff_death = any(
        event["kind"] == "payoff_death"
        and event["from_budget"] == 2
        and event["payoff"] == [3, 3]
        for event in canonical_events
    )
    repaired_survives = [1, 1] in repaired_before["cooperative_profiles"] and [1, 1] in repaired_after["cooperative_profiles"]

    gates = {
        "U0_universe": catalog_count == 512 and all(value["catalogs"] == 512 for value in counts.values()),
        "W0_witness": bool(canonical_syntax) and canonical_payoff_death,
        "L0_liveness": counts["prisoners_dilemma"]["catalogs_with_cooperative_death"] > 0
        and counts["prisoners_dilemma"]["catalogs_with_payoff_death"] > 0,
        "E0_extensional_control": repaired_survives
        and all(value["extensional_syntax_equivalence_deaths"] == 0 for value in counts.values()),
        "N0_source_blind_null": all(value["source_blind_syntax_equivalence_deaths"] == 0 for value in counts.values()),
        "P0_padding": padding_exact,
    }
    verdict = "finite_pure_frontier_nonmonotonicity_demonstrated" if all(gates.values()) else "instrument_failed"
    return {
        "schema_version": "asmp12_finite_program_frontier_result_v0_1",
        "verdict": verdict,
        "gates": gates,
        "catalog_count": catalog_count,
        "catalog_game_cases": catalog_count * len(GAMES),
        "counts": counts,
        "canonical_events": canonical_events,
        "repaired_survives": repaired_survives,
        "first_witnesses": first_witnesses,
    }


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def validate_registration(path: Path) -> dict[str, object]:
    registration = json.loads(path.read_text(encoding="utf-8"))
    bindings = registration["bindings"]
    files = {
        "prior_art_sha256": ROOT / "PRIOR_ART_v0_1.md",
        "protocol_sha256": ROOT / "PROTOCOL_v0_1.md",
        "runner_sha256": ROOT / "run_frontier.py",
        "tests_sha256": ROOT / "test_frontier.py",
    }
    mismatches = [key for key, file_path in files.items() if sha256_file(file_path) != bindings[key]]
    if mismatches:
        raise RuntimeError(f"registration binding mismatch: {mismatches}")
    return registration


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    registration = validate_registration(args.registration.resolve())
    result = run_census()
    result_path = args.output_dir.resolve() / "result.json"
    atomic_json(result_path, result)
    receipt = {
        "schema_version": "asmp12_finite_program_frontier_receipt_v0_1",
        "registration_sha256": sha256_file(args.registration.resolve()),
        "registration_source_commit": registration["source_commit"],
        "result_sha256": sha256_file(result_path),
        "verdict": result["verdict"],
    }
    atomic_json(args.output_dir.resolve() / "receipt.json", receipt)
    print(json.dumps({"gates": result["gates"], "verdict": result["verdict"]}, sort_keys=True))
    return 0 if result["verdict"] != "instrument_failed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

