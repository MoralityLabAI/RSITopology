# Independent arithmetic and receipt audit v0.80

## Audit status

**Pass.** The negative gate verdict is reproducible from the imported raw
rows without importing the experiment module.

## Checks

1. Recomputed all six hashes named by `execution_receipt.json`.
2. Confirmed byte identity of primary/replay `response_rows.jsonl`.
3. Confirmed byte identity of primary/replay `result.json`.
4. Parsed all 60 response rows.
5. Independently recomputed every Jeffreys-corrected logit margin estimate.
6. Recomputed the maximum R0 error and all sign decisions.
7. Recomputed the maximum raw shaping leakage.
8. Recomputed the Hellinger union bound independently.
9. Recomputed the accumulated iid TV penalty.
10. Confirmed the fixed sequence:

```text
W0 pass
I0 pass
R0 fail
L0 not_evaluated
M0 not_evaluated
```

## Numeric reconciliation

| Quantity | Independent recomputation | Runner |
|---|---:|---:|
| Maximum R0 error | 0.24483317010653805 | 0.24483317010653805 |
| All signs correct | true | true |
| Maximum raw leakage | 0.072265625 | 0.072265625 |
| Raw Hellinger bound | 0.13200188923004655 | 0.13200188923003764 |
| TV penalty | 0.01524271249739828 | 0.01524271249739828 |

The `8.9e-15` Hellinger difference is ordinary floating evaluation-order
roundoff and is far from any decision boundary.

## Provenance

External source directory:

```text
D:\Research_Engine\runs\asmp9_physical_target_interface_v0_80_20260729
```

The prereveal commit was already present on the remote branch before the
external receipt was created.

## Claim boundary

This audit verifies internal arithmetic, chronology, replay, and file
integrity. It is not an independent implementation of the response generator
and does not expand the scientific claim.
