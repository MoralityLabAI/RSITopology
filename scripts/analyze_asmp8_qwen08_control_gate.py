"""Held-out selective-risk test for the ASMP-8 Qwen confidence feature."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score


BASE_FEATURES = (
    "score_maximum",
    "score_second",
    "score_margin",
    "score_mean",
    "score_sd",
    "score_range",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def joined_rows(
    features: Sequence[dict[str, Any]], outcomes: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    feature_map = {str(row["row_id"]): row for row in features}
    outcome_map = {str(row["row_id"]): row for row in outcomes}
    if len(feature_map) != len(features) or len(outcome_map) != len(outcomes):
        raise ValueError("duplicate row IDs are forbidden")
    if set(feature_map) != set(outcome_map):
        raise ValueError("feature/outcome candidate ID equality failed")
    output = []
    for row_id in sorted(feature_map):
        if (
            feature_map[row_id]["proxy_selected_action"]
            != outcome_map[row_id]["proxy_selected_action"]
        ):
            raise ValueError("proxy action differs across feature and outcome tables")
        output.append({**feature_map[row_id], **outcome_map[row_id]})
    return output


def _design(
    rows: Sequence[dict[str, Any]],
    applications: Sequence[str],
    means: np.ndarray,
    scales: np.ndarray,
    *,
    include_qwen: bool,
) -> np.ndarray:
    continuous_names = list(BASE_FEATURES)
    if include_qwen:
        continuous_names.append("qwen_top_token_probability")
    values = np.asarray(
        [[float(row[name]) for name in continuous_names] for row in rows],
        dtype=np.float64,
    )
    values = (values - means[: values.shape[1]]) / scales[: values.shape[1]]
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
    qwen_override: dict[str, float] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    applications = sorted({str(row["application"]) for row in construction + validation})
    all_names = list(BASE_FEATURES) + ["qwen_top_token_probability"]
    construction_values = np.asarray(
        [[float(row[name]) for name in all_names] for row in construction],
        dtype=np.float64,
    )
    means = construction_values.mean(axis=0)
    scales = construction_values.std(axis=0)
    scales[scales == 0] = 1.0

    augmented_construction = [dict(row) for row in construction]
    augmented_validation = [dict(row) for row in validation]
    if qwen_override is not None:
        for row in augmented_construction + augmented_validation:
            row["qwen_top_token_probability"] = qwen_override[str(row["row_id"])]

    y = np.asarray([not bool(row["proxy_correct"]) for row in construction], dtype=int)
    if len(np.unique(y)) != 2:
        raise ValueError("construction outcomes require both classes")
    baseline = LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000, random_state=0)
    augmented = LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000, random_state=0)
    baseline.fit(
        _design(construction, applications, means, scales, include_qwen=False), y
    )
    augmented.fit(
        _design(
            augmented_construction,
            applications,
            means,
            scales,
            include_qwen=True,
        ),
        y,
    )
    return (
        baseline.predict_proba(
            _design(validation, applications, means, scales, include_qwen=False)
        )[:, 1],
        augmented.predict_proba(
            _design(
                augmented_validation,
                applications,
                means,
                scales,
                include_qwen=True,
            )
        )[:, 1],
    )


def selective_risk_auc(
    rows: Sequence[dict[str, Any]], scores: Sequence[float]
) -> float:
    if len(rows) != len(scores) or not rows:
        raise ValueError("rows and scores must be nonempty and aligned")
    ordered = sorted(
        zip(rows, scores, strict=True),
        key=lambda item: (-float(item[1]), str(item[0]["row_id"])),
    )
    regrets = np.asarray([float(row["proxy_regret"]) for row, _ in ordered])
    retained_sum = float(regrets.sum())
    risks = []
    for deferred in range(len(regrets)):
        retained_count = len(regrets) - deferred
        risks.append(retained_sum / retained_count)
        retained_sum -= float(regrets[deferred])
    return float(np.mean(risks))


def per_application_metrics(
    rows: Sequence[dict[str, Any]],
    baseline_scores: Sequence[float],
    augmented_scores: Sequence[float],
) -> dict[str, dict[str, float]]:
    output = {}
    applications = sorted({str(row["application"]) for row in rows})
    for application in applications:
        indices = [
            index for index, row in enumerate(rows) if row["application"] == application
        ]
        app_rows = [rows[index] for index in indices]
        baseline_auc = selective_risk_auc(
            app_rows, [baseline_scores[index] for index in indices]
        )
        augmented_auc = selective_risk_auc(
            app_rows, [augmented_scores[index] for index in indices]
        )
        output[application] = {
            "n": float(len(indices)),
            "baseline_selective_risk_auc": baseline_auc,
            "augmented_selective_risk_auc": augmented_auc,
            "selective_risk_auc_improvement": baseline_auc - augmented_auc,
        }
    return output


def balanced_improvement(metrics: dict[str, dict[str, float]]) -> float:
    return float(
        np.mean([row["selective_risk_auc_improvement"] for row in metrics.values()])
    )


def bootstrap_interval(
    values: Sequence[float], *, iterations: int, seed: int
) -> tuple[float, float]:
    array = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    sampled = array[rng.integers(0, len(array), size=(iterations, len(array)))].mean(
        axis=1
    )
    return float(np.quantile(sampled, 0.025)), float(np.quantile(sampled, 0.975))


def _permuted_qwen(
    rows: Sequence[dict[str, Any]], rng: np.random.Generator
) -> dict[str, float]:
    output: dict[str, float] = {}
    strata = sorted(
        {(str(row["application"]), str(row["geometry_half"])) for row in rows}
    )
    for application, half in strata:
        selected = [
            row
            for row in rows
            if row["application"] == application and row["geometry_half"] == half
        ]
        values = np.asarray(
            [float(row["qwen_top_token_probability"]) for row in selected]
        )
        values = values[rng.permutation(len(values))]
        for row, value in zip(selected, values, strict=True):
            output[str(row["row_id"])] = float(value)
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
    app_metrics = per_application_metrics(validation, baseline_scores, augmented_scores)
    observed = balanced_improvement(app_metrics)
    app_values = [
        app_metrics[name]["selective_risk_auc_improvement"]
        for name in sorted(app_metrics)
    ]
    lower, upper = bootstrap_interval(
        app_values, iterations=bootstrap_iterations, seed=bootstrap_seed
    )

    rng = np.random.default_rng(permutation_seed)
    null_values = []
    for _ in range(permutation_replicates):
        override = _permuted_qwen(rows, rng)
        perm_base, perm_augmented = fit_scores(
            construction, validation, qwen_override=override
        )
        null_values.append(
            balanced_improvement(
                per_application_metrics(validation, perm_base, perm_augmented)
            )
        )
    p_value = (1 + sum(value >= observed for value in null_values)) / (
        permutation_replicates + 1
    )

    baseline_log_loss = float(log_loss(validation_y, baseline_scores))
    augmented_log_loss = float(log_loss(validation_y, augmented_scores))
    result = {
        "schema_version": "asmp8_qwen08_control_gate_analysis_v0_1",
        "row_count": len(rows),
        "construction_count": len(construction),
        "validation_count": len(validation),
        "validation_proxy_failure_rate": float(validation_y.mean()),
        "validation_mean_regret": float(
            np.mean([float(row["proxy_regret"]) for row in validation])
        ),
        "application_metrics": app_metrics,
        "primary": {
            "metric": "application_balanced_selective_risk_auc_improvement",
            "observed": observed,
            "bootstrap_95": [lower, upper],
            "permutation_p_one_sided": p_value,
            "permutation_replicates": permutation_replicates,
        },
        "secondary": {
            "baseline_log_loss": baseline_log_loss,
            "augmented_log_loss": augmented_log_loss,
            "log_loss_improvement": baseline_log_loss - augmented_log_loss,
            "baseline_average_precision": float(
                average_precision_score(validation_y, baseline_scores)
            ),
            "augmented_average_precision": float(
                average_precision_score(validation_y, augmented_scores)
            ),
            "baseline_roc_auc": float(roc_auc_score(validation_y, baseline_scores)),
            "augmented_roc_auc": float(roc_auc_score(validation_y, augmented_scores)),
        },
    }
    gate_pass = observed > 0 and lower > 0 and p_value <= 0.05
    result["gates"] = {
        "J0_exact_join_and_outcome_support": "pass",
        "G0_heldout_selective_risk_increment": "pass" if gate_pass else "fail",
    }
    result["status"] = (
        "qwen_confidence_control_gate_established"
        if gate_pass
        else "qwen_confidence_control_gate_not_established"
    )
    result["claim_boundary"] = (
        "Held-out synthetic controller-task selective-risk prediction for one "
        "Qwen0.8B first-token probability. No causal, deployment, scalable-oversight, "
        "Goodhart-frontier, or recursive-improvement conclusion follows."
    )
    return result


def render_report(result: dict[str, Any]) -> str:
    primary = result["primary"]
    secondary = result["secondary"]
    lines = [
        "# ASMP-8 Qwen0.8B control-gating result v0.1",
        "",
        f"Status: `{result['status']}`",
        "",
        f"- Rows: {result['row_count']}",
        f"- Validation proxy-failure rate: {result['validation_proxy_failure_rate']:.6f}",
        f"- Validation mean regret: {result['validation_mean_regret']:.6f}",
        (
            "- Application-balanced selective-risk AUC improvement: "
            f"{primary['observed']:.8f}"
        ),
        (
            "- Application-cluster bootstrap 95% interval: "
            f"[{primary['bootstrap_95'][0]:.8f}, {primary['bootstrap_95'][1]:.8f}]"
        ),
        f"- One-sided within-stratum permutation p: {primary['permutation_p_one_sided']:.8f}",
        f"- Log-loss improvement: {secondary['log_loss_improvement']:.8f}",
        "",
        "## Per-application selective-risk improvement",
        "",
        "| Application | Improvement |",
        "|---|---:|",
    ]
    for name, row in sorted(result["application_metrics"].items()):
        lines.append(f"| {name} | {row['selective_risk_auc_improvement']:.8f} |")
    lines.extend(["", "## Claim boundary", "", result["claim_boundary"], ""])
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
    parser.add_argument("--permutation-seed", type=int, default=80720260725)
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=80820260725)
    args = parser.parse_args()

    rows = joined_rows(load_jsonl(args.features), load_jsonl(args.outcomes))
    result = analyze(
        rows,
        permutation_replicates=args.permutation_replicates,
        permutation_seed=args.permutation_seed,
        bootstrap_iterations=args.bootstrap_iterations,
        bootstrap_seed=args.bootstrap_seed,
    )
    result["inputs"] = {
        "features_sha256": sha256_path(args.features),
        "outcomes_sha256": sha256_path(args.outcomes),
    }
    json_payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    report_payload = render_report(result).encode()
    write_once(args.output_json, json_payload)
    write_once(args.output_report, report_payload)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
