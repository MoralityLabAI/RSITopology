# ASMP-9 v0.34 burned-pilot design

## Status

**Prospective design. The pilot is calibration data, not confirmation data.**

### v0.34.1 instrument amendment

The first registered v0.34 engineering smoke stopped before any choice receipt:
the raw instruction prompt allowed Qwen's positive-mass `<think>` control token
to precede the forced answer. The fail-closed extractor rejected it. The
v0.34.1 amendment wraps every already-frozen user query in the checkpoint's
documented chat template and inserts the explicit empty-thinking prefix:

```text
<|im_start|>assistant
<think>

</think>

```

The answer distribution is still required to contain exactly `A` and `B`.
No control token is discarded, renormalized, or interpreted as an answer.

The exact v0.33 result leaves one empirical question before a physical
quotient claim can be registered: can the preferred 18 scalar probes be
implemented as stable model-facing choices with a meaningful local
perturbation coordinate?

This pilot operationalizes that question without relabeling any prior Qwen
receipt.

## Registered choice object

The oracle is the frozen next-token distribution over the grammar `{A,B}` for
Qwen3.5-0.8B Q4_K_M. Every query is evaluated twice with the target option
first and second. The recorded scalar is the order-corrected log odds of the
target against its comparator.

The semantic rectangle has three durations by four service-improvement
levels. Every cell is measured against one common best/worst anchor through
five standard-gamble probabilities. Six disjoint compound lotteries audit
whether the same ruler is approximately mixture-affine.

The policy arm uses the three v0.33 policy contrasts and six preferred
behavioral cells. Its perturbation norm is not a hidden activation magnitude:
it is the explicitly stated probability that the candidate policy additionally
yields the registered cell consequence:

```text
norm in {0, 1/8, 1/4, 1/2}.
```

This makes the local secant question operational and independently
reproducible.

## Split and counts

Three paraphrase families are burned for calibration. Three additional
families are frozen but inaccessible to the pilot runner.

Per phase:

```text
standard gambles    12 cells x 5 probabilities x 2 orders x 3 families = 360
compound gambles     6 mixes x 5 probabilities x 2 orders x 3 families = 180
policy probes       18 probes x 4 norms x 2 orders x 3 families          = 432
total                                                                     972
```

The complete burned pilot uses two planned cold starts, for 1,944 receipts.
A bounded smoke may select a declared number of rows from each query type but
cannot be represented as the burned pilot.

## What the pilot may set

The pilot may inform, once and only once:

- an admissible common norm subset;
- cold-start and option-order repeatability tolerances;
- a simultaneous secant-error construction;
- prompt-family and replicate counts;
- the practical policy margin; and
- confirmation compute allocation.

It may not replace cells, policies, families, signs, anchors, mixture pairs, or
the preferred factorized basis after reading responses.

## Fail-closed interpretation

If the common ruler does not bracket enough cells, the compound-lottery
controls are not live, or any required factorized probe is indistinguishable
from its zero-probability sham across the pilot families, the physical
successor remains `not_established`. A pilot failure does not alter the exact
18-dimensional quotient theorem.

## Claim boundary

This pilot tests one explicit prompt-level access grammar on one quantized
small model. It cannot establish expected utility as a general model property,
identify a maximal reward-shaping group, validate the semantic content of the
registered policies, authorize downstream edits, or resolve ASMP-9.
