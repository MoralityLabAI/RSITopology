# ASMP-9 v0.20 registered result: exact block factorization

## Verdict

```text
finite_block_factorization_established_in_frozen_model_v0_20
```

All 10 registered gates passed.

This establishes the frozen finite theorem only. It does not solve the exact
local design problem inside a general biconnected block and does not resolve
ASMP-9.

## The theorem

For the independent-binomial conditional-access object inherited from
v0.17-v0.19, delete no data but ignore original bridge edges in the reward
quotient. Partition the remaining cyclic edges into the nontrivial
vertex-biconnected edge blocks `B_1,...,B_q`.

For every ternary residual edge-status vector:

```text
full quotient liveness on G
iff
the residual digraph induced by every B_j is strongly connected.
```

The proof is by the block-cut forest. A path leaving a block and first
returning to it cannot return at a different articulation vertex: that would
create a simple undirected cycle using an outside edge and a block edge,
contradicting maximal biconnectivity. Every global path between vertices of a
block can therefore be projected into that block by deleting its outside
excursions.

Under independent edge responses:

```text
F_G(n, labels)
  = product_j F_Bj(n restricted to B_j, labels restricted to B_j).
```

For the registered rectangular endpoint-label adversary:

```text
min_labels F_G(n, labels)
  = product_j min_(labels on B_j) F_Bj(n_Bj, labels_Bj).
```

Once exact block-local maximin tables `f_B(t)` are supplied, exact allocation
between blocks is a product Bellman recursion. No efficient construction of
`f_B` for a general overlapping-cycle block is asserted.

## Fresh exhaustive evidence

The four registered status censuses checked:

| Graph | Edges | Ternary states | Mismatches |
|---|---:|---:|---:|
| multiport diamond | 11 | 177,147 | 0 |
| theta--bridge--triangle | 10 | 59,049 | 0 |
| bridge-separated cycles | 9 | 19,683 | 0 |
| chorded seven-cycle | 8 | 6,561 | 0 |
| **Total** |  | **262,440** | **0** |

For every state, four paths agreed:

1. implementation direct liveness;
2. implementation blockwise liveness;
3. independent full-graph reachability with brute bridge detection; and
4. independent blockwise reachability using an exponential simple-cycle
   union decomposition.

All six registered Tarjan block partitions also matched the independent
decomposition and the frozen expected partitions.

## Exact probability products

At `epsilon = 2/9`, both fixed-label cells agreed exactly:

| Graph | Direct availability | Block product |
|---|---:|---:|
| multiport diamond | `10136591385792256 / 150094635296999121` | same |
| theta--bridge--triangle | `16009463249024 / 205891132094649` | same |

The complete rectangular-label cell on a triangle joined to a pentagon gave:

```text
global worst = product of blockwise worsts
             = 677766526472 / 22876792454961.
```

All `2^8 = 256` global endpoint-label assignments were evaluated. There were
four minimizing label vectors.

## Bridge control

The bridge-separated graph had bridge indices `{3,8}`. Across all 2,187
nonbridge status patterns, changing either bridge through all three residual
statuses caused zero liveness changes.

Changing only the two bridge counts from `(1,1)` to `(7,5)` and flipping both
bridge labels also left exact availability unchanged:

```text
156207688 / 3486784401.
```

## Exact finite allocation

The registered design graph joins an eight-edge chorded seven-cycle block to
a triangle. With total budget 12, there are 11 positive edge allocations.

Bellman recursion and the complete edge-allocation census returned the same
exact value:

```text
5800816 / 3486784401.
```

They returned the same seven optimizers. In every optimizer:

- the triangle remains at its positive-count floor;
- the chord edge remains at its floor; and
- the one extra trial is assigned to one of the seven rim edges.

This is a finite-cell design result, not a general closed form for chorded
blocks.

## Binding negative control

The chorded seven-cycle alone has one nontrivial block. Its direct and
one-factor product values agree:

```text
13121047912 / 282429536481.
```

The required interpretation is:

```text
factor_count_one_no_within_block_computational_simplification
```

Thus v0.20 does not manufacture a decomposition benefit on the irreducible
case.

## Resources

```text
wall time       34.743555 seconds
peak resident   30,740,480 bytes
GPU used        false
registered caps 180 seconds / 1,073,741,824 bytes / CPU-only
```

The resource gate passed with substantial margin.

## Integrity

```text
implementation freeze
  21da5b7aa04aa5f8ad1e70da0aff8da3f69b2bb0

registration commit
  8487edad48ba302cbf3d71192df593f2480842ca

registration SHA-256
  a26ef3900087416df5ba92e5c85fd23006ea35f3677ebeb98f5f2cb4fd7ede60

protocol SHA-256
  1c19bbd52e52243712fdd8c48728f5093365f30581ad2adc78dbed3afd317140

result SHA-256
  bd626d1ad1da1299ff05fd0be415acdffd264b561278a941e094982f8ad9394c
```

The independent verifier imports neither the implementation module nor the
runner. It passed all 14 checks, including the 22-file seal, hash chain,
complete status equivalence, exact products, design optimizer set, gate
mapping, and verdict mapping.

## Prior-art boundary

Biconnected decomposition, reliability multiplication over blocks, and
separable Bellman allocation are classical. The contribution here is the
exact translation of the registered conditional reward-access object into
those ingredients, with the irreducible local block exposed rather than
claimed solved.

## Claim boundary

This result does not establish:

- an efficient exact local-design algorithm or hardness classification for a
  general biconnected block;
- adaptive comparison allocation;
- dependence, contamination, strategic response, or link-misspecification
  robustness;
- downstream decision improvement;
- behavioral reward identification for humans or models;
- a general inverse-reinforcement-learning theorem; or
- a resolution of ASMP-9.
