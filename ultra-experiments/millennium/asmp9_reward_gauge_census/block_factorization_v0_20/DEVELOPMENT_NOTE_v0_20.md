# ASMP-9 v0.20 development note

Status: development-only. Nothing in this directory is registered or
claim-eligible yet.

## Candidate result

The finite residual-liveness event inherited from v0.17-v0.19 decomposes over
the nontrivial vertex-biconnected edge blocks of the original comparison
graph. Under independent edge responses, exact availability is the product of
the block-local availabilities. A rectangular endpoint-label minimum also
separates over blocks.

This would extend v0.19.2 from cactus cycles to arbitrary biconnected blocks
only at the *between-block* level. It does not solve or classify the exact
finite-design problem inside a block with overlapping cycles.

## Burned development checks

Run from the repository root:

```powershell
python -m pytest ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\test_block_factorization.py -q
python ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\run_development_census.py
```

Observed:

- 7 tests passed;
- 98,415 ternary states across three hand graphs, zero liveness mismatches;
- 636,606 ternary states across 96 NetworkX atlas graphs, zero liveness
  mismatches;
- all 96 Tarjan edge-block partitions matched NetworkX, including eight
  multiblock graphs;
- one exact rational availability calculation matched its block product:
  `7752548918073600 / 45949729863572161`;
- the multiple-articulation hostile test passed exhaustively over 59,049
  states;
- the bridge-separated cyclic-components test passed exhaustively and
  confirmed that all three bridge statuses are irrelevant; and
- a theta graph remains one irreducible biconnected block, so the
  factorization creates no false within-block simplification.

Receipt:

```text
artifacts_v0_20/development_census.json
SHA-256 ba0a768ff6179257196c91e161af2b17f6185965553ea725172af974fdba17ac
```

That receipt binds the development implementation committed at
`d7a235ed6dcd8f141dada5d7432c3603758199f3`. Later implementation hardening
does not retroactively rewrite it.

Every graph, allocation, label vector, and probability cell used by these
checks is burned and must be excluded from any registered run.

## Burned resource proxy

The prospective exact design gate uses blocks with 8 and 3 edges and one
trial above the positive-count floor. Before freezing the new cell, the same
algorithm was timed on an already-burned `K2,4` block joined to a triangle,
with the same block sizes and total budget:

```text
elapsed_seconds      2.607701
peak_resident_bytes  20,672,512
allocation_count     11
exact_match           true
```

The exact machine values and source hashes are in
`artifacts_v0_20/resource_pilot_v0_20.json`. The pilot is descriptive; the
registered 180-second/1-GiB gate remains binding and may still fail.

## Freeze blockers

Before registration:

1. independently restate and verify the block-excursion lemma;
2. choose fresh multiblock graphs outside the NetworkX atlas and hand-graph
   universe;
3. add an independent endpoint-label minimum factorization check, not merely
   one fixed-label product;
4. add a Bellman-versus-full-exhaustive allocation check on fresh small
   multiblock graphs;
5. include a one-block overlapping-cycle negative control showing that no
   computational benefit is claimed there; and
6. freeze a resource gate that does not create a hidden positive-outcome
   assumption.

## Claim boundary

This development evidence challenges the implementation and proof idea. It is
not prospective evidence, a complexity classification, a local reliability
design theorem for arbitrary biconnected blocks, an adaptive allocation
result, a behavioral reward-identification result, a general IRL theorem, or
an ASMP-9 resolution.
