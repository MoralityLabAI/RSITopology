# Physical-capture availability audit for ASMP-9 v0.34

## Status

Read-only development audit, 2026-07-29. No outcome was generated.

## Finding

No existing local capture instantiates the v0.34 physical-acquisition object.

The ASMP-9 run directories currently present under
`D:/Research_Engine/runs` cover exact finite registrations such as contextual
gluing, conditional fibers, unconditional availability, and balanced
allocation. They contain no language-model standard-gamble or compound-lottery
capture.

The available Qwen0.8B directories cover different registered objects:

- controller/audit throughput and completion measurements for ASMP-8;
- projector tomography;
- VPD policy arcs; and
- lineage, percolation, rank-one, precision, and holonomy measurements.

Those runs do not contain the three objects required jointly here:

1. a common global standard-gamble ruler over the twelve v0.32 cells;
2. redundant compound-lottery prompts capable of falsifying mixture affinity;
3. the three selected policy-contrast readouts needed by the optimized
   factorized coupling basis.

Reinterpreting a holonomy edge, ASMP-8 audit completion, or VPD edit score as
one of these objects would change the estimand after outcomes and is
prohibited.

## Reusable infrastructure

The existing Qwen harnesses may contribute only outcome-independent machinery:

- model and tokenizer loading;
- deterministic prompt hashing and grouping;
- fixed-precision execution;
- resource caps and cleanup;
- JSONL receipt writing; and
- one-to-one sealed outcome joins.

Their scientific observations must not be pooled into v0.34.

## Minimum new capture schema

Before a pilot, every row must carry:

```text
model_hash
tokenizer_hash
checkpoint
precision
site
prompt_family
prompt_id
behavioral_cell_index
policy_contrast_index
intervention_norm
replicate
seed
response
```

The construction split must contain all 18 optimized
`behavioral_cell x policy_contrast` probes. Prompt-family and run-replicate
holdouts are mandatory. Mixture-affinity controls use disjoint prompts from
the policy-effect evaluation.

## Pilot obligation

A burned pilot may estimate:

- response variance and dependence;
- truncation and invalid-response rates;
- attainable intervention norms;
- sham-intervention scale; and
- secant/Jacobian disagreement.

It may not change the 18-probe basis, the exact span evaluator, or the
leave-one-out negative controls. The pilot's only legitimate output is a
versioned proposal for numeric E0-E3 thresholds and a compute estimate.

Until that pilot is designed and sealed, v0.34 remains unregistered and
unrun.
