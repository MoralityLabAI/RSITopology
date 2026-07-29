import json
from pathlib import Path

from run_registered import CONFIRMATION_GRID, gate_records


HERE = Path(__file__).resolve().parent


def passing_census() -> dict:
    return {
        "experiments": 4096,
        "decisions": {
            "cut_01_vs_2": [0, 0, 1],
            "cut_02_vs_1": [0, 1, 0],
            "cut_0_vs_12": [0, 1, 1],
            "identity": [0, 1, 2],
        },
        "grid": ["1/4", "1/3", "2/3", "3/4"],
        "sampled_transcript_oracle": {
            "classes_with_multiple_risk_profiles": 1,
            "maximum_within_quotient_risk_spread": "1/10",
        },
        "population_law_oracle": {
            "classes_with_multiple_risk_profiles": 1,
            "maximum_within_quotient_risk_spread": "1/12",
        },
        "anchors": {
            "blackwell_anchor": {
                "informative_to_uninformative": "0",
                "uninformative_to_informative": "1/4",
            },
            "risk_transfer": {
                "comparisons": 100,
                "violations": 0,
                "minimum_bound_minus_gap": "0",
            },
            "conservatism_witness": {
                "expanded_parameter_deficiency": "1/2",
                "maximum_registered_target_only_risk_gap": "0",
            },
        },
    }


def test_confirmation_grid_is_disjoint_from_burned_grid() -> None:
    burned = {"0", "1/2", "1"}
    assert {str(value) for value in CONFIRMATION_GRID}.isdisjoint(burned)
    assert len(CONFIRMATION_GRID) ** 6 == 4096


def test_protocol_matches_runner_universe() -> None:
    protocol = json.loads(
        (HERE / "PROTOCOL_v0_37.json").read_text(encoding="utf-8")
    )
    experiment_class = protocol["experiment_class"]
    assert experiment_class["experiments"] == 4096
    assert experiment_class["confirmation_probability_grid"] == [
        str(value) for value in CONFIRMATION_GRID
    ]
    assert protocol["status"] == "prospective_protocol_not_run"
    assert protocol["outcomes_consumed"] is False
    assert protocol["prior_art_disposition"] == (
        "subsumed_instrument_consolidation"
    )


def test_each_gate_has_a_live_failure_path() -> None:
    baseline = passing_census()
    assert all(
        row["decision"] == "pass" for row in gate_records(baseline)
    )
    mutations = {
        "E0": lambda row: row.update(experiments=4095),
        "B0": lambda row: row["anchors"]["blackwell_anchor"].update(
            uninformative_to_informative="0"
        ),
        "R0": lambda row: row["anchors"]["risk_transfer"].update(
            violations=1
        ),
        "S0": lambda row: row["sampled_transcript_oracle"].update(
            classes_with_multiple_risk_profiles=0
        ),
        "C0": lambda row: row["anchors"]["conservatism_witness"].update(
            expanded_parameter_deficiency="0"
        ),
    }
    for expected_gate, mutation in mutations.items():
        candidate = json.loads(json.dumps(baseline))
        mutation(candidate)
        decisions = {
            row["gate"]: row["decision"]
            for row in gate_records(candidate)
        }
        assert decisions[expected_gate] == "fail"


def test_no_theorem_novelty_claim_in_protocol() -> None:
    text = (HERE / "PROTOCOL_v0_37.json").read_text(encoding="utf-8")
    assert "classical" in text
    assert "new comparison theorem" in text
    assert "resolve ASMP-9" in text

