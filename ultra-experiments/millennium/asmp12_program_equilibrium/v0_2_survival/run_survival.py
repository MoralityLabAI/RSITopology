#!/usr/bin/env python3
"""Exact ASMP-12 budget-by-temptation equilibrium survival surface."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from fractions import Fraction
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent
V1_PATH = ROOT.parent / "run_frontier.py"
SPEC = importlib.util.spec_from_file_location("asmp12_v1", V1_PATH)
V1 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(V1)

R = Fraction(3)
FAMILIES = {
    "pd_order": {"R": R, "S": Fraction(0), "P": Fraction(1)},
    "chicken_order": {"R": R, "S": Fraction(1), "P": Fraction(0)},
}
TEMPTATIONS = tuple(Fraction(value) for value in (0, Fraction(1, 2), 1, 2, 3, 4, 5, 6))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def utilities(family: str, temptation: Fraction, actions: tuple[int, int]) -> tuple[Fraction, Fraction]:
    values = FAMILIES[family]
    if actions == (1, 1):
        return values["R"], values["R"]
    if actions == (1, 0):
        return values["S"], temptation
    if actions == (0, 1):
        return temptation, values["S"]
    return values["P"], values["P"]


def payoff(catalog: Sequence[Sequence[int]], family: str, temptation: Fraction, row: int, column: int) -> tuple[Fraction, Fraction]:
    return utilities(family, temptation, V1.actions(catalog, row, column))


def admitted(costs: Sequence[int], budget: int) -> tuple[int, ...]:
    return tuple(index for index, cost in enumerate(costs) if cost <= budget)


def deviation_gaps(
    catalog: Sequence[Sequence[int]], family: str, temptation: Fraction,
    profile: tuple[int, int], programs: Sequence[int]
) -> tuple[Fraction, ...]:
    row, column = profile
    current = payoff(catalog, family, temptation, row, column)
    gaps = [
        current[0] - payoff(catalog, family, temptation, alternative, column)[0]
        for alternative in programs if alternative != row
    ]
    gaps.extend(
        current[1] - payoff(catalog, family, temptation, row, alternative)[1]
        for alternative in programs if alternative != column
    )
    return tuple(gaps)


def equilibrium_record(
    catalog: Sequence[Sequence[int]], family: str, temptation: Fraction,
    costs: Sequence[int], budget: int
) -> dict[str, object]:
    programs = admitted(costs, budget)
    profiles: list[tuple[int, int]] = []
    margins: dict[str, str | None] = {}
    for row in programs:
        for column in programs:
            profile = (row, column)
            gaps = deviation_gaps(catalog, family, temptation, profile, programs)
            if all(gap >= 0 for gap in gaps):
                profiles.append(profile)
                margins[f"{row},{column}"] = str(min(gaps)) if gaps else None
    payoff_set = sorted({payoff(catalog, family, temptation, *profile) for profile in profiles})
    cooperative = sorted(profile for profile in profiles if V1.actions(catalog, *profile) == (1, 1))
    return {
        "programs": list(programs),
        "profiles": [list(profile) for profile in profiles],
        "payoffs": [[str(left), str(right)] for left, right in payoff_set],
        "cooperative_profiles": [list(profile) for profile in cooperative],
        "margins": margins,
    }


def new_deviation_details(
    catalog: Sequence[Sequence[int]], family: str, temptation: Fraction,
    profile: tuple[int, int], new_program: int
) -> list[dict[str, object]]:
    row, column = profile
    current = payoff(catalog, family, temptation, row, column)
    details: list[dict[str, object]] = []
    candidates = (
        (0, payoff(catalog, family, temptation, new_program, column)[0], column),
        (1, payoff(catalog, family, temptation, row, new_program)[1], row),
    )
    for player, value, opponent in candidates:
        if value <= current[player]:
            continue
        older = [index for index in range(new_program) if tuple(catalog[index]) == tuple(catalog[new_program])]
        distinguishes = any(catalog[opponent][index] != catalog[opponent][new_program] for index in older)
        details.append(
            {
                "player": player,
                "gain": str(value - current[player]),
                "older_equivalent_programs": older,
                "opponent_distinguishes_equivalent": distinguishes,
            }
        )
    return details


def transition_summary(
    catalog: Sequence[Sequence[int]], family: str, temptation: Fraction
) -> dict[str, object]:
    cooperative_deaths = 0
    payoff_deaths = 0
    syntax_deaths = 0
    for budget in (1, 2):
        before = equilibrium_record(catalog, family, temptation, (1, 2, 3), budget)
        after = equilibrium_record(catalog, family, temptation, (1, 2, 3), budget + 1)
        after_profiles = {tuple(profile) for profile in after["profiles"]}
        for profile_list in before["cooperative_profiles"]:
            profile = tuple(profile_list)
            if profile in after_profiles:
                continue
            cooperative_deaths += 1
            details = new_deviation_details(catalog, family, temptation, profile, budget)
            syntax_deaths += any(
                item["older_equivalent_programs"] and item["opponent_distinguishes_equivalent"]
                for item in details
            )
        before_payoffs = {tuple(value) for value in before["payoffs"]}
        after_payoffs = {tuple(value) for value in after["payoffs"]}
        payoff_deaths += len(before_payoffs - after_payoffs)
    return {
        "cooperative_deaths": cooperative_deaths,
        "payoff_deaths": payoff_deaths,
        "syntax_deaths": syntax_deaths,
    }


def canonical_boundary() -> dict[str, object]:
    catalog = V1.canonical_catalog()
    profile = (1, 1)
    output: dict[str, object] = {}
    for label, temptation in (("below", R - Fraction(1, 100)), ("at", R), ("above", R + Fraction(1, 100))):
        record = equilibrium_record(catalog, "pd_order", temptation, (1, 2, 3), 3)
        gaps = deviation_gaps(catalog, "pd_order", temptation, profile, (0, 1, 2))
        output[label] = {
            "temptation": str(temptation),
            "is_equilibrium": [1, 1] in record["profiles"],
            "margin": str(min(gaps)),
        }
    return output


def run_census() -> dict[str, object]:
    cells: dict[str, dict[str, object]] = {}
    total_cells = 0
    margin_checks = 0
    positive_margin_certificates = 0
    margin_exact = True
    padding_exact = True
    source_blind_syntax = 0
    extensional_syntax = 0
    for family in FAMILIES:
        for temptation in TEMPTATIONS:
            key = f"{family}|T={temptation}"
            aggregate = {
                "catalogs": 0,
                "catalogs_with_cooperative_death": 0,
                "catalogs_with_payoff_death": 0,
                "catalogs_with_syntax_death": 0,
                "extensional_catalogs_with_cooperative_death": 0,
            }
            for catalog in V1.catalogs():
                total_cells += 1
                aggregate["catalogs"] += 1
                transitions = transition_summary(catalog, family, temptation)
                aggregate["catalogs_with_cooperative_death"] += transitions["cooperative_deaths"] > 0
                aggregate["catalogs_with_payoff_death"] += transitions["payoff_deaths"] > 0
                aggregate["catalogs_with_syntax_death"] += transitions["syntax_deaths"] > 0
                if V1.extensional_on_duplicates(catalog):
                    aggregate["extensional_catalogs_with_cooperative_death"] += transitions["cooperative_deaths"] > 0
                    extensional_syntax += transitions["syntax_deaths"]
                if V1.source_blind(catalog):
                    source_blind_syntax += transitions["syntax_deaths"]
                for budget in (1, 2, 3):
                    primary = equilibrium_record(catalog, family, temptation, (1, 2, 3), budget)
                    padded = equilibrium_record(catalog, family, temptation, (3, 4, 5), budget + 2)
                    padding_exact = padding_exact and primary == padded
                    programs = admitted((1, 2, 3), budget)
                    for profile_list in primary["profiles"]:
                        if V1.actions(catalog, *profile_list) != (1, 1):
                            continue
                        gaps = deviation_gaps(catalog, family, temptation, tuple(profile_list), programs)
                        if not gaps:
                            continue
                        margin = min(gaps)
                        margin_checks += 1
                        margin_exact = margin_exact and all(gap >= 0 for gap in gaps)
                        if margin > 0:
                            epsilon = margin / 4
                            margin_exact = margin_exact and margin - 2 * epsilon > 0
                            positive_margin_certificates += 1
            cells[key] = aggregate

    def values(family: str, relation: str) -> list[int]:
        selected = []
        for temptation in TEMPTATIONS:
            if (relation == "low" and temptation <= R) or (relation == "high" and temptation > R):
                selected.append(cells[f"{family}|T={temptation}"]["catalogs_with_cooperative_death"])
        return selected

    phase_pass = all(all(value == 0 for value in values(family, "low")) for family in FAMILIES)
    phase_pass = phase_pass and all(
        len(set(values(family, "high"))) == 1 and values(family, "high")[0] > 0
        for family in FAMILIES
    )
    decomposition_pass = all(
        cells[f"{family}|T={temptation}"]["catalogs_with_syntax_death"] == 0
        for family in FAMILIES for temptation in TEMPTATIONS if temptation <= R
    )
    decomposition_pass = decomposition_pass and all(
        cells[f"{family}|T={temptation}"]["catalogs_with_syntax_death"] > 0
        and cells[f"{family}|T={temptation}"]["extensional_catalogs_with_cooperative_death"] > 0
        for family in FAMILIES for temptation in TEMPTATIONS if temptation > R
    )
    decomposition_pass = decomposition_pass and extensional_syntax == 0

    boundary = canonical_boundary()
    boundary_pass = (
        boundary["below"]["is_equilibrium"]
        and boundary["at"]["is_equilibrium"]
        and not boundary["above"]["is_equilibrium"]
        and boundary["at"]["margin"] == "0"
    )
    gates = {
        "U0_universe": total_cells == 8192 and all(cell["catalogs"] == 512 for cell in cells.values()),
        "F0_temptation_phase": phase_pass,
        "B0_boundary_liveness": boundary_pass,
        "E0_decomposition": decomposition_pass,
        "M0_margin_certificate": margin_exact and margin_checks > 0 and positive_margin_certificates > 0,
        "P0_encoding": padding_exact,
        "N0_source_blind": source_blind_syntax == 0,
    }
    verdict = (
        "equilibrium_survival_phase_established_for_registered_finite_class"
        if all(gates.values()) else "instrument_failed"
    )
    return {
        "schema_version": "asmp12_equilibrium_survival_result_v0_2",
        "verdict": verdict,
        "gates": gates,
        "cells": cells,
        "canonical_boundary": boundary,
        "margin_checks": margin_checks,
        "positive_margin_certificates": positive_margin_certificates,
        "claim_boundary": "Exact finite pure-equilibrium survival surface only; no ordinary bifiltration, mixed-equilibrium, proof-agent, or language-model claim.",
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
        "prior_art_addendum_sha256": ROOT.parent / "PRIOR_ART_ADDENDUM_v0_2.md",
        "scope_sha256": ROOT.parent / "PERSISTENCE_SUCCESSOR_SCOPE_v0_2.md",
        "v1_runner_sha256": V1_PATH,
        "protocol_sha256": ROOT / "PROTOCOL_v0_2.md",
        "runner_sha256": ROOT / "run_survival.py",
        "tests_sha256": ROOT / "test_survival.py",
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
        "schema_version": "asmp12_equilibrium_survival_receipt_v0_2",
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

