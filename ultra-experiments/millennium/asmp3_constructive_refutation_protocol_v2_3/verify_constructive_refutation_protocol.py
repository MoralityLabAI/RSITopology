from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import cache
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "constructive_refutation_protocol_v2_3.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "constructive_refutation_protocol_verification_v2_3.json"
)
COMPOSITION_PATH = (
    HERE.parent
    / "asmp3_block_selection_composition_v1_9"
    / "artifacts"
    / "block_selection_composition_v1_9.json"
)
ENCODING_PATH = (
    HERE.parent
    / "asmp3_encoding_invariance_v2_0"
    / "artifacts"
    / "encoding_invariance_v2_0.json"
)
SEARCH_PATH = (
    HERE.parent
    / "asmp3_honest_search_barrier_v2_1"
    / "artifacts"
    / "honest_search_barrier_v2_1.json"
)
RESOURCE_PATH = (
    HERE.parent
    / "asmp3_resource_tradeoff_v2_2"
    / "artifacts"
    / "resource_tradeoff_v2_2.json"
)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


@cache
def majority_error(depth: int, eta: Q) -> Q:
    result = sum(
        (
            Q(comb(depth, errors))
            * eta**errors
            * (1 - eta) ** (depth - errors)
            for errors in range(depth // 2 + 1, depth + 1)
        ),
        Q(0),
    )
    if depth % 2 == 0:
        result += (
            Q(comb(depth, depth // 2))
            * eta ** (depth // 2)
            * (1 - eta) ** (depth // 2)
            / 2
        )
    return result


def joint_risk(size: int, depth: int, eta: Q) -> Q:
    return 1 - (1 - majority_error(depth, eta)) ** size


def minimum_depth(size: int, eta: Q, target: Q) -> int:
    for depth in (1, *range(3, 1024, 2)):
        if joint_risk(size, depth, eta) <= target:
            return depth
    raise RuntimeError("clean-room depth search exceeded limit")


def reconstruct_row(size: int, eta: Q, target: Q, atom_bits: int = 20):
    depth = minimum_depth(size, eta, target)
    atom = majority_error(depth, eta)
    risk = joint_risk(size, depth, eta)
    previous = joint_risk(size, depth - 2, eta) if depth > 1 else None
    prefix = size.bit_length()
    critic_bits = prefix + size * (atom_bits + 1)
    finder = size * atom_bits
    return {
        "maximum_refutation_classes": size,
        "eta": text(eta),
        "target_protocol_error": text(target),
        "atom_id_bits": atom_bits,
        "replications_per_atom": depth,
        "single_atom_majority_error": text(atom),
        "joint_decoding_error": text(risk),
        "previous_odd_depth_joint_error": text(previous) if previous is not None else None,
        "completeness_lower_bound": text(1 - risk),
        "soundness_upper_bound": text(risk),
        "completeness_soundness_gap_lower_bound": text(1 - 2 * risk),
        "semantic_query_count": size * depth,
        "critic_message_length_prefix_bits": prefix,
        "critic_message_bits": critic_bits,
        "registered_finder_time_bound": finder,
        "finder_contract": (
            "uniformly returns a sound-complete quotient witness of size <=r "
            "for every false admissible transcript"
        ),
        "noise_contract": (
            "fresh disjoint iid blocks sampled only after transcript and witness are fixed"
        ),
        "malformed_critic_message_policy": "ignore_and_accept_advocate",
        "minimal_odd_depth_certified": (
            risk <= target and (previous is None or previous > target)
        ),
        "certified": True,
    }


def reconstruct_scaling():
    rows = []
    for log_work in range(10, 101, 10):
        row = reconstruct_row(log_work, Q(1, 5), Q(1, log_work), log_work)
        budget = log_work**3
        rows.append(
            {
                "log2_prover_work": log_work,
                "refutation_size": log_work,
                "target_error": text(Q(1, log_work)),
                "replications_per_atom": row["replications_per_atom"],
                "semantic_queries": row["semantic_query_count"],
                "critic_message_bits": row["critic_message_bits"],
                "finder_time": row["registered_finder_time_bound"],
                "declared_polylog_cubic_budget": budget,
                "all_resources_within_cubic_polylog_budget": (
                    row["semantic_query_count"] <= budget
                    and row["critic_message_bits"] <= budget
                    and row["registered_finder_time_bound"] <= budget
                ),
                "gap_lower_bound": row["completeness_soundness_gap_lower_bound"],
            }
        )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    composition = json.loads(COMPOSITION_PATH.read_text(encoding="utf-8"))
    encoding = json.loads(ENCODING_PATH.read_text(encoding="utf-8"))
    search = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    resource = json.loads(RESOURCE_PATH.read_text(encoding="utf-8"))
    expected_rows = [
        reconstruct_row(size, eta, target)
        for eta in (Q(1, 5), Q(1, 3), Q(2, 5))
        for size in (1, 2, 4, 8, 16, 32, 64)
        for target in (Q(1, 10), Q(1, 100))
    ]
    rows = result.get("protocol_rows", [])
    scaling = reconstruct_scaling()
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version")
            == "asmp3_constructive_refutation_protocol_v2_3"
            and result.get("status")
            == "constructive_positive_protocol_under_typed_finder_noise_contracts"
            and result.get("parent_result") == "ASMP-3-RESOURCE-TRADEOFF-v2.2"
            and result.get("certified") is True
            and "does not prove those contracts" in result.get("claim_boundary", "")
        ),
        "V1_all_42_protocol_rows_reconstructed": len(rows) == 42 and rows == expected_rows,
        "V2_completeness_soundness_and_gap_exact": all(
            Q(row["completeness_lower_bound"]) == 1 - Q(row["joint_decoding_error"])
            and Q(row["soundness_upper_bound"]) == Q(row["joint_decoding_error"])
            and Q(row["completeness_soundness_gap_lower_bound"])
            == 1 - 2 * Q(row["joint_decoding_error"])
            for row in rows
        ),
        "V3_all_replication_depths_independently_minimized": all(
            row["minimal_odd_depth_certified"]
            and Q(row["joint_decoding_error"]) <= Q(row["target_protocol_error"])
            for row in rows
        ),
        "V4_polylog_scaling_lane_reconstructed": (
            result.get("polylog_scaling_rows") == scaling
            and all(row["all_resources_within_cubic_polylog_budget"] for row in scaling)
        ),
        "V5_all_resource_charges_reconstructed": all(
            row["semantic_query_count"]
            == row["maximum_refutation_classes"] * row["replications_per_atom"]
            and row["critic_message_bits"]
            == row["critic_message_length_prefix_bits"]
            + row["maximum_refutation_classes"] * (row["atom_id_bits"] + 1)
            and row["registered_finder_time_bound"]
            == row["maximum_refutation_classes"] * row["atom_id_bits"]
            for row in rows
        ),
        "V6_supporting_obstruction_and_noise_contracts_match": (
            composition["theorem"]["independent_M_atom_risk"] == "1-(1-e_d)^M"
            and encoding["theorem"]["dimension_result"].endswith("exact invariant")
            and search["theorem"]["conclusion"].startswith("small combinatorial dimension")
            and resource["theorem"]["lower_bound"]
            == "K*q>=N message-query covering inequality"
        ),
        "V7_producer_gates_all_true": (
            len(result.get("gates", {})) == 10 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_constructive_refutation_protocol_verification_v2_3",
        "checker": "clean_room_protocol_risk_resource_and_parent_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates the conditional challenge/refutation theorem "
            "for the declared finder, Refute, and fresh-iid contracts. It does not "
            "establish those contracts for arbitrary environments or interfaces."
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
        raise SystemExit(f"constructive-protocol verification failed: {failed}")
    print(
        "ASMP-3 constructive-protocol verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
