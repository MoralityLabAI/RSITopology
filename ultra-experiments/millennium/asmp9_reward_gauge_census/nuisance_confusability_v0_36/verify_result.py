"""Import-independent verifier for the ASMP-9 v0.36 exact result."""

from __future__ import annotations

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def direct_sets(
    tables: tuple[tuple[int, ...], ...],
    *,
    reset: bool,
) -> tuple[set[tuple[int, ...]], ...]:
    output: list[set[tuple[int, ...]]] = []
    for theta in range(3):
        marginals = [
            {table[theta * 2], table[theta * 2 + 1]}
            for table in tables
        ]
        if reset:
            output.append(set(product(*marginals)))
        else:
            output.append(
                {
                    tuple(table[theta * 2 + nuisance] for table in tables)
                    for nuisance in range(2)
                }
            )
    return tuple(output)


def edge_bits(sets: tuple[set[tuple[int, ...]], ...]) -> str:
    return "".join(
        "1" if sets[i] & sets[j] else "0"
        for i, j in ((0, 1), (0, 2), (1, 2))
    )


def transitive(bits: str) -> bool:
    adjacency = [
        [True, bits[0] == "1", bits[1] == "1"],
        [bits[0] == "1", True, bits[2] == "1"],
        [bits[1] == "1", bits[2] == "1", True],
    ]
    return all(
        not (adjacency[i][j] and adjacency[j][k]) or adjacency[i][k]
        for i in range(3)
        for j in range(3)
        for k in range(3)
    )


def recompute_counts() -> dict[str, int]:
    tables = tuple(product((0, 1), repeat=6))
    nontransitive = sum(
        not transitive(edge_bits(direct_sets((table,), reset=False)))
        for table in tables
    )
    shared_identifies = 0
    reset_identifies = 0
    shared_only = 0
    for first in tables:
        for second in tables:
            shared = edge_bits(
                direct_sets((first, second), reset=False)
            )
            reset = edge_bits(direct_sets((first, second), reset=True))
            shared_ok = shared == "000"
            reset_ok = reset == "000"
            shared_identifies += shared_ok
            reset_identifies += reset_ok
            shared_only += shared_ok and not reset_ok
    return {
        "one_query_nontransitive": nontransitive,
        "joint_shared_identifies_identity": shared_identifies,
        "joint_reset_identifies_identity": reset_identifies,
        "shared_only_identification": shared_only,
    }


def verify(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected_hash = str(payload["result_content_sha256"])
    actual_hash = hashlib.sha256(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "result_content_sha256"
            }
        )
    ).hexdigest()
    checks = {
        "result_content_hash": actual_hash == expected_hash,
        "all_gates_pass": all(
            row["decision"] == "pass" for row in payload["gates"]
        ),
        "witness_path": (
            payload["planted_witness"]["q0_edge_bits"] == "101"
            and not payload["planted_witness"]["q0_transitive"]
        ),
        "witness_shared_identifies": payload["planted_witness"][
            "joint_shared_identifies_identity"
        ],
        "witness_reset_fails": not payload["planted_witness"][
            "joint_reset_identifies_identity"
        ],
    }
    recomputed = recompute_counts()
    checks["one_query_count"] = recomputed[
        "one_query_nontransitive"
    ] == payload["one_query_census"]["nontransitive_relations"]
    for field in (
        "joint_shared_identifies_identity",
        "joint_reset_identifies_identity",
        "shared_only_identification",
    ):
        checks[field] = (
            recomputed[field] == payload["two_query_census"][field]
        )
    return {
        "schema_version": "asmp9_nuisance_confusability_verification_v0_36",
        "passed": all(checks.values()),
        "checks": checks,
        "recomputed": recomputed,
        "result_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    verification = verify(args.result.resolve())
    data = canonical_bytes(verification)
    output = args.output.resolve()
    if output.exists() and output.read_bytes() != data:
        raise FileExistsError(f"refusing unequal verification: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        output.write_bytes(data)
    if not verification["passed"]:
        raise SystemExit(1)
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
