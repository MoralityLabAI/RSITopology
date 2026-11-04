# ASMP-3 oracle-parametric replay completion audit v2.9

```text
parent v2.8 trace-binding certificate = preserved
oracle-parametric runtime contract = frozen
direct ideal-law compiler = proved
fresh-seed marginal sufficiency = proved and exhaustively checked
adaptive tree executions = 144,096
semantic queries replayed = 429,984
repeated-class executions = 111,552
compiler mismatches = 0
invalid trace-bound executions = 0
seed-law comparisons = 29,056
seed marginal mismatches = 0
contract mutants rejected = 8/8
positive runtime modes accepted = 2/2
transcript-only firewall rows = 19
v2.8 composition rows retained = 12/12
producer gates = 10/10
clean-room checks = 10/10
claim scope changed = no
```

## What closes

Efficient ideal-semantic replay is derived for total restartable runtimes whose
only semantic input is a callable, dependency-injected provider.  The compiler
uses a fresh nonsemantic seed from the declared sampler; it need not recover a
seed from a prior noisy run.  All kernel, verifier, ideal-evaluation, tracing,
and local-emulation costs are explicit.

Together with v2.8 trace binding and v2.7 coupling, every registered composition
row yields a positive finder margin `alpha >= 1-s-delta_q`.

## What the firewall closes

A noisy recording can stop on an erroneous branch and contain no information
about the ideal continuation.  The marker family makes `N` such continuations
indistinguishable from the recording while a restartable ideal-mode execution
exposes the correct one.  Therefore transcript possession is not a substitute
for runtime access.

## What remains open

The current ASMP-3 definition does not mandate restartable kernels, live
ideal-mode interaction, ideal-provider access for the finder, trace-complete
binding, or a cost convention for emulated adversaries.  Those are normative
interface choices.  One-shot/stateful strategies, stronger correlation models,
universal interactive lower bounds, and external expert reproduction remain
outside this certificate.

This is a genuinely broader normal-form theorem and a matching separation, not
an extension of the parity or finite-coupling grids that v2.6 froze.
