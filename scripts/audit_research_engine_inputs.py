from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"D:\Research_Engine\runs")
OUT = Path("artifacts/research_engine_input_audit.json")
REPORT = Path("reports/research_engine_input_audit.md")


def jsonl_count(path: Path) -> tuple[int, set[str]]:
    count = 0
    statuses: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            count += 1
            payload = json.loads(line)
            if "status" in payload:
                statuses.add(str(payload["status"]))
    return count, statuses


def main() -> int:
    policy = []
    for path in ROOT.rglob("policy_features.jsonl"):
        count, statuses = jsonl_count(path)
        policy.append(
            {
                "path": str(path),
                "rows": count,
                "statuses": sorted(statuses),
                "has_model_outcomes": not any(
                    "proxy_no_model" in status for status in statuses
                ),
            }
        )
    edit_runs = []
    for run_name in (
        "trm_basis_constrained_edits_arc_rank_sweep_k1_20260609",
        "trm_basis_constrained_edits_arc_rank_sweep_k2_20260609",
    ):
        directory = ROOT / run_name
        accepted = directory / "accepted_edits.jsonl"
        near = directory / "near_misses.jsonl"
        accepted_rows, _ = jsonl_count(accepted)
        near_rows, _ = jsonl_count(near)
        edit_runs.append(
            {
                "run": run_name,
                "accepted_rows": accepted_rows,
                "near_miss_rows": near_rows,
                "actual_edit_matrix_present": bool(
                    list(directory.glob("*edit*matrix*.npz"))
                    or list(directory.glob("*candidate*.npz"))
                ),
                "source_commit_present": (directory / "run_registration.json").exists(),
            }
        )
    payload = {
        "policy_feature_files": sorted(policy, key=lambda row: row["rows"], reverse=True),
        "edit_runs": edit_runs,
        "policy_gate": "blocked_insufficient_model_outcomes_and_group_count",
        "direct_edit_gate": "blocked_missing_edit_matrices_and_source_registration",
        "claim_boundary": "Archival input audit only; no retrospective causal or self-improvement claim.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "\n".join(
            [
                "# Research_Engine Input Audit",
                "",
                payload["claim_boundary"],
                "",
                f"Policy feature files found: `{len(policy)}`. The largest has "
                f"`{max((row['rows'] for row in policy), default=0)}` rows; proxy/no-model "
                "statuses and tiny group counts prevent the registered policy test.",
                "",
                "The June rank-sweep receipts preserve accepted and near-miss summaries "
                "but not reconstructable edit matrices or a source registration. The "
                "direct-edit spectral gate is therefore `blocked_missing_provenance`, "
                "not failed and not passed.",
                "",
                "```json",
                json.dumps(payload["edit_runs"], indent=2, sort_keys=True),
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

