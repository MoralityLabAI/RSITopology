# ASMP-9 v0.48 evidence-ordering theorem draft

## 1. Finite direct bounds

Let `Theta` and `X` be finite, let `P_theta` be an experiment on `X`, and let
`d:Theta -> R_+` be a declared decision risk. A direct upper confidence bound
`U:X -> R_+` is honest at level `1-alpha` when

```text
P_theta(d(theta) <= U(X)) >= 1-alpha
```

for every `theta`.

## 2. Buehler bound under a total order

Fix an ordering `pi=(x_1,...,x_m)` of the outcomes and write

```text
S_j={x_1,...,x_j}.
```

Among bounds nondecreasing along `pi`, the pointwise smallest honest bound is

```text
U_pi(x_j)
  = max {d(theta):P_theta(S_j)>alpha}.
```

The proof is the finite Buehler argument used in v0.47. If
`d(theta)>U_pi(x_j)`, then `P_theta(S_j)<=alpha`; conversely any smaller
nondecreasing value at `x_j` would make the complete prefix a noncoverage
event of probability greater than `alpha`.

## 3. Exact ordering objective

Freeze a positive reference law `w` on `X`. The expected reported upper bound
is

```text
C_d(pi)=sum_j w(x_j)U_pi(x_j).
```

For a prefix set `S`, define

```text
B_d(S)=max {d(theta):P_theta(S)>alpha}.
```

Then ordering optimization is a finite subset dynamic program:

```text
DP_d(S)
  = min_{x in S} [
      DP_d(S without {x}) + w(x) B_d(S)
    ],
DP_d(empty)=0.
```

For at most nine outcomes, v0.48 instead exhausts every permutation and
retains every optimizer, providing a direct certificate against the dynamic
program.

## 4. No universal ordering in general

The Buehler theorem is conditional on an ordering; it does not make the
ordering intrinsic to the experiment. Given two decision risks `d_1,d_2`,
there may be no ordering minimizing both `C_d1` and `C_d2`.

An exact finite witness requires:

```text
argmin_pi C_d1(pi)
  intersect
argmin_pi C_d2(pi)
  = empty,
```

with strictly positive cross-regret under both objectives. Such a witness
proves that selecting a confidence ordering without declaring downstream use
can be decision-suboptimal even when the statistical experiment is fixed.

This is not a surprising new theorem: loss-dependent optimal procedures are
standard decision theory, and Buehler limits are known to depend on their
ordering. The ASMP-9 contribution, if the registered channel witness passes,
is to make the ordering an explicit part of the value-access certificate and
measure its exact decision cost.

## 5. Relation to v0.47

At a unique minimum atom `x_0`, every ordering placing `x_0` first gives the
same mandatory-atom modulus

```text
max {d(theta):P_theta(X=x_0)>alpha}.
```

Thus v0.47 is ordering-independent at its one registered endpoint. Beyond the
first outcome, prefix unions couple the confidence budget and ordering choice
becomes live.

## Claim boundary

The finite Buehler construction, subset recursion, and loss-dependence are
classical. A finite census can establish only that one registered experiment
has incompatible decision-optimal orderings. It cannot establish a universal
impossibility for all reward-access experiments, identify an optimal
continuous statistic, validate a real preference channel, or resolve ASMP-9.
