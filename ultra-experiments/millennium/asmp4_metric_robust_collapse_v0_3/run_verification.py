from __future__ import annotations

import json

from metric_harness import verification_payload


def main() -> int:
    payload = verification_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
