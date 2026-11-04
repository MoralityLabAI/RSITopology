from execute_confirmation_v0_42 import (
    canonical_bytes,
    resolve_status,
    sha256_bytes,
)


def _gates(value=True):
    return {
        name: value
        for name in (
            "P0",
            "S0",
            "U0",
            "H0",
            "C0",
            "A0",
            "D0",
            "R0",
            "RESOURCE",
        )
    }


def test_canonical_bytes_are_stable():
    payload = canonical_bytes({"b": 2, "a": 1})
    assert payload == b'{\n  "a": 1,\n  "b": 2\n}\n'
    assert sha256_bytes(payload) == (
        "080d51f49b27c73d17f51f3b808515a4"
        "25d16218aa40021eed2ca1d204e59224"
    )


def test_total_status_mapping_prioritizes_channel_event_and_containment():
    assert resolve_status(_gates()) == (
        "finite_sample_sequential_risk_access_"
        "confirmation_established"
    )
    channel = _gates()
    channel["H0"] = False
    assert resolve_status(channel) == (
        "not_established_by_registered_channel_event"
    )
    containment = _gates()
    containment["C0"] = False
    assert resolve_status(containment) == (
        "theorem_or_implementation_failure"
    )
    resource = _gates()
    resource["RESOURCE"] = False
    assert resolve_status(resource) == "registered_gate_failed"


def test_event_bound_arithmetic_forces_all_four_decisions():
    eta = 0.0035309243001648894
    assert 61 / 135 + 4 * eta < 0.499
    assert 13 / 25 - 4 * eta > 0.501
    assert 4 / 45 + (8 / 3) * eta < 0.099
