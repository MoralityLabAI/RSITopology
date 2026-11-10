# BM-20: Exact parity-dual separation at bounded residual-support width

**10 November 2026 | constructive exact separation oracle, rational mask sparsification and a restricted LP complexity theorem.** Builds on [BM-19 support-aware completion](SUPPORT_AWARE_COMPLETION_BM19.md) after [BM-18 universal completion](UNIVERSAL_FOURIER_COMPLETION_BM18.md). The central structural object is the **residual Fourier support hypergraph** D over the m reported Boolean bits. Its hyperedges are the supports of the remaining unequal Fourier coefficients, after the initial masking policy is *frozen*.

This is standard max-sum variable elimination combined with the classical optimization–separation equivalence and Carathéodory support reduction. The mathematical specialization makes the BM-19 certificate algorithm explicit and testable. It does **not** solve arbitrary graph-specific adversarial masking, root-state attestation, or a fresh model-alignment problem.

## 1. Registered dual and separation problem

Take any two fixed Boolean observation laws F0=P0*Q0, F1=P1*Q1 from the BM-19 experiment. The independent common XOR postprocessor R must annihilate each remaining Fourier discrepancy indexed by

    D = {S subset [m], S!=empty : hatF0(S)!=hatF1(S)}.

The rational primal LP minimizes the maximum per-bit flip rate r of R:

    min r
    s.t. R(x)>=0, sum_x R(x)=1,
         sum_x R(x)*chi_S(x)=0        for S in D,
         sum_{x:x_i=1} R(x)<=r       for i in [m].      (1)

There are 2^m+1 primal variables, |D|+1 equality rows, and m marginal inequalities. Its exact rational dual has free y0 and y_S, signed z_i<=0 with -sum_i z_i=1, and one inequality for each mask x:

    F_y,z(x) =
       y0 + sum_{S in D} y_S (-1)^|S intersect x|
          + sum_i z_i x_i <= 0.                      (2)

A candidate dual is feasible iff max_{x in {0,1}^m} F_y,z(x)<=0. Any maximizing x with F_y,z(x)>0 is an exact violated-constraint witness. The dual objective y0 is a verified lower bound on the primal optimum when feasible.

## 2. BM-20/T1: a treewidth-controlled exact separation oracle

Define the primal interaction graph H(D) on the m **readout-bit indices**. For every Fourier support S in D, join all vertices of S into a clique. A dual can assign zero multipliers to some supports; its active interaction graph is the subgraph induced by those nonzero terms, so it can have smaller width than H(D).

The objective (2) is a sum of Boolean local factors:
- for each S with y_S!=0, a parity factor f_S(x_S)=y_S*(-1)^sum_{i in S}x_i;
- for each i with z_i!=0, a unary factor z_i*x_i;
- the constant factor y0.

Fix an elimination order v1,...,vm with **induced width w**, where the largest intermediate factor joins at most w+1 readout bits. For the first variable v, collect every factor that contains v and replace their sum by

    g(x_N)=max_{b in {0,1}} sum_{f containing v} f(x_N,v=b), (3)

with N the union of the collected factor scopes excluding v. All factors not containing v remain. Repeating (3) produces

    F_max = max_x F_y,z(x),                            (4)

because maxima over finite Boolean variables commute with addition of factors that do not contain the eliminated variable. Save one winning bit for each assignment to N at every elimination. Reversing the order reconstructs an explicit global maximizer x* and therefore a violated mask atom whenever F_max>0.

**Exact complexity:** with an order of induced width w supplied, this requires

    O(poly(m,|D|) 2^(w+1))

rational arithmetic operations and comparable bounded-width factor storage. Its bit complexity is polynomial in the encoded rational coefficients and intermediate factor sizes. The program uses Python fractions for *every* comparison, records its actual maximum joined scope and number of evaluated candidate assignments, checks the winning mask with a separate direct formula, and aborts before constructing any factor that exceeds a caller-set width/resource cap.

The [exact separation implementation](parity_width_separation_BM20.py) accepts arbitrary candidate BM-19 duals, includes a greedy min-fill order and also accepts an explicit order. **Min-fill is a heuristic** and supplies no guarantee of optimal w. The theoretical width bound is conditional on a supplied order or tree decomposition; it does not assume that the greedy order always finds minimum treewidth.

This is a classic weighted Max-XOR / valued-CSP dynamic program. Existing treatments of variable elimination and treewidth already establish its general algorithmic principle, for instance [Dechter's bucket-elimination framework](https://www.ccs.neu.edu/home/vip/teach/MLcourse/3_generative_models/materials/Murphy_GraphModel_Infer.pdf) and [Peyrard et al., exact/approximate inference and treewidth (2019)](https://doi.org/10.1111/anzs.12257).

## 3. BM-20/T2: exact LP optimization from bounded-width separation

The dual contains only |D|+m+1 scalar variables, even though its inequality collection is indexed by all 2^m Boolean masks. The max-sum oracle from T1 separates those inequalities exactly, while its simple sign and normalization constraints are checked directly.

The classical **rational optimization–separation equivalence** of Grötschel, Lovász and Schrijver implies the following **theoretical algorithmic corollary**:

> If D is supplied explicitly and the interaction graph H(D) has a provided elimination order of width w, the exact optimum of (1) and a matching rational primal/dual certificate can be computed in time polynomial in the explicit input bit length and 2^w.

The rational input matrix of (1) has entries in {-1,0,1}, so it has the standard polynomial bit-length bounds required to perform rational LP reconstruction. Strong LP duality equates the primal and dual optima. The statement is **FPT in the width of the explicit residual hypergraph**, when D itself is part of the input and a width-w order is provided. The currently committed program implements the exact **separation oracle**, *not* an ellipsoid optimizer or a general-purpose primal-recovery algorithm. Its exact primal witnesses in the tests are constructed independently.

The condition concerns H(D), **not the treewidth of the original gain graph**. BM-17's K4 can have a residual character containing all six edges, which creates a six-vertex clique in H(D). A chain of many two-bit residual supports has width one even if the original monitoring system had a different graph structure. Extracting D efficiently from an implicit graph in the first place remains a separate issue.

**Prior art:** [Grötschel–Lovász–Schrijver, *The ellipsoid method and its consequences in combinatorial optimization* (1981)](https://www.zib.de/userpage/groetschel/pubnew/paper/groetschellovaszschrijver1981a.pdf) and [*Geometric Algorithms and Combinatorial Optimization* (1988)](https://doi.org/10.1007/978-3-642-97881-4). The algorithmic polynomial-time consequence is an application of those established tools.

## 4. BM-20/T3: every feasible mask law has a sparse exact witness

Consider the moment vector for one mask x:

    v(x)=(1, (chi_S(x))_{S in D}, (x_i)_{i=1..m})
         in Q^(1+|D|+m).                             (5)

Every feasible probability distribution R has expected vector

    E_R v(x) = (1,0,...,0,p_1,...,p_m),              (6)

where the first block contains the normalization and all forced zero Fourier moments, and the last block contains the **exact individual flip marginals**.

By Carathéodory's theorem, (6) is a convex combination of at most

    1+|D|+m                                         (7)

of the points v(x) because all points have their first coordinate fixed to one. The resulting law has exactly the same required Fourier zeros and the same **per-bit** costs. Therefore any feasible mask distribution, including an optimal one, has an equally good witness with at most (7) nonzero mask atoms.

A constructive exact rational algorithm repeatedly selects 2+|D|+m positive-mass atoms, finds a nonzero affine dependence among their moment columns with fraction Gaussian elimination, moves along that null direction until one atom reaches probability zero, and repeats. Because every dependence has coefficients summing to zero, it has positive and negative coordinates. The move preserves (6), nonnegativity, normalizations, and the full cost vector. No approximation or rounding is used.

[The implementation](parity_width_separation_BM20.py) provides `sparsify_mask_law` and an independent `moment_fingerprint` control. It converts a nine-atom product mask law into at most seven atoms while preserving two Fourier parity zeros and all four edge marginals; another test compresses a **64-atom** dense law on six bits to at most ten atoms, preserving all registered moments and marginal probabilities.

The sparsity guarantee is **existential/constructive given an explicit starting law**. The rational support-reduction code runs on an explicitly represented distribution and can take exponential time if the source distribution itself is supplied as 2^m atoms. The GLS optimization–separation theorem is what supports a separate theoretical polynomial-time recovery route for bounded-width explicitly supplied D.

## 5. BM-20/T4: a solved infinite width-one family

Let m>=2 and D consist of every adjacent two-bit parity support

    D={ {i,i+1}: i=0,...,m-2 }.

This residual-support interaction graph is a path, hence it has treewidth **one**, and a natural left-to-right elimination order never joins more than two bits.

**Theorem:** the optimal additional common readout flip cap is **r*=1/4 for every m>=2**, despite the exponential 2^m raw mask space.

**Lower proof.** Pick any adjacent pair S={i,i+1}. Since hatR(S)=0, the observed parity of flips on that pair is odd with probability 1/2. Such an event requires at least one of those two bits to flip, giving

    1/2 <= p_i+p_(i+1) <=2r,
    r>=1/4.                                         (8)

**Attaining law.** Two-color the path alternately and let A and B be its two vertex-color classes. Choose R as:
- the zero mask with probability 1/2;
- the mask flipping every bit in A with probability 1/4;
- the mask flipping every bit in B with probability 1/4.

For every adjacent pair exactly one bit is flipped in each nonzero mask, so the parity expectation is 1/2-(1/4+1/4)=0. Every bit has error probability exactly 1/4. Thus r*=1/4.

A **one-character rational dual** with y0=1/4, y_S=-1/4 for any registered adjacent S, and z_i=z_(i+1)=-1/2 for that pair proves the same lower bound. The exact separator verifies its maximum slack is zero.

The same construction works for **any nonempty bipartite graph H of two-bit Fourier supports**, regardless of that graph's treewidth, by choosing the two color-class masks; the optimum is always 1/4. This shows that bounded width is **sufficient** for efficient general separation, while special algebraic structure can yield a compact exact answer even when H has large width. The code verifies the formula on paths and stars, including long cases with 256 readout bits without enumerating 2^256 masks. The supplied bipartite constructor rejects odd cycles; it does not assert that odd cycles cannot have other optimal mask laws.

## 6. Tests, verification and claim boundaries

- [BM-20 exact parity separation and sparsification](parity_width_separation_BM20.py).
- [BM-20 independent tests](test_parity_width_separation_BM20.py).
- Five existing BM-19 rational dual certificates are checked both by the new max-sum oracle and by exhaustive enumeration over their original 32/64 mask spaces. A deliberately falsified K4 certificate returns a **real violating mask and exact positive slack**.
- Seven independently seeded candidate-dual searches for each m=2..8 compare every DP optimum against direct 2^m enumeration and a second elimination order.
- A 128-bit path with 127 *active* parity factors, and a 256-bit path with a sparse active dual, keep maximum intermediate factor scope at **two bits**. The code records factor operations and the maximizing mask. These are tests of the *separation oracle*, not benchmark claims for a complete ellipsoid-based LP solver.
- Dense rational mask distributions are sparsified while maintaining every Fourier moment and bit marginal. Hostile malformed duals, invalid orders, nonbipartite input to the specialized constructor, and overwide factors are rejected.

### ASMP-14 consequence

BM-20 closes a carefully restricted piece of the certificate-width conjecture: **once the residual Fourier support D is explicitly available with bounded interaction width, the support-aware postprocessing LP has an exact FPT optimization route through a verified, finite, width-aware separation oracle**. This is directly relevant to choosing redundant monitoring observations whose remaining discrepancies are locally structured.

The still-open core problem starts *before* that step: construct or approximate D from a larger gain-graph monitoring problem without enumerating 2^m Fourier supports; jointly optimize the initial adversarial mask pairs and the intervention/audit policy; and establish a novel structural theorem under a frozen threat model. The work here is mathematical, uses classical tools, and provides no empirical AI alignment, model-control or trusted-restoration guarantee.
