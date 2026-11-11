# BM-23: Fixed-core edge subdivisions admit an exact polynomial-size erasure LP

**10 November 2026 | finite structural theorem and a sharp non-series-parallel K4 family.**

This extends the fixed-path theta [BM-14 orbit LP](PATH_ORBIT_LP_BM14.md), gain-balanced-subgraph [BM-21 Fourier identity](IMPLICIT_CACTUS_SUPPORT_BM21.md) and [BM-22 theta support circuit](IMPLICIT_THETA_SUPPORT_BM22.md) to **subdivisions of an arbitrary fixed gain-graph core**. In particular, the base graph can be K4, which is biconnected, has three independent cycles and lies outside two-terminal series-parallel topology.

The result concerns the explicitly registered hostile-readout model: fresh independent uniform vertex labels in K=F2^s, full Boolean edge-satisfaction reports, and possibly hypothesis-dependent correlated XOR readout-mask distributions **independent of the current clean report**, each with a common maximum marginal error cap eta. It is a classical orbit-symmetry/finite-LP and gain-balanced-subgraph calculation specialized to this observation model. A wider ASMP-14 structural monitoring theorem and independently authenticated intervention/audit promises remain open.

## 1. Fixed core and paths

Let H be a fixed finite oriented core graph on n0 vertices with k>=2 edge occurrences, each with distinct endpoints (parallel core edges are allowed). For each core edge e=(u,v), substitute a path of length L_e>=1 with fresh intermediate vertices not used in any other substituted edge. Each hypothesis h=0,1 assigns a total XOR gain g_(h,e) in K to the path; intermediate edge gains can be redistributed by gauge switching without changing the Boolean observation law.

The subdivided graph has

    m=sum_e L_e edges,
    n=n0+sum_e(L_e-1) vertices.

Define

    M=product_(e in E(H))(L_e+1).                    (1)

The class includes three-path theta networks when H is a two-vertex/three-parallel-edge core. It includes arbitrary edge subdivisions of K4, Wheatstone bridge cores and fixed-size higher-treewidth cores.

## 2. BM-23/T1: the exact fixed-core Fourier transfer

For any selected Walsh edge subset S of the m reported Boolean bits, let s_e be the number of selected edges on path e and let

    J(S)={e:s_e=L_e},
    b(S)=sum_(e notin J(S)) s_e,
    alpha=1-2/q.

Conditional on the core endpoint labels a(u),a(v), the residual values on a replacement path are uniform among all length-L_e vectors satisfying their total XOR condition. In particular, a selected **proper** subset of path edges has independent satisfaction indicators of probability 1/q, with Fourier factor alpha^s_e.

When all L_e path edges are selected, its terminal-conditional factor is

    f_e(d)=A_e+B_e*1[d=g_(h,e)],                     (2)

where d=a(u) XOR a(v) and

    A_e=alpha^L_e-(-2/q)^L_e,
    B_e=(-2)^L_e/q^(L_e-1).

Conditional on all core vertex labels, the different replacement paths have disjoint internal vertices, so their selected-edge Fourier factors multiply. Thus

    W_h(S)=alpha^b(S)*F_h(J(S)),                      (3)

where F_h(J) is the uniform-core-label average of the product of the full-path factors (2), over e in J.

**Gain-balanced core-subgraph expansion.** Expand each full-path factor into its A term and its B delta term. For a core edge subset T⊆J, the simultaneous endpoint equations `a(u) XOR a(v)=g_(h,e)` have probability

    Pr[all T endpoint constraints] =
        q^(-r_H(T)) if the gain restriction g_h|T is balanced,
        0 otherwise,

where r_H(T)=n0-components_H(T), including isolated core vertices. It follows that

    F_h(J) =
      sum_(T⊆J, gain-balanced under h)
         q^(-r_H(T))
         prod_(e in T) B_e
         prod_(e in J\T) A_e.                        (4)

Equations (3)/(4) compute **any exact clean Boolean Walsh coefficient** without enumeration over the q^n vertex labelings of the subdivided graph, and without looping over the q^n0 core labelings. They use at most 2^|J| gain-balanced subgraph terms for a specified J, or 3^k terms when all 2^k full-path subsets J are computed. The [implementation](core_subdivision_orbit_BM23.py) uses a weighted disjoint-set gain-balance/rank check on the fixed core, together with exact rational products.

### Exact support counting

For q>2, alpha is nonzero. Thus W0(S)-W1(S) vanishes iff F0(J(S))-F1(J(S)) does. Each completely selected path contributes exactly one edge subset; each *properly* selected path contributes (2^L_e-1) possibilities. Hence

    |D_clean| =
      sum_(J:F0(J)!=F1(J))
        prod_(e notin J)(2^L_e-1),                   (5)

which evaluates from 2^k fixed-core states even when |D_clean| itself is exponential in m.

For q=2, alpha=0. Only the *empty proper-path selection* survives for each e outside J, so the corresponding factor in (5) is one. The [module](core_subdivision_orbit_BM23.py) implements this distinction explicitly.

The result generalizes BM-22's support-count formula to cores containing overlapping cycles with more than two terminal vertices. Unlike a universally bounded-treewidth Fourier solver, the formula exploits a *fixed number of independently subdivided core edges*. Its exponential dependence on k remains explicit.

## 3. BM-23/T2: exact full hostile-readout LP orbit reduction

The crucial additional symmetry is at the level of the **complete Boolean law**, beyond individual Walsh coefficients.

Conditional on its two fixed core endpoint labels, every replacement path's XOR residual vector is uniformly distributed over the affine parity class of total XOR g_(h,e). Permuting the L_e residual positions preserves this class, so it preserves the entire Boolean zero-indicator law on that path. Different replacement-path interiors are conditionally independent given all core labels. Averaging core labels therefore preserves joint invariance under

    Gamma = product_(e in E(H)) S_(L_e).              (6)

The clean Boolean laws P0,P1 are invariant under Gamma.

Given ANY successful hypothesis-aware mask pair Q0,Q1 that equalizes the complete output laws, average each Q_h separately under Gamma. The clean law's invariance and equivariance of XOR convolution imply the averaged pair still equalizes the complete laws. Each coordinate's new error marginal is the average over its replacement path's original marginals, at most the registered eta. Consequently **there always exists an optimal mask pair constant on Gamma-orbits**.

A mask orbit is determined by the Hamming-weight vector

    t=(t_e)_e,    0<=t_e<=L_e,

which has M possible values from (1). Let w_h(t) be the total mask probability on this orbit. Uniformly distribute that probability across all `prod_e binomial(L_e,t_e)` masks within it.

For a selected Walsh signature s=(s_e)_e, its mask Fourier character on orbit t has the product Krawtchouk expectation

    Phi_s(t)=prod_e [
      sum_j (-1)^j binomial(s_e,j)
                     binomial(L_e-s_e,t_e-j)
        /binomial(L_e,t_e)
    ].                                                  (7)

Combining (3)/(4) with (7), complete output-law equality is equivalent to M-1 nontrivial orbit Fourier equations

    W_0(s)*sum_t w_0(t)Phi_s(t)
      = W_1(s)*sum_t w_1(t)Phi_s(t),
            s != (0,...,0).                            (8)

The other constraints are

    w_h(t)>=0, sum_t w_h(t)=1,
    sum_t w_h(t)t_e/L_e <=eta
                  for every h in {0,1} and core path e. (9)

**Theorem:** the original full hypothesis-aware erasure LP has the **same exact optimum** as the orbit LP (8)/(9), whose standard rational matrix has

| Quantity | Exact size |
|---|---:|
| Mask orbit classes per hypothesis | M=product_e(L_e+1) |
| Nonnegative primal variables, including eta | 2M+1 |
| Walsh equality plus normalization rows | M+1 |
| Path-marginal inequality rows | 2k |

A dual certificate likewise needs only M orbit-mask inequalities per hypothesis; its exact check uses the same Krawtchouk factors and clean coefficients. The module builds a solver-independent rational matrix, verifies primal feasibility and checks every dual inequality with exact fractions.

**Complexity boundary.** If H is **fixed**, k and n0 are constant. Then M is polynomial in m of degree at most k, the path factors have polynomial rational bit length in m and log q, and standard rational LP optimization solves the entire erasure problem in time polynomial in m and log q. For variable k the straightforward program is **XP-like** in k, since M can grow as m^k; no fixed-parameter tractability in k is asserted. The original core's treewidth can exceed two, while the orbit reduction remains exact.

This extends BM-14's two-terminal parallel-path theorem to fixed cores with **three or more terminals**, including graph classes containing K4 as a minor.

## 4. BM-23/T3: sharp K4 single-edge subdivision theorem

Choose the registered q=4 K4 core with vertices 0,1,2,3 and edges in order

    e0=01, e1=02, e2=03, e3=12, e4=13, e5=23.

The flat gains are all zero; the frustrated gains are

    c=(0,0,0,1,2,1).

All four K4 triangles are frustrated. BM-17 proved the exact full erasure threshold **3/14** on the original six-edge graph.

Now replace **only e0=01** by a path of length L>=2, preserving the gains of every other edge. The resulting graph has m=L+5 reported edges and n=L+3 vertices, remains 2-connected, and has treewidth three.

**Sharp theorem BM-23/T3:**

    eta_sym(K4[e0 -> path_L],c;q=4) =
      3/14  for L=1,
      1/5   for all L>=2.                              (10)

The exact L>=2 optimum is achieved by a **common** mask Q0=Q1, so it also holds against the full hypothesis-aware correlated-readout adversary.

### Lower bound from the diamond projection

Project the equalized output law onto the five core edges e1,...,e5 outside the long substituted path. They form the five-edge diamond K4-e0, with three u-v path gains **(1,0,3)** between endpoints 2 and 3, all distinct over F2². Up to gauge switching, core-vertex relabeling and the path-gain equality partition, this is the same contrabalanced q=4 diamond statistical problem solved exactly in BM-10. Its erasure threshold is **1/5**.

Every admissible complete-graph mask, however correlated with the long path or aware of the hidden hypothesis, projects to an admissible diamond mask with the same per-bit cap. The projected clean law is the diamond's uniform-label law. Therefore

    eta_sym >=1/5.                                    (11)

The committed lower-bound checker verifies the distinct path-gain structure and the exact BM-10 primal and dual certificates.

### Matching upper bound for L>=3: a product common mask

Take the BM-10 diamond's exact **common** optimum mask on e1,...,e5, with maximum bit marginal 1/5. Independently take the long-path common mask

    R_path=0 with probability 1/2,
    R_path=one uniformly random long-path bit
             with total probability 1/2.

It has per-bit error probability 1/(2L)<=1/6 for L>=3. The combined common mask Q has maximum per-bit flip cap exactly 1/5.

To prove complete output equality, examine any Walsh edge subset S:
- If it contains **all L edges** of the long path, the long-path mask's Walsh transform is zero because its error parity is unbiased. Thus W_h(S)hatQ(S)=0 in both worlds.
- If it selects **a proper subset** of the long path, the conditional Fourier path factor equals alpha^s independent of endpoint difference. The clean full-vs-frustrated difference factors as alpha^s times the corresponding five-edge diamond difference. The BM-10 mask already annihilates every such diamond difference. Independence of the long-path mask preserves that zero.

Every Fourier coefficient therefore matches between the two masked worlds; Walsh inversion proves equality of their entire Boolean output laws. This argument covers **arbitrary L>=3**, including enormous replacement paths, without enumerating 2^(L+5) masks.

### Matching upper bound for L=2: a 21-orbit rational witness

The independent product construction would spend 1/(2L)=1/4 on the two-edge path. For the **L=2** graph, a correlated common mask instead attains the lower bound of 1/5.

The [L2 exact witness](k4_subdivision_erasure_BM23.py) has **21 positive path-weight orbits**, with integer numerators summing to 40. Each orbit's mass is distributed uniformly among its possible two-edge long-path positions. The full seven-edge mask law has exact normalized rational masses and **each bit marginal 1/5**. The verifier checks every one of the orbit Fourier equality equations (97 rows including normalizations), and an **independent direct label census** checks all 128 complete output probabilities after common XOR convolution. All match.

Together with (11), this proves the sharp formula (10) for every L>=2.

### Symbolic large fixture

For L=120, the subdivided K4 has

    123 vertices, 125 observed edges, cycle rank 3,
    |D_clean| > 2^120 residual Fourier supports,

yet the exact complete hypothesis-aware erasure threshold remains **1/5**, with an explicit common mask sampler. The orbit quotient contains

    M=(120+1)*2^5=3,872

mask classes per world, compared with 2^125 full mask atoms. A 7,745-variable exact rational LP is thus available in principle. The **sharp theorem** already certifies the optimum without constructing that matrix. The symbolic support count and selected Fourier values are computed by (3)-(5) without complete label enumeration.

The large fixture does not constitute a measured full LP runtime benchmark. Its gain core is constant-sized, so the symbolic proof and sampler are efficient in the number of substituted edges, even though D is exponentially large.

## 5. Independent verification and important limits

New modules:
- [core_subdivision_orbit_BM23.py](core_subdivision_orbit_BM23.py): arbitrary fixed-core replacement-path graph construction, exact gain-balanced-subgraph Fourier averages, clean support counting, Krawtchouk full-orbit hostile-mask LP matrix, and direct primal/dual checks.
- [k4_subdivision_erasure_BM23.py](k4_subdivision_erasure_BM23.py): exact K4 sharp single-subdivision theorem, rational L=2 witness, mapped BM-10 diamond lower and upper certificates, long-path common mask sampler and O(2^5) symbolic upper verification for arbitrary L>=3.
- [test_core_subdivision_orbit_BM23.py](test_core_subdivision_orbit_BM23.py): every small Walsh subset against independent uniform-label census on K4, its subdivisions, q=8 K4 and nonseries-parallel Wheatstone cores; BM-12 parallel-edge-core recovery; the BM-17 q4 K4 original full primal **and** dual mapped into the general orbit LP; full q4 output-law checks for K4 subdivisions L=2,3,4,5; input/resource guards; and a q=4096 125-edge symbolic fixture.

The proof uses established symmetries of affine parity constraints, gain-graph balanced-subgraph rank identities, Krawtchouk association schemes and rational LP duality. Related background includes [Zaslavsky, *Biased Graphs I*](https://doi.org/10.1016/0095-8956(89)90063-4), the [gain-graph subdivision literature](https://www.mdpi.com/2227-7390/7/10/926), and the broader [linear-code LP hierarchy](https://www.ias.edu/sites/default/files/CoJeJo22.pdf). BM-23 is a specialized exact theorem in the frozen statistical readout model. A wider structural theorem for **variable-size cores**, uncertainty about real monitoring root state, and authenticated interventions remain unproved. No new UGC or operational AI alignment claim is made.
