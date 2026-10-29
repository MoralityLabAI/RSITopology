# Residual-cycle liveness and the bad-support allocation game

## Status

Development theorem draft. The residual-rank identity has been checked
against direct fiber enumeration on three graph families at one and two
trials per edge. The asymptotic allocation statement and exact finite
counterexample have executable rational checks. None is prospectively
registered yet.

## Setup

Let `G=(V,E)` be a finite loopless graph with a registered orientation and
incidence matrix `D`. Edge `e` receives `n_e>=1` independent Bernoulli
comparisons with probability `p_e`. For a realized count vector `y`, define:

```text
t = D^T y,
F_t = {x in Z^E : 0<=x_e<=n_e and D^T x=t},
S_t = span_R {x-z : x,z in F_t}.
```

The conditional experiment exposes the full reward quotient exactly when:

```text
dim(S_t)=beta_1(G).
```

## Theorem 1: residual-cycle rank

Construct the residual digraph `R_y` by placing:

```text
the forward arc of e when y_e<n_e,
the reverse arc of e when y_e>0.
```

Let `H_y` contain exactly the original edges whose endpoints lie in the same
strongly connected component of `R_y`. Then:

```text
dim(S_t)=beta_1(H_y).
```

In particular:

```text
dim(S_t)=beta_1(G)
```

if and only if every non-bridge edge of `G` lies on a directed residual
cycle.

### Proof

Fix `y` in `F_t`. A difference `x-y` is an integer circulation and respects
the residual signs: it can increase `e` only when the forward residual arc
exists and decrease `e` only when the reverse arc exists. Conversely, every
directed residual cycle can be augmented by one unit, producing another
point of `F_t`. Standard circulation decomposition therefore gives:

```text
S_t
  = image in R^E of the linear span of directed cycles in R_y.
```

Arcs outside strongly connected components lie on no directed cycle and can
be deleted. In the remaining residual graph, suppose `d` original edges are
bidirected. Its directed cycle-space dimension is:

```text
|E(H_y)| + d - |V(H_y)| + c(H_y).
```

The signed arc-to-original-edge map has exactly one independent kernel
direction for each bidirected edge: its directed two-cycle. Thus the image
dimension is:

```text
|E(H_y)| - |V(H_y)| + c(H_y)
  = beta_1(H_y).
```

Deleting bridges does not change cycle rank; deleting any original
non-bridge reduces it. This yields the full-rank criterion. QED.

The formula also proves that `beta_1(H_y)` is independent of which
representative `y` is selected from the fiber, even though the residual
digraph itself can change.

## Corollary 1: three-state compression

Fiber-rank liveness depends on each count only through:

```text
Z: y_e=0,
I: 0<y_e<n_e,
F: y_e=n_e.
```

The probabilities are:

```text
P_e(Z)=(1-p_e)^n_e,
P_e(F)=p_e^n_e,
P_e(I)=1-(1-p_e)^n_e-p_e^n_e.
```

Therefore exact full-quotient availability is a `3^|E|` finite reliability
polynomial rather than a product over every raw count.

## Theorem 2: endpoint reduction on a probability box

Let `A_G(n,p)` be full-quotient availability. For fixed values on all other
edges, let `a`, `b`, and `c` be the conditional liveness probabilities when
edge `e` has status `Z`, `F`, and `I`.

Changing `Z` or `F` to `I` only adds a residual arc, so:

```text
c>=a and c>=b.
```

Consequently:

```text
A_G(n,p_e)
  = c-(c-a)(1-p_e)^n_e-(c-b)p_e^n_e.
```

This is concave in `p_e`. Iteratively minimizing each coordinate proves:

```text
min over p in [epsilon,1-epsilon]^E A_G(n,p)
  = min over p in {epsilon,1-epsilon}^E A_G(n,p).
```

Thus the endpoint game used on one cycle remains exact on every finite graph
for this liveness event.

## Theorem 3: asymptotic allocation is a finite hypergraph game

Let `B_G` be the family of inclusion-minimal edge supports on which some
assignment of `Z/F` statuses, with every other edge `I`, makes the full
quotient unavailable. Call these the minimal bad boundary supports.

Consider positive integer allocations `n_e(N)` satisfying:

```text
sum_e n_e(N)=N,
n_e(N)/N -> w_e,
w in the probability simplex.
```

Let:

```text
Q_N
  = 1 - min over p in [epsilon,1-epsilon]^E A_G(n(N),p)
```

be worst-case unavailability, and put `r=1-epsilon`. For
`0<epsilon<=1/2`:

```text
lim_(N->infinity) -log(Q_N)/N
  = log(1/r) tau_G(w),

tau_G(w)
  = min over B in B_G sum_(e in B) w_e.
```

### Proof

For any endpoint choice, either boundary status on edge `e` has probability
at most `r^n_e`. Every bad status pattern contains an inclusion-minimal bad
subpattern. A union bound over the finite status universe therefore gives
the lower exponent:

```text
liminf -log(Q_N)/N
  >= log(1/r) min_B sum_(e in B) w_e.
```

For the reverse inequality, choose a minimizing support `B` and one of its
bad `Z/F` orientations. Nature selects each endpoint so the registered
boundary status has probability exactly `r^n_e`. Positive-weight complement
edges are interior with probability tending to one. Zero-weight complement
edges may be assigned arbitrary boundary extensions; removing residual arcs
cannot restore liveness, and their probabilities contribute only
`exp(-o(N))`. The chosen bad event therefore supplies the matching upper
exponent. QED.

Maximizing the exponent is the exact finite linear program:

```text
tau_G_star
  = max over w in simplex min over B in B_G sum_(e in B) w_e.
```

Its zero-sum dual is:

```text
tau_G_star
  = min over distributions mu on B_G
      max over edges e P_(B~mu)[e in B].
```

The dual gives short exact certificates: a distribution over bad supports
upper-bounds every allocation, while one primal weight vector meeting every
support proves attainment.

## Exact controls

### One cycle

For a simple `k`-cycle, the minimal bad supports are all two-edge subsets.
Uniform weights give support weight `2/k`. A uniform distribution over those
pairs includes every edge with probability `2/k`, so:

```text
tau_Ck_star=2/k
```

with the unique uniform primal allocation. This recovers the leading
exponent behind v0.15-v0.16.

### Five-edge theta graph

Take three internally disjoint paths between two terminals, with lengths:

```text
1,2,2.
```

Index the direct path by `0`, and the two length-two paths by `(1,2)` and
`(3,4)`. The six minimal bad supports are:

```text
{1,2}, {3,4},
{0,1,3}, {0,1,4}, {0,2,3}, {0,2,4}.
```

The primal weights:

```text
w=(0,1/4,1/4,1/4,1/4)
```

give every support weight `1/2`. The dual distribution assigning probability
`1/2` to `{1,2}` and `1/2` to `{3,4}` has maximum edge inclusion `1/2`.
Hence:

```text
tau_theta_star=1/2,
```

and the displayed primal vector is unique.

Uniform allocation has exponent only:

```text
2/5.
```

Thus one edge receives asymptotically zero budget even though it is
non-bridge and participates in both quotient cycles.

## Exact finite counterexample

At:

```text
epsilon=1/4,
N=10,
```

the uniform allocation gives:

```text
F_G(2,2,2,2,2)=218403/524288.
```

Full enumeration of all 126 positive labelled allocations gives exact
optimum:

```text
228591/524288,
```

attained by the four symmetry-related allocations:

```text
(1,3,2,2,2),
(1,2,3,2,2),
(1,2,2,3,2),
(1,2,2,2,3).
```

No allocation with counts differing by at most one is optimal. The exact gap
over uniform is:

```text
2547/131072.
```

This is the first general-graph obstruction to transferring the v0.16
balancing theorem.

## Claim boundary

The theorems concern full conditional-fiber rank under independent,
fixed-count Bernoulli comparisons on a known finite graph and a known
symmetric probability interior. The asymptotic result optimizes the
large-deviation exponent, not every finite-budget probability.

They do not cover adaptive allocation, dependent responses, unknown links,
downstream test power, behavioral validity, general inverse reinforcement
learning, or ASMP-9 resolution.
