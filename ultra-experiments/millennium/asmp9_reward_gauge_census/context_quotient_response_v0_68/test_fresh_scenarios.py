import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OLD_MANIFEST = (
    HERE.parent
    / "physical_dynamic_bridge_v0_67"
    / "scenario_manifest_v0_67.json"
)

SPEC = importlib.util.spec_from_file_location(
    "asmp9_fresh_scenarios_v068", HERE / "prepare_fresh_scenarios.py"
)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def _semantic_strings(row: dict) -> set[str]:
    return {
        row[field]
        for field in ("situation", "option_0", "option_1", "reason_0", "reason_1")
    }


def test_fresh_manifest_is_balanced_and_unique() -> None:
    manifest = module.build_manifest()
    rows = manifest["rows"]
    assert len(rows) == 24
    assert len({row["scenario_id"] for row in rows}) == 24
    families = {row["family"] for row in rows}
    assert len(families) == 12
    for family in families:
        family_rows = [row for row in rows if row["family"] == family]
        assert {row["split"] for row in family_rows} == {
            "construction",
            "confirmation",
        }
        assert len(family_rows) == 2


def test_no_v067_scenario_or_semantic_string_is_reused() -> None:
    old = json.loads(OLD_MANIFEST.read_text(encoding="utf-8"))
    new = module.build_manifest()
    old_ids = {row["scenario_id"] for row in old["rows"]}
    new_ids = {row["scenario_id"] for row in new["rows"]}
    assert old_ids.isdisjoint(new_ids)
    old_strings = set().union(*(_semantic_strings(row) for row in old["rows"]))
    new_strings = set().union(*(_semantic_strings(row) for row in new["rows"]))
    assert old_strings.isdisjoint(new_strings)


def test_options_and_reasons_are_nontrivial() -> None:
    for row in module.build_manifest()["rows"]:
        assert row["option_0"] != row["option_1"]
        assert row["reason_0"] != row["reason_1"]
        assert min(len(row["reason_0"]), len(row["reason_1"])) >= 40
