# ASMP-9 v0.47 sharp atom-modulus theorem draft

## 1. Setting

Let `Theta` be a finite parameter class, `X` a finite sample space, and
`P_theta` the calibration law under parameter `theta`.  A deterministic
confidence procedure `C:X -> 2^Theta` is honest at level `1-alpha` when

```text
P_theta(theta in C(X)) >= 1-alpha
```

for every `theta`.  Freeze one observed atom `x0`.

## 2. Mandatory-atom lemma

Every honest deterministic confidence procedure satisfies

```text
{theta : P_theta(X=x0) > alpha} subset C(x0).
```

Proof: if `theta` is omitted from `C(x0)`, the noncoverage event contains
`{X=x0}` and therefore has probability greater than `alpha`.

The strict inequality is necessary.  A point with atom probability exactly
`alpha` may be omitted while retaining coverage exactly `1-alpha`.

## 3. Pointwise sharpness

Define

```text
C*(x0) = {theta : P_theta(X=x0) > alpha},
C*(x)  = Theta for x != x0.
```

For a parameter outside `C*(x0)`, noncoverage can occur only at `x0` and has
probability at most `alpha`.  Hence `C*` is honest and the mandatory set is
attained exactly.

For any registered nonnegative decision-risk functional `d(theta)`, every
confidence-set-based certificate at `x0` must therefore report at least

```text
M_alpha(x0;d)
  = max_{theta : P_theta(X=x0) > alpha} d(theta),
```

and `C*` attains this value.  On a finite class this is an exact lower and
upper modulus, not a parameter-radius proxy.

The spike construction is deliberately useless away from `x0`.  It proves
pointwise attainability but is not the operational confidence procedure used
for the successor.

## 4. Nonvacuous Buehler extension

Freeze a finite ordered statistic `T` and let

```text
F_theta(t) = P_theta(T <= t).
```

For the scalar risk `d(theta)`, define

```text
U(t) = max {d(theta) : F_theta(t) > alpha}.
```

Then `U` is nondecreasing and

```text
P_theta(d(theta) <= U(T)) >= 1-alpha
```

for every `theta`.  To see this, let `t*` be the largest statistic value with
`U(t*)<d(theta)`.  The definition of `U` forces
`F_theta(t*)<=alpha`, so the noncoverage event has probability at most
`alpha`.

The bound is smallest among nondecreasing honest upper bounds based on the
registered statistic.  If another bound `V` had
`V(t)<d(theta)` while `F_theta(t)>alpha`, monotonicity would make every outcome
up through `t` a noncoverage event of probability greater than `alpha`.

When `x0` is the unique minimum-statistic atom,

```text
{T <= T(x0)} = {x0},
```

and `U(T(x0))` equals the mandatory-atom modulus exactly.  Thus the all-zero
result is the endpoint of a valid, nonvacuous confidence procedure over every
statistic value, not merely the output of the spike construction.

This is a finite Buehler-optimal confidence limit specialized to a
decision-risk functional.  The theorem is classical; novelty is not claimed.

## 5. Shared binary-channel specialization

For three independent calibration cells with allocations
`n=(n_root,n_left,n_right)`, flip parameters
`p=(p_root,p_left,p_right)`, and zero observed errors,

```text
P_p(X=0)
  = product_q (1-p_q)^n_q.
```

Consequently the mandatory image is

```text
sum_q n_q [-log(1-p_q)] < log(1/alpha),
```

intersected with the frozen finite parameter grid.  This region couples the
three rates.  It is neither the v0.45 independent generator rectangle nor the
v0.46 coordinatewise method-of-types box.

Use total observed calibration errors as the registered ordered statistic.
Its unique minimum is the all-zero count vector, so the v0.47 atom calculation
is exactly the minimum-statistic value of the Buehler bound.

## 6. Full decision propagation

For four-class loss, `d(p)` is the exact minimax risk of the complete
horizon-two 3,748-policy experiment.  For root-group loss, `d(p)=p_root`.
The v0.47 census computes `d(p)` once at every finite-grid channel and then
exhausts integer acquisition allocations by selecting the maximum over the
mandatory atom region.

The result is pointwise sharp among deterministic uniformly honest confidence
sets and Buehler-optimal among nondecreasing direct risk bounds based on the
registered statistic.  It is not a claim about average confidence-set volume,
Bayesian posterior risk, randomized confidence procedures, continuous
parameter classes, or optimal choice of statistic.

## 7. Resolution relevance

Versions v0.45-v0.46 optimized a confidence-valid construction and retained a
separate two-point parameter-radius benchmark.  The atom-modulus theorem
instead pushes the coverage obligation through the actual decision risk.  It
can therefore show exactly which part of the reported deficiency is forced by
uniform coverage and which part was introduced by the chosen concentration
or rectangular relaxation.

## Claim boundary

The mandatory-atom, spike-confidence, and Buehler arguments are classical
finite-sample confidence theory.  The candidate contribution is their exact
decision-relative specialization and executable audit inside the ASMP-9
access grammar.  A finite-grid result does not establish a continuous minimax
theorem, strategic robustness, real preference access, or resolution of
ASMP-9.
