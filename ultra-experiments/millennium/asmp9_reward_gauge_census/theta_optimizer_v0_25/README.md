# ASMP-9 generalized-theta optimizer development (v0.25)

This branch develops an exact global optimizer for a nontrivial
overlapping-cycle class at `epsilon=1/2`.

The key candidate theorem is:

> Every global optimum on a generalized theta block balances counts within
> each individual path.

The remaining optimization enumerates path totals using a closed exact
availability formula.  For a fixed number of paths it is polynomial in the
numerical trial budget and pseudopolynomial when the budget is binary encoded.

Status: prospective protocol prepared after a primary-source audit.  No fresh
outcome may be computed until the implementation commit and
`registration_v0_25.json` are committed.

Read:

1. `PRIOR_ART_GATE_v0_25.md`;
2. `THEORY_DRAFT_v0_25.md`;
3. `DEVELOPMENT_NOTE_v0_25.md`; and
4. `protocol_v0_25.json`.

The registration/execution sequence is deliberately two-stage:

```text
python register_v0_25.py --output registration_v0_25.json
python run_verification_v0_25.py \
  --registration registration_v0_25.json \
  --output-dir artifacts_v0_25
```

The first command is run and committed before the second.  The fresh cells in
the protocol were selected without reading their formula values or
optimizers.
