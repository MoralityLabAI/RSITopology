# ASMP-9 resolution-obligation matrix after v0.41

## Verdict

**ASMP-9 remains unresolved.**

Version v0.41 extends the exact finite access object from static subsets to
adaptive finite-horizon policies:

```text
sequential access sufficient at epsilon
  iff the reference adaptive upper risk polytope lies in the
     epsilon-shifted adaptive upper risk polytope of that access.
```

The compiler is exact and necessary-and-sufficient for known finite channels,
but policy-tree growth and the classical optimal-decision-tree boundary make
exhaustive compilation computational rather than efficient.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.41 | Status | Missing resolution evidence |
| --- | --- | --- | --- |
| 1. Correct maximal identifiability object | v0.36-v0.39 separate confusability, quotient, deficiency, leakage, and alignment; v0.40-v0.41 give static and adaptive upper risk polytopes | **Sharp for arbitrary known finite experiments relative to a registered finite loss type and horizon** | Continuous/compact classes, history-dependent rewards, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | v0.40 exact static containment; v0.41 exact Bellman generator recursion and adaptive containment | **Complete for finite known-channel, bounded-horizon policies by exhaustive compilation** | Unknown channels, interventions that alter later channel laws beyond the registered controlled experiment, unbounded horizons, and uniform infinite-class theorems |
| 3. Sharp query, sample, and intervention-order bounds | Many exact special-case rates; Test Cover boundary; v0.41 strict adaptive/open-loop gap | **Structural boundaries and finite examples established** | Approximation guarantees, adaptive policy-search complexity for the declared deficiency objective, confidence-valid finite-sample upper/lower certificates, and matching minimax rates |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses | **Partial and mostly synthetic** | Uniform robust transfer or matching no-go theorems over correlated/strategic nuisance and a valid physical channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | A two-sided scalar-versus-relation-versus-no-object classification with replacement objects |

## What v0.41 establishes

For finite query library `Q` and decision problem `d`, the exact recursion:

```text
V_(h+1)
  = V_0 union over q
      {sum_y diag(P_q(y|.)) v_y : v_y in V_h}
```

generates the upper risk set:

```text
U_h(d,Q) = conv(V_h(d,Q)) + R_+^Theta.
```

The v0.40 containment theorem therefore applies unchanged after replacing
static query-product experiments with adaptive policy-tree generators.

The registered noisy fixture gives a strict classification gap:

```text
adaptive h=2     = 61/135
open-loop h=2    = 13/25
gain             = 46/675,
```

while the asymmetric group decision has `4/45` in both modes.

## What v0.41 does not establish

- Exhaustive policy-tree compilation is not an efficient general algorithm.
- The query channels and downstream decision type are known exactly.
- The horizon is finite and fixed.
- No channel probabilities are estimated from samples.
- No strategic source changes its response law based on the audit policy.
- No real-model measurement channel is validated.

## Fixed resolution-directed sequence

1. **Completed through v0.41:** correct finite decision-relative object;
   observational/interventional alignment; static and adaptive known-channel
   access characterization.
2. Add finite-sample channel estimation with simultaneous confidence-valid
   inner and outer upper-risk-polytope bounds.
3. Derive matching sample or impossibility rates for deciding access
   sufficiency at a declared positive containment margin.
4. Add a frozen misspecification neighborhood and prove robust transfer or a
   matching impossibility under correlated or strategic nuisance.
5. Extend the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered,
   calibrated channel.

## Next load-bearing target

Version v0.42 should not add another known-channel finite census. It should
define a confidence-valid finite-sample access certificate:

```text
inner source upper-risk set
  and
outer reference upper-risk set
  imply access sufficiency only when containment clears
  a registered positive margin.
```

It must distinguish `pass`, `fail`, and `inconclusive`; a point estimate may
not certify access. The first theorem target is a finite Lipschitz bound that
propagates simultaneous channel-probability error through the Bellman
recursion and the directed containment radius.

## Claim boundary

All dynamic-programming and decision-tree ingredients are classical. Version
v0.41 consolidates them into the ASMP-9 decision-relative access compiler and
confirms that adaptivity gains depend on the registered loss. The broader
candidate problem remains open.
