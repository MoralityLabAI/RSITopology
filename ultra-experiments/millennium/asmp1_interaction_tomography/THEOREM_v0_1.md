# Interaction-order tomography modulo parent symmetry

## 1. Measurement object

Let `f:{-1,+1}^n -> {-1,+1}` have Walsh-Fourier expansion

```text
f(x) = sum_(T subseteq [n]) f_hat(T) chi_T(x),
chi_T(x) = product_(i in T) x_i.
```

For every `S subseteq [n]` with `|S|<=r` and every assignment
`a in {-1,+1}^S`, the order-`r` intervention design observes the exact
conditional mean

```text
m_f(S,a) = E[f(X) | X_S=a],
```

where the unconditioned coordinates are independent and uniform. The passive
mean is the row `S=empty`. In the implementation, fixed-denominator integer
conditional sums and unnormalised integer Walsh coefficients are stored; these
are invertible row-scalings of the displayed means and coefficients.

Observed output labels `-1,+1` are semantic and are not gauge. Parent names and
parent polarities are gauge: the hyperoctahedral group

```text
B_n = Sym(n) semidirect_product (Z/2)^n
```

acts by coordinate permutations and input-sign flips, with the intervention
interface relabelled by the same action.

## 2. Order-recovery theorem

**Theorem 1.** The order-`r` design observes exactly the Walsh coefficients
`f_hat(T)` with `|T|<=r`. Its linear rank on the full truth-table space is

```text
D(n,r) = sum_(j=0)^r binomial(n,j),
```

and its kernel is the span of Walsh characters of degree greater than `r`.

**Proof.** Averaging over every unconditioned coordinate kills a character
unless its support is contained in `S`, so

```text
m_f(S,a) = sum_(T subseteq S) f_hat(T) chi_T(a).
```

For fixed `S`, Fourier inversion on the `|S|`-cube recovers every coefficient
with support contained in `S`. Taking all `|S|<=r` therefore recovers exactly
the degree-at-most-`r` coefficients. Walsh characters are a basis, so the rank
and kernel statements follow. QED.

**Corollary 1 (labelled degree threshold).** On the class of Boolean functions
of Fourier degree at most `k`, uniform labelled identifiability holds if and
only if `r>=k`.

**Proof.** Sufficiency follows from Theorem 1. If `r<k`, the two semantic-output
functions `chi_T` and `-chi_T`, for any `|T|=k`, have identical zero
degree-at-most-`r` measurements and are distinct labelled functions. QED.

## 3. Gauge-quotient threshold for the full Boolean class

**Theorem 2.** For `n>=2`, on the full Boolean function class modulo `B_n`, the
smallest uniformly identifying intervention order is

```text
r_quotient = n-1.
```

**Proof.** At `r=n-1`, two Boolean functions with identical observations differ
by `c chi_[n]`, because the unobserved Walsh space is one-dimensional. Since a
Boolean truth-table difference takes values in `{-2,0,2}`, either `c=0` or
`c=+/-2`. In the latter case the pair is `chi_[n]` and `-chi_[n]`; flipping one
input coordinate relates them, so they are one `B_n` orbit. Hence the quotient
is identifiable.

For `r<=n-2`, choose parity functions of degrees `r+1` and `r+2`. Both have zero
observed coefficients, while signed coordinate permutations preserve parity
degree, so they lie in distinct `B_n` orbits. Thus the quotient is not
identifiable below `n-1`. QED.

This one-order reduction is a real effect of functional symmetry: a labelled
blind pair at order `n-1` becomes harmless only because its two members are the
same mechanism in the registered quotient.

## 4. Minimum-cost exact design

Give an intervention row fixing `S` the structural cost `|S|`. Restrict the
mechanism class to Fourier degree at most `k`.

**Theorem 3.** Among sets of distinct intervention rows, a
minimum-total-cost exact design contains `D(n,k)` rows and has total structural
cost

```text
C_min(n,k) = sum_(j=1)^k j binomial(n,j).
```

One optimum chooses the all-`+1` assignment once for every `S` with `|S|<=k`.

**Proof.** Rows of cost at most `j` span only the degree-at-most-`j` coefficient
subspace, of rank `D(n,j)`. Therefore any full basis can contain at most
`D(n,j)` independent rows of cost at most `j`. Writing total cost as the sum,
over `t=1,...,k`, of the number of basis rows with cost at least `t` gives the
lower bound

```text
sum_(t=1)^k (D(n,k)-D(n,t-1))
  = sum_(j=1)^k j binomial(n,j).
```

Choosing one all-positive row per `S` produces the subset-zeta matrix
`1[T subseteq S]`, which is triangular under any linear extension of subset
inclusion and has determinant one. It attains both the rank and cost bounds.
QED.

The optimum is an exact-identification statement, not a noise-optimality
statement. Its zeta inverse can amplify noise; the redundant all-assignments
design is therefore retained as a conditioning comparator.

## 5. Mechinterp interpretation

Singleton interventions expose only constant and first-order interaction
coordinates. If a behavior depends on order-`k` interactions, no attribution
score or number of additional singleton probes can recover those coordinates:
the missing directions lie in the exact measurement kernel. Coordinated edits
are not merely more statistical power; at the required order they change the
identifiable subspace.

For VPD, the corresponding design question is not "how many sites were
touched?" but "what interaction order and quotient-conditioned span did the
edits cover?" The theorem supplies a finite calibration object for that
question.

## Claim boundary

These are finite Walsh-analysis theorems under uniform parent environments,
perfect interventions, deterministic Boolean mechanisms, and a frozen parent
symmetry. They do not establish that transformer features form Boolean Fourier
coordinates, that a VPD edit implements a perfect intervention, or that the
minimum-cost exact design is sample-efficient under model noise. The registered
enumeration validates the bounded implementation and quotient census; it is not
the proof of the universal statements.
