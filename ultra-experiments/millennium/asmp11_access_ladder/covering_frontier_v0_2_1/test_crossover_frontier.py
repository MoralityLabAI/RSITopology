from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path

import build_registration
import crossover_frontier as primary
import pytest
import release_contract
import run
import synthesize_receipt
import verify_result as independent


ROOT = Path(__file__).resolve().parent


def test_full_draft_grid_has_48_covering_cells() -> None:
    count = sum(
        len(primary.intermediate_widths(n, k)) for n in (13, 15, 17) for k in (3, 4)
    )
    assert count == 48
    assert primary.intermediate_widths(13, 3) == (4, 5, 6, 7, 8, 9)
    assert primary.intermediate_widths(13, 4) == (5, 6, 7, 8, 9, 10)


def test_deterministic_incumbent_and_replayable_bounds() -> None:
    first = primary.deterministic_cover_bounds(
        7,
        4,
        3,
        max_greedy_rounds=100,
        max_candidate_blocks=1000,
    )
    second = primary.deterministic_cover_bounds(
        7,
        4,
        3,
        max_greedy_rounds=100,
        max_candidate_blocks=1000,
    )
    assert first == second
    assert primary.verify_cover(7, 4, 3, first.selected_blocks)
    replay = primary.replayable_lower_bound(7, 4, 3)
    assert first.lower_bound == replay["certified_lower_bound"]
    assert first.lower_bound <= first.upper_bound


def test_resource_stop_keeps_valid_incumbent_and_does_not_claim_optimum() -> None:
    stopped = primary.deterministic_cover_bounds(
        6,
        3,
        2,
        max_greedy_rounds=0,
        max_candidate_blocks=1000,
    )
    assert stopped.stop_reason == "deterministic_round_cap"
    assert stopped.construction_status == "bounded_stop_with_trivial_incumbent"
    assert stopped.upper_bound == comb(6, 3)
    assert primary.verify_cover(6, 3, 2, stopped.selected_blocks)
    assert not stopped.optimum_certified
    assert stopped.lower_bound < stopped.upper_bound


def test_exact_probability_reproduces_sealed_v02_costs() -> None:
    cases = (
        (4, Fraction(1, 20), 60),
        (5, Fraction(1, 4), 285),
        (comb(13, 3), Fraction(1, 20), 6292),
    )
    for query_count, flip_rate, expected_total in cases:
        design = primary.find_exact_design(
            query_count,
            flip_rate,
            Fraction(1, 20),
            Fraction(9, 10),
            4096,
        )
        assert design is not None
        assert design.total_samples == expected_total
        assert design.familywise_error_upper <= Fraction(1, 20)
        assert design.signal_power_lower >= Fraction(9, 10)


def test_all_three_bound_aware_classifications_are_live() -> None:
    args = (
        10,
        Fraction(1, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    certified = primary.classify_cost_interval(1, 1, *args)
    impossible = primary.classify_cost_interval(10, 10, *args)
    unresolved = primary.classify_cost_interval(1, 10, *args)
    assert certified.status == primary.STATUS_CERTIFIED
    assert impossible.status == primary.STATUS_IMPOSSIBLE
    assert unresolved.status == primary.STATUS_UNRESOLVED


def test_minimum_width_uses_interval_when_any_smaller_cell_is_unresolved() -> None:
    bracket = primary.build_minimum_width_bracket(
        3,
        (
            {"block_size": 4, "status": primary.STATUS_IMPOSSIBLE},
            {"block_size": 5, "status": primary.STATUS_UNRESOLVED},
            {"block_size": 6, "status": primary.STATUS_CERTIFIED},
        ),
        7,
    )
    assert bracket["s_no"] == 4
    assert bracket["s_yes"] == 6
    assert bracket["s_star"] is None
    assert bracket["unresolved_widths"] == [5]
    assert bracket["interval"] == "(4,6]"

    exact = primary.build_minimum_width_bracket(
        3,
        tuple(
            {"block_size": width, "status": primary.STATUS_IMPOSSIBLE}
            for width in (4, 5, 6)
        ),
        7,
    )
    assert exact["s_star"] == 7
    assert exact["interval"] is None

    reverse_order = (
        {"block_size": 4, "status": primary.STATUS_UNRESOLVED},
        {"block_size": 5, "status": primary.STATUS_IMPOSSIBLE},
        {"block_size": 6, "status": primary.STATUS_CERTIFIED},
    )
    honest = primary.build_minimum_width_bracket(3, reverse_order, 7)
    assert honest["s_no"] == 3
    assert honest["s_yes"] == 6
    assert honest["interval"] == "(3,6]"
    independently_honest = independent.independent_bracket(
        3,
        [
            {
                "block_size": row["block_size"],
                "primary": {"status": row["status"]},
            }
            for row in reverse_order
        ],
        7,
    )
    assert independently_honest == honest


def test_bracket_hardening_preserves_v0_2_1_1_registered_grid() -> None:
    costs = [
        json.loads(line)
        for line in (ROOT / "artifacts_v0_2_1_1/cost_cells.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    prior_result = json.loads(
        (ROOT / "artifacts_v0_2_1_1/result_layer.json").read_text(encoding="utf-8")
    )
    grouped: dict[tuple[int, int, str], list[dict[str, object]]] = {}
    for row in costs:
        key = (int(row["n"]), int(row["k"]), str(Fraction(row["flip_rate"])))
        grouped.setdefault(key, []).append(
            {
                "block_size": row["block_size"],
                "status": row["primary"]["status"],
            }
        )
    prior = {
        (int(row["n"]), int(row["k"]), str(Fraction(row["flip_rate"]))): row
        for row in prior_result["brackets"]
    }
    assert len(grouped) == len(prior) == 18
    for key, rows in grouped.items():
        n, k, _ = key
        replayed = primary.build_minimum_width_bracket(
            k, rows, primary.high_width_anchor(n, k)
        )
        assert replayed == {field: prior[key][field] for field in replayed}


def test_one_diagnostic_and_four_probes_are_nonbinding_and_independently_replay() -> (
    None
):
    primary_result = primary.classify_cost_interval(
        2,
        5,
        30,
        Fraction(3, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    probes = primary.metric_robustness_probes(
        primary_result,
        30,
        Fraction(3, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    assert len(probes) == 5
    assert all(probe["binding"] is False for probe in probes)
    independent_statuses = independent.independent_probe_statuses(
        2,
        5,
        30,
        Fraction(3, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    assert {
        probe["probe_id"]: probe["status"] for probe in probes
    } == independent_statuses


def test_independent_cover_lower_bound_and_probability_implementations_agree() -> None:
    cover = primary.deterministic_cover_bounds(
        8,
        5,
        3,
        max_greedy_rounds=100,
        max_candidate_blocks=1000,
    )
    assert independent.independent_verify_cover(8, 5, 3, cover.selected_blocks)
    independent_lower = independent.independent_lower_bounds(8, 5, 3)
    assert independent_lower["certified"] == cover.lower_bound
    independent_design = independent.independent_design(
        4,
        Fraction(1, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    assert independent_design is not None
    assert independent_design["total_samples"] == 60


def test_manifest_anchor_and_future_registration_source_set_are_complete() -> None:
    manifest = json.loads((ROOT / "experiment_v0_2_1.json").read_text(encoding="utf-8"))
    assert manifest["asmp11"]["release_id"] == release_contract.RELEASE_ID
    assert manifest["asmp11"]["status"] == "registration_required_before_execution"
    assert manifest["asmp11"]["expected_counts"] == {
        "covering_cells": 48,
        "cost_cells": 144,
        "brackets": 18,
        "metric_records_per_cost_cell": 5,
        "robustness_probes_per_cost_cell": 4,
    }
    _, checks = run.validate_prior_anchor(ROOT / "prior_anchor_v0_2.json")
    assert all(row["pass"] for row in checks)
    assert all(
        (ROOT / relative).is_file() for relative in build_registration.BOUND_SOURCES
    )


def test_all_hash_bound_text_writers_emit_lf_bytes(tmp_path: Path) -> None:
    payload = '{\n  "alpha": 1,\n  "beta": 2\n}\n'
    for index, writer in enumerate(
        (
            run.write_lf_text,
            build_registration.write_lf_text,
            independent.write_lf_text,
            synthesize_receipt.write_lf_text,
        )
    ):
        output = tmp_path / f"writer_{index}.json"
        writer(output, payload)
        emitted = output.read_bytes()
        assert emitted == payload.encode("utf-8")
        assert b"\r\n" not in emitted
        assert emitted.endswith(b"\n")


def test_atomic_json_and_jsonl_emit_lf_bytes(tmp_path: Path) -> None:
    json_path = tmp_path / "atomic.json"
    jsonl_path = tmp_path / "rows.jsonl"
    run.atomic_json(json_path, {"nested": {"value": 1}, "rows": [1, 2]})
    run.write_jsonl(jsonl_path, ({"row": 1}, {"row": 2}))
    for output in (json_path, jsonl_path):
        emitted = output.read_bytes()
        assert b"\r\n" not in emitted
        assert emitted.endswith(b"\n")


@pytest.mark.parametrize(
    "payload",
    ('{"duplicate":1,"duplicate":2}\n', '{"nonfinite":NaN}\n'),
)
def test_all_evidence_json_loaders_reject_noncanonical_json(
    tmp_path: Path, payload: str
) -> None:
    path = tmp_path / "mutant.json"
    path.write_text(payload, encoding="utf-8")
    for loader in (
        run.load_json,
        build_registration.load_json,
        independent.load_json,
        synthesize_receipt.load_json,
    ):
        with pytest.raises(ValueError):
            loader(path)
    with pytest.raises(ValueError):
        independent.read_jsonl(path)


def _registration_payload() -> dict[str, object]:
    manifest = json.loads((ROOT / "experiment_v0_2_1.json").read_text(encoding="utf-8"))
    hashes = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in release_contract.BOUND_SOURCES
    }
    return {
        "schema_version": release_contract.REGISTRATION_SCHEMA,
        "release_id": release_contract.RELEASE_ID,
        "protocol_id": release_contract.MATHEMATICAL_PROTOCOL_ID,
        "registered_at_utc": "2026-08-03T00:00:00+00:00",
        "status": "prospective_registration_before_claim_grid_execution",
        "proposed_asmp_id": "ASMP-11",
        "source_commit": "a" * 40,
        "source_hashes": hashes,
        "source_git_blob_oids": {
            name: "b" * 40 for name in release_contract.BOUND_SOURCES
        },
        "manifest_path": "experiment_v0_2_1.json",
        "manifest_sha256": hashes["experiment_v0_2_1.json"],
        "prior_anchor_path": "prior_anchor_v0_2.json",
        "prior_anchor_sha256": hashes["prior_anchor_v0_2.json"],
        "claim_grid": manifest["asmp11"],
        "claim_boundary": release_contract.CLAIM_BOUNDARY,
        "output_policy": "write_once_non_aliasing",
    }


def _patch_registration_git(monkeypatch: pytest.MonkeyPatch) -> None:
    def full_commit(reference: str) -> str:
        if len(reference) != 40:
            raise RuntimeError("abbreviated commit")
        return reference

    monkeypatch.setattr(run, "_full_commit", full_commit)
    monkeypatch.setattr(
        run, "_committed_bytes", lambda _commit, path: path.read_bytes()
    )
    monkeypatch.setattr(run, "_git_blob_oid", lambda _commit, _path: "b" * 40)
    monkeypatch.setattr(run, "_registration_commit", lambda _path, _commit: "c" * 40)


def _write_registration(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def test_registration_requires_exact_source_and_blob_sets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_registration_git(monkeypatch)
    path = tmp_path / "registration.json"
    valid = _registration_payload()
    _write_registration(path, valid)
    assert (
        run.validate_registration(path, require_committed_registration=False)[
            "release_id"
        ]
        == release_contract.RELEASE_ID
    )

    mutations = []
    empty_sources = copy.deepcopy(valid)
    empty_sources["source_hashes"] = {}
    mutations.append(empty_sources)
    extra_blob = copy.deepcopy(valid)
    extra_blob["source_git_blob_oids"]["unregistered.py"] = "b" * 40  # type: ignore[index]
    mutations.append(extra_blob)
    abbreviated = copy.deepcopy(valid)
    abbreviated["source_commit"] = "a" * 7
    mutations.append(abbreviated)
    wrong_blob = copy.deepcopy(valid)
    wrong_blob["source_git_blob_oids"]["run.py"] = "d" * 40  # type: ignore[index]
    mutations.append(wrong_blob)
    aliased_manifest_name = copy.deepcopy(valid)
    aliased_manifest_name["manifest_path"] = "subdir/../experiment_v0_2_1.json"
    mutations.append(aliased_manifest_name)
    changed_grid = copy.deepcopy(valid)
    changed_grid["claim_grid"]["flip_rates"] = ["1/20", "2/20", "1/4"]  # type: ignore[index]
    mutations.append(changed_grid)
    for mutation in mutations:
        _write_registration(path, mutation)
        with pytest.raises((RuntimeError, KeyError)):
            run.validate_registration(path, require_committed_registration=False)


def test_registration_rejects_manifest_and_anchor_aliases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_registration_git(monkeypatch)
    path = tmp_path / "registration.json"
    _write_registration(path, _registration_payload())
    manifest_alias = tmp_path / "manifest.json"
    anchor_alias = tmp_path / "anchor.json"
    manifest_alias.write_bytes((ROOT / "experiment_v0_2_1.json").read_bytes())
    anchor_alias.write_bytes((ROOT / "prior_anchor_v0_2.json").read_bytes())
    with pytest.raises(RuntimeError):
        run.validate_registration(
            path,
            manifest_alias,
            ROOT / "prior_anchor_v0_2.json",
            require_committed_registration=False,
        )
    with pytest.raises(RuntimeError):
        run.validate_registration(
            path,
            ROOT / "experiment_v0_2_1.json",
            anchor_alias,
            require_committed_registration=False,
        )


def test_registration_history_lookup_is_repo_root_anchored() -> None:
    prior_registration = ROOT / "registration_v0_2_1_1.json"
    payload = json.loads(prior_registration.read_text(encoding="utf-8"))
    source_commit = run._full_commit(payload["source_commit"])
    registration_commit = run._registration_commit(prior_registration, source_commit)
    assert registration_commit is not None
    assert len(registration_commit) == 40


def test_exact_cartesian_counters_reject_count_preserving_substitution() -> None:
    config = json.loads((ROOT / "experiment_v0_2_1.json").read_text(encoding="utf-8"))[
        "asmp11"
    ]
    covers = [
        {"n": n, "k": k, "block_size": block_size}
        for n, k, block_size in run.expected_cover_counter(config)
    ]
    costs = [
        {"n": n, "k": k, "block_size": block_size, "flip_rate": rate}
        for n, k, block_size, rate in run.expected_cost_counter(config)
    ]
    brackets = [
        {"n": n, "k": k, "flip_rate": rate}
        for n, k, rate in run.expected_bracket_counter(config)
    ]
    assert all(run.exact_grid_counters(config, covers, costs, brackets).values())
    numeric_string_covers = copy.deepcopy(covers)
    numeric_string_covers[0]["n"] = str(numeric_string_covers[0]["n"])
    assert not run.exact_grid_counters(config, numeric_string_covers, costs, brackets)[
        "covering"
    ]
    aliased_rates = copy.deepcopy(costs)
    aliased_rates[0]["flip_rate"] = "2/40"
    assert not run.exact_grid_counters(config, covers, aliased_rates, brackets)["cost"]
    assert not independent._canonical_fraction("2/40")
    costs[-1] = copy.deepcopy(costs[0])
    checks = run.exact_grid_counters(config, covers, costs, brackets)
    assert not checks["cost"]
    observed = independent.observed_grid_counters(covers, costs, brackets)
    expected = independent.expected_grid_counters(config)
    assert observed["cost"] != expected["cost"]
    assert sum(observed["cost"].values()) == sum(expected["cost"].values()) == 144


@pytest.mark.parametrize("mutant_n", ["8", 8.0, True])
def test_raw_record_shapes_reject_numeric_aliases_and_extra_fields(
    mutant_n: object,
) -> None:
    certificate = primary.deterministic_cover_bounds(
        8,
        4,
        3,
        max_greedy_rounds=128,
        max_candidate_blocks=30000,
    )
    cover = run.cover_record(certificate, 0.01)
    classification = primary.classify_cost_interval(
        certificate.lower_bound,
        certificate.upper_bound,
        comb(8, 3),
        Fraction(1, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    cost = {
        "n": 8,
        "k": 3,
        "block_size": 4,
        "flip_rate": "1/20",
        "primary": run.classification_record(classification),
        "metric_robustness_probes": list(
            primary.metric_robustness_probes(
                classification,
                comb(8, 3),
                Fraction(1, 20),
                Fraction(1, 20),
                Fraction(9, 10),
                4096,
            )
        ),
    }
    bracket = {
        "n": 8,
        "k": 3,
        "flip_rate": "1/20",
        "anchor_query_count": 1,
        **primary.build_minimum_width_bracket(
            3, ({"block_size": 4, "status": classification.status},), 5
        ),
    }
    assert independent.raw_record_shapes_pass([cover], [cost], [bracket])
    mutated = copy.deepcopy(cover)
    mutated["n"] = mutant_n
    assert not independent.raw_record_shapes_pass([mutated], [cost], [bracket])
    extra = copy.deepcopy(cost)
    extra["attacker_field"] = True
    assert not independent.raw_record_shapes_pass([cover], [extra], [bracket])


def test_receipt_closure_rejects_links_and_output_set_mutations(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    for name in release_contract.PRIMARY_OUTPUTS:
        (artifacts / name).write_text(name + "\n", encoding="utf-8")
    registration = tmp_path / "registration.json"
    manifest = tmp_path / "manifest.json"
    anchor = tmp_path / "anchor.json"
    for path in (registration, manifest, anchor):
        path.write_text(path.name + "\n", encoding="utf-8")
    claim = {"verdict": "claim_ready_for_independent_verification"}
    operation = {"registration": {"sha256": independent.sha256(registration)}}
    receipt = {
        "schema_version": independent.RECEIPT_SCHEMA,
        "release_id": independent.RELEASE_ID,
        "registration_sha256": independent.sha256(registration),
        "manifest_sha256": independent.sha256(manifest),
        "prior_anchor_sha256": independent.sha256(anchor),
        "outputs": {
            name: independent.sha256(artifacts / name)
            for name in release_contract.PRIMARY_OUTPUTS
        },
        "verdict": claim["verdict"],
    }
    assert independent.receipt_closure_passes(
        receipt, registration, manifest, anchor, artifacts, claim, operation
    )
    mutations = []
    missing_output = copy.deepcopy(receipt)
    missing_output["outputs"].pop("cost_checkpoint.json")
    mutations.append(missing_output)
    wrong_link = copy.deepcopy(receipt)
    wrong_link["registration_sha256"] = "0" * 64
    mutations.append(wrong_link)
    wrong_verdict = copy.deepcopy(receipt)
    wrong_verdict["verdict"] = "not_established"
    mutations.append(wrong_verdict)
    extra_output = copy.deepcopy(receipt)
    extra_output["outputs"]["extra.json"] = "0" * 64
    mutations.append(extra_output)
    for mutation in mutations:
        assert not independent.receipt_closure_passes(
            mutation, registration, manifest, anchor, artifacts, claim, operation
        )


def test_claim_and_metric_firewall_reject_overclaiming_mutations() -> None:
    claim = independent.expected_claim_layer()
    assert independent.claim_layer_passes(claim)
    for field, value in (
        ("claim_scope", "external_generalization"),
        ("robustness", "all metrics prove universal invariance"),
        ("not_supported", []),
    ):
        mutated = copy.deepcopy(claim)
        mutated[field] = value
        assert not independent.claim_layer_passes(mutated)

    firewall = independent.expected_metric_firewall()
    mutated_firewall = copy.deepcopy(firewall)
    mutated_firewall["hazard"].append("verified_cover_upper_bound")
    assert mutated_firewall != independent.expected_metric_firewall()


def _operation_fixture(
    tmp_path: Path,
) -> tuple[
    dict[str, object],
    dict[str, object],
    list[dict[str, object]],
    list[dict[str, object]],
    object,
    Path,
]:
    resource = {
        "execution": "sequential_cpu_only",
        "hard_wall_seconds_per_cell": 15,
        "max_candidate_blocks_per_cell": 30000,
        "max_greedy_rounds_per_cell": 4096,
        "max_ram_bytes": 4294967296,
        "max_total_wall_seconds": 900,
    }
    cover = {
        "n": 8,
        "k": 3,
        "block_size": 4,
        "elapsed_seconds": 1.0,
        "greedy_rounds": 10,
        "gain_evaluations": 700,
        "universe_size": 56,
        "candidate_block_count": 70,
        "stop_reason": "cover_complete",
        "construction_status": "deterministic_greedy_incumbent",
    }
    cost = {"n": 8, "k": 3, "block_size": 4, "flip_rate": "1/20"}
    registration_path = tmp_path / "registration.json"
    registration_path.write_text("{}\n", encoding="utf-8")
    registration = {
        "registered_at_utc": "2026-08-02T23:59:59+00:00",
        "source_commit": "a" * 40,
        "claim_grid": {"resource_policy": resource},
    }
    assessment = independent.independent_resource_accounting(
        [cover], resource, 2.0, False
    )
    assessment["events_match_covering_rows"] = True
    assessment["measured_checks_pass"] = True
    operation = {
        "schema_version": independent.OPERATION_SCHEMA,
        "release_id": independent.RELEASE_ID,
        "elapsed_seconds": 2.0,
        "started_utc": "2026-08-03T00:00:00+00:00",
        "finished_utc": "2026-08-03T00:00:02+00:00",
        "resource_policy": resource,
        "resource_compliance": assessment,
        "events": [
            {
                "event": "covering_cell_complete",
                "n": 8,
                "k": 3,
                "block_size": 4,
                "construction_status": "deterministic_greedy_incumbent",
                "stop_reason": "cover_complete",
                "elapsed_seconds": 1.0,
            }
        ],
        "stop_reason_counts": {"cover_complete": 1},
        "missing_cost_cells": [],
        "total_wall_stop": False,
        "run_status": "complete",
        "registration": {
            "path": str(registration_path.resolve()),
            "sha256": independent.sha256(registration_path),
            "source_commit": "a" * 40,
            "registration_commit": "b" * 40,
        },
        "environment": {
            "python": "test",
            "platform": "test",
            "cpu_count": 1,
            "git_head": "b" * 40,
        },
    }
    expected_costs = Counter({(8, 3, 4, "1/20"): 1})
    return operation, registration, [cover], [cost], expected_costs, registration_path


def test_operation_consistency_rejects_resource_event_stop_and_ram_lies(
    tmp_path: Path,
) -> None:
    operation, registration, covers, costs, expected_costs, path = _operation_fixture(
        tmp_path
    )
    assert independent.operation_consistency_passes(
        operation, registration, path, covers, costs, expected_costs
    )
    mutations = []
    no_events = copy.deepcopy(operation)
    no_events["events"] = []
    mutations.append(no_events)
    invented_stop = copy.deepcopy(operation)
    invented_stop["stop_reason_counts"] = {"invented": 1}
    mutations.append(invented_stop)
    elapsed_lie = copy.deepcopy(operation)
    elapsed_lie["elapsed_seconds"] = 999999
    mutations.append(elapsed_lie)
    ram_lie = copy.deepcopy(operation)
    ram_lie["resource_compliance"]["ram"]["compliance"] = "passed"
    mutations.append(ram_lie)
    for mutation in mutations:
        assert not independent.operation_consistency_passes(
            mutation, registration, path, covers, costs, expected_costs
        )

    aggregate_lie = copy.deepcopy(operation)
    aggregate_lie["elapsed_seconds"] = 0.5
    aggregate_lie["resource_compliance"] = independent.independent_resource_accounting(
        covers,
        registration["claim_grid"]["resource_policy"],
        0.5,
        False,  # type: ignore[index]
    )
    aggregate_lie["resource_compliance"]["events_match_covering_rows"] = True
    assert not independent.operation_consistency_passes(
        aggregate_lie, registration, path, covers, costs, expected_costs
    )

    cap_violating_covers = copy.deepcopy(covers)
    cap_violating_covers[0]["greedy_rounds"] = 4097
    cap_lie = copy.deepcopy(operation)
    cap_lie["resource_compliance"] = independent.independent_resource_accounting(
        cap_violating_covers,
        registration["claim_grid"]["resource_policy"],  # type: ignore[index]
        2.0,
        False,
    )
    cap_lie["resource_compliance"]["events_match_covering_rows"] = True
    assert not independent.operation_consistency_passes(
        cap_lie,
        registration,
        path,
        cap_violating_covers,
        costs,
        expected_costs,
    )

    forged_wall_covers = copy.deepcopy(covers)
    forged_wall_covers[0]["stop_reason"] = "operational_wall_stop"
    forged_wall_covers[0]["elapsed_seconds"] = 0.0
    forged_wall = copy.deepcopy(operation)
    forged_wall["events"][0]["stop_reason"] = "operational_wall_stop"
    forged_wall["events"][0]["elapsed_seconds"] = 0.0
    forged_wall["stop_reason_counts"] = {"operational_wall_stop": 1}
    forged_wall["resource_compliance"] = independent.independent_resource_accounting(
        forged_wall_covers,
        registration["claim_grid"]["resource_policy"],  # type: ignore[index]
        2.0,
        False,
    )
    forged_wall["resource_compliance"]["events_match_covering_rows"] = True
    assert not independent.operation_consistency_passes(
        forged_wall,
        registration,
        path,
        forged_wall_covers,
        costs,
        expected_costs,
    )


def test_full_probe_records_exclude_identity_and_reject_semantic_mutations() -> None:
    primary_result = primary.classify_cost_interval(
        2, 5, 30, Fraction(3, 20), Fraction(1, 20), Fraction(9, 10), 4096
    )
    actual = list(
        primary.metric_robustness_probes(
            primary_result,
            30,
            Fraction(3, 20),
            Fraction(1, 20),
            Fraction(9, 10),
            4096,
        )
    )
    expected = independent.independent_probe_records(
        2, 5, 30, Fraction(3, 20), Fraction(1, 20), Fraction(9, 10), 4096
    )
    assert actual == expected
    row = {
        "primary": {"status": primary_result.status},
        "metric_robustness_probes": actual,
    }
    assert run.probe_pack_is_well_formed([row], 5)
    summary = run.summarize_probe_records([row])
    assert summary == independent.independent_probe_summary([row])
    assert summary["totals"]["robustness_records"] == 4
    assert summary["totals"]["identity_diagnostic_records"] == 1
    assert actual[0]["counts_toward_robustness"] is False
    for field, value in (
        ("binding", True),
        ("agrees_with_primary", False),
        ("counts_toward_robustness", True),
        ("metric", "corrupted"),
    ):
        mutated = copy.deepcopy(actual)
        mutated[0][field] = value
        mutated_row = {
            "primary": {"status": primary_result.status},
            "metric_robustness_probes": mutated,
        }
        assert mutated != expected
        if field != "metric":
            assert not run.probe_pack_is_well_formed([mutated_row], 5)


def test_registered_grid_p5_replay_avoids_python_integer_string_limit() -> None:
    previous = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(4300)
        probes = independent.independent_probe_records(
            476,
            562,
            2380,
            Fraction(1, 20),
            Fraction(1, 20),
            Fraction(9, 10),
            4096,
        )
    finally:
        sys.set_int_max_str_digits(previous)
    assert len(probes) == 5
    assert probes[-1]["probe_id"] == "P5_exact_independent_fwer"


def test_synthesis_binds_three_stages_and_five_conclusion_layers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    registration_path = tmp_path / "registration.json"
    registration = _registration_payload()
    registration_path.write_text(
        json.dumps(registration, sort_keys=True) + "\n", encoding="utf-8"
    )
    expected = registration["claim_grid"]["expected_counts"]  # type: ignore[index]
    layers = {
        "result_layer.json": {
            "exact_grid_counters": {"covering": True, "cost": True, "bracket": True},
            "counts": {
                "covering_cells": expected["covering_cells"],
                "cost_cells": expected["cost_cells"],
                "brackets": expected["brackets"],
            },
            "brackets": [{"s_star": None}] * int(expected["brackets"]),
        },
        "reliability_layer.json": {
            "binding_gates": {gate: True for gate in release_contract.PRIMARY_GATE_IDS}
        },
        "claim_layer.json": {"verdict": "claim_ready_for_independent_verification"},
        "operation_layer.json": {
            "run_status": "complete",
            "resource_compliance": {"ram": {"compliance": "not_established"}},
            "registration": {"sha256": synthesize_receipt.sha256(registration_path)},
        },
    }
    for name in release_contract.PRIMARY_OUTPUTS:
        payload = layers.get(name, {"fixture": name})
        (artifacts / name).write_text(json.dumps(payload) + "\n", encoding="utf-8")
    receipt = {
        "schema_version": release_contract.RECEIPT_SCHEMA,
        "release_id": release_contract.RELEASE_ID,
        "registration_sha256": synthesize_receipt.sha256(registration_path),
        "manifest_sha256": registration["manifest_sha256"],
        "prior_anchor_sha256": registration["prior_anchor_sha256"],
        "outputs": {
            name: synthesize_receipt.sha256(artifacts / name)
            for name in release_contract.PRIMARY_OUTPUTS
        },
        "verdict": "claim_ready_for_independent_verification",
    }
    receipt_path = artifacts / "receipt.json"
    receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
    verification = {
        "schema_version": release_contract.VERIFICATION_SCHEMA,
        "release_id": release_contract.RELEASE_ID,
        "verified": True,
        "gates": {gate: True for gate in release_contract.VERIFICATION_GATE_IDS},
        "registration_sha256": synthesize_receipt.sha256(registration_path),
        "receipt_sha256": synthesize_receipt.sha256(receipt_path),
        "primary_outputs": dict(sorted(receipt["outputs"].items())),
        "counts": {
            "covering_cells": expected["covering_cells"],
            "cost_cells": expected["cost_cells"],
            "brackets": expected["brackets"],
        },
        "metric_robustness": {
            "totals": {
                "robustness_records": 576,
                "robustness_agreements": 576,
                "robustness_disagreements": 0,
                "identity_diagnostic_records": 144,
                "identity_diagnostic_agreements": 144,
            }
        },
        "resource_assessment": {
            "measured_resource_checks": "passed",
            "wall_observations": "self_reported_internally_consistent",
            "ram_compliance": "not_established_unmeasured",
        },
        "claim_boundary": release_contract.CLAIM_BOUNDARY,
    }
    verification_path = artifacts / release_contract.VERIFICATION_FILENAME
    verification_path.write_text(json.dumps(verification) + "\n", encoding="utf-8")
    replayed = copy.deepcopy(verification)
    monkeypatch.setattr(
        synthesize_receipt,
        "verify_bundle",
        lambda *_args, **_kwargs: copy.deepcopy(replayed),
    )
    synthesis = synthesize_receipt.build_synthesis(
        registration_path, artifacts, verification_path
    )
    assert synthesis["pass"]
    assert set(synthesis["conclusion_layers"]) == {
        "metric_robustness",
        "task_result",
        "measurement_reliability",
        "claim_support",
        "operational_decision",
    }
    forged = copy.deepcopy(verification)
    forged["receipt_sha256"] = "0" * 64
    verification_path.write_text(json.dumps(forged) + "\n", encoding="utf-8")
    assert not synthesize_receipt.build_synthesis(
        registration_path, artifacts, verification_path
    )["pass"]

    sensitive = copy.deepcopy(verification)
    sensitive["metric_robustness"]["totals"]["robustness_agreements"] = 575
    sensitive["metric_robustness"]["totals"]["robustness_disagreements"] = 1
    verification_path.write_text(json.dumps(sensitive) + "\n", encoding="utf-8")
    replayed = copy.deepcopy(sensitive)
    sensitive_synthesis = synthesize_receipt.build_synthesis(
        registration_path, artifacts, verification_path
    )
    assert sensitive_synthesis["pass"]
    assert (
        sensitive_synthesis["conclusion_layers"]["metric_robustness"]
        == "alternative_metric_sensitivity_detected"
    )

    truthy_gate = copy.deepcopy(verification)
    first_gate = next(iter(release_contract.VERIFICATION_GATE_IDS))
    truthy_gate["gates"][first_gate] = "true"
    verification_path.write_text(json.dumps(truthy_gate) + "\n", encoding="utf-8")
    replayed = copy.deepcopy(truthy_gate)
    assert not synthesize_receipt.build_synthesis(
        registration_path, artifacts, verification_path
    )["pass"]
