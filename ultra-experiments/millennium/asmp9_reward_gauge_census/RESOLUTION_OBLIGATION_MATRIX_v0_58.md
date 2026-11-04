# ASMP-9 resolution-obligation matrix after v0.58 development

## Verdict

**ASMP-9 remains unresolved.**

Versions v0.55-v0.56 give a verified sharp negative theorem for unrestricted
positive completion: every proper menu domain remains tier-ambiguous whenever
it admits a Luce or random-utility completion. Versions v0.57-v0.58 develop a
conditional positive replacement:

```text
bounded cross-menu interaction degree
  + menus through size r+2
  -> exact full-kernel reconstruction;

declared tier-separation margin
  + iid responses
  + observed probability floor
  -> finite-sample tier certification.
```

The positive lane is not yet prospectively registered. It is development
evidence, not a verified theorem result.

## Status against the five obligations

| Obligation | Strongest evidence after v0.58 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Maximal invariance or identifiability object | v0.36-v0.53 distinguish decision quotients, nuisance leakage, experiment comparison, and confidence procedures; v0.54-v0.56 classify complete-kernel Luce/RUM/non-RUM tiers | **Sharp in several finite registered grammars; open generally** | A class-level theorem for context-dependent, strategic, history-dependent, non-expected-utility, continuous, and welfare-relevant targets |
| 2. Necessary and sufficient query/intervention access | v0.56 proves complete access is sharp under unrestricted completion; v0.57 develops a constructive `r+2` menu-size threshold and a matching `r+1` ambiguity witness in `BP_r` | **Verified for unrestricted completion; candidate-sharp for bounded context degree** | External subsumption review and registration of v0.57; ties, hidden/endogenous menus, continuous domains, and physically realizable access |
| 3. Sharp query, sample, and intervention-order bounds | v0.57 gives an exact interpolation norm; v0.58 proves no finite exact-tier bound without separation, gives a sufficient margin-promised count, and matches the `gamma^-2` exponent on one `n=3,r=1` RUM/non-RUM slice | **Margin exponent matched on one finite slice; dimension and conditioning open** | Minimax dependence on `n`, `r`, probability floor, interpolation condition, confidence, adaptive design, and computational cost |
| 4. Robustness to behavioral misspecification | Earlier unknown-link, coherence, interval, and nuisance results cover named finite deviations; v0.58 handles ordinary iid sampling around a correctly specified `BP_r` kernel | **Partial and synthetic** | Adversarial contamination, correlated responses, context drift, endogenous menus, strategic answers, nonstationarity, and model-class misspecification |
| 5. No-go without a coherent latent value object | v0.54 supplies the finite stochastic-choice trichotomy; v0.56 gives unrestricted-completion ambiguity for all finite universes; v0.58 adds statistically contiguous paths across both adjacent tier boundaries | **Strong finite no-go evidence; general classification open** | Weak orders, incomplete/nontransitive preferences, dynamic and continuous choice, context mixtures, and a theorem stating when no coherent quotient-valued target exists |

## What v0.57-v0.58 add

### Structured completion

For pairwise context log odds of Boolean Mobius degree at most `r`, menus
through size `r+2` reconstruct the complete kernel. The threshold is sharp for
full-kernel recovery, and menus through size `r+1` cannot uniformly separate a
Luce kernel from a regularity-violating non-RUM kernel.

This answers the v0.56 successor question for one non-circular structural
class. It does not establish that real demonstrators satisfy bounded context
degree.

### Statistical boundary

Exact tier labels touch at both boundaries:

```text
Luce <-> non-Luce RUM <-> non-RUM.
```

No finite budget uniformly classifies them without a separation promise. Under
maximum menuwise `L1` margin `gamma`, the development theorem supplies a
finite sufficient count. An explicit margin-promised RUM/non-RUM pair proves
that `Omega(gamma^-2)` adaptive queries are necessary on one
three-alternative slice.

The upper bound can still be extremely conservative because the deterministic
Mobius reconstruction norm is large at intermediate degree.

## Remaining load-bearing sequence

### A. Bind and independently review the structured finite theorem

Before treating v0.57-v0.58 as claim-eligible:

1. complete a direct prior-art/subsumption review of bounded-context
   stochastic-choice model selection;
2. freeze the exact interpolation, lower-witness, margin, and oracle
   conventions;
3. prospectively verify the theorem source with an import-independent checker;
   and
4. keep the semialgebraic Luce-distance procedure distinct from an efficient
   practical algorithm.

### B. Add a sharp misspecification radius

The next mathematical target should not be another clean iid table. Freeze a
per-menu adversarial contamination model

```text
observed law = (1-epsilon) clean law + epsilon contaminant
```

and characterize exactly when two clean kernels can induce the same observed
law. For one categorical menu, contamination neighborhoods intersect exactly
when

```text
TV(p,q) <= epsilon/(1-epsilon).
```

The successor should lift this radius through the `BP_r` reconstruction and
the nested Luce/RUM tier margins, with:

- a constructive robust classifier above the radius;
- a matching cross-tier ambiguity pair below it;
- sampling and contamination uncertainty kept separate; and
- an explicit `inconclusive` state at equality.

This directly advances obligation 4 and stress-tests whether the v0.58 margin
is operational or merely clean-model notation.

### C. Classify context and menu endogeneity

After the contamination radius, replace exogenous menu sampling with a frozen
selection law. Determine when hidden or target-dependent menu availability is
ancillary, correctable by intervention, or exactly confounded with the value
object. Arbitrary selection is a trivial no-go and is not an acceptable final
statement; the useful target is a sharp class boundary.

### D. Continuous or representation-sensitive extension

Either extend the finite access theorem to a declared compact experiment class
with stable constants, or prove a representation-sensitive impossibility for
uniform exact certification. A finite sequence of increasingly large menu
censuses is not evidence for this obligation.

### E. Physical access validation

No mathematical access theorem shows that human or model responses implement
its query channel. A prospective physical bridge must test the response-model
and probability-floor premises before using the recovered object for any
decision or welfare claim.

## Next load-bearing target

**ASMP-9 v0.59 should be the adversarial-contamination radius, conditional on
v0.57-v0.58 surviving the prior-art gate.**

The intended theorem has a live positive and negative side:

```text
above contamination-plus-sampling radius:
    one tier certificate or an explicit inconclusive result;

at or below the radius:
    two margin-admissible clean kernels in different tiers
    with the same contaminated observation law.
```

The target is finite and exact enough to verify, but it attacks behavioral
misspecification—the largest unresolved obligation touched least by the
v0.54-v0.58 chain.

## Claim boundary

The verified v0.56 theorem and unregistered v0.57-v0.58 development together
close neither strategic behavior nor the broad ASMP-9 classification. They do
not establish that humans or models have a coherent latent value object, that
the selected tier is morally relevant, or that a physically realizable query
channel meets the assumptions. No full resolution is claimed.
