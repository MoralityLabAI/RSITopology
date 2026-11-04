# ASMP-9 v0.38 decision-relative access result

## Verdict

`finite_decision_relative_access_threshold_established`

All eight registered gates passed on all six prospectively sealed cells. In
this finite reward/query grammar:

- deleting either target query costs exactly half its response-probability
  gap in target-relative deficiency;
- both target queries together are exactly decision-sufficient relative to
  full access;
- a target-independent query revealing the constant-shift reward
  representative has zero target decision value; and
- omitting that same query costs `1/2` under full expanded-parameter
  reconstruction.

This is an exact access threshold for the registered grammar, not a
resolution of ASMP-9.

## Chronology and binding

- implementation commit:
  `551f9b4addc90709718a358a4f76965673e14cdc`
- registration commit:
  `662c127f0e0d7a3f5268d2c7ce3f7ea5b1a91533`
- registration SHA-256:
  `c8d106eb2181ee561c5509f3af8ccf1309cf7aaf9ccb7c9fb8047b88c8f14a99`
- result content SHA-256:
  `c9f2ac95179813f6f416c0b6d7bc1d3ddde339ee94771c80fcfeb7da70a300ba`
- result file SHA-256:
  `a21a102bfede8dba771292520f8c2161ba2479b209d2ae937f606721f5e7689b`

The registration and its fifteen sealed input hashes were pushed before the
confirmation executor was invoked.

## Exact confirmation results

The nuisance-bias rows were exactly identical for each strength, as predicted.

| `(high,low)` | `gap/2` | One-query `delta_D` | No-query `delta_D` | One-query `G_D` |
| --- | ---: | ---: | ---: | ---: |
| `(5/7,2/7)` | `3/14` | `3/14` | `12/49` | `5/36` |
| `(7/8,1/8)` | `3/8` | `3/8` | `15/32` | `14/45` |
| `(5/8,3/8)` | `1/8` | `1/8` | `13/96` | `10/143` |

For both nuisance laws, `P(xi=1)=1/2` and `P(xi=1)=2/3`:

```text
delta_D(both target queries, full access) = 0
delta(target pair, target pair + gauge ancillary) = 0
delta(target pair + gauge ancillary, target pair) = 0
delta_D(gauge only, full access)
  = delta_D(no queries, full access)
delta_full(target pair, full access) = 1/2.
```

The optimized minimax value gap was strictly smaller than the rule-uniform
target-relative deficiency in all six cells. This confirms that `G_D` is a
coarser operational summary and cannot replace the rule-by-rule instrument.

## Access threshold

Let `gap=high-low`.

- For every `epsilon < gap/2`, both target queries are necessary and
  sufficient.
- At `epsilon=gap/2`, either single target query is inclusion-minimal.
- The no-query and gauge-only families remain strictly above the boundary.
- The gauge query is absent from every inclusion-minimal target-relative
  family, despite being necessary for zero expanded-parameter deficiency.

This is the exact distinction ASMP-9 needs in finite form: access sufficient
for downstream decisions can be strictly weaker than access sufficient to
reconstruct the raw reward representative.

## Gates

| Gate | Registered requirement | Result |
| --- | --- | --- |
| P0 | exact solver and definition preflight | pass |
| S0 | all sealed hashes match | pass |
| R0 | exact six-cell universe | pass |
| T0 | deletion cost equals `gap/2` | pass |
| G0 | target-independent gauge observation is ancillary | pass |
| E0 | expanded missing-gauge deficiency equals `1/2` | pass |
| A0 | no-query family remains above the boundary | pass |
| RESOURCE | wall/RAM ceilings respected | pass |

## Verification and resources

- execution time: `88.9350269` seconds;
- peak working set: `75,509,760` bytes (`72.01 MiB`);
- ceiling: `600` seconds and `1 GiB`;
- preflight: `16 passed`;
- registered cells independently checked: `6`;
- exact replay: byte-identical mathematical rows and gate values;
- verifier SHA-256:
  `89d8b8569776ae12e7cfa5a566f18995dc01e331b102b0e390660775034e0aee`.

## Post-result observation

Because every registered pair also satisfied `high+low=1`, the no-query
values exposed the exact pattern

```text
delta_D(no queries, full access)
  = gap/2 + gap^2/6.
```

That expression was not a registered v0.38 prediction and is not used to
claim a gate pass. A separate post-run note proves it for the symmetric
family and marks it as requiring disjoint confirmation if promoted to an
empirical theorem check.

## What changed in the ASMP-9 obligation ledger

Before v0.38, the program had:

1. a zero-error nuisance-component quotient that was too coarse for
   quantitative risk; and
2. full expanded-parameter deficiency that could overprice nuisance.

Version v0.38 supplies the missing finite middle object and an exact threshold
inside one reward grammar:

```text
zero-error quotient
  < target-relative rule/risk comparison
  < full target-by-nuisance reconstruction.
```

The remaining resolution work is substantial: correlated and strategic
nuisance, adaptive interventions, larger policy/reward classes, unknown
links, misspecification, and a valid physical measurement channel.

## Claim boundary

The comparison theory is classical. The result establishes a finite
specialization with three policies, three target classes, symmetric binary
queries, constant-shift gauge, and target-independent nuisance. It is not
evidence about a language model, human values, recursive self-improvement, or
the general necessary-and-sufficient access characterization demanded by
ASMP-9.

