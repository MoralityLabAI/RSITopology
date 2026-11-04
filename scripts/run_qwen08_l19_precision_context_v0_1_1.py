"""Execute the sealed, resumable v0.1.1 Qwen precision/context analysis."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_qwen08_l19_precision_context import _report, validate_authorization  # noqa: E402
from rsi_topology.godel_capture import (  # noqa: E402
    canonical_json_bytes,
    sha256_file,
    write_once_or_equal,
)
from rsi_topology.qwen_precision_context_v0_1_1 import (  # noqa: E402
    AMENDMENT_ID,
    analyze_precision_context_v0_1_1,
    validate_amendment,
)


def _append_event(path: Path, value: Mapping[str, Any]) -> None:
    item = {**value, "ts_utc": datetime.now(timezone.utc).isoformat()}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def main(args: argparse.Namespace) -> None:
    authorization = validate_authorization(args)
    amendment = validate_amendment(
        args.compute_amendment, scientific_protocol_path=args.protocol
    )
    expected = authorization.get("compute_amendment")
    if not isinstance(expected, Mapping):
        raise ValueError("authorization lacks compute amendment")
    if Path(str(expected.get("path", ""))).resolve() != args.compute_amendment.resolve():
        raise ValueError("authorized compute-amendment path differs")
    if expected.get("sha256") != sha256_file(args.compute_amendment):
        raise ValueError("authorized compute amendment changed")
    if expected.get("protocol_id") != AMENDMENT_ID:
        raise ValueError("authorized compute amendment ID differs")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    events = output / "analysis_events.jsonl"
    _append_event(
        events,
        {
            "event": "analysis_start_or_resume",
            "authorization_sha256": sha256_file(args.authorization),
            "compute_amendment_sha256": sha256_file(args.compute_amendment),
        },
    )
    result = analyze_precision_context_v0_1_1(
        amendment_path=args.compute_amendment,
        protocol_path=args.protocol,
        manifest_path=args.manifest,
        fourbit_indices={
            "base": args.fourbit_base_index,
            "naive_qlora": args.fourbit_naive_index,
        },
        float16_indices={
            "base": args.float16_base_index,
            "naive_qlora": args.float16_naive_index,
        },
        output_dir=output,
        progress=lambda value: _append_event(events, value),
    )
    report_path = output / "REPORT.md"
    write_once_or_equal(report_path, _report(result).encode("utf-8"))
    checkpoint_files = sorted((output / "checkpoints").rglob("block_*.json"))
    receipt = {
        "schema_version": "qwen08_l19_precision_context_run_receipt_v0_1_1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": authorization["run_id"],
        "authorization_sha256": sha256_file(args.authorization),
        "compute_amendment_sha256": sha256_file(args.compute_amendment),
        "analysis_result_sha256": sha256_file(output / "analysis_result.json"),
        "report_sha256": sha256_file(report_path),
        "checkpoint_file_count": len(checkpoint_files),
        "checkpoint_chain_terminal_hashes": {
            path.parent.name: sha256_file(path)
            for path in checkpoint_files
            if path == sorted(path.parent.glob("block_*.json"))[-1]
        },
        "result_category": result["result_category"],
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "scientific_decisions_changed_from_v0_1": False,
    }
    receipt_path = output / "run_receipt.json"
    write_once_or_equal(receipt_path, canonical_json_bytes(receipt))
    _append_event(events, {"event": "analysis_complete", "result_category": result["result_category"]})
    release = {
        "schema_version": "qwen08_l19_precision_context_release_manifest_v0_1_1",
        "files": {
            path.name: sha256_file(path)
            for path in (output / "analysis_result.json", report_path, receipt_path, events)
        },
        "checkpoint_file_count": len(checkpoint_files),
    }
    write_once_or_equal(output / "release_manifest.json", canonical_json_bytes(release))
    print(json.dumps({"status": "completed", **receipt}, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--authorization", type=Path, required=True)
    value.add_argument("--compute-amendment", type=Path, required=True)
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
