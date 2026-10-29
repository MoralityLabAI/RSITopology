from fractions import Fraction

from run import F, plant_step, quantifier_trap, safe, sensor_symbol, solve_universal


def fixture_protocol():
    return {
        "plant": {
            "initial_n": ["-1/4", "0", "1/4"],
            "initial_z": ["-1/4", "0", "1/4"],
            "disturbances": ["-1/32", "1/32"],
            "primary_a_n": "3/2",
        },
        "interface": {
            "ordered_sensor_thresholds": {"0": [], "1": ["0"], "2": ["-1/2", "0", "1/2"]},
            "action_dictionaries": {"0": ["0"], "1": ["-1/2", "1/2"], "2": ["-3/4", "-1/4", "1/4", "3/4"]},
        },
    }


def test_quantifier_trap_separates_per_cell_from_universal():
    result = quantifier_trap()
    assert result == {"per_cell_feasible": True, "universal_feasible": False, "pass": True}


def test_sensor_threshold_equality_enters_higher_bin():
    cuts = (F("-1/2"), F(0), F("1/2"))
    assert sensor_symbol((F(0), F(0)), a_n=F(1), coupling=F(0), cuts=cuts) == 2
    assert sensor_symbol((F("1/2"), F(0)), a_n=F(1), coupling=F(0), cuts=cuts) == 3


def test_symbol_relabel_is_exact_reversal():
    cuts = (F("-1/2"), F(0), F("1/2"))
    for q_value in map(F, ("-1", "-1/2", "-1/4", "0", "1/4", "1/2", "1")):
        raw = sensor_symbol((q_value, F(0)), a_n=F(1), coupling=F(0), cuts=cuts)
        relabeled = sensor_symbol((q_value, F(0)), a_n=F(1), coupling=F(0), cuts=cuts, relabel=True)
        assert raw + relabeled == len(cuts)


def test_plant_step_is_exact_and_safety_boundary_closed():
    result = plant_step(
        (F("1/4"), F("-1/4")),
        a_n=F("3/2"),
        a_z=F("6/5"),
        coupling=F("1/2"),
        action=F("-1/4"),
        disturbance=F("1/32"),
    )
    assert result == (F("1/32"), F("-3/10"))
    assert safe((F(1), F(999)))
    assert not safe((F("33/32"), F(0)))


def test_zero_horizon_is_vacuously_feasible_without_reading_outcomes():
    result = solve_universal(
        fixture_protocol(),
        horizon=0,
        a_n=F("3/2"),
        a_z=F("3/2"),
        coupling=F("1/2"),
        read_bits=0,
        write_bits=0,
    )
    assert result["feasible"] is True
    assert result["policy"] == []


def test_one_step_witness_replays_same_global_belief_not_per_initial_state():
    protocol = fixture_protocol()
    result = solve_universal(
        protocol,
        horizon=1,
        a_n=F("4/5"),
        a_z=F("3/2"),
        coupling=F(0),
        read_bits=0,
        write_bits=0,
    )
    assert result["feasible"] is True
    assert len(result["policy"]) == 1
    assert set(result["policy"][0]) == {"0"}


def test_fraction_constructor_avoids_binary_float_rounding():
    assert F("0.1") == Fraction(1, 10)
