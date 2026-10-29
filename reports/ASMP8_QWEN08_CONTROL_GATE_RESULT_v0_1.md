# ASMP-8 Qwen0.8B control-gating result v0.1

Status: `qwen_confidence_control_gate_not_established`

## Result

The stable Qwen first-token probability did not improve held-out control-risk
ranking over application identity and visible proposer-score summaries.

| Quantity | Result |
|---|---:|
| Rows | 576 |
| Construction / validation | 288 / 288 |
| Validation proxy-failure rate | 24.65% |
| Validation mean regret | 0.13257 |
| Application-balanced selective-risk AUC improvement | -0.00031074 |
| Application-bootstrap 95% interval | [-0.00087434, 0.00009901] |
| Within-stratum permutation p, one-sided | 0.94143 |
| Log-loss improvement | -0.00027228 |
| Average precision, baseline / augmented | 0.76810 / 0.76617 |
| ROC-AUC, baseline / augmented | 0.93568 / 0.93458 |

The exact feature/outcome join and outcome-support gate passed. The registered
predictive gate failed. The observed primary improvement was negative, its
interval crossed zero, and 94.1% of the one-sided matched-null ordering was at
least as favorable.

Across the nine applications, the Qwen feature improved selective-risk AUC in
one, worsened it in three, and tied it in five. The only positive
per-application change was small (`secret_route`, +0.00045139).

## Interpretation

The Prime measurement pass established that the statistic was live and
perfectly reproducible across cache order, exact repeats, and server restarts.
This follow-up shows why measurement reliability and decision relevance must
be separate gates: the reliable statistic was not useful for risk-based
deferral.

The prompt explicitly asked Qwen to represent a controller state without
choosing an action, and the measured token was the initial formatting token.
The negative result therefore rejects this cheap completion-probability
feature, not model confidence as a general object. A successor would need to
change the measurement object prospectively—for example, a task-conditioned
action probe, sequence-level likelihood ratio, or target-blind hidden-state
feature—rather than retune this analysis.

## Integrity

- Preregistration commit:
  `1d12733f90aa831dbeb23c9b9981489ddd2c2ad4`
- Sealed feature SHA-256:
  `0a26ec884c72c758d0cdf82f2792cd1266b370f1b383bc66418f88d9c8aa058b`
- Outcome SHA-256:
  `98c4838d5deee0862f75080ffcccc9090884ed93b25cbb8c110da5e009c336a6`
- Analysis SHA-256:
  `bad070ff9474cb4ab3f7195fc9ed97b7ef003f475715178733170f8396ac01c5`
- Frozen analysis and report replayed byte-identically.
- Focused suite: 18 passed.

## Claim boundary

This is a held-out synthetic controller-task result for one Qwen0.8B
first-formatting-token probability. It does not establish causality,
deployment safety, scalable-oversight sufficiency, a Goodhart phase frontier,
recursive-improvement risk, or ASMP-8 resolution.
