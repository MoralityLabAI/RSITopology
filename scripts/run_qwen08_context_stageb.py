"""Execute the sealed target-blind Qwen context Stage-B analysis."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal
from rsi_topology.qwen_context_stageb import analyze_stage_b


def _validate_authorization(args: argparse.Namespace) -> dict:
    value = json.loads(args.authorization.read_text(encoding="utf-8-sig"))
    if value.get("schema_version") != "qwen_holonomy_geometry_analysis_authorization_v0_1":
        raise ValueError("invalid Stage-B analysis authorization")
    if value.get("status") != "authorized_for_target_blind_stage_b_analysis":
        raise ValueError("Stage-B analysis is not authorized")
    parameters = value.get("analysis_parameters", {})
    expected = {
        "protocol": args.protocol,
        "causal_protocol": args.causal_protocol,
        "manifest": args.manifest,
        "main_base_index": args.main_base_index,
        "main_naive_index": args.main_naive_index,
        "control_base_index": args.control_base_index,
        "control_naive_index": args.control_naive_index,
    }
    for key, path in expected.items():
        entry = parameters.get(key)
        if not isinstance(entry, dict):
            raise ValueError(f"authorization omits {key}")
        if Path(entry["path"]).resolve() != path.resolve() or entry["sha256"] != sha256_file(path):
            raise ValueError(f"authorized Stage-B input differs: {key}")
    if Path(parameters["output_dir"]).resolve() != args.output_dir.resolve():
        raise ValueError("authorized Stage-B output directory differs")
    if int(parameters["seed"]) != args.seed:
        raise ValueError("authorized Stage-B seed differs")
    for key, raw in value["source_paths"].items():
        path = Path(raw)
        if not path.is_file() or sha256_file(path) != value["source_sha256"][key]:
            raise ValueError(f"authorized Stage-B source differs: {key}")
    return value


def _report(result: dict) -> str:
    lines = [
        "# Qwen0.8B context-restricted sign-percolation Stage B",
        "",
        "## Decision",
        "",
        f"`{result['decision']}`",
        "",
        "This is a fresh development-model geometry result. It consumed no model answers or causal outcomes and performed no generation, gradients, or weight mutation.",
        "",
        "## Main four-bit geometry",
        "",
        "| Site | Rank | Phase at tau=0.9 | beta_1 | admitted generators | w1 gate | tau_conn | tau_cycle |",
        "|---|---:|---|---:|---:|---|---:|---:|",
    ]
    for row in result["main"]["site_results"]:
        phase = row["phase_at_registered_floor"]
        critical = row["curve"]["critical_floors"]
        lines.append(
            f"| {row['site']} | {row['rank']} | {phase['phase']} | {phase['beta_1']} | "
            f"{row['admitted_generator_count']} | {str(row['w1_gate_passed']).lower()} | "
            f"{critical['tau_conn']} | {critical['tau_cycle']} |"
        )
    precision = result["precision_control"]["comparison"]
    lines.extend(
        [
            "",
            "## Unquantized float16 control",
            "",
            f"Status: `{precision['status']}`. Common admitted loops: {len(precision.get('common_admitted_loop_ids', []))}. Determinant-sign agreement: {precision.get('determinant_sign_agreement')}.",
            "",
            "Float16 is an unquantized full-weight control with float32-stored activations. It is not a float32 model run.",
            "",
            "## Claim boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--causal-protocol", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--authorization", type=Path, required=True)
    value.add_argument("--main-base-index", type=Path, required=True)
    value.add_argument("--main-naive-index", type=Path, required=True)
    value.add_argument("--control-base-index", type=Path, required=True)
    value.add_argument("--control-naive-index", type=Path, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    value.add_argument("--seed", type=int, default=2026071702)
    return value


def main() -> None:
    args = parser().parse_args()
    _validate_authorization(args)
    result = analyze_stage_b(
        protocol_path=args.protocol,
        causal_protocol_path=args.causal_protocol,
        manifest_path=args.manifest,
        main_indices={"base": args.main_base_index, "naive_qlora": args.main_naive_index},
        control_indices={"base": args.control_base_index, "naive_qlora": args.control_naive_index},
        output_dir=args.output_dir,
        seed=args.seed,
    )
    write_once_or_equal(
        args.output_dir / "REPORT.md", _report(result).encode("utf-8")
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
