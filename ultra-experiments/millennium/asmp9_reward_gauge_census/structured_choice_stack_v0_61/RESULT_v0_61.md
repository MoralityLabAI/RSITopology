# ASMP-9 conditional structured-choice stack result v0.61

## Verdict

**`conditional_structured_choice_stack_verified`**

All nine frozen gates passed.  This prospectively verifies the finite
implementations and proof handoffs joining v0.57-v0.60:

```text
bounded context degree
  -> exact nested-menu reconstruction;

separation margin
  -> finite-sample tier certificate;

fixed Huber contamination
  -> exact population overlap radius;

selection timing and positivity
  -> support/rate boundary or complete confounding.
```

The ingredients are classical or elementary.  The result is conditional on
the registered model and does not resolve ASMP-9.

## Prospective chronology

- verifier-source commit:
  `b74486bfb875368ed23d6fe8a827a7c6dcbb1e83`
- registration commit:
  `ef1f92edab1f6de5ba4a82f22632e7d808a1ad03`
- registration SHA-256:
  `e6138bb101b094110c2011a91bf71ccaaa808857ad8c0eeec1fb38ac35ae69df`
- frozen-cell SHA-256:
  `fbddc7646d4603243f56914778c89c5b56407462c7efc542171a96cf62bc62f5`
- canonical fact digest:
  `b6a183bac5f264bc410c2c25e07bd4030b7d0b2286efcaa3cb9ae302060ac9ae`
- verification-result SHA-256:
  `a6deb25c85ee2a2f2c21c6b16206d3d1348af2ee13dd89882a457069fbee7bd7`

The verifier source was committed and pushed before the registration was
created.  The registration was committed and pushed before the fresh cells
were executed.  The v0.57-v0.60 development tables and checks were treated as
burned.

## B57 — bounded-degree access

Twelve new cells used universe sizes `9` through `12` and context degrees
spanning low, interior, and full-access orders.

- `88,724` probability coordinates on menus below the threshold were checked
  for exact agreement with the uniform Luce kernel.
- `86,228` Möbius coefficients above the registered degree were checked as
  exact zeros.
- Every cell had a live order-`r` coefficient.
- Every held-out deterministic polynomial target reconstructed exactly.
- Every sharp witness gave

```text
p(x0|A0)=(r+2)/(2r+3)>1/2
```

against binary probability `1/2`, supplying the registered regularity
violation.

The fresh exact interpolation norms ranged from `1` at full access to `7,423`
in an interior `(n=12,r=7)` cell.  This confirms the implementation of the
sharp access theorem while displaying why exact identification can be
statistically ill-conditioned.

## M58 — margin and sampling

Three new rational Luce/RUM paths preserved uniform binary menus while moving
the full-menu vector off Luce.  Three new RUM/non-RUM paths crossed the
registered regularity face by exactly `2 gamma`.

The sufficient per-menu counts on the three frozen cells were:

| `n` | `r` | `K_star` | `Q(n,r)` | sufficient count |
|---:|---:|---:|---:|---:|
| 4 | 1 | 3 | 24 | 13,024,922 |
| 7 | 3 | 49 | 392 | 457,140,887,781 |
| 9 | 6 | 127 | 2,286 | 276,738,083,591,819 |

These are conservative theorem counts, not recommended experimental budgets
or minimax rates.  Their size is a substantive warning: a bounded-degree
identifiability premise does not make high-order extrapolation practically
certifiable without much stronger conditioning.

## C59 — fixed contamination

The exact overlap theorem was verified on all `13,695` unordered pairs
(including equality pairs) of the `165` four-outcome rational distributions
with denominator `8`.  Every equality case constructed a normalized common
observation and valid contaminant for both clean laws.

Three fresh RUM/non-RUM witnesses met exactly at

```text
epsilon = 2 gamma/(1+2 gamma).
```

Nine fresh robust sampling cells separately charged contamination bias and
sampling error against the clean coordinate tolerance.  All closed their
registered reconstruction bound; equality remained non-passing.

## S60 — selection timing and recording

The exact outcome-dependent-selection construction and bounded recording
radius were checked on all `1,596` unordered pairs of `56` strictly positive
four-outcome rational distributions.

- unrestricted outcome-dependent recording produced a common complete record
  law for every pair;
- `4,788` pair-by-recording-interval decisions matched the exact symmetric
  likelihood-ratio condition;
- every admitted bounded pair constructed recording weights inside the
  declared interval; and
- the pre-response joint law recovered exactly the positive-support menus
  `[0,2,3]` while leaving the zero-support menu unclaimed.

For the fresh conditional-response cell, the per-menu sufficient count was
`65,285`.  Selection floors from `1/5` to `1/2000` produced total sufficient
draw counts from `652,850` to `261,140,000`, with the independent lower
calculation preserving the exact `1/pi` exponent.

## X0 and compactness

Version v0.61 fixes the shared coordinate-count convention as

```text
Q(n,r)=sum k*choose(n,k)
```

over observed menu sizes.  Both implementations agreed on every `Q`,
`K_star`, witness, threshold equality, and selection handoff.

The proof audit also closes the class-minimum attainment premise.  An observed
probability floor `a>0` and interpolation norm `K_star` give the conservative
full-kernel coordinate floor

```text
a^(2 K_star)/n > 0.
```

The reconstruction image is therefore compact inside the positive-kernel
space; the margin-separated tier fibers are closed and compact; and the
cross-tier minima `Delta` and `Lambda` used by v0.59-v0.60 are attained.

## Independent replay and resources

The replay imports neither the primary verifier nor any v0.57-v0.60
implementation.  It uses closed-form counts and Cartesian-grid enumeration
where the primary uses subset transforms and composition generators.

```text
fact digests equal:  yes
gate records equal:  yes
fact rows equal:     yes
tests:               6 passed
elapsed:             12.21 seconds
resident memory:     25,206,784 bytes
workers:             1
```

## What this establishes

The verified conditional ledger is:

1. `D_(r+2)` is the sharp nested access threshold inside the declared
   degree-`r` positive log-odds class.
2. Exact tier classification has no uniform finite sample bound without a
   separation promise; with the promise, one explicit sufficient rate closes.
3. Fixed Huber contamination has an exact class-overlap radius, conditional on
   the attained cross-tier modulus.
4. Recorded pre-response selection reduces to support plus a `1/pi` sampling
   cost; unknown outcome-dependent recording instead causes complete
   confounding unless its likelihood-ratio radius is bounded.

## What this does not establish

The result does not:

- select or empirically validate context degree `r`;
- show that a human or model has a coherent latent value object;
- make the sufficient sample counts minimax or computationally practical;
- compute `Delta` or `Lambda` for a general nontrivial class;
- handle zeros, ties, hidden consideration sets, latent state confounding,
  adaptive sample replacement, strategic or nonstationary response;
- give welfare or moral semantics to any tier; or
- resolve ASMP-9.

The next load-bearing mathematical target is no longer registration of this
stack.  It is an exact primal/dual evaluation of the cross-tier moduli on a
nontrivial finite bounded-degree class, followed by a hidden-choice-set or
latent-confounding access theorem.
