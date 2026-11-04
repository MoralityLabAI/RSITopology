# ASMP-9 v0.10 execution-label note

## Chronology

The development commit `b9d2cac` contains only burned checks:

- deterministic two-action kernels at `S=2` and `S=3`;
- cyclic structured cells through `S=16`; and
- the 64 query graphs on four reward coordinates.

The prospective implementation and protocol were frozen at:

```text
56126229126c8f6cfdacf366deef2b52b1762d5f
```

The separate registration commit is:

```text
f54cbb1402a0b0e95c91b5fb43c94eb2463d2598
```

Its registration file hashes thirteen frozen inputs. The runner required the
repository `HEAD` to equal the commit containing that registration, required
the tracked tree to be clean, checked every sealed hash, and checked that the
implementation commit was an ancestor before constructing any fresh cell.

Only then were the claim-eligible cells executed:

- all 65,536 deterministic `S=4, A=2` kernels;
- 4,096 seeded rational stochastic kernels;
- structured state counts `17..32`; and
- all 32,768 query graphs on six coordinates.

## Replay label

The primary artifact directory is `artifacts_v0_10`. A second clean execution
was used only as a deterministic replay check. Its Markdown report was
byte-identical, and every scientific field in the JSON result was identical
after removing the inherently variable elapsed-time and peak-resident-memory
fields.

The frozen deterministic-policy helper used the analytic action-gap formula.
After the run, a separate verifier reconstructed both kernels and solved all
64 fixed-policy Bellman systems independently in exact rational arithmetic.
That diagnostic passed. It is labelled post-run verification and is not
counted among the eleven preregistered gates.

## Claim label

`finite_mdp_environment_access_geometry_verified` means that all eleven
registered finite gates passed. It is not a claim of novel general IRL theory
and not an ASMP-9 resolution.
