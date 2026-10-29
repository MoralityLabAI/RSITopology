from __future__ import annotations

import hashlib
import json
from pathlib import Path

from joint_linear_quotient import (
    analyze_joint_quotient,
    canonical_fixtures,
    stability_certificate,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_69.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    fixtures: dict[str, object] = {}
    for name, matrices in canonical_fixtures().items():
        analysis = analyze_joint_quotient(*matrices)
        fixtures[name] = {
            "exact": analysis.to_jsonable(),
            "stability": stability_certificate(*matrices),
        }

    payload = {
        "status": "development_only_not_preregistered",
        "theorem_object": (
            "finite-dimensional representative-insensitive linear quotient"
        ),
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
        "checks": {
            "full_common_mode_identifies": fixtures["full_common_mode"][
                "exact"
            ]["exactly_identifies_reward_quotient"],
            "partial_common_mode_fails": not fixtures[
                "partial_common_mode"
            ]["exact"]["exactly_identifies_reward_quotient"],
            "visible_gauge_is_detected": fixtures[
                "gauge_leaking_but_complete"
            ]["exact"]["visible_gauge_rank"] == 1,
            "forced_quotient_can_still_identify": fixtures[
                "gauge_leaking_but_complete"
            ]["exact"]["exactly_identifies_reward_quotient"],
            "non_gauge_confounder_is_exhibited": fixtures[
                "non_gauge_confounded"
            ]["exact"]["non_gauge_witness"] is not None,
        },
        "claim_boundary": (
            "Exact finite linear-algebra consolidation. No behavioral model, "
            "physical reward gauge, nonlinear channel, finite-sample minimax "
            "rate, human-value claim, or ASMP-9 resolution is established."
        ),
        "source_hashes": {
            "joint_linear_quotient.py": sha256(
                ROOT / "joint_linear_quotient.py"
            ),
            "test_joint_linear_quotient.py": sha256(
                ROOT / "test_joint_linear_quotient.py"
            ),
            "THEOREM_DRAFT_v0_69.md": sha256(
                ROOT / "THEOREM_DRAFT_v0_69.md"
            ),
            "PRIOR_ART_GATE_v0_69.md": sha256(
                ROOT / "PRIOR_ART_GATE_v0_69.md"
            ),
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["checks"], sort_keys=True))


if __name__ == "__main__":
    main()
