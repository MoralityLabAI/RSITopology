from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import comb


DOMAIN_SIZE = 16
COMPLIANT_BOUNDARY = 8
FORBIDDEN_BOUNDARIES = (14, 16)
ERROR_LIMIT = Fraction(1, 20)
THETA_GRID = (Fraction(1, 2), Fraction(3, 4), Fraction(4, 5), Fraction(1))
COVERAGE_COUNTS = (0, 8, 10, 12, 14, 16)
MODELS = ("policy_independent", "adversarial_selective")
M_CAP = 8192


@dataclass(frozen=True)
class ObservationPair:
    model: str
    k1: int
    theta: Fraction
    coverage_count: int
    q0: Fraction
    q1: Fraction
    common_law: bool
    common_witness: dict[str, object] | None

    @property
    def effective_delta(self) -> Fraction:
        if self.common_law:
            return Fraction(0)
        return self.q1 - self.q0


@dataclass(frozen=True)
class ExactThresholdTest:
    m: int
    q0: Fraction
    q1: Fraction
    cutoff: int
    gamma: Fraction
    fp: Fraction
    fn: Fraction

    @property
    def feasible(self) -> bool:
        return self.fp <= ERROR_LIMIT and self.fn <= ERROR_LIMIT


@dataclass(frozen=True)
class MinimumCertificate:
    test: ExactThresholdTest | None
    predecessor: ExactThresholdTest | None
    cap_test: ExactThresholdTest | None
    exact_evaluations: int


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def full_report_probability(k: int, theta: Fraction, domain_size: int = DOMAIN_SIZE) -> Fraction:
    if not 0 <= k <= domain_size:
        raise ValueError("agreement count outside domain")
    if not Fraction(1, 2) <= theta <= 1:
        raise ValueError("theta outside randomized-response range")
    return (1 - theta) + (2 * theta - 1) * Fraction(k, domain_size)


def policy_independent_probability(k: int, theta: Fraction, coverage_count: int) -> Fraction:
    """Event-level coverage is independent of the execution and policy class.

    A covered event releases the full-meter randomized-response bit. An
    uncovered event releases a fresh fair bit. Coverage is therefore a signal
    attenuation, not a hidden execution-dependent subset.
    """
    if coverage_count not in range(DOMAIN_SIZE + 1):
        raise ValueError("coverage count outside domain")
    full_q = full_report_probability(k, theta)
    rho = Fraction(coverage_count, DOMAIN_SIZE)
    return Fraction(1, 2) + rho * (full_q - Fraction(1, 2))


def covered_agreement_range(
    k: int, coverage_count: int, domain_size: int = DOMAIN_SIZE
) -> tuple[int, int]:
    if not 0 <= k <= domain_size or not 0 <= coverage_count <= domain_size:
        raise ValueError("invalid agreement or coverage count")
    return max(0, k + coverage_count - domain_size), min(k, coverage_count)


def selective_probability(
    covered_agreements: int,
    theta: Fraction,
    coverage_count: int,
    domain_size: int = DOMAIN_SIZE,
) -> Fraction:
    if not 0 <= covered_agreements <= coverage_count <= domain_size:
        raise ValueError("invalid selective-coverage counts")
    # Covered events expose randomized-response correctness; uncovered events
    # emit a fresh fair bit. Sampling remains uniform over the full domain.
    return Fraction(1, 2) + (2 * theta - 1) * Fraction(
        2 * covered_agreements - coverage_count, 2 * domain_size
    )


def observation_pair(
    model: str, k1: int, theta: Fraction, coverage_count: int
) -> ObservationPair:
    if model not in MODELS:
        raise ValueError("unknown coverage model")
    if k1 not in FORBIDDEN_BOUNDARIES:
        raise ValueError("unregistered forbidden boundary")
    if theta not in THETA_GRID or coverage_count not in COVERAGE_COUNTS:
        raise ValueError("cell outside frozen grid")

    if model == "policy_independent":
        q0 = policy_independent_probability(COMPLIANT_BOUNDARY, theta, coverage_count)
        q1 = policy_independent_probability(k1, theta, coverage_count)
        common = q0 == q1
        witness = None
        if common:
            witness = {
                "kind": "identical_bernoulli_law",
                "q": fraction_text(q0),
                "reason": "zero_coverage" if coverage_count == 0 else "privacy_channel_kill",
            }
        return ObservationPair(model, k1, theta, coverage_count, q0, q1, common, witness)

    compliant_range = covered_agreement_range(COMPLIANT_BOUNDARY, coverage_count)
    forbidden_range = covered_agreement_range(k1, coverage_count)
    q0 = selective_probability(compliant_range[1], theta, coverage_count)
    q1 = selective_probability(forbidden_range[0], theta, coverage_count)

    if theta == Fraction(1, 2):
        common = True
        witness = {
            "kind": "identical_bernoulli_law",
            "q": "1/2",
            "compliant_covered_agreements": compliant_range[0],
            "forbidden_covered_agreements": forbidden_range[0],
            "reason": "privacy_channel_kill",
        }
    else:
        overlap_low = max(compliant_range[0], forbidden_range[0])
        overlap_high = min(compliant_range[1], forbidden_range[1])
        common = overlap_low <= overlap_high
        witness = None
        if common:
            common_a = overlap_low
            common_q = selective_probability(common_a, theta, coverage_count)
            witness = {
                "kind": "selective_mask_common_law",
                "q": fraction_text(common_q),
                "covered_agreements": common_a,
                "compliant_range": list(compliant_range),
                "forbidden_range": list(forbidden_range),
                "reason": "coverage_alignment_overlap",
            }
    return ObservationPair(model, k1, theta, coverage_count, q0, q1, common, witness)


def _integer_binomial_masses(m: int, q: Fraction) -> tuple[list[int], int]:
    if m < 0 or not 0 <= q <= 1:
        raise ValueError("invalid binomial parameters")
    a, b = q.numerator, q.denominator
    denominator = b**m
    if a == 0:
        return [denominator] + [0] * m, denominator
    if a == b:
        return [0] * m + [denominator], denominator

    complement = b - a
    masses = [complement**m]
    for count in range(m):
        next_mass = masses[-1] * (m - count) * a // ((count + 1) * complement)
        masses.append(next_mass)
    if sum(masses) != denominator:
        raise ArithmeticError("integer binomial masses do not sum to denominator")
    return masses, denominator


@lru_cache(maxsize=None)
def exact_size_test(m: int, q0: Fraction, q1: Fraction) -> ExactThresholdTest:
    if not 0 <= m <= M_CAP:
        raise ValueError("m outside registered cap")
    if not Fraction(0) <= q0 < q1 <= 1:
        raise ValueError("exact upper-tail test requires q0 < q1")

    masses0, denominator0 = _integer_binomial_masses(m, q0)
    cutoff = m
    tail = 0
    while cutoff >= 0 and Fraction(tail + masses0[cutoff], denominator0) < ERROR_LIMIT:
        tail += masses0[cutoff]
        cutoff -= 1
    if cutoff < 0:
        raise ArithmeticError("failed to locate exact size cutoff")
    equal0 = masses0[cutoff]
    gamma = (ERROR_LIMIT - Fraction(tail, denominator0)) / Fraction(equal0, denominator0)
    if not 0 <= gamma <= 1:
        raise ArithmeticError("cutoff randomization outside [0,1]")
    fp = Fraction(tail, denominator0) + gamma * Fraction(equal0, denominator0)

    masses1, denominator1 = _integer_binomial_masses(m, q1)
    lower1 = sum(masses1[:cutoff])
    equal1 = masses1[cutoff]
    fn = Fraction(lower1, denominator1) + (1 - gamma) * Fraction(equal1, denominator1)
    return ExactThresholdTest(m, q0, q1, cutoff, gamma, fp, fn)


@lru_cache(maxsize=None)
def certify_minimum(q0: Fraction, q1: Fraction, cap: int = M_CAP) -> MinimumCertificate:
    if not q0 < q1:
        raise ValueError("a common or reversed law has no minimum certificate")
    evaluations = 0
    high = 1
    high_test = exact_size_test(high, q0, q1)
    evaluations += 1
    while high < cap and not high_test.feasible:
        high = min(cap, high * 2)
        high_test = exact_size_test(high, q0, q1)
        evaluations += 1
    if not high_test.feasible:
        return MinimumCertificate(None, None, high_test, evaluations)

    low = 0
    while low < high:
        middle = (low + high) // 2
        middle_test = exact_size_test(middle, q0, q1)
        evaluations += 1
        if middle_test.feasible:
            high = middle
        else:
            low = middle + 1
    test = exact_size_test(low, q0, q1)
    evaluations += 1
    predecessor = exact_size_test(low - 1, q0, q1) if low else None
    if predecessor is not None:
        evaluations += 1
    return MinimumCertificate(test, predecessor, None, evaluations)


def test_record(test: ExactThresholdTest) -> dict[str, object]:
    return {
        "m": test.m,
        "cutoff": test.cutoff,
        "gamma": fraction_text(test.gamma),
        "fp": fraction_text(test.fp),
        "fn": fraction_text(test.fn),
    }


def cell_record(model: str, k1: int, theta: Fraction, coverage_count: int) -> dict[str, object]:
    pair = observation_pair(model, k1, theta, coverage_count)
    record: dict[str, object] = {
        "model": model,
        "k1": k1,
        "theta": fraction_text(theta),
        "coverage_count": coverage_count,
        "coverage": fraction_text(Fraction(coverage_count, DOMAIN_SIZE)),
        "q0_worst": fraction_text(pair.q0),
        "q1_worst": fraction_text(pair.q1),
        "effective_delta": fraction_text(pair.effective_delta),
        "common_law_witness": pair.common_witness,
    }
    if pair.common_law:
        record.update(
            {
                "status": "common_law_impossible",
                "m_star": None,
                "sum_error_lower_bound": "1/1",
                "exact_evaluations": 0,
            }
        )
        return record

    certificate = certify_minimum(pair.q0, pair.q1)
    if certificate.test is None:
        assert certificate.cap_test is not None
        record.update(
            {
                "status": "infeasible_within_cap",
                "m_star": None,
                "cap": certificate.cap_test.m,
                "cap_test": test_record(certificate.cap_test),
                "exact_evaluations": certificate.exact_evaluations,
            }
        )
        return record
    record.update(
        {
            "status": "feasible_exact",
            "m_star": certificate.test.m,
            "test": test_record(certificate.test),
            "predecessor": test_record(certificate.predecessor)
            if certificate.predecessor is not None
            else None,
            "exact_evaluations": certificate.exact_evaluations,
        }
    )
    return record


def compute_records() -> list[dict[str, object]]:
    return [
        cell_record(model, k1, theta, coverage_count)
        for model in MODELS
        for k1 in FORBIDDEN_BOUNDARIES
        for theta in THETA_GRID
        for coverage_count in COVERAGE_COUNTS
    ]


def _fraction(value: object) -> Fraction:
    numerator, denominator = str(value).split("/", 1)
    return Fraction(int(numerator), int(denominator))


def _record_index(records: list[dict[str, object]]) -> dict[tuple[str, int, Fraction, int], dict[str, object]]:
    return {
        (str(row["model"]), int(row["k1"]), _fraction(row["theta"]), int(row["coverage_count"])): row
        for row in records
    }


def binomial_distribution(m: int, q: Fraction) -> tuple[Fraction, ...]:
    return tuple(Fraction(comb(m, k)) * q**k * (1 - q) ** (m - k) for k in range(m + 1))


def direct_report_distribution(m: int, q: Fraction) -> tuple[Fraction, ...]:
    counts = [Fraction(0) for _ in range(m + 1)]
    for reports in product((0, 1), repeat=m):
        ones = sum(reports)
        counts[ones] += q**ones * (1 - q) ** (m - ones)
    return tuple(counts)


def brute_force_small_cases() -> dict[str, object]:
    range_failures: list[str] = []
    invariance_failures: list[str] = []
    domain_size = 4
    universe = tuple(range(domain_size))
    for k in range(domain_size + 1):
        expected_by_c = {
            c: set(range(*(
                lambda bounds: (bounds[0], bounds[1] + 1)
            )(covered_agreement_range(k, c, domain_size))))
            for c in range(domain_size + 1)
        }
        observed_by_mask: dict[int, set[frozenset[int]]] = {c: set() for c in range(domain_size + 1)}
        for agreements_tuple in combinations(universe, k):
            agreements = set(agreements_tuple)
            for c in range(domain_size + 1):
                attained: set[int] = set()
                for coverage_tuple in combinations(universe, c):
                    attained.add(len(agreements.intersection(coverage_tuple)))
                if attained != expected_by_c[c]:
                    range_failures.append(f"n=4,k={k},c={c},agreements={agreements_tuple}")
                observed_by_mask[c].add(frozenset(attained))
        for c, observed in observed_by_mask.items():
            if len(observed) != 1:
                invariance_failures.append(f"n=4,k={k},c={c}")

    distribution_failures: list[str] = []
    for q in (Fraction(1, 2), Fraction(9, 16), Fraction(3, 4)):
        for m in range(6):
            if direct_report_distribution(m, q) != binomial_distribution(m, q):
                distribution_failures.append(f"q={fraction_text(q)},m={m}")
    return {
        "pass": not range_failures and not invariance_failures and not distribution_failures,
        "range_failures": range_failures,
        "invariance_failures": invariance_failures,
        "distribution_failures": distribution_failures,
        "domain_size": domain_size,
        "report_lengths": list(range(6)),
    }


def evaluate_gates(records: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    index = _record_index(records)
    adjacency_failures: list[str] = []
    for row in records:
        if row["status"] != "feasible_exact":
            continue
        label = (
            f"{row['model']},k1={row['k1']},theta={row['theta']},"
            f"c={row['coverage_count']}"
        )
        test = row["test"]
        predecessor = row["predecessor"]
        if _fraction(test["fp"]) != ERROR_LIMIT or _fraction(test["fn"]) > ERROR_LIMIT:
            adjacency_failures.append(f"{label}:test")
        if predecessor is not None and _fraction(predecessor["fn"]) <= ERROR_LIMIT:
            adjacency_failures.append(f"{label}:predecessor")

    expected = {
        (14, Fraction(3, 4)): 73,
        (14, Fraction(4, 5)): 50,
        (14, Fraction(1)): 15,
        (16, Fraction(3, 4)): 40,
        (16, Fraction(4, 5)): 26,
        (16, Fraction(1)): 5,
    }
    reproduction_failures: list[str] = []
    for model in MODELS:
        for (k1, theta), m_star in expected.items():
            row = index[(model, k1, theta, 16)]
            if row["status"] != "feasible_exact" or row["m_star"] != m_star:
                reproduction_failures.append(f"{model},k1={k1},theta={fraction_text(theta)}")

    monotonicity_failures: list[str] = []
    for model in MODELS:
        for k1 in FORBIDDEN_BOUNDARIES:
            for theta in THETA_GRID:
                ordered = [index[(model, k1, theta, c)] for c in COVERAGE_COUNTS]
                previous_m: int | None = None
                previous_live = False
                previous_delta = Fraction(-1)
                for row in ordered:
                    delta = _fraction(row["effective_delta"])
                    if delta < previous_delta:
                        monotonicity_failures.append(
                            f"delta:{model},k1={k1},theta={fraction_text(theta)},c={row['coverage_count']}"
                        )
                    previous_delta = delta
                    live = row["status"] == "feasible_exact"
                    if previous_live and not live:
                        monotonicity_failures.append(
                            f"status:{model},k1={k1},theta={fraction_text(theta)},c={row['coverage_count']}"
                        )
                    if live and previous_m is not None and int(row["m_star"]) > previous_m:
                        monotonicity_failures.append(
                            f"m:{model},k1={k1},theta={fraction_text(theta)},c={row['coverage_count']}"
                        )
                    if live:
                        previous_m = int(row["m_star"])
                        previous_live = True

    common_failures: list[str] = []
    for row in records:
        should_be_zero_information = row["theta"] == "1/2" or row["coverage_count"] == 0
        if should_be_zero_information and row["status"] != "common_law_impossible":
            common_failures.append(
                f"zero:{row['model']},k1={row['k1']},theta={row['theta']},c={row['coverage_count']}"
            )
        if row["status"] == "common_law_impossible":
            if row["common_law_witness"] is None or row["sum_error_lower_bound"] != "1/1":
                common_failures.append(
                    f"witness:{row['model']},k1={row['k1']},theta={row['theta']},c={row['coverage_count']}"
                )
    for theta in THETA_GRID[1:]:
        row = index[("adversarial_selective", 14, theta, 10)]
        if row["status"] != "common_law_impossible":
            common_failures.append(f"selective_overlap:k1=14,theta={fraction_text(theta)},c=10")

    brute_force = brute_force_small_cases()
    return {
        "E0_exact_adjacency": {"pass": not adjacency_failures, "failures": adjacency_failures},
        "R0_full_coverage_reproduction": {
            "pass": not reproduction_failures,
            "failures": reproduction_failures,
            "expected_cells": len(expected) * len(MODELS),
        },
        "M0_coverage_monotonicity": {
            "pass": not monotonicity_failures,
            "failures": monotonicity_failures,
        },
        "Z0_common_law_zero_information": {
            "pass": not common_failures,
            "failures": common_failures,
        },
        "B0_bruteforce_small_cases": brute_force,
    }


def evaluate_metric_robustness(
    records: list[dict[str, object]], gates: dict[str, dict[str, object]]
) -> dict[str, dict[str, object]]:
    index = _record_index(records)
    invariant = gates["B0_bruteforce_small_cases"]["pass"] and not gates[
        "B0_bruteforce_small_cases"
    ]["invariance_failures"]

    ind_half = index[("policy_independent", 14, Fraction(3, 4), 8)]
    ind_full = index[("policy_independent", 14, Fraction(3, 4), 16)]
    ind_three_quarters = index[("policy_independent", 14, Fraction(3, 4), 12)]
    adv_three_quarters = index[("adversarial_selective", 14, Fraction(3, 4), 12)]
    sensitivity = (
        ind_half["status"] == "feasible_exact"
        and ind_full["status"] == "feasible_exact"
        and int(ind_half["m_star"]) > int(ind_full["m_star"])
        and adv_three_quarters["status"] == "feasible_exact"
        and ind_three_quarters["status"] == "feasible_exact"
        and int(adv_three_quarters["m_star"]) > int(ind_three_quarters["m_star"])
    )

    anti_gaming_failures: list[str] = []
    for theta in THETA_GRID[1:]:
        independent = index[("policy_independent", 14, theta, 10)]
        adversarial = index[("adversarial_selective", 14, theta, 10)]
        if independent["status"] != "feasible_exact" or adversarial["status"] != "common_law_impossible":
            anti_gaming_failures.append(f"theta={fraction_text(theta)}")

    clean_failures: list[str] = []
    for k1 in FORBIDDEN_BOUNDARIES:
        for theta in THETA_GRID[1:]:
            left = index[("policy_independent", k1, theta, 16)]
            right = index[("adversarial_selective", k1, theta, 16)]
            if (
                left["status"] != "feasible_exact"
                or right["status"] != "feasible_exact"
                or left["m_star"] != right["m_star"]
                or left["q0_worst"] != right["q0_worst"]
                or left["q1_worst"] != right["q1_worst"]
            ):
                clean_failures.append(f"k1={k1},theta={fraction_text(theta)}")

    return {
        "invariance": {
            "pass": bool(invariant),
            "probe": "all n=4 input relabelings preserve attainable covered-agreement sets",
        },
        "sensitivity": {
            "pass": sensitivity,
            "probe": "sample burden responds to coverage loss and selective suppression",
            "independent_m_c8": ind_half["m_star"],
            "independent_m_c16": ind_full["m_star"],
            "independent_m_c12": ind_three_quarters["m_star"],
            "adversarial_m_c12": adv_three_quarters["m_star"],
        },
        "monotonicity": {
            "pass": gates["M0_coverage_monotonicity"]["pass"],
            "probe": "more exact coverage never increases certified burden on the frozen grid",
        },
        "anti_gaming": {
            "pass": not anti_gaming_failures,
            "probe": "nominal independent coverage cannot substitute for selective worst-case coverage",
            "failures": anti_gaming_failures,
        },
        "clean_control": {
            "pass": not clean_failures and gates["R0_full_coverage_reproduction"]["pass"],
            "probe": "both models collapse to the v0.2.1 full-coverage experiment",
            "failures": clean_failures,
        },
    }


def build_result() -> dict[str, object]:
    records = compute_records()
    gates = evaluate_gates(records)
    probes = evaluate_metric_robustness(records, gates)
    reliability_gate_names = (
        "E0_exact_adjacency",
        "R0_full_coverage_reproduction",
        "B0_bruteforce_small_cases",
    )
    measurement_reliable = all(gates[name]["pass"] for name in reliability_gate_names)
    claim_gate_names = ("M0_coverage_monotonicity", "Z0_common_law_zero_information")
    claim_supported = measurement_reliable and all(gates[name]["pass"] for name in claim_gate_names) and all(
        probe["pass"] for probe in probes.values()
    )

    task_status = (
        "not_evaluated_invalid_measurement"
        if not measurement_reliable
        else "selective_suppression_weakens_registered_attestability"
        if probes["sensitivity"]["pass"] and probes["anti_gaming"]["pass"]
        else "registered_coverage_contrast_not_established"
    )
    return {
        "experiment_id": "ASMP-7-METER-COVERAGE-ROBUSTNESS-v0.3",
        "evidence_class": "exact_finite_rational_composite_testing",
        "protocol_constants": {
            "domain_size": DOMAIN_SIZE,
            "compliant_boundary": COMPLIANT_BOUNDARY,
            "forbidden_boundaries": list(FORBIDDEN_BOUNDARIES),
            "theta_grid": [fraction_text(value) for value in THETA_GRID],
            "coverage_counts": list(COVERAGE_COUNTS),
            "models": list(MODELS),
            "error_limit": fraction_text(ERROR_LIMIT),
            "m_cap": M_CAP,
        },
        "task_result": {
            "status": task_status,
            "basis": "exact comparison of policy-independent coverage and adversarial selective suppression",
        },
        "measurement_reliability": {
            "status": "reliable_exact_finite_measurement"
            if measurement_reliable
            else "unreliable_measurement",
            "gate_names": list(reliability_gate_names),
            "all_pass": measurement_reliable,
        },
        "claim_support": {
            "status": "registered_finite_claim_supported"
            if claim_supported
            else "claim_not_supported",
            "claim": (
                "On the frozen Boolean grid, selective suppression can create an exact common-law "
                "region and otherwise weakly increases audit burden relative to policy-independent coverage."
            ),
            "all_pass": claim_supported,
        },
        "operational_decision": {
            "status": "no_deployment_decision_authorized",
            "reason": "synthetic finite registry with no validated real-meter or deployment bridge",
        },
        "gates": gates,
        "metric_robustness_probes": probes,
        "records": records,
        "claim_boundary": (
            "This result concerns a 16-point Boolean registry, exact-size event coverage, fresh fair "
            "fallback bits, independent challenges, and two declared suppression models. It does not "
            "establish real meter coverage, identify a deployment threshold, characterize adaptive "
            "history-dependent suppression, prove transformation-universal attestability, or resolve ASMP-7."
        ),
    }
