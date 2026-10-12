from __future__ import annotations

import json
from itertools import combinations, product
from math import ceil, log2
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "encoding_invariance_v2_0.json"
OUTPUT_PATH = HERE / "artifacts" / "encoding_invariance_verification_v2_0.json"
PARENT_PATH = (
    HERE.parent
    / "asmp3_block_selection_composition_v1_9"
    / "artifacts"
    / "block_selection_composition_v1_9.json"
)
REPLICATION_PATH = (
    HERE.parent
    / "asmp3_independent_noise_amplification_v1_8"
    / "artifacts"
    / "independent_noise_amplification_v1_8.json"
)


def task(class_count: int, levels: tuple[int, ...]):
    universe = tuple(range(class_count))
    return {
        f"tau_{index}": tuple(
            frozenset(candidate) for candidate in combinations(universe, level)
        )
        for index, level in enumerate(levels)
    }


def minima(witnesses):
    return {
        transcript: min(len(witness) for witness in family)
        for transcript, family in witnesses.items()
    }


def dimension(witnesses) -> int:
    return max(minima(witnesses).values())


def transport(witnesses, class_map, transcript_map):
    return {
        transcript_map[transcript]: tuple(
            frozenset(class_map[item] for item in witness)
            for witness in family
        )
        for transcript, family in witnesses.items()
    }


def canonical(witnesses):
    result = {}
    for transcript, family in witnesses.items():
        size = min(len(witness) for witness in family)
        result[transcript] = min(
            tuple(sorted(witness)) for witness in family if len(witness) == size
        )
    return result


def reconstruct_transport_rows() -> list[dict[str, object]]:
    rows = []
    for class_count in range(2, 11):
        profiles = (
            (1, class_count),
            (max(1, class_count // 2), max(1, class_count - 1)),
            tuple(range(1, min(class_count, 4) + 1)),
        )
        for profile_id, levels in enumerate(profiles):
            source = task(class_count, levels)
            transcript_names = tuple(source)
            class_map = {item: (item + 1) % class_count for item in range(class_count)}
            transcript_map = {
                name: f"encoded_{len(transcript_names) - 1 - index}"
                for index, name in enumerate(transcript_names)
            }
            encoded = transport(source, class_map, transcript_map)
            aliases = tuple(
                1 + ((item + profile_id) % 3) for item in range(class_count)
            )
            source_canonical = canonical(source)
            witness_transport = all(
                frozenset(class_map[item] for item in source_canonical[name])
                in encoded[transcript_map[name]]
                for name in source
            )
            rows.append(
                {
                    "class_count": class_count,
                    "profile_id": profile_id,
                    "transcript_levels": list(levels),
                    "source_transcript_minima": minima(source),
                    "encoded_transcript_minima": minima(encoded),
                    "source_dimension": dimension(source),
                    "encoded_dimension": dimension(encoded),
                    "alias_multiplicities": list(aliases),
                    "raw_alias_alphabet_size": sum(aliases),
                    "semantic_class_count": class_count,
                    "canonical_witness_transport_holds": witness_transport,
                    "encoded_search_witnesses": {
                        key: list(value) for key, value in canonical(encoded).items()
                    },
                    "dimension_invariant": dimension(source) == dimension(encoded),
                    "certified": (
                        dimension(source) == dimension(encoded)
                        and witness_transport
                        and sum(aliases) >= class_count
                    ),
                }
            )
    return rows


def raw_minimum(class_count: int, level: int) -> tuple[int, int]:
    multiplicities = tuple(1 + (item % 2) for item in range(class_count))
    alias_to_class = {
        f"c{item}_alias{alias}": item
        for item, count in enumerate(multiplicities)
        for alias in range(count)
    }
    raw = tuple(alias_to_class)
    target_family = task(class_count, (level,))["tau_0"]
    for size in range(len(raw) + 1):
        for candidate in combinations(raw, size):
            projected = {alias_to_class[atom] for atom in candidate}
            if any(witness <= projected for witness in target_family):
                return len(raw), size
    raise RuntimeError("no raw witness")


def parity_row(bit_count: int) -> dict[str, object]:
    ambiguous = 0
    holds = True
    for partial in product((-1, 0, 1), repeat=bit_count):
        if -1 not in partial:
            continue
        ambiguous += 1
        pivot = partial.index(-1)
        left = [0 if value == -1 else value for value in partial]
        right = list(left)
        right[pivot] = 1
        holds = holds and (sum(left) % 2 != sum(right) % 2)
    expected = 3**bit_count - 2**bit_count
    budget = ceil(log2(bit_count + 1))
    return {
        "bit_count": bit_count,
        "ambiguous_partial_assignments_checked": ambiguous,
        "ambiguous_partial_assignment_formula": expected,
        "every_nonterminal_partial_assignment_ambiguous": holds,
        "pivotal_bits": bit_count,
        "exact_deterministic_query_complexity": bit_count,
        "base_refutation_dimension": bit_count,
        "macro_refutation_dimension": 1,
        "macro_evaluation_cost": bit_count,
        "declared_local_atom_evaluation_budget": budget,
        "macro_within_declared_budget": bit_count <= budget,
        "semantic_class_bijection_exists": False,
        "benign_encoding": False,
        "certified": ambiguous == expected and holds and bit_count > budget,
    }


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    replication = json.loads(REPLICATION_PATH.read_text(encoding="utf-8"))
    transports = reconstruct_transport_rows()
    recorded_transports = result.get("transport_rows", [])

    alias_rows = result.get("exhaustive_alias_rows", [])
    alias_match = len(alias_rows) == 14
    expected_alias_keys = [
        (class_count, level)
        for class_count in range(2, 6)
        for level in range(1, class_count + 1)
    ]
    for row, key in zip(alias_rows, expected_alias_keys):
        class_count, level = key
        raw_count, minimum = raw_minimum(class_count, level)
        alias_match = alias_match and (
            row["class_count"] == class_count
            and row["level"] == level
            and row["raw_atoms_enumerated"] == raw_count
            and row["raw_minimum"] == minimum == level
            and row["quotient_minimum"] == level
            and row["matches"] is True
        )

    parity = [parity_row(bit_count) for bit_count in range(4, 13)]
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_encoding_invariance_v2_0"
            and result.get("status")
            == "exact_replication_quotient_invariance_and_macro_cost_barrier"
            and result.get("parent_result")
            == "ASMP-3-BLOCK-SELECTION-COMPOSITION-v1.9"
            and result.get("certified") is True
            and "randomized approximation" in result.get("claim_boundary", "")
        ),
        "V1_all_27_transport_rows_reconstructed": (
            len(recorded_transports) == 27 and recorded_transports == transports
        ),
        "V2_quotient_dimension_and_search_transport_exact": all(
            row["source_dimension"] == row["encoded_dimension"]
            and row["canonical_witness_transport_holds"]
            and row["certified"]
            for row in transports
        ),
        "V3_alias_expansion_exhaustion_replayed": alias_match,
        "V4_parity_partial_assignment_lower_bounds_replayed": (
            result.get("parity_macro_rows") == parity
            and all(row["certified"] for row in parity)
        ),
        "V5_macro_semantic_and_resource_rejection_exact": all(
            row["base_refutation_dimension"] == row["bit_count"]
            and row["macro_refutation_dimension"] == 1
            and row["macro_evaluation_cost"]
            > row["declared_local_atom_evaluation_budget"]
            and not row["semantic_class_bijection_exists"]
            and not row["benign_encoding"]
            for row in parity
        ),
        "V6_parent_replication_contract_reconstructed": (
            parent["parent_result"]
            == "ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8"
            and "meaning-preserving" in replication["claim_boundary"]
            and "registered" in replication["claim_boundary"]
        ),
        "V7_producer_gates_all_true": (
            len(result.get("gates", {})) == 10 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_encoding_invariance_verification_v2_0",
        "checker": "clean_room_quotient_transport_alias_and_parity_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates finite exact quotient bijections and the "
            "deterministic exact-query parity macro barrier. It does not certify "
            "all resource-preserving encodings or randomized approximate queries."
        ),
    }


def main() -> None:
    result = verify()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["passed"]:
        failed = [name for name, passed in result["checks"].items() if not passed]
        raise SystemExit(f"encoding-invariance verification failed: {failed}")
    print(
        "ASMP-3 encoding-invariance verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
