# ASMP-3 expected weighted-noise completion audit v1.7

## Newly closed

```text
separate per-truth expected flip-cost noise class = typed
distributional verifier game = reduced to minimum total variation
normalized-score verifier lower certificate = exact
all-zero/all-one endpoint-mixture upper certificate = exact
value max(0,1-2B/C) for rational B = proved
dependence only on total cost C = proved/certified
all 2729 v1.6 integer-budget rows = compared
expected value <= hard value = certified universally on registry
strict hard/expected separation = witnessed in 1139 rows
subset-sum paired instance convexification = certified
fractional-budget value 5/8 witness = certified
large 2^32-score instance without word enumeration = certified
small rational distribution grids = exhausted (35808 pairs)
clean-room TV/parent/grid checker = passed
```

## Still open

```text
almost-sure or tail-risk weighted budgets beyond v1.6 = open
joint expected budget averaged over truth = open
nonuniform or adversarial truth priors = open
truth-ignorant or randomness-restricted noise = open
path-observed costs and adaptive verifier queries = open
honest-prover computation characterization = open
matching communication and honest-prover lower bounds = open
WV-ADM interface optimization = open
v0.1 scope adjudication = open/normative
external mathematical review = absent
```

## Noise-quantifier resolution

The hard-budget PARTITION obstruction is not a generic weighted-noise
obstruction.  Replacing almost-sure legality with an expectation constraint
convexifies the feasible languages, and the exact problem becomes a two-moment
total-variation saddle with a constant-size certificate after summing costs.

## Non-overclaim rule

The formula applies only to the declared separate per-truth expectation bounds.
It must not be transferred to hard, tail, coupled-prior, path-dependent, or
truth-ignorant constraints by matching only their mean error rate.
