# ASMP-1 finite identifiability seed: result v0.1

## Outcome

All eight registered gates passed on the exact bounded enumeration. The
universal finite-chain statement is established by the proof in
`THEOREM_v0_1.md`; the enumeration is an implementation and finite-universe
check, not the proof of the universal statement.

The run was bound to preregistration commit
`9ab2af6379fcfd2ba0f1c80476fb2d7d901b62e7`. It checked:

- 60 `(input size, hidden size, output size)` configurations;
- 147,638 deterministic mechanisms, including 33,542 with surjective hidden
  maps;
- 4,380 unrestricted-plus-surjective observation signatures;
- 3,288,302 explicit hidden-label gauge transformations; and
- zero disagreements with the registered Stirling-partition formula.

The result receipt SHA-256 is
`FFCC2C03B9F79DB8A75C8382F5C436365BB9CFF7F9C248A05C8F13F46279758F`.

## The mathematical result

For a deterministic finite chain

```text
X --h--> H --g--> Y,
```

with all input environments and all perfect hidden-state interventions observed,
hidden labels remain a global `Sym(H)` gauge. For each output `y`, let

```text
n_y = |{x : g(h(x))=y}|,
k_y = |g^-1(y)|.
```

The compatible mechanism orbits are exactly independent partitions of each
labelled environment fiber into at most `k_y` blocks. Their count is

```text
product_y sum_(j=0)^k_y S(n_y,j).
```

When `h` is required to be surjective, the count is

```text
product_y S(n_y,k_y).
```

Consequently, when `|X|>=2`, for fixed `g` and the unrestricted class of all
upstream `h`, full hidden interventions identify every `h` exactly when `g` is
injective. Cut coverage supplies access, but downstream response separation
supplies identifiability.

## Two exact obstructions

### 1. Downstream state aliasing

The registered `|X|=4, |H|=3, |Y|=2` construction has surjective `g` and two
surjective upstream maps with identical natural outputs and identical complete
hidden-intervention responses. They occupy distinct gauge orbits because they
induce different labelled-input partitions. The signature has exactly three
compatible surjective mechanism orbits, as preregistered.

This falsifies the bare statement that intervening on every state of a causal
cut is sufficient to identify the upstream mechanism.

### 2. Singleton interventions miss higher-order interactions

For an observed Boolean mechanism with `n` Boolean parents, passive output count
plus every singleton-perfect-intervention count has exact design rank `n+1` in
the `2^n`-dimensional truth-table space. At `n=3`, the registered pair has:

- shared count signature `(3,1,2,1,2,1,2)`;
- exact rank/nullity `4/4`;
- every parent essential;
- influence multisets `(1,3,3)` versus `(3,3,3)`; and
- a truth-table difference exactly in the design kernel.

Thus even complete singleton-site coverage need not identify a multi-parent
mechanism. It observes the constant and first-order Boolean subspace while
leaving higher-order interactions unresolved.

## What changes for mechanistic interpretability

The useful object is not intervention coverage alone. It is the conditioning of
an intervention design on the mechanism class after quotienting functional
symmetries. The finite seed suggests replacing a cut-count criterion with
**intervention-design tomography modulo functional symmetry**:

1. freeze the permitted mechanism class and gauge;
2. define a representative-independent quotient observation metric;
3. require quotient injectivity for exact identification; and
4. require a positive, normalized quotient separation modulus for stable noisy
   recovery.

For VPD-style edit discovery, the immediate implication is concrete: a family
of individually visible or attributable sites may still fail to span the
interaction directions that distinguish mechanisms. The next useful experiment
should compare intervention families by their quotient-kernel dimension and
separation modulus, rather than by the number of sites touched.

A concrete next seed is **interaction-order tomography**: for degree-bounded
Boolean or finite-field mechanisms, sweep designs that intervene on parent
subsets of size at most `r`, and compute exact quotient rank and a normalized
quotient-secant modulus. Under uniform Boolean Fourier coding, the sharp target
is that uniform recovery of a degree-`k` class turns on at `r=k`; noisy planted
mechanisms then test the associated sample-complexity transition. This directly
asks when coordinated multi-site VPD edits reveal structure that singleton edits
provably cannot see.

## Claim boundary

This result proves an elementary theorem for deterministic finite chains and
verifies two finite counterexamples exactly. It does not establish that a
transformer circuit is represented by this chain, resolve noisy or
sample-limited identifiability, identify latent counterfactual/noise couplings,
or resolve the generic analytic ASMP-1 problem. It is a closed theorem seed and
a falsification of two overly broad measurement heuristics.

## Receipt

- Protocol SHA-256:
  `F0A7244C6DCAE567C008E8884649192CBDFD7917E48C8ED1FB095DFEA28B0779`
- Runner SHA-256:
  `107CB8AB75D2FD530AC69658B81166184AEAF88FBA678901FF70AC473F8BAF14`
- Theorem SHA-256:
  `036E4A752A2F5035EFC4D7DB0F5CA08AB238D55ED5160314136C5EED39E0E005`
- Result SHA-256:
  `FFCC2C03B9F79DB8A75C8382F5C436365BB9CFF7F9C248A05C8F13F46279758F`

The exact argv, environment, per-configuration census, fixture checks, gates,
and committed-blob bindings are stored in `artifacts/result_v0_1.json`.

Local Git history records the registration commit before the result commit, and
the runner verified the committed blobs before and after enumeration. The
registration commit was not pushed or externally timestamp-anchored before the
run, however, so the archive proves byte binding but does not independently
prove preregistration chronology to an external observer.
