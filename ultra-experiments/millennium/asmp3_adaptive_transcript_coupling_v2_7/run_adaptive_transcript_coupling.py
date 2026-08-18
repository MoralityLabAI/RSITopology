from __future__ import annotations

import json
from pathlib import Path

from adaptive_transcript_coupling import build_result


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "adaptive_transcript_coupling_v2_7.json"


def main() -> None:
    result = build_result()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    passed = sum(result["gates"].values())
    total = len(result["gates"])
    if not result["certified"]:
        failed = [name for name, ok in result["gates"].items() if not ok]
        raise SystemExit(f"adaptive-transcript gates failed: {failed}")
    print(f"ASMP-3 adaptive transcript coupling certified: {passed}/{total} gates")


if __name__ == "__main__":
    main()
