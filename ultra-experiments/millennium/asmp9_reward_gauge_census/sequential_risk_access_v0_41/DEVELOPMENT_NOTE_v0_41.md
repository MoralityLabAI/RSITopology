# ASMP-9 v0.41 burned-development note

## Correction found by the first run

The frozen development prediction for the two-query nonadaptive arm was:

```text
deficiency = 1/2.
```

That prediction treated the failure of every deterministic two-query sequence
as though one such sequence had to be selected globally. The v0.40/v0.41
access class allows randomization over deterministic policies. Convexifying
the imperfect open-loop sequences distributes their unresolved-pair errors
across targets and gives exact worst-target deficiency:

```text
deficiency = 1/4.
```

The main structural prediction survives:

```text
adaptive horizon 2      = 0
nonadaptive horizon 2   = 1/4
nonadaptive horizon 3   = 0.
```

This correction is scientifically useful. A decision-tree existence check
alone detects the zero/nonzero adaptivity gap, but it does not quantify
approximate access when randomized open-loop designs are allowed. The upper
risk-polytope compiler does.

## Status

This is burned development. The original prediction remains byte-visible in
`DEVELOPMENT_PROTOCOL_v0_41.json`. No registration or claim-eligible
confirmation has occurred.
