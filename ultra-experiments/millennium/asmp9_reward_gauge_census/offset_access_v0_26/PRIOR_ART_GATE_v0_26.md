# ASMP-9 v0.26 prior-art gate

Status: development audit; must be finalized before registration.

## Proposed contribution sentence

For a finite anchored utility vector, a registered additive-offset comparison
channel converts every unknown strictly increasing symmetric response link
into the same coordinate-threshold oracle. Bisection gives sharp dyadic
population-query complexity, while finite-sample recovery requires an explicit
margin floor and is impossible uniformly over arbitrarily flat links.

This is a specialization and consolidation, not a novelty claim.

## Primary sources inspected

1. Lin and Kulasekera, *Identifiability of single-index models and
   additive-index models*, Biometrika 94 (2007), DOI
   `10.1093/biomet/asm029`.

   Unknown-link single-index identifiability depends on support and
   normalization. The v0.26 result does not claim unknown-link identifiability
   as new.

2. Ge, Juba, and Vorobeychik, *Learning Linear Utility Functions From Pairwise
   Comparison Queries*, arXiv `2405.02612` (2024).

   This paper distinguishes prediction from utility-parameter recovery and
   proves a qualitative active-versus-passive learnability gap for linear
   utilities under its own query and noise models. V0.26 isolates a
   one-dimensional threshold subproblem created by a stronger registered
   additive-offset intervention.

3. Frazier, Henderson, and Waeber, *Probabilistic Bisection Converges Almost
   as Quickly as Stochastic Approximation*, Mathematics of Operations Research
   44(2), 2019, DOI `10.1287/moor.2018.0938`.

   Probabilistic bisection and stochastic root finding are classical. Their
   work explicitly treats noisy directional responses and removes the
   fixed-noise-probability assumption using power-one tests. V0.26's
   Hoeffding construction is deliberately simpler and is not claimed optimal.

4. Massimino and Davenport, *As You Like It: Localization via Paired
   Comparisons*, JMLR 22(186), 2021.

   Adaptive binary comparisons can stably localize a continuous object under
   geometric and noise assumptions. V0.26 is not a general paired-comparison
   localization theorem.

5. Bostic, Herrnstein, and Luce, *The Effect on the Preference-Reversal
   Phenomenon of Using Choice Indifferences*, Journal of Economic Behavior &
   Organization 13(2), 1990, DOI `10.1016/0167-2681(90)90086-S`.

   Choice indifference points were elicited with a classical up-down method
   and Parameter Estimation by Sequential Testing. More generally,
   willingness-to-pay, certainty-equivalent, matching, and iterative-bidding
   methods locate indifference thresholds by varying a known consequence.
   The v0.26 offset channel belongs to this classical elicitation family.

6. Bateman, Langford, and Rasbash, *Willingness-To-Pay Question Format Effects
   in Contingent Valuation Studies*, in *Valuing Environmental Preferences*
   (Oxford University Press, 2001), DOI
   `10.1093/0199248915.003.0015`.

   This source compares open-ended, bounded dichotomous-choice, and iterative
   bidding formats. V0.26 abstracts away the behavioral format effects those
   methods expose; its positive theorem is conditional on a stable response
   model under offset interventions.

7. Skalse, Farrugia-Roberts, Russell, Abate, and Gleave, *Invariance in Policy
   Optimisation and Partial Identifiability in Reward Learning*, ICML 2022,
   arXiv `2203.07475`; and Skalse and Abate, *Partial Identifiability and
   Misspecification in Inverse Reinforcement Learning*, arXiv `2411.15951`.

   Reward-learning invariances and misspecified behavioral models are the
   broader literature. The current result is one finite access-class theorem
   below that scope.

## Subsumption assessment

The bisection algorithm, metric-entropy lower bound, and need for a margin
condition are classical. The ASMP-9 value is the explicit quotient/access
ledger:

```text
unknown monotone link + uncalibrated finite comparisons
  -> non-affine difference-order ambiguity;

unknown monotone link + a known offset spanning every threshold
  -> utility modulo translation, with sharp dyadic population access;

finite samples + no margin floor
  -> no uniform rate;

finite samples + a declared margin floor
  -> an explicit conservative recovery certificate.
```

The additive offset fixes utility scale by assumption. The result must never
be described as extracting cardinal scale from ordinary ordinal comparisons.

## Search record

Searches performed 2026-07-28:

- `pairwise comparisons unknown link function active learning utility
  differences query offsets`
- `comparison queries recover utility vector binary search`
- `cardinal utility pairwise comparison oracle query complexity`
- `stochastic root finding binary responses unknown response probability`
- `active learning threshold unknown regression function binary search`
- `willingness to pay bisection elicitation dichotomous choice`
- `choice indifference point PEST preference reversal`

Databases and sites included arXiv, JMLR, PMLR, Mathematics of Operations
Research, Oxford Academic, ScienceDirect, and publisher/author primary pages
surfaced by web search.

## Registration disposition

`partial_extension`, with novelty explicitly disclaimed. Registration is
allowed only after the proof checks include:

- exact population recovery;
- exact dyadic upper/lower-bound agreement;
- a restricted-offset indistinguishability witness;
- deterministic bounded-error verification of the finite-sample decision
  rule; and
- preservation of the v0.8 no-offset non-affine witness.
