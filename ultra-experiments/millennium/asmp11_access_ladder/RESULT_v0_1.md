# ASMP-11 Boolean access-ladder result v0.1

## Verdict

`finite_access_ladder_established`

All eight frozen gates passed over 114 planted mechanisms and 245
degree/access cells.

## Exact boundary

For a planted degree-`k` parity mechanism and access class `A_(r,s)`—Walsh
observation through order `r` after fixing at most `s` parent coordinates—the
distinguishing advantage is exactly

```text
0  when r+s < k
1  when r+s >= k.
```

The minimum total resource `r+s` was therefore `2,3,4,5,6` for planted degrees
`2,3,4,5,6`. The result held separately on the interleaved construction and
held-out support/sign ensembles.

## What the two-resource view adds

Causal access substitutes for observation order: fixing one parent of a parity
reduces its remaining degree by one. But this algebraic trade is not a query
efficiency theorem. Under the registered **nonadaptive exhaustive** grammar,
the cheapest boundary point is always pure observation:

| Degree | Cheapest boundary `(r,s)` | Exhaustive queries | Pure causal `(0,k)` queries |
|---:|---:|---:|---:|
| 2 | (2,0) | 22 | 73 |
| 3 | (3,0) | 42 | 233 |
| 4 | (4,0) | 57 | 473 |
| 5 | (5,0) | 63 | 665 |
| 6 | (6,0) | 64 | 729 |

Thus “causal interventions expose hidden structure” and “causal interventions
are cheaper” are distinct claims. The first is exact in this seed; the second
is false only under its nonadaptive exhaustive query accounting. No adaptive
query lower bound was proved.

## Controls

- All paired clean and planted mechanisms produce identical benign actions.
- Moving the same coefficient between dormant and action channels preserves
  the unlabelled coefficient-magnitude spectrum.
- Every coordinatewise stronger access class contains every observation from
  the weaker class; no frontier level is created solely by relabeling a
  simulable interface.
- Every below-boundary cell is exactly blind, and every on/above-boundary cell
  is exactly detecting.

## Interpretation

The experiment supplies a sharp planted negative control for a future
conditional-defection detector and a machine-checkable access-lattice schema.
For Silico or the identity-attestation harness, a detector should report both
its observation order and causal-intervention budget, plus the actual query
count. Collapsing these into a single “white-box access” label discards the
measured boundary.

## Prior art

The registered [prior-art boundary](PRIOR_ART_v0_1.md) and the additive
[access-model addendum](PRIOR_ART_ADDENDUM_v0_1.md) position this seed beneath
the Boolean-Fourier/SQ parity literature, noisy-parity/LPN work, Angluin et
al.'s value-injection query model, and existing white-box-undetectability
constructions. In particular, the intervention coordinate has a direct circuit-
learning ancestor and is not introduced here as a novel query model.

## Claim boundary

The threshold is a direct Boolean-Fourier restriction fact, not a novel
cryptographic theorem. The planted parity is transparent and is not a rare
linguistic trigger. Raw full-weight access, obfuscation, learned features,
finite-sample noise, and real conditional defection are not modeled. This does
not show that interpretability access defeats the white-box-undetectability
constructions in the cited literature, and it does not resolve proposed
`ASMP-11`.
