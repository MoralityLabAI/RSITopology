# ASMP-7 finite attestation-frontier result v0.1

## Verdict

`exact_finite_trace_impossibility_and_charged_audit_frontier_established`

All eight prospectively frozen gates passed. In the registered finite class,
trace-only telemetry cannot uniformly distinguish compliant from forbidden
executions, while three charged semantic-audit channels meet the separate 5%
false-positive and false-negative requirements.

This is an exact finite application of classical testing theory, not a new
hypothesis-testing theorem and not a resolution of ASMP-7.

## Exact transformation census

The run checked every one of the

```text
65,536 truth tables * 48 representation states = 3,145,728 states.
```

All LUT, RLE, algebraic-normal-form, single-device, and two-device XOR-share
representations reconstructed the original truth table and preserved its
policy class. The truth-table census was:

| Class | Frozen definition | Count |
|---|---|---:|
| compliant | agreement with parity target at most 8/16 | 39,203 |
| forbidden | agreement at least 14/16 | 137 |
| outside comparison | agreement 9/16 through 13/16 | 26,196 |

## Trace-only impossibility

For every one of the 48 representation states, the frozen compliant witness
with `k=8` and forbidden witness with `k=14` produced the same deterministic
trace law. Therefore the compliant and forbidden composite law sets intersect.
For any randomized trace-only test `phi`, evaluated on that shared law `Q`,

```text
FP + FN = E_Q[phi] + E_Q[1-phi] = 1.
```

Consequently no trace-only test can satisfy the registered pair
`FP<=1/20, FN<=1/20`. This is a law-level witness, not a claim that all
real compute traces are uninformative.

## Charged-audit frontier

The trusted meter sampled challenges uniformly with replacement and released
fresh randomized-response correctness bits. The sufficient statistic was the
number `K` of reported-correct answers. Direct enumeration of 108 report-string
cases agreed exactly with the registered binomial reduction.

Minimum feasible channels through `m=128` were:

| Truth-report probability `theta` | Minimum `m` | Cutoff `c` | Boundary randomization `gamma` | Worst FP | Worst FN | Status |
|---:|---:|---:|---:|---:|---:|---|
| 1/2 | — | — | — | — | — | infeasible through 128 |
| 3/5 | — | — | — | — | — | infeasible through 128 |
| 2/3 | — | — | — | — | — | infeasible through 128 |
| 3/4 | 73 | 44 | 0.957664 | 0.049469 | 0.049223 | feasible, Pareto |
| 4/5 | 50 | 31 | 0.630573 | 0.049484 | 0.049394 | feasible, Pareto |
| 1 | 15 | 11 | 0.765793 | 0.049478 | 0.049039 | feasible, Pareto |

The exact rational values, including the exact randomized cutoffs, are in
`artifacts_v0_1/result.json`. Every feasible test was rechecked against every
`k<=8` and every `k>=14`; there were zero uniform-composite violations.

All three feasible minimum channels are Pareto-nondominated under the frozen
unscalarized ordering. More truthful reports require fewer challenges but
provide less privacy. The result does not select a deployment point or assert
that this grid is globally Blackwell-minimal.

## Gates

| Gate | Result | Receipt |
|---|---|---|
| T0 finite-orbit integrity | pass | 3,145,728 / 3,145,728 states preserved |
| T1 trace impossibility | pass | 48 shared laws; `FP+FN>=1` |
| P0 sufficient statistic | pass | 108/108 direct-enumeration cases exact |
| A0 privacy kill | pass | `theta=1/2` infeasible for all `m<=128` |
| A1 charged-audit liveness | pass | 3 feasible truth-report levels |
| U0 uniform composite | pass | zero FP/FN violations |
| E0 exhaustive liveness | pass | `theta=1` feasible at `m=15` |
| F0 frontier integrity | pass | 3 nondominated points |

## Interpretation

The finite example separates three propositions that are often blurred:

1. **Evidence integrity:** a signed trace packet can be authentic.
2. **Evidence completeness:** every relevant execution produced a packet.
3. **Semantic sufficiency:** the packet distribution separates compliant from
   forbidden executions uniformly over allowed transformations.

This experiment assumes the second proposition for charged challenges. It
shows that the registered trace experiment fails the third, while an explicitly
semantic and explicitly costly challenge experiment can pass it. Signatures or
hashes would protect either packet from alteration; they would not establish
coverage or sufficiency by themselves.

The practical ASMP-7 lesson is therefore conditional: when a transformation
class destroys the relation between an extensional policy predicate and its
resource proxy, attestation requires a newly charged measurement tied to the
predicate. That measurement's access and coverage assumptions belong in the
certificate rather than being smuggled in as “telemetry.”

## Prior art and claim boundary

Randomized response, monotone-likelihood-ratio binomial testing, comparison of
experiments, and Boolean property testing are classical. The registered
contribution is the finite access-class construction, exact audit frontier,
and replayable ASMP-7 receipt.

The result does **not** establish semantic meter coverage in a deployment,
attestability of a real model, closure under unregistered compression or
decomposition, an optimal channel among all telemetry experiments, or a
solution to ASMP-7. It gives one exact worked example required by the broader
problem.

## Reproducibility

- prereveal source commit: `524eef05ec7793b98dc5465e4f7965ea0bf2a818`
- registration commit: `9a67844b496eff8cfb7bfabbdf1ba923fae0a8a1`
- registration SHA-256:
  `0a5f1ad88e7c66822314e906792f1f9a5a97b4fcf10b13c7488a3cb751b1f234`
- result SHA-256:
  `74d8e0d0e4cbc39aa7691e1c40fa7669fda6ae8705773fee2c8db2c6fab52bf4`
- arithmetic: Python standard-library `fractions.Fraction`
- runtime: CPU only; no GPU
- dedicated tests: 8 passed

