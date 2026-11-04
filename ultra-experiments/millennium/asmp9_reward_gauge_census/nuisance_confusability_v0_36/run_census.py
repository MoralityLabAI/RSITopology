"""Execute the prospectively registered ASMP-9 v0.36 exact census."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import time
import tracemalloc
from typing import Any, Mapping, Sequence

from confusability import (
    all_tables,
    confusability_relation,
    decision_identifiable,
    decoder_exists,
    is_equivalence_relation,
    is_reflexive,
    is_symmetric,
    is_transitive,
    mirrored_threshold_tables,
    relation_edge_bits,
    relation_subset,
    set_equality_relation,
    signatures,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRATION_SCHEMA = "asmp9_nuisance_confusability_registration_v0_36"
RESULT_SCHEMA = "asmp9_nuisance_confusability_result_v0_36"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (REPO / path).resolve()


def load_registration(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != REGISTRATION_SCHEMA:
        raise ValueError("unexpected registration schema")
    if (
        payload.get("status") != "registered_not_run"
        or payload.get("outcomes_consumed") is not False
    ):
        raise ValueError("registration is not prereveal")
    expected = str(payload["registration_content_sha256"])
    actual = hashlib.sha256(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "registration_content_sha256"
            }
        )
    ).hexdigest()
    if actual != expected:
        raise ValueError("registration content hash mismatch")
    for group_name in ("implementation", "documents"):
        for name, item in payload[group_name].items():
            candidate = resolve_path(str(item["path"]))
            if not candidate.is_file():
                raise FileNotFoundError(candidate)
            if sha256_file(candidate) != str(item["sha256"]):
                raise ValueError(
                    f"registered {group_name} hash mismatch: {name}"
                )
    return payload


def all_decisions() -> tuple[tuple[int, int, int], ...]:
    return tuple(product(range(3), repeat=3))


def decoder_theorem_mismatches(
    observation_sets: Sequence[frozenset[tuple[int, ...]]],
    relation: tuple[tuple[bool, ...], ...],
) -> int:
    return sum(
        decision_identifiable(relation, decisions)
        != decoder_exists(observation_sets, decisions)
        for decisions in all_decisions()
    )


def one_query_census() -> dict[str, Any]:
    relation_shapes: Counter[str] = Counter()
    nontransitive = 0
    equality_relation_failures = 0
    decoder_mismatches = 0
    table_count = 0
    for table in all_tables(3, 2, 2):
        table_count += 1
        observation_sets = signatures(
            (table,), 3, 2, nuisance_mode="shared"
        )
        relation = confusability_relation(observation_sets)
        relation_shapes[relation_edge_bits(relation)] += 1
        nontransitive += not is_transitive(relation)
        equality_relation_failures += not is_equivalence_relation(
            set_equality_relation(observation_sets)
        )
        decoder_mismatches += decoder_theorem_mismatches(
            observation_sets, relation
        )
    return {
        "tables": table_count,
        "relation_shape_counts": dict(sorted(relation_shapes.items())),
        "nontransitive_relations": nontransitive,
        "set_equality_relation_failures": equality_relation_failures,
        "decision_maps_per_table": len(all_decisions()),
        "decoder_theorem_mismatches": decoder_mismatches,
    }


def minimality_census() -> dict[str, Any]:
    cells: list[dict[str, Any]] = []
    for theta_count, nuisance_count, alphabet_count in (
        (1, 2, 2),
        (2, 2, 2),
        (3, 1, 2),
        (3, 2, 1),
    ):
        tables = 0
        nontransitive = 0
        for table in all_tables(
            theta_count, nuisance_count, alphabet_count
        ):
            tables += 1
            relation = confusability_relation(
                signatures(
                    (table,),
                    theta_count,
                    nuisance_count,
                    nuisance_mode="shared",
                )
            )
            nontransitive += not is_transitive(relation)
        cells.append(
            {
                "theta_count": theta_count,
                "nuisance_count": nuisance_count,
                "alphabet_count": alphabet_count,
                "tables": tables,
                "nontransitive_relations": nontransitive,
            }
        )
    return {
        "cells": cells,
        "all_registered_smaller_cells_transitive": all(
            row["nontransitive_relations"] == 0 for row in cells
        ),
    }


def two_query_census() -> dict[str, Any]:
    tables = tuple(all_tables(3, 2, 2))
    identity = (0, 1, 2)
    counts: Counter[str] = Counter()
    shared_shapes: Counter[str] = Counter()
    reset_shapes: Counter[str] = Counter()
    decoder_mismatches = 0
    query_monotonicity_failures = 0
    shared_reset_subset_failures = 0
    for first in tables:
        first_sets = signatures(
            (first,), 3, 2, nuisance_mode="shared"
        )
        first_relation = confusability_relation(first_sets)
        for second in tables:
            counts["ordered_table_pairs"] += 1
            second_sets = signatures(
                (second,), 3, 2, nuisance_mode="shared"
            )
            second_relation = confusability_relation(second_sets)
            shared_sets = signatures(
                (first, second), 3, 2, nuisance_mode="shared"
            )
            reset_sets = signatures(
                (first, second), 3, 2, nuisance_mode="reset"
            )
            shared_relation = confusability_relation(shared_sets)
            reset_relation = confusability_relation(reset_sets)
            shared_shapes[relation_edge_bits(shared_relation)] += 1
            reset_shapes[relation_edge_bits(reset_relation)] += 1

            first_identifies = decision_identifiable(
                first_relation, identity
            )
            second_identifies = decision_identifiable(
                second_relation, identity
            )
            shared_identifies = decision_identifiable(
                shared_relation, identity
            )
            reset_identifies = decision_identifiable(
                reset_relation, identity
            )
            counts["first_query_identifies_identity"] += first_identifies
            counts["second_query_identifies_identity"] += second_identifies
            counts["joint_shared_identifies_identity"] += shared_identifies
            counts["joint_reset_identifies_identity"] += reset_identifies
            counts["shared_query_synergy"] += (
                not first_identifies
                and not second_identifies
                and shared_identifies
            )
            counts["shared_only_identification"] += (
                shared_identifies and not reset_identifies
            )

            query_monotonicity_failures += not (
                relation_subset(shared_relation, first_relation)
                and relation_subset(shared_relation, second_relation)
            )
            shared_reset_subset_failures += not relation_subset(
                shared_relation, reset_relation
            )
            decoder_mismatches += decoder_theorem_mismatches(
                shared_sets, shared_relation
            )
            decoder_mismatches += decoder_theorem_mismatches(
                reset_sets, reset_relation
            )
    return {
        **dict(sorted(counts.items())),
        "decision_maps_per_channel": len(all_decisions()),
        "decoder_theorem_mismatches": decoder_mismatches,
        "query_monotonicity_failures": query_monotonicity_failures,
        "shared_reset_subset_failures": shared_reset_subset_failures,
        "shared_relation_shape_counts": dict(sorted(shared_shapes.items())),
        "reset_relation_shape_counts": dict(sorted(reset_shapes.items())),
    }


def planted_witness() -> dict[str, Any]:
    q0, q1 = mirrored_threshold_tables()
    q0_sets = signatures((q0,), 3, 2, nuisance_mode="shared")
    q1_sets = signatures((q1,), 3, 2, nuisance_mode="shared")
    shared_sets = signatures((q0, q1), 3, 2, nuisance_mode="shared")
    reset_sets = signatures((q0, q1), 3, 2, nuisance_mode="reset")
    q0_relation = confusability_relation(q0_sets)
    q1_relation = confusability_relation(q1_sets)
    shared_relation = confusability_relation(shared_sets)
    reset_relation = confusability_relation(reset_sets)

    def serializable(
        values: Sequence[frozenset[tuple[int, ...]]],
    ) -> list[list[list[int]]]:
        return [
            [list(observation) for observation in sorted(value)]
            for value in values
        ]

    return {
        "q0_table": list(q0),
        "q1_table": list(q1),
        "q0_signatures": serializable(q0_sets),
        "q1_signatures": serializable(q1_sets),
        "joint_shared_signatures": serializable(shared_sets),
        "joint_reset_signatures": serializable(reset_sets),
        "q0_edge_bits": relation_edge_bits(q0_relation),
        "q1_edge_bits": relation_edge_bits(q1_relation),
        "q0_reflexive": is_reflexive(q0_relation),
        "q0_symmetric": is_symmetric(q0_relation),
        "q0_transitive": is_transitive(q0_relation),
        "q1_transitive": is_transitive(q1_relation),
        "joint_shared_identifies_identity": decision_identifiable(
            shared_relation, (0, 1, 2)
        ),
        "joint_reset_identifies_identity": decision_identifiable(
            reset_relation, (0, 1, 2)
        ),
        "joint_shared_edge_bits": relation_edge_bits(shared_relation),
        "joint_reset_edge_bits": relation_edge_bits(reset_relation),
    }


def compute_result(registration: Mapping[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    tracemalloc.start()
    one_query = one_query_census()
    minimality = minimality_census()
    two_query = two_query_census()
    witness = planted_witness()
    gates = [
        {
            "gate": "N0",
            "decision": (
                "pass"
                if (
                    witness["q0_reflexive"]
                    and witness["q0_symmetric"]
                    and not witness["q0_transitive"]
                    and witness["q0_edge_bits"] == "101"
                )
                else "fail"
            ),
        },
        {
            "gate": "M0",
            "decision": (
                "pass"
                if minimality["all_registered_smaller_cells_transitive"]
                else "fail"
            ),
        },
        {
            "gate": "D0",
            "decision": (
                "pass"
                if (
                    one_query["decoder_theorem_mismatches"] == 0
                    and two_query["decoder_theorem_mismatches"] == 0
                )
                else "fail"
            ),
        },
        {
            "gate": "Q0",
            "decision": (
                "pass"
                if (
                    two_query["query_monotonicity_failures"] == 0
                    and two_query["shared_reset_subset_failures"] == 0
                )
                else "fail"
            ),
        },
        {
            "gate": "W0",
            "decision": (
                "pass"
                if (
                    witness["joint_shared_identifies_identity"]
                    and not witness["joint_reset_identifies_identity"]
                    and two_query["shared_only_identification"] > 0
                )
                else "fail"
            ),
        },
    ]
    all_pass = all(row["decision"] == "pass" for row in gates)
    _, peak_traced_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA,
        "status": (
            "bounded_confusability_theorem_verified"
            if all_pass
            else "bounded_confusability_theorem_not_established"
        ),
        "one_query_census": one_query,
        "minimality_census": minimality,
        "two_query_census": two_query,
        "planted_witness": witness,
        "gates": gates,
        "runtime": {
            "elapsed_seconds": time.perf_counter() - started,
            "peak_python_tracemalloc_bytes": peak_traced_bytes,
        },
        "registration": {
            "content_sha256": registration[
                "registration_content_sha256"
            ],
            "git_commit_before_registration": registration[
                "git_commit_before_registration"
            ],
        },
        "claim_boundary": registration["claim_boundary"],
    }
    result["result_content_sha256"] = hashlib.sha256(
        canonical_bytes(result)
    ).hexdigest()
    return result


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing unequal result: {path}")
        return
    path.write_bytes(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registration_path = args.registration.resolve()
    registration = load_registration(registration_path)
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=REPO,
        text=True,
    ).strip():
        raise RuntimeError("runner requires a clean registered worktree")
    current_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        text=True,
    ).strip()
    before = str(registration["git_commit_before_registration"])
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", before, current_commit],
        cwd=REPO,
        check=False,
    )
    if ancestor.returncode != 0:
        raise RuntimeError("implementation commit is not an ancestor of HEAD")
    try:
        relative_registration = registration_path.relative_to(REPO).as_posix()
    except ValueError as error:
        raise RuntimeError("registration must be committed in the repo") from error
    committed_registration = subprocess.check_output(
        ["git", "show", f"HEAD:{relative_registration}"],
        cwd=REPO,
    )
    if hashlib.sha256(committed_registration).hexdigest() != sha256_file(
        registration_path
    ):
        raise RuntimeError("working registration differs from committed bytes")
    result = compute_result(registration)
    result["registration"]["file_sha256"] = sha256_file(registration_path)
    result["result_content_sha256"] = hashlib.sha256(
        canonical_bytes(
            {
                key: value
                for key, value in result.items()
                if key != "result_content_sha256"
            }
        )
    ).hexdigest()
    write_once(args.output.resolve(), canonical_bytes(result))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
