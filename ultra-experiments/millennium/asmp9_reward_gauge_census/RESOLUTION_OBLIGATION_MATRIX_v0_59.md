# ASMP-9 resolution-obligation matrix after v0.59 development

## Verdict

**ASMP-9 remains unresolved.**

Version v0.59 closes one exact misspecification cell:

```text
fixed per-menu Huber contamination
  + compact separated value-tier class
  -> exact population threshold Delta/(1+Delta).
```

It also supplies a bounded-context lower bracket, a matching-direction
cross-tier ambiguity witness, and a conservative finite-sample ledger. The
class modulus is not yet sharply evaluated in general, the positive
v0.57-v0.59 lane is unregistered, and the model excludes adaptive corruption
and menu endogeneity.

## Status against the five obligations

| Obligation | Strongest evidence after v0.59 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Maximal invariance or identifiability object | v0.36-v0.53 separate decision quotients, nuisance leakage, experiment comparison, and confidence procedures; v0.54-v0.56 classify finite Luce/RUM/non-RUM tiers | **Sharp in several finite grammars; open generally** | A class-level object covering context dependence, history, non-expected utility, continuous outcomes, strategic response, and welfare relevance |
| 2. Necessary and sufficient query/intervention access | v0.56 proves complete finite-menu access is sharp under unrestricted completion; v0.57 develops the `r+2` threshold for bounded context degree | **Verified for unrestricted finite completion; candidate-sharp conditionally** | Registration/subsumption review of v0.57, physically realizable queries, endogenous or hidden menus, ties, and continuous domains |
| 3. Sharp query, sample, and intervention-order bounds | v0.58 gives no-uniform-rate paths, a conservative sufficient count, and an `Omega(gamma^-2)` lower bound on one slice; v0.59 subtracts contamination bias from the clean coordinate tolerance | **Margin exponent matched on one clean slice; robust rates and conditioning open** | Minimax robust rates, dependence on `n,r,a,K_star,delta`, adaptive design, computational cost, and a practical certified estimator |
| 4. Robustness to behavioral misspecification | v0.59 gives the exact fixed-mixture population radius through the cross-tier observed-TV modulus, plus a constructive RUM/non-RUM ambiguity witness | **Exact for known fixed Huber mixtures; strategic robustness open** | Adaptive replacement, correlated responses, unknown contamination, drift, endogenous menus, strategic answers, and general model-class misspecification |
| 5. No-go without a coherent latent value object | v0.54 supplies a finite stochastic-choice trichotomy; v0.56 proves unrestricted-completion ambiguity; v0.58 gives contiguous boundary paths; v0.59 makes one boundary robustly confusable | **Strong finite no-go evidence; broad classification open** | Weak/incomplete/nontransitive preferences, dynamic and continuous choice, mixtures, and a general theorem for when no coherent quotient-valued target exists |

## What v0.59 establishes

### Exact contamination geometry

For independently selected per-menu contaminants, two clean kernels have a
common observed population law iff

```text
max_A TV(p_A,p'_A) <= epsilon/(1-epsilon).
```

Thus the exact cross-tier radius is governed by one intrinsic modulus:

```text
Delta(C,D)
  = min_(different tiers)
      max_(A in D) TV(p_A,p'_A).
```

This converts "robustness" from a qualitative adjective into a measurable
population separation. It does not make `Delta` easy to compute.

### Constructive finite witness

On the three-alternative `BP_1` slice, a margin-promised RUM/non-RUM pair has
observed TV `2 gamma` and becomes exactly confusable at

```text
epsilon = 2 gamma/(1+2 gamma).
```

The equality law and both contaminants are rational and explicit.

### Conservative sampling ledger

For the current plug-in reconstruction,

```text
interpolation conditioning
  + deterministic contamination bias
  + statistical coordinate error
  < clean tier margin.
```

The resulting counts can be enormous. They are diagnostics of the present
proof technique, not minimax lower bounds.

## Remaining load-bearing sequence

### A. Review and register the v0.57-v0.59 finite theorem stack

Before treating the conditional positive lane as claim-eligible:

1. complete external subsumption review of the bounded-context choice class;
2. bind the compact tier fibers, exact modulus, equality convention, and
   distance-oracle semantics;
3. decide whether the population theorem and conservative sampling corollary
   should be one registration or separate registrations;
4. prospectively verify with an import-independent checker; and
5. preserve the distinction between decidability and efficient computation.

### B. Make the contamination radius computational

The formula `Delta/(1+Delta)` is exact but only operational if `Delta` can be
computed or certified. On fixed small universes:

1. formulate the RUM side with ranking-weight linear constraints;
2. formulate Luce closure distance with certified polynomial constraints;
3. derive primal cross-tier witnesses and dual lower certificates; and
4. quantify the gap between the v0.59 interpolation lower bound and the true
   modulus.

A table of numerical optimizers without dual certificates is not a sharp
result.

### C. Classify menu endogeneity

This is now the next conceptual target. Replace the exogenous observed menu
family by a frozen selection channel. Characterize when selection is:

- ancillary and ignorable;
- correctable from recorded propensities or interventions;
- partially identifying; or
- exactly confounded with the value tier.

Arbitrary target-dependent selection gives a trivial no-go and is not enough.
The useful theorem needs a positive and negative boundary in a declared
selection class.

### D. Strengthen contamination beyond fixed mixtures

Separate future models rather than silently generalizing v0.59:

1. strong/adaptive sample replacement;
2. menu-correlated contaminants;
3. unknown contamination level;
4. drifting clean kernels; and
5. a strategic responder observing the query policy.

Each changes the experiment law and requires a new proof.

### E. Continuous and physical extensions

No finite-menu theorem establishes that human or model answers implement its
access channel or that its identified object is welfare-relevant. A
prospective bridge must validate probability floors, context-degree
structure, separation, stationarity, and response semantics before the
certificate can authorize a decision.

## Next load-bearing target

**ASMP-9 v0.60 should be a sharp menu-selection/endogeneity theorem, while
v0.59 undergoes independent review.**

The intended two-sided statement is:

```text
inside a declared selection class:
    recorded selection information or intervention identifies the same
    tier as exogenous complete access;

outside the boundary:
    two clean kernels in different tiers and two admissible selection laws
    induce the same observed menu-choice process.
```

The target should avoid the vacuous unrestricted-selection impossibility and
should distinguish known propensities, positivity failure, latent
target-dependent selection, and direct menu intervention.

## Claim boundary

The v0.59 theorem is a finite fixed-mixture robustness result. It neither
establishes coherent human or model values nor resolves strategic response,
menu endogeneity, continuous behavior, computational feasibility, or the
semantic adequacy of the tier labels. No full ASMP-9 resolution is claimed.
