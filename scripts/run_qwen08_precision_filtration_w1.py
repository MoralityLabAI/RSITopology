"""Run the sealed Qwen precision filtration and rank-one w1 analysis."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import canonical_json_bytes, runtime_environment, sha256_file, write_once_or_equal  # noqa: E402
from rsi_topology.qwen_precision_filtration_w1 import analyze, load_protocol  # noqa: E402


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
        raise ValueError("analysis authorization is invalid")
    if value.get("caps_confirmed_by_user") is not True or value.get("environment_lock") != runtime_environment():
        raise ValueError("caps or environment differ from authorization")
    if value.get("scientific_protocol_sha256") != sha256_file(args.protocol):
        raise ValueError("filtration/w1 protocol differs")
    if value.get("prompt_manifest_sha256") != sha256_file(args.manifest):
        raise ValueError("prompt manifest differs")
    if Path(str(value.get("output_dir", ""))).resolve() != args.output_dir.resolve():
        raise ValueError("output directory differs")
    for field in ("outcomes_consumed", "generation", "gradients", "weight_mutation"):
        if value.get(field) is not False:
            raise ValueError(f"authorization does not declare {field}=false")
    _match(value["parent_scientific_protocol"], args.parent_protocol, "parent protocol")
    _match(value["parent_analysis_result"], args.parent_result, "parent result")
    _match(value["parent_run_receipt"], args.parent_run_receipt, "parent receipt")
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
    if set(value.get("capture_indices", {})) != set(supplied):
        raise ValueError("capture-index universe differs")
    for name, path in supplied.items():
        _match(value["capture_indices"][name], path, name)
    return value


def _event(path: Path, value: Mapping[str, Any]) -> None:
    row = {**value, "ts_utc": datetime.now(timezone.utc).isoformat()}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def _write_jsonl(path: Path, rows: list[Mapping[str, Any]]) -> None:
    payload = b"".join(canonical_json_bytes(row).rstrip(b"\n") + b"\n" for row in rows)
    write_once_or_equal(path, payload)


def _write_csv(path: Path, fieldnames: list[str], rows: list[Mapping[str, Any]]) -> None:
    import io

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    write_once_or_equal(path, stream.getvalue().encode("utf-8"))


def _figures(result: Mapping[str, Any], output: Path) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    figures = []
    paired = [row for row in result["paired_precision_records"] if row["site"] == "model.layers.19"]
    paired.sort(key=lambda row: (row["state"], row["context_shard"]))
    x = np.arange(len(paired))
    point = np.asarray([row["float16_minus_fourbit_complete_margin_point"] for row in paired])
    lower = np.asarray([row["float16_minus_fourbit_complete_margin_lower_95"] for row in paired])
    upper = np.asarray([row["float16_minus_fourbit_complete_margin_upper_95"] for row in paired])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.errorbar(x, point, yerr=np.vstack((point - lower, upper - point)), fmt="o", capsize=3)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x, [f"{row['state']}\n{row['context_shard']}" for row in paired], rotation=25, ha="right")
    ax.set_ylabel("float16 − 4bit complete margin")
    ax.set_title("Paired precision margins (central 90% bootstrap intervals)")
    fig.tight_layout()
    path = output / "figure_a_paired_margins.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    figures.append(path)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey=True)
    for ax, graph in zip(axes.flat, sorted(result["graphs"], key=lambda row: (row["site"], row["precision"]))):
        rows = sorted(graph["filtration"], key=lambda row: row["tau"])
        tau = [row["tau"] for row in rows]
        ax.step(tau, [row["beta_1"] for row in rows], where="post", label="β₁")
        ax.step(tau, [row["component_count"] for row in rows], where="post", label="components", alpha=0.75)
        ax.axvline(0.9, color="black", linestyle="--", linewidth=0.8)
        ax.axvline(graph["tau_cycle"]["point"], color="tab:red", linewidth=1.1)
        ax.set_title(f"{graph['precision']} · {graph['site'].split('.')[-1]}")
        ax.grid(alpha=0.2)
    axes[0, 0].legend()
    fig.supxlabel("lineage floor τ")
    fig.supylabel("filtration count")
    fig.suptitle("Lineage percolation and cycle availability")
    fig.tight_layout()
    path = output / "figure_b_filtration_curves.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    figures.append(path)

    support = result["support_records"]
    row_keys = [(p, s, site) for p in ("4bit", "float16") for s in ("base", "naive_qlora") for site in ("model.layers.19", "model.layers.23")]
    matrix = np.full((len(row_keys), 4), np.nan)
    for i, key in enumerate(row_keys):
        for row in support:
            if (row["precision"], row["state"], row["site"]) == key:
                matrix[i, int(row["context_shard"].split("-")[-1])] = row["signed_support_margin"]
    fig, ax = plt.subplots(figsize=(8, 6))
    limit = max(abs(np.nanmin(matrix)), abs(np.nanmax(matrix)))
    image = ax.imshow(matrix, cmap="RdYlGn", vmin=-limit, vmax=limit, aspect="auto")
    ax.set_xticks(range(4), [f"shard-{i:02d}" for i in range(4)])
    ax.set_yticks(range(len(row_keys)), [f"{p} · {s} · {site.split('.')[-1]}" for p, s, site in row_keys])
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i,j]:.3f}", ha="center", va="center", fontsize=7)
    fig.colorbar(image, ax=ax, label="signed support margin")
    ax.set_title("Rank-one support across precision, state, site, and context")
    fig.tight_layout()
    path = output / "figure_c_support_heatmap.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    figures.append(path)
    return figures


def _report(result: Mapping[str, Any], *, protocol_sha: str, manifest_sha: str) -> str:
    lines = [
        "# Runtime precision as a probe of identity-object geometry",
        "",
        f"**Registered w1 result:** `{result['w1_category']}`",
        f"**Percolation shift established:** `{result['percolation_shift_established']}`",
        "",
        "This compares four-bit NF4 double-quant with float16 compute against unquantized float16 weights. It is not an fp32 arithmetic comparison.",
        "",
        "## Filtration thresholds",
        "",
        "| precision | site | tau_conn | tau_cycle | tau_loop | fragility |",
        "|---|---|---:|---:|---:|---|",
    ]
    for graph in result["graphs"]:
        lines.append(
            f"| {graph['precision']} | {graph['site']} | {graph['tau_conn']['point']:.6f} | {graph['tau_cycle']['point']:.6f} | {graph['tau_loop']['point']:.6f} | {graph['fragility_classification']} ({graph['fragility_margin_point']:.6f}) |"
        )
    lines.extend(
        [
            "",
            "## Rank-one holonomy",
            "",
            "The frozen 2×4 ladder has no ten-edge simple cycle: its longest simple cycle has eight edges. The analysis evaluates all six connected simple cycles plus the remaining nonzero GF(2) cycle-chain. Canonical angles are suppressed because O(1) holonomy is the sign ±1.",
            "",
        ]
    )
    for graph in result["graphs"]:
        negative = [row["cycle_id"] for row in graph["cycles"] if row["geometry_validation_sign"] < 0]
        lines.append(f"- `{graph['graph_id']}`: {len(negative)} negative cycle classes; gauge mismatches {graph['gauge_preflight']['determinant_decision_mismatches']}.")
    lines.extend(
        [
            "",
            "## Reproducibility",
            "",
            f"- Protocol SHA-256: `{protocol_sha}`",
            "- Prompt payload SHA-256: `87d2f05eb24e7074943b6625c907bf08362db5ffa5ac24f6a313f7d75806c14e`",
            f"- Prompt manifest SHA-256: `{manifest_sha}`",
            "- Resampling: 256 paired, stratified replicates; seed 2026071719.",
            "- No multiplicity correction was registered; individual cell intervals are descriptive.",
            "",
            "## Claim boundary",
            "",
            str(result["claim_boundary"]),
            "",
            "Stage B and 1.7B results are context only and are not pooled with this analysis.",
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
        parent_protocol_path=args.parent_protocol,
        manifest_path=args.manifest,
        parent_result_path=args.parent_result,
        fourbit_indices={"base": args.fourbit_base_index, "naive_qlora": args.fourbit_naive_index},
        float16_indices={"base": args.float16_base_index, "naive_qlora": args.float16_naive_index},
        output_dir=output,
        progress=lambda value: _event(events, value),
    )
    edges = [{"graph_id": graph["graph_id"], **row} for graph in result["graphs"] for row in graph["edges"]]
    cycles = [{"graph_id": graph["graph_id"], **row} for graph in result["graphs"] for row in graph["cycles"]]
    _write_jsonl(output / "edge_receipts.jsonl", edges)
    _write_jsonl(output / "cycle_receipts.jsonl", cycles)
    _write_csv(
        output / "filtration_thresholds.csv",
        ["precision", "site", "tau_conn", "tau_cycle", "tau_loop", "fragility_margin", "fragility_classification"],
        [
            {
                "precision": graph["precision"],
                "site": graph["site"],
                "tau_conn": graph["tau_conn"]["point"],
                "tau_cycle": graph["tau_cycle"]["point"],
                "tau_loop": graph["tau_loop"]["point"],
                "fragility_margin": graph["fragility_margin_point"],
                "fragility_classification": graph["fragility_classification"],
            }
            for graph in result["graphs"]
        ],
    )
    figures = _figures(result, output)
    report = output / "REPORT.md"
    write_once_or_equal(report, _report(result, protocol_sha=sha256_file(args.protocol), manifest_sha=sha256_file(args.manifest)).encode("utf-8"))
    _event(events, {"event": "complete", "w1_category": result["w1_category"]})
    receipt = {
        "schema_version": "qwen08_precision_filtration_w1_run_receipt_v0_1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": auth["run_id"],
        "authorization_sha256": sha256_file(args.authorization),
        "protocol_sha256": sha256_file(args.protocol),
        "analysis_result_sha256": sha256_file(output / "analysis_result.json"),
        "checkpoint_count": len(list((output / "checkpoints").glob("block_*.json"))),
        "w1_category": result["w1_category"],
        "percolation_shift_established": result["percolation_shift_established"],
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    write_once_or_equal(output / "run_receipt.json", canonical_json_bytes(receipt))
    files = [output / "analysis_result.json", output / "edge_receipts.jsonl", output / "cycle_receipts.jsonl", output / "filtration_thresholds.csv", report, events, output / "run_receipt.json", *figures]
    manifest = {"schema_version": "qwen08_precision_filtration_w1_release_manifest_v0_1", "files": {path.name: sha256_file(path) for path in files}}
    write_once_or_equal(output / "release_manifest.json", canonical_json_bytes(manifest))
    print(json.dumps({"status": "completed", **receipt}, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--authorization", type=Path, required=True)
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--parent-protocol", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--parent-result", type=Path, required=True)
    value.add_argument("--parent-run-receipt", type=Path, required=True)
    value.add_argument("--fourbit-base-index", type=Path, required=True)
    value.add_argument("--fourbit-naive-index", type=Path, required=True)
    value.add_argument("--float16-base-index", type=Path, required=True)
    value.add_argument("--float16-naive-index", type=Path, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    return value


if __name__ == "__main__":
    main(parser().parse_args())
