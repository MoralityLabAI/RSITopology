# Bounded log-odds context degree: access and sharpness

Status: **candidate theorem; development only**.

## 1. Setup

Let `X` be a finite set of `n>=2` alternatives. A positive stochastic-choice
kernel `p` gives a strictly positive probability vector `p(.|A)` on every
nontrivial menu `A subseteq X`.

For distinct `x,y` and context `S subseteq X\{x,y}`, define the observable
pairwise log odds

```text
g_xy(S) = log[p(x | S union {x,y}) / p(y | S union {x,y})].
```

Its Boolean Mobius coefficient at `T subseteq X\{x,y}` is

```text
theta_xy(T)
  = sum_{U subseteq T} (-1)^(|T|-|U|) g_xy(U).
```

Write `BP_r(X)` for the positive kernels satisfying

```text
theta_xy(T)=0 whenever |T|>r
```

for every ordered pair. Equivalently, each pairwise log-odds function has
Boolean degree at most `r`. The name records that this is a
Batsell-Polking-style log-ratio truncation, not a new choice-model hierarchy.

Let

```text
D_m = {A subseteq X : 2 <= |A| <= m}.
```

## 2. Candidate theorem

For `0<=r<=n-2`:

1. **Constructive sufficiency.** Restriction to `D_(r+2)` is injective on
   `BP_r(X)`. The full kernel is recovered by Mobius inversion followed by
   within-menu normalization.
2. **Sharp full-kernel threshold.** Restriction to `D_(r+1)` is not injective
   on `BP_r(X)`.
3. **Sharp tier threshold for `r>=1`.** For every `n>=r+2`, there are a Luce
   kernel and a non-random-utility kernel in `BP_r(X)` that agree on every menu
   in `D_(r+1)`.

Thus `r+2` is the sharp maximum queried-menu size for uniform full-kernel
identification in this nested access family. For `r>=1`, it is also the sharp
uniform threshold for identifying the Luce/RUM/non-RUM tier.

The `r=0` boundary is different: `BP_0(X)` is exactly the positive Luce class,
so the tier is assumed by the class even without data. Binary menus are still
necessary and sufficient to identify the full kernel.

## 3. Reconstruction proof

Assume `p in BP_r(X)` and all menus through size `r+2` are observed.

Fix `x!=y`. Observed menus give `g_xy(U)` for every context `|U|<=r`. Hence,
for every `|T|<=r`, compute

```text
theta_xy(T)
  = sum_{U subseteq T} (-1)^(|T|-|U|) g_xy(U).
```

All higher coefficients vanish by the class definition. Therefore, for any
unobserved context `S`,

```text
g_xy(S) = sum_{T subseteq S, |T|<=r} theta_xy(T).
```

Now fix any menu `A` and a root alternative `a in A`. Reconstruct
`g_xa(A\{x,a})` for every `x in A\{a}` and set

```text
w_a = 1,
w_x = exp(g_xa(A\{x,a})).
```

Then

```text
p(x|A) = w_x / sum_{z in A} w_z.
```

This is the unique probability vector with the reconstructed ratios.
Applying the procedure to every menu recovers the full kernel. If two
`BP_r(X)` kernels agree on `D_(r+2)`, every reconstructed ratio and probability
therefore agrees, proving injectivity.

## 4. Exact deterministic stability constant

The same interpolation has an exact worst-case error-amplification constant.
Suppose every observed value `g_xy(U)`, `|U|<=r`, is perturbed by at most
`epsilon`. For a target context `S` of size `s>r`, the coefficient of one
observed value indexed by `U subseteq S`, `|U|=u`, is

```text
c_(s,r,u) = (-1)^(r-u) choose(s-u-1, r-u).
```

This follows by exchanging the two sums in the Mobius reconstruction and using
the partial alternating-binomial identity

```text
sum_(j=0)^(r-u) (-1)^j choose(s-u,j)
  = (-1)^(r-u) choose(s-u-1,r-u).
```

Therefore the exact `l_infinity`-to-absolute-error operator norm at level `s`
is

```text
K(s,r)
  = sum_(u=0)^r choose(s,u) choose(s-u-1,r-u).
```

The reconstructed pairwise log odds have error at most `K(s,r)*epsilon`.
The constant is attained for an unrestricted low-layer perturbation by taking
the sign of every error equal to the corresponding interpolation coefficient.
For `s<=r`, the target is directly observed and the constant is one.

This is a deterministic condition number, not a sampling theorem. Translating
it into a tier decision still requires probability floors and a registered
separation margin from the Luce identities and RUM-polytope boundary. No
uniform finite-sample tier claim is made.

## 5. Fixed-universe sharpness construction

Fix `n>=r+2` and `r>=1`. Choose a distinguished `(r+2)`-set `A_0 subseteq X`,
a distinguished `x_0 in A_0`, and

```text
B_0 = A_0 \ {x_0},        |B_0|=r+1.
```

Let `b=r+2`. Give each `(r+1)`-subset `B` an integer parameter `lambda_B`,
with

```text
lambda_(B_0)=1,
lambda_B=0 otherwise.
```

For each menu `A` and item `x in A`, define the score exponent

```text
u_x(A)
  = sum_{B subseteq A\{x}, |B|=r+1} lambda_B
```

and the positive choice kernel

```text
p_lambda(x|A)
  = b^(u_x(A)) / sum_{z in A} b^(u_z(A)).
```

### 5.1 Agreement below the threshold

If `|A|<=r+1`, then `A\{x}` contains no `(r+1)`-subset. Every exponent is zero,
so `p_lambda(.|A)` is uniform. It agrees with the uniform Luce kernel on all
menus in `D_(r+1)`.

### 5.2 Membership in `BP_r(X)`

For `A=S union {x,y}`, the terms indexed by `(r+1)`-subsets of `S` cancel
between `u_x(A)` and `u_y(A)`. The remaining log odds, measured in base `b`,
are

```text
log_b[p_lambda(x|A)/p_lambda(y|A)]
  = sum_{T subseteq S, |T|=r}
      (lambda_(T union {y}) - lambda_(T union {x})).
```

This is a pure degree-`r` Boolean zeta expansion. Hence every higher Mobius
coefficient vanishes and `p_lambda in BP_r(X)`.

### 5.3 Non-RUM certificate

On `A_0`, only `x_0` has exponent one. Therefore

```text
p_lambda(x_0|A_0)
  = (r+2) / ((r+2)+(r+1))
  > 1/2.
```

Every binary menu is uniform, so for each `y in A_0\{x_0}`,

```text
p_lambda(x_0|{x_0,y}) = 1/2.
```

This violates random-utility regularity because `{x_0,y} subset A_0` but
choice probability increases when the menu expands. Thus `p_lambda` is
non-RUM, while the kernel it matches below the threshold is Luce.

This proves both fixed-`n` non-injectivity and tier ambiguity below `r+2`.

## 6. The `r=0` boundary

If every `g_xy` has degree zero, it is constant across contexts. Within-menu
odds cycles imply constants of the form

```text
g_xy = log(w_x/w_y)
```

for positive alternative weights `w`. Thus `BP_0(X)` is Luce. Binary menus
identify all weight ratios and therefore the full kernel. Without binary
menus, distinct Luce weights give distinct full kernels, proving the
full-kernel threshold while showing why `r=0` cannot be used as a non-circular
tier-certification result.

## 7. Executable support

The development implementation uses integer formal log-odds exponents and
exact `Fraction` probabilities. It checks:

- exact Boolean Mobius inversion on independent synthetic coefficient tables;
- the fixed-`n` witness for every `3<=n<=8` and `1<=r<=n-2`;
- agreement on every menu through size `r+1`;
- zero coefficients above degree `r`;
- exact reconstruction of every full-menu probability from menus through
  size `r+2`;
- the closed-form interpolation coefficients and their attained exact
  `l_infinity` operator norm;
- the explicit regularity violation; and
- the `r=0` Luce/full-kernel boundary.

Finite checks validate the implementation and witness family. They are not a
proof of the arbitrary-`n` theorem.

## 8. Proof and scope debt before registration

1. Obtain independent review of the fixed-universe construction and indexing.
2. Search specifically for a Batsell-Polking or subsequent theorem stating
   the same maximum-menu-size threshold.
3. Obtain independent review of the deterministic interpolation constant and
   keep it separate from any sampling or tier-margin claim.
4. Keep selection or validation of `r` outside the claim unless a separate
   prospective procedure is supplied.

## Claim boundary

This is an exact finite access theorem conditional on bounded contextual
log-odds degree. It neither shows that the assumption is empirically true nor
selects the order. It does not handle samples, zeros, ties, endogenous menus,
strategic or nonstationary response, continuous choice, moral value, or
welfare. It would close one structured-completion cell in the v0.56
obligation matrix, not resolve ASMP-9.
