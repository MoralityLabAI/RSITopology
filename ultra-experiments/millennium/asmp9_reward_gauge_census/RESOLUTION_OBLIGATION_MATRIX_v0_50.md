# ASMP-9 resolution-obligation matrix after v0.50

## Verdict

**ASMP-9 remains unresolved.**

Version v0.50 removes the arbitrary-single-reference-law seam from the finite
evidence-ordering result. For each ordering, its joint-optimality region is an
exact rational polytope in reference-weight space. Robustness over a declared
reference polytope is necessary and sufficient at its vertices, and an
intersection of scenario-specific tight-predecessor DAGs returns every robust
common ordering or a labelled obstruction.

Across all 361 ordered pairs of three-outcome Buehler-admissible monotone
tables, 79 retained a common ordering across both frozen reference vertices
and 282 did not. All exact path, regret, region, and interpolation comparisons
matched.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.50 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Correct maximal identifiability object | v0.36-v0.39 separate confusability, quotient, leakage, alignment, and decision equivalence; v0.40-v0.50 propagate finite decision risks through access, information, design, uncertainty, confidence, evidence ordering, and reference-law families | **Sharp for finite registered decision types and experiments** | Compact classes, history-dependent reward, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | v0.40 static containment; v0.41 adaptive Bellman containment; v0.42.1 finite samples; v0.44 policy information; v0.45-v0.47 design and exact moduli; v0.48-v0.50 full-statistic, common-order, and reference-family characterizations | **Complete for finite known channels and the declared shared-parameter iid grammar** | Continuous classes, unbounded horizons, interventions changing future laws, strategic response, and physically justified query channels |
| 3. Sharp query, sample, and intervention-order bounds | Exact rates and exponents, decision-directed allocation, exact coupled uncertainty, sharp atom modulus, full Buehler optimization, common-order certificates, and exact reference-weight regions | **Sharp finite deterministic instruments established** | Randomized procedures, continuous simultaneous constants, efficient global design, and lower bounds under strategic response |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses, coupled iid images, confidence moduli, evidence-order controls, and reference-family sensitivity | **Partial and synthetic** | Correlated, adaptive, and strategic nuisance; uniform transfer; and a valid physical preference channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | Complete scalar-versus-relation-versus-no-object classification with explicit replacement objects |

## What v0.50 establishes

For ordering feature vectors `b_d^pi`,

```text
R_pi(D)
  = {
      w :
      <w,b_d^pi-b_d^sigma> <= 0
      for every d and sigma
    }
```

is exactly the reference-law region where `pi` is jointly optimal.

For `W=conv{v_i}`, one order is optimal for every `d` and `w in W` exactly
when it is optimal in every `(d,v_i)` scenario. The corresponding
tight-predecessor DAG intersection gives a necessary-and-sufficient robust
chain certificate.

The exact worst-case regret is

```text
Reg(pi;D,W)
  = max_(d,i,sigma)
      <v_i,b_d^pi-b_d^sigma>.
```

The smallest reference-sensitivity witness has one objective, two outcomes,
two reference vertices, no robust ordering, and minimum worst-case regret
`1/2`.

## What v0.50 does not establish

- That any registered reference law is scientifically correct.
- Optimal randomized confidence procedures.
- A statistic-independent or asymptotic minimax comparison.
- Efficient representation of all ordering regions at large width.
- Continuous experiments or unbounded adaptive horizons.
- Robustness to correlated, adaptive, or strategic misspecification.
- A calibrated physical preference channel.
- A complete scalar-versus-relation-versus-no-object classification.

## Fixed resolution-directed sequence

1. **Completed through v0.50:** finite decision-relative object; static and
   adaptive known-channel characterization; finite-sample certification;
   rate and information refinements; decision-directed design; exact coupled
   image; sharp atom and full-statistic moduli; exact common-chain
   characterization; minimal universal ordering no-go; positive zero-curl
   equivalence; and exact reference-law-family robustness.
2. Characterize randomized evidence-ordering procedures and their dual
   adversarial scenario game.
3. Extend the result to a statistic-independent lower/upper comparison or
   continuous experiment class.
4. Add a frozen correlated/adaptive/strategic misspecification neighborhood
   and prove robust transfer or a matching impossibility.
5. Complete the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered,
   calibrated channel.

## Next load-bearing target

Randomization cannot produce exact zero regret unless its support lies in the
common optimizer intersection. It can, however, reduce positive worst-case
regret by mixing deterministic orderings.

Version v0.51 should:

1. formulate the finite zero-sum game whose rows are orderings and whose
   columns are objective/reference scenarios;
2. prove the exact LP dual and the support condition for zero regret;
3. give a smallest witness where randomization strictly improves minimax
   regret but cannot reach zero;
4. quantify the gap between deterministic and randomized robust regret over a
   frozen complete table universe; and
5. keep exact certification distinct from approximate minimax compromise.

The v0.50 two-outcome switch already predicts the smallest control:
deterministic minimax regret is `1/2`, while an equal mixture of its two
orders should reduce worst-case regret to `1/4` without restoring exact
optimality.

## Claim boundary

Version v0.50 is classical finite linear, multiobjective, and robust
shortest-path mathematics specialized to Buehler evidence ordering. It
closes reference-law-family sensitivity inside that grammar. It does not
identify real values, validate human preference access, prove continuous or
strategic robustness, or resolve ASMP-9.
