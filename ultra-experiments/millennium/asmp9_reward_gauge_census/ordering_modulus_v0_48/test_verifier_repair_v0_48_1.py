from verify_result_v0_48_1 import adjudication_valid, instrument_valid


INSTRUMENT = {
    "P0": True,
    "S0": True,
    "U0": True,
    "E0": True,
    "D0": True,
    "L0": True,
    "C0": True,
    "A0": True,
    "RESOURCE": True,
}


def test_positive_prediction_is_valid_when_status_matches():
    gates = {**INSTRUMENT, "X0": True}
    result = {
        "gates": gates,
        "status": "decision_dependent_evidence_ordering_established",
    }
    assert instrument_valid(gates)
    assert adjudication_valid(result)


def test_registered_null_is_valid_when_status_matches():
    gates = {**INSTRUMENT, "X0": False}
    result = {
        "gates": gates,
        "status": "decision_dependent_ordering_not_established",
    }
    assert instrument_valid(gates)
    assert adjudication_valid(result)


def test_instrument_failure_is_not_accepted_as_valid_result():
    gates = {**INSTRUMENT, "X0": False, "C0": False}
    result = {"gates": gates, "status": "invalid_ordering_instrument"}
    assert not instrument_valid(gates)
    assert not adjudication_valid(result)


def test_resource_failure_is_an_instrument_failure():
    gates = {**INSTRUMENT, "X0": False, "RESOURCE": False}
    result = {
        "gates": gates,
        "status": "decision_dependent_ordering_not_established",
    }
    assert not instrument_valid(gates)
    assert not adjudication_valid(result)


def test_status_mismatch_is_rejected():
    gates = {**INSTRUMENT, "X0": False}
    result = {
        "gates": gates,
        "status": "decision_dependent_evidence_ordering_established",
    }
    assert instrument_valid(gates)
    assert not adjudication_valid(result)
