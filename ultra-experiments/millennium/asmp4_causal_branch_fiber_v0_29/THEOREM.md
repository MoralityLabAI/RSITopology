# ASMP-4 causal successor-fiber branching theorem v0.29

## 1. Registered branching cost

For a finite realized port language `L(T)`, let `deg_L(p)` be the number of
successor symbols after a realized prefix `p`. Register the worst-path causal
branching cost

`B_T(L) = max_(ell in L(T)) sum_(t<T) log2 deg_L(ell[:t]).`

Equivalently, `2^{B_T(L)}` is the largest product of successor degrees along a
root-to-leaf path. This is the history-dependent branching metric used in v0.3,
not terminal log-cardinality.

## 2. Causal prefix morphism

Let `phi` map a target prefix tree `A` to a source prefix tree `S`. It is
registered to be length-preserving and extension-consistent: if `pa` extends
`p` by one target symbol, then `phi(pa)` extends `phi(p)` by one source symbol.

At target prefix `p`, define the local successor fiber

`m(p) = max_b |{a: phi(pa)=phi(p)b}|.`

For horizon `T`, define the maximum local-fiber path product

`F_phi(T) = max_(ell in A(T)) product_(t<T) m(ell[:t]).`

This is a prefix-local invariant. It is different from the maximum terminal
fiber of the full-word map used for language cardinality in v0.28.

## 3. Finite-horizon theorem

Every causal prefix morphism satisfies

`B_T(A) <= B_T(S) + log2 F_phi(T).`

### Proof

At a target prefix `p`, group its successor symbols by their source successor
image. Each group has at most `m(p)` members, and the image tree has
`deg_S(phi(p))` possible source successors. Therefore

`deg_A(p) <= m(p) deg_S(phi(p)).`

Multiply this inequality along any target leaf `ell`. The source-degree
product along `phi(ell)` is at most the maximum source branch product, and the
local multiplicity product is at most `F_phi(T)`. Taking `log2` and then the
maximum over target leaves proves the claim. QED.

The maximum is load-bearing. If `M` target successors map to one source
successor and one target successor maps to another, the minimum local fiber is
one while the target degree is `M+1` and the source degree is two.

## 4. Asymptotic transfer

For a safe strategy transfer whose port factor has a uniform profile `F_i(T)`,
define the directional local successor-fiber entropy

`nu_i = limsup_(T -> infinity) log2 F_i(T)/T.`

The target port branching rate is at most the source rate plus `nu_i`. Read and
write require separate profiles, and the reverse strategy transfer requires
separate reverse morphisms. Bidirectional subexponential local-fiber products
preserve the complete branching-cost region.

Uniformly bounded products are sufficient but not necessary. If local merging
occurs only at dyadic times, `F(T)=2^{bit_length(T)}` is unbounded but has zero
normalized logarithmic growth. A burst/rest schedule also shows that `limsup`
cannot be replaced by `liminf`.

## 5. Injective-terminal disclosure obstruction

Consider the target language

`A = {000,001,010,100}`

and the source image

`S = {000,001,010,011}`.

Use the causal edge map

- at the root, both target symbols map to `0`;
- after target prefix `0`, symbols `0,1` map to `0,1`;
- after target prefix `1`, its only successor `0` maps to `1`;
- at depth two, map the two successors after `00` to `0,1`, the only successor
  after `01` to `0`, and the only successor after `10` to `1`.

The full-word map is a bijection, so its terminal transcript fiber is one.
Nevertheless,

`B_3(A)=3,   B_3(S)=2,   F_phi(3)=2.`

The theorem is tight. Repeating this three-step block `k` times gives terminal
fiber one, branch costs `3k` and `2k`, and local-fiber product `2^k`. The
asymptotic gap is exactly one third bit per step. Terminal fiber entropy alone
therefore cannot transfer causal branching cost.

## 6. Clone sharpness

For a full `m`-ary target tree mapped locally to a deterministic source tree,
`m(p)=m` at every prefix. Hence `F(T)=m^T`, the target/source branch-cost gap is
`T log2 m`, and the asymptotic correction `log2 m` is attained.

## 7. Scope

This theorem supplies the factor-distortion law for worst-path uniform
branching cost. It does not establish the analogous law for the sequential
minimax prefix-free cost `P_T`; rounding in its Kraft recurrence requires a
separate proof. It also does not construct public quotients for arbitrary
nonlinear plants or compute adversarial multidimensional mean-payoff regions.
