"""Run deterministic development checks for the ASMP-9 v0.56 theorem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import general_incomplete as gi


def build_result():
    result = {
        "affine_rank_checks": {},
        "claim_boundary": (
            "Development-only finite checks of an arbitrary-n theorem draft; "
            "not registered, not an arbitrary-n proof, and not an ASMP-9 "
            "resolution."
        ),
        "domain_checks": {},
        "schema": "asmp9-v0.56-development-result-v1",
        "status": "candidate_general_incomplete_menu_theorem_supported",
        "version": "0.56",
    }

    for n in (3, 4, 5):
        result["affine_rank_checks"][str(n)] = {
            "ambient_dimension": gi.ambient_dimension(n),
            "ranking_affine_rank": gi.random_utility_affine_rank(n),
        }

    for n in (3, 4):
        domains = list(gi.proper_domains(n))
        gaps = [gi.dimension_gap(n, domain) for domain in domains]
        source = gi.uniform_kernel(n)
        witness_failures = 0
        preservation_failures = 0
        for observed in domains:
            completion = gi.construct_nonrum_completion(n, observed, source)
            if not gi.regularity_violations(n, completion):
                witness_failures += 1
            if any(
                completion[(menu, choice)] != source[(menu, choice)]
                for menu in observed
                for choice in menu
            ):
                preservation_failures += 1
        result["domain_checks"][str(n)] = {
            "maximum_dimension_gap": max(gaps),
            "minimum_dimension_gap": min(gaps),
            "nonrum_witness_failures": witness_failures,
            "observed_data_preservation_failures": preservation_failures,
            "proper_domains": len(domains),
        }

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(build_result(), indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists() and args.output.read_text(encoding="utf-8") != payload:
            raise SystemExit(f"refusing to overwrite differing {args.output}")
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
