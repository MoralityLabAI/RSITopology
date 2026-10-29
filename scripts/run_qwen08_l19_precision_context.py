"""Execute the sealed Qwen0.8B L19 precision/context analysis."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import (  # noqa: E402
    canonical_json_bytes,
    runtime_environment,
    sha256_file,
    write_once_or_equal,
)
from rsi_topology.qwen_precision_context import (  # noqa: E402
    analyze_precision_context,
    load_protocol,
)


AUTH_SCHEMA = "qwen_holonomy_geometry_analysis_authorization_v0_1"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _artifact_matches(item: Mapping[str, Any], path: Path, label: str) -> None:
    if Path(str(item.get("path", ""))).resolve() != path.resolve():
        raise ValueError(f"authorized {label} path differs")
    if not path.is_file() or sha256_file(path) != item.get("sha256"):
        raise ValueError(f"authorized {label} changed")


def validate_authorization(args: argparse.Namespace) -> dict[str, Any]:
    value = _json(args.authorization.resolve())
    if value.get("schema_version") != AUTH_SCHEMA or value.get("status") != "authorized_for_analysis":
        raise ValueError("analysis authorization is invalid")
    if value.get("caps_confirmed_by_user") is not True:
        raise ValueError("analysis caps were not explicitly confirmed")
    if value.get("environment_lock") != runtime_environment():
        raise ValueError("analysis environment differs from authorization")
    if value.get("scientific_protocol_sha256") != sha256_file(args.protocol):
        raise ValueError("analysis protocol binding differs")
    if value.get("prompt_manifest_sha256") != sha256_file(args.manifest):
        raise ValueError("analysis manifest binding differs")
    if Path(str(value.get("output_dir", ""))).resolve() != args.output_dir.resolve():
        raise ValueError("analysis output directory differs")
    if value.get("resource_caps", {}).get("swap_bytes") != 0:
        raise ValueError("analysis authorization permits swap")
    for field in ("outcomes_consumed", "generation", "gradients", "weight_mutation"):
        if value.get(field) is not False:
            raise ValueError(f"analysis authorization does not declare {field}=false")
    _artifact_matches(value["prompt_separation_receipt"], args.separation_receipt, "separation receipt")
    _artifact_matches(value["precision_pair_receipt"], args.pair_receipt, "precision-pair receipt")
    if _json(args.separation_receipt).get("passed") is not True:
        raise ValueError("prompt separation is not passed")
    if _json(args.pair_receipt).get("identical_except_runtime_precision") is not True:
        raise ValueError("precision prompt payloads are not identical")
    sources = value.get("source_paths")
    hashes = value.get("source_sha256")
    if not isinstance(sources, Mapping) or not isinstance(hashes, Mapping) or set(sources) != set(hashes):
        raise ValueError("authorized analysis source universe is incomplete")
    for name, raw in sources.items():
        path = Path(str(raw))
        if not path.is_file() or sha256_file(path) != hashes[name]:
            raise ValueError(f"authorized analysis source changed: {name}")
    supplied_indices = {
        "fourbit_base": args.fourbit_base_index,
        "fourbit_naive": args.fourbit_naive_index,
        "float16_base": args.float16_base_index,
        "float16_naive": args.float16_naive_index,
    }
    if set(value.get("capture_indices", {})) != set(supplied_indices):
        raise ValueError("authorized capture-index universe differs")
    for name, path in supplied_indices.items():
        _artifact_matches(value["capture_indices"][name], path, name)
    validation = value.get("hard_cap_validation_receipt")
    wrapper = value.get("hard_cap_wrapper")
    cleanup = value.get("cleanup_script")
    for label, item in (("hard-cap validation", validation), ("wrapper", wrapper), ("cleanup", cleanup)):
        if not isinstance(item, Mapping):
            raise ValueError(f"authorization lacks {label}")
        path = Path(str(item.get("path", "")))
        if not path.is_file() or sha256_file(path) != item.get("sha256"):
            raise ValueError(f"authorized {label} changed")
    validation_value = _json(Path(str(validation["path"])))
    if validation_value.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation receipt is not passed")
    if validation_value.get("wrapper", {}).get("sha256") != wrapper["sha256"]:
        raise ValueError("validation receipt does not bind wrapper")
    if validation_value.get("cleanup", {}).get("sha256") != cleanup["sha256"]:
        raise ValueError("validation receipt does not bind cleanup")
    return value


def _report(result: Mapping[str, Any]) -> str:
    lines = [
        "# Qwen0.8B paired precision/context result",
        "",
        f"**Registered category:** `{result['result_category']}`",
        "",
        "This outcome-free analysis compares four-bit NF4/float16-compute against unquantized float16 weights, with float32-stored activations in both arms. It is not a float32 arithmetic comparison.",
        "",
        "## Sentinel interaction",
        "",
        "```json",
        json.dumps(result["sentinel_interaction"], indent=2, sort_keys=True),
        "```",
        "",
        "## Cell support",
        "",
        "| precision | state | site | shard | signed margin | gate |",
        "|---|---|---|---|---:|---|",
    ]
    for row in result["support_records"]:
        lines.append(
            f"| {row['precision']} | {row['state']} | {row['site']} | {row['context_shard']} | {row['signed_support_margin']:.6f} | {row['passed_matched_random_label_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            str(result["claim_boundary"]),
            "",
            "Rank-one holonomy rows are diagnostics only; they neither add an attestation level nor authorize causal/VPD work.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(args: argparse.Namespace) -> None:
    authorization = validate_authorization(args)
    load_protocol(args.protocol)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    result = analyze_precision_context(
        protocol_path=args.protocol,
        manifest_path=args.manifest,
        fourbit_indices={"base": args.fourbit_base_index, "naive_qlora": args.fourbit_naive_index},
        float16_indices={"base": args.float16_base_index, "naive_qlora": args.float16_naive_index},
        output_dir=output,
    )
    report_path = output / "REPORT.md"
    write_once_or_equal(report_path, _report(result).encode("utf-8"))
    receipt = {
        "schema_version": "qwen08_l19_precision_context_run_receipt_v0_1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": authorization["run_id"],
        "authorization_sha256": sha256_file(args.authorization),
        "analysis_result_sha256": sha256_file(output / "analysis_result.json"),
        "report_sha256": sha256_file(report_path),
        "result_category": result["result_category"],
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    receipt_path = output / "run_receipt.json"
    write_once_or_equal(receipt_path, canonical_json_bytes(receipt))
    manifest = {
        "schema_version": "qwen08_l19_precision_context_release_manifest_v0_1",
        "files": {
            path.name: sha256_file(path)
            for path in (output / "analysis_result.json", report_path, receipt_path)
        },
    }
    write_once_or_equal(output / "release_manifest.json", canonical_json_bytes(manifest))
    print(json.dumps({"status": "completed", **receipt}, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--authorization", type=Path, required=True)
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--separation-receipt", type=Path, required=True)
    value.add_argument("--pair-receipt", type=Path, required=True)
    value.add_argument("--fourbit-base-index", type=Path, required=True)
    value.add_argument("--fourbit-naive-index", type=Path, required=True)
    value.add_argument("--float16-base-index", type=Path, required=True)
    value.add_argument("--float16-naive-index", type=Path, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    return value


if __name__ == "__main__":
    main(parser().parse_args())
