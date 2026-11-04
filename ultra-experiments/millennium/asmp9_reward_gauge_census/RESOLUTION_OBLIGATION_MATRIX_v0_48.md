# ASMP-9 resolution-obligation matrix after v0.48

## Verdict

**ASMP-9 remains unresolved.**

Version v0.48 extends the exact finite confidence instrument from the
all-zero atom to every outcome of a registered experiment. For any frozen
outcome ordering it constructs the smallest direct nondecreasing Buehler
bound; an exact subset dynamic program then optimizes its reference cost over
all orderings.

The registered decision-dependence prediction did not survive confirmation.
An internal development fixture had disjoint optimum sets, but the disjoint
confirmation had 1,451,520 common optima and zero cross-regret. The evidence
therefore supports existence of both compatible and incompatible finite
fixtures, not a universal ordering theorem in either direction.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.48 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Correct maximal identifiability object | v0.36-v0.39 separate confusability, quotient, leakage, alignment, and decision equivalence; v0.40-v0.48 propagate finite risks through access, information, design, uncertainty, confidence, and evidence ordering | **Sharp for finite registered decision types and experiments** | Compact classes, history-dependent reward, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | v0.40 exact static containment; v0.41 adaptive Bellman containment; v0.42.1 finite samples; v0.44 pathwise information occupancy; v0.45 design; v0.46 exact shared-parameter image; v0.47 atom modulus; v0.48 full finite Buehler tables | **Complete for finite known channels and the declared shared-parameter iid grammar** | Continuous classes, unbounded horizons, interventions changing future laws, strategic response, and physically justified query channels |
| 3. Sharp query, sample, and intervention-order bounds | Exact special-case query rates, sentinel exponents, policy boxes, allocation results, matching atom lower/upper bound, and exact full-statistic ordering optimization | **Sharp finite instruments established; uniform structural modulus remains open** | Conditions for common optimal ordering versus forced cross-regret, statistic-independent comparisons, randomized procedures, continuous simultaneous constants, and efficient global design |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses, rectangles, exact coupled iid image, finite-grid confidence modulus, and ordering controls | **Partial and synthetic** | Correlated, adaptive, and strategic nuisance; uniform transfer; and a valid physical preference channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | Complete scalar-versus-relation-versus-no-object classification with replacement objects |

## What v0.48 establishes

For each finite decision risk `d` and outcome ordering `pi`, the registered
direct bound is

```text
U_pi(x_pi(j))
  = max {d(theta) : P_theta(S_j(pi)) > alpha}.
```

It is the smallest nondecreasing direct bound for that ordering. The exact
subset recurrence

```text
DP_d(S)
  = min_{x in S} [DP_d(S \ {x}) + w(x) B_d(S)]
```

optimizes expected reference cost and counts every optimizer.

The burned `(1,1,1)` fixture had no common optimizers and positive
cross-regrets. The prospectively registered `(2,1,1)` fixture instead had:

```text
four-class optimizers: 1,451,520
root-group optimizers: 4,354,560
common optimizers:     1,451,520
cross-regrets:         0 and 0.
```

Thus decision-dependent optimal evidence ordering exists in the finite
grammar, but is not forced by having distinct decision losses.

## What v0.48 does not establish

- A necessary-and-sufficient condition for shared optimal ordering.
- A universal ordering that is optimal for every decision quotient.
- A universal incompatibility or positive-regret theorem.
- Reference-law-independent ordering optimality.
- Optimality among randomized confidence procedures or other confidence
  criteria.
- A continuous-channel or asymptotic minimax theorem.
- Robustness to correlated, adaptive, or strategic misspecification.
- A calibrated real preference channel.

## Fixed resolution-directed sequence

1. **Completed through v0.48:** finite decision-relative object; static and
   adaptive known-channel characterization; finite-sample certification;
   rate and information refinements; decision-directed design; exact coupled
   image; matching atom modulus; and full finite Buehler-order optimization.
2. Characterize when two Buehler set functions admit a common optimal maximal
   chain, and when every pair of optima has positive cross-regret.
3. Extend that structural result to reference-law families or a
   statistic-independent lower/upper comparison.
4. Add a frozen correlated/adaptive/strategic misspecification neighborhood
   and prove robust transfer or a matching impossibility.
5. Extend the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered,
   calibrated channel.

## Next load-bearing target

Version v0.49 should be theorem-first, not another parameter-grid search.
Let

```text
B_d(S) = max {d(theta) : P_theta(S) > alpha}
```

on the outcome subset lattice. Determine structural conditions under which
two such set functions have a shared minimum-cost maximal chain.

At minimum, the successor should:

1. prove a sufficient common-order condition;
2. prove or construct a sharp obstruction to common optimality;
3. distinguish differing lexicographic representatives from disjoint optimum
   sets;
4. recover both the burned incompatibility witness and the prospective
   common-optimum fixture; and
5. state whether the condition is merely sufficient, necessary within a
   declared class, or fully necessary and sufficient.

Candidate structure to test includes common nested level sets, comonotone
marginal increments, and positive affine transformations of one decision
risk. Any theorem must be expressed on the induced set functions, because the
v0.48 null shows that distinct semantic losses alone do not determine
ordering compatibility.

## Claim boundary

Version v0.48 is classical finite confidence theory plus exact subset
optimization, specialized to one ASMP-9 experiment. It sharpens the finite
evidence-ordering obligation and records a valid prospective null. It does not
resolve general value identifiability, strategic behavioral misspecification,
real preference access, or ASMP-9.
