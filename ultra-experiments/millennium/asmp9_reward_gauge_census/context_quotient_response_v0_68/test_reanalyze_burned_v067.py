import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def test_reanalysis_on_minimal_complete_fixture(tmp_path: Path) -> None:
    records = []
    scores = {
        ("balanced", None): (0.0, 0.0),
        ("balanced_washout", None): (0.0, 0.0),
        ("content", 0): (2.0, -2.0),
        ("content", 1): (-2.0, 2.0),
        ("label", 0): (0.5, -0.5),
        ("label", 1): (-0.5, 0.5),
        ("content_washout", 0): (0.1, -0.1),
        ("content_washout", 1): (-0.1, 0.1),
    }
    for (arm, target), by_order in scores.items():
        for order, raw_score in enumerate(by_order):
            records.append(
                {
                    "scenario_id": "fixture",
                    "family": "fixture_family",
                    "arm": arm,
                    "target": target,
                    "display_order": order,
                    "raw_log_odds_a_over_b": raw_score,
                }
            )
    records_path = tmp_path / "records.jsonl"
    records_path.write_text(
        "".join(json.dumps(row) + "\n" for row in records), encoding="utf-8"
    )
    output_path = tmp_path / "result.json"
    subprocess.run(
        [
            sys.executable,
            str(HERE / "reanalyze_burned_v067.py"),
            "--records",
            str(records_path),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["endpoint_summary"]["specificity"][
        "positive_in_both_orders"
    ] == 2
    assert result["endpoint_summary"]["washout_effect"][
        "positive_in_both_orders"
    ] == 2
    assert result["status"] == "post_hoc_design_evidence_only"
