# ASMP-9 v0.68.2.1 local confirmation result

Status: **scientific gates rederived; execution cleanup invalid**.

The untouched v0.68.1 confirmation split was scored once on the registered
Qwen3.5-0.8B-Instruct bytes. This was inference only: no model was trained,
fine-tuned, or updated. The local RTX 3050 completed all 528 registered
singleton scores under the frozen batch, prompt, memory, temperature, and
timeout limits.

The frozen analyzer returned
`confirmation_local_and_global_established`, and an independent post-run
implementation rederived that decision from the 528 sealed records. The
Windows wrapper nevertheless returned `cleanup_invalid` because system-wide
page-file usage rose by 3 MB while the owned job was live. The v0.68.2
resource amendment registered a zero-increase rule, so this release preserves
the invalid cleanup status. It does not waive the rule on the ground that the
increase was small.

## Chronology and binding

- prereveal source/repair commit:
  `866c2e684f2b3402387469036de73c13826590f3`
- repaired execution-intent commit:
  `cd3a1dca295709812ba6fe61ce7650d913d50a9a`
- registration SHA-256:
  `b4dd543caf890e4980f94f2a98340320db29fe03c74e4cbe28039ec57dabf90b`
- authorization SHA-256:
  `91bbdd4d393e94ff491c0dc87f731a01d9ac2c51a70131c8a963980b87fadc2f`
- registered score-job SHA-256:
  `097f9cad620a8de161d1e611d2d1e1c12b3b6d6d35c9298913d824b9d9a7a300`
- model-weight SHA-256:
  `04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696`
- sealed records SHA-256:
  `ea43e8ed6b442830c977ddc798ca423c74c4bdc4b8176f640d5a8e698c2ebdcb`

The execution intent containing the exact registration and authorization
hashes was pushed before the first confirmation forward pass.

## Scientific readout

| Quantity | Result |
| --- | ---: |
| scored records | 528 / 528 |
| semantic inputs | 264 |
| exact-repeat failures | 0 |
| scenario successes | 12 / 12 |
| frozen endpoint epsilon | 0.0156353893 |
| median worst-direction specificity | 0.28125 |
| mean scenario-mean specificity | 0.9153645805 |
| confirmation shared-effect intersection | [0.6874895809, 0.7656353297] |
| intersection margin | 0.0781457488 |
| confirmation cells intersecting sealed construction interval | 24 / 24 |

Thus the registered local response-family rule and the registered global
construction-overlap rule both pass on this finite confirmation registry.
The independent audit agrees with the frozen analyzer on every recomputed
quantity and decision.

## Resource and cleanup readout

| Quantity | Result |
| --- | ---: |
| runner elapsed time | 322.78 s |
| runner exit code | 0 |
| analysis exit code | 0 |
| peak runner CUDA allocation | 1,562.58 MB |
| peak wrapper-observed GPU allocation | 2,031 MB |
| peak GPU temperature | 86 C |
| peak owned working set | 2,529.71 MB |
| lingering owned processes | 0 |
| post-cleanup GPU allocation | 0 MB |
| cleanup script | passed |
| system page-file increase | 3 MB |
| wrapper status | `cleanup_invalid` |

The page-file counter is system-wide, so the receipt does not establish that
the owned Python job caused the 3 MB movement. That limitation does not permit
a post-outcome relaxation of the registered zero-increase rule.

## Decision

Two statements must remain separate:

1. **Scientific readout:** the frozen and independently rederived finite-
   registry gates say `confirmation_local_and_global_established`.
2. **Execution-envelope readout:** this is not a fully clean zero-swap local
   execution because the registered cleanup rule returned `cleanup_invalid`.

The existing confirmation outcomes are now read. Re-running the same holdout
under a relaxed cleanup threshold would not restore prereveal status. A future
fully clean resource confirmation requires a versioned purpose and an
untouched holdout or other prospectively registered replication universe.

## Claim boundary

This result concerns exact nuisance-quotiented expressed-response contrasts
in one frozen 0.8B model on one finite scenario registry. It does not identify
a value, moral truth, human preference, persistent reward-shaping orbit,
recursive-improvement mechanism, or ASMP-9 resolution. It is also not evidence
that a larger Qwen must be trained: the registered 0.8B inference workload
completed on the local 4 GB RTX 3050.

