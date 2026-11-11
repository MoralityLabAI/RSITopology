# BM-16: Exact bounded-separator Fourier elimination on arbitrary gain graphs

**10 November 2026 | exact algorithm and finite verification.** The purpose is to continue beyond the special two-terminal, series-parallel structures of [BM-14](PATH_ORBIT_LP_BM14.md) and [BM-15](SERIES_PARALLEL_GAIN_TRANSFER_BM15.md). This method works on **arbitrary finite gain graphs**, including K4 and networks with more complex separators. It is an application of classical sum-product/factor elimination to a registered Boolean gain-monitor statistic, rather than a novel general inference algorithm.

## 1. Model and quantity

Fix a finite oriented edge-occurrence multigraph G=(V,E), labels in K=F2^s, q=|K|, and edge shifts c_e in K. Draw a fresh uniformly random labeling a in K^V. For selected edge set S subset E define the full-observation Walsh coefficient

    W_c(S) = E_a[prod_(e in S)(1-2 X_e(a))],
    X_e(a)=1[a(v_e)-a(u_e)=c_e].                      (1)

For each edge create a factor

    psi_e(a_u,a_v) = 1-2 1[a_v-a_u=c_e],            e in S.

Edges outside S contribute the constant factor one. The expectation in (1) is the uniform average of the product of all selected factors. Loop edges are allowed and become one-variable constant factors as appropriate.

We also need **conditional boundary signals**. Given a registered set of boundary vertices B subset V and a fixed assignment a_B=b, define

    W_c(S|b) = E_[a_(V\B) uniform] [
                    prod_(e in S) psi_e(a_u,a_v) | a_B=b]. (2)

These boundary tables can be joined by dynamic programming across a graph separator. Their conditional law is invariant when all boundary labels are translated by the same gain, since only label differences matter.

## 2. BM-16/T1: exact variable elimination

Choose an elimination order v1,...,v_(n-|B|) of the nonboundary vertices. At each stage gather the factors involving the next vertex v, multiply them, and average uniformly over that vertex:

    psi_new(b_N) = (1/q) sum_(x in K)
                        prod_(f containing v) f(b_N,x),  (3)

where N is the union of their scopes excluding v. This replaces the gathered factors by one factor on N. A variable with no incident current factors averages the constant one and can be discarded.

**Exactness** follows from repeated finite-sum distributivity and the independence of the uniform vertex labels. Induction over eliminated vertices preserves (2); after all nonboundary vertices are removed, multiplying the remaining factors gives W_c(S|b). For empty B, the final result is W_c(S).

Define w to be the induced width of the chosen order on the selected-edge factor graph. Equivalently, the largest factor join involves at most w+1 vertex labels, with any retained boundary counted in the final table. The largest temporary joint assignment table then has at most

    q^(w+1) states,

and each elimination is performed by exact rational summation. A direct implementation evaluates one Walsh coefficient in

    O(poly(n,m) q^(w+1)) rational arithmetic operations,          (4)

with rational bit complexity depending polynomially on the input encoding and intermediate denominators. Stored factor tables require O(poly(n,m)q^w) entries, except when a boundary output q^|B| itself dominates. This is an exact **treewidth-style** computation. Its dependence on q can be large, especially for q=2^s with s stored in binary: when w>=2 it is exponential in the bit-length of q.

The [BM-16 implementation](separator_factor_transfer_BM16.py) exposes a greedy min-fill order, accepts any explicit valid order, reports the peak number of jointly enumerated variables, and returns exact conditional boundary tables. It also checks the expected global XOR translation invariance after reducing a boundary assignment by anchoring its first vertex label to zero.

## 3. Nonseries-parallel and separator controls

Tests include a K4 with four vertices, six edges and treewidth three. K4 has no two-terminal series-parallel decomposition of the BM-15 type. For q=4 and q=8, **every one of its 64 Walsh subsets** is compared against independent full-label enumeration. A Wheatstone bridge with four vertices and five edges is also tested with three boundary vertices, retaining a q^3 conditional table and comparing its q^(3-1) gauge-anchored entries against full enumeration.

For the q=4 K2,3 theta graph, min-fill removes the three degree-two intermediate vertices before the two terminals. This keeps the maximum joined scope to three variables, while an explicit poor order that eliminates one terminal first joins four variables. Both give the **same exact coefficient**, making the resource cost of separator order visible and testable.

A length-15 chain over q=32 supplies a larger control: the greedy order uses joined scopes of two variables and only q^2=1024 temporary assignments at each elimination. Its coefficient matches independently against BM-15's gain-spike transfer, without attempting any of the 32^16 full vertex labelings.

Finally, the nested TTSP graph from BM-15 is checked across **all 32 Walsh edge subsets** against the general factor-elimination method. This verifies that a general separator solver agrees with the specialized sparse gain-spike algebra wherever both apply.

## 4. Complexity and ASMP-14 scope

BM-11 decomposes articulation one-sums into independent erasure problems; BM-14 compresses the full adversarial erasure LP when a path-permutation symmetry is present; BM-15 and BM-16 compute **individual clean Fourier coefficients** on more general cyclic blocks.

These solve different resource questions. A bounded-width factor graph permits an efficient coefficient oracle for fixed q and width w, but the adversarial readout LP may still involve 2^m independent mask outcomes. Small separators by themselves **do not imply** that the complete mask-erasure optimization has polynomial size. BM-15's nested-branch negative control shows that even series-parallel structure may lack the exact edge-permutation symmetry used by BM-14.

**BM-16/C1 (open research question):** After factoring out articulation blocks, identify graph families with a declared separator-width bound and a restricted but meaningful adversarial mask grammar for which the full erasure LP has a polynomial-size exact or approximation-preserving representation. The theorem must provide a compatible upper mask law, a checkable weighted Fourier lower certificate, and an explicit accounting of alphabet bit-length, separator width and any assumed mask symmetries. A candidate counterexample could keep graph treewidth small while requiring exponentially many distinct mask-response classes.

The central distinction is between *statistical signal computation* and *minimax adversarial masking*. BM-16 resolves a finite-computation primitive and supplies tests for the more ambitious ASMP-14 certificate-width conjecture.

### Reproducibility and background

- [General factor-elimination implementation](separator_factor_transfer_BM16.py).
- [Independent BM-16 tests](test_separator_factor_transfer_BM16.py): K4, Wheatstone, q=4/q=8 full label comparisons, boundary gauge quotients, min-fill versus poor ordering, BM-15 cross-checks, loop edges, malformed inputs and q=32 chain.
- [BM-15 SP boundary algebra](SERIES_PARALLEL_GAIN_TRANSFER_BM15.md), [BM-14 path-orbit LP](PATH_ORBIT_LP_BM14.md).
- Standard mathematical antecedents include variable elimination and junction-tree message passing on bounded-treewidth graphical models, and series-parallel transfer-matrix treatments in statistical mechanics. [Potts/random-cluster background](https://www.statslab.cam.ac.uk/~grg1000/papers/tutte-grg.pdf) and [BM-09 theta proof](THETA_CYCLE_INTERACTION_BM09.md) provide relevant graph context.

All results use exact rational arithmetic and a CPU-only focused GitHub Actions workflow. No live behavioral model evaluation, GPU training, or certified real-world intervention was performed.
