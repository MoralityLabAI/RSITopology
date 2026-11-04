import importlib.util
from fractions import Fraction
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("run_survival.py")
SPEC = importlib.util.spec_from_file_location("asmp12_survival", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_payoff_families_are_symmetric():
    for family in MODULE.FAMILIES:
        for temptation in MODULE.TEMPTATIONS:
            for actions in ((0, 0), (0, 1), (1, 0), (1, 1)):
                left, right = MODULE.utilities(family, temptation, actions)
                swapped = MODULE.utilities(family, temptation, actions[::-1])
                assert left == swapped[1]
                assert right == swapped[0]


def test_canonical_boundary_is_exact():
    boundary = MODULE.canonical_boundary()
    assert boundary["below"]["is_equilibrium"]
    assert boundary["at"]["is_equilibrium"]
    assert boundary["at"]["margin"] == "0"
    assert not boundary["above"]["is_equilibrium"]


def test_canonical_phase_changes_only_above_r():
    catalog = MODULE.V1.canonical_catalog()
    low = MODULE.transition_summary(catalog, "pd_order", Fraction(3))
    high = MODULE.transition_summary(catalog, "pd_order", Fraction(301, 100))
    assert low["cooperative_deaths"] == 0
    assert high["cooperative_deaths"] > 0
    assert high["syntax_deaths"] > 0


def test_padding_replay_on_boundary_catalog():
    catalog = MODULE.V1.canonical_catalog()
    for family in MODULE.FAMILIES:
        for temptation in (Fraction(2), Fraction(3), Fraction(4)):
            for budget in (1, 2, 3):
                primary = MODULE.equilibrium_record(catalog, family, temptation, (1, 2, 3), budget)
                padded = MODULE.equilibrium_record(catalog, family, temptation, (3, 4, 5), budget + 2)
                assert primary == padded

