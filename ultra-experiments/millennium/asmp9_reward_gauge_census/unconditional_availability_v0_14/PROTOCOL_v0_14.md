# ASMP-9 unconditional availability protocol v0.14

## Status

This protocol freezes a fresh exact finite verification of the v0.14 theorem.
The 135-cell development registry is burned and cannot satisfy any gate.

## Frozen theorem

For fixed finite cycle length `k`, trials per edge `n`, circulation odds
`R>1`, and conditional size `alpha`:

1. conditioning on vertex win balance removes every scalar-gradient nuisance;
2. the cycle fiber is informative exactly when `max(Y)-min(Y)<n`;
3. the exact conditional upper-tail test has size `alpha`;
4. unconditional excess power factors through informative fibers;
5. an unbounded scalar nuisance can make excess power converge to zero; and
6. a declared edge-probability interior gives a strictly positive uniform
   lower bound.

The frozen proof is [`THEOREM_v0_14.md`](THEOREM_v0_14.md).

## Fresh registry

The fresh Cartesian registry is:

```text
k in {6,7}
n in {1,2,3}
R in {1,5/4,7/4,5/2}
q in {1,3,12,64,1024}
alpha = 1/20.
```

The `R=1` arm is a null control. For `R>1`, `q=1` is the balanced nuisance and
`q=1024` is the registered extreme endpoint. The nuisance family is:

```text
s(q)=(q^(k-1),q^(-1),...,q^(-1)).
```

Every cell is evaluated by exact rational enumeration. No Monte Carlo
quantity enters a gate.

The matched positive arm is fixed before execution: every `R>1`, `q=1` cell
must satisfy the common edge-probability interior `epsilon=1/4`, and its
observed excess power must exceed the theorem's lower bound computed using
that fixed `epsilon`, not a fitted cell-specific threshold.

## Gates

- `G0_registration_binding`: every sealed hash matches and the registration
  commit is the clean execution head.
- `G1_fiber_partition_and_mass`: every fresh cell completes with positive
  fiber counts and normalized exact null and alternative mass.
- `G2_availability_formula`: the closed informative-fiber probability matches
  exhaustive enumeration in every cell.
- `G3_exact_conditional_size`: every fiber test has exact conditional size
  `1/20`.
- `G4_excess_factorization`: unconditional power minus size equals the
  informative-fiber decomposition in every cell.
- `G5_no_go_upper_bound`: every positive-alternative cell satisfies
  `0 < excess <= (1-alpha) P_alt(informative)`.
- `G6_interior_sufficiency`: every positive-alternative cell has positive
  cellwise quantities; additionally, every registered `q=1` positive-control
  cell satisfies the fixed `epsilon=1/4` interior and its observed excess is
  no smaller than the corresponding fixed-interior lower bound.
- `G7_null_control`: every `R=1` cell has power exactly `1/20`, zero excess,
  and zero minimum informative-fiber gain.
- `G8_extreme_nuisance_collapse`: for every `(k,n,R>1)` stratum, the
  `q=1024` informative probability and excess power are strictly below their
  `q=1` values, and the excess-power ratio is below `1/1000`.
- `G9_resource_and_scope`: the CPU-only run completes within 120 seconds and
  1 GiB, records all status telemetry, and preserves the claim boundary.

Every gate is binding. A failed or unavailable gate stops the registered
claim.

## Resource envelope

```text
CPU only
maximum wall time: 120 seconds
maximum peak resident memory: 1 GiB
```

The GPU is prohibited.

## Claim boundary

The registered result can verify an exact finite conditional/unconditional
access theorem on oriented cycles. It cannot establish that Bradley-Terry is
a valid human or model response law, certify scalarity from non-rejection,
cover unknown links or dependent responses, solve general IRL, or resolve
ASMP-9.
