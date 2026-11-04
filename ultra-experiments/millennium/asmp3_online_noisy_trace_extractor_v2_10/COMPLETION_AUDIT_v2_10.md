# ASMP-3 online noisy-trace extractor completion audit v2.10

```text
parent v2.9 replay result = preserved but no longer required
actual noisy-trace binding = frozen
candidate-only ideal revalidation = implemented
strategy restart = not required
ideal execution replay = not required
adaptive query policies = 2,355
noisy executions = 1,144,000
decoded semantic queries = 3,423,680
repeated-class executions = 889,856
all-correct rejections = 107,728
all-correct extraction misses = 0
invalid noisy candidates = 499,952
invalid candidates safely failed = 499,952
invalid emitted witnesses = 0
probability tables = 53,129
probability-bound violations = 0
sharp equality tables = 1,770
one-shot erased-state rows = 18
contract mutants rejected = 8/8
positive interaction modes accepted = 2/2
parent composition rows = 12/12
producer gates = 10/10
clean-room checks = 10/10
claim scope changed = no
```

## Closed in this release

The finder no longer needs to replay or restart a dishonest strategy.  It uses
one actual noisy execution, extracts the logged rejection candidate, evaluates
`H` only on that candidate, and returns it only after the declared `Refute`
relation succeeds again.  This is Las Vegas-valid on every path and succeeds
with probability at least `1-s-delta_q`.

The exact five-event probability enumeration proves the bound and its
sharpness.  The adaptive implementation audit covers every error pattern, and
the erased-state family confirms that the algorithm remains valid when all
counterfactual strategy state is destroyed.

## Remaining boundary

The theorem still requires public trace-complete binding on actual noisy
rejections, candidate-only ideal evaluation, decidable rechecking, and a joint
adaptive path-error bound.  The current typed successor does not mandate these
operational clauses.  Persistent/adversarial correlation, universal resource
lower bounds, the normative interface choice, and external reproduction remain
outside the certificate.

This is a broader normal form than v2.9, not another extension of an exhausted
finite parity or coupling grid.
