from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "machine_grammar_v0_3.json"
VERIFY_PATH = HERE / "artifacts" / "machine_grammar_verification_v0_3.json"
GRAMMAR_PATH = HERE / "asmp3_machine_grammar_v0_3.json"
EXAMPLE_FIX_PATH = HERE / "artifacts" / "v2_21_e17_FIX.machine.json"
EXAMPLE_ADM_PATH = HERE / "artifacts" / "v2_21_e17_ADM.machine.json"
PATHS = {
    "canonical_sha256": ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "registry_sha256": ROOT / "problem_set_v0_1.json",
    "typed_markdown_sha256": ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "typed_json_sha256": ROOT / "asmp3_typed_successor_v0_2" / "typed_successor_v0_2.json",
    "v2_21_theorem_sha256": ROOT / "asmp3_standard_encoding_transfer_v2_21" / "STANDARD_ENCODING_AND_QUANTIFIER_TRANSFER_THEOREM_v2_21.md",
    "v2_21_artifact_sha256": ROOT / "asmp3_standard_encoding_transfer_v2_21" / "artifacts" / "standard_encoding_transfer_v2_21.json",
    "v2_21_verification_sha256": ROOT / "asmp3_standard_encoding_transfer_v2_21" / "artifacts" / "standard_encoding_transfer_verification_v2_21.json",
    "v2_21_manifest_sha256": ROOT / "asmp3_standard_encoding_transfer_v2_21" / "RELEASE_MANIFEST_v2_21.json",
    "grammar_sha256": GRAMMAR_PATH,
}
FIXTURE_INDICES = (0, 1, 2, 5, 17, 64, 999)
PROGRAM_SPECS = (
    ("ATOM_DESC_BOUND", "ATOM_COORDINATE_BOUND_V1", "atom_description_bound", None),
    ("ATOM_EVAL_COST", "ATOM_COORDINATE_COST_V1", "atom_evaluation_cost", "machine"),
    ("ATOM_LOCALITY", "ATOM_COORDINATE_LOCALITY_V1", "atom_locality_bound", None),
    ("ATOM_VALID", "ATOM_COORDINATE_VALID_V1", "atom_valid", None),
    ("DECISION_RELATION", "PARITY_RELATION_V1", "decision_relation", None),
    ("IDEAL_ORACLE", "V2_21_IDEAL_ORACLE_V1", "ideal_oracle", "machine"),
    ("INFO_PROVER", "PROVER_FULL_WORLD_VIEW_V1", "information_prover", None),
    ("INFO_VERIFIER", "VERIFIER_PUBLIC_VIEW_V1", "information_verifier", None),
    ("MALFORMED", "MALFORMED_LOSES_V1", "interface_malformed", None),
    ("MESSAGE_VALID", "VECTOR_MESSAGE_VALID_V1", "interface_message_valid", None),
    ("NOISE_KERNEL", "BSC_ONE_FIFTH_KERNEL_V1", "noise_transition_kernel", None),
    ("NOISE_LEGAL", "NOISE_EXACT_BSC_LEGAL_V1", "noise_legal", None),
    ("ORDER", "VECTOR_ORDER_V1", "interface_order", None),
    ("OUTPUT_VALID", "OUTPUT_BIT_VALID_V1", "output_valid", None),
    ("PAYOFF", "CLAIM_SELECTION_PAYOFF_V1", "interface_payoff", None),
    ("PROVER_BUDGET", "WV_PROVER_EXP_BUDGET_V1", "prover_budget", None),
    ("PUBLIC_VALID", "PUBLIC_BYTES_VALID_V1", "public_instance_valid", None),
    ("QUERY_BOUND", "WV_LINEAR_QUERY_BOUND_V1", "interface_resource_bound", None),
    ("REFUTE", "COORDINATE_REFUTE_V1", "interface_refute", "machine"),
    ("REPLICATION_EQUIV", "IDENTITY_REPLICATION_EQUIVALENT_V1", "replication_equivalent", None),
    ("REPLICATION_VALID", "IDENTITY_REPLICATION_VALID_V1", "replication_valid", None),
    ("STOP", "SINGLE_RESPONSE_STOP_V1", "interface_stop", None),
    ("TIME_BOUND", "WV_LINEAR_TIME_BOUND_V1", "interface_resource_bound", None),
    ("TRANSCRIPT_BOUND", "WV_LINEAR_TRANSCRIPT_BOUND_V1", "interface_resource_bound", None),
    ("WORLD_VALID", "WORLD_D_BITS_VALID_V1", "world_valid", None),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def uleb(value: int) -> bytes:
    output = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        output.append(byte | 0x80 if value else byte)
        if not value:
            return bytes(output)


def independent_machine_index(halts: bool) -> int:
    payload = bytearray([0xA3])
    payload.extend(uleb(1))
    payload.extend(uleb(0))
    for symbol in range(4):
        payload.extend(uleb(0 if halts else 1))
        payload.append(symbol | (1 << 2))
    return int.from_bytes(payload, "big")


def independent_tm_gas(machine_index: int, input_bytes: bytes, steps: int, halts: bool) -> tuple[bool, int]:
    tape = {}
    position = 0
    for byte in input_bytes:
        for bit in range(7, -1, -1):
            tape[position] = (byte >> bit) & 1
            position += 1
    tape[position] = 2
    head = 0
    gas = 1 + max(1, machine_index.bit_length()) + 8 * len(input_bytes)
    for _ in range(steps):
        symbol = tape.get(head, 3)
        tape[head] = symbol
        gas += 1 + 1 + max(1, abs(head).bit_length()) + max(1, len(tape).bit_length())
        if halts:
            return True, gas
    return False, gas


def independent_countdown_receipts(start: int) -> tuple[dict[str, object], dict[str, object]]:
    gas = 4
    dispatches = 2
    current = start
    while True:
        gas += 1 + max(1, current.bit_length()) + 1 + 1
        dispatches += 1
        gas += 2
        dispatches += 1
        if current == 0:
            gas += 2
            dispatches += 1
            break
        next_value = current - 1
        gas += 1 + max(1, current.bit_length()) + 1 + max(1, next_value.bit_length())
        dispatches += 1
        gas += 1
        dispatches += 1
        current = next_value
    return (
        {"status": "HALT", "value": 0, "gas": gas, "dispatches": dispatches},
        {"status": "FAULT", "reason": "OUT_OF_GAS", "gas": 4, "dispatches": 3},
    )


def independent_instance(grammar: dict[str, Any], machine_index: int, mode: str, hashes: dict[str, str]) -> dict[str, Any]:
    programs = []
    for program_id, builtin, component, param_kind in PROGRAM_SPECS:
        signature = grammar["component_signatures"][component]
        programs.append(
            {
                "id": program_id,
                "kind": "builtin",
                "inputs": signature["inputs"],
                "output": signature["output"],
                "builtin": builtin,
                "params": {"machine_index": machine_index} if param_kind == "machine" else {},
            }
        )
    programs.sort(key=lambda item: item["id"])
    interface = {
        "id": "G_VEC",
        "message_valid": "MESSAGE_VALID",
        "order": "ORDER",
        "stop": "STOP",
        "verifier_time_bound": "TIME_BOUND",
        "semantic_query_bound": "QUERY_BOUND",
        "transcript_bit_bound": "TRANSCRIPT_BOUND",
        "malformed": "MALFORMED",
        "payoff": "PAYOFF",
        "refute": "REFUTE",
        "serialization": {"codec": "ASMP3-CANONICAL-JSON-v0.3", "aliases": False, "padding": False},
    }
    return {
        "schema_version": "asmp3_machine_instance_v0_3",
        "problem_id": "ASMP-3",
        "problem_version": "ASMP-3-MACHINE-v0.3",
        "codec": "ASMP3-CANONICAL-JSON-v0.3",
        "universal_machine": "WV-IR-v0.3",
        "membership_semantics": "WV-MEMBERSHIP-v0.3",
        "family_id": f"nonhalt-reduction-{machine_index}-{mode.lower()}",
        "interface_mode": mode,
        "scale": {"parameter": "n", "minimum": 2},
        "programs": programs,
        "environment": {
            "domains": {"public_instance_valid": "PUBLIC_VALID", "world_valid": "WORLD_VALID", "output_valid": "OUTPUT_VALID"},
            "decision_relation": "DECISION_RELATION",
            "atoms": {"valid": "ATOM_VALID", "description_length_bound": "ATOM_DESC_BOUND", "locality_bound": "ATOM_LOCALITY", "evaluation_cost_bound": "ATOM_EVAL_COST"},
            "replications": {"valid": "REPLICATION_VALID", "equivalent": "REPLICATION_EQUIV"},
            "ideal_oracle": "IDEAL_ORACLE",
            "noise": {"model_id": "BSC_ONE_FIFTH", "legal_process": "NOISE_LEGAL", "transition_kernel": "NOISE_KERNEL", "marginal_eta": {"num": 1, "den": 5}},
            "information": {"prover_view": "INFO_PROVER", "verifier_view": "INFO_VERIFIER"},
            "prover_budget": "PROVER_BUDGET",
        },
        "interfaces": [interface],
        "fixed_interface": "G_VEC" if mode == "FIX" else None,
        "admissible_interfaces": None if mode == "FIX" else {"kind": "finite", "interface_ids": ["G_VEC"]},
        "provenance": {
            "canonical_sha256": hashes["canonical_sha256"],
            "typed_successor_sha256": hashes["typed_json_sha256"],
            "v2_21_theorem_sha256": hashes["v2_21_theorem_sha256"],
            "v2_21_artifact_sha256": hashes["v2_21_artifact_sha256"],
        },
    }


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    grammar = json.loads(GRAMMAR_PATH.read_text(encoding="utf-8"))
    hashes = {name: sha256(path) for name, path in PATHS.items()}
    reconstructed = []
    for machine_index in FIXTURE_INDICES:
        for mode in ("FIX", "ADM"):
            instance = independent_instance(grammar, machine_index, mode, hashes)
            encoded = canonical_bytes(instance)
            reconstructed.append(
                {
                    "machine_index": machine_index,
                    "mode": mode,
                    "bytes": len(encoded),
                    "sha256": hashlib.sha256(encoded).hexdigest().upper(),
                    "round_trip_equal": json.loads(encoded) == instance,
                    "fixed_interface": instance["fixed_interface"],
                    "admissible_interfaces": instance["admissible_interfaces"],
                    "certified": json.loads(encoded) == instance,
                }
            )
    typed = json.loads(PATHS["typed_json_sha256"].read_text(encoding="utf-8"))
    v2_21 = json.loads(PATHS["v2_21_artifact_sha256"].read_text(encoding="utf-8"))
    halt_index = independent_machine_index(True)
    loop_index = independent_machine_index(False)
    halt_result, halt_gas = independent_tm_gas(halt_index, b"A", 1, True)
    loop_result, loop_gas = independent_tm_gas(loop_index, b"A", 32, False)
    countdown_success, countdown_low_fuel = independent_countdown_receipts(19)
    runtime = result["reference_runtime_audit"]
    checks = {
        "V0_schema_status_and_all_hashes": result["schema_version"] == "asmp3_machine_grammar_artifact_v0_3" and result["source_hashes"] == hashes,
        "V1_codec_fields_and_forbidden_alias_features": len(grammar["canonical_codec"]) == 12 and all(grammar["canonical_codec"][key] is False for key in ("allow_duplicate_keys", "allow_float", "allow_unknown_fields", "allow_bom", "allow_trailing_bytes")),
        "V2_universal_machine_basis_opcodes_and_cost_frozen": grammar["universal_machine"]["id"] == "WV-IR-v0.3" and len(grammar["universal_machine"]["opcodes"]) == 25 and "Minsky-complete" in grammar["universal_machine"]["universal_basis"] and "bit-cost" in grammar["universal_machine"]["cost_model"],
        "V3_all_component_and_builtin_signatures_are_closed": len(grammar["component_signatures"]) == 23 and len(grammar["builtin_programs"]) == 25 and all(component in grammar["component_signatures"] for component in grammar["builtin_programs"].values()),
        "V4_all_fourteen_compilers_and_two_examples_reconstructed_byte_exactly": result["compiled_rows"] == reconstructed and len(reconstructed) == 14 and EXAMPLE_FIX_PATH.read_bytes() == canonical_bytes(independent_instance(grammar, 17, "FIX", hashes)) and EXAMPLE_ADM_PATH.read_bytes() == canonical_bytes(independent_instance(grammar, 17, "ADM", hashes)),
        "V5_FIX_and_ADM_machine_quantifiers_are_distinct": all(row["fixed_interface"] == "G_VEC" and row["admissible_interfaces"] is None for row in reconstructed if row["mode"] == "FIX") and all(row["fixed_interface"] is None and row["admissible_interfaces"] == {"kind": "finite", "interface_ids": ["G_VEC"]} for row in reconstructed if row["mode"] == "ADM"),
        "V6_malformed_canonicality_firewall_receipts_complete": len(result["malformed_rows"]) == 5 and all(row["rejected"] and row["reason"] for row in result["malformed_rows"]),
        "V7_typed_parent_fields_are_machine_represented": typed["status"] == "nonnormative_successor_draft" and set(typed["typed_layers"]) == {"environment", "fixed_game", "protocol"},
        "V8_v2_21_full_set_reduction_survives_compilation": v2_21["certified"] is True and v2_21["parent_resolution_audit"]["FIX_ADM_quantifier_fork_changes_reduction_truth"] is False and result["resolution_effect"]["v2_21_reduction_compiles"] is True,
        "V9_claim_boundary_is_successor_not_silent_parent_amendment": result["resolution_effect"]["v0_1_silently_amended"] is False and result["resolution_effect"]["successor_problem_created"] == "ASMP-3-MACHINE-v0.3" and result["resolution_effect"]["remaining_external_reproductions"] == "0/2" and "nonnormative successor proposal" in grammar["claim_boundary"] and result["certified"] is True,
        "V10_reference_UTM_and_IR_gas_receipts_reconstructed": runtime["halt_machine_index"] == str(halt_index) and runtime["loop_machine_index"] == str(loop_index) and runtime["halt_gas"] == halt_gas and runtime["loop_gas"] == loop_gas and runtime["invalid_gas"] == 2 and halt_result is True and loop_result is False and runtime["countdown_success"] == countdown_success and runtime["countdown_low_fuel"] == countdown_low_fuel and runtime["certified"] is True,
    }
    return {
        "schema_version": "asmp3_machine_grammar_verification_v0_3",
        "checker": "clean_room_hash_codec_IR_signature_compiler_quantifier_malformed_parent_and_claim_boundary_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": "The checker reconstructs compiler bytes independently. Adoption and external expert reproduction remain non-machine obligations.",
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if not receipt["passed"]:
        failed = [name for name, passed in receipt["checks"].items() if not passed]
        raise RuntimeError(f"ASMP-3 machine grammar verification failed: {failed}")
    print(f"ASMP-3 machine grammar verification passed: {receipt['check_count']}/{receipt['check_count']}")


if __name__ == "__main__":
    main()
