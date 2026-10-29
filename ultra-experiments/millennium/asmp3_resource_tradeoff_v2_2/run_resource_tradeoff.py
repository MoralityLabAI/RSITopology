from __future__ import annotations

import json
from pathlib import Path

from resource_tradeoff import build_result


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "resource_tradeoff_v2_2.json"


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
        raise SystemExit(f"resource-tradeoff gates failed: {failed}")
    print(
        "ASMP-3 resource tradeoff certified: "
        f"{len(result['gates'])}/{len(result['gates'])} gates, "
        f"{len(result['frontier_rows'])} frontier points"
    )


if __name__ == "__main__":
    main()
