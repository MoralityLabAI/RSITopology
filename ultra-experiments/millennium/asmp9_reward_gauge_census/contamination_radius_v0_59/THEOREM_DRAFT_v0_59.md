# A sharp population contamination boundary for finite value-object tiers

Status: **candidate theorem; development only**.

## 1. Access model

Let `D` be a finite observed menu family. A clean stochastic-choice kernel
`p` does not generate the observed response law directly. For each menu
`A in D`, responses are iid from

```text
q_A = (1-epsilon) p_A + epsilon c_A,
```

where `epsilon in [0,1)` is known and each `c_A` is an arbitrary categorical
distribution. Contaminants may differ by menu but are fixed before iid
sampling. This is the additive Huber contamination model. It is not the
stronger sample-replacement model and is not adaptive to realized samples.

For a clean distribution `p_A`, write

```text
N_epsilon(p_A)
  = {(1-epsilon)p_A + epsilon c_A : c_A is a distribution}.
```

## 2. Exact categorical overlap theorem

For any two distributions `p` and `p'` on one finite alphabet,

```text
N_epsilon(p) intersects N_epsilon(p')

iff

TV(p,p') <= epsilon/(1-epsilon).
```

Equivalently, the smallest contamination level permitting a common observed
law is

```text
epsilon_star(p,p') = TV(p,p') / {1+TV(p,p')}.
```

### Proof

Every common observed law `q` must dominate both clean components:

```text
q_i >= (1-epsilon) max(p_i,p'_i).
```

Since

```text
sum_i max(p_i,p'_i) = 1 + TV(p,p'),
```

such a probability law can exist only when

```text
(1-epsilon){1+TV(p,p')} <= 1.
```

This is the displayed condition. Conversely, assign the mandatory mass

```text
(1-epsilon) max(p_i,p'_i)
```

to every coordinate and put the nonnegative leftover mass on any coordinate.
Subtracting `(1-epsilon)p` or `(1-epsilon)p'` and dividing by `epsilon`
constructs the two contaminating distributions. The condition is therefore
necessary and sufficient, including equality.

For independently selectable contaminants on a menu family `D`, two clean
kernels are observationally confusable exactly when

```text
max_(A in D) TV(p_A,p'_A) <= epsilon/(1-epsilon).
```

## 3. Exact class-level tier threshold

Fix a compact clean class `C` carrying a tier map

```text
tier: C -> {L,R,N},
```

where `L` is Luce, `R` is random utility but not Luce, and `N` is non-RUM.
Assume each of the three tier fibers is compact; equivalently for the
application below, use the closed margin-promised tier fibers inside the
positive probability-floor slice. This makes every nonempty cross-tier
product compact and the minimum below attained.
Define the observed-menu cross-tier modulus

```text
Delta(C,D)
  = min_{
      p,p' in C,
      tier(p) != tier(p')
    }
    max_(A in D) TV(p_A,p'_A).
```

Then the exact population threshold is

```text
epsilon_star(C,D)
  = Delta(C,D) / {1+Delta(C,D)}.
```

- If `epsilon < epsilon_star(C,D)`, no two different tiers induce a common
  contaminated observed law, so the tier is population identifiable.
- If `epsilon >= epsilon_star(C,D)`, a minimizing cross-tier pair has
  intersecting contamination neighborhoods, so no procedure can identify the
  tier uniformly.
- Equality is an ambiguity boundary, never a pass.

Without compact tier fibers, replace `min` by `inf`: the strict
identifiability and strict ambiguity statements remain valid, but equality
requires a separate attainment check. This is a characterization in terms of
a class modulus, not an efficient algorithm for computing that modulus.

## 4. Bounds for the bounded-context class

Use the v0.57-v0.58 class

```text
C_(n,r,a,gamma)
  = BP_r
    intersect Hbar_gamma
    intersect {observed probabilities >= a}.
```

Here `Hbar_gamma` uses the same v0.58 margins but replaces the positive Luce
fiber by its closure inside the probability-floor slice. This is the compact
version of the margin-promised tier union; on strictly positive kernels its
Luce fiber agrees with the positive Luce model. Any two members in different
tiers have full-kernel maximum menuwise `L1` distance at least `gamma`.

Let `K_star(n,r)` be the v0.57 interpolation norm. If

```text
tau = max_(A in D_(r+2)) TV(p_A,p'_A),
```

then every observed coordinate differs by at most `tau`. Exact Mobius
interpolation and likelihood-ratio oscillation give

```text
d(p,p')
  <= 2 tanh[
       -K_star(n,r) log(1-tau/a)
     ].
```

Consequently,

```text
Delta(C_(n,r,a,gamma),D_(r+2))
  >=
  a {
    1-exp[
      -atanh(gamma/2)/K_star(n,r)
    ]
  }.
```

This yields a certified population-identifiability region:

```text
epsilon/(1-epsilon)
  <
  a {
    1-exp[
      -atanh(gamma/2)/K_star(n,r)
    ]
  }.
```

### Matching explicit ambiguity direction

For `n=3`, `r=1`, `a<=1/5`, and `0<gamma<=1/125`, the v0.58
RUM/non-RUM pair agrees on every binary menu and has full-menu vectors

```text
q_0       = (2/5,           2/5,           1/5),
q_(2g)    = (2/5+2 gamma,   2/5-2 gamma,   1/5).
```

The pair lies in `Hbar_gamma` and has observed-menu TV distance `2 gamma`.
Therefore

```text
Delta(C_(3,1,a,gamma),D_3) <= 2 gamma
```

and contamination ambiguity occurs by

```text
epsilon = 2 gamma/(1+2 gamma).
```

At that exact boundary, contaminating `q_0` by a point mass on the first
alternative and contaminating `q_(2g)` by a point mass on the second
alternative produces the same observed full-menu law.

The lower modulus bound and explicit upper witness do not coincide. Version
v0.59 therefore characterizes the exact threshold through `Delta`, brackets
it constructively, and leaves sharp evaluation of `Delta` open.

## 5. Finite-sample sufficient certificate

Take `N` independent observations from every menu in `D_(r+2)` and let
`p_hat_A` be the empirical contaminated law. Treat `p_hat_A` as the low-menu
input to the v0.57 reconstruction.

On the simultaneous coordinate event

```text
max_(A,x) |p_hat_A(x)-q_A(x)| <= t,
```

the clean-coordinate error is at most

```text
epsilon + t.
```

Define the clean v0.58 tolerance

```text
t_clean
  = a {
      1-exp[
        -atanh(gamma/6)/K_star(n,r)
      ]
    }.
```

If `epsilon >= t_clean`, this plug-in certificate is unavailable regardless
of sample size. If `epsilon < t_clean`, set

```text
t_sample = t_clean - epsilon.
```

With

```text
Q(n,r) = sum_(k=2)^(r+2) k choose(n,k),

N >
  log{2 Q(n,r)/delta}
  / {2 t_sample^2},
```

coordinatewise Hoeffding gives the simultaneous event with probability at
least `1-delta`. The reconstructed full kernel is then within `gamma/3` of
the clean kernel, and the frozen v0.58 distance classifier returns the correct
tier for every member of `Hbar_gamma`.

Sampling error `t` and adversarial bias `epsilon` are separate additive
terms. Equality at `t_clean` returns `inconclusive`; it is not adjudicated.

This sufficient count is conservative. It is not the minimax robust testing
rate and does not attain the exact class threshold in Section 3.

## 6. What this changes

The clean v0.58 separation margin becomes an operational robustness budget:

```text
structural interpolation consumes conditioning;
contamination consumes deterministic coordinate tolerance;
sampling consumes the remainder.
```

The exact modulus `Delta(C,D)` is the population object deciding whether any
robust tier certificate is possible. Marginal accuracy of the contaminated
responses is not enough.

## Proof debt before registration

1. Independently verify the exact overlap construction over rational
   categorical grids.
2. Verify the RUM/non-RUM common-observation witness against the frozen v0.54
   tier classifier.
3. Audit compactness and threshold attainment for the exact declared class
   `C_(n,r,a,gamma)`.
4. Search robust-testing prior art for this exact finite categorical overlap
   specialization; presume it is classical until shown otherwise.
5. Decide whether the registration should bind only the exact population
   theorem or also the conservative sampling corollary.

## Claim boundary

The theorem concerns fixed per-menu Huber mixtures with known contamination
level, iid observations, known context degree, a positive clean probability
floor, and a declared tier-separation promise. It does not cover adaptive
sample replacement, dependent or strategic contaminants, endogenous menu
selection, unknown contamination, nonstationarity, or efficient optimization
of the class modulus. It is not evidence about human or model values and does
not resolve ASMP-9.
