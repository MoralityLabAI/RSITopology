"""Independent verifier for the ASMP-1 v0.2 machine-readable result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from identifiability_boundary import build_result, serialize


REQUIRED_DOCUMENTS = (
    "THEOREM_v0_2.md",
    "RESULT_v0_2.md",
    "RESOLUTION_AUDIT_v0_2.md",
    "PRIOR_ART_v0_2.md",
)


def verify(
    result_path: Path,
    source_path: Path,
    recompute: bool = True,
) -> dict[str, object]:
    stored = json.loads(result_path.read_text(encoding="utf-8"))
    source_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    directory = source_path.parent
    census = stored["linear_design_census"]
    binding = stored["computable_real_undecidability_fixture"][
        "canonical_rational_taylor_binding"
    ]

    checks: dict[str, bool] = {
        "schema_matches": stored.get("schema_version")
        == "asmp1_identifiability_boundary_v0_2",
        "all_exact_gates_pass": stored.get("all_exact_gates_pass") is True,
        "source_hash_matches": stored.get("source_sha256") == source_sha256,
        "matrix_partition_matches": census["matrix_count"]
        == census["full_rank_count"] + census["rank_deficient_count"],
        "registered_full_census_size": census["matrix_count"] == 21_300,
        "registered_recovery_count": census["full_rank_count"] == 12_516,
        "registered_collision_count": census["rank_deficient_count"] == 8_784,
        "canonical_binding_has_positive_local_margins": (
            binding["local_conditioning_margin"] >= 1
            and binding["intervention_strength_margin"] >= 1
        ),
        "canonical_binding_is_finite_and_bounded": (
            binding["typed_node_count"] == 3
            and binding["mechanism_class_size_upper_bound"] == 2
            and binding["covering_number_upper_bound"] == 2
            and binding["norm_bound"] == 2
        ),
        "required_documents_present": all(
            (directory / document).is_file() for document in REQUIRED_DOCUMENTS
        ),
    }

    if recompute:
        recomputed = serialize(
            build_result(
                max_quotient_dimension=int(census["max_quotient_dimension"]),
                max_rows=int(census["max_rows"]),
            )
        )
        assert isinstance(recomputed, dict)
        recomputed["source_sha256"] = source_sha256
        checks["full_result_recomputes_byte_semantically"] = recomputed == stored

    return {
        "schema_version": "asmp1_identifiability_boundary_verify_v0_2",
        "result_path": str(result_path),
        "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        "source_path": str(source_path),
        "source_sha256": source_sha256,
        "recomputed": recompute,
        "checks": checks,
        "verified": all(checks.values()),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    base = Path(__file__).resolve().parent
    parser.add_argument(
        "--result",
        type=Path,
        default=base / "artifacts" / "result_v0_2.json",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=base / "identifiability_boundary.py",
    )
    parser.add_argument("--no-recompute", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    receipt = verify(
        result_path=args.result.resolve(),
        source_path=args.source.resolve(),
        recompute=not args.no_recompute,
    )
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(args.output)
    return 0 if receipt["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
