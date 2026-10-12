from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence


Q = Fraction
Vector = tuple[Q, ...]
Matrix = tuple[Vector, ...]


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def qvector(values: Iterable[Q]) -> list[str]:
    return [qstr(value) for value in values]


def dot(left: Sequence[Q], right: Sequence[Q]) -> Q:
    if len(left) != len(right):
        raise ValueError("vector dimensions differ")
    return sum((x * y for x, y in zip(left, right)), Q(0))


@dataclass(frozen=True)
class HPolytope:
    inequalities: Matrix
    bounds: Vector
    equalities: Matrix
    targets: Vector

    @property
    def dimension(self) -> int:
        rows = (*self.inequalities, *self.equalities)
        if not rows:
            raise ValueError("polytope needs at least one constraint row")
        return len(rows[0])

    def validate_shape(self) -> None:
        dimension = self.dimension
        if len(self.inequalities) != len(self.bounds):
            raise ValueError("inequality row/bound count mismatch")
        if len(self.equalities) != len(self.targets):
            raise ValueError("equality row/target count mismatch")
        if any(
            len(row) != dimension
            for row in (*self.inequalities, *self.equalities)
        ):
            raise ValueError("polytope row dimensions differ")

    def contains(self, point: Sequence[Q]) -> bool:
        self.validate_shape()
        if len(point) != self.dimension:
            return False
        return all(
            dot(row, point) <= bound
            for row, bound in zip(self.inequalities, self.bounds)
        ) and all(
            dot(row, point) == target
            for row, target in zip(self.equalities, self.targets)
        )


def law_polytope(
    dimension: int,
    extra_inequalities: Sequence[tuple[Sequence[Q], Q]] = (),
    extra_equalities: Sequence[tuple[Sequence[Q], Q]] = (),
) -> HPolytope:
    inequalities = [tuple(row) for row, _ in extra_inequalities]
    bounds = [bound for _, bound in extra_inequalities]
    for index in range(dimension):
        row = [Q(0)] * dimension
        row[index] = Q(-1)
        inequalities.append(tuple(row))
        bounds.append(Q(0))
    equalities = [(Q(1),) * dimension]
    targets = [Q(1)]
    equalities.extend(tuple(row) for row, _ in extra_equalities)
    targets.extend(target for _, target in extra_equalities)
    return HPolytope(
        tuple(inequalities), tuple(bounds), tuple(equalities), tuple(targets)
    )


def dual_linear_combination(
    polytope: HPolytope,
    inequality_multipliers: Sequence[Q],
    equality_multipliers: Sequence[Q],
) -> tuple[Vector, Q]:
    polytope.validate_shape()
    if len(inequality_multipliers) != len(polytope.inequalities):
        raise ValueError("wrong number of inequality multipliers")
    if len(equality_multipliers) != len(polytope.equalities):
        raise ValueError("wrong number of equality multipliers")
    if any(value < 0 for value in inequality_multipliers):
        raise ValueError("inequality dual multipliers must be nonnegative")

    coefficients = tuple(
        sum(
            (
                multiplier * row[column]
                for multiplier, row in zip(
                    inequality_multipliers, polytope.inequalities
                )
            ),
            Q(0),
        )
        + sum(
            (
                multiplier * row[column]
                for multiplier, row in zip(
                    equality_multipliers, polytope.equalities
                )
            ),
            Q(0),
        )
        for column in range(polytope.dimension)
    )
    objective = dot(inequality_multipliers, polytope.bounds) + dot(
        equality_multipliers, polytope.targets
    )
    return coefficients, objective


def verify_maximum_dual_bound(
    polytope: HPolytope,
    objective_coefficients: Sequence[Q],
    inequality_multipliers: Sequence[Q],
    equality_multipliers: Sequence[Q],
    claimed_upper_bound: Q,
) -> dict[str, object]:
    coefficients, objective = dual_linear_combination(
        polytope, inequality_multipliers, equality_multipliers
    )
    coefficient_match = tuple(objective_coefficients) == coefficients
    bound_valid = objective <= claimed_upper_bound
    return {
        "coefficient_match": coefficient_match,
        "dual_objective": qstr(objective),
        "claimed_upper_bound": qstr(claimed_upper_bound),
        "bound_valid": bound_valid,
        "valid": coefficient_match and bound_valid,
    }


def total_variation(left: Sequence[Q], right: Sequence[Q]) -> Q:
    if len(left) != len(right):
        raise ValueError("law dimensions differ")
    return sum((abs(x - y) for x, y in zip(left, right)), Q(0)) / 2


def audit_polyhedral_certificate(
    honest: HPolytope,
    false: HPolytope,
    acceptance: Sequence[Q],
    honest_lower: Q,
    false_upper: Q,
    honest_dual_y: Sequence[Q],
    honest_dual_z: Sequence[Q],
    false_dual_y: Sequence[Q],
    false_dual_z: Sequence[Q],
    closest_honest: Sequence[Q],
    closest_false: Sequence[Q],
    claimed_gap: Q,
) -> dict[str, object]:
    honest.validate_shape()
    false.validate_shape()
    if honest.dimension != false.dimension:
        raise ValueError("honest and false alphabets differ")
    if len(acceptance) != honest.dimension:
        raise ValueError("acceptance vector has the wrong dimension")
    if any(value < 0 or value > 1 for value in acceptance):
        raise ValueError("acceptance probabilities must lie in [0,1]")

    honest_bound = verify_maximum_dual_bound(
        honest,
        tuple(-value for value in acceptance),
        honest_dual_y,
        honest_dual_z,
        -honest_lower,
    )
    false_bound = verify_maximum_dual_bound(
        false,
        acceptance,
        false_dual_y,
        false_dual_z,
        false_upper,
    )
    lower_gap = honest_lower - false_upper
    honest_witness_valid = honest.contains(closest_honest)
    false_witness_valid = false.contains(closest_false)
    upper_gap = total_variation(closest_honest, closest_false)

    exact = (
        honest_bound["valid"]
        and false_bound["valid"]
        and honest_witness_valid
        and false_witness_valid
        and lower_gap == claimed_gap
        and upper_gap == claimed_gap
    )
    return {
        "honest_minimum_dual": honest_bound,
        "false_maximum_dual": false_bound,
        "honest_closest_witness_valid": honest_witness_valid,
        "false_closest_witness_valid": false_witness_valid,
        "lower_gap": qstr(lower_gap),
        "upper_tv_witness": qstr(upper_gap),
        "claimed_gap": qstr(claimed_gap),
        "exact": exact,
    }


def serialize_polytope(polytope: HPolytope) -> dict[str, object]:
    return {
        "dimension": polytope.dimension,
        "A": [qvector(row) for row in polytope.inequalities],
        "b": qvector(polytope.bounds),
        "E": [qvector(row) for row in polytope.equalities],
        "e": qvector(polytope.targets),
    }


def fixture_rows() -> list[dict[str, object]]:
    fixtures: list[dict[str, object]] = []

    interval_honest = law_polytope(
        2,
        (
            ((Q(-1), Q(0)), Q(-4, 5)),
            ((Q(1), Q(0)), Q(9, 10)),
        ),
    )
    interval_false = law_polytope(
        2,
        (
            ((Q(-1), Q(0)), Q(-1, 10)),
            ((Q(1), Q(0)), Q(1, 5)),
        ),
    )
    fixtures.append(
        {
            "case_id": "interval_noise_bands",
            "interpretation": (
                "continuum law bands retain a constant robust terminal gap"
            ),
            "honest": interval_honest,
            "false": interval_false,
            "acceptance": (Q(1), Q(0)),
            "honest_lower": Q(4, 5),
            "false_upper": Q(1, 5),
            "honest_dual_y": (Q(1), Q(0), Q(0), Q(0)),
            "honest_dual_z": (Q(0),),
            "false_dual_y": (Q(0), Q(1), Q(0), Q(0)),
            "false_dual_z": (Q(0),),
            "closest_honest": (Q(4, 5), Q(1, 5)),
            "closest_false": (Q(1, 5), Q(4, 5)),
            "gap": Q(3, 5),
        }
    )

    full_simplex = law_polytope(2)
    fixed_uniform = law_polytope(
        2,
        (
            ((Q(-1), Q(0)), Q(-1, 2)),
            ((Q(1), Q(0)), Q(1, 2)),
        ),
    )
    fixtures.append(
        {
            "case_id": "polyhedral_hull_collision",
            "interpretation": (
                "a false law inside the honest law polytope forces zero gap"
            ),
            "honest": full_simplex,
            "false": fixed_uniform,
            "acceptance": (Q(0), Q(0)),
            "honest_lower": Q(0),
            "false_upper": Q(0),
            "honest_dual_y": (Q(0), Q(0)),
            "honest_dual_z": (Q(0),),
            "false_dual_y": (Q(0), Q(0), Q(0), Q(0)),
            "false_dual_z": (Q(0),),
            "closest_honest": (Q(1, 2), Q(1, 2)),
            "closest_false": (Q(1, 2), Q(1, 2)),
            "gap": Q(0),
        }
    )

    even_event = (Q(1), Q(0), Q(0), Q(1))
    joint_honest = law_polytope(
        4,
        ((tuple(-value for value in even_event), Q(-4, 5)),),
    )
    joint_false = law_polytope(
        4,
        ((even_event, Q(1, 5)),),
    )
    fixtures.append(
        {
            "case_id": "joint_event_robust_bands",
            "interpretation": (
                "a joint event separates large law polytopes despite "
                "overlapping coordinate marginals"
            ),
            "honest": joint_honest,
            "false": joint_false,
            "acceptance": even_event,
            "honest_lower": Q(4, 5),
            "false_upper": Q(1, 5),
            "honest_dual_y": (Q(1), Q(0), Q(0), Q(0), Q(0)),
            "honest_dual_z": (Q(0),),
            "false_dual_y": (Q(1), Q(0), Q(0), Q(0), Q(0)),
            "false_dual_z": (Q(0),),
            "closest_honest": (Q(4, 5), Q(1, 5), Q(0), Q(0)),
            "closest_false": (Q(1, 5), Q(4, 5), Q(0), Q(0)),
            "gap": Q(3, 5),
            "equal_marginal_honest": (Q(1, 2), Q(0), Q(0), Q(1, 2)),
            "equal_marginal_false": (Q(0), Q(1, 2), Q(1, 2), Q(0)),
        }
    )

    rows = []
    for fixture in fixtures:
        audit = audit_polyhedral_certificate(
            fixture["honest"],
            fixture["false"],
            fixture["acceptance"],
            fixture["honest_lower"],
            fixture["false_upper"],
            fixture["honest_dual_y"],
            fixture["honest_dual_z"],
            fixture["false_dual_y"],
            fixture["false_dual_z"],
            fixture["closest_honest"],
            fixture["closest_false"],
            fixture["gap"],
        )
        row = {
            "case_id": fixture["case_id"],
            "interpretation": fixture["interpretation"],
            "honest_polytope": serialize_polytope(fixture["honest"]),
            "false_polytope": serialize_polytope(fixture["false"]),
            "certificate": {
                "acceptance": qvector(fixture["acceptance"]),
                "honest_lower": qstr(fixture["honest_lower"]),
                "false_upper": qstr(fixture["false_upper"]),
                "honest_dual_y": qvector(fixture["honest_dual_y"]),
                "honest_dual_z": qvector(fixture["honest_dual_z"]),
                "false_dual_y": qvector(fixture["false_dual_y"]),
                "false_dual_z": qvector(fixture["false_dual_z"]),
                "closest_honest": qvector(fixture["closest_honest"]),
                "closest_false": qvector(fixture["closest_false"]),
                "claimed_gap": qstr(fixture["gap"]),
            },
            "audit": audit,
        }
        if "equal_marginal_honest" in fixture:
            row["equal_marginal_witness"] = {
                "honest": qvector(fixture["equal_marginal_honest"]),
                "false": qvector(fixture["equal_marginal_false"]),
            }
        rows.append(row)
    return rows


def build_result() -> dict[str, object]:
    rows = fixture_rows()
    by_id = {row["case_id"]: row for row in rows}
    gates = {
        "P0_all_farkas_lower_certificates_valid": all(
            row["audit"]["honest_minimum_dual"]["valid"]
            and row["audit"]["false_maximum_dual"]["valid"]
            for row in rows
        ),
        "P1_all_closest_law_witnesses_feasible": all(
            row["audit"]["honest_closest_witness_valid"]
            and row["audit"]["false_closest_witness_valid"]
            for row in rows
        ),
        "P2_all_polyhedral_optima_exact": all(
            row["audit"]["exact"] for row in rows
        ),
        "I0_interval_band_gap_is_three_fifths": (
            by_id["interval_noise_bands"]["audit"]["claimed_gap"] == "3/5"
        ),
        "C0_hull_collision_gap_is_zero": (
            by_id["polyhedral_hull_collision"]["audit"]["claimed_gap"] == "0"
        ),
        "J0_joint_event_band_gap_is_three_fifths": (
            by_id["joint_event_robust_bands"]["audit"]["claimed_gap"] == "3/5"
        ),
    }
    return {
        "schema_version": "asmp3_polyhedral_tv_frontier_v0_9",
        "experiment_id": "ASMP-3-POLYHEDRAL-TV-FRONTIER-v0.9",
        "status": "exact_rational_polyhedral_subtheorem",
        "parent_result": "ASMP-3-FINITE-TV-FRONTIER-v0.8",
        "theorem": {
            "input": (
                "nonempty rational H-polytopes P,Q contained in the "
                "terminal-law simplex"
            ),
            "value": "distance_TV(P,Q)",
            "algorithm": (
                "rational linear program in p,q,t with L1 epigraph constraints"
            ),
            "terminal_verifier": (
                "recovered from the LP dual as a bounded separating function"
            ),
            "certificate": (
                "Farkas verifier lower bound plus feasible closest-law TV upper bound"
            ),
        },
        "case_rows": rows,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "This removes explicit law enumeration when the induced truthful "
            "and false law sets already have polynomial-size rational "
            "H-representations. It does not prove that arbitrary interactive "
            "ASMP-3 strategy/noise sets admit such representations."
        ),
    }
