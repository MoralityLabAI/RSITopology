from __future__ import annotations

import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path

from conditional_fiber import (
    conditional_weights,
    enumerate_fibers,
    fiber_affine_rank,
    first_power_attainment,
    flat_null_state_mass,
    fraction_text,
    gauge_transform_odds,
    graph_cycle_rank,
    incidence_rows,
)


HERE = Path(__file__).resolve().parent


GRAPHS = {
    "cycle_3": (3, [(0, 1), (1, 2), (2, 0)]),
    "cycle_4": (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
    "theta_5": (
        4,
        [(0, 1), (1, 3), (0, 2), (2, 3), (0, 3)],
    ),
    "complete_4": (
        4,
        [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    ),
}


def encode_fraction(value: Fraction) -> dict[str, object]:
    numerator = value.numerator
    denominator = value.denominator

    def integer_bytes(integer: int) -> bytes:
        magnitude = abs(integer)
        payload = magnitude.to_bytes(
            max(1, (magnitude.bit_length() + 7) // 8), "big"
        )
        return (b"-" if integer < 0 else b"+") + payload

    encoded: dict[str, object] = {
        "decimal": float(value),
        "numerator_bit_length": abs(numerator).bit_length(),
        "denominator_bit_length": denominator.bit_length(),
        "numerator_sha256": hashlib.sha256(integer_bytes(numerator)).hexdigest(),
        "denominator_sha256": hashlib.sha256(
            integer_bytes(denominator)
        ).hexdigest(),
    }
    if max(abs(numerator).bit_length(), denominator.bit_length()) <= 512:
        encoded["fraction"] = fraction_text(value)
    return encoded


def liveness_census() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for graph_name, (node_count, edges) in GRAPHS.items():
        rows = incidence_rows(node_count, edges)
        beta1 = graph_cycle_rank(node_count, edges)
        for trials_per_edge in (1, 2, 3):
            trials = [trials_per_edge] * len(edges)
            fibers = enumerate_fibers(trials, rows)
            mass = flat_null_state_mass(fibers, trials)
            rank_counts: dict[int, int] = {}
            for fiber in fibers.values():
                rank = fiber_affine_rank(fiber)
                rank_counts[rank] = rank_counts.get(rank, 0) + 1

            nontrivial = next(
                (fiber for fiber in fibers.values() if len(fiber) > 1),
                None,
            )
            gauge_exact = False
            if nontrivial is not None:
                odds = tuple(
                    Fraction(index + 2, index + 1)
                    for index in range(len(edges))
                )
                primes = [2, 3, 5, 7]
                scales = tuple(Fraction(primes[v]) for v in range(node_count))
                transformed = gauge_transform_odds(odds, edges, scales)
                gauge_exact = conditional_weights(
                    nontrivial, trials, odds
                ) == conditional_weights(nontrivial, trials, transformed)

            records.append(
                {
                    "graph": graph_name,
                    "node_count": node_count,
                    "edge_count": len(edges),
                    "beta1": beta1,
                    "trials_per_edge": trials_per_edge,
                    "fiber_count": len(fibers),
                    "fiber_rank_counts": {
                        str(key): value for key, value in sorted(rank_counts.items())
                    },
                    "flat_null_rank_mass": {
                        str(key): encode_fraction(value)
                        for key, value in mass.items()
                    },
                    "full_quotient_mass": encode_fraction(
                        mass.get(beta1, Fraction(0, 1))
                    ),
                    "gauge_invariance_exact": gauge_exact,
                }
            )
    return records


def power_census() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    alpha = Fraction(1, 20)
    target = Fraction(4, 5)
    for odds_ratio in (Fraction(3, 2), Fraction(2), Fraction(3)):
        for cycle_length in (3, 4, 6, 8, 12):
            threshold = first_power_attainment(
                cycle_length,
                odds_ratio,
                alpha,
                target,
                maximum_trials=4096,
            )
            record: dict[str, object] = {
                "cycle_length": cycle_length,
                "odds_ratio": fraction_text(odds_ratio),
                "log_odds": __import__("math").log(float(odds_ratio)),
                "alpha": fraction_text(alpha),
                "target_power": fraction_text(target),
                "status": threshold["status"],
            }
            if threshold["status"] == "reached":
                exact = threshold["exact_test"]
                record.update(
                    {
                        "trials_per_edge": threshold["trials_per_edge"],
                        "boundary": exact["boundary"],
                        "randomization": encode_fraction(exact["randomization"]),
                        "exact_size": encode_fraction(exact["size"]),
                        "exact_power": encode_fraction(exact["power"]),
                        "previous_power": encode_fraction(
                            threshold["previous_power"]
                        ),
                        "scaled_first_attainment": (
                            threshold["trials_per_edge"]
                            / cycle_length
                            * __import__("math").log(float(odds_ratio)) ** 2
                        ),
                        "pre_attainment_power_decrease_count": threshold[
                            "pre_attainment_power_decrease_count"
                        ],
                    }
                )
            else:
                record.update(threshold)
            records.append(record)
    return records


def main() -> None:
    started = time.perf_counter()
    result = {
        "status": "development_only_burned",
        "claim_eligible": False,
        "liveness": liveness_census(),
        "conditional_power": power_census(),
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    output = HERE / "DEVELOPMENT_CENSUS_v0_13.json"
    output.write_text(payload, encoding="utf-8")
    receipt = {
        "elapsed_seconds": time.perf_counter() - started,
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "status": result["status"],
    }
    (HERE / "DEVELOPMENT_RECEIPT_v0_13.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
