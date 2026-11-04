"""Exact binary safety-deficiency calculations for ASMP-2."""

from __future__ import annotations

import hashlib
import math
from fractions import Fraction
from pathlib import Path


def majority_success(sample_size: int, signal: Fraction) -> Fraction:
    """Minimax success for the symmetric binary experiment.

    In world s, each observation equals s with probability 1/2+signal.
    The safe action is -s. Majority testing is minimax; an even tie is
    randomized uniformly.
    """

    if sample_size < 0:
        raise ValueError("sample_size must be nonnegative")
    if not 0 <= signal < Fraction(1, 2):
        raise ValueError("signal must lie in [0,1/2)")
    if sample_size == 0:
        return Fraction(1, 2)

    correct = Fraction(1, 2) + signal
    incorrect = Fraction(1, 2) - signal
    threshold = sample_size // 2 + 1
    success = sum(
        Fraction(math.comb(sample_size, count))
        * correct**count
        * incorrect ** (sample_size - count)
        for count in range(threshold, sample_size + 1)
    )
    if sample_size % 2 == 0:
        tie_count = sample_size // 2
        tie_probability = (
            Fraction(math.comb(sample_size, tie_count))
            * correct**tie_count
            * incorrect**tie_count
        )
        success += tie_probability / 2
    return success


def safety_deficiency(sample_size: int, signal: Fraction) -> Fraction:
    return 1 - majority_success(sample_size, signal)


def sample_complexity(
    signal: Fraction, delta: Fraction, *, maximum: int = 100_000
) -> int | None:
    """Return the smallest n with deficiency <= delta, or None if unavailable."""

    if not 0 <= delta < 1:
        raise ValueError("delta must lie in [0,1)")
    if signal == 0 and delta < Fraction(1, 2):
        return None
    for sample_size in range(maximum + 1):
        if safety_deficiency(sample_size, signal) <= delta:
            return sample_size
    return None


def best_environment(signals: tuple[Fraction, ...]) -> int:
    """Return the lowest index with greatest one-sample safety value."""

    if not signals:
        raise ValueError("at least one candidate environment is required")
    if any(not 0 <= signal < Fraction(1, 2) for signal in signals):
        raise ValueError("signals must lie in [0,1/2)")
    return max(range(len(signals)), key=lambda index: (signals[index], -index))


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_deficiency_result() -> dict[str, object]:
    here = Path(__file__).resolve().parent
    theorem = here / "DECISION_DEFICIENCY_REDUCTION_v0_3.md"
    signals = (
        Fraction(0),
        Fraction(1, 16),
        Fraction(1, 8),
        Fraction(1, 4),
    )
    sample_sizes = tuple(range(10))
    table = {
        fraction_text(signal): {
            str(sample_size): {
                "success": fraction_text(majority_success(sample_size, signal)),
                "deficiency": fraction_text(safety_deficiency(sample_size, signal)),
            }
            for sample_size in sample_sizes
        }
        for signal in signals
    }
    delta = Fraction(1, 10)
    complexities = {
        fraction_text(signal): sample_complexity(signal, delta, maximum=10_000)
        for signal in signals
    }
    active_signals = (Fraction(1, 16), Fraction(1, 4), Fraction(1, 8))
    gates = {
        "zero_signal_deficiency_is_one_half_for_all_n": all(
            safety_deficiency(sample_size, Fraction(0)) == Fraction(1, 2)
            for sample_size in sample_sizes
        ),
        "zero_signal_sample_complexity_is_infinite_below_one_half": (
            sample_complexity(Fraction(0), Fraction(49, 100)) is None
        ),
        "positive_signal_eventually_crosses_delta": all(
            complexities[fraction_text(signal)] is not None for signal in signals[1:]
        ),
        "success_monotone_across_registered_signals": all(
            majority_success(sample_size, signals[index])
            <= majority_success(sample_size, signals[index + 1])
            for sample_size in sample_sizes
            for index in range(len(signals) - 1)
        ),
        "active_choice_is_largest_signal": best_environment(active_signals) == 1,
    }
    return {
        "schema_version": "asmp2_safety_deficiency_v0_3",
        "theorem_sha256": sha256(theorem),
        "signals": [fraction_text(signal) for signal in signals],
        "sample_sizes": list(sample_sizes),
        "exact_table": table,
        "target_delta": fraction_text(delta),
        "sample_complexities": {
            key: "infinity" if value is None else value
            for key, value in complexities.items()
        },
        "active_signals": [fraction_text(signal) for signal in active_signals],
        "active_choice_index": best_environment(active_signals),
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "claim_boundary": (
            "exact binary specialization of decision-specific safety deficiency; "
            "not a general closed-form rate for arbitrary semiparametric classes"
        ),
    }
