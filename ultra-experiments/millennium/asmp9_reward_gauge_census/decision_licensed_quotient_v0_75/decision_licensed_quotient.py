"""Decision-derived linear reward quotient for ASMP-9 v0.75."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import sympy as sp


def matrix(rows: Sequence[Sequence[object]]) -> sp.Matrix:
    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def _column_basis(value: sp.Matrix, ambient_rows: int) -> sp.Matrix:
    columns = value.columnspace()
    return sp.Matrix.hstack(*columns) if columns else sp.zeros(ambient_rows, 0)


def _null_basis(value: sp.Matrix, ambient_rows: int) -> sp.Matrix:
    columns = value.nullspace()
    return sp.Matrix.hstack(*columns) if columns else sp.zeros(ambient_rows, 0)


def occupancy_difference_matrix(occupancies: sp.Matrix) -> sp.Matrix:
    """Return policy rows relative to the registered first policy."""

    if occupancies.rows == 0 or occupancies.cols == 0:
        raise ValueError("occupancy matrix must be nonempty")
    reference = occupancies.row(0)
    return sp.Matrix.vstack(
        *[
            occupancies.row(index) - reference
            for index in range(1, occupancies.rows)
        ]
    ) if occupancies.rows > 1 else sp.zeros(0, occupancies.cols)


@dataclass(frozen=True)
class DecisionLicensedAnalysis:
    reward_dimension: int
    policy_count: int
    decision_rank: int
    gauge_dimension: int
    effective_measurement_rank: int
    exactly_identifies_decision_quotient: bool
    decision_matrix: sp.Matrix
    gauge_basis: sp.Matrix
    effective_map: sp.Matrix
    non_gauge_witness: sp.Matrix | None

    def to_jsonable(self) -> dict[str, object]:
        def rows(value: sp.Matrix | None) -> list[list[str]] | None:
            if value is None:
                return None
            return [
                [str(value[row, column]) for column in range(value.cols)]
                for row in range(value.rows)
            ]

        return {
            "reward_dimension": self.reward_dimension,
            "policy_count": self.policy_count,
            "decision_rank": self.decision_rank,
            "gauge_dimension": self.gauge_dimension,
            "effective_measurement_rank": self.effective_measurement_rank,
            "exactly_identifies_decision_quotient": (
                self.exactly_identifies_decision_quotient
            ),
            "decision_matrix": rows(self.decision_matrix),
            "gauge_basis": rows(self.gauge_basis),
            "effective_map": rows(self.effective_map),
            "non_gauge_witness": rows(self.non_gauge_witness),
        }


def analyze_decision_licensed_quotient(
    occupancies: sp.Matrix,
    measurement: sp.Matrix,
    nuisance_basis: sp.Matrix,
) -> DecisionLicensedAnalysis:
    """Derive the all-margin gauge, then test representative-free access."""

    if occupancies.cols != measurement.cols:
        raise ValueError("occupancies and rewards have different dimensions")
    if nuisance_basis.rows != measurement.rows:
        raise ValueError("nuisance basis must live in measurement space")

    reward_dimension = occupancies.cols
    decision = occupancy_difference_matrix(occupancies)
    gauge = _null_basis(decision, reward_dimension)
    decision_rank = decision.rank()

    visible_gauge = measurement * gauge
    joint_nuisance = _column_basis(
        nuisance_basis.row_join(visible_gauge),
        measurement.rows,
    )
    output_complement = _null_basis(joint_nuisance.T, measurement.rows)

    # The row space of the decision matrix is the standard-inner-product
    # complement of its kernel and supplies quotient coordinates.
    quotient_basis = _column_basis(decision.T, reward_dimension)
    effective_map = output_complement.T * measurement * quotient_basis
    effective_rank = effective_map.rank()
    exact = effective_rank == decision_rank

    non_gauge_witness = None
    if not exact:
        representative_free_channel = output_complement.T * measurement
        for candidate in representative_free_channel.nullspace():
            if not (decision * candidate).is_zero_matrix:
                non_gauge_witness = candidate
                break
        if non_gauge_witness is None:
            raise AssertionError("failed to construct non-gauge kernel witness")

    return DecisionLicensedAnalysis(
        reward_dimension=reward_dimension,
        policy_count=occupancies.rows,
        decision_rank=decision_rank,
        gauge_dimension=gauge.cols,
        effective_measurement_rank=effective_rank,
        exactly_identifies_decision_quotient=exact,
        decision_matrix=decision,
        gauge_basis=gauge,
        effective_map=effective_map,
        non_gauge_witness=non_gauge_witness,
    )
