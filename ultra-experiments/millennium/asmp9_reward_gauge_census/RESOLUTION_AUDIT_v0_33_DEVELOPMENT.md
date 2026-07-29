# ASMP-9 resolution audit after v0.33 development

## Status

**Development audit only. ASMP-9 remains unresolved.**

Version v0.33 has not been prospectively registered. Its calculations can
shape a successor protocol but are not claim-eligible evidence.

## Progress since v0.32

The v0.32 audit named sharp joint stochastic policy complexity as the next
load-bearing obligation. Development work now supplies three pieces.

### 1. Decision quotient

A finite controlled-sensing model treats reward-gauge aliases as one answer
class when they induce the same registered policy. Decision identifiability
holds exactly when every answer-changing alternative differs under some
query. Full parameter identification is intentionally stronger and can fail
without harming the declared decision.

### 2. Native channel ledger

A finite fixture imported from sealed v0.28-v0.32 objects contains:

- a reward-changing alternative;
- a mechanics-changing alternative;
- a mixture-validity failure returning `not_certified`; and
- an observationally identical same-policy gauge alias.

Return, mechanics, and mixture-audit channels are each necessary. Under the
temporary equal-cost convention, the mixture audit receives most of the
max-min allocation because its planted violation is much smaller. This is a
development sensitivity finding, not an operational allocation.

### 3. Semantic-coupling quotient

The v0.31 and v0.32 matrix composition is now exact. For coupling `K`:

```text
policy effect = Q L K C;
vec(policy effect) = (transpose(C) kron (Q L)) vec(K).
```

The sealed objects give:

```text
raw coupling dimension          48
decision-relevant dimension     18
decision-null gauge dimension   30
```

Thus a successor need not identify a unique 48-coordinate coupling. It must
identify the 18-dimensional quotient relevant to the full registered policy
family. A two-policy control reduces that target to six dimensions, showing
that the quotient depends on the declared answer family.

## What remains load-bearing

### A. Coupling acquisition

Freeze a physically meaningful query grammar for estimating the coupling.
Compute its exact row space before outcomes. The grammar is adequate only if
its induced rows span the 18-dimensional decision quotient; otherwise provide
an explicit decision-changing indistinguishability witness.

### B. Finite-sample upper bound

The current characteristic-time expression is a classical lower bound.
Supply a registered stopping rule and a nonasymptotic error/sample guarantee,
or label the result only as a design criterion.

### C. Cost and dependence model

Freeze query costs, observation dependence, support conditions, and the
handling of infinite KL. The current equal-cost, independent finite laws are
not deployment models.

### D. Coarser mechanics and behavioral misspecification

The v0.32 mixture-affine interface, exact registered occupancies, and finite
hypothesis registry remain strong assumptions. Coarser environment
equivalence and general non-expected-utility or strategic demonstrators are
still open.

## Next falsifiable fork

The next protocol should be capable of returning either:

```text
quotient_spanned
```

with a rank-18 construction and held-out reconstruction bound, or:

```text
decision_access_insufficient
```

with a nonzero coupling perturbation that is invisible to every admitted
query but changes `Q L K C`.

Either outcome advances the access classification. Neither outcome alone
resolves ASMP-9.
