# ASMP-9 physical dynamic bridge v0.67 registration decision

## Decision

```text
register_construction_then_confirmation
```

The protocol, scenario universe, code, tokenizer contract, arms, estimands,
construction calibration formulas, resource caps, and claim boundary are
frozen before construction inference.

This is a two-stage registration:

1. The construction registration binds the execution environment, exact model
   and tokenizer files, sources, and construction split.
2. The confirmation registration is impossible until a completed construction
   analysis receipt exists. It binds that receipt, the exact construction
   records, calibration, numeric envelopes, and transition map before any
   confirmation inference.

Changing the source, scenario, model bytes, tokenizer, resource contract, or
threshold derivation requires a new version. A construction failure is a
result of this version; it is not permission to tune v0.67.

## Why registration is warranted

The predecessor v0.66 deliberately stayed unregistered because its finite
transducer theorem was classical. Version v0.67 crosses the registered
boundary requested there: it tests a model response system, uses disjoint
scenario pairs, can return `latent_state_model_not_established`, and separates
context effect, terminal response, created consensus, and transducer replay.

## Evidence status

At freeze time:

- no Qwen score records exist for this protocol;
- no construction threshold has been computed;
- no confirmation registration can yet exist; and
- synthetic unit tests validate only the instrument logic.

Registration makes future outcomes claim-eligible within the written boundary.
It is not evidence that any scientific endpoint passes.
