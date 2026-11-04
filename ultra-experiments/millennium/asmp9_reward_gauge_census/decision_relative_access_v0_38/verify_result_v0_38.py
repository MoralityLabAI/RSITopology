"""Post-result verifier for ASMP-9 decision-relative access v0.38."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as Q
from pathlib import Path

from confirmation import run_confirmation
from execute_confirmation import (
    BASE,
    canonical_bytes,
    sha256_bytes,
    sha256_file,
    validate_registration,
)


def verify(
    registration_path: Path,
    result_path: Path,
    replay: bool,
) -> dict:
    registration = validate_registration(registration_path)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    claimed_content_hash = result["result_content_sha256"]
    unhashed = dict(result)
    del unhashed["result_content_sha256"]
    observed_content_hash = sha256_bytes(canonical_bytes(unhashed))
    if observed_content_hash != claimed_content_hash:
        raise ValueError("result content hash mismatch")
    if result["registration_file_sha256"] != sha256_file(registration_path):
        raise ValueError("result points to the wrong registration bytes")

    expected_cells = {
        (high, low, nuisance)
        for high, low in registration["confirmation_grid"]["strengths"]
        for nuisance in registration["confirmation_grid"][
            "nuisance_one_probabilities"
        ]
    }
    observed_cells = set()
    analytic_checks = []
    for row in result["rows"]:
        cell = (
            row["high"],
            row["low"],
            row["nuisance_one_probability"],
        )
        if cell in observed_cells:
            raise ValueError(f"duplicate result cell: {cell}")
        observed_cells.add(cell)
        high, low = Q(row["high"]), Q(row["low"])
        gap = high - low
        half_gap = gap / 2
        checks = {
            "gap": Q(row["gap"]) == gap,
            "half_gap": Q(row["half_gap"]) == half_gap,
            "q0_deletion": Q(row["q0_relative_deficiency"]) == half_gap,
            "q1_deletion": Q(row["q1_relative_deficiency"]) == half_gap,
            "target_pair_zero": Q(
                row["target_pair_relative_deficiency"]
            )
            == 0,
            "append_ancillary_zero": Q(
                row["append_ancillary_deficiency"]
            )
            == 0,
            "drop_ancillary_zero": Q(
                row["drop_ancillary_deficiency"]
            )
            == 0,
            "gauge_equals_empty": Q(
                row["gauge_relative_deficiency"]
            )
            == Q(row["empty_relative_deficiency"]),
            "expanded_missing_gauge": Q(
                row["expanded_missing_gauge_deficiency"]
            )
            == Q(1, 2),
            "boundary_nonvacuous": Q(
                row["empty_relative_deficiency"]
            )
            > half_gap,
            "value_gap_strictly_coarser_q0": Q(
                row["q0_value_gap"]
            )
            < Q(row["q0_relative_deficiency"]),
            "value_gap_strictly_coarser_q1": Q(
                row["q1_value_gap"]
            )
            < Q(row["q1_relative_deficiency"]),
        }
        # This closed form was noticed after reveal and is descriptive until a
        # separately registered confirmation. It is not used as a v0.38 gate.
        if high + low == 1:
            checks["posthoc_empty_formula"] = Q(
                row["empty_relative_deficiency"]
            ) == half_gap + gap * gap / 6
        if not all(checks.values()):
            raise ValueError(f"analytic check failed for {cell}: {checks}")
        analytic_checks.append({"cell": list(cell), "checks": checks})
    if observed_cells != expected_cells:
        raise ValueError("result cell universe differs from registration")
    if not all(result["gates"].values()):
        raise ValueError("one or more registered gates did not pass")
    if result["status"] != (
        "finite_decision_relative_access_threshold_established"
    ):
        raise ValueError("unexpected result status")

    replay_match = None
    if replay:
        replay_result = run_confirmation()
        replay_match = (
            replay_result["rows"] == result["rows"]
            and replay_result["gates"]
            == {
                key: result["gates"][key]
                for key in replay_result["gates"]
            }
        )
        if not replay_match:
            raise ValueError("exact replay differs from sealed result")

    return {
        "status": "verified",
        "registration_file_sha256": sha256_file(registration_path),
        "result_file_sha256": sha256_file(result_path),
        "result_content_sha256": claimed_content_hash,
        "sealed_files_checked": len(registration["sealed_files"]),
        "registered_cells_checked": len(observed_cells),
        "analytic_checks": analytic_checks,
        "exact_replay_requested": replay,
        "exact_replay_match": replay_match,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=BASE / "registration_v0_38.json",
    )
    parser.add_argument(
        "--result",
        type=Path,
        default=BASE / "artifacts_v0_38" / "RESULT_v0_38.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "artifacts_v0_38" / "VERIFY_v0_38.json",
    )
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    verification = verify(
        args.registration.resolve(),
        args.result.resolve(),
        args.replay,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(canonical_bytes(verification))
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

