# ASMP-9 hidden-consideration development result v0.64

Status: **unregistered development result; not claim eligible**.

## Result

The hidden-menu branch has an exact access dichotomy.

### Unrestricted hidden consideration

For any finite stochastic choice kernel and any latent strict preference,
menu- and instruction-dependent singleton consideration reproduces the kernel
exactly.  Therefore:

```text
randomized recorded menus
  + randomized attention prompts
  + unrestricted unobserved compliance

do not identify any nonconstant preference functional.
```

Randomization does not become an attention intervention merely because the
prompt is labelled that way.

### General hidden-compliance interface

For each intervention, the allowed hidden consideration sets induce an
attainable-choice set for every latent ranking.  Under unrestricted
rank-dependent compliance, two rankings are separated exactly when one
intervention gives them disjoint attainable-choice sets.  A suite identifies
all rankings exactly when these intervention-specific separation sets cover
every unordered pair of rankings.

This supplies an exact finite target for intermediate hidden-menu grammars,
rather than treating unrestricted collapse and perfect pair forcing as the
only possible interfaces.

### Verified exact pair forcing

If the actual considered set can instead be forced to equal an exact pair,
and the latent preference is deterministic and stable, the nonadaptive pair
family identifies every strict ranking iff it is complete:

```text
E=binom(X,2).
```

The sharp nonadaptive count is `binom(n,2)`.  Every missing pair has an
adjacent-swap witness producing the same answers on all queried pairs.

## Verification

```text
8 tests passed
```

The import-independent development census reports:

```json
{
  "collapse_rankings": 872,
  "complete_signatures": 5912,
  "compliance_pair_checks": 7329146,
  "graph_cells": 1098,
  "missing_edge_witnesses": 84,
  "registered": false,
  "status": "development_checks_passed"
}
```

The graph census exhausts every pair-query graph through five items.
Complete-family injectivity is also checked through seven items, and an
explicit missing-edge witness through eight.

## Prior-art decision

The theorem is not registered as a novelty claim.  Structured
limited-consideration recovery, bounded-shifter observational equivalence,
two-instrument identification, and complete stochastic-choice identified
sets all have direct current precedents.

The durable ASMP-9 points are the interface distinction

```text
assigned instruction != verified consideration intervention.
```

and the exact intermediate object:

```text
minimum identifying suite = minimum separation cover
over attainable-choice supports.
```

## Next decision

Before prospective registration, decide whether this elementary dichotomy is
worth claim-eligible packaging.  The mathematically harder surviving branch
is a responder that observes the query policy or changes its response law
over time.  That branch must freeze the adversary's commitment time and the
history visible to each side.

## Claim boundary

This is a finite consolidation and access ledger.  It is not a new
limited-consideration theorem, a stochastic-mixture identification result, a
welfare result, a physical human/model finding, or a resolution of ASMP-9.
