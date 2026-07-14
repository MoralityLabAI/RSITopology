"""Target-blind identity stratification for intervention-vs-random VPD runs."""

from __future__ import annotations

from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from .attestation import AnchorRegistry, LEVEL_ORDER


REQUIRED_FEATURE_FIELDS = (
    "candidate_id",
    "pair_id",
    "arm",
    "site_id",
    "run_replicate",
    "prompt_group",
    "family",
    "norm",
    "rank",
)
REQUIRED_OUTCOME_FIELDS = ("candidate_id", "accepted", "repair_auc", "initial_decay")
ARMS = frozenset({"intervention", "matched_random"})
V02_REQUIRED_FEATURE_FIELDS = REQUIRED_FEATURE_FIELDS + (
    "contrast_type",
    "layer_index",
    "component_type",
    "direction_policy",
    "jacobian_visibility",
    "baseline_activation_rms",
)
CONTRAST_TYPES = frozenset({"direction_value", "site_selection"})
RELATIVE_CALIPER = 0.20


def _canonical_line(item: Mapping[str, Any]) -> bytes:
    return json.dumps(item, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n"


def _canonical_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(f"{label} must be a canonical nonempty string")
    return value


def seal_identity_strata(
    feature_rows: Iterable[Mapping[str, Any]], registry: AnchorRegistry
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Assign target-blind certificate strata and validate matched pairs."""
    sealed: list[dict[str, Any]] = []
    candidate_ids: set[str] = set()
    for raw in feature_rows:
        missing = [field for field in REQUIRED_FEATURE_FIELDS if field not in raw]
        if missing:
            raise ValueError(f"feature row missing fields: {missing}")
        candidate_id = _canonical_id(raw["candidate_id"], "candidate_id")
        pair_id = _canonical_id(raw["pair_id"], "pair_id")
        if candidate_id in candidate_ids:
            raise ValueError(f"duplicate candidate_id: {candidate_id}")
        candidate_ids.add(candidate_id)
        arm = str(raw["arm"])
        if arm not in ARMS:
            raise ValueError(f"invalid arm: {arm}")
        site_id = _canonical_id(raw["site_id"], "site_id")
        certificate = registry.certify(site_id, requested_use="disparate_weight_edit")
        row = {field: raw[field] for field in REQUIRED_FEATURE_FIELDS}
        row.update(
            {
                "candidate_id": candidate_id,
                "pair_id": pair_id,
                "site_id": site_id,
                "identity_stratum": certificate.certification_level,
                "identity_certificate_sha256": certificate.record_sha256,
                "signed_intervention_authorized": certificate.authorized,
                "lineage_margin": certificate.margins["mean_edge_chordal_lineage"],
                "holonomy_angle_margin_degrees": certificate.margins["holonomy_angle_degrees"],
                "det_h_flag": certificate.margins["det_h_orientation"] < 0,
            }
        )
        sealed.append(row)

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in sealed:
        grouped.setdefault(row["pair_id"], []).append(row)
    match_fields = ("site_id", "run_replicate", "prompt_group", "family", "norm", "rank", "identity_stratum")
    for pair_id, rows in grouped.items():
        if len(rows) != 2 or {row["arm"] for row in rows} != ARMS:
            raise ValueError(f"pair {pair_id} must contain exactly one intervention and one matched_random")
        for field in match_fields:
            if rows[0][field] != rows[1][field]:
                raise ValueError(f"pair {pair_id} is not matched on {field}")

    sealed.sort(key=lambda row: row["candidate_id"])
    payload = b"".join(_canonical_line(row) for row in sealed)
    manifest = {
        "schema_version": "1.0.0",
        "named_consumer": "vpd_edit_program",
        "row_count": len(sealed),
        "pair_count": len(grouped),
        "candidate_ids_sha256": sha256(
            "\n".join(row["candidate_id"] for row in sealed).encode()
        ).hexdigest(),
        "sealed_feature_sha256": sha256(payload).hexdigest(),
        "anchor_registry_sha256": registry.sha256,
        "outcomes_present": False,
        "stratum_counts": {
            level: sum(row["identity_stratum"] == level for row in sealed)
            for level in sorted(LEVEL_ORDER, key=LEVEL_ORDER.get)
        },
    }
    return sealed, manifest


def write_sealed_strata(
    directory: str | Path,
    feature_rows: Iterable[Mapping[str, Any]],
    registry: AnchorRegistry,
    *,
    protocol_path: str | Path,
) -> dict[str, Any]:
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    protocol_bytes = Path(protocol_path).read_bytes()
    protocol = json.loads(protocol_bytes)
    if protocol.get("protocol_id") == "vpd_identity_stratification_v0_2":
        sealed, manifest = seal_identity_strata_v02(feature_rows, registry)
    else:
        sealed, manifest = seal_identity_strata(feature_rows, registry)
    manifest["protocol_sha256"] = sha256(protocol_bytes).hexdigest()
    feature_payload = b"".join(_canonical_line(row) for row in sealed)
    manifest_payload = json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False).encode() + b"\n"
    _write_once(output / "sealed_identity_strata.jsonl", feature_payload)
    _write_once(output / "stratification_registration.json", manifest_payload)
    return manifest


def analyze_stratified_outcomes(
    sealed_rows: Iterable[Mapping[str, Any]],
    outcomes: Iterable[Mapping[str, Any]],
    registration: Mapping[str, Any],
) -> dict[str, Any]:
    """Join exact IDs and report only within-stratum paired effects."""
    if registration.get("schema_version") == "0.2.0":
        return analyze_stratified_outcomes_v02(sealed_rows, outcomes, registration)
    sealed = [dict(row) for row in sealed_rows]
    sealed_payload = b"".join(_canonical_line(row) for row in sorted(sealed, key=lambda x: x["candidate_id"]))
    if sha256(sealed_payload).hexdigest() != registration["sealed_feature_sha256"]:
        raise ValueError("sealed feature hash mismatch")

    by_id: dict[str, dict[str, Any]] = {}
    for raw in outcomes:
        missing = [field for field in REQUIRED_OUTCOME_FIELDS if field not in raw]
        if missing:
            raise ValueError(f"outcome row missing fields: {missing}")
        candidate_id = _canonical_id(raw["candidate_id"], "candidate_id")
        if candidate_id in by_id:
            raise ValueError(f"duplicate outcome candidate_id: {candidate_id}")
        accepted = raw["accepted"]
        if isinstance(accepted, bool):
            accepted = int(accepted)
        if accepted not in (0, 1):
            raise ValueError(f"accepted must be 0/1 for {candidate_id}")
        values = {name: float(raw[name]) for name in ("repair_auc", "initial_decay")}
        if not all(np.isfinite(list(values.values()))):
            raise ValueError(f"nonfinite outcomes for {candidate_id}")
        by_id[candidate_id] = {"accepted": int(accepted), **values}

    feature_ids = {row["candidate_id"] for row in sealed}
    if set(by_id) != feature_ids:
        missing = sorted(feature_ids - set(by_id))
        extra = sorted(set(by_id) - feature_ids)
        raise ValueError(f"outcome ID universe mismatch; missing={missing}, extra={extra}")

    pairs: dict[str, dict[str, dict[str, Any]]] = {}
    for row in sealed:
        joined = {**row, **by_id[row["candidate_id"]]}
        pairs.setdefault(row["pair_id"], {})[row["arm"]] = joined

    strata: dict[str, list[dict[str, Any]]] = {}
    for pair_id, arms in pairs.items():
        if set(arms) != ARMS:
            raise ValueError(f"broken sealed pair: {pair_id}")
        intervention, matched = arms["intervention"], arms["matched_random"]
        if intervention["identity_stratum"] != matched["identity_stratum"]:
            raise ValueError(f"identity stratum changed within pair: {pair_id}")
        diff = {
            "pair_id": pair_id,
            "run_replicate": intervention["run_replicate"],
            "accepted": intervention["accepted"] - matched["accepted"],
            "repair_auc": intervention["repair_auc"] - matched["repair_auc"],
            "initial_decay": intervention["initial_decay"] - matched["initial_decay"],
        }
        strata.setdefault(intervention["identity_stratum"], []).append(diff)

    results: dict[str, Any] = {}
    for stratum in sorted(strata, key=LEVEL_ORDER.get):
        rows = strata[stratum]
        results[stratum] = {
            "pair_count": len(rows),
            "accepted": _outcome_summary(rows, "accepted"),
            "repair_auc": _outcome_summary(rows, "repair_auc"),
            "initial_decay": _outcome_summary(rows, "initial_decay"),
        }
    outcome_payload = b"".join(_canonical_line({"candidate_id": key, **by_id[key]}) for key in sorted(by_id))
    return {
        "schema_version": "1.0.0",
        "named_consumer": "vpd_edit_program",
        "analysis_scope": "within_identity_stratum_only",
        "pooled_effect": "prohibited",
        "sealed_feature_sha256": registration["sealed_feature_sha256"],
        "outcome_sha256": sha256(outcome_payload).hexdigest(),
        "strata": results,
    }


def _finite_nonnegative(value: Any, label: str) -> float:
    number = float(value)
    if not np.isfinite(number) or number < 0:
        raise ValueError(f"{label} must be finite and nonnegative")
    return number


def _positive_integer(value: Any, label: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be an integer")
    number = int(value)
    if float(value) != number or number < (0 if allow_zero else 1):
        raise ValueError(f"{label} must be {'nonnegative' if allow_zero else 'positive'} integer")
    return number


def _relative_distance(left: float, right: float) -> float:
    return float(2.0 * abs(left - right) / (abs(left) + abs(right) + 1e-12))


def seal_identity_strata_v02(
    feature_rows: Iterable[Mapping[str, Any]], registry: AnchorRegistry
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Seal both direction-value and cross-site site-selection estimands."""
    sealed: list[dict[str, Any]] = []
    candidate_ids: set[str] = set()
    for raw in feature_rows:
        missing = [field for field in V02_REQUIRED_FEATURE_FIELDS if field not in raw]
        if missing:
            raise ValueError(f"v0.2 feature row missing fields: {missing}")
        candidate_id = _canonical_id(raw["candidate_id"], "candidate_id")
        pair_id = _canonical_id(raw["pair_id"], "pair_id")
        if candidate_id in candidate_ids:
            raise ValueError(f"duplicate candidate_id: {candidate_id}")
        candidate_ids.add(candidate_id)
        arm = str(raw["arm"])
        contrast = str(raw["contrast_type"])
        if arm not in ARMS:
            raise ValueError(f"invalid arm: {arm}")
        if contrast not in CONTRAST_TYPES:
            raise ValueError(f"invalid contrast_type: {contrast}")
        site_id = _canonical_id(raw["site_id"], "site_id")
        certificate = registry.certify(site_id, requested_use="disparate_weight_edit")
        row = {field: raw[field] for field in V02_REQUIRED_FEATURE_FIELDS}
        row.update(
            {
                "candidate_id": candidate_id,
                "pair_id": pair_id,
                "site_id": site_id,
                "run_replicate": _canonical_id(raw["run_replicate"], "run_replicate"),
                "prompt_group": _canonical_id(raw["prompt_group"], "prompt_group"),
                "family": _canonical_id(raw["family"], "family"),
                "norm": _finite_nonnegative(raw["norm"], "norm"),
                "rank": _positive_integer(raw["rank"], "rank"),
                "layer_index": _positive_integer(raw["layer_index"], "layer_index", allow_zero=True),
                "component_type": _canonical_id(raw["component_type"], "component_type"),
                "direction_policy": _canonical_id(raw["direction_policy"], "direction_policy"),
                "jacobian_visibility": _finite_nonnegative(raw["jacobian_visibility"], "jacobian_visibility"),
                "baseline_activation_rms": _finite_nonnegative(
                    raw["baseline_activation_rms"], "baseline_activation_rms"
                ),
                "identity_stratum": certificate.certification_level,
                "identity_certificate_sha256": certificate.record_sha256,
                "signed_intervention_authorized": certificate.authorized,
                "lineage_margin": certificate.margins["mean_edge_chordal_lineage"],
                "holonomy_angle_margin_degrees": certificate.margins["holonomy_angle_degrees"],
                "det_h_flag": certificate.margins["det_h_orientation"] < 0,
            }
        )
        sealed.append(row)

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in sealed:
        grouped.setdefault(row["pair_id"], []).append(row)
    exact_common = (
        "contrast_type",
        "run_replicate",
        "prompt_group",
        "family",
        "norm",
        "rank",
        "layer_index",
        "component_type",
        "identity_stratum",
    )
    support_rows: list[dict[str, Any]] = []
    for pair_id, rows in grouped.items():
        if len(rows) == 1 and rows[0]["contrast_type"] == "site_selection":
            rows[0]["matched_support"] = False
            rows[0]["support_failures"] = ["missing_matched_arm"]
            support_rows.append(
                {
                    "pair_id": pair_id,
                    "contrast_type": "site_selection",
                    "matched_support": False,
                    "support_failures": ["missing_matched_arm"],
                    "jacobian_relative_distance": None,
                    "activation_rms_relative_distance": None,
                }
            )
            continue
        if len(rows) != 2 or {row["arm"] for row in rows} != ARMS:
            raise ValueError(f"pair {pair_id} must contain exactly one intervention and one matched_random")
        intervention = next(row for row in rows if row["arm"] == "intervention")
        matched = next(row for row in rows if row["arm"] == "matched_random")
        for field in exact_common:
            if intervention[field] != matched[field]:
                raise ValueError(f"pair {pair_id} is not matched on {field}")
        contrast = intervention["contrast_type"]
        if contrast == "direction_value":
            if intervention["site_id"] != matched["site_id"]:
                raise ValueError(f"direction pair {pair_id} must use the same site_id")
            if intervention["direction_policy"] != "attribution_selected":
                raise ValueError(f"direction pair {pair_id} intervention must use attribution_selected")
            if matched["direction_policy"] != "matched_random":
                raise ValueError(f"direction pair {pair_id} control must use matched_random")
            jacobian_distance = _relative_distance(
                intervention["jacobian_visibility"], matched["jacobian_visibility"]
            )
            activation_distance = _relative_distance(
                intervention["baseline_activation_rms"], matched["baseline_activation_rms"]
            )
        else:
            if intervention["site_id"] == matched["site_id"]:
                raise ValueError(f"site-selection pair {pair_id} must use different site_id values")
            if intervention["direction_policy"] != matched["direction_policy"]:
                raise ValueError(f"site-selection pair {pair_id} must hold direction_policy fixed")
            jacobian_distance = _relative_distance(
                intervention["jacobian_visibility"], matched["jacobian_visibility"]
            )
            activation_distance = _relative_distance(
                intervention["baseline_activation_rms"], matched["baseline_activation_rms"]
            )
        support_failures = []
        if contrast == "site_selection":
            if jacobian_distance > RELATIVE_CALIPER:
                support_failures.append("jacobian_visibility_outside_caliper")
            if activation_distance > RELATIVE_CALIPER:
                support_failures.append("baseline_activation_rms_outside_caliper")
        matched_support = not support_failures
        for row in rows:
            row["matched_support"] = matched_support
            row["support_failures"] = list(support_failures)
        support_rows.append(
            {
                "pair_id": pair_id,
                "contrast_type": contrast,
                "matched_support": matched_support,
                "support_failures": support_failures,
                "jacobian_relative_distance": jacobian_distance,
                "activation_rms_relative_distance": activation_distance,
            }
        )

    sealed.sort(key=lambda row: row["candidate_id"])
    payload = b"".join(_canonical_line(row) for row in sealed)
    contrast_counts = {
        contrast: sum(rows[0]["contrast_type"] == contrast for rows in grouped.values())
        for contrast in sorted(CONTRAST_TYPES)
    }
    eligible_counts = {
        contrast: sum(
            rows[0]["contrast_type"] == contrast
            and len(rows) == 2
            and all(row.get("matched_support", False) for row in rows)
            for rows in grouped.values()
        )
        for contrast in sorted(CONTRAST_TYPES)
    }
    manifest = {
        "schema_version": "0.2.0",
        "named_consumer": "vpd_edit_program",
        "row_count": len(sealed),
        "pair_count": len(grouped),
        "contrast_pair_counts": contrast_counts,
        "eligible_contrast_pair_counts": eligible_counts,
        "outside_support_pair_count": sum(not row["matched_support"] for row in support_rows),
        "candidate_ids_sha256": sha256(
            "\n".join(row["candidate_id"] for row in sealed).encode()
        ).hexdigest(),
        "sealed_feature_sha256": sha256(payload).hexdigest(),
        "anchor_registry_sha256": registry.sha256,
        "outcomes_present": False,
        "relative_caliper": RELATIVE_CALIPER,
        "support_diagnostics": sorted(support_rows, key=lambda row: row["pair_id"]),
        "stratum_counts": {
            contrast: {
                level: sum(
                    row["contrast_type"] == contrast and row["identity_stratum"] == level
                    for row in sealed
                )
                for level in sorted(LEVEL_ORDER, key=LEVEL_ORDER.get)
            }
            for contrast in sorted(CONTRAST_TYPES)
        },
    }
    return sealed, manifest


def analyze_stratified_outcomes_v02(
    sealed_rows: Iterable[Mapping[str, Any]],
    outcomes: Iterable[Mapping[str, Any]],
    registration: Mapping[str, Any],
) -> dict[str, Any]:
    sealed = [dict(row) for row in sealed_rows]
    sealed_payload = b"".join(
        _canonical_line(row) for row in sorted(sealed, key=lambda row: row["candidate_id"])
    )
    if sha256(sealed_payload).hexdigest() != registration["sealed_feature_sha256"]:
        raise ValueError("sealed feature hash mismatch")

    by_id: dict[str, dict[str, Any]] = {}
    for raw in outcomes:
        missing = [field for field in REQUIRED_OUTCOME_FIELDS if field not in raw]
        if missing:
            raise ValueError(f"outcome row missing fields: {missing}")
        candidate_id = _canonical_id(raw["candidate_id"], "candidate_id")
        if candidate_id in by_id:
            raise ValueError(f"duplicate outcome candidate_id: {candidate_id}")
        accepted = int(raw["accepted"]) if isinstance(raw["accepted"], (bool, int, np.integer)) else raw["accepted"]
        if accepted not in (0, 1):
            raise ValueError(f"accepted must be 0/1 for {candidate_id}")
        repair_auc = float(raw["repair_auc"])
        initial_decay = float(raw["initial_decay"])
        if not np.isfinite([repair_auc, initial_decay]).all():
            raise ValueError(f"nonfinite outcomes for {candidate_id}")
        by_id[candidate_id] = {
            "accepted": int(accepted),
            "repair_auc": repair_auc,
            "initial_decay": initial_decay,
        }
    feature_ids = {row["candidate_id"] for row in sealed}
    if set(by_id) != feature_ids:
        raise ValueError(
            "outcome ID universe mismatch; "
            f"missing={sorted(feature_ids - set(by_id))}, extra={sorted(set(by_id) - feature_ids)}"
        )

    pairs: dict[str, dict[str, dict[str, Any]]] = {}
    for row in sealed:
        pairs.setdefault(row["pair_id"], {})[row["arm"]] = {**row, **by_id[row["candidate_id"]]}
    nested: dict[str, dict[str, list[dict[str, Any]]]] = {}
    outside_support: list[dict[str, Any]] = []
    for pair_id, arms in pairs.items():
        members = list(arms.values())
        if members and not all(row.get("matched_support", False) for row in members):
            outside_support.append(
                {
                    "pair_id": pair_id,
                    "contrast_type": members[0]["contrast_type"],
                    "site_ids": sorted({row["site_id"] for row in members}),
                    "support_failures": sorted(
                        {failure for row in members for failure in row.get("support_failures", [])}
                    ),
                }
            )
            continue
        if set(arms) != ARMS:
            raise ValueError(f"broken sealed pair: {pair_id}")
        intervention, matched = arms["intervention"], arms["matched_random"]
        contrast = intervention["contrast_type"]
        stratum = intervention["identity_stratum"]
        nested.setdefault(contrast, {}).setdefault(stratum, []).append(
            {
                "pair_id": pair_id,
                "run_replicate": intervention["run_replicate"],
                "accepted": intervention["accepted"] - matched["accepted"],
                "repair_auc": intervention["repair_auc"] - matched["repair_auc"],
                "initial_decay": intervention["initial_decay"] - matched["initial_decay"],
            }
        )

    contrasts: dict[str, Any] = {}
    for contrast in sorted(CONTRAST_TYPES):
        strata = nested.get(contrast, {})
        contrasts[contrast] = {
            "estimand": (
                "attribution_direction_minus_random_direction_same_site"
                if contrast == "direction_value"
                else "attribution_selected_site_minus_matched_random_site_direction_policy_fixed"
            ),
            "strata": {
                stratum: {
                    "pair_count": len(rows),
                    "accepted": _outcome_summary(rows, "accepted"),
                    "repair_auc": _outcome_summary(rows, "repair_auc"),
                    "initial_decay": _outcome_summary(rows, "initial_decay"),
                }
                for stratum, rows in sorted(strata.items(), key=lambda item: LEVEL_ORDER[item[0]])
            },
            "empty_strata": [
                level for level in sorted(LEVEL_ORDER, key=LEVEL_ORDER.get) if level not in strata
            ],
        }
    outcome_payload = b"".join(
        _canonical_line({"candidate_id": key, **by_id[key]}) for key in sorted(by_id)
    )
    return {
        "schema_version": "0.2.0",
        "named_consumer": "vpd_edit_program",
        "analysis_scope": "separate_contrasts_within_identity_stratum_only",
        "pooled_across_contrasts": "prohibited",
        "pooled_across_identity_strata": "prohibited",
        "outside_matched_support": sorted(outside_support, key=lambda row: row["pair_id"]),
        "sealed_feature_sha256": registration["sealed_feature_sha256"],
        "outcome_sha256": sha256(outcome_payload).hexdigest(),
        "contrasts": contrasts,
    }


def _outcome_summary(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    differences = np.array([float(row[field]) for row in rows], dtype=np.float64)
    clusters: dict[str, list[float]] = {}
    for row, value in zip(rows, differences):
        clusters.setdefault(str(row["run_replicate"]), []).append(float(value))
    cluster_means = np.array([np.mean(clusters[key]) for key in sorted(clusters)], dtype=np.float64)
    return {
        "mean_paired_difference": float(np.mean(differences)),
        "wins": int(np.sum(differences > 0)),
        "losses": int(np.sum(differences < 0)),
        "ties": int(np.sum(differences == 0)),
        "run_replicate_count": len(cluster_means),
        "cluster_sign_flip_p_two_sided": _sign_flip_p(cluster_means),
    }


def _sign_flip_p(values: np.ndarray, seed: int = 20260712, draws: int = 65536) -> float:
    values = np.asarray(values, dtype=np.float64)
    if not len(values) or np.all(values == 0):
        return 1.0
    observed = abs(float(np.mean(values)))
    if len(values) <= 18:
        signs = itertools.product((-1.0, 1.0), repeat=len(values))
        simulated = [abs(float(np.mean(values * np.fromiter(item, dtype=np.float64)))) for item in signs]
    else:
        rng = np.random.default_rng(seed)
        signs = rng.choice((-1.0, 1.0), size=(draws, len(values)))
        simulated = np.abs(np.mean(signs * values[None, :], axis=1))
    simulated_array = np.asarray(simulated)
    return float((1 + np.sum(simulated_array >= observed - 1e-15)) / (1 + len(simulated_array)))


def _write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite different sealed artifact: {path}")
        return
    path.write_bytes(payload)
