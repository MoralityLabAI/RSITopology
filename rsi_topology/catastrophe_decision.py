"""Scope-aware interval audit for comparative catastrophic-risk assertions.

Uses *causal delta* intervals supplied by a study. This module does not infer
probabilities from stakes, rhetoric, policy preferences, or model output.
It never performs an intervention and cannot authenticate external evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Sequence


@dataclass(frozen=True)
class Interval:
    lower: float
    upper: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.lower) and math.isfinite(self.upper)
                and self.lower <= self.upper):
            raise ValueError("interval endpoints must be finite and ordered")


@dataclass(frozen=True)
class CausalDeltas:
    nuclear: Interval | None
    ai_control: Interval | None
    independent_roots: tuple[str, ...] = ()
    study_id: str = ""
    identification: str = "unidentified"  # unidentified | assumed | assessed
    scope: str = "synthetic"  # synthetic | external

    def __post_init__(self) -> None:
        if self.identification not in {"unidentified", "assumed", "assessed"}:
            raise ValueError("unknown identification status")
        if self.scope not in {"synthetic", "external"}:
            raise ValueError("unknown scope")
        for delta in (self.nuclear, self.ai_control):
            if delta is not None and (delta.lower < -1 or delta.upper > 1):
                raise ValueError("probability deltas must be inside [-1,1]")
        if any(not isinstance(root, str) for root in self.independent_roots):
            raise ValueError("roots must be strings")


@dataclass(frozen=True)
class Governance:
    authorized: bool
    independently_audited: bool
    human_recall: bool
    transparent_protocol: bool

    def __post_init__(self) -> None:
        if any(type(v) is not bool for v in (
            self.authorized, self.independently_audited,
            self.human_recall, self.transparent_protocol,
        )):
            raise ValueError("governance flags must be boolean")

    def violations(self) -> tuple[str, ...]:
        return tuple(name for name in (
            "authorized", "independently_audited", "human_recall",
            "transparent_protocol",
        ) if not getattr(self, name))


@dataclass(frozen=True)
class LossModel:
    nuclear_loss: float
    control_loss: float
    intervention_cost: Interval

    def __post_init__(self) -> None:
        if (not math.isfinite(self.nuclear_loss) or self.nuclear_loss < 0
                or not math.isfinite(self.control_loss) or self.control_loss < 0
                or self.intervention_cost.lower < 0):
            raise ValueError("loss weights and direct costs must be finite and nonnegative")


def evidence_grade(data: CausalDeltas) -> str:
    """Receipt quality grade, not a claim that a source is authentic."""
    if data.nuclear is None or data.ai_control is None:
        return "missing_deltas"
    if data.identification == "unidentified":
        return "unidentified"
    if data.identification == "assumed":
        return "assumption_only"
    if (not data.study_id.strip() or len(data.independent_roots) < 2
            or any(not r.strip() for r in data.independent_roots)
            or len(set(data.independent_roots)) != len(data.independent_roots)):
        return "provenance_gap"
    return "synthetic_assessed" if data.scope == "synthetic" else "external_assessment_unverified"


def expected_loss_bounds(data: CausalDeltas, model: LossModel) -> Interval | None:
    """Sound outer enclosure for Ln Δpn + Lc Δpc + Δcost.

    Marginal interval arithmetic may be conservative when deltas correlate.
    """
    if data.nuclear is None or data.ai_control is None:
        return None
    return Interval(
        model.nuclear_loss * data.nuclear.lower
        + model.control_loss * data.ai_control.lower
        + model.intervention_cost.lower,
        model.nuclear_loss * data.nuclear.upper
        + model.control_loss * data.ai_control.upper
        + model.intervention_cost.upper,
    )


def audit_comparison(data: CausalDeltas, governance: Governance,
                     model: LossModel, *, asserted: str = "unknown") -> dict:
    """Audit an intervention relative to a specified unchanged baseline.

    asserted: 'benefit', 'harm', or 'unknown'. A robust sign uses strict
    inequalities, treating contact with zero as unresolved.
    """
    if asserted not in {"benefit", "harm", "unknown"}:
        raise ValueError("assertion must be benefit, harm or unknown")
    grade = evidence_grade(data)
    bounds = expected_loss_bounds(data, model)
    sign = "unresolved"
    if bounds is not None:
        if bounds.upper < 0:
            sign = "benefit"
        elif bounds.lower > 0:
            sign = "harm"
    gaps = governance.violations()
    identified = grade in {"synthetic_assessed", "external_assessment_unverified"}
    if gaps:
        decision = "blocked_governance"
    elif not identified:
        decision = "request_evidence"
    elif sign == "harm":
        decision = "reject_predicted_harm"
    elif sign == "benefit":
        decision = "eligible_for_independent_review"
    else:
        decision = "review_uncertainty"
    # A supplied external receipt still requires outside verification.
    claim_supported_in_scope = identified and asserted == sign and asserted != "unknown"
    receipt = {
        "schema": "catastrophe_comparison_v1",
        "study_id": data.study_id,
        "scope": data.scope,
        "evidence_grade": grade,
        "provenance_roots": sorted(set(data.independent_roots)),
        "governance_violations": list(gaps),
        "delta_expected_loss": None if bounds is None else {
            "lower": bounds.lower, "upper": bounds.upper,
        },
        "interval_sign": sign,
        "asserted_direction": asserted,
        "claim_supported_in_stated_scope": claim_supported_in_scope,
        "empirical_validity_verified": False,
        "decision": decision,
    }
    receipt["sha256"] = hashlib.sha256(json.dumps(
        receipt, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()
    return receipt


def finite_frc_tail_audit(fidelity: Sequence[float]) -> dict:
    """Finite observed suffix infima, with no extrapolation to liminf at infinity."""
    if not fidelity:
        raise ValueError("at least one observed generation is required")
    if any(not math.isfinite(v) or not 0 <= v <= 1 for v in fidelity):
        raise ValueError("fidelity must lie in [0,1]")
    suffix = [0.0] * len(fidelity)
    floor = 1.0
    for i in range(len(fidelity) - 1, -1, -1):
        floor = min(floor, fidelity[i])
        suffix[i] = floor
    return {
        "observed_generations": len(fidelity),
        "observed_suffix_infima": suffix,
        "last_observed_fidelity": fidelity[-1],
        "infinite_liminf_certified": False,
        "future_uniform_bound_required": True,
    }
