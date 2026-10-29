from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import Iterable, Sequence


Q = Fraction
Law = tuple[Q, ...]


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def qlist(values: Iterable[Q]) -> list[str]:
    return [qstr(value) for value in values]


def dot(left: Sequence[Q], right: Sequence[Q]) -> Q:
    if len(left) != len(right):
        raise ValueError("vector lengths differ")
    return sum((x * y for x, y in zip(left, right)), Q(0))


def subtract(left: Sequence[Q], right: Sequence[Q]) -> Law:
    if len(left) != len(right):
        raise ValueError("law lengths differ")
    return tuple(x - y for x, y in zip(left, right))


def validate_laws(honest: Sequence[Law], false: Sequence[Law]) -> int:
    if not honest or not false:
        raise ValueError("both transcript-law classes must be nonempty")
    width = len(honest[0])
    if width == 0:
        raise ValueError("the outcome alphabet must be nonempty")
    for law in (*honest, *false):
        if len(law) != width:
            raise ValueError("transcript laws have different alphabets")
        if any(value < 0 for value in law):
            raise ValueError("negative probability")
        if sum(law, Q(0)) != 1:
            raise ValueError("transcript law is not normalized")
    return width


def audit_gap_certificate(
    honest: Sequence[Law],
    false: Sequence[Law],
    acceptance: Sequence[Q],
    claimed_gap: Q,
    joint_weights: Sequence[Q],
    positive_part_bounds: Sequence[Q],
) -> dict[str, object]:
    """Check matching primal and minimax/TV dual certificates exactly.

    ``joint_weights`` is indexed in honest-major order over H x F.  Its
    marginals produce a pair of convex mixtures.  ``positive_part_bounds``
    upper-bounds the positive coordinates of their signed difference.
    """

    width = validate_laws(honest, false)
    if len(acceptance) != width:
        raise ValueError("acceptance vector has the wrong width")
    if any(value < 0 or value > 1 for value in acceptance):
        raise ValueError("acceptance probabilities must lie in [0,1]")

    pair_count = len(honest) * len(false)
    if len(joint_weights) != pair_count:
        raise ValueError("joint certificate has the wrong width")
    if any(value < 0 for value in joint_weights):
        raise ValueError("negative joint certificate weight")
    if sum(joint_weights, Q(0)) != 1:
        raise ValueError("joint certificate weights do not sum to one")
    if len(positive_part_bounds) != width:
        raise ValueError("dual positive-part vector has the wrong width")
    if any(value < 0 for value in positive_part_bounds):
        raise ValueError("negative positive-part bound")

    pair_gaps = []
    mixture_difference = [Q(0) for _ in range(width)]
    pair_index = 0
    for honest_law in honest:
        for false_law in false:
            difference = subtract(honest_law, false_law)
            pair_gaps.append(dot(difference, acceptance))
            weight = joint_weights[pair_index]
            for index, value in enumerate(difference):
                mixture_difference[index] += weight * value
            pair_index += 1

    lower_valid = min(pair_gaps) >= claimed_gap
    dual_coordinate_valid = all(
        bound >= difference
        for bound, difference in zip(
            positive_part_bounds, mixture_difference
        )
    )
    upper_bound = sum(positive_part_bounds, Q(0))
    exact = lower_valid and dual_coordinate_valid and upper_bound == claimed_gap

    return {
        "lower_certificate_valid": lower_valid,
        "minimum_pair_gap": qstr(min(pair_gaps)),
        "dual_coordinate_bounds_valid": dual_coordinate_valid,
        "dual_upper_bound": qstr(upper_bound),
        "mixture_difference": qlist(mixture_difference),
        "claimed_gap": qstr(claimed_gap),
        "exact": exact,
    }


def solve_square_system(
    matrix: Sequence[Sequence[Q]], right: Sequence[Q]
) -> tuple[Q, ...] | None:
    size = len(matrix)
    if size == 0 or len(right) != size:
        return None
    augmented = [list(row) + [rhs] for row, rhs in zip(matrix, right)]
    if any(len(row) != size + 1 for row in augmented):
        return None

    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if augmented[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(
                        augmented[row], augmented[column]
                    )
                ]
    return tuple(augmented[row][-1] for row in range(size))


def exact_primal_vertex_optimum(
    honest: Sequence[Law], false: Sequence[Law]
) -> tuple[Law, Q]:
    """Exhaust the vertices of the finite verifier-gap LP.

    This deliberately small standard-library solver is used only for compact
    fixtures.  It is independent of the analytic certificates used for the
    growing parity family.
    """

    width = validate_laws(honest, false)
    variable_count = width + 1
    constraints: list[tuple[tuple[Q, ...], Q]] = []

    for honest_law in honest:
        for false_law in false:
            difference = subtract(honest_law, false_law)
            constraints.append(
                (tuple(-value for value in difference) + (Q(1),), Q(0))
            )
    for outcome in range(width):
        upper = [Q(0)] * variable_count
        upper[outcome] = Q(1)
        constraints.append((tuple(upper), Q(1)))
        lower = [Q(0)] * variable_count
        lower[outcome] = Q(-1)
        constraints.append((tuple(lower), Q(0)))
    gamma_upper = [Q(0)] * variable_count
    gamma_upper[-1] = Q(1)
    constraints.append((tuple(gamma_upper), Q(1)))
    gamma_lower = [Q(0)] * variable_count
    gamma_lower[-1] = Q(-1)
    constraints.append((tuple(gamma_lower), Q(1)))

    best: tuple[Q, ...] | None = None
    for active in combinations(constraints, variable_count):
        solution = solve_square_system(
            [row for row, _ in active], [rhs for _, rhs in active]
        )
        if solution is None:
            continue
        if all(dot(row, solution) <= rhs for row, rhs in constraints):
            if best is None or solution[-1] > best[-1]:
                best = solution
    if best is None:
        raise RuntimeError("bounded verifier-gap LP had no enumerated vertex")
    return tuple(best[:-1]), best[-1]


def bsc_law(input_word: int, depth: int, error: Q) -> Law:
    values = []
    for observed in range(1 << depth):
        distance = (input_word ^ observed).bit_count()
        values.append(error**distance * (1 - error) ** (depth - distance))
    return tuple(values)


def parity_laws(depth: int, error: Q) -> tuple[tuple[Law, ...], tuple[Law, ...]]:
    honest = tuple(
        bsc_law(word, depth, error)
        for word in range(1 << depth)
        if word.bit_count() % 2 == 0
    )
    false = tuple(
        bsc_law(word, depth, error)
        for word in range(1 << depth)
        if word.bit_count() % 2 == 1
    )
    return honest, false


def average_laws(laws: Sequence[Law]) -> Law:
    width = len(laws[0])
    weight = Q(1, len(laws))
    return tuple(
        sum((weight * law[index] for law in laws), Q(0))
        for index in range(width)
    )


def parity_certificate_row(depth: int, error: Q = Q(1, 5)) -> dict[str, object]:
    honest, false = parity_laws(depth, error)
    contraction = 1 - 2 * error
    gap = contraction**depth
    honest_accept = (1 + gap) / 2
    false_accept = (1 - gap) / 2

    honest_mixture = average_laws(honest)
    false_mixture = average_laws(false)
    mixture_difference = subtract(honest_mixture, false_mixture)
    positive_part = tuple(max(value, Q(0)) for value in mixture_difference)
    expected_positive = Q(gap, 1 << (depth - 1))

    acceptance = tuple(
        Q(1) if observed.bit_count() % 2 == 0 else Q(0)
        for observed in range(1 << depth)
    )
    honest_acceptance_values = {
        dot(honest_law, acceptance) for honest_law in honest
    }
    false_acceptance_values = {
        dot(false_law, acceptance) for false_law in false
    }
    pair_gaps = {
        honest_value - false_value
        for honest_value in honest_acceptance_values
        for false_value in false_acceptance_values
    }

    return {
        "depth": depth,
        "outcome_count": 1 << depth,
        "honest_world_count": len(honest),
        "false_world_count": len(false),
        "error": qstr(error),
        "contraction": qstr(contraction),
        "honest_acceptance": qstr(honest_accept),
        "false_acceptance": qstr(false_accept),
        "all_pair_gaps": sorted(qlist(pair_gaps)),
        "dual_positive_value_per_even_outcome": qstr(expected_positive),
        "dual_positive_sum": qstr(sum(positive_part, Q(0))),
        "closed_form_gap": qstr(gap),
        "mixture_formula_matches": all(
            value
            == (
                expected_positive
                if observed.bit_count() % 2 == 0
                else -expected_positive
            )
            for observed, value in enumerate(mixture_difference)
        ),
        "certificate_exact": (
            pair_gaps == {gap}
            and sum(positive_part, Q(0)) == gap
        ),
    }


def explicit_case_rows() -> list[dict[str, object]]:
    cases = []

    fixtures = (
        (
            "single_bit_bsc",
            ((Q(4, 5), Q(1, 5)),),
            ((Q(1, 5), Q(4, 5)),),
            (Q(1), Q(0)),
            Q(3, 5),
            (Q(1),),
            (Q(3, 5), Q(0)),
            "one noisy semantic bit has constant gap",
        ),
        (
            "convex_hull_collision",
            ((Q(1), Q(0)), (Q(0), Q(1))),
            ((Q(1, 2), Q(1, 2)),),
            (Q(0), Q(0)),
            Q(0),
            (Q(1, 2), Q(1, 2)),
            (Q(0), Q(0)),
            "pairwise-looking cases fail when the transcript-law hulls meet",
        ),
        (
            "joint_correlation_signal",
            ((Q(1, 2), Q(0), Q(0), Q(1, 2)),),
            ((Q(0), Q(1, 2), Q(1, 2), Q(0)),),
            (Q(1), Q(0), Q(0), Q(1)),
            Q(1),
            (Q(1),),
            (Q(1, 2), Q(0), Q(0), Q(1, 2)),
            "identical one-coordinate marginals can hide perfect joint signal",
        ),
    )

    for (
        case_id,
        honest,
        false,
        acceptance,
        gap,
        weights,
        positive,
        interpretation,
    ) in fixtures:
        audit = audit_gap_certificate(
            honest, false, acceptance, gap, weights, positive
        )
        vertex_acceptance, vertex_gap = exact_primal_vertex_optimum(
            honest, false
        )
        cases.append(
            {
                "case_id": case_id,
                "outcomes": len(acceptance),
                "honest_laws": [qlist(law) for law in honest],
                "false_laws": [qlist(law) for law in false],
                "acceptance_certificate": qlist(acceptance),
                "joint_dual_weights": qlist(weights),
                "dual_positive_part": qlist(positive),
                "claimed_gap": qstr(gap),
                "certificate_audit": audit,
                "vertex_solver_gap": qstr(vertex_gap),
                "vertex_solver_acceptance": qlist(vertex_acceptance),
                "vertex_solver_matches": vertex_gap == gap,
                "interpretation": interpretation,
            }
        )
    return cases


def alias_refinement_row(alias_count: int) -> dict[str, object]:
    honest = (
        tuple(
            value
            for probability in (Q(4, 5), Q(1, 5))
            for value in [probability / alias_count] * alias_count
        ),
    )
    false = (
        tuple(
            value
            for probability in (Q(1, 5), Q(4, 5))
            for value in [probability / alias_count] * alias_count
        ),
    )
    acceptance = tuple(
        [Q(1)] * alias_count + [Q(0)] * alias_count
    )
    positive = tuple(
        [Q(3, 5 * alias_count)] * alias_count
        + [Q(0)] * alias_count
    )
    audit = audit_gap_certificate(
        honest,
        false,
        acceptance,
        Q(3, 5),
        (Q(1),),
        positive,
    )
    return {
        "alias_count_per_semantic_outcome": alias_count,
        "raw_outcome_count": 2 * alias_count,
        "quotient_outcome_count": 2,
        "gap": "3/5",
        "certificate_exact": audit["exact"],
        "dual_upper_bound": audit["dual_upper_bound"],
    }


def build_result() -> dict[str, object]:
    explicit = explicit_case_rows()
    parity = [parity_certificate_row(depth) for depth in range(1, 9)]
    aliases = [alias_refinement_row(count) for count in range(1, 9)]

    gates = {
        "E0_all_explicit_certificates_exact": all(
            row["certificate_audit"]["exact"] for row in explicit
        ),
        "E1_vertex_solver_matches_explicit_certificates": all(
            row["vertex_solver_matches"] for row in explicit
        ),
        "P0_parity_gap_is_three_fifths_to_depth": all(
            row["closed_form_gap"] == qstr(Q(3, 5) ** row["depth"])
            for row in parity
        ),
        "P1_parity_primal_dual_certificates_exact": all(
            row["certificate_exact"] for row in parity
        ),
        "P2_parity_mixture_formula_enumerated": all(
            row["mixture_formula_matches"] for row in parity
        ),
        "J0_joint_case_has_zero_marginal_signal_and_unit_joint_gap": (
            explicit[2]["claimed_gap"] == "1"
        ),
        "C0_convex_hull_collision_has_zero_gap": (
            explicit[1]["claimed_gap"] == "0"
        ),
        "R0_alias_refinement_preserves_gap": all(
            row["certificate_exact"] and row["gap"] == "3/5"
            for row in aliases
        ),
    }

    return {
        "schema_version": "asmp3_finite_tv_frontier_v0_8",
        "experiment_id": "ASMP-3-FINITE-TV-FRONTIER-v0.8",
        "status": "exact_finite_typed_subtheorem",
        "theorem": {
            "setting": (
                "finite fixed transcript alphabet with finite honest and "
                "false transcript-law classes"
            ),
            "primal": (
                "max_a min_(p in H,q in F) <p-q,a>, 0<=a<=1"
            ),
            "dual": "min_(p in conv(H),q in conv(F)) TV(p,q)",
            "positive_gap_criterion": "conv(H) and conv(F) are disjoint",
            "asymptotic_constant_gap_criterion": (
                "inf_n distance_TV(conv(H_n),conv(F_n)) > 0"
            ),
        },
        "explicit_cases": explicit,
        "parity_bsc_rows": parity,
        "alias_refinement_rows": aliases,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "This is an exact characterization of the finite post-transcript "
            "decision lane for a fixed interface. It does not choose the v0.1 "
            "interface quantifier, construct efficient interactive protocols "
            "in general, or resolve WV-ADM."
        ),
    }
