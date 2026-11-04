from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREDECESSOR = HERE.parent / "repair_v0_26_1" / "verify_repair_v0_26_1.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location(
        "offset_access_verify_v0_26_1", PREDECESSOR
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load sealed predecessor verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


if __name__ == "__main__":
    main()
