"""Write-once prospective registration for ASMP-9 v0.61."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = HERE / "verification_registration_v0_61.json"
RESULT = HERE / "VERIFY_RESULT_v0_61.json"
PREFIX = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "structured_choice_stack_v0_61/"
)

NEW_SOURCE_FILES = tuple(
    PREFIX + name
    for name in (
        "PRIOR_ART_GATE_v0_61.md",
        "PROOF_AUDIT_v0_61.md",
        "README.md",
        "VERIFICATION_PROTOCOL_v0_61.md",
        "independent_replay_v0_61.py",
        "register_verification_v0_61.py",
        "stack_verifier_v0_61.py",
        "test_stack_verifier_v0_61.py",
        "verification_cells_v0_61.json",
        "verify_stack_v0_61.py",
    )
)

BURNED_FILES = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "general_incomplete_menu_v0_56/RESULT_v0_56.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "general_incomplete_menu_v0_56/THEOREM_DRAFT_v0_56.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "general_incomplete_menu_v0_56/VERIFY_RESULT_v0_56.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "bounded_context_degree_v0_57/PRIOR_ART_GATE_v0_57.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "bounded_context_degree_v0_57/THEOREM_DRAFT_v0_57.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "bounded_context_degree_v0_57/bounded_context_degree.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "finite_sample_tiers_v0_58/PRIOR_ART_GATE_v0_58.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "finite_sample_tiers_v0_58/THEOREM_DRAFT_v0_58.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "finite_sample_tiers_v0_58/finite_sample_tiers.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "contamination_radius_v0_59/PRIOR_ART_GATE_v0_59.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "contamination_radius_v0_59/THEOREM_DRAFT_v0_59.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "contamination_radius_v0_59/contamination_radius.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "selection_channel_v0_60/PRIOR_ART_GATE_v0_60.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "selection_channel_v0_60/THEOREM_DRAFT_v0_60.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "selection_channel_v0_60/selection_channel.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("cannot register after a verification result exists")
    cells = json.loads((HERE / "verification_cells_v0_61.json").read_text())
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        text=True,
    ).strip()
    registration = {
        "burned_inputs_sha256": {
            relative: sha256(REPO / relative) for relative in BURNED_FILES
        },
        "claim_boundary": (
            "Conditional finite stochastic-choice access ledger: bounded "
            "context-degree reconstruction, margin-promised sampling, fixed "
            "Huber contamination, and recorded pre-response versus "
            "outcome-dependent selection. Classical/elementary ingredients; "
            "no empirical-premise, efficient-general-modulus, hidden-menu, "
            "latent-confounding, strategic/nonstationary, welfare, novelty, "
            "or full ASMP-9 resolution claim."
        ),
        "expected_test_count": 6,
        "freshness": {
            "burned_v57_maximum_n": 8,
            "verification_v57_minimum_n": min(
                int(cell["n"]) for cell in cells["v57_cells"]
            ),
        },
        "protocol_id": cells["protocol_id"],
        "resource_caps": cells["resource_caps"],
        "schema": "asmp9-v0.61-verification-registration-v1",
        "source_commit": commit,
        "source_sha256": {
            relative: sha256(REPO / relative) for relative in NEW_SOURCE_FILES
        },
        "test_command": (
            "python -m pytest -q -p no:cacheprovider "
            + PREFIX
            + "test_stack_verifier_v0_61.py"
        ),
        "verification_command": "python " + PREFIX + "verify_stack_v0_61.py",
    }
    encoded = (json.dumps(registration, indent=2, sort_keys=True) + "\n").encode()
    if OUTPUT.exists():
        if OUTPUT.read_bytes() != encoded:
            raise FileExistsError("registration exists with different bytes")
    else:
        OUTPUT.write_bytes(encoded)
    print(sha256(OUTPUT))


if __name__ == "__main__":
    main()

