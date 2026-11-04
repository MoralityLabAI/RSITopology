from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

from collusion_frontier import (
    ALPHABET_SIZE,
    AUDIT_CHARGE_GRID,
    COVER,
    COVERTNESS_REGIMES,
    DELTA_GRID,
    as_distribution,
    chi_squared,
    encoder_laws,
    exact_fraction,
    exact_frontier,
    mixture,
    registered_controls,
)


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PROTOCOL_v0_1.md"
REGISTRATION = ROOT / "registration_v0_1.json"
OUTPUT_DIR = ROOT / "artifacts_v0_1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def current_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def verify_registration() -> dict[str, object]:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    for relative, expected in registration["source_hashes"].items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise RuntimeError(f"registration mismatch for {relative}: {actual} != {expected}")
    return registration


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"write-once output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    registration = verify_registration()
    started = time.time()
    controls = registered_controls()
    cells = exact_frontier()

    rows = []
    for cell in cells:
        rows.append(
            {
                "covertness_regime": cell.covertness_regime,
                "delta": str(cell.delta),
                "audit_charge": cell.audit_charge,
                "minimax_error": str(cell.minimax_error),
                "minimax_error_float": float(cell.minimax_error),
                "eligible_code_count": cell.eligible_code_count,
                "optimal_code_count": cell.optimal_code_count,
                "optimal_code_hash_digest": hashlib.sha256(
                    "\n".join(cell.optimal_code_hashes).encode("ascii")
                ).hexdigest(),
            }
        )

    monotone = True
    for regime in COVERTNESS_REGIMES:
        for delta in DELTA_GRID:
            sequence = [
                cell.minimax_error
                for cell in cells
                if cell.covertness_regime == regime and cell.delta == delta
            ]
            monotone &= sequence == sorted(sequence)

    lookup = {
        (cell.covertness_regime, cell.delta, cell.audit_charge): cell.minimax_error
        for cell in cells
    }
    mixture_zero_live = lookup[("mixture", Fraction(0), 0)] == 0
    per_message_zero_dead = lookup[("per_message", Fraction(0), 0)] == Fraction(1, 2)
    full_charge_kill = all(
        lookup[(regime, delta, ALPHABET_SIZE)] == Fraction(1, 2)
        for regime in COVERTNESS_REGIMES
        for delta in DELTA_GRID
    )

    laws = encoder_laws()
    zero_mixture_codes = []
    both_chi_zero = True
    support_forward = 0
    support_reverse = 0
    for left in laws:
        p0 = as_distribution(left)
        for right in laws:
            p1 = as_distribution(right)
            stego = mixture(p0, p1)
            forward = chi_squared(COVER, stego)
            reverse = chi_squared(stego, COVER)
            support_forward += int(forward is not None)
            support_reverse += int(reverse is not None)
            if stego == COVER:
                zero_mixture_codes.append((left, right))
                both_chi_zero &= forward == 0 and reverse == 0

    gates = {
        "G0_registration_binding": all(
            sha256(ROOT / relative) == expected
            for relative, expected in registration["source_hashes"].items()
        ),
        "G1_complete_census": len(cells) == 40 and all(controls.values()),
        "G2_covertness_definition_separation": mixture_zero_live and per_message_zero_dead,
        "G3_full_audit_kill": full_charge_kill,
        "G4_audit_monotonicity": monotone,
        "G5_dual_chi_squared_support": both_chi_zero and support_reverse == 1225,
    }
    verdict = (
        "finite_registry_frontier_established"
        if all(gates.values())
        else "invalid_or_not_established"
    )

    csv_path = output / "frontier.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    result = {
        "schema_version": "asmp6_semantic_collusion_frontier_result_v0_1",
        "verdict": verdict,
        "claim_boundary": "Exact finite four-symbol registry only; no asymptotic capacity, learned collusion, or linguistic codebook claim.",
        "gates": gates,
        "counts": {
            "encoder_laws": len(laws),
            "ordered_codes": len(laws) ** 2,
            "audit_maps": ALPHABET_SIZE**ALPHABET_SIZE,
            "frontier_cells": len(cells),
            "zero_mixture_covertness_codes": len(zero_mixture_codes),
            "chi2_cover_given_stego_finite_codes": support_forward,
            "chi2_stego_given_cover_finite_codes": support_reverse,
        },
        "headline": {
            "mixture_zero_detectability_no_audit_error": exact_fraction(
                lookup[("mixture", Fraction(0), 0)]
            ),
            "per_message_zero_detectability_no_audit_error": exact_fraction(
                lookup[("per_message", Fraction(0), 0)]
            ),
            "full_charge_error": exact_fraction(Fraction(1, 2)),
        },
        "precision": "fractions.Fraction exact rational arithmetic",
    }
    result_path = output / "result.json"
    result_path.write_text(canonical_json(result), encoding="utf-8")

    receipt = {
        "schema_version": "asmp6_semantic_collusion_frontier_receipt_v0_1",
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(PROTOCOL),
        "source_commit": current_commit(),
        "elapsed_seconds": time.time() - started,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "outputs": {
            "frontier.csv": sha256(csv_path),
            "result.json": sha256(result_path),
        },
    }
    (output / "receipt.json").write_text(canonical_json(receipt), encoding="utf-8")
    print(canonical_json({"verdict": verdict, "gates": gates, "output": str(output)}), end="")
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
