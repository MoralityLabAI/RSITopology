import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_protocol_binds_fresh_scenario_manifest() -> None:
    protocol = json.loads(
        (HERE / "protocol_v0_68.json").read_text(encoding="utf-8")
    )
    assert protocol["fresh_universe"]["scenario_manifest_sha256"] == _sha256(
        HERE / "scenario_manifest_v0_68.json"
    )
    assert protocol["fresh_universe"][
        "v067_construction_and_confirmation_excluded"
    ]


def test_all_endpoint_coefficients_annihilate_common_mode() -> None:
    protocol = json.loads(
        (HERE / "protocol_v0_68.json").read_text(encoding="utf-8")
    )
    assert all(
        sum(coefficients.values()) == 0
        for coefficients in protocol["endpoint_coefficients"].values()
    )


def test_scenario_boundary_uses_clustered_exact_randomization() -> None:
    protocol = json.loads(
        (HERE / "protocol_v0_68.json").read_text(encoding="utf-8")
    )
    thresholds = protocol["thresholds"]
    assert thresholds["required_scenario_successes"] == 10
    assert thresholds["scenario_trials"] == 12
    assert thresholds["randomization_universe"] == 4096
    assert thresholds["maximum_exact_randomization_p"] == 0.05


def test_decision_mapping_keeps_local_and_global_separate() -> None:
    protocol = json.loads(
        (HERE / "protocol_v0_68.json").read_text(encoding="utf-8")
    )
    mapping = protocol["decision_mapping"]
    assert (
        mapping["L0_pass_and_G0_fail"]
        == "local_response_family_established_context_conditioned"
    )
    assert (
        mapping["L0_pass_and_G0_pass"]
        == "local_response_family_established_shared_magnitude_compatible"
    )
