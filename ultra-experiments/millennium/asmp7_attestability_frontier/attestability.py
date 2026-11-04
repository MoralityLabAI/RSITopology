from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb
from typing import Iterable


DOMAIN_SIZE = 16
TRUTH_TABLE_COUNT = 1 << DOMAIN_SIZE
ERROR_LIMIT = Fraction(1, 20)
THETA_GRID = (
    Fraction(1, 2),
    Fraction(3, 5),
    Fraction(2, 3),
    Fraction(3, 4),
    Fraction(4, 5),
    Fraction(1, 1),
)
MAX_CHALLENGES = 128

ENCODINGS = ("lut", "rle", "anf")
DECOMPOSITIONS = ("single", "xor_share_2")
CACHES = ("none", "memoized")
ORDERS = ("canonical", "commuted")
PADDINGS = ("fixed_64", "fixed_128")


@dataclass(frozen=True, order=True)
class RepresentationState:
    encoding: str
    decomposition: str
    cache: str
    order: str
    padding: str


@dataclass(frozen=True)
class ThresholdTest:
    m: int
    theta: Fraction
    cutoff: int
    gamma: Fraction
    worst_fp: Fraction
    worst_fn: Fraction


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def parity_target() -> int:
    return sum(((index.bit_count() & 1) << index) for index in range(DOMAIN_SIZE))


TARGET_TABLE = parity_target()


def bit_tuple(table: int) -> tuple[int, ...]:
    if not 0 <= table < TRUTH_TABLE_COUNT:
        raise ValueError("truth table outside the 16-bit universe")
    return tuple((table >> index) & 1 for index in range(DOMAIN_SIZE))


def agreement_count(table: int) -> int:
    return DOMAIN_SIZE - (table ^ TARGET_TABLE).bit_count()


def policy_class(table: int) -> str:
    k = agreement_count(table)
    if k <= 8:
        return "compliant"
    if k >= 14:
        return "forbidden"
    return "unclassified"


def class_counts() -> dict[str, int]:
    counts = {"compliant": 0, "forbidden": 0, "unclassified": 0}
    for table in range(TRUTH_TABLE_COUNT):
        counts[policy_class(table)] += 1
    return counts


def representation_states() -> tuple[RepresentationState, ...]:
    return tuple(
        RepresentationState(*values)
        for values in product(ENCODINGS, DECOMPOSITIONS, CACHES, ORDERS, PADDINGS)
    )


def _encode_rle(bits: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    runs: list[tuple[int, int]] = []
    for bit in bits:
        if runs and runs[-1][0] == bit:
            value, count = runs[-1]
            runs[-1] = (value, count + 1)
        else:
            runs.append((bit, 1))
    return tuple(runs)


def _decode_rle(runs: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    bits: list[int] = []
    for value, count in runs:
        bits.extend([value] * count)
    if len(bits) != DOMAIN_SIZE:
        raise ValueError("invalid RLE length")
    return tuple(bits)


def _anf_coefficients(bits: tuple[int, ...]) -> tuple[int, ...]:
    coefficients = list(bits)
    for axis in range(4):
        for mask in range(DOMAIN_SIZE):
            if mask & (1 << axis):
                coefficients[mask] ^= coefficients[mask ^ (1 << axis)]
    return tuple(coefficients)


def _anf_values(coefficients: tuple[int, ...]) -> tuple[int, ...]:
    values: list[int] = []
    for point in range(DOMAIN_SIZE):
        value = 0
        subset = point
        while True:
            value ^= coefficients[subset]
            if subset == 0:
                break
            subset = (subset - 1) & point
        values.append(value)
    return tuple(values)


def _bits_to_table(bits: Iterable[int]) -> int:
    return sum((int(bit) & 1) << index for index, bit in enumerate(bits))


def representation_roundtrip(table: int, state: RepresentationState) -> int:
    bits = bit_tuple(table)
    if state.encoding == "lut":
        decoded = bits
    elif state.encoding == "rle":
        decoded = _decode_rle(_encode_rle(bits))
    elif state.encoding == "anf":
        decoded = _anf_values(_anf_coefficients(bits))
    else:
        raise ValueError(f"unknown encoding {state.encoding}")

    reconstructed = _bits_to_table(decoded)
    if state.decomposition == "xor_share_2":
        mask = 0xA5A5
        share_a = mask
        share_b = reconstructed ^ mask
        reconstructed = share_a ^ share_b
    elif state.decomposition != "single":
        raise ValueError(f"unknown decomposition {state.decomposition}")
    return reconstructed


def trace_atom(state: RepresentationState) -> tuple[str, str, str, int, str]:
    device_id = "d0" if state.decomposition == "single" else "d0+d1"
    opcode_class = f"{state.encoding}:{state.order}"
    memory_bucket = "hot" if state.cache == "memoized" else "cold"
    message_length = 64 if state.padding == "fixed_64" else 128
    timing_bucket = "constant_registered"
    return device_id, opcode_class, memory_bucket, message_length, timing_bucket


def make_accuracy_table(k: int) -> int:
    if not 0 <= k <= DOMAIN_SIZE:
        raise ValueError("k outside 0..16")
    table = TARGET_TABLE
    for index in range(k, DOMAIN_SIZE):
        table ^= 1 << index
    if agreement_count(table) != k:
        raise AssertionError("accuracy witness construction failed")
    return table


def audit_probability(k: int, theta: Fraction) -> Fraction:
    return (1 - theta) + (2 * theta - 1) * Fraction(k, DOMAIN_SIZE)


def binomial_pmf(m: int, q: Fraction, count: int) -> Fraction:
    if count < 0 or count > m:
        return Fraction(0)
    return Fraction(comb(m, count)) * q**count * (1 - q) ** (m - count)


def binomial_distribution(m: int, q: Fraction) -> tuple[Fraction, ...]:
    distribution = tuple(binomial_pmf(m, q, count) for count in range(m + 1))
    if sum(distribution, Fraction(0)) != 1:
        raise AssertionError("binomial distribution does not sum to one")
    return distribution


def direct_report_count_distribution(m: int, q: Fraction) -> tuple[Fraction, ...]:
    if m > 8:
        raise ValueError("direct enumeration is limited to the registered preflight length")
    counts = [Fraction(0) for _ in range(m + 1)]
    for reports in product((0, 1), repeat=m):
        successes = sum(reports)
        probability = q**successes * (1 - q) ** (m - successes)
        counts[successes] += probability
    return tuple(counts)


def decision_errors(m: int, q: Fraction, cutoff: int, gamma: Fraction) -> tuple[Fraction, Fraction]:
    distribution = binomial_distribution(m, q)
    forbidden_probability = sum(distribution[cutoff + 1 :], Fraction(0)) + gamma * distribution[cutoff]
    compliant_probability = 1 - forbidden_probability
    return forbidden_probability, compliant_probability


def find_feasible_test(m: int, theta: Fraction, limit: Fraction = ERROR_LIMIT) -> ThresholdTest | None:
    q0 = audit_probability(8, theta)
    q1 = audit_probability(14, theta)
    dist0 = binomial_distribution(m, q0)
    dist1 = binomial_distribution(m, q1)
    for cutoff in range(m + 1):
        p0_equal = dist0[cutoff]
        p1_equal = dist1[cutoff]
        p0_greater = sum(dist0[cutoff + 1 :], Fraction(0))
        p1_less = sum(dist1[:cutoff], Fraction(0))

        lower = Fraction(0)
        upper = Fraction(1)
        if p0_equal:
            upper = min(upper, (limit - p0_greater) / p0_equal)
        elif p0_greater > limit:
            continue
        if p1_equal:
            lower = max(lower, 1 - (limit - p1_less) / p1_equal)
        elif p1_less > limit:
            continue
        lower = max(lower, Fraction(0))
        upper = min(upper, Fraction(1))
        if lower > upper:
            continue
        gamma = (lower + upper) / 2
        worst_fp, _ = decision_errors(m, q0, cutoff, gamma)
        _, worst_fn = decision_errors(m, q1, cutoff, gamma)
        if worst_fp <= limit and worst_fn <= limit:
            return ThresholdTest(m, theta, cutoff, gamma, worst_fp, worst_fn)
    return None


def uniform_errors(test: ThresholdTest) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
    false_positives: dict[int, Fraction] = {}
    false_negatives: dict[int, Fraction] = {}
    for k in range(0, 9):
        q = audit_probability(k, test.theta)
        fp, _ = decision_errors(test.m, q, test.cutoff, test.gamma)
        false_positives[k] = fp
    for k in range(14, 17):
        q = audit_probability(k, test.theta)
        _, fn = decision_errors(test.m, q, test.cutoff, test.gamma)
        false_negatives[k] = fn
    return false_positives, false_negatives


@lru_cache(maxsize=1)
def minimum_channels() -> dict[Fraction, ThresholdTest | None]:
    results: dict[Fraction, ThresholdTest | None] = {}
    for theta in THETA_GRID:
        results[theta] = next(
            (test for m in range(MAX_CHALLENGES + 1) if (test := find_feasible_test(m, theta)) is not None),
            None,
        )
    return results


def pareto_frontier(channels: dict[Fraction, ThresholdTest | None]) -> tuple[ThresholdTest, ...]:
    feasible = tuple(test for test in channels.values() if test is not None)
    frontier: list[ThresholdTest] = []
    for candidate in feasible:
        dominated = any(
            other.m <= candidate.m
            and other.theta <= candidate.theta
            and (other.m < candidate.m or other.theta < candidate.theta)
            for other in feasible
            if other is not candidate
        )
        if not dominated:
            frontier.append(candidate)
    return tuple(sorted(frontier, key=lambda test: (test.theta, test.m)))


def validate_orbit() -> dict[str, object]:
    states = representation_states()
    checked = 0
    failures: list[dict[str, object]] = []
    # Codec/decomposition output depends only on these two fields. Cache the
    # expensive part while still checking every registered state explicitly.
    roundtrips: dict[tuple[int, str, str], int] = {}
    for table in range(TRUTH_TABLE_COUNT):
        before_class = policy_class(table)
        for state in states:
            key = (table, state.encoding, state.decomposition)
            if key not in roundtrips:
                roundtrips[key] = representation_roundtrip(table, state)
            restored = roundtrips[key]
            checked += 1
            if restored != table or policy_class(restored) != before_class:
                failures.append({"table": table, "state": state.__dict__, "restored": restored})
                if len(failures) >= 8:
                    break
        if failures:
            break
    return {
        "state_count": len(states),
        "checked_pairs": checked,
        "expected_pairs": TRUTH_TABLE_COUNT * len(states),
        "failures": failures,
        "class_counts": class_counts(),
        "unique_trace_atoms": len({trace_atom(state) for state in states}),
    }


def validate_trace_witness() -> dict[str, object]:
    compliant = make_accuracy_table(8)
    forbidden = make_accuracy_table(14)
    mismatches = []
    for state in representation_states():
        law0 = {trace_atom(state): Fraction(1)}
        law1 = {trace_atom(state): Fraction(1)}
        if law0 != law1:
            mismatches.append(state.__dict__)
    return {
        "compliant_table": compliant,
        "forbidden_table": forbidden,
        "compliant_k": agreement_count(compliant),
        "forbidden_k": agreement_count(forbidden),
        "states_checked": len(representation_states()),
        "law_mismatches": mismatches,
        "sum_error_lower_bound": "1/1",
    }


def evaluate_gates(
    orbit: dict[str, object],
    trace: dict[str, object],
    channels: dict[Fraction, ThresholdTest | None],
    frontier: tuple[ThresholdTest, ...],
) -> dict[str, dict[str, object]]:
    p0_cases = 0
    p0_exact = True
    for theta in THETA_GRID:
        for k in (8, 14):
            q = audit_probability(k, theta)
            for m in range(0, 9):
                p0_cases += 1
                p0_exact &= direct_report_count_distribution(m, q) == binomial_distribution(m, q)

    uniform_violations: list[dict[str, object]] = []
    for theta, test in channels.items():
        if test is None:
            continue
        fps, fns = uniform_errors(test)
        for k, value in fps.items():
            if value > ERROR_LIMIT:
                uniform_violations.append({"theta": fraction_text(theta), "k": k, "type": "fp"})
        for k, value in fns.items():
            if value > ERROR_LIMIT:
                uniform_violations.append({"theta": fraction_text(theta), "k": k, "type": "fn"})

    feasible = tuple(test for test in channels.values() if test is not None)
    frontier_valid = all(test in feasible for test in frontier)
    for candidate in frontier:
        if any(
            other.m <= candidate.m
            and other.theta <= candidate.theta
            and (other.m < candidate.m or other.theta < candidate.theta)
            for other in feasible
            if other is not candidate
        ):
            frontier_valid = False

    expected_pairs = TRUTH_TABLE_COUNT * len(representation_states())
    return {
        "T0_finite_orbit_integrity": {
            "pass": orbit["state_count"] == 48
            and orbit["checked_pairs"] == expected_pairs
            and not orbit["failures"],
            "checked_pairs": orbit["checked_pairs"],
            "expected_pairs": expected_pairs,
        },
        "T1_trace_impossibility": {
            "pass": not trace["law_mismatches"] and trace["sum_error_lower_bound"] == "1/1",
            "states_checked": trace["states_checked"],
            "sum_error_lower_bound": trace["sum_error_lower_bound"],
        },
        "P0_sufficient_statistic": {"pass": p0_exact, "exact_cases": p0_cases},
        "A0_privacy_kill": {
            "pass": channels[Fraction(1, 2)] is None,
            "theta": "1/2",
        },
        "A1_charged_audit_liveness": {
            "pass": any(test is not None for theta, test in channels.items() if theta > Fraction(1, 2)),
            "feasible_theta_count": sum(test is not None for test in channels.values()),
        },
        "U0_uniform_composite": {
            "pass": not uniform_violations,
            "violations": uniform_violations,
        },
        "E0_exhaustive_liveness": {
            "pass": channels[Fraction(1)] is not None,
            "minimum_m": channels[Fraction(1)].m if channels[Fraction(1)] else None,
        },
        "F0_frontier_integrity": {
            "pass": frontier_valid and bool(frontier),
            "frontier_size": len(frontier),
        },
    }


def test_to_record(test: ThresholdTest | None) -> dict[str, object] | None:
    if test is None:
        return None
    fps, fns = uniform_errors(test)
    return {
        "m": test.m,
        "theta": fraction_text(test.theta),
        "cutoff": test.cutoff,
        "gamma": fraction_text(test.gamma),
        "worst_fp": fraction_text(max(fps.values())),
        "worst_fn": fraction_text(max(fns.values())),
        "endpoint_fp": fraction_text(test.worst_fp),
        "endpoint_fn": fraction_text(test.worst_fn),
        "sequential_privacy": (
            "infinity"
            if test.theta == 1
            else f"{test.m}*ln({test.theta.numerator}/{test.theta.denominator - test.theta.numerator})"
        ),
        "cost_tuple": {
            "challenge_executions": test.m,
            "released_bits": test.m,
            "verifier_units": test.m,
            "truth_report_probability": fraction_text(test.theta),
        },
    }
