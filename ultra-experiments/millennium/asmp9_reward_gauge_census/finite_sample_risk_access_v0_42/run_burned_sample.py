"""Run one explicitly burned sampled integration before registration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sampled_confirmation import run_sampled_confirmation


BASE = Path(__file__).resolve().parent


def main() -> None:
    output = BASE / "DEVELOPMENT_SAMPLED_RESULT_v0_42.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    seed = hashlib.sha256(
        b"asmp9-v0.42-burned-sampled-development"
    ).digest()
    result = run_sampled_confirmation(
        samples_per_target=4800,
        seed=seed,
    )
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
