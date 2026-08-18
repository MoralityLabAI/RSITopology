# ASMP-9 context-gluing resource repair v0.11.1

## Reason

The registered v0.11 implementation exceeded its 360-second wall-time cap and
was terminated without producing a scientific artifact. The literal tuple
loop recomputed exact rational incidence ranks for all three constituent
graphs and their union in every one of 262,144 tuples.

## Frozen-equivalent optimization

There are only 64 simple graphs on four labelled items. Version v0.11.1
precomputes, once for each graph:

- exact incidence rank by rational Gaussian elimination;
- connected-component count;
- edge count; and
- cycle rank.

For each ordered graph triple, the labelled-union incidence rank equals the
rank of the simple union graph because duplicate labelled rows do not change
row rank. The optimized loop therefore uses:

```text
direct rank difference
  = sum_context precomputed_rank(mask_c)
      - precomputed_rank(bitwise_union(mask_c))
```

and independently computes:

```text
mixed cycle rank
  = labelled_edge_count - item_count
      + components(bitwise_union(mask_c))
      - sum_context local_cycle_rank(mask_c).
```

The scientific tuple, random-cell, minimality, status, gate, and resource
specifications are unchanged. Exact equality between the optimized and
literal implementations is tested over every burned cell through the full
four-item/two-context census.

## Claim boundary

This is an implementation repair, not a protocol relaxation and not a new
scientific hypothesis.
