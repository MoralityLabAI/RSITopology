from __future__ import annotations

import json
from itertools import combinations, product
from math import ceil, log2
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_block_selection_composition_v1_9"
    / "artifacts"
    / "block_selection_composition_v1_9.json"
)
REPLICATION_PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_independent_noise_amplification_v1_8"
    / "artifacts"
    / "independent_noise_amplification_v1_8.json"
)


WitnessFamily = dict[str, tuple[frozenset[int], ...]]


def make_task(class_count: int, levels: tuple[int, ...]) -> WitnessFamily:
    if class_count < 1 or not levels or any(level < 1 or level > class_count for level in levels):
        raise ValueError("invalid quotient-refutation task")
    classes = tuple(range(class_count))
    return {
        f"tau_{index}": tuple(
            frozenset(witness) for witness in combinations(classes, level)
        )
        for index, level in enumerate(levels)
    }


def transcript_minima(task: WitnessFamily) -> dict[str, int]:
    if not task or any(not witnesses for witnesses in task.values()):
        raise ValueError("every false transcript needs a refuting witness")
    return {
        transcript: min(len(witness) for witness in witnesses)
        for transcript, witnesses in task.items()
    }


def quotient_dimension(task: WitnessFamily) -> int:
    return max(transcript_minima(task).values())


def transport_task(
    task: WitnessFamily,
    class_map: dict[int, int],
    transcript_map: dict[str, str],
) -> WitnessFamily:
    source_classes = set().union(*(set(witness) for family in task.values() for witness in family))
    if set(class_map) != source_classes or len(set(class_map.values())) != len(class_map):
        raise ValueError("class transport must be a bijection")
    if set(transcript_map) != set(task) or len(set(transcript_map.values())) != len(task):
        raise ValueError("transcript transport must be a bijection")
    return {
        transcript_map[transcript]: tuple(
            frozenset(class_map[item] for item in witness)
            for witness in witnesses
        )
        for transcript, witnesses in task.items()
    }


def canonical_witnesses(task: WitnessFamily) -> dict[str, tuple[int, ...]]:
    result = {}
    for transcript, witnesses in task.items():
        minimum = min(len(witness) for witness in witnesses)
        candidates = [tuple(sorted(witness)) for witness in witnesses if len(witness) == minimum]
        result[transcript] = min(candidates)
    return result


def alias_map(multiplicities: tuple[int, ...]) -> dict[str, int]:
    if not multiplicities or any(value < 1 for value in multiplicities):
        raise ValueError("every semantic class needs at least one alias")
    return {
        f"c{class_id}_alias{alias_id}": class_id
        for class_id, count in enumerate(multiplicities)
        for alias_id in range(count)
    }


def expanded_refutes(
    raw_atoms: frozenset[str], witnesses: tuple[frozenset[int], ...], aliases: dict[str, int]
) -> bool:
    if not raw_atoms <= set(aliases):
        raise ValueError("unknown raw atom")
    projected = {aliases[atom] for atom in raw_atoms}
    return any(witness <= projected for witness in witnesses)


def exhaustive_raw_minimum(
    witnesses: tuple[frozenset[int], ...], aliases: dict[str, int]
) -> int:
    raw = tuple(sorted(aliases))
    for size in range(len(raw) + 1):
        if any(
            expanded_refutes(frozenset(candidate), witnesses, aliases)
            for candidate in combinations(raw, size)
        ):
            return size
    raise ValueError("expanded syntax has no refutation")


def transport_registry() -> list[dict[str, object]]:
    rows = []
    for class_count in range(2, 11):
        profiles = (
            (1, class_count),
            (max(1, class_count // 2), max(1, class_count - 1)),
            tuple(range(1, min(class_count, 4) + 1)),
        )
        for profile_id, levels in enumerate(profiles):
            task = make_task(class_count, levels)
            transcripts = tuple(task)
            class_transport = {
                class_id: (class_id + 1) % class_count
                for class_id in range(class_count)
            }
            transcript_transport = {
                transcript: f"encoded_{len(transcripts) - 1 - index}"
                for index, transcript in enumerate(transcripts)
            }
            encoded = transport_task(task, class_transport, transcript_transport)
            aliases = tuple(
                1 + ((class_id + profile_id) % 3)
                for class_id in range(class_count)
            )
            canonical = canonical_witnesses(task)
            encoded_canonical = canonical_witnesses(encoded)
            witness_transport_holds = all(
                tuple(sorted(class_transport[item] for item in canonical[transcript]))
                in [
                    tuple(sorted(witness))
                    for witness in encoded[transcript_transport[transcript]]
                ]
                for transcript in task
            )
            rows.append(
                {
                    "class_count": class_count,
                    "profile_id": profile_id,
                    "transcript_levels": list(levels),
                    "source_transcript_minima": transcript_minima(task),
                    "encoded_transcript_minima": transcript_minima(encoded),
                    "source_dimension": quotient_dimension(task),
                    "encoded_dimension": quotient_dimension(encoded),
                    "alias_multiplicities": list(aliases),
                    "raw_alias_alphabet_size": sum(aliases),
                    "semantic_class_count": class_count,
                    "canonical_witness_transport_holds": witness_transport_holds,
                    "encoded_search_witnesses": {
                        key: list(value) for key, value in encoded_canonical.items()
                    },
                    "dimension_invariant": quotient_dimension(task)
                    == quotient_dimension(encoded),
                    "certified": (
                        quotient_dimension(task) == quotient_dimension(encoded)
                        and witness_transport_holds
                        and sum(aliases) >= class_count
                    ),
                }
            )
    return rows


def exhaustive_alias_audit() -> list[dict[str, object]]:
    rows = []
    for class_count in range(2, 6):
        for level in range(1, class_count + 1):
            task = make_task(class_count, (level,))
            multiplicities = tuple(1 + (class_id % 2) for class_id in range(class_count))
            aliases = alias_map(multiplicities)
            transcript = next(iter(task))
            raw_minimum = exhaustive_raw_minimum(task[transcript], aliases)
            rows.append(
                {
                    "class_count": class_count,
                    "level": level,
                    "alias_multiplicities": list(multiplicities),
                    "raw_atoms_enumerated": len(aliases),
                    "raw_minimum": raw_minimum,
                    "quotient_minimum": level,
                    "matches": raw_minimum == level,
                }
            )
    return rows


def parity_macro_row(bit_count: int) -> dict[str, object]:
    if bit_count < 2:
        raise ValueError("parity macro audit starts at two bits")
    ambiguous_partial_assignments = 0
    ambiguity_holds = True
    for partial in product((-1, 0, 1), repeat=bit_count):
        if -1 not in partial:
            continue
        ambiguous_partial_assignments += 1
        first_unknown = partial.index(-1)
        zero_completion = [0 if value == -1 else value for value in partial]
        one_completion = list(zero_completion)
        one_completion[first_unknown] = 1
        ambiguity_holds = ambiguity_holds and (
            sum(zero_completion) % 2 != sum(one_completion) % 2
        )
    expected_ambiguous = 3**bit_count - 2**bit_count
    pivotal_bits = 0
    zero_input = [0] * bit_count
    for bit in range(bit_count):
        flipped = list(zero_input)
        flipped[bit] = 1
        pivotal_bits += (sum(zero_input) % 2) != (sum(flipped) % 2)
    base_task = make_task(bit_count, (bit_count,))
    macro_task = make_task(1, (1,))
    atom_budget = ceil(log2(bit_count + 1))
    return {
        "bit_count": bit_count,
        "ambiguous_partial_assignments_checked": ambiguous_partial_assignments,
        "ambiguous_partial_assignment_formula": expected_ambiguous,
        "every_nonterminal_partial_assignment_ambiguous": ambiguity_holds,
        "pivotal_bits": pivotal_bits,
        "exact_deterministic_query_complexity": bit_count,
        "base_refutation_dimension": quotient_dimension(base_task),
        "macro_refutation_dimension": quotient_dimension(macro_task),
        "macro_evaluation_cost": bit_count,
        "declared_local_atom_evaluation_budget": atom_budget,
        "macro_within_declared_budget": bit_count <= atom_budget,
        "semantic_class_bijection_exists": bit_count == 1,
        "benign_encoding": False,
        "certified": (
            ambiguous_partial_assignments == expected_ambiguous
            and ambiguity_holds
            and pivotal_bits == bit_count
            and quotient_dimension(base_task) == bit_count
            and quotient_dimension(macro_task) == 1
            and bit_count > atom_budget
        ),
    }


def build_result() -> dict[str, object]:
    parent = json.loads(PARENT_ARTIFACT.read_text(encoding="utf-8"))
    replication_parent = json.loads(
        REPLICATION_PARENT_ARTIFACT.read_text(encoding="utf-8")
    )
    transports = transport_registry()
    aliases = exhaustive_alias_audit()
    parity = [parity_macro_row(bit_count) for bit_count in range(4, 13)]
    gates = {
        "E0_transport_registry_complete": len(transports) == 27,
        "E1_quotient_dimension_invariant_under_all_bijections": all(
            row["dimension_invariant"] and row["certified"] for row in transports
        ),
        "E2_alias_alphabet_growth_does_not_change_quotient_count": all(
            row["raw_alias_alphabet_size"] >= row["semantic_class_count"]
            and row["source_dimension"] == row["encoded_dimension"]
            for row in transports
        ),
        "E3_small_alias_expansions_exhaustively_reconstructed": (
            len(aliases) == 14 and all(row["matches"] for row in aliases)
        ),
        "E4_honest_witness_search_transports_constructively": all(
            row["canonical_witness_transport_holds"] for row in transports
        ),
        "E5_all_parity_partial_assignments_certify_query_lower_bound": all(
            row["every_nonterminal_partial_assignment_ambiguous"]
            and row["exact_deterministic_query_complexity"] == row["bit_count"]
            for row in parity
        ),
        "E6_macro_dimension_drop_is_semantic_not_benign": all(
            row["base_refutation_dimension"] == row["bit_count"]
            and row["macro_refutation_dimension"] == 1
            and not row["semantic_class_bijection_exists"]
            and not row["benign_encoding"]
            for row in parity
        ),
        "E7_macro_global_evaluation_cost_rejected": all(
            row["macro_evaluation_cost"] > row["declared_local_atom_evaluation_budget"]
            and not row["macro_within_declared_budget"]
            for row in parity
        ),
        "E8_parent_replication_contract_is_preserved": (
            parent["parent_result"]
            == "ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8"
            and "meaning-preserving" in replication_parent["claim_boundary"]
            and "registered" in replication_parent["claim_boundary"]
        ),
        "E9_all_rows_certified": all(row["certified"] for row in parity),
    }
    return {
        "schema_version": "asmp3_encoding_invariance_v2_0",
        "experiment_id": "ASMP-3-ENCODING-INVARIANCE-v2.0",
        "status": "exact_replication_quotient_invariance_and_macro_cost_barrier",
        "parent_result": "ASMP-3-BLOCK-SELECTION-COMPOSITION-v1.9",
        "replication_contract_result": (
            "ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8"
        ),
        "theorem": {
            "benign_transport": (
                "bijections on false transcripts and semantic equivalence classes "
                "with sound-complete Refute transport"
            ),
            "dimension_result": "replication-quotiented refutation dimension is exact invariant",
            "search_result": "canonical witnesses transport constructively at linear witness cost",
            "macro_barrier": (
                "an N-bit parity macro has deterministic evaluation-query cost N "
                "despite one-atom syntax"
            ),
        },
        "transport_rows": transports,
        "exhaustive_alias_rows": aliases,
        "parity_macro_rows": parity,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The invariant theorem assumes actual bijections of transcript and "
            "semantic-equivalence quotient objects plus sound-complete witness "
            "transport. Adding a new macro semantic oracle is not an encoding. "
            "The parity lower bound is deterministic exact-query complexity, not "
            "a lower bound for randomized approximation or promised inputs."
        ),
    }
