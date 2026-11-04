import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("run_frontier.py")
SPEC = importlib.util.spec_from_file_location("asmp12_frontier", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_canonical_cooperation_dies_by_syntax_exploit():
    catalog = MODULE.canonical_catalog()
    before = MODULE.equilibrium_record(catalog, "prisoners_dilemma", (1, 2, 3), 2)
    after = MODULE.equilibrium_record(catalog, "prisoners_dilemma", (1, 2, 3), 3)
    assert [1, 1] in before["cooperative_profiles"]
    assert [1, 1] not in after["profiles"]
    events = MODULE.transitions(catalog, "prisoners_dilemma")
    assert any(event.get("syntax_equivalence_exploited") for event in events)


def test_repaired_catalog_survives_duplicate_extension():
    catalog = MODULE.repaired_catalog()
    assert MODULE.extensional_on_duplicates(catalog)
    before = MODULE.equilibrium_record(catalog, "prisoners_dilemma", (1, 2, 3), 2)
    after = MODULE.equilibrium_record(catalog, "prisoners_dilemma", (1, 2, 3), 3)
    assert [1, 1] in before["cooperative_profiles"]
    assert [1, 1] in after["cooperative_profiles"]


def test_padding_shifts_budget_without_changing_record():
    catalog = MODULE.canonical_catalog()
    for game in MODULE.GAMES:
        for budget in (1, 2, 3):
            primary = MODULE.equilibrium_record(catalog, game, (1, 2, 3), budget)
            padded = MODULE.equilibrium_record(catalog, game, (3, 4, 5), budget + 2)
            assert primary == padded


def test_source_blind_catalog_has_no_syntax_exploit():
    catalog = ((0, 0, 0), (1, 1, 1), (0, 0, 0))
    assert MODULE.source_blind(catalog)
    assert all(
        not event.get("syntax_equivalence_exploited", False)
        for game in MODULE.GAMES
        for event in MODULE.transitions(catalog, game)
    )

