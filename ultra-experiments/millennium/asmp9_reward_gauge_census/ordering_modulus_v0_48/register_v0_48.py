"""Create the write-once ASMP-9 v0.48 preregistration."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

SEALED = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/coupled_uncertainty.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/sharp_atom_modulus.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/PRIOR_ART_GATE_v0_48.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/PROTOCOL_v0_48.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/THEOREM_DRAFT_v0_48.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/environment_lock_v0_48.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/ordering_modulus.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/test_ordering_modulus.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/run_confirmation_v0_48.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/verify_result_v0_48.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "ordering_modulus_v0_48/build_release_v0_48.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    for relative in SEALED:
        path = REPO / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        if tracked.returncode:
            raise RuntimeError(f"sealed file is not tracked: {relative}")
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=REPO,
        )
        if dirty.returncode:
            raise RuntimeError(
                f"sealed file differs from implementation commit: {relative}"
            )

    payload = {
        "protocol_id": "asmp9-decision-dependent-ordering-v0.48",
        "version": "0.48",
        "status": "registered_before_confirmation",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "implementation_commit": git("rev-parse", "HEAD"),
        "expected_status": (
            "decision_dependent_evidence_ordering_established"
        ),
        "expected_test_count": 13,
        "test_command": (
            "python -m pytest -q ultra-experiments/millennium/"
            "asmp9_reward_gauge_census/ordering_modulus_v0_48/"
            "test_ordering_modulus.py"
        ),
        "frozen_universe": {
            "targets": 4,
            "queries": ["root", "left", "right"],
            "horizon": 2,
            "symbolic_policy_count": 3748,
            "allocation": [2, 1, 1],
            "outcome_count": 12,
            "implicit_order_count": 479001600,
            "alpha": "1/10",
            "levels": ["0", "3/20", "7/20"],
            "parameter_count": 27,
            "reference_law": (
                "uniform mixture over registered parameter laws"
            ),
            "confidence_class": (
                "deterministic nondecreasing Buehler direct bounds"
            ),
        },
        "frozen_predictions": {
            "common_optimizer_count": 0,
            "classification_cross_regret_strictly_positive": True,
            "root_cross_regret_strictly_positive": True,
            "minimum_coverage": "9/10",
            "all_zero_singleton_matches_atom_modulus": True,
            "bound_tables_nonconstant": True,
        },
        "burned_replay": {
            "levels": ["0", "1/5", "2/5"],
            "allocation": [1, 1, 1],
            "alpha": "1/10",
            "classification_optimum": "1984/3125",
            "classification_optimizer_count": 5040,
            "root_optimum": "246/625",
            "root_optimizer_count": 5040,
            "common_optimizer_count": 0,
            "classification_cross_regret": "4/3125",
            "root_cross_regret": "2/625",
            "development_sha256": (
                "cd57bfc889d8bdcdc46a33dbe11b1af7faf1ff45"
                "03091d8f9a6bd83efd19efa2"
            ),
            "claim_eligible": False,
        },
        "resource_ceiling": {
            "seconds": 180,
            "peak_aggregate_working_set_bytes": 1073741824,
            "worker_processes": 4,
        },
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SEALED
        },
        "claim_boundary": (
            "One finite shared-BSC calibration experiment, uniform "
            "parameter-mixture objective, deterministic nondecreasing "
            "Buehler bounds, and two exact finite decision risks. Not a "
            "universal no-statistic theorem, reference-law optimization, "
            "randomized-confidence result, real preference-channel "
            "validation, or ASMP-9 resolution."
        ),
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output = HERE / "registration_v0_48.json"
    if output.exists():
        if output.read_bytes() != encoded:
            raise RuntimeError("write-once registration mismatch")
    else:
        output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "path": output.relative_to(REPO).as_posix(),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "implementation_commit": payload[
                    "implementation_commit"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
