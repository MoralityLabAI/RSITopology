# Claim packet: `asmp2.crossed_shift` v0.1

## Plain-language claim

Spanning every local shift direction does not by itself certify safety over a
global deployment region. A hidden crossed term can vanish, together with its
first derivative, on an axial source design while becoming safety-relevant
away from the axes.

## Formal proposition

For `s in {-1,+1}` and `theta=(theta_1,theta_2) in [-1,1]^2`, let

```text
L_s(theta) = 1/2 + (theta_1+theta_2)/16
                   + s theta_1 theta_2/8.
```

Let `E_axis` contain the origin and the four signed half-axis points. Then:

1. `L_+=L_-` on `E_axis`, and their gradients agree at the origin.
2. For `0<=t<=1`,
   `sup_(||theta||_infinity<=t) |L_+(theta)-L_-(theta)|=t^2/4`.
3. The global ambiguity at `t=1` is `1/4`.
4. At `(1,1)`, `L_+=3/4` and `L_-=1/2`, which lie on opposite sides of the
   registered threshold `3/5`.
5. Adding the diagonal point `(1/2,1/2)` separates the worlds by `1/16`.

For the registered observation model with independent `Z1`, `Z2`, and `Y`,
the Fisher information at the origin is

```text
I_0 = [[5/64, 1/64],
       [1/64, 5/64]].
```

Its exact eigenpairs are `((1,-1),1/16)` and `((1,1),3/32)`, so the local
score experiment spans both coordinates and has minimum Fisher-norm gain
`kappa=sqrt(1/16)=1/4` in the frozen Euclidean parameter coordinates.

## Proof

The loss difference is

```text
L_+(theta)-L_-(theta)=theta_1 theta_2/4.
```

It vanishes on either coordinate axis, as does its derivative at the origin.
On the infinity ball, `|theta_1 theta_2|<=t^2`, with equality at every corner,
proving items 1–3. Direct substitution proves items 4–5.

For a Bernoulli variable with probability `p(theta)`, Fisher information is
`grad(p) grad(p)^T/[p(1-p)]`. At the origin all three probabilities are `1/2`.
The gradients are `(1/8,0)`, `(0,1/8)`, and `(1/16,1/16)`. Summing their three
outer products divided by `1/4` gives `I_0`. Multiplication by the two stated
vectors proves the eigenpairs without numerical whitening.

## Liveness and controls

- A matched unspanned source line with hidden term `s theta_2/8` has ambiguity
  `t/4`, exposing a first-order failure.
- Removing the crossed term gives zero ambiguity.
- A third unspanned coordinate that changes a nuisance observation but is
  discarded by `Q(theta_1,theta_2,phi)=(theta_1,theta_2)` does not block the
  risk-relevant rank.
- Acting has utility `1>=4/5`; abstention has utility `0<4/5`.
- Signed coordinate permutations preserve the infinity ball and the absolute
  crossed monomial.

## Evidence and application boundary

The proposition is elementary and analytically forced. The computation is an
implementation calibration and certificate-format test. A passing run may
provide a `shift_span_certificate` fixture to the HRMmmm evaluation planner.
It does not support a general local-to-global theorem, active-design claim, or
resolution of ASMP-2.
