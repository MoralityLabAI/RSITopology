from __future__ import annotations

import importlib.util
import math
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_qwen08_completion_audits.py"
SPEC = importlib.util.spec_from_file_location("run_qwen08_completion_audits", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_extract_probability_from_current_post_sampling_schema() -> None:
    assert MODULE.extract_probability({"probs": [{"prob": 0.25}]}) == 0.25


def test_extract_probability_from_current_logprob_schema() -> None:
    observed = MODULE.extract_probability({"probs": [{"logprob": math.log(0.4)}]})
    assert observed is not None
    assert abs(observed - 0.4) < 1e-12


def test_extract_probability_from_legacy_nested_schema() -> None:
    payload = {"completion_probabilities": [{"probs": [{"prob": 0.75}]}]}
    assert MODULE.extract_probability(payload) == 0.75
