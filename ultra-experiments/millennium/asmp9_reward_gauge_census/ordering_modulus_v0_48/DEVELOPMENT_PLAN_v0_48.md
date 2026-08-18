# ASMP-9 v0.48 ordering-modulus development plan

## Question

Can the evidence ordering used to turn confidence coverage into a full
decision-risk bound be chosen independently of downstream use?

## Burned search

Use three independent binary calibration cells with one sample per cell,
giving exactly eight count-vector outcomes. Search small rational shared-BSC
grids and several rational alpha levels. For each fixture:

1. compute the complete exact horizon-two four-class decision risk;
2. use `p_root` as the root-group risk;
3. use the uniform mixture of all parameter laws as the frozen reference law;
4. build every subset-prefix Buehler bound;
5. exhaust all `8! = 40,320` evidence orderings for each decision;
6. retain every optimizer; and
7. test whether the two optimizer sets intersect and whether both cross-costs
   are strictly positive.

The search is development-only. Its first live fixture selects the shape of a
disjoint confirmation; no searched value is claim-eligible.

## Liveness requirements

- More than one distinct Buehler bound value.
- Nonconstant exact decision risk for both losses.
- Every experiment row and reference mixture sums exactly to one.
- At least one optimizer for each loss.
- Prefer a fixture with disjoint optimizer sets and positive cross-regrets.
- If no disjoint fixture exists, report the null rather than enlarging the
  search after inspecting confirmation outcomes.

## Prospective confirmation

A confirmation must change at least one of:

- channel grid;
- alpha;
- allocation; or
- target signature,

while freezing the change and the predicted incompatibility before risk
outcomes are computed. It must retain the complete ordering universe and an
order-independent endpoint control.

## Prior-art gate

Before registration, place the finite construction below:

- Neyman confidence coverage;
- Buehler optimal limits and ordering dependence;
- finite statistical decision theory; and
- exact subset dynamic programming / sequencing formulations.

No novelty claim attaches to those ingredients.

## Claim boundary

This development probes one finite ordering choice. Even a positive
confirmation would show decision-dependent evidence ordering, not solve
general value identifiability or ASMP-9.
