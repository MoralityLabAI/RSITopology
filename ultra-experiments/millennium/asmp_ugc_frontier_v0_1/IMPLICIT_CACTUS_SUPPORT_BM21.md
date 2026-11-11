# BM-21: Implicit Fourier supports, cactus cycle circuits and a treewidth separation obstruction

**10 November 2026 | exact finite theorem family, independent controls and large symbolic counterexample.** This continues [BM-20 bounded residual-support-width separation](PARITY_WIDTH_SEPARATION_BM20.md) by investigating the earlier, previously open step of *extracting the residual Fourier support from a gain graph*. The result contains an exponential-output obstruction at graph treewidth two and an exact compressed solution on the cactus graph family.

This is an application of classical gain-graph switching, graphic-matroid rank, finite-group constraint counting, Boolean Fourier analysis and block-cut factorization. It establishes results only for the registered finite readout channels; it makes no novelty claim against the wider combinatorics literature or empirical claim about AI model behavior.

## 1. Frozen statistical model and Walsh discrepancy

Fix a simple connected graph G=(V,E) whose oriented edge occurrences have gains c_e in K=F2^s, with q=|K|=2^s. Every observation episode samples a fresh uniformly random labeling a:V→K. Its Boolean satisfaction vector is

    X_e(a)=1[a(v_e)-a(u_e)=c_e].

We compare the flat connection c=0 to the registered connection c, and denote their clean Boolean Walsh coefficient by

    W_c(S)=E_a[(-1)^(sum_(e in S)X_e)].

The clean Fourier discrepancy is

    Delta_c(S)=W_0(S)-W_c(S).

The BM-19 *post-readout* residual discrepancy also allows independent (from the current clean sample) hypothesis-aware correlated XOR mask laws Q0,Q1:

    Delta_Q(S)=W_0(S) hatQ0(S)-W_c(S) hatQ1(S).       (1)

An output support family D={S:Delta_Q(S)≠0} can have exponentially many members. The distinction between an **explicit enumeration of D** and a **compressed membership, counting and optimization certificate** is therefore material.

## 2. BM-21/T0: balanced-subgraph inclusion/exclusion on arbitrary gain graphs

For T⊆E, let r(T)=|V|-components(V,T), with isolated vertices counted in the component count. All constraints in T can be satisfied simultaneously iff every gain holonomy on a cycle of (V,T) is zero, i.e. the gain restriction is balanced. In that case, the event has probability q^(-r(T)), because an independent label for each component determines all its other vertex labels. In an unbalanced subgraph, that event has probability zero.

Expand the product ∏_(e∈S)(1-2X_e) to obtain the exact signed rank formula

    W_c(S) = sum_(T⊆S, T balanced) (-2)^|T| q^(-r(T)).  (2)

Every T is balanced for c=0, so subtracting gives

    Delta_c(S)=sum_(T⊆S, T unbalanced) (-2)^|T| q^(-r(T)). (3)

This immediately proves:

- **Necessary cycle containment:** a nonzero clean discrepancy requires S to contain at least one unbalanced cycle.
- **Minimal support seeds:** for any simple unbalanced cycle C of length L, no proper subset contains an unbalanced cycle, and

      Delta_c(C)=(-2)^L/q^(L-1) != 0.                 (4)

- **Possible cancellations:** containing an unbalanced cycle need not make Delta nonzero when several cycle terms interact.

The pure-stdlib [balanced-subgraph oracle](gain_balanced_inclusion_BM21.py) checks gain balance and graphic rank by weighted disjoint-set union and evaluates (2)/(3) by exact inclusion/exclusion, in O(2^|S| poly(|S|,|V|)) arithmetic. Its exponential dependence on |S| is explicit. Independent tests compare all 64 Walsh coefficients of the BM-17 K4 example with both the full uniform-label census and the BM-16 factor-elimination oracle.

## 3. BM-21/T1: exact cactus Fourier circuit

Suppose G is a **cactus**, meaning every edge belongs to at most one simple cycle; different cycles meet in at most one vertex. Let its cycle blocks be C1,...,Ck and let B denote its bridge edges. Write L_j=|C_j| and h_j=Hol_c(C_j) in K, and define

    alpha=1-2/q,
    A_L=alpha^L+(q-1)(-2/q)^L,
    F_L=alpha^L-(-2/q)^L.                              (5)

These are the full-L-cycle Walsh coefficients for zero and nonzero holonomy, respectively. For each selected edge subset S, write s_j=|S∩C_j| and b=|S∩B|.

**Exact factorization theorem:**

    W_c(S)= alpha^b * product_(j=1)^k f_(h_j,L_j)(s_j), (6)

with

    f_(h,L)(s) =
        alpha^s        when s<L,
        A_L            when s=L and h=0,
        F_L            when s=L and h!=0.

To prove (6), condition on the common vertex of any one-vertex sum. Each block's satisfaction law is invariant under global K-translation of its labels, so it is independent of that common vertex label. Repeatedly separating articulation blocks makes the complete satisfaction law a product of the independent cycle laws and Bernoulli(1/q) bridge bits. On a cycle any proper selected edge set is a forest, giving alpha^s, and the full-cycle value is (5).

Equation (6) is an exact arithmetic circuit with one factor per cycle and a bridge exponent. It evaluates W0(S), Wc(S) and Delta_c(S) for an arbitrary queried subset S in O(k) block arithmetic plus bit operations. It stores **no 2^|E| Fourier table**. For *arbitrary explicitly given* Q0,Q1, applying their mask Walsh transforms to (6) gives an exact post-readout residual-membership oracle for (1), without complete label enumeration.

The [cactus circuit module](cactus_fourier_cones_BM21.py) discovers all fundamental cycles of a supplied connected simple graph and rejects overlapping-cycle graphs such as K4 or K2,3. It uses a spanning tree plus one path query for each non-tree edge, with polynomial extraction time. The registered circuit requires the full cactus premise; the standalone inclusion/exclusion oracle is available for other graphs.

## 4. BM-21/T2: exponentially many discrepancies at treewidth two

Consider a frustrated triangle C with t additional **bridge edges** forming an attached tree. The graph has

    |E|=t+3,  |V|=t+3,  treewidth(G)=2.

Only the triangle carries nonzero holonomy. Equation (6) gives for every S⊆E

    Delta_c(S) =
       (-2)^3/q^2 * alpha^|S\C|   if C⊆S,
       0                            otherwise.       (7)

At q=4, alpha=1/2 and (7) simplifies to

    Delta_c(S)=-(1/2)*(1/2)^|S\C|  if C⊆S.          (8)

Since alpha≠0 when q>2, the residual support for **identity readout masks** is exactly the upward Boolean cone

    D={S⊆E : C⊆S};  |D|=2^t.                         (9)

At q=2, alpha=0; the exact residual support consists only of C, illustrating an alphabet-sensitive change in observation geometry.

An explicit support list for (9) is exponential even though membership is the constant-size requirement `(S & cycle_mask)==cycle_mask`. There is also a separation-width obstruction: because **the entire edge set E belongs to D**, the clique expansion of the *full* residual Fourier hypergraph has an m-vertex clique and treewidth **m−1=t+2**, while the original gain graph's treewidth stays two.

The committed large fixture takes **t=250** and q=4. It has 253 vertices and 253 observed edges, and the symbolic circuit returns the exact support count 2^250 and the nonzero full-edge coefficient `-1/2^251` without constructing a Fourier table or enumerating any of the 4^253 vertex labelings. Tests confirm cone membership and rejection of explicit exponential mask expansion.

This demonstrates a genuine limit of using the **original graph's treewidth** as a proxy for the treewidth or *explicit size* of its Fourier discrepancy support. It does not establish hardness of every implicit support-completion problem: this very family has a small closed-form solution.

## 5. BM-21/T3: an exact q=4 cactus support formula, including cancellations

When q=4, alpha=1/2, and the two full-cycle Fourier values in (5) obey:

    L odd:  A_L=-F_L !=0;
    L even: A_L>0, F_L=0.                             (10)

All proper-cycle Fourier factors and all balanced-cycle factors remain nonzero. Let O be the frustrated **odd** cycles and E_even the frustrated **even** cycles. Then

    Delta_c(S) != 0

holds **exactly when** either some C in E_even is fully contained in S, or the number of cycles C in O fully contained in S is odd. This is a compact Boolean formula of size O(k); it accounts for exact cancellation among fully selected frustrated odd cycles.

For example, two frustrated triangles attached at an articulation vertex each have 2^3=8 selected-edge subsets, with seven proper subsets and one full subset. The six-edge Fourier discrepancy vanishes when **both** triangles are fully selected, because their q=4 full-cycle sign reversals cancel. The entire residual support has **14** selected-edge subsets, computed and independently verified.

There is also a closed-form **exact support count**, with no enumeration. Put `B_count=|B|+sum_(C balanced)|C|`, let `l_j` be lengths in O and `e_i` lengths in E_even. Define

    N_even_odd =
      [ 2^(sum_j l_j) + product_j (2^(l_j)-2) ] / 2.

The number of Fourier indices with *zero* discrepancy is

    N_zero = 2^(B_count) * product_i(2^(e_i)-1)
                              * N_even_odd.         (11)

Thus

    |D|=2^|E|-N_zero.                                (12)

Empty products equal one. The expression uses polynomially many integer operations and bit lengths O(|E|), even when the answer counts exponentially many indices. The [implementation](cactus_fourier_cones_BM21.py) verifies every index on small q=4 cactus examples containing both odd and even frustrated cycles, balanced cycles and bridges.

## 6. BM-21/T4: sharp common and hypothesis-aware erasure costs

The large Fourier support in section 4 still admits a short **common** postprocessor. For each frustrated cactus cycle C of length L, independently choose:

    R_C=0 mask                 with probability 1/2,
    R_C=one uniformly chosen edge of C  with total probability 1/2.

Every edge of that cycle is flipped at rate 1/(2L); bridge edges and balanced cycles are untouched. The mask is current-clean-sample-independent and is the same under both hypotheses. Its exact Fourier transform is

    hatR(S)=prod_(C frustrated)
                       [1-|S∩C|/|C|].               (13)

For each block, any clean Fourier difference requires **all** of the edges of a frustrated cycle to appear in S. At that point the corresponding factor of (13) is zero. Thus every residual discrepancy is annihilated, even if D has 2^250 members. The complete output laws are equal by Walsh inversion.

**Optimal common-channel theorem:**

    r*_common(G,c;q)
       = max_(C frustrated) 1/(2|C|),                (14)

with value zero when all cycles are balanced. To prove the lower bound, fix any frustrated cycle C. Its clean difference on the exact cycle character is nonzero by (4). An arbitrary common XOR mask erasing that difference must have hatR(C)=0, hence odd error parity on C with probability 1/2. Union bound then gives

    1/2 <= sum_(e in C) Pr(R_e=1)
        <= |C| max_e Pr(R_e=1).

Equation (13) attains the maximum of these lower bounds. Correlated masks across blocks cannot reduce (14). The [symbolic common-mask verifier](cactus_fourier_cones_BM21.py) checks the block-local character identity for every possible selected-edge count in each cycle, without listing all residual supports.

The same lower bound has an extremely sparse **exact BM-19 dual certificate**. Select the shortest frustrated cycle C of length L and set

    y0=1/(2L), y_C=-1/(2L),
    z_e=-1/L for e in C, and z_e=0 otherwise.

For any mask x containing k flipped bits on C, its dual slack is

    [1-(-1)^k]/(2L) - k/L <=0.                       (15)

Checking k=0..L suffices for **every** mask on all m edges. The 253-edge fixture has a dual with only the three-bit triangle Fourier character active. BM-20's exact max-sum separator verifies this dual using joined factors on at most **three Boolean bits**, induced active width two. The *full* discrepancy hypergraph still has width 252. This is the clearest current example of why **active certificate width** and the structure of implicit support descriptions may be more appropriate complexity parameters than raw residual-support width.

Under the wider BM-08 adversary, the two worlds may choose **different** mask laws. BM-11 articulation-factorization and BM-08's sharp single-cycle theorem give the stronger cactus-level exact identity

    eta_sym(G,c;q) =
        max_(C frustrated) eta_star(q,|C|),          (16)

where `eta_star` is the exact state-aware cycle threshold, with the maximum of an empty set defined as zero. Projection to each cycle proves the lower bound even against arbitrary joint correlated world-specific masks, and products of BM-08's attaining cycle masks give the upper bound.

For q=2 or 4, (16) equals (14). For q>=8, the state-aware cactus cap can be **strictly smaller**. Two frustrated triangles over q=8 have common erasure cost 1/6 but the exact state-aware cap is 1/14. The module constructs both independent world-specific mask distributions and verifies every Walsh output equality. The independent tests also compare complete Boolean output distributions by direct uniform-label enumeration on this q=8 example.

This distinction is essential: (9) and (12) describe the clean or identity-mask Fourier support, while (16) optimizes fully hypothesis-aware adversarial masks and need not retain that original support.

## 7. Reproducibility, exact claims and next ASMP-14 frontier

New committed modules:
- [cactus_fourier_cones_BM21.py](cactus_fourier_cones_BM21.py): cactus extractor, factored Fourier coefficients, exact q4 residual-support membership/counting, sparse readout-mask residual queries, common and hypothesis-aware optimal mask constructions, symbolic full-erasure proof and one-character dual.
- [gain_balanced_inclusion_BM21.py](gain_balanced_inclusion_BM21.py): general balanced-subgraph inclusion/exclusion oracle with exact weighted disjoint-set consistency.
- [test_cactus_fourier_cones_BM21.py](test_cactus_fourier_cones_BM21.py): direct independent full-label census for q=2,4,8 unicyclic and multicycle cactus examples; K4 and K2,3 rejection; double-triangle Fourier cancellation; exact q4 counting; nontrivial world-specific masks; factorized complete-output check; symbolic 253-edge/2^250 discrepancy case; and BM-20's width-two certificate.

The most important boundary is now explicit: **small original graph treewidth does not imply a small explicit Fourier discrepancy support or small full-support hypergraph width**. A tractable implicit support representation can still exist, and some exponential-support families have constant-size primal/dual certificate descriptions.

A stronger future ASMP-14 claim should freeze a class of **compressed Fourier-support grammars** and the allowed sparse/factored mask channels, then prove extraction, separation and optimal mask recovery within stated time and bit-complexity bounds. The cactus family supplies a positive algebraic benchmark with a provable exponential-output negative control. Extending this to 2-connected networks with overlapping cycles and to authenticated, costly interventions remains open.

**Prior mathematics:** gain-graph switching and balanced-cycle theory are classical; see [*On cospectrality of gain graphs*](https://doi.org/10.1515/spma-2022-0169), as well as [Jenssen, Patel and Regts, *Improved bounds for the zeros of the chromatic polynomial via Whitney's Broken Circuit Theorem* (2024)](https://doi.org/10.1016/j.jctb.2024.06.005) for related graphic-subgraph inclusion/exclusion. BM-21 is a specialized finite observation-model theorem, with no claim to have resolved a new general complexity class, the Unique Games Conjecture, or a real-world AI monitoring guarantee.
