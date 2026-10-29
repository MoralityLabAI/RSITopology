from __future__ import annotations

import json
from pathlib import Path

from weighted_noise_subset_sum import build_result


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "weighted_noise_subset_sum_v1_6.json"


def main() -> None:
    result = build_result()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["certified"]:
        failed = [name for name, passed in result["gates"].items() if not passed]
        raise SystemExit(f"weighted-noise gates failed: {failed}")
    print(
        "ASMP-3 weighted-noise subset-sum boundary certified: "
        f"{len(result['gates'])}/{len(result['gates'])} gates, "
        f"{len(result['weighted_rows'])} rows"
    )


if __name__ == "__main__":
    main()
