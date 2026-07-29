from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping, Sequence


Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]


def q(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def fraction_text(value: Any) -> str:
    value = q(value)
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def as_vector(values: Sequence) -> Vector:
    return tuple(q(value) for value in values)


def as_matrix(rows: Sequence[Sequence], *, width: int | None = None) -> Matrix:
    result = tuple(as_vector(row) for row in rows)
    if not result:
        raise ValueError("matrix must have at least one row")
    inferred = len(result[0])
    if width is not None and inferred != width:
        raise ValueError("matrix width mismatch")
    if any(len(row) != inferred for row in result):
        raise ValueError("matrix must be rectangular")
    return result


def zeros(rows: int, columns: int) -> Matrix:
    return tuple(
        tuple(Fraction(0) for _ in range(columns))
        for _ in range(rows)
    )


def identity(size: int) -> Matrix:
    return tuple(
        tuple(Fraction(int(row == column)) for column in range(size))
        for row in range(size)
    )


def transpose(matrix: Matrix) -> Matrix:
    if not matrix:
        return ()
    return tuple(tuple(row[index] for row in matrix) for index in range(len(matrix[0])))


def dot(left: Sequence, right: Sequence) -> Fraction:
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    return sum((q(a) * q(b) for a, b in zip(left, right)), Fraction(0))


def matvec(matrix: Matrix, vector: Sequence) -> Vector:
    vector = as_vector(vector)
    if matrix and len(matrix[0]) != len(vector):
        raise ValueError("matrix-vector dimension mismatch")
    return tuple(dot(row, vector) for row in matrix)


def matmul(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right:
        raise ValueError("matrix product requires nonempty matrices")
    if len(left[0]) != len(right):
        raise ValueError("matrix product dimension mismatch")
    columns = transpose(right)
    return tuple(tuple(dot(row, column) for column in columns) for row in left)


def matrix_subtract(left: Matrix, right: Matrix) -> Matrix:
    if len(left) != len(right) or any(
        len(a) != len(b) for a, b in zip(left, right)
    ):
        raise ValueError("matrix dimension mismatch")
    return tuple(
        tuple(a - b for a, b in zip(left_row, right_row))
        for left_row, right_row in zip(left, right)
    )


def vector_add(*vectors: Sequence) -> Vector:
    if not vectors:
        return ()
    width = len(vectors[0])
    if any(len(vector) != width for vector in vectors):
        raise ValueError("vector dimension mismatch")
    return tuple(
        sum((q(vector[index]) for vector in vectors), Fraction(0))
        for index in range(width)
    )


def vector_subtract(left: Sequence, right: Sequence) -> Vector:
    if len(left) != len(right):
        raise ValueError("vector dimension mismatch")
    return tuple(q(a) - q(b) for a, b in zip(left, right))


def solve_square(matrix: Matrix, rhs: Sequence) -> Vector:
    size = len(matrix)
    rhs = as_vector(rhs)
    if size == 0 or len(rhs) != size or any(len(row) != size for row in matrix):
        raise ValueError("nonsingular square system required")
    work = [list(row) + [rhs[index]] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(work[row], work[column])
            ]
    return tuple(row[-1] for row in work)


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("square matrix required")
    columns = [
        solve_square(matrix, identity(size)[column])
        for column in range(size)
    ]
    return transpose(tuple(columns))


def rational_rank(matrix: Matrix) -> int:
    work = [list(row) for row in matrix]
    if not work:
        return 0
    width = len(work[0])
    rank = 0
    for column in range(width):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(len(work)):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == len(work):
            break
    return rank


def nuisance_projector(context_design: Sequence[Sequence]) -> Matrix:
    context = as_matrix(context_design)
    rows = len(context)
    columns = len(context[0])
    if columns == 0:
        return identity(rows)
    if rational_rank(context) != columns:
        raise ValueError("context_design must be a column-space basis")
    gram = matmul(transpose(context), context)
    projection = matmul(matmul(context, inverse(gram)), transpose(context))
    return matrix_subtract(identity(rows), projection)


def quotient_analysis_map(
    nominal_design: Sequence[Sequence],
    context_design: Sequence[Sequence],
) -> dict[str, Any]:
    design = as_matrix(nominal_design)
    context = as_matrix(context_design, width=len(context_design[0]))
    if len(design) != len(context):
        raise ValueError("designs must have the same row count")
    projector = nuisance_projector(context)
    projected = matmul(projector, design)
    dimension = len(design[0])
    rank = rational_rank(projected)
    if rank != dimension:
        return {
            "available": False,
            "dimension": dimension,
            "projected_design": projected,
            "projected_rank": rank,
            "projector": projector,
            "status": "context_confounded",
        }
    gram = matmul(transpose(projected), projected)
    left_inverse = matmul(inverse(gram), transpose(projected))
    analysis_map = matmul(left_inverse, projector)
    if matmul(analysis_map, design) != identity(dimension):
        raise RuntimeError("analysis map is not a left inverse")
    if any(value for row in matmul(analysis_map, context) for value in row):
        raise RuntimeError("analysis map failed to remove context nuisance")
    return {
        "analysis_map": analysis_map,
        "available": True,
        "dimension": dimension,
        "projected_design": projected,
        "projected_rank": rank,
        "projector": projector,
        "status": "available",
    }


def _validate_widths(values: Sequence, size: int, label: str) -> Vector:
    result = as_vector(values)
    if len(result) != size or any(value < 0 for value in result):
        raise ValueError(f"{label} must contain {size} nonnegative widths")
    return result


def box_image_support(
    direction: Sequence,
    transform: Sequence[Sequence],
    widths: Sequence,
) -> Fraction:
    transform = as_matrix(transform)
    direction = as_vector(direction)
    widths = _validate_widths(widths, len(transform[0]), "widths")
    if len(direction) != len(transform):
        raise ValueError("support direction dimension mismatch")
    pulled_back = matvec(transpose(transform), direction)
    return sum(
        (width * abs(coordinate) for width, coordinate in zip(widths, pulled_back)),
        Fraction(0),
    )


def _compose(left: Matrix, right: Matrix) -> Matrix:
    if len(right[0]) == 0:
        return zeros(len(left), 0)
    return matmul(left, right)


def build_joint_certificate(
    nominal_design: Sequence[Sequence],
    context_design: Sequence[Sequence],
    localized_values: Sequence,
    localization_widths: Sequence,
    midpoint_residual_widths: Sequence,
    mechanical_row_l1_widths: Sequence,
    semantic_incidence: Sequence[Sequence],
    semantic_cell_widths: Sequence,
) -> dict[str, Any]:
    access = quotient_analysis_map(nominal_design, context_design)
    if not access["available"]:
        return access
    design = as_matrix(nominal_design)
    rows = len(design)
    localized = _validate_widths(
        [abs(q(value)) for value in localized_values],
        rows,
        "localized_values",
    )
    # Restore signs after using the common length/finiteness validation path.
    localized = as_vector(localized_values)
    localization = _validate_widths(
        localization_widths, rows, "localization_widths"
    )
    midpoint = _validate_widths(
        midpoint_residual_widths, rows, "midpoint_residual_widths"
    )
    mechanical = _validate_widths(
        mechanical_row_l1_widths, rows, "mechanical_row_l1_widths"
    )
    semantic = as_matrix(semantic_incidence)
    if len(semantic) != rows:
        raise ValueError("semantic incidence row count mismatch")
    semantic_widths = _validate_widths(
        semantic_cell_widths,
        len(semantic[0]),
        "semantic_cell_widths",
    )

    analysis_map = access["analysis_map"]
    semantic_map = _compose(analysis_map, semantic)
    theta_hat = matvec(analysis_map, localized)
    additive_rows = tuple(
        left + right for left, right in zip(localization, midpoint)
    )

    coordinate_directions = identity(len(theta_hat))
    additive_coordinate_supports = tuple(
        box_image_support(direction, analysis_map, additive_rows)
        + box_image_support(direction, semantic_map, semantic_widths)
        for direction in coordinate_directions
    )
    additive_radius = max(additive_coordinate_supports, default=Fraction(0))
    mechanical_coordinate_gains = tuple(
        box_image_support(direction, analysis_map, mechanical)
        for direction in coordinate_directions
    )
    mechanical_gain = max(
        mechanical_coordinate_gains, default=Fraction(0)
    )
    if mechanical_gain >= 1:
        return {
            **access,
            "additive_radius": additive_radius,
            "mechanical_gain": mechanical_gain,
            "status": "mechanical_contraction_unavailable",
        }

    theta_radius = (
        max((abs(value) for value in theta_hat), default=Fraction(0))
        + additive_radius
    ) / (1 - mechanical_gain)
    joint_row_widths = tuple(
        additive + theta_radius * drift
        for additive, drift in zip(additive_rows, mechanical)
    )
    return {
        **access,
        "additive_coordinate_supports": additive_coordinate_supports,
        "additive_radius": additive_radius,
        "certificate_available": True,
        "joint_row_widths": joint_row_widths,
        "localization_widths": localization,
        "mechanical_coordinate_gains": mechanical_coordinate_gains,
        "mechanical_gain": mechanical_gain,
        "mechanical_row_l1_widths": mechanical,
        "midpoint_residual_widths": midpoint,
        "semantic_cell_widths": semantic_widths,
        "semantic_incidence": semantic,
        "semantic_map": semantic_map,
        "status": "joint_certificate_available",
        "theta_hat": theta_hat,
        "theta_radius": theta_radius,
    }


def certificate_support(
    certificate: Mapping[str, Any],
    direction: Sequence,
) -> Fraction:
    if not certificate.get("certificate_available"):
        raise ValueError("joint certificate is unavailable")
    return box_image_support(
        direction,
        certificate["analysis_map"],
        certificate["joint_row_widths"],
    ) + box_image_support(
        direction,
        certificate["semantic_map"],
        certificate["semantic_cell_widths"],
    )


def support_witness(
    certificate: Mapping[str, Any],
    direction: Sequence,
) -> dict[str, Any]:
    if not certificate.get("certificate_available"):
        raise ValueError("joint certificate is unavailable")
    direction = as_vector(direction)
    analysis_map = certificate["analysis_map"]
    semantic_map = certificate["semantic_map"]
    row_pullback = matvec(transpose(analysis_map), direction)
    semantic_pullback = matvec(transpose(semantic_map), direction)
    row_source = tuple(
        width * (1 if coordinate > 0 else -1 if coordinate < 0 else 0)
        for width, coordinate in zip(
            certificate["joint_row_widths"], row_pullback
        )
    )
    semantic_source = tuple(
        width * (1 if coordinate > 0 else -1 if coordinate < 0 else 0)
        for width, coordinate in zip(
            certificate["semantic_cell_widths"], semantic_pullback
        )
    )
    error = vector_add(
        matvec(analysis_map, row_source),
        matvec(semantic_map, semantic_source),
    )
    attained = dot(direction, error)
    expected = certificate_support(certificate, direction)
    if attained != expected:
        raise RuntimeError("support witness failed")
    return {
        "attained_support": attained,
        "error": error,
        "row_source": row_source,
        "semantic_source": semantic_source,
    }


def first_argmax(values: Sequence[Fraction]) -> int:
    maximum = max(values)
    return next(index for index, value in enumerate(values) if value == maximum)


def evaluate_policy_family(
    certificate: Mapping[str, Any],
    policy_occupancies: Sequence[Sequence],
) -> dict[str, Any]:
    if not certificate.get("certificate_available"):
        return {
            "available": False,
            "status": certificate["status"],
        }
    occupancies = as_matrix(policy_occupancies)
    if len(occupancies[0]) != len(certificate["theta_hat"]):
        raise ValueError("policy occupancy dimension mismatch")
    values = tuple(dot(certificate["theta_hat"], row) for row in occupancies)
    selected = first_argmax(values)
    rows = []
    regret_bound = Fraction(0)
    identity = True
    for competitor in range(len(occupancies)):
        if competitor == selected:
            continue
        difference = vector_subtract(
            occupancies[selected], occupancies[competitor]
        )
        margin = dot(certificate["theta_hat"], difference)
        uncertainty = certificate_support(certificate, difference)
        lower_margin = margin - uncertainty
        competitor_regret = max(Fraction(0), uncertainty - margin)
        regret_bound = max(regret_bound, competitor_regret)
        row_certified = lower_margin > 0
        identity &= row_certified
        rows.append(
            {
                "competitor": competitor,
                "lower_margin": lower_margin,
                "margin": margin,
                "policy_identity_certified": row_certified,
                "worst_case_competitor_regret": competitor_regret,
                "worst_case_margin_loss": uncertainty,
            }
        )
    return {
        "available": True,
        "estimated_values": values,
        "margin_rows": tuple(rows),
        "policy_identity_certified": identity,
        "robust_regret_bound": regret_bound,
        "selected_policy": selected,
        "status": "evaluated",
    }


def measurement_from_sources(
    nominal_design: Sequence[Sequence],
    context_design: Sequence[Sequence],
    theta: Sequence,
    context_parameter: Sequence,
    mechanical_delta: Sequence[Sequence],
    localization_error: Sequence,
    midpoint_residual: Sequence,
    semantic_incidence: Sequence[Sequence],
    semantic_residual: Sequence,
) -> Vector:
    design = as_matrix(nominal_design)
    context = as_matrix(context_design)
    delta = as_matrix(mechanical_delta)
    semantic = as_matrix(semantic_incidence)
    if len(delta) != len(design) or len(delta[0]) != len(design[0]):
        raise ValueError("mechanical_delta dimension mismatch")
    if len(context) != len(design) or len(semantic) != len(design):
        raise ValueError("source design row mismatch")
    return vector_add(
        matvec(design, theta),
        matvec(delta, theta),
        matvec(context, context_parameter),
        localization_error,
        midpoint_residual,
        matvec(semantic, semantic_residual),
    )


def realized_direction_audit(
    certificate: Mapping[str, Any],
    true_theta: Sequence,
    directions: Sequence[Sequence],
) -> tuple[dict[str, Any], ...]:
    error = vector_subtract(certificate["theta_hat"], true_theta)
    rows = []
    for direction in directions:
        direction = as_vector(direction)
        realized = abs(dot(direction, error))
        support = certificate_support(certificate, direction)
        rows.append(
            {
                "covered": realized <= support,
                "direction": direction,
                "realized_error": realized,
                "support": support,
            }
        )
    return tuple(rows)
