from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("frontier", HERE / "frontier.py")
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def protocol():
    import json

    return json.loads((HERE / "protocol_v0_2.json").read_text(encoding="utf-8"))


def test_weak_composition_count_is_exact():
    assert len(list(MODULE.compositions(15, 5))) == 3876


def test_dual_coordinates_match_named_special_cases():
    p0 = (Fraction(1, 2), Fraction(1, 2))
    policy = (Fraction(3, 4), Fraction(1, 4))
    assert MODULE.dual_movement(policy, p0, "infinity") == Fraction(1, 2)
    assert MODULE.dual_movement(policy, p0, "2") == Fraction(1, 4)
    assert MODULE.dual_movement(policy, p0, "1") == Fraction(1, 2)


def test_sharpness_witnesses_attain_all_three_dual_bounds():
    p0 = (Fraction(1, 3),) * 3
    policy = (Fraction(2, 3), Fraction(1, 3), Fraction(0))
    epsilon = Fraction(1, 4)
    for q in ("infinity", "2", "1"):
        assert MODULE.sharpness_witness(policy, p0, epsilon, q)["pass"] is True


def test_near_tie_control_attains_two_epsilon():
    result = MODULE.near_tie_control(protocol())
    assert result["pass"] is True
    assert result["regret"] == "1/2"


def test_rare_tail_control_is_live():
    result = MODULE.rare_tail_control(protocol())
    assert result["pass"] is True
    assert Fraction(result["weighted_l2_error_squared"]) <= Fraction(result["error_ceiling_squared"])
    assert Fraction(result["true_gain"]) <= -Fraction(99, 100)


def test_full_census_passes_core_gates_and_finds_both_coordinate_witnesses():
    result, rows, witnesses = MODULE.run_census(protocol())
    assert result["policy_count"] == 3876
    assert rows
    assert all(gate["pass"] for gate in result["gates"].values())
    for q in ("infinity", "2", "1"):
        payload = witnesses["coordinate_minimality"][q]
        assert payload["equal_proxy_gain_unequal_movement"] is not None
        assert payload["equal_movement_unequal_proxy_gain"] is not None

