"""Held-out control-gating analysis for the Qwen four-choice action probe."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import analyze_asmp8_qwen08_control_gate as prior  # noqa: E402


BASE_FEATURES = prior.BASE_FEATURES
PROBE_FEATURES = (
    "probe_probability_A",
    "probe_probability_B",
    "probe_probability_C",
    "probe_probability_D",
    "probe_probability_maximum",
    "probe_probability_margin",
    "probe_proxy_action_probability",
    "probe_normalized_entropy",
    "probe_proxy_disagreement",
)


def joined_rows(
    features: Sequence[dict[str, Any]], outcomes: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    feature_map = {str(row["row_id"]): row for row in features}
    outcome_map = {str(row["row_id"]): row for row in outcomes}
    if len(feature_map) != len(features) or len(outcome_map) != len(outcomes):
        raise ValueError("duplicate row IDs are forbidden")
    if set(feature_map) != set(outcome_map):
        raise ValueError("feature/outcome row-ID equality failed")
    output = []
    for row_id in sorted(feature_map):
        feature = feature_map[row_id]
        outcome = outcome_map[row_id]
        if feature["proxy_selected_action"] != outcome["proxy_selected_action"]:
            raise ValueError("proxy action differs across feature and outcome tables")
        if feature["probe_selected_action"] != outcome["probe_selected_action"]:
            raise ValueError("probe action differs across feature and outcome tables")
        output.append({**feature, **outcome})
    return output


def _design(
    rows: Sequence[Mapping[str, Any]],
    applications: Sequence[str],
    names: Sequence[str],
    means: np.ndarray,
    scales: np.ndarray,
) -> np.ndarray:
    values = np.asarray(
        [[float(row[name]) for name in names] for row in rows], dtype=np.float64
    )
    values = (values - means) / scales
    categories = np.zeros((len(rows), max(0, len(applications) - 1)), dtype=np.float64)
    app_index = {name: index for index, name in enumerate(applications)}
    for row_index, row in enumerate(rows):
        index = app_index[str(row["application"])]
        if index:
            categories[row_index, index - 1] = 1.0
    return np.column_stack((categories, values))


def fit_scores(
    construction: Sequence[dict[str, Any]],
    validation: Sequence[dict[str, Any]],
    *,
    probe_override: Mapping[str, Mapping[str, float]] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    applications = sorted({str(row["application"]) for row in construction + validation})
    baseline_names = list(BASE_FEATURES)
    augmented_names = baseline_names + list(PROBE_FEATURES)
    augmented_construction = [dict(row) for row in construction]
    augmented_validation = [dict(row) for row in validation]
    if probe_override is not None:
        for row in augmented_construction + augmented_validation:
            override = probe_override[str(row["row_id"])]
            for name in PROBE_FEATURES:
                row[name] = float(override[name])

    baseline_values = np.asarray(
        [[float(row[name]) for name in baseline_names] for row in construction]
    )
    augmented_values = np.asarray(
        [[float(row[name]) for name in augmented_names] for row in augmented_construction]
    )
    baseline_means = baseline_values.mean(axis=0)
    baseline_scales = baseline_values.std(axis=0)
    baseline_scales[baseline_scales == 0] = 1.0
    augmented_means = augmented_values.mean(axis=0)
    augmented_scales = augmented_values.std(axis=0)
    augmented_scales[augmented_scales == 0] = 1.0
    y = np.asarray([not bool(row["proxy_correct"]) for row in construction], dtype=int)
    if len(np.unique(y)) != 2:
        raise ValueError("construction outcomes require both classes")

    baseline = LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000, random_state=0)
    augmented = LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000, random_state=0)
    baseline.fit(
        _design(
            construction,
            applications,
            baseline_names,
            baseline_means,
            baseline_scales,
        ),
        y,
    )
    augmented.fit(
        _design(
            augmented_construction,
            applications,
            augmented_names,
            augmented_means,
            augmented_scales,
        ),
        y,
    )
    return (
        baseline.predict_proba(
            _design(
                validation,
                applications,
                baseline_names,
                baseline_means,
                baseline_scales,
            )
        )[:, 1],
        augmented.predict_proba(
            _design(
                augmented_validation,
                applications,
                augmented_names,
                augmented_means,
                augmented_scales,
            )
        )[:, 1],
    )


def permuted_probe_block(
    rows: Sequence[dict[str, Any]], rng: np.random.Generator
) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    strata = sorted(
        {(str(row["application"]), str(row["geometry_half"])) for row in rows}
    )
    for application, half in strata:
        selected = [
            row
            for row in rows
            if row["application"] == application and row["geometry_half"] == half
        ]
        permutation = rng.permutation(len(selected))
        for target, source_index in zip(selected, permutation, strict=True):
            source = selected[int(source_index)]
            output[str(target["row_id"])] = {
                name: float(source[name]) for name in PROBE_FEATURES
            }
    return output


def analyze(
    rows: Sequence[dict[str, Any]],
    *,
    permutation_replicates: int,
    permutation_seed: int,
    bootstrap_iterations: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    construction = [row for row in rows if row["geometry_half"] == "construction"]
    validation = [row for row in rows if row["geometry_half"] == "validation"]
    if len(construction) + len(validation) != len(rows):
        raise ValueError("unexpected geometry half")
    validation_y = np.asarray(
        [not bool(row["proxy_correct"]) for row in validation], dtype=int
    )
    if len(np.unique(validation_y)) != 2:
        raise ValueError("validation outcomes require both classes")

    baseline_scores, augmented_scores = fit_scores(construction, validation)
    app_metrics = prior.per_application_metrics(
        validation, baseline_scores, augmented_scores
    )
    observed = prior.balanced_improvement(app_metrics)
    app_values = [
        app_metrics[name]["selective_risk_auc_improvement"]
        for name in sorted(app_metrics)
    ]
    lower, upper = prior.bootstrap_interval(
        app_values, iterations=bootstrap_iterations, seed=bootstrap_seed
    )
    rng = np.random.default_rng(permutation_seed)
    null_values = []
    for _ in range(permutation_replicates):
        override = permuted_probe_block(rows, rng)
        perm_base, perm_augmented = fit_scores(
            construction, validation, probe_override=override
        )
        null_values.append(
            prior.balanced_improvement(
                prior.per_application_metrics(validation, perm_base, perm_augmented)
            )
        )
    p_value = (1 + sum(value >= observed for value in null_values)) / (
        permutation_replicates + 1
    )

    proxy_correct = np.asarray(
        [bool(row["proxy_correct"]) for row in validation], dtype=bool
    )
    probe_correct = np.asarray(
        [bool(row["probe_correct"]) for row in validation], dtype=bool
    )
    gate_pass = observed > 0 and lower > 0 and p_value <= 0.05
    result = {
        "schema_version": "asmp8_qwen08_action_probe_analysis_v0_1",
        "row_count": len(rows),
        "construction_count": len(construction),
        "validation_count": len(validation),
        "validation_proxy_failure_rate": float(validation_y.mean()),
        "application_metrics": app_metrics,
        "primary": {
            "metric": "application_balanced_selective_risk_auc_improvement",
            "observed": observed,
            "bootstrap_95": [lower, upper],
            "permutation_p_one_sided": p_value,
            "permutation_replicates": permutation_replicates,
        },
        "secondary_prediction": {
            "baseline_log_loss": float(log_loss(validation_y, baseline_scores)),
            "augmented_log_loss": float(log_loss(validation_y, augmented_scores)),
            "log_loss_improvement": float(
                log_loss(validation_y, baseline_scores)
                - log_loss(validation_y, augmented_scores)
            ),
            "baseline_average_precision": float(
                average_precision_score(validation_y, baseline_scores)
            ),
            "augmented_average_precision": float(
                average_precision_score(validation_y, augmented_scores)
            ),
            "baseline_roc_auc": float(roc_auc_score(validation_y, baseline_scores)),
            "augmented_roc_auc": float(roc_auc_score(validation_y, augmented_scores)),
        },
        "secondary_action": {
            "proxy_accuracy": float(proxy_correct.mean()),
            "probe_accuracy": float(probe_correct.mean()),
            "probe_correct_proxy_wrong_rate": float(
                np.mean(probe_correct & ~proxy_correct)
            ),
            "probe_wrong_proxy_correct_rate": float(
                np.mean(~probe_correct & proxy_correct)
            ),
            "proxy_mean_regret": float(
                np.mean([float(row["proxy_regret"]) for row in validation])
            ),
            "probe_mean_regret": float(
                np.mean([float(row["probe_regret"]) for row in validation])
            ),
            "probe_proxy_disagreement_rate": float(
                np.mean(
                    [
                        row["probe_selected_action"] != row["proxy_selected_action"]
                        for row in validation
                    ]
                )
            ),
        },
        "gates": {
            "J0_exact_join_and_outcome_support": "pass",
            "G0_heldout_selective_risk_increment": "pass" if gate_pass else "fail",
        },
        "status": (
            "qwen_action_probe_control_gate_established"
            if gate_pass
            else "qwen_action_probe_control_gate_not_established"
        ),
        "claim_boundary": (
            "Held-out synthetic controller-task result for one constrained Qwen0.8B "
            "action distribution. No causal, deployment, scalable-oversight, "
            "Goodhart-frontier, recursive-improvement, or ASMP-8 conclusion follows."
        ),
    }
    return result


def render_report(result: Mapping[str, Any]) -> str:
    primary = result["primary"]
    action = result["secondary_action"]
    prediction = result["secondary_prediction"]
    lines = [
        "# ASMP-8 Qwen0.8B action-probe result v0.1",
        "",
        f"Status: `{result['status']}`",
        "",
        f"- Rows: {result['row_count']}",
        (
            "- Application-balanced selective-risk AUC improvement: "
            f"{primary['observed']:.8f}"
        ),
        (
            "- Application-cluster bootstrap 95% interval: "
            f"[{primary['bootstrap_95'][0]:.8f}, {primary['bootstrap_95'][1]:.8f}]"
        ),
        f"- One-sided matched-block permutation p: {primary['permutation_p_one_sided']:.8f}",
        f"- Log-loss improvement: {prediction['log_loss_improvement']:.8f}",
        f"- Proxy action accuracy: {action['proxy_accuracy']:.6f}",
        f"- Probe action accuracy: {action['probe_accuracy']:.6f}",
        f"- Proxy mean regret: {action['proxy_mean_regret']:.6f}",
        f"- Probe mean regret: {action['probe_mean_regret']:.6f}",
        f"- Probe/proxy disagreement rate: {action['probe_proxy_disagreement_rate']:.6f}",
        "",
        "## Per-application selective-risk improvement",
        "",
        "| Application | Improvement |",
        "|---|---:|",
    ]
    for name, row in sorted(result["application_metrics"].items()):
        lines.append(f"| {name} | {row['selective_risk_auc_improvement']:.8f} |")
    lines.extend(["", "## Claim boundary", "", str(result["claim_boundary"]), ""])
    return "\n".join(lines)


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--outcomes", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-report", type=Path, required=True)
    parser.add_argument("--permutation-replicates", type=int, default=2048)
    parser.add_argument("--permutation-seed", type=int, default=81720260725)
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=81820260725)
    args = parser.parse_args()

    rows = joined_rows(prior.load_jsonl(args.features), prior.load_jsonl(args.outcomes))
    result = analyze(
        rows,
        permutation_replicates=args.permutation_replicates,
        permutation_seed=args.permutation_seed,
        bootstrap_iterations=args.bootstrap_iterations,
        bootstrap_seed=args.bootstrap_seed,
    )
    result["inputs"] = {
        "features_sha256": prior.sha256_path(args.features),
        "outcomes_sha256": prior.sha256_path(args.outcomes),
    }
    write_once(
        args.output_json,
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    write_once(args.output_report, render_report(result).encode("utf-8"))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
