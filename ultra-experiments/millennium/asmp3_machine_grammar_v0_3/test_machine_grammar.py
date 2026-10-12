from __future__ import annotations

import copy
import json

import pytest

from machine_grammar import (
    ARTIFACT_PATH,
    EXAMPLE_ADM_PATH,
    EXAMPLE_FIX_PATH,
    ExecutionFault,
    GrammarError,
    bounded_halts_utm_v1,
    build_artifact,
    canonical_bytes,
    compile_v2_21_instance,
    encode_utm_v1,
    execute_ir,
    load_grammar,
    malformed_fixtures,
    parse_canonical_bytes,
    validate_instance,
    validate_program,
    reference_runtime_audit,
)
from verify_machine_grammar import verify


def test_grammar_registry_freezes_codec_machine_and_membership() -> None:
    grammar = load_grammar()
    assert grammar["canonical_codec"]["id"] == "ASMP3-CANONICAL-JSON-v0.3"
    assert grammar["universal_machine"]["id"] == "WV-IR-v0.3"
    assert grammar["membership_semantics"]["id"] == "WV-MEMBERSHIP-v0.3"


def test_registry_has_closed_component_builtin_and_opcode_tables() -> None:
    grammar = load_grammar()
    assert len(grammar["component_signatures"]) == 23
    assert len(grammar["builtin_programs"]) == 25
    assert len(grammar["universal_machine"]["opcodes"]) == 25


@pytest.mark.parametrize("mode", ["FIX", "ADM"])
@pytest.mark.parametrize("machine_index", [0, 1, 17, 999])
def test_v2_21_instances_round_trip_canonically(machine_index: int, mode: str) -> None:
    instance = compile_v2_21_instance(machine_index, mode)
    assert parse_canonical_bytes(canonical_bytes(instance)) == instance


def test_FIX_and_ADM_quantifier_fields_are_distinct() -> None:
    fixed = compile_v2_21_instance(5, "FIX")
    adm = compile_v2_21_instance(5, "ADM")
    assert fixed["fixed_interface"] == "G_VEC" and fixed["admissible_interfaces"] is None
    assert adm["fixed_interface"] is None and adm["admissible_interfaces"]["interface_ids"] == ["G_VEC"]


def test_all_noncanonical_byte_fixtures_are_rejected() -> None:
    rows = malformed_fixtures(compile_v2_21_instance(17, "FIX"))
    assert len(rows) == 5
    assert all(row["rejected"] and row["reason"] for row in rows)


def test_unknown_top_level_field_is_rejected() -> None:
    instance = compile_v2_21_instance(2, "FIX")
    instance["alias"] = "forbidden"
    with pytest.raises(GrammarError):
        validate_instance(instance)


def test_unsorted_program_table_is_rejected() -> None:
    instance = compile_v2_21_instance(2, "FIX")
    instance["programs"][0], instance["programs"][1] = instance["programs"][1], instance["programs"][0]
    with pytest.raises(GrammarError, match="sorted"):
        validate_instance(instance)


def test_noncanonical_rational_is_rejected() -> None:
    instance = compile_v2_21_instance(2, "FIX")
    instance["environment"]["noise"]["marginal_eta"] = {"num": 2, "den": 10}
    with pytest.raises(GrammarError, match="coprime"):
        validate_instance(instance)


def test_wrong_component_signature_is_rejected() -> None:
    instance = compile_v2_21_instance(2, "FIX")
    target = next(program for program in instance["programs"] if program["id"] == "WORLD_VALID")
    target["inputs"] = ["nat"]
    with pytest.raises(GrammarError, match="signature"):
        validate_instance(instance)


def test_builtin_rejects_unknown_parameters() -> None:
    instance = compile_v2_21_instance(2, "FIX")
    target = next(program for program in instance["programs"] if program["id"] == "WORLD_VALID")
    target["params"] = {"hidden": 1}
    with pytest.raises(GrammarError, match="takes no params"):
        validate_instance(instance)


def test_typed_IR_accepts_minsky_core_program() -> None:
    grammar = load_grammar()
    program = {
        "id": "COUNTDOWN",
        "kind": "ir",
        "inputs": ["nat"],
        "output": "nat",
        "registers": ["nat", "nat", "nat", "bit"],
        "instructions": [
            {"op": "const_nat", "dst": 1, "value": 1},
            {"op": "const_nat", "dst": 2, "value": 0},
            {"op": "eq", "dst": 3, "left": 0, "right": 2},
            {"op": "branch", "cond": 3, "if_true": 6, "if_false": 4},
            {"op": "sub_sat", "dst": 0, "left": 0, "right": 1},
            {"op": "jump", "target": 2},
            {"op": "return", "src": 0},
        ],
    }
    program_id, signature = validate_program(program, grammar)
    assert program_id == "COUNTDOWN"
    assert signature == (("nat",), "nat")


def test_reference_interpreter_executes_minsky_countdown_with_gas() -> None:
    program = {
        "id": "COUNTDOWN",
        "kind": "ir",
        "inputs": ["nat"],
        "output": "nat",
        "registers": ["nat", "nat", "nat", "bit"],
        "instructions": [
            {"op": "const_nat", "dst": 1, "value": 1},
            {"op": "const_nat", "dst": 2, "value": 0},
            {"op": "eq", "dst": 3, "left": 0, "right": 2},
            {"op": "branch", "cond": 3, "if_true": 6, "if_false": 4},
            {"op": "sub_sat", "dst": 0, "left": 0, "right": 1},
            {"op": "jump", "target": 2},
            {"op": "return", "src": 0},
        ],
    }
    receipt = execute_ir(program, [23], 100_000)
    assert receipt["status"] == "HALT"
    assert receipt["value"] == 0
    assert receipt["gas"] > 0
    assert execute_ir(program, [23], 10)["reason"] == "OUT_OF_GAS"


def test_U_TM_v1_halt_loop_and_invalid_code_semantics() -> None:
    halt = encode_utm_v1(1, 0, [(None, symbol, 1) for symbol in range(4)])
    loop = encode_utm_v1(1, 0, [(0, symbol, 1) for symbol in range(4)])
    assert bounded_halts_utm_v1(halt, b"x", 1)[0] is True
    assert bounded_halts_utm_v1(loop, b"x", 100)[0] is False
    assert bounded_halts_utm_v1(0, b"", 100)[0] is True


def test_reference_runtime_audit_passes_all_checks() -> None:
    audit = reference_runtime_audit()
    assert audit["certified"]
    assert len(audit["checks"]) == 5


def test_large_allocation_and_long_simulation_preflight_fuel() -> None:
    pow_program = {
        "id": "POW_GUARD",
        "kind": "ir",
        "inputs": ["nat"],
        "output": "nat",
        "registers": ["nat", "nat"],
        "instructions": [{"op": "pow2", "dst": 1, "exponent": 0}, {"op": "return", "src": 1}],
    }
    assert execute_ir(pow_program, [10**9], 100)["reason"] == "OUT_OF_GAS"

    loop = encode_utm_v1(1, 0, [(0, symbol, 1) for symbol in range(4)])
    sim_program = {
        "id": "SIM_GUARD",
        "kind": "ir",
        "inputs": ["nat"],
        "output": "bit",
        "registers": ["nat", "bytes", "bit"],
        "instructions": [
            {"op": "const_bytes", "dst": 1, "hex": ""},
            {"op": "bounded_halts", "dst": 2, "machine_index": loop, "input": 1, "steps": 0},
            {"op": "return", "src": 2},
        ],
    }
    assert execute_ir(sim_program, [10**9], 100)["reason"] == "OUT_OF_GAS"


def test_IR_rejects_out_of_range_jump_and_return_type() -> None:
    grammar = load_grammar()
    bad_jump = {"id": "BAD_JUMP", "kind": "ir", "inputs": [], "output": "nat", "registers": ["nat"], "instructions": [{"op": "jump", "target": 2}, {"op": "return", "src": 0}]}
    with pytest.raises(GrammarError, match="out of range"):
        validate_program(bad_jump, grammar)
    bad_return = {"id": "BAD_RETURN", "kind": "ir", "inputs": [], "output": "bit", "registers": ["nat"], "instructions": [{"op": "return", "src": 0}]}
    with pytest.raises(GrammarError, match="return type"):
        validate_program(bad_return, grammar)


def test_provenance_hashes_are_bound() -> None:
    instance = compile_v2_21_instance(64, "ADM")
    assert set(instance["provenance"]) == {"canonical_sha256", "typed_successor_sha256", "v2_21_theorem_sha256", "v2_21_artifact_sha256"}
    assert all(len(value) == 64 for value in instance["provenance"].values())


def test_all_eleven_producer_gates_pass() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["gates"]) == 11
    assert all(artifact["gates"].values())


def test_written_artifact_and_independent_verifier_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    assert parse_canonical_bytes(EXAMPLE_FIX_PATH.read_bytes())["interface_mode"] == "FIX"
    assert parse_canonical_bytes(EXAMPLE_ADM_PATH.read_bytes())["interface_mode"] == "ADM"
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 11
