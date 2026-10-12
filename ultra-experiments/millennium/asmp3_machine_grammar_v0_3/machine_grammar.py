from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GRAMMAR_PATH = HERE / "asmp3_machine_grammar_v0_3.json"
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "machine_grammar_v0_3.json"
EXAMPLE_FIX_PATH = ARTIFACT_DIR / "v2_21_e17_FIX.machine.json"
EXAMPLE_ADM_PATH = ARTIFACT_DIR / "v2_21_e17_ADM.machine.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_MD_PATH = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
TYPED_JSON_PATH = ROOT / "asmp3_typed_successor_v0_2" / "typed_successor_v0_2.json"
V2_21_THEOREM_PATH = ROOT / "asmp3_standard_encoding_transfer_v2_21" / "STANDARD_ENCODING_AND_QUANTIFIER_TRANSFER_THEOREM_v2_21.md"
V2_21_ARTIFACT_PATH = ROOT / "asmp3_standard_encoding_transfer_v2_21" / "artifacts" / "standard_encoding_transfer_v2_21.json"
V2_21_VERIFY_PATH = ROOT / "asmp3_standard_encoding_transfer_v2_21" / "artifacts" / "standard_encoding_transfer_verification_v2_21.json"
V2_21_MANIFEST_PATH = ROOT / "asmp3_standard_encoding_transfer_v2_21" / "RELEASE_MANIFEST_v2_21.json"


VALUE_TYPES = {"bit", "nat", "bytes", "rational", "json"}
ID_PATTERN = re.compile(r"[A-Z][A-Z0-9_]{0,63}\Z")
INSTANCE_KEYS = {
    "schema_version",
    "problem_id",
    "problem_version",
    "codec",
    "universal_machine",
    "membership_semantics",
    "family_id",
    "interface_mode",
    "scale",
    "programs",
    "environment",
    "interfaces",
    "fixed_interface",
    "admissible_interfaces",
    "provenance",
}
ENVIRONMENT_KEYS = {
    "domains",
    "decision_relation",
    "atoms",
    "replications",
    "ideal_oracle",
    "noise",
    "information",
    "prover_budget",
}
INTERFACE_KEYS = {
    "id",
    "message_valid",
    "order",
    "stop",
    "verifier_time_bound",
    "semantic_query_bound",
    "transcript_bit_bound",
    "malformed",
    "payoff",
    "refute",
    "serialization",
}


class GrammarError(ValueError):
    pass


class ExecutionFault(RuntimeError):
    pass


class OutOfGas(ExecutionFault):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GrammarError(f"duplicate object key: {key}")
        result[key] = value
    return result


def _validate_json_domain(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if value < 0:
            raise GrammarError(f"negative integer at {path}")
        return
    if isinstance(value, float):
        raise GrammarError(f"floating-point value at {path}")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_domain(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise GrammarError(f"non-string key at {path}")
            _validate_json_domain(item, f"{path}.{key}")
        return
    raise GrammarError(f"unsupported JSON value at {path}: {type(value).__name__}")


def canonical_bytes(value: object) -> bytes:
    _validate_json_domain(value)
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def parse_canonical_json_value(payload: bytes) -> Any:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise GrammarError("UTF-8 BOM is forbidden")
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda _: (_ for _ in ()).throw(GrammarError("floats are forbidden")),
        )
    except GrammarError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise GrammarError("invalid canonical JSON value") from exc
    _validate_json_domain(value)
    if canonical_bytes(value) != payload:
        raise GrammarError("noncanonical JSON value bytes")
    return value


def parse_canonical_bytes(payload: bytes) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise GrammarError("UTF-8 BOM is forbidden")
    value = parse_canonical_json_value(payload)
    if not isinstance(value, dict):
        raise GrammarError("top-level value must be an object")
    _validate_json_domain(value)
    if canonical_bytes(value) != payload:
        raise GrammarError("noncanonical byte serialization")
    validate_instance(value)
    return value


def _uleb_decode(payload: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    start = offset
    while offset < len(payload):
        byte = payload[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            if offset - start > 1 and byte == 0:
                raise ExecutionFault("noncanonical ULEB128")
            return value, offset
        shift += 7
        if shift > 1_000_000:
            raise ExecutionFault("ULEB128 field too large")
    raise ExecutionFault("truncated ULEB128")


def _uleb_encode(value: int) -> bytes:
    if value < 0:
        raise ValueError(value)
    encoded = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            encoded.append(byte | 0x80)
        else:
            encoded.append(byte)
            return bytes(encoded)


def encode_utm_v1(state_count: int, start_state: int, transitions: list[tuple[int | None, int, int]]) -> int:
    if state_count < 1 or not 0 <= start_state < state_count or len(transitions) != 4 * state_count:
        raise ValueError("invalid U_TM_v1 table dimensions")
    payload = bytearray([0xA3])
    payload.extend(_uleb_encode(state_count))
    payload.extend(_uleb_encode(start_state))
    for next_state, write_symbol, move in transitions:
        if next_state is not None and not 0 <= next_state < state_count:
            raise ValueError("invalid next state")
        if not 0 <= write_symbol <= 3 or not 0 <= move <= 2:
            raise ValueError("invalid transition action")
        payload.extend(_uleb_encode(0 if next_state is None else next_state + 1))
        payload.append(write_symbol | (move << 2))
    return int.from_bytes(payload, "big")


def _decode_utm_v1(machine_index: int) -> tuple[int, list[tuple[int | None, int, int]]]:
    if machine_index < 0:
        raise ExecutionFault("negative machine index")
    payload = b"" if machine_index == 0 else machine_index.to_bytes((machine_index.bit_length() + 7) // 8, "big")
    if not payload or payload[0] != 0xA3:
        raise ExecutionFault("invalid U_TM_v1 magic")
    state_count, offset = _uleb_decode(payload, 1)
    start_state, offset = _uleb_decode(payload, offset)
    if state_count < 1 or start_state >= state_count:
        raise ExecutionFault("invalid U_TM_v1 header")
    if 8 * state_count > len(payload) - offset:
        raise ExecutionFault("U_TM_v1 table cannot fit remaining bytes")
    transitions = []
    for _ in range(4 * state_count):
        next_plus_one, offset = _uleb_decode(payload, offset)
        if offset >= len(payload):
            raise ExecutionFault("truncated U_TM_v1 action")
        action = payload[offset]
        offset += 1
        write_symbol = action & 0x03
        move = (action >> 2) & 0x03
        if action >> 4 or move > 2:
            raise ExecutionFault("invalid U_TM_v1 action")
        next_state = None if next_plus_one == 0 else next_plus_one - 1
        if next_state is not None and next_state >= state_count:
            raise ExecutionFault("invalid U_TM_v1 target")
        transitions.append((next_state, write_symbol, move))
    if offset != len(payload):
        raise ExecutionFault("trailing U_TM_v1 bytes")
    return start_state, transitions


def bounded_halts_utm_v1(machine_index: int, input_bytes: bytes, steps: int, gas_limit: int | None = None) -> tuple[bool, int]:
    try:
        state, transitions = _decode_utm_v1(machine_index)
    except ExecutionFault:
        invalid_gas = 1 + max(1, machine_index.bit_length())
        if gas_limit is not None and invalid_gas > gas_limit:
            raise OutOfGas("U_TM_v1 decode exceeds gas")
        return True, invalid_gas
    tape: dict[int, int] = {}
    position = 0
    for byte in input_bytes:
        for bit in range(7, -1, -1):
            tape[position] = (byte >> bit) & 1
            position += 1
    tape[position] = 2
    head = 0
    gas = 1 + max(1, machine_index.bit_length()) + 8 * len(input_bytes)
    if gas_limit is not None and gas > gas_limit:
        raise OutOfGas("U_TM_v1 initialization exceeds gas")
    for _ in range(steps):
        symbol = tape.get(head, 3)
        next_state, write_symbol, move = transitions[4 * state + symbol]
        tape[head] = write_symbol
        if write_symbol == 3:
            tape.pop(head, None)
        if move == 0:
            head -= 1
        elif move == 2:
            head += 1
        gas += 1 + max(1, state.bit_length()) + max(1, abs(head).bit_length()) + max(1, len(tape).bit_length())
        if gas_limit is not None and gas > gas_limit:
            raise OutOfGas("U_TM_v1 execution exceeds gas")
        if next_state is None:
            return True, gas
        state = next_state
    return False, gas


def _typed_zero(value_type: str) -> Any:
    return {"bit": 0, "nat": 0, "bytes": b"", "rational": {"num": 0, "den": 1}, "json": None}[value_type]


def _runtime_type(value: Any, expected: str) -> bool:
    if expected == "bit":
        return isinstance(value, int) and not isinstance(value, bool) and value in (0, 1)
    if expected == "nat":
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0
    if expected == "bytes":
        return isinstance(value, bytes)
    if expected == "rational":
        try:
            _rational(value, "runtime.rational")
            return True
        except GrammarError:
            return False
    if expected == "json":
        try:
            _validate_json_domain(value)
            return True
        except GrammarError:
            return False
    return False


def value_bit_size(value: Any, value_type: str) -> int:
    if value_type == "bit":
        return 1
    if value_type == "nat":
        return max(1, value.bit_length())
    if value_type == "bytes":
        return max(1, 8 * len(value))
    if value_type == "rational":
        return max(1, value["num"].bit_length()) + max(1, value["den"].bit_length())
    if value_type == "json":
        return max(1, 8 * len(canonical_bytes(value)))
    raise ExecutionFault("unknown runtime type")


def execute_ir(program: dict[str, Any], arguments: list[Any], fuel: int) -> dict[str, Any]:
    grammar = load_grammar()
    _, (inputs, output) = validate_program(program, grammar)
    if program["kind"] != "ir":
        raise ExecutionFault("reference interpreter executes IR programs only")
    if len(arguments) != len(inputs) or fuel < 0:
        raise ExecutionFault("invalid execution invocation")
    for value, value_type in zip(arguments, inputs):
        if not _runtime_type(value, value_type):
            raise ExecutionFault("runtime input type mismatch")
    register_types = program["registers"]
    registers = [_typed_zero(value_type) for value_type in register_types]
    registers[: len(arguments)] = arguments
    instructions = program["instructions"]
    pc = 0
    gas = 0
    dispatches = 0
    while True:
        if not 0 <= pc < len(instructions):
            return {"status": "FAULT", "reason": "PC_OUT_OF_RANGE", "gas": gas, "dispatches": dispatches}
        instruction = instructions[pc]
        op = instruction["op"]
        dispatches += 1
        reads: list[int] = []
        writes: list[tuple[int, Any]] = []
        next_pc = pc + 1
        extra_gas = 0
        try:
            if op == "const_bit" or op == "const_nat":
                writes = [(instruction["dst"], instruction["value"])]
            elif op == "const_bytes":
                writes = [(instruction["dst"], bytes.fromhex(instruction["hex"]))]
            elif op == "const_rational" or op == "const_json":
                writes = [(instruction["dst"], instruction["value"])]
            elif op == "copy":
                reads = [instruction["src"]]
                writes = [(instruction["dst"], registers[instruction["src"]])]
            elif op in {"eq", "lt", "add", "sub_sat", "mul"}:
                left_index, right_index = instruction["left"], instruction["right"]
                left, right = registers[left_index], registers[right_index]
                reads = [left_index, right_index]
                if op == "eq":
                    result = int(left == right)
                elif op == "lt":
                    result = int(left < right)
                elif op == "add":
                    result = left + right
                elif op == "sub_sat":
                    result = max(0, left - right)
                else:
                    result = left * right
                writes = [(instruction["dst"], result)]
            elif op == "pow2":
                reads = [instruction["exponent"]]
                exponent = registers[instruction["exponent"]]
                minimum_cost = 1 + value_bit_size(exponent, "nat") + exponent + 1
                if gas + minimum_cost > fuel:
                    return {"status": "FAULT", "reason": "OUT_OF_GAS", "gas": gas, "dispatches": dispatches}
                writes = [(instruction["dst"], 1 << exponent)]
            elif op == "length":
                reads = [instruction["src"]]
                writes = [(instruction["dst"], len(registers[instruction["src"]]))]
            elif op == "parity":
                reads = [instruction["src"]]
                writes = [(instruction["dst"], sum(byte.bit_count() for byte in registers[instruction["src"]]) & 1)]
            elif op == "bytes_to_nat":
                reads = [instruction["src"]]
                writes = [(instruction["dst"], int.from_bytes(registers[instruction["src"]], "big"))]
            elif op == "get_bit":
                reads = [instruction["src"], instruction["index"]]
                payload = registers[instruction["src"]]
                index = registers[instruction["index"]]
                if index >= 8 * len(payload):
                    bit = 0
                else:
                    bit = (payload[len(payload) - 1 - index // 8] >> (index % 8)) & 1
                writes = [(instruction["dst"], bit)]
            elif op == "concat":
                reads = [instruction["left"], instruction["right"]]
                writes = [(instruction["dst"], registers[instruction["left"]] + registers[instruction["right"]])]
            elif op == "slice":
                reads = [instruction["src"], instruction["start"], instruction["length"]]
                start = registers[instruction["start"]]
                length = registers[instruction["length"]]
                writes = [(instruction["dst"], registers[instruction["src"]][start : start + length])]
            elif op == "json_encode":
                reads = [instruction["src"]]
                writes = [(instruction["dst"], canonical_bytes(registers[instruction["src"]]))]
            elif op == "json_decode":
                reads = [instruction["src"]]
                writes = [(instruction["dst"], parse_canonical_json_value(registers[instruction["src"]]))]
            elif op == "bounded_halts":
                reads = [instruction["input"], instruction["steps"]]
                base_cost = 1 + sum(value_bit_size(registers[index], register_types[index]) for index in reads) + 1
                simulation_limit = fuel - gas - base_cost
                if simulation_limit < 0:
                    return {"status": "FAULT", "reason": "OUT_OF_GAS", "gas": gas, "dispatches": dispatches}
                halted, simulation_gas = bounded_halts_utm_v1(
                    instruction["machine_index"],
                    registers[instruction["input"]],
                    registers[instruction["steps"]],
                    gas_limit=simulation_limit,
                )
                extra_gas = simulation_gas
                writes = [(instruction["dst"], int(halted))]
            elif op == "jump":
                next_pc = instruction["target"]
            elif op == "branch":
                reads = [instruction["cond"]]
                next_pc = instruction["if_true"] if registers[instruction["cond"]] else instruction["if_false"]
            elif op == "return":
                reads = [instruction["src"]]
            elif op == "fault":
                instruction_cost = 1
                if gas + instruction_cost > fuel:
                    return {"status": "FAULT", "reason": "OUT_OF_GAS", "gas": gas, "dispatches": dispatches}
                return {"status": "FAULT", "reason": instruction["code"], "gas": gas + instruction_cost, "dispatches": dispatches}
            else:
                raise ExecutionFault("unknown opcode")
        except OutOfGas:
            return {"status": "FAULT", "reason": "OUT_OF_GAS", "gas": gas, "dispatches": dispatches}
        except (GrammarError, ExecutionFault, OverflowError, MemoryError, ValueError, TypeError) as exc:
            return {"status": "FAULT", "reason": f"RUNTIME_{type(exc).__name__.upper()}", "gas": gas, "dispatches": dispatches}
        read_cost = sum(value_bit_size(registers[index], register_types[index]) for index in reads)
        write_cost = sum(value_bit_size(value, register_types[index]) for index, value in writes)
        instruction_cost = 1 + read_cost + write_cost + extra_gas
        if gas + instruction_cost > fuel:
            return {"status": "FAULT", "reason": "OUT_OF_GAS", "gas": gas, "dispatches": dispatches}
        gas += instruction_cost
        for index, value in writes:
            if not _runtime_type(value, register_types[index]):
                return {"status": "FAULT", "reason": "OUTPUT_TYPE", "gas": gas, "dispatches": dispatches}
            registers[index] = value
        if op == "return":
            result = registers[instruction["src"]]
            if not _runtime_type(result, output):
                return {"status": "FAULT", "reason": "RETURN_TYPE", "gas": gas, "dispatches": dispatches}
            return {"status": "HALT", "value": result, "gas": gas, "dispatches": dispatches}
        pc = next_pc


def _exact_keys(value: object, expected: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GrammarError(f"{path} must be an object")
    actual = set(value)
    if actual != expected:
        raise GrammarError(f"{path} keys mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    return value


def _identifier(value: object, path: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise GrammarError(f"invalid identifier at {path}")
    return value


def _nat(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise GrammarError(f"{path} must be a nonnegative integer")
    return value


def _rational(value: object, path: str) -> dict[str, int]:
    result = _exact_keys(value, {"num", "den"}, path)
    num = _nat(result["num"], f"{path}.num")
    den = _nat(result["den"], f"{path}.den")
    if den == 0 or math.gcd(num, den) != 1:
        raise GrammarError(f"{path} must be a coprime rational with positive denominator")
    return {"num": num, "den": den}


def load_grammar() -> dict[str, Any]:
    return json.loads(GRAMMAR_PATH.read_text(encoding="utf-8"))


def _signature(value: object, path: str) -> tuple[tuple[str, ...], str]:
    result = _exact_keys(value, {"inputs", "output"}, path)
    inputs = result["inputs"]
    output = result["output"]
    if not isinstance(inputs, list) or not all(item in VALUE_TYPES for item in inputs):
        raise GrammarError(f"invalid inputs at {path}")
    if output not in VALUE_TYPES:
        raise GrammarError(f"invalid output at {path}")
    return tuple(inputs), output


def _reg_type(registers: list[str], index: object, expected: str | None, path: str) -> str:
    position = _nat(index, path)
    if position >= len(registers):
        raise GrammarError(f"register out of range at {path}")
    actual = registers[position]
    if expected is not None and actual != expected:
        raise GrammarError(f"register type mismatch at {path}: expected {expected}, got {actual}")
    return actual


def _instruction_keys(instruction: dict[str, Any], required: set[str], path: str) -> None:
    if set(instruction) != required | {"op"}:
        raise GrammarError(f"instruction keys mismatch at {path}")


def _validate_instruction(instruction: object, registers: list[str], count: int, path: str) -> None:
    if not isinstance(instruction, dict) or not isinstance(instruction.get("op"), str):
        raise GrammarError(f"invalid instruction at {path}")
    op = instruction["op"]
    if op == "const_bit":
        _instruction_keys(instruction, {"dst", "value"}, path)
        _reg_type(registers, instruction["dst"], "bit", path + ".dst")
        if instruction["value"] not in (0, 1) or isinstance(instruction["value"], bool):
            raise GrammarError(f"invalid bit at {path}.value")
    elif op == "const_nat":
        _instruction_keys(instruction, {"dst", "value"}, path)
        _reg_type(registers, instruction["dst"], "nat", path + ".dst")
        _nat(instruction["value"], path + ".value")
    elif op == "const_bytes":
        _instruction_keys(instruction, {"dst", "hex"}, path)
        _reg_type(registers, instruction["dst"], "bytes", path + ".dst")
        encoded = instruction["hex"]
        if not isinstance(encoded, str) or len(encoded) % 2 or not re.fullmatch(r"[0-9A-F]*", encoded):
            raise GrammarError(f"invalid canonical hex at {path}.hex")
    elif op == "const_rational":
        _instruction_keys(instruction, {"dst", "value"}, path)
        _reg_type(registers, instruction["dst"], "rational", path + ".dst")
        _rational(instruction["value"], path + ".value")
    elif op == "const_json":
        _instruction_keys(instruction, {"dst", "value"}, path)
        _reg_type(registers, instruction["dst"], "json", path + ".dst")
        _validate_json_domain(instruction["value"], path + ".value")
    elif op == "copy":
        _instruction_keys(instruction, {"dst", "src"}, path)
        dst = _reg_type(registers, instruction["dst"], None, path + ".dst")
        src = _reg_type(registers, instruction["src"], None, path + ".src")
        if dst != src:
            raise GrammarError(f"copy type mismatch at {path}")
    elif op in {"eq", "lt", "add", "sub_sat", "mul"}:
        _instruction_keys(instruction, {"dst", "left", "right"}, path)
        output_type = "bit" if op in {"eq", "lt"} else "nat"
        input_type = None if op == "eq" else "nat"
        _reg_type(registers, instruction["dst"], output_type, path + ".dst")
        left = _reg_type(registers, instruction["left"], input_type, path + ".left")
        right = _reg_type(registers, instruction["right"], input_type, path + ".right")
        if op == "eq" and left != right:
            raise GrammarError(f"equality type mismatch at {path}")
    elif op == "pow2":
        _instruction_keys(instruction, {"dst", "exponent"}, path)
        _reg_type(registers, instruction["dst"], "nat", path + ".dst")
        _reg_type(registers, instruction["exponent"], "nat", path + ".exponent")
    elif op in {"length", "parity", "bytes_to_nat"}:
        _instruction_keys(instruction, {"dst", "src"}, path)
        _reg_type(registers, instruction["dst"], "bit" if op == "parity" else "nat", path + ".dst")
        _reg_type(registers, instruction["src"], "bytes", path + ".src")
    elif op == "get_bit":
        _instruction_keys(instruction, {"dst", "src", "index"}, path)
        _reg_type(registers, instruction["dst"], "bit", path + ".dst")
        _reg_type(registers, instruction["src"], "bytes", path + ".src")
        _reg_type(registers, instruction["index"], "nat", path + ".index")
    elif op == "concat":
        _instruction_keys(instruction, {"dst", "left", "right"}, path)
        for key in ("dst", "left", "right"):
            _reg_type(registers, instruction[key], "bytes", path + "." + key)
    elif op == "slice":
        _instruction_keys(instruction, {"dst", "src", "start", "length"}, path)
        _reg_type(registers, instruction["dst"], "bytes", path + ".dst")
        _reg_type(registers, instruction["src"], "bytes", path + ".src")
        _reg_type(registers, instruction["start"], "nat", path + ".start")
        _reg_type(registers, instruction["length"], "nat", path + ".length")
    elif op == "json_encode":
        _instruction_keys(instruction, {"dst", "src"}, path)
        _reg_type(registers, instruction["dst"], "bytes", path + ".dst")
        _reg_type(registers, instruction["src"], "json", path + ".src")
    elif op == "json_decode":
        _instruction_keys(instruction, {"dst", "src"}, path)
        _reg_type(registers, instruction["dst"], "json", path + ".dst")
        _reg_type(registers, instruction["src"], "bytes", path + ".src")
    elif op == "bounded_halts":
        _instruction_keys(instruction, {"dst", "machine_index", "input", "steps"}, path)
        _reg_type(registers, instruction["dst"], "bit", path + ".dst")
        _nat(instruction["machine_index"], path + ".machine_index")
        _reg_type(registers, instruction["input"], "bytes", path + ".input")
        _reg_type(registers, instruction["steps"], "nat", path + ".steps")
    elif op == "jump":
        _instruction_keys(instruction, {"target"}, path)
        target = _nat(instruction["target"], path + ".target")
        if target >= count:
            raise GrammarError(f"jump target out of range at {path}")
    elif op == "branch":
        _instruction_keys(instruction, {"cond", "if_true", "if_false"}, path)
        _reg_type(registers, instruction["cond"], "bit", path + ".cond")
        for key in ("if_true", "if_false"):
            if _nat(instruction[key], path + "." + key) >= count:
                raise GrammarError(f"branch target out of range at {path}.{key}")
    elif op == "return":
        _instruction_keys(instruction, {"src"}, path)
        _reg_type(registers, instruction["src"], None, path + ".src")
    elif op == "fault":
        _instruction_keys(instruction, {"code"}, path)
        _identifier(instruction["code"], path + ".code")
    else:
        raise GrammarError(f"unknown opcode at {path}: {op}")


def validate_program(program: object, grammar: dict[str, Any]) -> tuple[str, tuple[tuple[str, ...], str]]:
    if not isinstance(program, dict):
        raise GrammarError("program must be an object")
    kind = program.get("kind")
    if kind == "ir":
        _exact_keys(program, {"id", "kind", "inputs", "output", "registers", "instructions"}, "program")
    elif kind == "builtin":
        _exact_keys(program, {"id", "kind", "inputs", "output", "builtin", "params"}, "program")
    else:
        raise GrammarError("program.kind must be ir or builtin")
    program_id = _identifier(program["id"], "program.id")
    inputs, output = _signature({"inputs": program["inputs"], "output": program["output"]}, f"program[{program_id}].signature")
    if kind == "builtin":
        builtin = program["builtin"]
        builtins = grammar["builtin_programs"]
        if builtin not in builtins:
            raise GrammarError(f"unknown builtin in {program_id}")
        expected = _signature(grammar["component_signatures"][builtins[builtin]], f"builtin[{builtin}]")
        if (inputs, output) != expected:
            raise GrammarError(f"builtin signature mismatch in {program_id}")
        params = program["params"]
        if not isinstance(params, dict):
            raise GrammarError(f"builtin params must be object in {program_id}")
        _validate_json_domain(params, f"program[{program_id}].params")
        if builtin in {"V2_21_IDEAL_ORACLE_V1", "ATOM_COORDINATE_COST_V1", "COORDINATE_REFUTE_V1"}:
            _exact_keys(params, {"machine_index"}, f"program[{program_id}].params")
            _nat(params["machine_index"], f"program[{program_id}].params.machine_index")
        elif params:
            raise GrammarError(f"builtin {builtin} takes no params")
    else:
        registers = program["registers"]
        instructions = program["instructions"]
        if not isinstance(registers, list) or not registers or not all(item in VALUE_TYPES for item in registers):
            raise GrammarError(f"invalid register types in {program_id}")
        if tuple(registers[: len(inputs)]) != inputs:
            raise GrammarError(f"input registers do not match signature in {program_id}")
        if not isinstance(instructions, list) or not instructions:
            raise GrammarError(f"empty instruction list in {program_id}")
        for index, instruction in enumerate(instructions):
            _validate_instruction(instruction, registers, len(instructions), f"program[{program_id}].instructions[{index}]")
            if isinstance(instruction, dict) and instruction.get("op") == "return":
                if registers[instruction["src"]] != output:
                    raise GrammarError(f"return type mismatch in {program_id}")
        if not any(isinstance(item, dict) and item.get("op") == "return" for item in instructions):
            raise GrammarError(f"program has no return in {program_id}")
    return program_id, (inputs, output)


def _program_ref(programs: dict[str, tuple[tuple[str, ...], str]], ref: object, component: str, grammar: dict[str, Any], path: str) -> str:
    program_id = _identifier(ref, path)
    if program_id not in programs:
        raise GrammarError(f"unknown program reference at {path}")
    expected = _signature(grammar["component_signatures"][component], f"component[{component}]")
    if programs[program_id] != expected:
        raise GrammarError(f"component signature mismatch at {path}")
    return program_id


def validate_instance(instance: object) -> None:
    value = _exact_keys(instance, INSTANCE_KEYS, "instance")
    grammar = load_grammar()
    constants = {
        "schema_version": "asmp3_machine_instance_v0_3",
        "problem_id": "ASMP-3",
        "problem_version": "ASMP-3-MACHINE-v0.3",
        "codec": "ASMP3-CANONICAL-JSON-v0.3",
        "universal_machine": "WV-IR-v0.3",
        "membership_semantics": "WV-MEMBERSHIP-v0.3",
    }
    for key, expected in constants.items():
        if value[key] != expected:
            raise GrammarError(f"invalid {key}")
    family_id = value["family_id"]
    if not isinstance(family_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,127}", family_id):
        raise GrammarError("invalid family_id")
    mode = value["interface_mode"]
    if mode not in {"FIX", "ADM"}:
        raise GrammarError("invalid interface_mode")
    scale = _exact_keys(value["scale"], {"parameter", "minimum"}, "scale")
    if scale["parameter"] != "n" or _nat(scale["minimum"], "scale.minimum") < 2:
        raise GrammarError("scale must be n>=2")

    raw_programs = value["programs"]
    if not isinstance(raw_programs, list) or not raw_programs:
        raise GrammarError("programs must be a nonempty list")
    programs: dict[str, tuple[tuple[str, ...], str]] = {}
    program_order: list[str] = []
    for raw in raw_programs:
        program_id, signature = validate_program(raw, grammar)
        if program_id in programs:
            raise GrammarError(f"duplicate program id: {program_id}")
        programs[program_id] = signature
        program_order.append(program_id)
    if program_order != sorted(program_order):
        raise GrammarError("program table must be sorted by id")

    environment = _exact_keys(value["environment"], ENVIRONMENT_KEYS, "environment")
    domains = _exact_keys(environment["domains"], {"public_instance_valid", "world_valid", "output_valid"}, "environment.domains")
    _program_ref(programs, domains["public_instance_valid"], "public_instance_valid", grammar, "environment.domains.public_instance_valid")
    _program_ref(programs, domains["world_valid"], "world_valid", grammar, "environment.domains.world_valid")
    _program_ref(programs, domains["output_valid"], "output_valid", grammar, "environment.domains.output_valid")
    _program_ref(programs, environment["decision_relation"], "decision_relation", grammar, "environment.decision_relation")
    atoms = _exact_keys(environment["atoms"], {"valid", "description_length_bound", "locality_bound", "evaluation_cost_bound"}, "environment.atoms")
    _program_ref(programs, atoms["valid"], "atom_valid", grammar, "environment.atoms.valid")
    _program_ref(programs, atoms["description_length_bound"], "atom_description_bound", grammar, "environment.atoms.description_length_bound")
    _program_ref(programs, atoms["locality_bound"], "atom_locality_bound", grammar, "environment.atoms.locality_bound")
    _program_ref(programs, atoms["evaluation_cost_bound"], "atom_evaluation_cost", grammar, "environment.atoms.evaluation_cost_bound")
    replications = _exact_keys(environment["replications"], {"valid", "equivalent"}, "environment.replications")
    _program_ref(programs, replications["valid"], "replication_valid", grammar, "environment.replications.valid")
    _program_ref(programs, replications["equivalent"], "replication_equivalent", grammar, "environment.replications.equivalent")
    _program_ref(programs, environment["ideal_oracle"], "ideal_oracle", grammar, "environment.ideal_oracle")
    noise = _exact_keys(environment["noise"], {"model_id", "legal_process", "transition_kernel", "marginal_eta"}, "environment.noise")
    _identifier(noise["model_id"], "environment.noise.model_id")
    _program_ref(programs, noise["legal_process"], "noise_legal", grammar, "environment.noise.legal_process")
    _program_ref(programs, noise["transition_kernel"], "noise_transition_kernel", grammar, "environment.noise.transition_kernel")
    eta = _rational(noise["marginal_eta"], "environment.noise.marginal_eta")
    if 2 * eta["num"] >= eta["den"]:
        raise GrammarError("marginal_eta must be less than one half")
    information = _exact_keys(environment["information"], {"prover_view", "verifier_view"}, "environment.information")
    _program_ref(programs, information["prover_view"], "information_prover", grammar, "environment.information.prover_view")
    _program_ref(programs, information["verifier_view"], "information_verifier", grammar, "environment.information.verifier_view")
    _program_ref(programs, environment["prover_budget"], "prover_budget", grammar, "environment.prover_budget")

    raw_interfaces = value["interfaces"]
    if not isinstance(raw_interfaces, list) or not raw_interfaces:
        raise GrammarError("interfaces must be nonempty")
    interface_ids: list[str] = []
    for index, raw_interface in enumerate(raw_interfaces):
        interface = _exact_keys(raw_interface, INTERFACE_KEYS, f"interfaces[{index}]")
        interface_id = _identifier(interface["id"], f"interfaces[{index}].id")
        if interface_id in interface_ids:
            raise GrammarError("duplicate interface id")
        interface_ids.append(interface_id)
        refs = {
            "message_valid": "interface_message_valid",
            "order": "interface_order",
            "stop": "interface_stop",
            "verifier_time_bound": "interface_resource_bound",
            "semantic_query_bound": "interface_resource_bound",
            "transcript_bit_bound": "interface_resource_bound",
            "malformed": "interface_malformed",
            "payoff": "interface_payoff",
            "refute": "interface_refute",
        }
        for field, component in refs.items():
            _program_ref(programs, interface[field], component, grammar, f"interfaces[{index}].{field}")
        serialization = _exact_keys(interface["serialization"], {"codec", "aliases", "padding"}, f"interfaces[{index}].serialization")
        if serialization != {"codec": "ASMP3-CANONICAL-JSON-v0.3", "aliases": False, "padding": False}:
            raise GrammarError("interface serialization must be canonical and alias-free")
    if interface_ids != sorted(interface_ids):
        raise GrammarError("interface table must be sorted by id")

    if mode == "FIX":
        fixed = _identifier(value["fixed_interface"], "fixed_interface")
        if fixed not in interface_ids or value["admissible_interfaces"] is not None:
            raise GrammarError("FIX requires one named fixed interface and null admissible_interfaces")
    else:
        if value["fixed_interface"] is not None:
            raise GrammarError("ADM requires null fixed_interface")
        admissible = _exact_keys(value["admissible_interfaces"], {"kind", "interface_ids"}, "admissible_interfaces")
        if admissible["kind"] != "finite" or not isinstance(admissible["interface_ids"], list) or not admissible["interface_ids"]:
            raise GrammarError("v0.3 ADM requires a nonempty finite interface catalog")
        if admissible["interface_ids"] != sorted(set(admissible["interface_ids"])) or not set(admissible["interface_ids"]).issubset(interface_ids):
            raise GrammarError("invalid ADM interface catalog")

    provenance = _exact_keys(value["provenance"], {"canonical_sha256", "typed_successor_sha256", "v2_21_theorem_sha256", "v2_21_artifact_sha256"}, "provenance")
    for key, digest in provenance.items():
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9A-F]{64}", digest):
            raise GrammarError(f"invalid provenance hash: {key}")


def _builtin(program_id: str, builtin: str, component: str, params: dict[str, object] | None = None) -> dict[str, object]:
    grammar = load_grammar()
    signature = grammar["component_signatures"][component]
    return {
        "id": program_id,
        "kind": "builtin",
        "inputs": signature["inputs"],
        "output": signature["output"],
        "builtin": builtin,
        "params": {} if params is None else params,
    }


def compile_v2_21_instance(machine_index: int, mode: str) -> dict[str, Any]:
    _nat(machine_index, "machine_index")
    if mode not in {"FIX", "ADM"}:
        raise GrammarError("mode must be FIX or ADM")
    programs = [
        _builtin("ATOM_DESC_BOUND", "ATOM_COORDINATE_BOUND_V1", "atom_description_bound"),
        _builtin("ATOM_EVAL_COST", "ATOM_COORDINATE_COST_V1", "atom_evaluation_cost", {"machine_index": machine_index}),
        _builtin("ATOM_LOCALITY", "ATOM_COORDINATE_LOCALITY_V1", "atom_locality_bound"),
        _builtin("ATOM_VALID", "ATOM_COORDINATE_VALID_V1", "atom_valid"),
        _builtin("DECISION_RELATION", "PARITY_RELATION_V1", "decision_relation"),
        _builtin("IDEAL_ORACLE", "V2_21_IDEAL_ORACLE_V1", "ideal_oracle", {"machine_index": machine_index}),
        _builtin("INFO_PROVER", "PROVER_FULL_WORLD_VIEW_V1", "information_prover"),
        _builtin("INFO_VERIFIER", "VERIFIER_PUBLIC_VIEW_V1", "information_verifier"),
        _builtin("MALFORMED", "MALFORMED_LOSES_V1", "interface_malformed"),
        _builtin("MESSAGE_VALID", "VECTOR_MESSAGE_VALID_V1", "interface_message_valid"),
        _builtin("NOISE_KERNEL", "BSC_ONE_FIFTH_KERNEL_V1", "noise_transition_kernel"),
        _builtin("NOISE_LEGAL", "NOISE_EXACT_BSC_LEGAL_V1", "noise_legal"),
        _builtin("ORDER", "VECTOR_ORDER_V1", "interface_order"),
        _builtin("OUTPUT_VALID", "OUTPUT_BIT_VALID_V1", "output_valid"),
        _builtin("PAYOFF", "CLAIM_SELECTION_PAYOFF_V1", "interface_payoff"),
        _builtin("PROVER_BUDGET", "WV_PROVER_EXP_BUDGET_V1", "prover_budget"),
        _builtin("PUBLIC_VALID", "PUBLIC_BYTES_VALID_V1", "public_instance_valid"),
        _builtin("QUERY_BOUND", "WV_LINEAR_QUERY_BOUND_V1", "interface_resource_bound"),
        _builtin("REFUTE", "COORDINATE_REFUTE_V1", "interface_refute", {"machine_index": machine_index}),
        _builtin("REPLICATION_EQUIV", "IDENTITY_REPLICATION_EQUIVALENT_V1", "replication_equivalent"),
        _builtin("REPLICATION_VALID", "IDENTITY_REPLICATION_VALID_V1", "replication_valid"),
        _builtin("STOP", "SINGLE_RESPONSE_STOP_V1", "interface_stop"),
        _builtin("TIME_BOUND", "WV_LINEAR_TIME_BOUND_V1", "interface_resource_bound"),
        _builtin("TRANSCRIPT_BOUND", "WV_LINEAR_TRANSCRIPT_BOUND_V1", "interface_resource_bound"),
        _builtin("WORLD_VALID", "WORLD_D_BITS_VALID_V1", "world_valid"),
    ]
    programs.sort(key=lambda program: program["id"])
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
    instance = {
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
            "canonical_sha256": sha256(CANONICAL_PATH),
            "typed_successor_sha256": sha256(TYPED_JSON_PATH),
            "v2_21_theorem_sha256": sha256(V2_21_THEOREM_PATH),
            "v2_21_artifact_sha256": sha256(V2_21_ARTIFACT_PATH),
        },
    }
    validate_instance(instance)
    return instance


def malformed_fixtures(valid_instance: dict[str, Any]) -> list[dict[str, object]]:
    canonical = canonical_bytes(valid_instance)
    duplicate = canonical.replace(b'{"admissible_interfaces"', b'{"schema_version":"asmp3_machine_instance_v0_3","admissible_interfaces"', 1)
    fixtures: list[tuple[str, bytes]] = [
        ("pretty_printed", json.dumps(valid_instance, indent=2, sort_keys=True).encode()),
        ("trailing_newline", canonical + b"\n"),
        ("utf8_bom", b"\xef\xbb\xbf" + canonical),
        ("duplicate_key", duplicate),
        ("floating_number", canonical.replace(b'"minimum":2', b'"minimum":2.0')),
    ]
    rows = []
    for name, payload in fixtures:
        rejected = False
        reason = ""
        try:
            parse_canonical_bytes(payload)
        except GrammarError as exc:
            rejected = True
            reason = str(exc)
        rows.append({"fixture": name, "bytes": len(payload), "rejected": rejected, "reason": reason})
    return rows


def reference_runtime_audit() -> dict[str, object]:
    halt_table = [(None, symbol, 1) for symbol in range(4)]
    loop_table = [(0, symbol, 1) for symbol in range(4)]
    halt_index = encode_utm_v1(1, 0, halt_table)
    loop_index = encode_utm_v1(1, 0, loop_table)
    halt_result, halt_gas = bounded_halts_utm_v1(halt_index, b"A", 1)
    loop_result, loop_gas = bounded_halts_utm_v1(loop_index, b"A", 32)
    invalid_result, invalid_gas = bounded_halts_utm_v1(0, b"", 32)
    countdown = {
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
    countdown_ok = execute_ir(countdown, [19], 100_000)
    countdown_fault = execute_ir(countdown, [19], 10)
    checks = {
        "one_state_halting_machine_halts_in_one_step": halt_result is True and halt_gas > 0,
        "one_state_loop_machine_does_not_halt_in_thirty_two_steps": loop_result is False and loop_gas > halt_gas,
        "invalid_machine_code_halts_at_step_zero": invalid_result is True and invalid_gas > 0,
        "Minsky_countdown_returns_zero": countdown_ok["status"] == "HALT" and countdown_ok["value"] == 0 and countdown_ok["gas"] > 0,
        "insufficient_fuel_faults": countdown_fault["status"] == "FAULT" and countdown_fault["reason"] == "OUT_OF_GAS",
    }
    return {
        "halt_machine_index": str(halt_index),
        "loop_machine_index": str(loop_index),
        "halt_gas": halt_gas,
        "loop_gas": loop_gas,
        "invalid_gas": invalid_gas,
        "countdown_success": countdown_ok,
        "countdown_low_fuel": countdown_fault,
        "checks": checks,
        "certified": all(checks.values()),
    }


def build_artifact() -> dict[str, object]:
    grammar = load_grammar()
    grammar_hash = sha256(GRAMMAR_PATH)
    source_hashes = {
        "canonical_sha256": sha256(CANONICAL_PATH),
        "registry_sha256": sha256(REGISTRY_PATH),
        "typed_markdown_sha256": sha256(TYPED_MD_PATH),
        "typed_json_sha256": sha256(TYPED_JSON_PATH),
        "v2_21_theorem_sha256": sha256(V2_21_THEOREM_PATH),
        "v2_21_artifact_sha256": sha256(V2_21_ARTIFACT_PATH),
        "v2_21_verification_sha256": sha256(V2_21_VERIFY_PATH),
        "v2_21_manifest_sha256": sha256(V2_21_MANIFEST_PATH),
        "grammar_sha256": grammar_hash,
    }
    compiled_rows = []
    fixture_indices = (0, 1, 2, 5, 17, 64, 999)
    for machine_index in fixture_indices:
        for mode in ("FIX", "ADM"):
            instance = compile_v2_21_instance(machine_index, mode)
            encoded = canonical_bytes(instance)
            decoded = parse_canonical_bytes(encoded)
            compiled_rows.append(
                {
                    "machine_index": machine_index,
                    "mode": mode,
                    "bytes": len(encoded),
                    "sha256": hashlib.sha256(encoded).hexdigest().upper(),
                    "round_trip_equal": decoded == instance,
                    "fixed_interface": decoded["fixed_interface"],
                    "admissible_interfaces": decoded["admissible_interfaces"],
                    "certified": decoded == instance,
                }
            )
    invalid_rows = malformed_fixtures(compile_v2_21_instance(17, "FIX"))
    runtime = reference_runtime_audit()
    source = " ".join(CANONICAL_PATH.read_text(encoding="utf-8").split())
    source_markers = {
        "closed_core_requires_encodings": "Objects, domains, encodings, resource bounds, randomness, adversaries, and quantifier order are explicit" in source,
        "standard_encodings_required": "standard encodings of computation, probability, and analysis" in source,
        "ASMP3_frozen_fields_present": "freeze a decision relation `R_n`; a public-coin message order and stopping rule" in source,
        "complete_noise_required": "a complete correlation/adaptivity class" in source,
        "honest_efficiency_required": "The honest prover must itself have an efficient strategy" in source,
        "encoding_invariance_required": "a complete solution must prove that encoding invariance rather than assume it from syntax alone" in source,
    }
    gates = {
        "M0_all_nine_inputs_hashed": len(source_hashes) == 9 and all(len(value) == 64 for value in source_hashes.values()),
        "M1_source_machine_closure_markers_hold": all(source_markers.values()),
        "M2_codec_has_all_twelve_canonicality_fields": len(grammar["canonical_codec"]) == 12 and grammar["canonical_codec"]["allow_duplicate_keys"] is False and grammar["canonical_codec"]["allow_float"] is False,
        "M3_universal_IR_has_twenty_five_typed_opcodes_and_bit_cost": len(grammar["universal_machine"]["opcodes"]) == 25 and "bit-cost" in grammar["universal_machine"]["cost_model"],
        "M4_all_twenty_three_component_signatures_registered": len(grammar["component_signatures"]) == 23,
        "M5_all_twenty_five_builtin_semantics_registered": len(grammar["builtin_programs"]) == 25,
        "M6_all_fourteen_FIX_ADM_compiler_rows_round_trip": len(compiled_rows) == 14 and all(row["certified"] for row in compiled_rows),
        "M7_all_five_noncanonical_byte_fixtures_rejected": len(invalid_rows) == 5 and all(row["rejected"] for row in invalid_rows),
        "M8_FIX_and_ADM_quantifier_locations_are_machine_distinct": all(row["fixed_interface"] == "G_VEC" and row["admissible_interfaces"] is None for row in compiled_rows if row["mode"] == "FIX") and all(row["fixed_interface"] is None and row["admissible_interfaces"] == {"kind": "finite", "interface_ids": ["G_VEC"]} for row in compiled_rows if row["mode"] == "ADM"),
        "M9_v2_21_compiler_image_is_in_machine_grammar_domain": all(row["certified"] for row in compiled_rows) and json.loads(V2_21_ARTIFACT_PATH.read_text(encoding="utf-8"))["certified"] is True,
        "M10_reference_IR_gas_and_U_TM_execution_checks_pass": runtime["certified"] and len(runtime["checks"]) == 5,
    }
    return {
        "schema_version": "asmp3_machine_grammar_artifact_v0_3",
        "experiment_id": "ASMP-3-MACHINE-GRAMMAR-v0.3",
        "status": "executable_nonnormative_successor_machine_grammar",
        "source_hashes": source_hashes,
        "source_markers": source_markers,
        "grammar_summary": {
            "codec": grammar["canonical_codec"]["id"],
            "universal_machine": grammar["universal_machine"]["id"],
            "membership_semantics": grammar["membership_semantics"]["id"],
            "component_signatures": len(grammar["component_signatures"]),
            "builtins": len(grammar["builtin_programs"]),
            "opcodes": len(grammar["universal_machine"]["opcodes"]),
        },
        "compiled_rows": compiled_rows,
        "malformed_rows": invalid_rows,
        "reference_runtime_audit": runtime,
        "resolution_effect": {
            "v0_1_silently_amended": False,
            "successor_problem_created": "ASMP-3-MACHINE-v0.3",
            "v2_21_reduction_compiles": True,
            "membership_under_successor": "undecidable for FIX and ADM by the v2.21 NONHALT reduction",
            "remaining_external_reproductions": "0/2",
        },
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": "The parser and compiler close the machine grammar for a successor proposal. They do not establish authorial adoption of v0.3 or provide external expert reproduction.",
    }


def write_artifact() -> dict[str, object]:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    EXAMPLE_FIX_PATH.write_bytes(canonical_bytes(compile_v2_21_instance(17, "FIX")))
    EXAMPLE_ADM_PATH.write_bytes(canonical_bytes(compile_v2_21_instance(17, "ADM")))
    return artifact
