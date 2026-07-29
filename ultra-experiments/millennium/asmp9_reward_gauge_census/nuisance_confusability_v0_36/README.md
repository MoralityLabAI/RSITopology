# ASMP-9 nuisance-confusability theorem seed v0.36

This bounded exact experiment tests a correction to the first ASMP-9
resolution obligation. A fixed reward symmetry group produces an orbit
equivalence relation. An unknown response nuisance can instead produce a
pairwise confusability relation that is reflexive and symmetric but
nontransitive. In that regime, no group quotient can be the complete
identifiability object.

The finite theorem uses deterministic observation tables

```text
f_q : Theta x H -> Y
```

and compares one nuisance shared across queries with a nuisance that resets
independently. Its primary planted construction uses two mirrored threshold
queries. Each query alone is insufficient; together they identify all three
target values only when the unknown threshold is stable across interventions.

## Files

- `THEOREM_NOTE_v0_36.md`: definitions and proofs;
- `PRIOR_ART_v0_36.md`: zero-error, compound-channel, measurement-theory, and
  reward-identifiability boundary;
- `PROTOCOL_v0_36.json`: prospective census and five frozen gates;
- `confusability.py`: reusable exact definitions;
- `run_census.py`: registration-bound exhaustive runner;
- `verify_result.py`: import-independent result verifier; and
- `test_confusability.py`: prereveal unit and planted-control tests.

## Frozen execution scale

- 64 one-query binary tables on `3 x 2` target/nuisance cells;
- 4,096 ordered pairs of such tables;
- both shared and reset nuisance semantics;
- all 27 labelled three-value decision maps per channel; and
- all registered smaller-cardinality controls.

The census must not run until `REGISTRATION_v0_36.json` has been generated,
committed, and pushed.

## Claim boundary

Confusability graphs, zero-error decoding, compound channels, and interval
scale transformations are classical. This experiment is a finite access
ledger and a correction to the object demanded by ASMP-9. It is not a general
stochastic or adaptive theorem, behavioral evidence, reward recovery, or a
resolution of ASMP-9.
