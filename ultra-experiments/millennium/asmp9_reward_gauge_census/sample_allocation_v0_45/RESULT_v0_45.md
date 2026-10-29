# ASMP-9 v0.45 decision-directed sample-allocation result

## Verdict

**`decision_directed_sample_allocation_established`**

All twelve registered gates passed. Under the frozen shared-flip calibration
grammar, the exact integer allocation minimizing the robust deficiency
endpoint depends on the decision loss. A matched policy that uses every query
recovers uniform allocation.

This closes one finite allocation target from the v0.44 obligation matrix. It
does not establish general optimal design, a minimax confidence construction,
or resolution of ASMP-9.

## Frozen design

- Four targets and three binary queries `(root,left,right)`.
- Horizon two.
- One shared symmetric flip parameter per query.
- Known-target error indicators pooled within each query.
- Total acquisition budget `N=60`.
- Every query receives at least one sample.
- `alpha=0.05`.
- Binary method-of-types toll:

  ```text
  kappa(n) = ceil_1e-12(log(3(n+1)/0.05)/n).
  ```

- 1,711 labelled positive allocations per decision problem.
- 3,422 exact rational deficiency LP evaluations in total.

The `N=60` confirmation was registered after a disclosed, non-claim-eligible
`N=54` development census.

## Exact allocation results

| Decision problem | Unique exact optimum | Exact upper | Uniform allocation | Uniform upper | Relative improvement |
|---|---:|---:|---:|---:|---:|
| four-class identification | `(26,17,17)` | `0.589535161433` | `(20,20,20)` | `0.597447361697` | `1.324334%` |
| root-group loss | `(58,1,1)` | `0.265419024703` | `(20,20,20)` | `0.422459080858` | `37.172844%` |

The absolute improvements are:

```text
four-class : 0.007912200264
root-group : 0.157040056155
```

The allocations differ on the same channel library and sample budget because
the losses make different experiments decision-relevant. Four-way
identification needs both branch queries. Root-group loss can spend all but
the mandatory coverage samples on the root.

## Matched all-query control

The registered serial control uses every query exactly once. Its objective is

```text
kappa(n_root)+kappa(n_left)+kappa(n_right).
```

Across the same 1,711 integer allocations, its unique optimum was:

```text
(20,20,20).
```

Unequal allocation is therefore not an automatic output of the confidence
formula. It appears only when the registered policy/loss makes query
occupancy unequal.

## Constructive bound audit

The root-group closed form equaled the exact LP on all 1,711 allocations.

For classification, the simple perfect-policy bound was conservative on
1,325 of 1,711 allocations. Its maximum excess over the exact LP was:

```text
0.07504109039024635.
```

It underbounded the exact LP zero times and selected the same unique optimum.
This distinction is load-bearing: v0.45 establishes the optimum through the
exact census, not by pretending the convenient formula is globally exact.

Canonical exact-row hashes:

```text
classification:
4a72696cd42b0e5307190a964cf010cdee0166cd72ba338560c336208b02ce41

root-group:
9c95770c2cfe5b9aae6a7ecee8ae0475be676150d178bfe3e915baeeafa9cf52
```

## Two-point lower benchmark

For every distinct count in the optimal and uniform designs, the run
exhausted symmetric Bernoulli alternatives

```text
p_minus=1/2-d, p_plus=1/2+d, d=j/200.
```

The largest `d` whose exact equal-prior Bayes error remained strictly above
5% was:

| Samples | Certified radius lower bound |
|---:|---:|
| 1 | `0.445` |
| 17 | `0.185` |
| 20 | `0.175` |
| 26 | `0.155` |
| 58 | `0.105` |

At the next grid point every Bayes error was at most 5%. These are lower
bounds on a uniformly valid Bernoulli parameter-confidence radius, not direct
lower bounds on the final deficiency values. They do not match the
constructive KL/Pinsker certificate. Consequently the finite allocation is
exact for the registered upper-bound objective, but the underlying statistical
radius remains constructive rather than minimax.

## Gates

| Gate | Result |
|---|---|
| `P0`: exactly 21 preregistration tests | pass |
| `S0`: every sealed and inherited source hash | pass |
| `U0`: exact budget/query/allocation universe | pass |
| `K0`: 60 positive strictly decreasing KL tolls | pass |
| `E0`: 3,422 exact LP rows | pass |
| `B0`: zero constructive underbounds | pass |
| `A0`: predicted classification optimum and >1% gain | pass |
| `D0`: predicted root-group optimum and >35% gain | pass |
| `C0`: unique uniform serial-control optimum | pass |
| `L0`: exact two-point grid boundaries | pass |
| `R0`: decision problems select different optima | pass |
| `RESOURCE`: time, memory, worker count | pass |

Execution used 265.70 seconds and a peak aggregate working set of 395,005,952
bytes, below the registered ceilings of 420 seconds and 1.25 GiB. Independent
replay reproduced every scientific field, gate, and canonical row hash.

## What changed

Version v0.44 established that uncertainty should remain attached to each
policy risk generator. Version v0.45 now makes acquisition itself
decision-relative:

```text
loss type
  -> policy query occupancy
  -> sample allocation
  -> simultaneous KL tolls
  -> robust deficiency endpoint.
```

The result is exact only after fixing the finite channel, policy horizon,
shared-parameter pooling grammar, confidence construction, decision loss, and
sample budget.

## Provenance

- Implementation commit:
  `4c28948641cb7f41849b14204cb509fe6ddf5b3a`
- Registration commit:
  `e75a6d8b1401a58b8cf0eee07248ac14c4381be1`
- Registration SHA-256:
  `74cb1dcc643f1a3a2b44b440bd11bb9ae50658fdede061a2226fb0fcfe6ff8a4`

## Claim boundary

Version v0.45 proves an exact integer allocation result for one finite iid
shared-flip calibration grammar and one inherited robust-deficiency objective.
It does not prove target-dependent nonparametric cell allocation, optimal
simultaneous confidence constants, a general minimax deficiency modulus,
efficient policy compilation, strategic-source robustness, validity of a real
preference channel, or resolution of ASMP-9.
