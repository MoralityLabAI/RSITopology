from __future__ import annotations

import json
from pathlib import Path

from trace_binding_extractor import build_result


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "trace_binding_extractor_v2_8.json"


def main() -> None:
    result = build_result()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if not result["certified"]:
        raise SystemExit(f"trace-binding gates failed: {[k for k,v in result['gates'].items() if not v]}")
    print(f"ASMP-3 trace binding extractor certified: {len(result['gates'])}/{len(result['gates'])} gates")


if __name__ == "__main__":
    main()
