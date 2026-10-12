"""Deterministic bounds and exact sample costs for ASMP-11 v0.2.1.

The covering construction is deliberately conservative.  A deterministic
greedy pass supplies a replayable incumbent, while counting and Schoenheim
bounds supply an exact, independently replayable lower bound.  Equality of the
bounds certifies an optimum.  A resource stop keeps a valid all-block
incumbent; it never rounds a partial search into an optimum.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb
from time import monotonic
from typing import Iterable, Sequence


STATUS_CERTIFIED = "crossover_certified"
STATUS_IMPOSSIBLE = "crossover_impossible_under_bounds"
STATUS_UNRESOLVED = "unresolved_covering_gap"
CLASSIFICATION_STATUSES = (
    STATUS_CERTIFIED,
    STATUS_IMPOSSIBLE,
    STATUS_UNRESOLVED,
)


@dataclass(frozen=True)
class CoverCertificate:
    n: int
    block_size: int
    support_size: int
    lower_bound: int
    counting_lower_bound: int
    schoenheim_lower_bound: int
    upper_bound: int
    selected_blocks: tuple[tuple[int, ...], ...]
    optimum_certified: bool
    construction_status: str
    greedy_rounds: int
    gain_evaluations: int
    universe_size: int
    candidate_block_count: int
    stop_reason: str


@dataclass(frozen=True)
class ExactTestDesign:
    query_count: int
    samples_per_query: int
    cutoff: int
    null_tail: Fraction
    familywise_error_upper: Fraction
    signal_power_lower: Fraction
    fwer_mode: str

    @property
    def total_samples(self) -> int:
        return self.query_count * self.samples_per_query


@dataclass(frozen=True)
class CostClassification:
    status: str
    lower_query_bound: int
    upper_query_bound: int
    baseline: ExactTestDesign
    certified_design: ExactTestDesign | None
    optimistic_design: ExactTestDesign | None
    evaluated_query_counts: int


def ceil_div(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    return -(-numerator // denominator)


def subsets(n: int, size: int) -> tuple[tuple[int, ...], ...]:
    if not 0 <= size <= n:
        raise ValueError("subset size must lie in [0,n]")
    return tuple(combinations(range(n), size))


def counting_lower_bound(n: int, block_size: int, support_size: int) -> int:
    if not 0 < support_size <= block_size <= n:
        raise ValueError("require 0 < support_size <= block_size <= n")
    return ceil_div(comb(n, support_size), comb(block_size, support_size))


def schoenheim_lower_bound(n: int, block_size: int, support_size: int) -> int:
    """Return the exact recursive Schoenheim lower bound C(n,s,k)."""

    if not 0 <= support_size <= block_size <= n:
        raise ValueError("require 0 <= support_size <= block_size <= n")
    if support_size == 0:
        return 1
    return ceil_div(
        n * schoenheim_lower_bound(n - 1, block_size - 1, support_size - 1),
        block_size,
    )


def replayable_lower_bound(
    n: int, block_size: int, support_size: int
) -> dict[str, int]:
    counting = counting_lower_bound(n, block_size, support_size)
    schoenheim = schoenheim_lower_bound(n, block_size, support_size)
    return {
        "counting": counting,
        "schoenheim": schoenheim,
        "certified_lower_bound": max(counting, schoenheim),
    }


def verify_cover(
    n: int,
    block_size: int,
    support_size: int,
    selected_blocks: Sequence[Sequence[int]],
) -> bool:
    if not 0 < support_size <= block_size <= n:
        return False
    covered: set[tuple[int, ...]] = set()
    for raw_block in selected_blocks:
        block = tuple(raw_block)
        if len(block) != block_size or tuple(sorted(block)) != block:
            return False
        if len(set(block)) != block_size or any(
            point < 0 or point >= n for point in block
        ):
            return False
        covered.update(combinations(block, support_size))
    return len(covered) == comb(n, support_size)


def _incidence_masks(
    n: int,
    block_size: int,
    support_size: int,
    deadline: float | None = None,
) -> tuple[
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
    tuple[int, ...],
    bool,
]:
    supports = subsets(n, support_size)
    support_index = {support: index for index, support in enumerate(supports)}
    blocks = subsets(n, block_size)
    masks: list[int] = []
    for block in blocks:
        if deadline is not None and monotonic() >= deadline:
            return supports, blocks, tuple(masks), True
        mask = 0
        for support in combinations(block, support_size):
            mask |= 1 << support_index[support]
        masks.append(mask)
    return supports, blocks, tuple(masks), False


def _iter_set_bits(mask: int) -> Iterable[int]:
    while mask:
        least = mask & -mask
        yield least.bit_length() - 1
        mask ^= least


def _reverse_delete(
    selected: Sequence[int],
    masks: Sequence[int],
    universe_size: int,
    deadline: float | None = None,
) -> tuple[tuple[int, ...], bool]:
    counts = [0] * universe_size
    for index in selected:
        if deadline is not None and monotonic() >= deadline:
            return tuple(selected), True
        for support_index in _iter_set_bits(masks[index]):
            counts[support_index] += 1
    kept = list(selected)
    for index in reversed(tuple(selected)):
        if deadline is not None and monotonic() >= deadline:
            return tuple(kept), True
        if all(
            counts[support_index] >= 2 for support_index in _iter_set_bits(masks[index])
        ):
            kept.remove(index)
            for support_index in _iter_set_bits(masks[index]):
                counts[support_index] -= 1
    return tuple(kept), False


def deterministic_cover_bounds(
    n: int,
    block_size: int,
    support_size: int,
    *,
    max_greedy_rounds: int,
    max_candidate_blocks: int,
    hard_wall_seconds: float | None = None,
) -> CoverCertificate:
    """Construct a deterministic incumbent and exact combinatorial lower bound.

    The scientific stop is ``max_greedy_rounds``.  ``hard_wall_seconds`` is an
    operational fail-safe.  Either stop returns the complete family of blocks
    as a valid incumbent and retains the same replayable lower bound.
    """

    if max_greedy_rounds < 0:
        raise ValueError("max_greedy_rounds must be nonnegative")
    if hard_wall_seconds is not None and hard_wall_seconds < 0:
        raise ValueError("hard_wall_seconds must be nonnegative")
    deadline = (
        monotonic() + hard_wall_seconds if hard_wall_seconds is not None else None
    )
    candidate_count = comb(n, block_size)
    if candidate_count > max_candidate_blocks:
        raise ValueError(
            f"candidate block cap exceeded: {candidate_count}>{max_candidate_blocks}"
        )
    supports, blocks, masks, wall_hit = _incidence_masks(
        n, block_size, support_size, deadline
    )
    lower = replayable_lower_bound(n, block_size, support_size)
    universe_mask = (1 << len(supports)) - 1
    uncovered = universe_mask
    selected: list[int] = []
    selected_set: set[int] = set()
    rounds = 0
    evaluations = 0
    stop_reason = "operational_wall_stop" if wall_hit else "cover_complete"

    while uncovered and not wall_hit:
        if rounds >= max_greedy_rounds:
            stop_reason = "deterministic_round_cap"
            break
        if deadline is not None and monotonic() >= deadline:
            stop_reason = "operational_wall_stop"
            break
        best_index: int | None = None
        best_gain = 0
        for index, mask in enumerate(masks):
            if deadline is not None and monotonic() >= deadline:
                wall_hit = True
                stop_reason = "operational_wall_stop"
                break
            if index in selected_set:
                continue
            gain = (mask & uncovered).bit_count()
            evaluations += 1
            if gain > best_gain:
                best_gain = gain
                best_index = index
        if wall_hit:
            break
        if best_index is None or best_gain == 0:
            stop_reason = "construction_stalled"
            break
        selected.append(best_index)
        selected_set.add(best_index)
        uncovered &= ~masks[best_index]
        rounds += 1

    if uncovered:
        # Every k-support is contained in at least one s-block.  Keeping every
        # block is a deterministic, replayable incumbent even after a stop.
        chosen = tuple(range(len(blocks)))
        construction_status = "bounded_stop_with_trivial_incumbent"
    else:
        chosen, reverse_wall_hit = _reverse_delete(
            selected, masks, len(supports), deadline
        )
        if reverse_wall_hit:
            stop_reason = "operational_wall_stop"
        construction_status = "deterministic_greedy_incumbent"

    selected_blocks = tuple(blocks[index] for index in chosen)
    if not verify_cover(n, block_size, support_size, selected_blocks):
        raise AssertionError("constructed incumbent is not a valid cover")
    upper_bound = len(selected_blocks)
    exact = upper_bound == lower["certified_lower_bound"]
    if exact:
        construction_status = "exact_bounds_match"
    return CoverCertificate(
        n=n,
        block_size=block_size,
        support_size=support_size,
        lower_bound=lower["certified_lower_bound"],
        counting_lower_bound=lower["counting"],
        schoenheim_lower_bound=lower["schoenheim"],
        upper_bound=upper_bound,
        selected_blocks=selected_blocks,
        optimum_certified=exact,
        construction_status=construction_status,
        greedy_rounds=rounds,
        gain_evaluations=evaluations,
        universe_size=len(supports),
        candidate_block_count=len(blocks),
        stop_reason=stop_reason,
    )


@lru_cache(maxsize=None)
def two_sided_binomial_tail(
    samples: int, cutoff: int, plus_probability: Fraction
) -> Fraction:
    if samples < 1:
        raise ValueError("samples must be positive")
    if not 0 <= plus_probability <= 1:
        raise ValueError("probability must lie in [0,1]")
    if cutoff < 0:
        return Fraction(0)
    if 2 * cutoff >= samples:
        return Fraction(1)
    a = plus_probability.numerator
    b = plus_probability.denominator
    minus = b - a
    numerator = sum(
        comb(samples, count) * a**count * minus ** (samples - count)
        for count in range(cutoff + 1)
    )
    numerator += sum(
        comb(samples, count) * a**count * minus ** (samples - count)
        for count in range(samples - cutoff, samples + 1)
    )
    return Fraction(numerator, b**samples)


def familywise_error(null_tail: Fraction, query_count: int, mode: str) -> Fraction:
    if mode == "bonferroni":
        return min(Fraction(1), query_count * null_tail)
    if mode == "independent_exact":
        return Fraction(1) - (Fraction(1) - null_tail) ** query_count
    raise ValueError(f"unknown FWER mode: {mode}")


@lru_cache(maxsize=None)
def most_permissive_cutoff(
    samples: int,
    query_count: int,
    alpha: Fraction,
    fwer_mode: str,
) -> int | None:
    accepted: int | None = None
    for cutoff in range((samples - 1) // 2 + 1):
        tail = two_sided_binomial_tail(samples, cutoff, Fraction(1, 2))
        if familywise_error(tail, query_count, fwer_mode) <= alpha:
            accepted = cutoff
        else:
            break
    return accepted


@lru_cache(maxsize=None)
def find_exact_design(
    query_count: int,
    flip_rate: Fraction,
    alpha: Fraction,
    target_power: Fraction,
    sample_cap: int,
    fwer_mode: str = "bonferroni",
) -> ExactTestDesign | None:
    if query_count < 1:
        raise ValueError("query_count must be positive")
    if not 0 <= flip_rate < Fraction(1, 2):
        raise ValueError("flip_rate must lie in [0,1/2)")
    signal_probability = Fraction(1) - flip_rate
    for samples in range(1, sample_cap + 1):
        cutoff = most_permissive_cutoff(samples, query_count, alpha, fwer_mode)
        if cutoff is None:
            continue
        null_tail = two_sided_binomial_tail(samples, cutoff, Fraction(1, 2))
        power = two_sided_binomial_tail(samples, cutoff, signal_probability)
        if power >= target_power:
            return ExactTestDesign(
                query_count=query_count,
                samples_per_query=samples,
                cutoff=cutoff,
                null_tail=null_tail,
                familywise_error_upper=familywise_error(
                    null_tail, query_count, fwer_mode
                ),
                signal_power_lower=power,
                fwer_mode=fwer_mode,
            )
    return None


def classify_cost_interval(
    lower_query_bound: int,
    upper_query_bound: int,
    baseline_query_count: int,
    flip_rate: Fraction,
    alpha: Fraction,
    target_power: Fraction,
    sample_cap: int,
    *,
    fwer_mode: str = "bonferroni",
) -> CostClassification:
    if not 1 <= lower_query_bound <= upper_query_bound:
        raise ValueError("require 1 <= lower_query_bound <= upper_query_bound")
    baseline = find_exact_design(
        baseline_query_count,
        flip_rate,
        alpha,
        target_power,
        sample_cap,
        fwer_mode,
    )
    if baseline is None:
        raise RuntimeError("observational baseline exceeds the sample cap")
    certified = find_exact_design(
        upper_query_bound,
        flip_rate,
        alpha,
        target_power,
        sample_cap,
        fwer_mode,
    )
    feasible = [
        design
        for query_count in range(lower_query_bound, upper_query_bound + 1)
        if (
            design := find_exact_design(
                query_count,
                flip_rate,
                alpha,
                target_power,
                sample_cap,
                fwer_mode,
            )
        )
        is not None
    ]
    optimistic = min(
        feasible,
        key=lambda design: (design.total_samples, design.query_count),
        default=None,
    )
    if certified is not None and certified.total_samples < baseline.total_samples:
        status = STATUS_CERTIFIED
    elif optimistic is None or optimistic.total_samples >= baseline.total_samples:
        status = STATUS_IMPOSSIBLE
    else:
        status = STATUS_UNRESOLVED
    return CostClassification(
        status=status,
        lower_query_bound=lower_query_bound,
        upper_query_bound=upper_query_bound,
        baseline=baseline,
        certified_design=certified,
        optimistic_design=optimistic,
        evaluated_query_counts=upper_query_bound - lower_query_bound + 1,
    )


def classify_query_interval(
    lower_query_bound: int, upper_query_bound: int, baseline_query_count: int
) -> str:
    if upper_query_bound < baseline_query_count:
        return STATUS_CERTIFIED
    if lower_query_bound >= baseline_query_count:
        return STATUS_IMPOSSIBLE
    return STATUS_UNRESOLVED


def intermediate_widths(n: int, support_size: int) -> tuple[int, ...]:
    if support_size == 3:
        high = n - 3
    elif support_size == 4:
        high = n - 2
    else:
        raise ValueError("the v0.2.1 claim grid supports k in {3,4}")
    return tuple(range(support_size + 1, high))


def high_width_anchor(n: int, support_size: int) -> int:
    if support_size == 3:
        return n - 3
    if support_size == 4:
        return n - 2
    raise ValueError("the v0.2.1 claim grid supports k in {3,4}")


def build_minimum_width_bracket(
    support_size: int,
    intermediate_rows: Sequence[dict[str, object]],
    anchor_width: int,
) -> dict[str, object]:
    """Build the draft's exact minimum or honest unresolved bracket.

    ``intermediate_rows`` must contain every integer width strictly between
    ``support_size`` and ``anchor_width`` exactly once.  The analytic boundary
    at ``s=k`` is a non-crossover, and the sealed v0.2 anchor is a certified
    crossover.
    """

    by_width = {int(row["block_size"]): str(row["status"]) for row in intermediate_rows}
    expected = set(range(support_size + 1, anchor_width))
    if len(intermediate_rows) != len(expected) or set(by_width) != expected:
        raise ValueError("intermediate width rows are incomplete or duplicated")
    if any(status not in CLASSIFICATION_STATUSES for status in by_width.values()):
        raise ValueError("unknown crossover classification")
    statuses = {
        support_size: STATUS_IMPOSSIBLE,
        **by_width,
        anchor_width: STATUS_CERTIFIED,
    }
    s_yes = min(
        width for width, status in statuses.items() if status == STATUS_CERTIFIED
    )
    smaller = {width: statuses[width] for width in range(support_size, s_yes)}
    impossible = [
        width for width, status in smaller.items() if status == STATUS_IMPOSSIBLE
    ]
    unresolved = [
        width for width, status in smaller.items() if status == STATUS_UNRESOLVED
    ]
    s_no = support_size
    for width in range(support_size + 1, s_yes):
        if statuses[width] != STATUS_IMPOSSIBLE:
            break
        s_no = width
    s_star = (
        s_yes if not unresolved and len(impossible) == s_yes - support_size else None
    )
    return {
        "s_no": s_no,
        "s_yes": s_yes,
        "s_star": s_star,
        "unresolved_widths": unresolved,
        "interval": None if s_star is not None else f"({s_no},{s_yes}]",
        "status_by_width": {str(width): statuses[width] for width in sorted(statuses)},
    }


def design_record(design: ExactTestDesign | None) -> dict[str, object] | None:
    if design is None:
        return None
    return {
        "query_count": design.query_count,
        "samples_per_query": design.samples_per_query,
        "total_samples": design.total_samples,
        "cutoff": design.cutoff,
        "null_tail": str(design.null_tail),
        "familywise_error_upper": str(design.familywise_error_upper),
        "signal_power_lower": str(design.signal_power_lower),
        "fwer_mode": design.fwer_mode,
    }


def classification_record(classification: CostClassification) -> dict[str, object]:
    return {
        "status": classification.status,
        "lower_query_bound": classification.lower_query_bound,
        "upper_query_bound": classification.upper_query_bound,
        "evaluated_query_counts": classification.evaluated_query_counts,
        "baseline": design_record(classification.baseline),
        "best_certified": design_record(classification.certified_design),
        "optimistic_floor": design_record(classification.optimistic_design),
    }


def metric_robustness_probes(
    primary: CostClassification,
    baseline_query_count: int,
    flip_rate: Fraction,
    alpha: Fraction,
    target_power: Fraction,
    sample_cap: int,
) -> tuple[dict[str, object], ...]:
    """Return one identity diagnostic and four non-binding robustness probes."""

    lower = primary.lower_query_bound
    upper = primary.upper_query_bound
    alternatives = (
        (
            "D1_primary_bound_interval_replay",
            primary.status,
            {
                "metric": "exact total samples over every integer q in [L,U]",
                "evaluated_query_counts": primary.evaluated_query_counts,
                "record_kind": "identity_diagnostic",
                "counts_toward_robustness": False,
            },
        ),
        (
            "P2_query_count_only",
            classify_query_interval(lower, upper, baseline_query_count),
            {
                "metric": "query count without replicate cost",
                "record_kind": "robustness_probe",
                "probe_family": "query_count_only_alternative",
                "counts_toward_robustness": True,
            },
        ),
        (
            "P3_stricter_familywise_error",
            classify_cost_interval(
                lower,
                upper,
                baseline_query_count,
                flip_rate,
                alpha / 2,
                target_power,
                sample_cap,
            ).status,
            {
                "alpha": str(alpha / 2),
                "fwer_mode": "bonferroni",
                "record_kind": "robustness_probe",
                "probe_family": "stricter_alpha_alternative",
                "counts_toward_robustness": True,
            },
        ),
        (
            "P4_stricter_power",
            classify_cost_interval(
                lower,
                upper,
                baseline_query_count,
                flip_rate,
                alpha,
                Fraction(19, 20),
                sample_cap,
            ).status,
            {
                "target_power": "19/20",
                "fwer_mode": "bonferroni",
                "record_kind": "robustness_probe",
                "probe_family": "stricter_power_alternative",
                "counts_toward_robustness": True,
            },
        ),
        (
            "P5_exact_independent_fwer",
            classify_cost_interval(
                lower,
                upper,
                baseline_query_count,
                flip_rate,
                alpha,
                target_power,
                sample_cap,
                fwer_mode="independent_exact",
            ).status,
            {
                "alpha": str(alpha),
                "fwer_mode": "independent_exact",
                "assumption": "fresh query samples are independent",
                "record_kind": "robustness_probe",
                "probe_family": "independent_fwer_alternative",
                "counts_toward_robustness": True,
            },
        ),
    )
    return tuple(
        {
            "probe_id": probe_id,
            "status": status,
            "agrees_with_primary": status == primary.status,
            "binding": False,
            **details,
        }
        for probe_id, status, details in alternatives
    )
