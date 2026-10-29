# ASMP-9 capped-simplex modulus theorem draft v0.63

Status: **unregistered theorem development; not claim eligible**.

## 1. Frozen stochastic-choice fiber

Let the alternatives be `X={a,b,c}`.  Freeze the binary responses

```text
p(a|ab)=2/5,
p(a|ac)=3/5,
p(b|bc)=3/5.
```

The binary Luce cycle defect is

```text
|(2/5)(3/5)(2/5) - (3/5)(2/5)(3/5)| = 6/125,
```

so no completion of this binary fiber is Luce.

Let

```text
x=(x_a,x_b,x_c)=p(.|abc).
```

In lexicographic ranking order

```text
(abc, acb, bac, bca, cab, cba),
```

the unique ranking-mixture weights compatible with the fixed binary and
full-menu responses are

```text
(
  3/5-x_b,
  2/5-x_c,
  3/5-x_a,
  2/5-x_c,
  2/5-x_a,
  3/5-x_b
).
```

They sum to one.  Therefore the kernel is a random-utility model exactly when

```text
x_a<=2/5,
x_b<=3/5,
x_c<=2/5.
```

Write

```text
u=(2/5,3/5,2/5),
P={x in Delta_3: x_i<=u_i for every i}.
```

Fix a probability floor `alpha=1/10` and `0<gamma<=1/50`.  Define

```text
P_alpha={p in P: p_i>=alpha},

V(q)=sum_i (q_i-u_i)_+,

N_(alpha,gamma)
  ={q in Delta_3: q_i>=alpha and V(q)>=gamma}.
```

Every member of `P_alpha` is non-Luce RUM.  Every member of
`N_(alpha,gamma)` is non-RUM.

## 2. Exact projection theorem

For every positive full-menu law `q`,

```text
dist_TV(q,P)=V(q).
```

### Lower bound

Let

```text
E(q)={i:q_i>u_i}.
```

For every `p in P`,

```text
TV(p,q)
  = sum_(i:q_i>p_i) (q_i-p_i)
  >= sum_(i in E(q)) (q_i-p_i)
  >= sum_(i in E(q)) (q_i-u_i)
  = V(q).
```

### Attainment

Replace every `q_i>u_i` by `u_i`, removing exactly `V(q)` probability mass.
The total unused cap outside `E(q)` is

```text
sum_(i notin E(q)) (u_i-q_i)
  = sum_i u_i - 1 + V(q)
  = 2/5 + V(q).
```

It therefore exceeds the removed mass.  Redistributing the removed mass
among coordinates outside `E(q)` produces a point in `P` at TV distance
exactly `V(q)`.  If `q_i>=alpha`, the redistribution only raises untouched
coordinates, so the projection also lies in `P_alpha`.

Thus `V` is not merely a regularity witness on this fiber: it is the exact
distance to stochastic rationalizability.

## 3. Exact additive modulus

Define

```text
Delta_(alpha,gamma)
  = min_{
      p in P_alpha,
      q in N_(alpha,gamma)
    } TV(p,q).
```

The projection theorem gives `Delta>=gamma`.  Equality is attained by

```text
p*=(2/5,3/10,3/10),

q*=(2/5+gamma, 3/10-gamma/2, 3/10-gamma/2).
```

Both points respect the floor for `gamma<=1/50`, and

```text
TV(p*,q*)=gamma.
```

Hence

```text
Delta_(alpha,gamma)=gamma.
```

The fixed per-menu Huber threshold inherited from v0.59 is

```text
epsilon*=gamma/(1+gamma).
```

At equality the common observed distribution is

```text
r_i=max(p*_i,q*_i)/(1+gamma).
```

## 4. A support formula for multiplicative separation

For positive distributions define

```text
rho(p,q)=max_i max{p_i/q_i,q_i/p_i}.
```

Fix `p in P_alpha` and `q in N_(alpha,gamma)`.  Let

```text
E=E(q),
U_E=sum_(i in E) u_i,
d=V(q).
```

Because `q(E)=U_E+d<=1`, every feasible violation support satisfies `U_E<1`.
Aggregate ratios imply

```text
max_(i in E) q_i/p_i
  >= q(E)/p(E)
  >= (U_E+d)/U_E,

max_(i notin E) p_i/q_i
  >= p(E^c)/q(E^c)
  >= (1-U_E)/(1-U_E-d).
```

Therefore

```text
rho(p,q)
  >= L(U_E,d)
  :=max{
       1+d/U_E,
       (1-U_E)/(1-U_E-d)
     }.
```

Both terms increase in `d`, so `d>=gamma` gives the support-specific lower
bound `L(U_E,gamma)`.

For the cap vector `(2/5,3/5,2/5)`, the only feasible nonempty violation
supports have

```text
U_E in {2/5,3/5,4/5}.
```

Their exact lower bounds are

```text
U_E=2/5:
  L=max{1+(5/2)gamma, (3/5)/(3/5-gamma)}
   =1+(5/2)gamma,

U_E=3/5:
  L=max{1+(5/3)gamma, (2/5)/(2/5-gamma)}
   =(2/5)/(2/5-gamma),

U_E=4/5:
  L=max{1+(5/4)gamma, (1/5)/(1/5-gamma)}
   =(1/5)/(1/5-gamma).
```

The first equality uses `gamma<=1/5`; the other two comparisons hold for
every positive admissible `gamma`.  Moreover,

```text
1+(5/2)gamma
  < 1/(1-(5/2)gamma)
  <= (2/5)/(2/5-gamma),

1+(5/2)gamma
  < (1/5)/(1/5-gamma).
```

Thus the global support minimum is achieved by violating exactly one of the
two coordinates whose RUM cap is `2/5`.

## 5. Exact bounded-recording modulus

Define

```text
Lambda_(alpha,gamma)
  = min_{
      p in P_alpha,
      q in N_(alpha,gamma)
    } rho(p,q).
```

The support formula gives

```text
Lambda_(alpha,gamma)>=1+(5/2)gamma.
```

The same pair `(p*,q*)` from Section 3 attains equality:

```text
q*_a/p*_a=1+(5/2)gamma,

p*_b/q*_b
  =p*_c/q*_c
  =(3/5)/(3/5-gamma)
  <=1+(5/2)gamma.
```

Consequently,

```text
Lambda_(alpha,gamma)=1+(5/2)gamma.
```

The exact bounded outcome-recording boundary inherited from v0.60 is

```text
u/ell=1+(5/2)gamma.
```

Equality is confusable and remains `boundary_inconclusive`, never a pass.

## 6. What is stronger than v0.62

Version v0.62 evaluated the moduli on two chosen line segments.  Version
v0.63 evaluates them over:

- the entire two-dimensional, floor-truncated RUM polygon compatible with the
  fixed binary menus; and
- every floor-truncated non-RUM full-menu law whose exact distance from that
  polygon is at least `gamma`.

The multiplicative result is not obtained by inspecting one chosen pair.  It
requires exhausting the three possible violated-facet sums and proving which
support controls the global optimum.

## Proof debt before registration

1. Independently reconstruct the six ranking weights from the five observable
   degrees of freedom.
2. Exhaustively verify the projection formula on an exact rational grid.
3. Verify every support lower bound and both primal common-observation
   constructions on fresh rational gamma cells.
4. Review the result against the ARSP/RUM-polytope minimum-distance
   literature and robust-testing geometry.
5. Do not promote the formula into a claim about hidden choice sets,
   strategic response, or physical query access.

## Claim boundary

This is an exact calculation on one full-dimensional three-alternative
fixed-binary fiber.  Its RUM-polytope, distance, and likelihood-ratio
ingredients are classical convex geometry.  It is not a general algorithm
for arbitrary random-utility polytopes, a minimax robust-choice theorem, an
empirical result, a welfare theorem, or a resolution of ASMP-9.

