# ASMP-9 resolution-obligation matrix after v0.51

## Verdict

**ASMP-9 remains unresolved.**

Version v0.51 closes randomized minimax regret over individually valid
evidence orderings inside the finite Buehler grammar. Mixing strictly improved
worst-case regret for 234 of 361 table pairs, but randomized value was zero
for exactly the same 79 pairs with a deterministic common optimum.

The result confirms a sharp conceptual boundary: randomized compromise can
reduce certificate cost regret, but cannot create exact decision-relative
identity when the common-chain intersection is empty.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.51 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Correct maximal identifiability object | v0.36-v0.39 separate confusability, quotient, leakage, alignment, and decision equivalence; v0.40-v0.51 propagate finite risks through access, information, design, uncertainty, confidence, evidence ordering, reference families, and mixed-order regret | **Sharp for finite registered decision types and experiments** | Compact classes, history-dependent reward, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | v0.40 static containment; v0.41 adaptive containment; v0.42.1 finite samples; v0.44-v0.47 information, design, and moduli; v0.48-v0.51 full-statistic, common-order, reference-family, and mixed-order characterizations | **Complete for finite known channels and the declared shared-parameter iid grammar** | Continuous classes, unbounded horizons, interventions changing future laws, strategic response, and physically justified query channels |
| 3. Sharp query, sample, and intervention-order bounds | Exact rates and exponents, decision-directed allocation, coupled uncertainty, sharp atom modulus, full Buehler optimization, common-order certificates, reference-weight regions, and exact mixed-order regret | **Sharp finite ordering instruments established** | Completeness among all direct confidence maps, aggregate randomized coverage, continuous constants, efficient global design, and strategic lower bounds |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses, coupled iid images, confidence moduli, evidence controls, reference-family sensitivity, and mixed regret | **Partial and synthetic** | Correlated, adaptive, and strategic nuisance; uniform transfer; and a valid physical preference channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | Complete scalar-versus-relation-versus-no-object classification with explicit replacement objects |

## What v0.51 establishes

For regret matrix

```text
A(pi,s)
  = C_s(pi) - min_sigma C_s(sigma),
```

the optimizer's randomized minimax value and the adversary's least-favorable
scenario value are an exact finite primal/dual LP pair.

Because `A>=0`,

```text
randomized value = 0
  iff
support is contained in the deterministic common-zero intersection.
```

On the complete three-outcome census:

```text
strict randomization gain: 234/361 pairs
maximum gain:              1/4
mean gain:                 35489/454860
new zero certificates:     0.
```

## What v0.51 does not establish

- Completeness of Buehler ordering among all deterministic direct bounds.
- Optimal aggregate-coverage randomized confidence procedures.
- Operational desirability of randomized evidence reporting.
- Efficient large-width solution despite stronger prior-art algorithms.
- Statistic-independent or continuous asymptotic minimax comparison.
- Robustness to correlated, adaptive, or strategic misspecification.
- A calibrated physical preference channel.
- A complete scalar-versus-relation-versus-no-object classification.

## Fixed resolution-directed sequence

1. **Completed through v0.51:** finite decision-relative object; static and
   adaptive known-channel characterization; finite-sample certification;
   information and design refinements; exact coupled image; sharp atom and
   full-statistic moduli; common-chain and ordering-gauge theorems;
   reference-law-family robustness; and randomized minimax regret over valid
   orderings.
2. Prove or refute completeness of all-order Buehlerization among
   deterministic direct finite confidence maps.
3. Characterize aggregate-coverage randomized procedures separately.
4. Extend to a continuous experiment class or statistic-independent
   lower/upper comparison.
5. Add correlated/adaptive/strategic misspecification and prove transfer or a
   matching impossibility.
6. Complete the scalar-versus-relation-versus-no-object trichotomy.
7. Re-enter real-model measurement only through a prospectively registered,
   calibrated channel.

## Next load-bearing target

Let `u(x)` be any deterministic direct upper confidence map with uniform
coverage. Sort outcomes by nondecreasing `u(x)` and construct the minimal
Buehler bound under that order.

The candidate v0.52 theorem is:

> The induced Buehler map is pointwise no larger than `u`.

If true, it follows that optimizing over all evidence orderings already
equals optimizing over every valid deterministic direct confidence map under
any positive reference law. The proof candidate is short: if the Buehler
bound at prefix `j` exceeded `u(x_j)`, that prefix would be a failure set of
probability greater than `alpha` for the witnessing parameter, contradicting
coverage.

Version v0.52 should:

1. state and prove the dominance theorem with ties handled explicitly;
2. verify it over every three-valued monotone table on three outcomes and
   every direct report vector from the same level set;
3. compare global direct-map optima with all-order Buehler optima under
   multiple positive reference laws; and
4. provide a strict-dominance control plus an equality control.

This would close deterministic direct-map completeness. It must not be
silently extended to randomized procedures whose individual components can
under-cover while their aggregate meets coverage.

## Claim boundary

Version v0.51 is a directly subsumed randomized-minmax specialization. Its
exact census closes mixed ordering regret, not general randomized confidence
inference. It does not identify real values, validate human preference
access, prove continuous or strategic robustness, or resolve ASMP-9.
