# BM-14: Exact path-symmetry reduction of adversarial erasure LPs

**10 November 2026 | fixed-path-width algorithmic theorem.** Companion to [BM-11 articulation decomposition](BLOCK_TENSOR_ERASURE_BM11.md), [BM-12 theta Fourier transfer](THETA_FOURIER_TRANSFER_BM12.md) and [BM-13 sparse weighted duals](SPARSE_FOURIER_DEGREE_BM13.md). This is an exact result for a precisely specified family of two-terminal *parallel-path gain networks*. It gives a polynomial-size full erasure LP when the number of internally vertex-disjoint paths is fixed. It is a Hamming-orbit/Krawtchouk symmetry reduction of classical finite rational linear programming, requiring independent novelty review.

## 1. The graph and hostile readout interface

Fix a finite additive group K=F2^s, q=|K|, and a graph with k>=2 internally vertex-disjoint directed u-v paths. Path i has L_i>=1 edge occurrences and additive gain g_{h,i} in hidden hypothesis h=0 or 1. Let

    m=sum_i L_i,      M=product_i(L_i+1).

Every episode samples a fresh, independent and uniformly random vertex labeling. The complete Boolean vector X_e=1[a(v)-a(u)=c_e] is the clean observation. Under hypothesis h, a readout adversary may apply an arbitrary correlated Boolean XOR mask N from a distribution Q_h, which may depend on h, the chosen externally known intervention and prior history, but is **independent of the current clean X**. Each edge's conditional mask-flip marginal is at most eta. For the one-episode statistical erasure LP we require

    P_0*Q_0=P_1*Q_1,

as complete Boolean distributions on {0,1}^m. The objective is to minimize eta. Q_0 and Q_1 may differ; no restriction to common or independent readout masks is imposed.

## 2. Symmetry theorem BM-14/T1

For each path, conditional on endpoint difference d=a(v)-a(u), its entire vector of edge residuals is uniform over the affine space of length-L_i vectors summing to d-g_{h,i}. This residual law, hence its Boolean zero-indicator law, is invariant under *arbitrary permutations of the L_i edge occurrences*. Conditional on d, the path-internal labelings are independent. Averaging d gives a clean full-pattern distribution P_h invariant under the product group

    H = S_(L_1) x ... x S_(L_k).

Take any feasible readout-mask pair Q_0,Q_1. For each h average Q_h over all H-permutations, creating \bar Q_h. Convolution with a path-permutation-invariant P_h commutes with this action. Therefore

    P_0*\bar Q_0=P_1*\bar Q_1.

The average per-edge marginal in each path is the mean of the original marginals, at most eta. The averaged masks remain independent of the current clean X. Thus **some optimal erasing pair is constant on each pathwise mask-weight orbit**.

An orbit is indexed by a tuple t=(t_1,...,t_k), 0<=t_i<=L_i, where t_i is the number of flipped bits in path i. There are exactly M mask orbits per hidden hypothesis. Let w_h(t) be the **total** mass assigned to orbit t; within that orbit the probability is uniform among the product_i binomial(L_i,t_i) individual masks. The marginal cap constraints reduce to

    sum_t w_h(t) (t_i/L_i) <= eta,   h=0,1, i=1..k.

Normalization is sum_t w_h(t)=1, and w_h(t)>=0.

This proves an exact reduction of the complete adversarial mask optimization from two sets of 2^m individual probabilities to **2M orbit masses** and eta.

## 3. Fourier-orbit equality and Krawtchouk coefficients

For a Walsh subset S of edge reports, let s_i=|S intersect path_i|, and write s=(s_1,...,s_k). Clean Fourier coefficients \hat P_h(S)=E[(-1)^(sum_(e in S)X_e)] depend only on s, by the same symmetry. The precise rational value \hat P_h(s) is obtained from BM-12's terminal-transfer formula in O(k 2^k) arithmetic operations for each s.

Given a mask sampled uniformly from orbit t, the exact Walsh character expectation at a fixed S of signature s is

    Phi_s(t)=product_i [
        1/binomial(L_i,t_i)
        sum_j (-1)^j binomial(s_i,j)
                         binomial(L_i-s_i,t_i-j)
    ].                                                     (1)

The sum ranges over valid intersections j. It is a product of normalized **binary Krawtchouk polynomial values** (the two conventions with s/t exchanged differ by their binomial normalizers). Consequently the Fourier transform of a path-symmetric Q_h is

    \hat Q_h(s) = sum_t w_h(t) Phi_s(t).

Since the Walsh transform is invertible, equality of the *entire* masked output distributions is **equivalent** to the following finite constraints, one for every nonzero Walsh orbit signature s:

    \hat P_0(s) sum_t w_0(t) Phi_s(t)
       = \hat P_1(s) sum_t w_1(t) Phi_s(t).          (2)

There are M-1 nontrivial equality signatures. Add two normalizations and 2k path-marginal inequalities, giving the **exact rational LP**:

| Item | Size |
|---|---:|
| Nonnegative primal variables | 2M+1, including eta |
| Fourier/normalization equality rows | M+1 |
| Readout marginal inequality rows | 2k |
| Fourier coefficient evaluations | M; each O(k 2^k) arithmetic |
| Krawtchouk orbit entries | at most M^2 |
| Uncompressed readout states per hypothesis | 2^m |
| Compressed mask classes per hypothesis | M |

By the arithmetic-geometric mean bound, M<=((m+k)/k)^k, so for any **fixed number of paths k**, constructing and optimizing this rational LP takes time polynomial in m and the input bit length (including log q) using standard rational LP algorithms. The q-dependent fractions, binomial coefficients, and Krawtchouk terms have polynomial bit length in m and log q. When k varies, the dependence is O(m^k), placing the generic construction in an **XP-type regime** with respect to k; a parameterized **FPT** theorem in k remains open.

This is stronger than a coefficient oracle: it provides the **entire exact primal optimization problem** at polynomial size for fixed k, with an equally compact dual feasibility region.

## 4. Compressed dual certificates BM-14/T2

Let y_s denote signed equality multipliers for each nonzero Walsh orbit signature s, y_norm,h the two normalization multipliers and z_(h,i)<=0 the pathwise marginal multipliers. If

    -sum_(h,i) z_(h,i)=1,

and for every mask-weight orbit t and both hypotheses h,

    y_norm,h + (-1)^h sum_s
        y_s \hat P_h(s) Phi_s(t)
        + sum_i z_(h,i)t_i/L_i <= 0,                (3)

then exact weak LP duality certifies

    eta_sym >= y_norm,0 + y_norm,1.

There are only 2M mask-orbit inequalities to verify, and at most M-1 orbit Fourier multipliers. The [executable dual verifier](theta_orbit_lp_BM14.py) checks (3) with exact fractions.

Moreover **every full Walsh dual certificate can be averaged under the same symmetry group**. For each Fourier signature s, add together all full-dual coefficients with that signature to obtain y_s. For each path i sum its full per-edge marginal multipliers into z_(h,i). The resulting orbit dual is feasible, with exactly the same objective, because every orbit-dual slack is the average of the corresponding original full-mask slacks. Hence the reduced LP's dual is as strong as the original full dual.

The orbit encoding should be described precisely: a single y_s represents a **permutation orbit of potentially many individual Walsh terms**. A polynomial number of *orbit signatures* is a compact certificate, even though its expansion into the uncompressed Walsh basis can have exponentially many supported terms. This result does **not** prove small support in the original full Fourier basis.

## 5. Independent count-channel cross-check

To verify (2) without depending on the same Walsh code, the module also implements a direct exact probability law for the number of satisfied edges in each path. Let k_i=L_i-r_i be its failure count. Under a fixed endpoint difference d, the number of nonzero residual assignments compatible with a specified Boolean path pattern is

    N_0(k_i)=((q-1)^k_i+(q-1)(-1)^k_i)/q,   d=g_i,
    N_1(k_i)=((q-1)^k_i-(-1)^k_i)/q,        d!=g_i.

Let H be the set of distinct gains among the k paths. Averaging the endpoint difference over K and multiplying by the number of Boolean patterns in each count orbit gives

    P_h(r)= [product_i binomial(L_i,r_i)] /
             q^(1+sum_i(L_i-1))
       * [ (q-|H|) product_i N_1(k_i)
           + sum_(g in H) product_i N_(1[g_i=g]?0:1)(k_i) ].   (4)

All values are exact nonnegative rationals. When a mask orbit of t_i flipped edges is applied to a clean path with r_i satisfied bits, the number of satisfied bits after masking has the exact hypergeometric transition

    T_i(r'_i|r_i,t_i)
      = sum_j 1[r'_i=r_i+t_i-2j]
          binomial(r_i,j)binomial(L_i-r_i,t_i-j)
          / binomial(L_i,t_i).                               (5)

The direct count-channel oracle uses the product of (5) across paths and compares full output-count laws independently of the Walsh equalities. The tests also expand each orbit mass uniformly back into all individual masks and compare **complete output-pattern laws** against the original enumerated vertex-label oracle on the small examples.

## 6. Exact calibrated examples

| Registered graph and label alphabet | Edges m | Full masks per world | Orbit masks per world | Exact erasure cap |
|---|---:|---:|---:|---:|
| q=4 diamond, L=(1,2,2) | 5 | 32 | 18 | 1/5 |
| q=4 theta, L=(2,2,2) | 6 | 64 | 27 | 1/6 |
| q=8 theta, L=(2,2,2) | 6 | 64 | 27 | 29/630 |
| q=4096, L=(12,10,9) | 31 | 2,147,483,648 | 1,430 | structural reduction; optimum not evaluated |

The exact q=4 and q=8 optimal-mask witnesses from BM-09/BM-10 project to legal orbit distributions and still satisfy **every** reduced Fourier equality at their previously proven sharp caps. The q=4 diamond/theta sparse duals from BM-13 can be averaged to orbit certificates with, respectively, **six** and **four** nonzero orbit signatures (compared with eight and five original nonzero Walsh terms). Their dual inequalities are checked exactly on both hypothesis sides and every orbit mask class.

For L=(12,10,9) there are 1,430 mask orbits and a potential exact LP with **2,861 variables, 1,431 equality rows and six marginal inequalities**. The code verifies metadata, selected Krawtchouk entries and Fourier coefficients without materializing the entire dense rational matrix or running a solver. A full solution at this size may be expensive in practice, despite the polynomial-size theorem. No optimum, speed benchmark or empirical AI-model evaluation is claimed for this large example.

## 7. Research consequence and novelty boundary

This establishes a **concrete fixed-structure class** in which the complete state-aware erasure threshold and the compact dual certificate can be computed exactly using a polynomial-size rational LP. The price depends on the number of parallel terminal paths k. The remaining ASMP-14 challenge is to extend this toward biconnected gain graphs with more general separators and overlapping cycle complexes, without losing the ability to price and authenticate readout interventions.

The proof uses group averaging, the binary Hamming association scheme, Krawtchouk coefficients and elementary rational LP duality. These are established mathematical techniques. Related references include [*A Complete Linear Programming Hierarchy for Linear Codes*](https://www.ias.edu/sites/default/files/CoJeJo22.pdf), which discusses orbitwise Krawtchouk symmetrization, [Dunkl–Ramirez, *Krawtchouk Polynomials and the Symmetrization of Hypergroups*](https://doi.org/10.1137/0505039), and [BM-12 theta transfer](THETA_FOURIER_TRANSFER_BM12.md). The contribution to this research packet is the exact specialization to the frozen gain-graph adversarial-monitoring LP and independently checked certificate grammar. Prior-art review is required before any novelty claim.

### Code and verification

- [theta_orbit_lp_BM14.py](theta_orbit_lp_BM14.py): full exact orbit LP matrix, Krawtchouk Fourier oracle, projection and expansion of mask laws, independent count-channel convolution, primal/dual checkers and full-dual orbit aggregation.
- [test_theta_orbit_lp_BM14.py](test_theta_orbit_lp_BM14.py): all small Krawtchouk orbits checked by direct mask enumeration, direct vertex-label counts for both hypotheses in q=4 and q=8 examples, all quotient Fourier equalities for prior sharp mask witnesses, reduced LP exact matrix verification, full-pattern and count-channel output comparisons, sparse dual contraction, and the 31-edge scaling control.
- All CI tests are standard-library, deterministic, CPU-only; the exact lazy model is available without allocating an exponential state array.
