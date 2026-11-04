# Catastrophic-risk comparison audit v1

## Claim being tested

A high-stakes claim such as "the covert intervention will save billions" or
"the intervention's net effect is harmful" is a *causal comparative claim*.
It requires bounds on changes in outcome probabilities under a common
baseline, governance constraints, and evidence about the causal mechanism.
A population-at-risk figure by itself supplies none of these probability
changes.

For intervention `a` against registered baseline `b`, define

`DeltaL(a,b) = L_N * [p_N(a)-p_N(b)] + L_C * [p_C(a)-p_C(b)] + DeltaCost(a,b)`.

- `p_N` is the registered catastrophic-conflict outcome event.
- `p_C` is a separately specified catastrophic loss-of-AI-control event.
- `L_N`, `L_C` are consequences in the *same loss unit* and must allocate
  overlap between events to avoid double-counting joint consequences.
- `DeltaCost` covers intervention and opportunity cost. v1 inputs require
  nonnegative direct costs; negative opportunity costs require a revised model.

The sign of the interval upper bound establishes a *conditional* net benefit
when strictly below zero. A lower bound strictly above zero establishes
conditional harm. Intervals touching or straddling zero are unresolved. Interval
arithmetic is a safe outer enclosure even for correlated probability deltas;
it can be loose if the underlying studies share latent variables. The model
assumes the supplied delta intervals themselves have valid simultaneous
coverage. v1 does not calculate that coverage or establish causal identification.

## Evidence and consent requirements

`CausalDeltas` records two interval estimates, a study ID, causal grade,
independent *root identifiers*, and a scope (`synthetic` or `external`).
Repetition or relaying of one origin does not create independent evidence.
The evaluator rejects missing, unidentified, assumed, and duplicate-root
claims as adequate grounds for a confident intervention recommendation.
It distinguishes an externally *assessed* claim from verified empirical
validity. Authenticity and independence of roots require an outside verifier.

Four governance requirements remain separate from projected utility:
prior authorization, independent audit, human recall, and a transparent
protocol. Failure of any requirement blocks the intervention, including
when the supplied utility bounds predict benefit. `eligible_for_independent_review`
means an auditable argument is available for a decision-maker; the audit
engine grants no operational permission.

`audit_comparison(..., asserted="harm")` tests exactly the kind of
unsupported "net effect harmful" assertion raised by the Claude exchange.
Unknown risk intervals result in `request_evidence`. It can also identify
unsupported optimism or harm claims without substituting its own probabilities.
The receipt includes a canonical SHA-256 digest of the argument's evaluation.

## FRC and model succession

`finite_frc_tail_audit` computes the minima of observed suffixes of fidelity
scores for model generations `1...T`. A finite sample **cannot certify**
`liminf_(t->infinity) FRC_t`: arbitrarily poor generations can still occur
after the final observation. A rigorous asymptotic claim needs a persistent
lower-bound theorem, a verified closed transition system, or an explicit
stationarity/generalization assumption with its uncertainty reported.
The receipt therefore reports `infinite_liminf_certified: false`.

Link to CoupBench: its `risk_claim_audit` explores whether stylized
review policies obey these interval, evidence, authority, and successor
revalidation constraints under matched synthetic cases, including forged
source-root witnesses. Those numbers are toy calibration, not estimates of
war, nuclear conflict, AI collusion, or real intervention efficacy.

## Reproduce

From an editable install of RSITopology with pytest:

```sh
python -m pytest -q tests/test_catastrophe_decision.py
python -m scripts.run_catastrophe_comparison
```

The synthetic example registers `L_N=10`, `L_C=15`, nuclear delta
`[-0.08,-0.06]`, control delta `[0.005,0.01]` and cost `[0.01,0.02]`.
Its conditional net-loss interval is `[-0.715,-0.43]`. The numbers were
chosen to exercise the code and have no empirical significance.

### Future empirical work

1. Preregister the outcome definitions and a causal identification design.
2. Gather independent source attestations and interval coverage evidence.
3. Benchmark models on identical views with private oracle outcomes held out.
4. Stress the controls under changed model generations and revoked evidence.
5. Keep model-backed evidence distinct from script and synthetic fixture outcomes.
