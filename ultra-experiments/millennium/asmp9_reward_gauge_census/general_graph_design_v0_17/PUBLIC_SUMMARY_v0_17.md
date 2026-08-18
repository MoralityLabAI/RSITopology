# ASMP-9 v0.17: residual-cycle liveness and graph-aware allocation

## Result

The one-cycle rule “balance trial counts across edges” does not extend to
general comparison graphs.

Version v0.17 gives the replacement for the registered independent Bernoulli
comparison model:

1. conditional-fiber rank is exactly the cycle rank of the residual-live
   subgraph;
2. every edge count compresses without loss to the three statuses
   `zero/interior/full`;
3. worst-case probabilities on a symmetric interior box occur at its
   endpoints;
4. minimal bad boundary supports determine the large-deviation exponent; and
5. the maximin asymptotic allocation is the primal solution of a finite
   hypergraph game, certified by a matching dual distribution over bad
   supports.

The prospectively registered fresh run passed all ten gates. An independent
implementation passed 41 checks, and a clean detached replay reproduced every
scientific payload field.

## The residual-rank theorem

Let `G=(V,E)` have registered edge orientations. Edge `e` receives `n_e`
Bernoulli comparisons and realizes count `y_e`. Conditioning on the vertex
balance `t=D^T y` gives the fiber

```text
F_t = {x in Z^E : 0 <= x_e <= n_e and D^T x=t}
S_t = span_R{x-z : x,z in F_t}.
```

Construct the residual digraph by retaining the forward arc of `e` when
`y_e<n_e` and the reverse arc when `y_e>0`. Let `H_y` contain the original
edges whose endpoints lie in one residual strongly connected component. Then

```text
dim(S_t) = beta_1(H_y).
```

Thus the complete reward-gauge quotient is available exactly when every
original nonbridge edge lies on a directed residual cycle.

The proof is a circulation decomposition. Feasible fiber differences are
precisely the images of residual circulations. Directed cycles span the
circulation space inside the residual strongly connected components. Each
bidirected original edge contributes one directed two-cycle to the kernel of
the signed arc-to-edge map, leaving image dimension

```text
|E(H_y)| - |V| + c(H_y) = beta_1(H_y).
```

This also proves that the value is independent of which count representative
of the conditional fiber is used.

## Exact probability reduction

The residual graph depends on a count only through

```text
Z: y_e=0
I: 0<y_e<n_e
F: y_e=n_e.
```

For comparison probability `p_e`,

```text
P(Z)=(1-p_e)^n_e
P(F)=p_e^n_e
P(I)=1-(1-p_e)^n_e-p_e^n_e.
```

For fixed statuses on all other edges, write `a,b,c` for liveness after fixing
the selected edge to `Z,F,I`. Adding the missing residual arc cannot destroy a
cycle, so `c>=a,b`, and

```text
A(p_e)=c-(c-a)(1-p_e)^n_e-(c-b)p_e^n_e
```

is concave. Coordinatewise minimization therefore reduces the full
probability box `[epsilon,1-epsilon]^E` exactly to its endpoint labels.

Fresh direct raw-binomial and ternary calculations agreed:

| graph | raw probability | ternary probability |
|---|---:|---:|
| five-node wheel | `2395953994/3486784401` | `2395953994/3486784401` |
| theta `(1,3,3)` | `1529775/11529602` | `1529775/11529602` |
| four-cycle with bridge tail | `13923/62500` | `13923/62500` |

Across six fresh capacity cells, all 3,852 count representatives in 1,900
conditional fibers satisfied the residual-rank identity, with zero
representative-invariance failures.

## The graph-aware allocation game

Let `B_G` be the inclusion-minimal edge supports on which some `Z/F`
orientation destroys full quotient liveness while all other edges are
interior. If fixed-total allocations satisfy

```text
n_e(N)/N -> w_e
```

and `0<epsilon<=1/2`, worst-case unavailability `Q_N` obeys

```text
lim_(N->infinity) -log(Q_N)/N
  = log(1/(1-epsilon)) tau_G(w),

tau_G(w)=min_(B in B_G) sum_(e in B) w_e.
```

The optimal exponent is the finite zero-sum game

```text
max_(w in simplex) min_(B in B_G) sum_(e in B) w_e
 =
min_(mu over B_G) max_e P_(B~mu)[e in B].
```

Matching exact primal and dual certificates gave:

| graph | optimal support exponent | allocation structure |
|---|---:|---|
| six-cycle | `1/3` | uniform |
| four-cycle with bridge tail | `1/2` | uniform on cycle, zero on bridge |
| theta `(1,3,3)` | `1/3` | zero on direct edge, uniform on six long-path edges |

The theta control is the decisive obstruction. Uniform weights give only
`2/7`, because a two-edge failure inside either long path is cheaper than the
three-edge supports involving the direct path. The allocation game therefore
spends asymptotically no budget on an edge that is nonbridge and belongs to
two quotient cycles.

## Prospectively registered finite counterexample

The frozen stress test used theta path lengths `(1,3,3)`, total budget `N=14`,
and `epsilon=2/7`. All `C(13,6)=1716` positive labelled allocations and all
endpoint labels were enumerated exactly.

Uniform allocation:

```text
(2,2,2,2,2,2,2)
value = 3557696000/13841287201
      ~= 0.257035054
```

Exact optimum:

```text
value = 25309152000/96889010407
      ~= 0.261217984
```

The exact gap is

```text
405280000/96889010407 ~= 0.004182931,
```

or about `1.627%` relative to uniform. There are six optimizers:

```text
(1,3,2,2,2,2,2)
```

and the five permutations moving the `3` among the other long-path edges.
Every optimizer assigns one trial to the direct edge; no balanced allocation
is optimal.

## Verification

- implementation freeze: `f6bb525ff62aea1c9d2c3c1674090063c819a65b`
- prospective registration: `0297fcddbe34ea028597fe60b0d3cb849deabfaf`
- registration SHA-256:
  `fc0931d34707dad22481e34c3fb50b686978e444828adbd1fd9686b599813b1b`
- registered gates: `10/10` pass
- independent checks: `41/41` pass
- clean detached focused tests: `11/11` pass
- primary run: `81.56` seconds, `24,076,288` peak resident bytes
- clean replay: `78.84` seconds, `24,137,728` peak resident bytes
- GPU use: none

The first proposed “fresh” house graph was detected before freeze as
isomorphic to the burned theta `(1,2,3)` development graph. It was replaced
with a five-node wheel, and graph-isomorphism freshness became a registered
gate.

## Prior art and novelty boundary

Residual networks, circulation decomposition, flow-space dimensions,
reliability polynomials, minimal cut sets, and reliability allocation are
classical. The prior-art gate therefore does not claim a new general network
flow or reliability theorem.

The contribution is their exact composition for this conditional
reward-gauge ledger, plus a prospectively registered finite counterexample to
transferring the single-cycle balance rule. The sealed prior-art record is
[`PRIOR_ART_GATE_v0_17.md`](PRIOR_ART_GATE_v0_17.md).

## Claim boundary

This result concerns full conditional-fiber rank under independent,
fixed-count Bernoulli comparisons on a known finite graph and a known
symmetric probability interior. The asymptotic result optimizes the
large-deviation exponent, not every finite-budget probability.

It is not an adaptive allocation theorem, a dependent-response result, an
unknown-link result, a downstream testing-power theorem, general inverse
reinforcement-learning identification, evidence about human preferences, or
a resolution of ASMP-9.

The next load-bearing work is to characterize exact finite-budget allocation
on general graphs and then test whether adaptivity or response
misspecification changes the bad-support game.
