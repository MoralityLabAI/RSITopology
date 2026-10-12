# ASMP-9 conditional-fiber direct-fiber repair v0.13.2

## Cause

The v0.13.1 exact-power calculation was no longer the bottleneck. Before
calling it, the verification runner used the generic fiber enumerator to
construct the zero-balance fiber of a consistently oriented simple cycle.
For the fresh `k=18`, `n=3` formula check, that enumerated `4^18` ambient
count vectors even though the registered theorem proves that only four can
have zero vertex balance.

Both v0.13 and v0.13.1 therefore ended resource-unavailable without emitting
scientific outputs. No gate or fresh-cell result was read from either attempt.

## Repair

For a consistently oriented `k`-cycle with equal edge trial count `n`,
v0.13.2 constructs the proven fiber directly:

```text
F_0 = {(z,...,z) : z=0,...,n}.
```

The streaming exact conditional test introduced in v0.13.1 is otherwise
unchanged.

## Scientific invariants

This repair changes no theorem, graph, sample count, odds ratio, alpha,
power band, gate, success criterion, claim boundary, or resource limit. It is
an implementation repair only.

## Pre-registration checks

Before registration, direct and exhaustive fiber construction must agree on
all burned cells

```text
k in {3,4,6,8}
n in {1,2,3}.
```

The v0.13.2 power path must also reproduce v0.13.1 on a burned exact-power
cell and complete the largest burned preflight analog without using a GPU.

