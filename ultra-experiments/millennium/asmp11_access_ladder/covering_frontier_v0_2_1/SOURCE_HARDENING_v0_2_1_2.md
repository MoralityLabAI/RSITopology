# ASMP-11 v0.2.1.2 source hardening

## Status

Source checkpoint only. This change authorizes no registration, claim-grid run,
verification promotion, or reuse of the v0.2.1.1 artifacts under a new release
label. The verified v0.2.1.1 evidence bundle remains immutable prior evidence.

Version 0.2.1.2 preserves the v0.2.1 covering, lower-bound, exact-probability,
classification, resource-ceiling, claim-boundary arithmetic, and current
registered-grid numerical outcomes. It corrects the honest bracket endpoint
for admissible nonmonotone status sequences and otherwise hardens the release
measurement system after adversarial cross-review.

## Hardening contract

- registration requires the exact frozen source-name set, a full source commit
  OID, SHA-256 hashes of the committed blobs, and their Git blob OIDs;
- the registration, manifest, prior anchor, and registered grid must agree
  exactly, and the committed registration must postdate the source checkpoint;
- primary receipt link fields and output names are exact rather than
  caller-selected subsets;
- covering, cost, and bracket grids are compared as Cartesian `Counter`
  objects, so duplicates cannot replace missing cells;
- the honest bracket lower endpoint uses only the contiguous certified
  non-crossover prefix from `s=k`; an impossible cell after an unresolved gap
  cannot exclude an earlier crossover when cost monotonicity is not assumed;
- operation evidence is checked against registered wall, round, candidate,
  event, and stop contracts, while RAM compliance is explicitly recorded as
  unmeasured rather than passed;
- independent replay compares complete probe records and summaries, requires
  `binding=false`, and excludes the identity replay diagnostic from robustness
  agreement totals; and
- a final synthesis writer fresh-replays and exact-compares the independent
  verification, then binds it with the registration, primary receipt, and five
  conclusion layers without making alternative-probe unanimity binding.

## Required non-aliasing sequence

1. Commit this source checkpoint by itself.
2. Build `registration_v0_2_1_2.json` from that full commit OID.
3. Inspect and commit the registration separately.
4. Run into a new empty `artifacts_v0_2_1_2/` directory.
5. Write independent verification and synthesis receipts into that new bundle.

The existing `registration_v0_2_1_1.json`, `RESULT_v0_2_1_1.md`, and
`artifacts_v0_2_1_1/` must not be modified or used as v0.2.1.2 outputs.
