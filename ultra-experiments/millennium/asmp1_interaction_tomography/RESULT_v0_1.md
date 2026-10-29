# Interaction-order tomography result v0.1

## Outcome

All nine registered gates passed. The result supplies an exact constructive
successor to the singleton-intervention obstruction:

1. interventions fixing at most `r` parents recover exactly interaction
   coordinates of order at most `r`;
2. labelled and symmetry-quotiented identifiability have different sharp
   thresholds; and
3. the cheapest exact design is substantially less well-conditioned than the
   redundant design, separating exact identifiability from stable estimation.

The universal statements are proved in `THEOREM_v0_1.md`. The enumeration
checks the registered finite universe and implementation; it is not the proof.

## Exact census

The run was bound to registration commit
`7ca4eb8a9a91e229544579f071a906eb0513bf39` and enumerated every Boolean truth
table for `n=2,3,4`:

| Parents | Labelled functions | Signed-parent gauge orbits | Labelled threshold | Quotient threshold |
|---:|---:|---:|---:|---:|
| 2 | 16 | 6 | 2 | 1 |
| 3 | 256 | 22 | 3 | 2 |
| 4 | 65,536 | 402 | 4 | 3 |

Across 65,808 functions, the exact identity between direct conditional sums and
low-order Walsh coefficients had zero mismatches.

For four parents, the ambiguity filtration was:

| Maximum intervention order `r` | Measurement signatures | Labelled-ambiguous signatures | Quotient-ambiguous signatures | Maximum quotient multiplicity |
|---:|---:|---:|---:|---:|
| 0 | 17 | 15 | 13 | 74 |
| 1 | 5,817 | 3,935 | 2,725 | 17 |
| 2 | 61,419 | 3,333 | 961 | 2 |
| 3 | 65,535 | 1 | 0 | 1 |
| 4 | 65,536 | 0 | 0 | 1 |

At `r=3`, exactly one labelled collision remains: top parity versus negative
top parity. One parent-sign flip relates the pair, so it is not a quotient
collision. At every `r<=2`, parity functions of degrees `r+1` and `r+2` give a
registered collision between genuinely distinct gauge orbits.

This verifies the sharp split:

```text
labelled threshold = n,
signed-parent quotient threshold = n-1.
```

## Rank and minimum-cost design

All 34 registered `(n,r)` design cells through `n=8` and `r<=4` had exact
modular rank

```text
D(n,r) = sum_(j=0)^r binomial(n,j).
```

The greedy minimum-weight basis always selected one all-positive assignment for
each parent subset through order `r`, with exact cost

```text
C_min(n,r) = sum_(j=1)^r j binomial(n,j).
```

The conditioning comparison exposes the practical price of that minimum:

| `n` | `r` | Rank | Full rows | Minimum cost | Minimum-basis condition number | Full-design condition number |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 16 | 81 | 32 | 46.979 | 2.250 |
| 6 | 3 | 42 | 233 | 96 | 92.310 | 5.397 |
| 8 | 4 | 163 | 1,697 | 512 | 489.733 | 10.299 |

These condition numbers are descriptive rather than gated, but the pattern is
mechanistically important. The zeta basis is optimally cheap for noiseless exact
recovery while becoming fragile under perturbation. Redundant sign assignments
cost more but keep the inverse substantially better conditioned.

## Implication for mechinterp and VPD

This identifies a failure mode distinct from holonomy and identity drift:
**interaction-order blindness**. A design can have perfect site coverage and
arbitrarily many repeated singleton measurements while retaining an exact
kernel containing every higher-order interaction coordinate.

For a VPD edit program, the corresponding tool should report:

- the maximum coordinated edit order admitted by the design;
- the rank gained at each order;
- the quotient-kernel dimension after registered feature symmetries;
- the minimum quotient-secant retention or conditioning margin; and
- the cost/conditioning position of the selected edit family relative to the
  minimum zeta basis and redundant all-sign design.

The immediate real-model falsification experiment is a small, cross-fitted edit
patch. Choose `n` identity-certified candidate directions, execute all signed
coordinated edits through order `r`, fit the local multilinear response, and
test on held-out prompts whether newly exposed degree-`r` terms predict effects
of held-out coordinated edits beyond every lower-order model. The theorem
predicts a hard null below the true interaction order and a rank increase when
that order is reached. Failure of the rank increase would reject the Boolean
local-tomography approximation for that patch rather than being interpreted as
evidence for a missing capability.

## Claim boundary

This result proves finite Walsh-analysis statements under uniform parent
environments, perfect interventions, deterministic semantic Boolean outputs,
and signed parent-coordinate gauge. It does not show that transformer
directions are independent Boolean parents, that finite-norm weight edits are
perfect interventions, or that these exact ranks predict model behavior.
Condition numbers are implementation diagnostics, not a registered noisy
sample-complexity result.

## Receipt

- Protocol registration commit:
  `7ca4eb8a9a91e229544579f071a906eb0513bf39`
- Result SHA-256:
  `342B36AB82C8207F89A23528EEC36DB36C15D10385C4D530AA1215D2AC1D39B7`

The exact argv, source/protocol/theorem hashes, environment, rank cells, gauge
orbits, collision summaries, parity fixtures, and gate records are stored in
`artifacts/result_v0_1.json`.

Local Git history records registration before execution and the runner matched
the committed blobs before and after the census. The registration commit was
not externally timestamp-anchored before the run, so the archive proves byte
binding but not preregistration chronology to an external observer.
