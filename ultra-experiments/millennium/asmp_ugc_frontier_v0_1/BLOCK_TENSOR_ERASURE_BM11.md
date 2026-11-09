# BM-11: Exact articulation-block tensorization and sparse Fourier dual lifting

**10 November 2026 | finite theorem with independent integer controls.** This extends [BM-09 theta interaction](THETA_CYCLE_INTERACTION_BM09.md) and [BM-10 weighted Fourier diamond](WEIGHTED_FOURIER_DIAMOND_BM10.md). Gain-graph and random-cluster decompositions at articulation vertices are established mathematical structures; this note specializes them to the **registered adversarial Boolean-readout erasure objective**.

## 1. Fixed statistical model

Let G=(V,E) be a finite directed edge-occurrence graph, with K=F2^s, q=|K| and a fixed gain connection c in K^E. For every episode sample a uniformly random labeling of its vertices. The monitor sees only the full Boolean satisfaction vector X_e=1[a(v)-a(u)=c_e]. We compare the flat world c=0 against this specific c.

The readout adversary knows whether the world is flat or frustrated and may choose separate distributions Q0,Q1 on XOR masks over all E, independent of the **current** clean satisfaction vector. Each edge's marginal flip probability must be at most a common eta. Correlations within each mask, between graph blocks, and with the hidden hypothesis are allowed. Define

    eta_sym(G,c;q)=min{eta: exists admissible Q0,Q1 with
                           P0*Q0=P1*Q1 as complete Boolean laws}.

The one-episode target and noise contract are exactly those of BM-08/09/10; this theorem asserts nothing about live-model state restoration, uncertain root identity, or adversarial coupling to the current clean sample.

## 2. Theorem BM-11/T1: articulation-one-sum erasure tensorization

Suppose A and B are edge-occurrence graphs with one designated vertex each. Form G=A vee B by identifying only those vertices, retaining their disjoint edge sets. Let c_A and c_B be connections on A,B, and let c be their union.

**Exact theorem:**

    eta_sym(A vee B,c_A vee c_B;q)
       = max(eta_sym(A,c_A;q), eta_sym(B,c_B;q)).       (1)

**Proof of statistical factorization.** Conditional on the common vertex receiving any particular label k, the remaining vertex labels in A and B are independent uniform variables. The satisfaction pattern in either block depends only on **differences** of vertex labels, so translating every label in one block by a fixed group element leaves its satisfaction pattern unchanged. Its conditional pattern law is therefore independent of k. Consequently the full clean Boolean vector has exactly the product law under **each hypothesis**:

    P_h^G(x_A,x_B)=P_h^A(x_A) P_h^B(x_B),  h=0,1.     (2)

**Lower bound.** Suppose an arbitrary, possibly cross-block-correlated, hypothesis-aware pair (Q0,Q1) equalizes the full masked G observation law. Project both outputs onto A. The projected mask is just the A-marginal of Q_h, remains independent of the current clean A observation, and respects all per-edge flip caps. Thus it is an admissible erasing channel for A. Hence eta>=eta_sym(A). Repeat with B.

**Upper bound.** Choose attaining mask pairs on A and B with caps eta_A and eta_B, and form their **product distributions** separately under each hypothesis. Convolution of product clean laws with product masks is a product of the two already equalized block output laws. Every edge marginal in the product mask equals its block marginal, so the joint cap is max(eta_A,eta_B). Finite compactness gives attaining channels, and (1) follows.

Induction over a block-cut tree gives the same maximum-over-blocks rule for finite **1-sums of edge-disjoint cyclic blocks**, even when several meet at articulation vertices. Bridge edges are additional acyclic blocks: their satisfaction bits are independent Bernoulli(1/q) and carry no flat-vs-shift information, so they can be attached without changing the optimum. The result includes disconnected unions by direct independence as well.

This theorem establishes an exact **block-decomposition algorithm** for the fixed erasure LP: solve only its 2-connected blocks, then take the largest cap. The general full-graph LP has 2^(|E|) mask variables per hypothesis. Blockwise computation involves only the independent subproblem sizes, and the construction can compose their solutions. Dense interaction costs can therefore arise within a 2-connected block, as BM-09/10 showed, while articulation structure adds no further minimax overhead.

## 3. Theorem BM-11/T2: lifting a block-local Fourier dual

Consider the usual finite erasure LP in the Walsh basis. A lower-bound dual certificate for block A has equality multipliers y_S indexed by subsets S of E(A), normalization multipliers y_norm0,y_norm1, and marginal multipliers z_(h,e) for e in E(A). The dual objective lower-bounds eta_sym(A).

Lift this certificate to G=A vee B by setting the same y_S for S contained entirely in E(A), setting all coefficients involving B edges to zero, and extending z by zero on B. Equation (2) gives

    hat P_h^G(S)=hat P_h^A(S)       for S subset E(A).

Every full-mask dual inequality at m=(m_A,m_B) therefore equals the original block-A inequality evaluated at m_A. The eta coefficient and normalization objectives are unchanged. Thus a valid block dual is a **valid global dual with identical value and the same nonzero Fourier support**.

This is a constructive, compact lower-bound certificate for any graph containing a hard block as a one-sum component. It does not claim that sparse certificates must exist inside arbitrary 2-connected blocks.

## 4. Worked exact experiment: diamond vee theta

Glue the q=4 BM-10 five-edge diamond to the q=4 BM-09 six-edge contrabalanced theta at one vertex. The combined graph has

    vertices=8, edges=11, beta1=4, alphabet q=4.

The diamond's exact erasure cap is 1/5, and the theta's is 1/6, so (1) proves the **eleven-edge exact optimum**

    eta_sym(diamond vee theta;4)=max(1/5,1/6)=1/5.    (3)

The [standalone Python module](block_tensor_erasure_BM11.py) independently enumerates all 4^8=65536 complete vertex labelings in each world and compares all 2^11=2048 complete pattern counts against the tensor product of the two block count tables. The match is exact after accounting for the shared vertex's uniform group symmetry.

The achieving readout mask uses the product of:
- the diamond's q=4 common distribution with denominator 20 and five edge marginals 4/20=1/5;
- the theta's q=4 common distribution with denominator 12 and six edge marginals 2/12=1/6.

This gives a joint mask law with denominator **240**, support size **110**, and exact per-edge marginal numerators

    (48,48,48,48,48,40,40,40,40,40,40)/240.

The verifier checks complete output equality for all 2048 observed patterns, with integer arithmetic, independently from the conceptual proof. The largest marginal is exactly 1/5.

**Independent sparse dual.** BM-10's existing diamond certificate has 17 nonzero Walsh multipliers, two normalization multipliers and five marginal multipliers. The [lifted verifier](block_tensor_erasure_BM11.py) checks that the global 11-edge Fourier coefficients on those 17 subsets agree with the local diamond values, using independent full labeling enumeration. It then checks all **2*2048=4096** global dual mask-atom inequalities by extending the local dual, with no new Fourier multipliers. The lower objective remains 1/5, completing an exact primal/dual certification of (3).

This supplies an example where a graph's cycle rank grows from two to four and its mask space from 32 to 2048, while the optimal lower certificate retains its original 17 Fourier terms. In fact, arbitrary additional one-sum blocks with smaller erasure cap preserve the same lifted certificate size.

## 5. Limits, conjecture and admission gate

The exact one-sum rule is a decomposition theorem; related independence and factorization phenomena are standard in the theory of Tutte/Potts/random-cluster invariants and biased graphs. Its research value here is to isolate the genuinely difficult objects for **ASMP-14:** cyclic blocks sharing **edges**, where BM-09's K2,3 theta and BM-10's diamond show additional masking cost.

**Refined BM-11/C1:** fix an explicit graph class, group alphabet, weighted cycle-intersection graph and allowable Fourier-dual support family. Determine whether the global erasure LP on each 2-connected block admits a provably good sparse or fixed-parameter-size weighted Fourier dual, with certificate complexity bounded in terms of its **internal cycle-overlap width**, rather than total cycle rank or the number of articulation blocks.

A legitimate novel theorem would require a frozen width parameter, bit-complexity bounds, a universal approximation ratio, and adversarial counterexamples. The BM-11 factorization gives a provable reduction to individual blocks, while BM-10's zero-Fourier-only counterexample prevents unsupported support-only approximations.

### Sources and reproducibility

- [BM-11 exact oracle and lifted dual](block_tensor_erasure_BM11.py).
- [Six targeted tests](test_block_tensor_erasure_BM11.py): nonzero-root vertex sums, 4^8 joint labeling census, 2048-pattern convolution, lifted 4096-inequality dual, multi-block associativity and malformed mask contracts.
- [BM-10 weighted diamond dual](WEIGHTED_FOURIER_DIAMOND_BM10.md), [BM-09 theta theorem](THETA_CYCLE_INTERACTION_BM09.md).
- Related classical background: [Zaslavsky, gain-graph balanced chromatic polynomials](https://people.math.binghamton.edu/zaslav/Tpapers/gaingraphs-lecture-notes.pdf), [Fortuin–Kasteleyn expansion of the Potts model](https://mathworld.wolfram.com/PottsModel.html), and [block decomposition in graph reliability](https://arxiv.org/abs/1305.0972).

All verification uses the standard library, exact integers/Fractions, and the five-minute CPU GitHub Actions workflow. No empirical AI-safety or model weights are implicated.
