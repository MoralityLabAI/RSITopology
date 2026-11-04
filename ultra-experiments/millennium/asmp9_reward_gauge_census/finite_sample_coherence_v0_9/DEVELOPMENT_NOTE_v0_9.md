# ASMP-9 v0.9 development note

## Burned pilot

The development pilot used seeds `909100` through `909105`, 1,024 replicates
per arm, and the following six graphs:

```text
cycle_3, cycle_4, cycle_6, cycle_8, theta_4, complete_5.
```

Each graph was evaluated at sample multipliers

```text
0.125, 0.25, 0.5, 1.0, 2.0
```

relative to the conservative graph-dependent sufficient bound. The frozen
development constants were:

```text
alpha                  = 0.05
probability floor      = 0.10
coherent tolerance     = 0.50
incoherent margin      = 0.60
planted circulation    = +/-1.20
```

The sufficient per-edge sample counts ranged from `42,556` for the triangle
to `364,615` for the eight-cycle. They increased with the square of the
maximum fundamental-cycle length, up to the smaller logarithmic edge-count
term.

At multiplier `0.125`, the coherent arm was inconclusive in every pilot cell.
The positive/negative planted arms were at least `98.2%` inconclusive on the
short-cycle graphs and `100%` inconclusive on the six- and eight-cycles. At
multiplier `0.5` and above, every pilot replicate returned the expected
certificate. The theorem's multiplier-`1.0` sufficient bound was therefore
conservative, as intended.

Across every pilot sample:

- no certificate contradicted ground truth on the simultaneous event;
- no multiplier-at-or-above-bound sample missed its expected decision on the
  simultaneous event;
- mirrored positive and negative samples produced exactly mirrored status
  counts; and
- every forest control returned `unavailable_no_cycles`.

These outcomes are burned development data. The confirmatory protocol must use
fresh seeds and may not claim that the observed empirical crossover at
approximately half the analytic bound is itself a theorem.

## Design correction before registration

The first sample-bound draft controlled only cycle-band width. A skeptical
check found that this was insufficient to guarantee the data-dependent
probability-floor admission. The final development bound also includes the
minimum true-probability distance `d_p` from the registered floor and requires

```text
2 delta_n <= d_p.
```

This correction was made before any protocol or registration was frozen.
