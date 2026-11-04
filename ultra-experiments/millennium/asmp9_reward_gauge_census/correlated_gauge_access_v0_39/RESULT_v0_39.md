# ASMP-9 v0.39 correlated gauge access result

## Verdict

`correlated_gauge_access_alignment_established`

All ten registered gates passed. In the frozen three-policy reward grammar:

1. observing which constant-shift reward representative was selected has
   exact leakage radius

   ```text
   (max_theta P(xi=1|theta) - min_theta P(xi=1|theta))/2;
   ```

2. randomizing that choice independently of the target erases the leakage;
   and
3. equal leakage radius does not imply equal usefulness as a substitute for a
   missing target query.

This is an exact finite access result, not a general reward-identifiability
theorem or a resolution of ASMP-9.

## Chronology and binding

- implementation commit:
  `06b819d27d6dace13defa45f12db0c55838882d6`;
- registration commit:
  `20c9437804221c1f66fb7cec97ef62e6113fd004`;
- registration SHA-256:
  `2aee1094df09a140e1eae28b52c9bf6fd25b3bbecc99682e5f2b049ce8220a90`;
- result content SHA-256:
  `ee9d5d4185c17ef118437892f7659b2abaf2dadb2129f5b6365ac6a3284d95e7`;
- result file SHA-256:
  `6647db080bd772220290b7d46319185004d53c2d4695d4739cced50254e42cbc`.

The implementation and all fifteen sealed files were pushed before the
confirmation executor was invoked.

## Exact gauge-leakage theorem

Let `E_p` reveal the gauge-selection bit with
`p_theta=P(xi=1|theta)`, and let `E_0` return a constant observation. For the
registered three-policy zero-one regret type:

```text
delta_D(E_0,E_p) = delta(E_0,E_p) = diam(p)/2,
delta_D(E_p,E_0) = delta(E_p,E_0) = 0.
```

The three disjoint confirmation vectors gave:

| `p` | Analytic half-range | `delta_D` | Ordinary `delta` |
| --- | ---: | ---: | ---: |
| `(7/9,2/9,4/9)` | `5/18` | `5/18` | `5/18` |
| `(1/6,5/6,1/2)` | `1/3` | `1/3` | `1/3` |
| `(4/11,4/11,4/11)` | `0` | `0` | `0` |

Thus gauge semantics and statistical ancillarity are separate. The reward
representatives are decision-equivalent under the licensed constant shift,
but the mechanism choosing a representative can still reveal the target.

## Observational versus interventional access

The registered stochastic interventions

```text
do(xi ~ Bernoulli(2/7))
do(xi ~ Bernoulli(5/9))
```

made the assignment law target-independent. Both decision-relative and
ordinary leakage became exactly zero in both cells.

This intervention does not “identify more.” It deliberately destroys an
observational correlation. The result therefore distinguishes:

```text
decision-preserving reward gauge
  != target-independent assignment law
  != useful target-query alignment.
```

## Equal-radius access separation

For every registered symmetric strength, the three target-aligned gauge
channels `q0`, `q1`, and `q2` had the same leakage radius
`(high-low)/2`. Their value beside retained query `q1`, relative to reference
access `(q0,q1)`, was nevertheless:

```text
aligned q0 or complement(q0):  0
redundant q1:                   (high-low)/2
transverse q2:                 high*low*(high-low)
target-independent gauge:      (high-low)/2.
```

The disjoint cells were:

| `(high,low)` | Common radius | Aligned `q0` | Redundant `q1` | Transverse `q2` | Intervened/constant |
| --- | ---: | ---: | ---: | ---: | ---: |
| `(6/7,1/7)` | `5/14` | `0` | `5/14` | `30/343` | `5/14` |
| `(7/10,3/10)` | `1/5` | `0` | `1/5` | `21/250` | `1/5` |
| `(11/16,5/16)` | `3/16` | `0` | `3/16` | `165/2048` | `3/16` |
| `(9/14,5/14)` | `1/7` | `0` | `1/7` | `45/686` | `1/7` |

Decision-relative and ordinary deficiency agreed on every registered
alignment row. The main scientific conclusion is the separation, not that
agreement: scalar information magnitude is insufficient to determine
decision access; its target geometry matters.

## Gates

| Gate | Requirement | Result |
| --- | --- | --- |
| P0 | eleven-test exact preflight | pass |
| S0 | fifteen sealed hashes | pass |
| R0 | exact `3+2+20` row universe | pass |
| L0 | leakage equals the half-range | pass |
| I0 | stochastic intervention erases leakage | pass |
| A0 | aligned and complemented access substitute exactly | pass |
| Q0 | redundant and constant access remain at half-gap | pass |
| T0 | transverse branch equals `high*low*(high-low)` | pass |
| U0 | equal radius yields three distinct access values | pass |
| RESOURCE | wall and memory ceilings | pass |

## Verification and resources

- confirmation time: `39.5738381` seconds;
- peak working set: `74,448,896` bytes (`71.00 MiB`);
- ceiling: `600` seconds and `1 GiB`;
- independent replay: all 20 alignment, 3 leakage, and 2 intervention rows;
- sealed inputs independently revalidated: `15`;
- verifier artifact SHA-256:
  `2ee7cd624fd4d1379ee61ef3e7c17a946eab0363247e7919e631fb169906b024`.

## What changed in the resolution ledger

Version v0.38 classified necessary and sufficient access only when gauge
selection was target-independent. Version v0.39 closes the next registered
finite obligation:

- it characterizes exactly when the gauge observation is ancillary;
- it quantifies observational leakage when it is not;
- it shows an intervention that restores ancillarity; and
- it proves that leakage magnitude alone cannot rank access families.

The next unresolved step is a broader finite classification of alignment
under arbitrary target channels, losses, adaptive queries, and interventions,
followed by robust sample bounds and a valid physical measurement channel.

## Claim boundary

Blackwell comparison, Le Cam/Torgersen deficiency, nuisance
marginalization, ancillarity, and stochastic intervention are classical.
This result is their exact specialization to one finite reward-gauge access
grammar. It is not evidence about a language model, human values, recursive
self-improvement, or the full necessary-and-sufficient classification
demanded by ASMP-9.
