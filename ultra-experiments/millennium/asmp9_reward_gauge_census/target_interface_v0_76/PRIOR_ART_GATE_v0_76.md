# Prior-art gate for ASMP-9 target interface v0.76

Status: **elementary factorization and sufficient-statistic bookkeeping**.

## Subsumption

No novelty is claimed for:

- factorization of one finite map through another;
- refinement order on equivalence relations or partitions;
- sufficient statistics as target-recovering summaries; or
- nuisance invariance as constancy on declared target fibers.

The contribution is a terminology and decision-ledger correction inside the
ASMP-9 program.

## Relation to prior versions

- v0.69 constructs a representative-insensitive linear channel by quotienting
  physical nuisance and visible gauge image.
- v0.74 requires equality between observation fibers and licensed gauge
  orbits for an exact target interface.
- v0.76 separates the weaker decoder-based recovery condition from the
  additional no-leakage condition.

None of the earlier algebra is invalidated. Their claim type is now named more
precisely.

## Residual contribution

Every future access result should report two booleans:

```text
target_recoverable
representative_insensitive
```

and derive its status from the registered total table. A single label such as
“identified” is insufficient when the raw instrument may expose a gauge
representative.

## Hostile-review questions

1. Is the target decoder known constructively or only asserted to exist?
2. Does representative leakage create a governance or privacy hazard?
3. Is a lossy invariant statistic being mistaken for a sufficient statistic?
4. Is extra observation information being discarded before or after the
   target decoder is frozen?
5. Are finite-data approximate equalities replacing exact partition claims?

All remain outside the finite exact development.
