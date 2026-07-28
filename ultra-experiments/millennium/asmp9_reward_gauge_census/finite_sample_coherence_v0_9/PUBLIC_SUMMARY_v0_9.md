# Finite samples can certify cycle coherence without treating silence as proof

## Result

Pairwise choice probabilities form a directed edge flow:

```text
l_e = logit(P(j preferred to i)).
```

For a scalar Bradley-Terry value model, this flow is a gradient. Every
fundamental-cycle circulation therefore vanishes. Version v0.7 established
that exact population-law criterion; v0.9 supplies a finite-sample
certificate.

With `m` comparison edges, `n` independent Bernoulli observations per edge,
and familywise error level `alpha`, define

```text
delta_n = sqrt(log(2m/alpha)/(2n)).
```

A union bound over Hoeffding intervals gives

```text
P(max_e |p_hat_e-p_e| > delta_n) <= alpha.
```

The procedure admits a run only when every simultaneous probability interval
lies inside a registered interior `[eta,1-eta]`. The logit's derivative is
then bounded, and a cycle `c` of length `k_c` receives the simultaneous band

```text
c^T logit(p_hat)
  +/- k_c delta_n/(eta(1-eta)).
```

The output is total:

- `certified_coherent_within_tolerance` only when every cycle band lies inside
  the declared coherent region;
- `certified_incoherent` only when a cycle band clears the separated
  incoherence margin;
- `inconclusive` between those regions;
- `unavailable_no_cycles` when the graph has no cycle test; and
- `unavailable_probability_floor` when the logit stability assumption is not
  supported.

No finite sample is reported as proving exact zero circulation.

## Conservative graph-dependent bound

Let `k_max` be the longest registered fundamental cycle, `d_p` the minimum
true-probability distance from the interior boundary, `epsilon_0` the coherent
tolerance, `epsilon_1` the incoherent margin, and `Delta` the planted
circulation. It suffices that

```text
delta_n <= min(
  d_p/2,
  eta(1-eta)/(2 k_max) * min(epsilon_0, Delta-epsilon_1)
).
```

The resulting sufficient scaling is quadratic in maximum cycle length:

```text
n = O(k_max^2 log(m/alpha)/margin^2),
```

with the registered probability-interior factors made explicit. This is a
sufficient bound for this certificate, not a minimax lower bound.

## Prospective verification

The theorem, prior-art boundary, implementation, environment, tests,
protocol, and runner were hash-sealed before fresh sampling. The CPU-only run
used six graphs:

| graph | beta_1 | k_max | sufficient samples per edge |
|---|---:|---:|---:|
| `cycle_3` | 1 | 3 | 42,556 |
| `cycle_4` | 1 | 4 | 80,201 |
| `cycle_6` | 1 | 6 | 194,868 |
| `cycle_8` | 1 | 8 | 364,615 |
| `theta_4` | 2 | 4 | 83,727 |
| `complete_5` | 6 | 3 | 53,258 |

Each graph received coherent, positive-circulation, and mirrored
negative-circulation arms at five sample multipliers, with 4,096 replicates
per cell: 368,640 certificates in total. Two 8,192-replicate controls tested
forests and out-of-interior probabilities.

All ten registered gates passed:

- no certificate contradicted ground truth on its simultaneous event;
- every at-or-above-bound sample on that event returned its expected
  certificate;
- at one-eighth of the bound, the smallest one-sided 99%
  Clopper-Pearson lower bound on the inconclusive fraction was `0.9762`;
- at or above the bound, the smallest corresponding lower bound on the
  expected decision fraction was `0.998876`;
- all 8,192 forest controls returned `unavailable_no_cycles`;
- all 8,192 probability-floor controls returned
  `unavailable_probability_floor`; and
- all positive/negative mirror status counts matched exactly.

The independent artifact verifier passed, and all 84 prereveal tests passed.

## ASMP-9 contribution and remaining gap

This closes a narrow but load-bearing misuse of population coherence tests:
finite noisy data can support a simultaneous near-coherence certificate, but
insufficient data must remain inconclusive and a forest cannot test coherence
at all.

It does not resolve ASMP-9. The result assumes independent fixed-count
comparisons, a known logit link, a fixed graph and cycle basis, and a declared
probability interior. It gives no minimax lower bound, adaptive allocation
theorem, unknown-link estimator, contextual-response model, or general
finite-MDP reward-identification result. The concentration, Bradley-Terry,
and HodgeRank ingredients are classical; novelty is not claimed.
