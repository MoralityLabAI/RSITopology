"""Run the sealed Qwen precision frustration-margin correction analysis."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import canonical_json_bytes, runtime_environment, sha256_file, write_once_or_equal  # noqa: E402
from rsi_topology.qwen_precision_frustration_margin import analyze, load_protocol  # noqa: E402


AUTH_SCHEMA = "qwen_holonomy_geometry_analysis_authorization_v0_1"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _match(item: Mapping[str, Any], path: Path, label: str) -> None:
    if Path(str(item.get("path", ""))).resolve() != path.resolve():
        raise ValueError(f"authorized {label} path differs")
    if not path.is_file() or sha256_file(path) != item.get("sha256"):
        raise ValueError(f"authorized {label} changed")


def validate_authorization(args: argparse.Namespace) -> dict[str, Any]:
    value = _json(args.authorization.resolve())
    if value.get("schema_version") != AUTH_SCHEMA or value.get("status") != "authorized_for_analysis":
        raise ValueError("authorization is invalid")
    if value.get("caps_confirmed_by_user") is not True or value.get("environment_lock") != runtime_environment():
        raise ValueError("caps or environment differ")
    if value.get("scientific_protocol_sha256") != sha256_file(args.protocol):
        raise ValueError("correction protocol differs")
    if Path(str(value.get("output_dir", ""))).resolve() != args.output_dir.resolve():
        raise ValueError("output directory differs")
    for label, item, path in (
        ("scientific protocol", value["parent_scientific_protocol"], args.scientific_protocol),
        ("filtration result", value["filtration_result"], args.filtration_result),
        ("filtration receipt", value["filtration_run_receipt"], args.filtration_run_receipt),
    ):
        _match(item, path, label)
    sources, hashes = value.get("source_paths"), value.get("source_sha256")
    if not isinstance(sources, Mapping) or not isinstance(hashes, Mapping) or set(sources) != set(hashes):
        raise ValueError("source universe differs")
    for name, raw in sources.items():
        path = Path(str(raw))
        if not path.is_file() or sha256_file(path) != hashes[name]:
            raise ValueError(f"authorized source changed: {name}")
    supplied = {
        "fourbit_base": args.fourbit_base_index,
        "fourbit_naive": args.fourbit_naive_index,
        "float16_base": args.float16_base_index,
        "float16_naive": args.float16_naive_index,
    }
    for name, path in supplied.items():
        _match(value["capture_indices"][name], path, name)
    for field in ("outcomes_consumed", "generation", "gradients", "weight_mutation"):
        if value.get(field) is not False:
            raise ValueError(f"authorization does not declare {field}=false")
    return value


def _event(path: Path, value: Mapping[str, Any]) -> None:
    row = {**value, "ts_utc": datetime.now(timezone.utc).isoformat()}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def _figure(result: Mapping[str, Any], output: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    graphs = sorted(result["graphs"], key=lambda row: (row["site"], row["precision"]))
    points = np.asarray([row["minimum_frustration_margin_interval"]["point"] for row in graphs])
    lower = np.asarray([row["minimum_frustration_margin_interval"]["lower_descriptive_90"] for row in graphs])
    upper = np.asarray([row["minimum_frustration_margin_interval"]["upper_descriptive_90"] for row in graphs])
    x = np.arange(len(graphs))
    fig, ax = plt.subplots(figsize=(8.5, 5))
    # Percentile ranges can exclude the full-sample max-statistic point. Draw
    # intervals independently rather than using errorbar's nonnegative yerr.
    ax.vlines(x, lower, upper, color="tab:blue", linewidth=2, label="descriptive 90% percentile range")
    ax.scatter(x, points, color="black", zorder=3, label="full-sample point")
    ax.axhline(0.0, color="tab:red", linestyle="--", label="w1 liveness boundary")
    ax.set_xticks(x, [f"{row['precision']}\n{row['site'].split('.')[-1]}" for row in graphs])
    ax.set_ylabel("minimum frustration margin (degrees)")
    ax.set_title("Distance to the 180° projective frustration bound")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    path = output / "figure_frustration_margins.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _report(result: Mapping[str, Any]) -> str:
    lines = [
        "# Frustration-margin correction to the rank-one holonomy interpretation",
        "",
        f"**Registered category:** `{result['result_category']}`",
        "",
        "The parent receipts remain valid, but their positive rank-one holonomy signs were geometrically forced: every conservative simple-cycle angle budget stayed below 180°. They are not empirical evidence that w1 is precision-stable.",
        "",
        "## Graph-level angle budgets",
        "",
        "| precision | site | max budget | frustration margin | upper budget percentile | forced with 90% support |",
        "|---|---|---:|---:|---:|---|",
    ]
    for graph in result["graphs"]:
        budget = graph["maximum_angle_budget_interval"]
        margin = graph["minimum_frustration_margin_interval"]
        lines.append(
            f"| {graph['precision']} | {graph['site']} | {budget['point']:.3f}° | {margin['point']:.3f}° | {budget['upper_descriptive_90']:.3f}° | {graph['forced_orientable_with_90_support']} |"
        )
    lines.extend(["", "## Quantization erosion", ""])
    for row in result["quantization_erosions"]:
        lines.append(
            f"- `{row['site']}`: {row['point']:.3f}° (descriptive 90% [{row['lower_descriptive_90']:.3f}, {row['upper_descriptive_90']:.3f}]); relative point erosion {100.0 * row['relative_erosion_point']:.1f}%; established={row['quantization_erosion_established']}."
        )
    lines.extend(
        [
            "",
            "## Corrected claim",
            "",
            "Four-bit quantization compressed rank-one support margins, caused one local support-gate crossing, and eroded the loop angle budget toward the 180° frustration bound, while every measured cycle remained inside the geometrically forced orientable regime. On this capture, w1 carries no information beyond edge lineages: the frustration margin, not the class, is the live graded diagnostic.",
            "",
            "The bootstrap ranges are descriptive percentile intervals for max-type statistics. The full-sample point may lie outside them; no calibrated coverage claim is made.",
            "",
            "## Claim boundary",
            "",
            str(result["claim_boundary"]),
        ]
    )
    return "\n".join(lines) + "\n"


def main(args: argparse.Namespace) -> None:
    auth = validate_authorization(args)
    load_protocol(args.protocol)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    events = output / "analysis_events.jsonl"
    _event(events, {"event": "start_or_resume", "authorization_sha256": sha256_file(args.authorization)})
    result = analyze(
        protocol_path=args.protocol,
        scientific_protocol_path=args.scientific_protocol,
        filtration_result_path=args.filtration_result,
        manifest_path=args.manifest,
        fourbit_indices={"base": args.fourbit_base_index, "naive_qlora": args.fourbit_naive_index},
        float16_indices={"base": args.float16_base_index, "naive_qlora": args.float16_naive_index},
        output_dir=output,
        progress=lambda value: _event(events, value),
    )
    figure = _figure(result, output)
    report = output / "REPORT_SUPERSEDING_INTERPRETATION.md"
    write_once_or_equal(report, _report(result).encode("utf-8"))
    _event(events, {"event": "complete", "result_category": result["result_category"]})
    receipt = {
        "schema_version": "qwen08_precision_frustration_margin_run_receipt_v0_1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": auth["run_id"],
        "authorization_sha256": sha256_file(args.authorization),
        "protocol_sha256": sha256_file(args.protocol),
        "analysis_result_sha256": sha256_file(output / "analysis_result.json"),
        "checkpoint_count": len(list((output / "checkpoints").glob("block_*.json"))),
        "result_category": result["result_category"],
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    write_once_or_equal(output / "run_receipt.json", canonical_json_bytes(receipt))
    files = [output / "analysis_result.json", report, figure, events, output / "run_receipt.json"]
    release = {"schema_version": "qwen08_precision_frustration_margin_release_manifest_v0_1", "files": {path.name: sha256_file(path) for path in files}}
    write_once_or_equal(output / "release_manifest.json", canonical_json_bytes(release))
    print(json.dumps({"status": "completed", **receipt}, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--authorization", type=Path, required=True)
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--scientific-protocol", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--filtration-result", type=Path, required=True)
    value.add_argument("--filtration-run-receipt", type=Path, required=True)
    value.add_argument("--fourbit-base-index", type=Path, required=True)
    value.add_argument("--fourbit-naive-index", type=Path, required=True)
    value.add_argument("--float16-base-index", type=Path, required=True)
    value.add_argument("--float16-naive-index", type=Path, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    return value


if __name__ == "__main__":
    main(parser().parse_args())
