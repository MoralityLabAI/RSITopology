# ASMP-9 v0.41 finite sequential risk-access result

## Verdict

`finite_sequential_risk_access_characterization_established`

All nine registered gates passed. For finite targets, finite rational query
channels, a finite decision type, and a frozen horizon, the upper risk
polytope of adaptive policies is generated exactly by a Bellman recursion.
Necessary and sufficient sequential access at tolerance `epsilon` is the same
upper-risk-polytope containment criterion as v0.40, applied to those adaptive
generators.

On the registered noisy-channel fixture, two-query adaptive four-way
identification has deficiency:

```text
61/135
```

against:

```text
13/25
```

for randomized nonadaptive open-loop query sequences. The exact adaptivity
gain is:

```text
13/25 - 61/135 = 46/675.
```

The same channel library has no adaptive advantage for the asymmetric
root-group loss: both modes have deficiency `4/45`.

Sequential-design and decision-tree mathematics are classical. This is an
exact ASMP-9 finite specialization, not a full resolution.

## Chronology and binding

- implementation commit:
  `4a4b24b6741882d94cc21c08c48810f5c3dee24b`;
- registration commit:
  `797a7990be5edd48655e39be37da756ff39a5b06`;
- registration SHA-256:
  `1666885fe1072f9c718268d6007c98b453a9c534394bef047f1f1629febeb08e`;
- result content SHA-256:
  `e9221f35cea03a165b7461dd6a7953a90d03fa7e0dcf5b1f89512de021bfc30f`;
- result file SHA-256:
  `b76bd22e972478c6b98e2a8d0701e7d4b2993fcfda150c0660babea1b039e685`;
- verifier file SHA-256:
  `f83fdf080e6895871dc3b9927fe9cc2fe16df77e44138d5b0ae9754aee39b9bb`.

The thirteen-file registration was pushed before the canonical result was
written.

## Exact sequential object

For decision problem `d`, terminal action-loss generators `V_0(d)`, query
library `Q`, and horizon `h`, define:

```text
V_(h+1)(d,Q)
  = V_0(d)
    union over q in Q of
      {sum_y diag(P_q(y|.)) v_y :
       v_y in V_h(d,Q) for every y}.
```

Then:

```text
U_h(d,Q) = conv(V_h(d,Q)) + R_+^Theta
```

is exactly the upper risk set of randomized adaptive policies that ask at
most `h` queries and then act. Therefore access library `A` is sufficient
relative to reference library `B` at tolerance `epsilon` iff:

```text
U_h(d,B) subset U_h(d,A) + epsilon*1
```

for every registered decision problem.

This is a finite Bellman representation of a classical sequential
experiment. Coordinate-wise dominated generators can be removed without
changing the upper risk set.

## Burned-development correction

The first deterministic development fixture correctly predicted that an
adaptive depth-two tree identifies four targets while no deterministic
two-query open-loop sequence does. It incorrectly predicted open-loop
deficiency `1/2`.

Exact convexification over randomized open-loop plans gave:

```text
1/4.
```

The failed prediction is retained in
`DEVELOPMENT_PROTOCOL_v0_41.json`. This correction motivated the disjoint
confirmation: tree existence detects exact identification, but only the risk
polytope quantifies approximate access under randomized designs.

## Registered confirmation fixture

The four targets were measured through three binary channels:

| Query | Noiseless signature | Error rate |
| --- | --- | ---: |
| `root_q` | `(0,0,1,1)` | `1/5` |
| `left_q` | `(0,1,0,0)` | `1/4` |
| `right_q` | `(0,0,0,1)` | `1/3` |

Every response is conditionally flipped according to the displayed rational
error rate.

### Four-way identification

| Horizon | Adaptive deficiency | Open-loop deficiency |
| ---: | ---: | ---: |
| 0 | `3/4` | `3/4` |
| 1 | `3/5` | `3/5` |
| 2 | `61/135` | `13/25` |

The modes coincide before a response can influence a later query and separate
at horizon two. The exact gain `46/675` is about `13.1%` of the open-loop
deficiency.

The adaptive horizon-two upper hull has 133 coordinate-minimal generators;
the open-loop hull has 106. Exact primal-dual certificates equalize all four
target risks at their displayed minimax values.

### Decision-type negative control

The same channels were evaluated under root-group labels `(0,0,1,1)`,
false-positive cost `1/3`, and false-negative cost `2/3`.

| Horizon | Adaptive deficiency | Open-loop deficiency |
| ---: | ---: | ---: |
| 2 | `4/45` | `4/45` |

Thus adaptive experiment selection is not uniformly valuable. Its value is a
relation among channel geometry, horizon, and the registered downstream loss.

## Gates

| Gate | Requirement | Result |
| --- | --- | --- |
| P0 | fourteen preregistration tests | pass |
| S0 | thirteen sealed hashes | pass |
| R0 | exact six-plus-two cell universe | pass |
| B0 | adaptive curve `3/4, 3/5, 61/135` | pass |
| N0 | horizon-zero and horizon-one mode equality | pass |
| A0 | horizon-two gap exactly `46/675` | pass |
| D0 | group loss exactly `4/45` in both modes | pass |
| X0 | target-equalized exact minimax certificates | pass |
| RESOURCE | wall and memory ceilings | pass |

## Verification and resources

- confirmation time: `134.3748898` seconds;
- peak working set: `75,210,752` bytes (`71.73 MiB`);
- ceiling: `600` seconds and `1 GiB`;
- classification cells independently replayed: `6`;
- group cells independently replayed: `2`;
- sealed files independently revalidated: `13`;
- independent replay status:
  `independent_exact_replay_passed`.

The desktop caller timed out after launching the original executor, but that
executor continued. A later duplicate restart attempt was detected and
terminated before it produced any output. The original single executor wrote
the canonical result; the separate verifier subsequently recomputed it from
sealed source. This orchestration incident did not alter inputs or artifacts
and is retained in the run receipt.

## Resolution significance

v0.40 characterized arbitrary finite static access by upper risk-polytope
containment. v0.41 lifts that object to finite-horizon adaptive policies:

```text
registered decision type
  -> outcome-conditioned policy tree
  -> Bellman risk generators
  -> adaptive upper risk polytope
  -> exact sequential access certificate.
```

This closes the finite, known-channel, bounded-horizon characterization as an
exact object. It does not make exhaustive policy-tree enumeration efficient.
The next load-bearing resolution step is confidence-valid finite-sample
estimation of these access certificates when the channels are not known.

## Claim boundary

The recursion and complexity context are classical sequential
decision/experiment theory. The result does not establish a new Chernoff,
Blackwell, or optimal-decision-tree theorem; a polynomial-time solver;
continuous reward identifiability; finite-sample validity; strategic
demonstrator robustness; a transformer result; or resolution of ASMP-9.
