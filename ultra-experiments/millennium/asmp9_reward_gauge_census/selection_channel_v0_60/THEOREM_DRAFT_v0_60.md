# A timing and positivity boundary for selected stochastic-choice data

Status: **candidate theorem; development only**.

## 1. Frozen objects

Let `X` be a finite alternative set and

```text
M(X) = {A subseteq X : |A| >= 2}
```

the nontrivial menu universe. A positive clean stochastic-choice kernel `p`
assigns a response distribution `p_A` to every menu.

This version distinguishes two selection mechanisms that must not be called
the same form of "endogeneity."

### Recorded pre-response menu selection

First draw a menu

```text
A ~ s_p,
```

then draw

```text
Y | A ~ p_A,
```

and record both `(A,Y)`. The selection law may depend arbitrarily on the
entire clean kernel `p`, but conditional response stability is assumed:
selection occurs before the registered response, and no additional latent
variable affects both menu assignment and that response.

### Outcome-dependent recording

For a base-assigned menu `A`, draw `Y~p_A`, then retain the response with
unknown probability

```text
rho_A(Y) in (0,1].
```

The record contains `A`, the retention indicator, and `Y` when retained.
This is a nonignorable selection mechanism because retention depends on the
response.

Neither model includes strategic adaptation across rounds, hidden
alternatives inside a recorded menu, or time-varying kernels.

## 2. Recorded pre-response selection theorem

The population joint law is

```text
J_p,s(A,x) = s_p(A) p_A(x).
```

For every menu with positive selection probability,

```text
s_p(A) = sum_x J_p,s(A,x),

p_A(x) = J_p,s(A,x) / s_p(A).
```

Consequently the joint law identifies exactly the restriction of `p` to

```text
D(s_p) = {A : s_p(A)>0}.
```

This remains true when `s_p` is unknown and target-dependent. The
target-dependence is visible in the recorded menu marginal and does not bias
the conditional response law under the frozen factorization. Because the
mapping `p -> s_p` is otherwise unrestricted and unknown, its marginal carries
no uniformly usable information about missing conditionals. A known
selection model could supply additional information and is a different access
class.

### Exact unrestricted tier consequence

Combine the factorization with the verified v0.56 incomplete-menu theorem.
For positive unrestricted kernels on `n>=3` alternatives:

```text
D(s_p) = M(X)
  -> the complete kernel and its tier are identified;

D(s_p) proper-subset M(X)
  -> compatible tiers are exactly

     {N}       if no RUM completion exists,
     {R,N}     if a RUM but no Luce completion exists,
     {L,R,N}   if a Luce completion exists.
```

Thus arbitrary pre-response target dependence is not the obstruction.
Support is. A proper domain may sometimes refute RUM and identify tier `N`,
but it cannot uniformly classify all clean kernels. Complete positive support
is necessary and sufficient for **uniform** singleton-tier classification
under unrestricted completion.

For the v0.57 bounded-context class, the same factorization reduces selection
to the observed support, after which the candidate `r+2` reconstruction
theorem applies if that complete identifying subfamily is supported. This
conditional statement inherits v0.57's development-only status.

## 3. Positivity is also the finite-sample rate parameter

Let `D` be a finite identifying menu family of size `m_D` and assume

```text
pi = min_(A in D) s_p(A) > 0.
```

Suppose `n_A` clean conditional samples per menu are sufficient for a frozen
conditional-response certificate with failure probability `delta/2`.
With `T` iid selected-menu draws, multiplicative Chernoff and a union bound
give

```text
P[
  some A has N_A < T pi/2
]
<=
m_D exp(-T pi/8).
```

Therefore

```text
T >= max{
  2 n_A/pi,
  (8/pi) log(2 m_D/delta)
}
```

suffices to supply every menu with `n_A` responses with probability at least
`1-delta/2`. Combining that event with the conditional certificate gives total
failure probability at most `delta`.

For the v0.58 margin-promised plug-in rule, use

```text
n_A
  =
  ceil[
    log{4 Q(n,r)/delta}
    / {2 t_gamma^2}
  ].
```

The resulting total-draw sufficient rate is

```text
O(
  1/(pi t_gamma^2)
  * log{Q(n,r)m_D/delta}
).
```

### Matching dependence on the selection floor

Use the v0.58 three-alternative margin-promised RUM/non-RUM pair. The two
kernels differ only on the full menu, whose conditional KL divergence is

```text
D_gamma = -(2/5) log(1-25 gamma^2).
```

Assign that informative menu probability `eta>0` under both hypotheses. The
single-draw joint divergence is exactly

```text
eta D_gamma.
```

For any classifier based on `T` iid selected-menu draws whose maximum error is
at most `delta<1/2`, product-law KL, Pinsker, and Le Cam imply

```text
T
>=
2(1-2 delta)^2
/
{eta D_gamma}.
```

Hence `T=Omega(1/(pi gamma^2))` on this slice. The positive bound and negative
witness match both the `1/pi` and `1/gamma^2` exponents there.

If no positive selection floor is declared, let `eta` tend to zero. Every
menu can remain in population support while no finite total budget works
uniformly. Population identifiability and uniform finite-sample
certifiability are therefore separate.

## 4. Outcome-dependent recording theorem

For one menu, retained responses have joint masses

```text
h(x) = p(x) rho(x)
```

and total retention probability `z=sum_x h(x)`. Conditional on retention,

```text
q(x) = p(x)rho(x)/z.
```

Take any two positive clean laws `p,p'` and any positive target selected law
`q`. Choose

```text
0 < z <= min_x {
  p(x)/q(x),
  p'(x)/q(x),
  1
}.
```

Set

```text
rho(x)  = z q(x)/p(x),
rho'(x) = z q(x)/p'(x).
```

Both recording functions lie in `(0,1]` and produce exactly the same:

```text
P(R=1,Y=x) = z q(x),
P(R=0)     = 1-z.
```

Applying the construction independently to every menu proves:

> Under unrestricted unknown positive outcome-dependent recording, every two
> positive clean stochastic-choice kernels are observationally equivalent,
> even when every menu is base-assigned, menu identities are recorded, and
> retention rates are observed.

The tier is therefore unidentified. This is stronger than a missing-menu
obstruction: the complete recorded menu domain can still be useless.

### Exact bounded-recording radius

The unrestricted no-go has a nonvacuous bounded counterpart. Suppose every
unknown recording probability lies in one declared interval

```text
0 < ell <= rho_A(x) <= u <= 1.
```

Two positive clean distributions `p,p'` on one menu induce the same complete
record law, including the retention rate, iff

```text
max_x max{
  p(x)/p'(x),
  p'(x)/p(x)
}
<=
u/ell.
```

Necessity is coordinatewise: a common recorded mass `h(x)` must belong to

```text
[ell p(x), u p(x)]
intersect
[ell p'(x), u p'(x)].
```

Sufficiency follows by choosing

```text
h(x) = max{ell p(x), ell p'(x)}.
```

The ratio condition places this value below both upper endpoints. Setting
`rho=h/p` and `rho'=h/p'` gives the same recorded responses and the same
unretained probability.

For a compact clean class `C` with compact tier fibers and a complete
registered menu family `D`, define

```text
Lambda(C,D)
  =
  min_(tier(p) != tier(p'))
    max_(A in D, x in A)
      max{
        p_A(x)/p'_A(x),
        p'_A(x)/p_A(x)
      }.
```

Then `u/ell < Lambda` identifies the tier at population level. At equality a
minimizing pair is already confusable but the frozen reported status is
`boundary_inconclusive`; above equality the status is `ambiguous`. This is an
exact multiplicative selection radius, though computing `Lambda` may be
difficult.

For the v0.58 `Hbar_gamma` margin class, every cross-tier pair has some menu
with `L1` distance at least `gamma`. If its coordinatewise likelihood ratios
were bounded by `kappa`, the sharp likelihood-ratio oscillation inequality
would give

```text
L1 <= 2 tanh{log(kappa)/2}.
```

Therefore

```text
Lambda
>=
(2+gamma)/(2-gamma),
```

and a certified positive region is

```text
u/ell < (2+gamma)/(2-gamma).
```

The explicit v0.58 RUM/non-RUM pair has exact required ratio

```text
1/(1-5 gamma),
```

so it supplies a cross-tier ambiguity witness when

```text
u/ell >= 1/(1-5 gamma).
```

The lower and upper brackets do not coincide. Sharp evaluation of `Lambda`
remains open.

### Correctable boundary

If every `rho_A(x)` is known and positive, then

```text
p_A(x) = h_A(x)/rho_A(x)
```

exactly. A registered intervention that forces retention, or makes it a known
response-independent constant, also restores the clean conditionals.

Thus the sharp finite distinction is:

```text
recorded pre-response selection:
    support controls identification;

unknown outcome-dependent selection:
    complete support does not identify without a recording-ratio restriction;

known positive recording weights or forced recording:
    inverse correction restores identification.
```

## 5. What this changes

The term "endogenous menu" is too coarse for an access theorem. The order and
observability of the selection mechanism determine which mathematical object
survives:

```text
target-dependent menu frequency
  != response-dependent observation
  != hidden choice set
  != strategic response.
```

Version v0.60 closes only the first two finite factorizations. Hidden choice
sets and latent-state confounding require richer identified-set machinery.

## Proof debt before registration

1. Verify all factorization and common-observation constructions on exact
   rational grids.
2. Check the v0.56 tier handoff and v0.58 lower path against their frozen
   implementations.
3. Review whether the conditional-iid argument remains valid under the
   intended selected-menu sampling protocol.
4. Obtain a direct missing-data/discrete-choice subsumption review; presume
   the factorization is classical.
5. Decide whether the registered theorem should bind the finite-sample
   corollary or only the population timing boundary.

## Claim boundary

This theorem concerns finite positive stochastic-choice kernels, recorded
menus, iid draws, a stable conditional response law, and either pre-response
menu selection or response-dependent recording. It does not identify
unobserved choice sets, latent preference-selection confounding, strategic
demonstrators, hidden alternatives, nonstationarity, continuous choice,
unknown context degree, welfare relevance, or a physical human/model query
channel. The ingredients are classical missing-data and choice-sampling
mathematics specialized to the ASMP-9 tier object. ASMP-9 remains unresolved.
