from __future__ import annotations

import json
from pathlib import Path

from matrix_game_bridge import build_result


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "matrix_game_bridge_v1_2.json"


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
        raise SystemExit(f"matrix-game bridge gates failed: {failed}")
    print(
        "ASMP-3 matrix-game bridge certified: "
        f"{len(result['gates'])}/{len(result['gates'])} gates"
    )


if __name__ == "__main__":
    main()
