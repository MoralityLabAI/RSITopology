# BM-22: Implicit Fourier-support circuits and sharp erasure on 2-connected theta graphs

**10 November 2026 | exact finite structural theorem and independent regression tests.** This advances the [BM-21 cactus Fourier circuit](IMPLICIT_CACTUS_SUPPORT_BM21.md) to **2-connected graphs whose cycles overlap along paths**. It also proves a sharp erasure formula for an infinite three-path theta family, generalizing the [BM-09 six-edge theta certificate](THETA_CYCLE_INTERACTION_BM09.md).

These are finite observations under uniform fresh vertex labelings and XOR readout masks independent of the *current* clean sample. The mathematical tools are classical gain-graph balance, Fourier characters, terminal conditioning and LP/hypothesis-testing symmetrizability. No general Unique Games theorem, broader graph family complexity result or empirical AI safety guarantee is claimed.

## 1. Structural setting and conditional path messages

Consider k>=2 internally vertex-disjoint paths from a common terminal u to a common terminal v, with path lengths L_0,...,L_(k-1)>=1. Gains take values in K=F₂^s with q=|K|. Each hypothesis h=0,1 fixes the path gains g_(h,i), the XOR sum of its constituent edge gains. A fresh uniformly random vertex labeling determines the Boolean satisfaction vector X of all m=sum_i L_i edge reports.

For a Walsh subset S of the m observed edges, write

    J(S)={i : ALL L_i edges of path i occur in S},
    b(S)=sum_{i not in J(S)} |S intersect path_i|,
    alpha = 1-2/q.

BM-12's conditional terminal-difference formula gives a *properly selected* path's Fourier factor alpha^s. A **fully selected** path of length L has factor

    f_(L,g)(d)=A_L+B_L 1[d=g],                    (1)

where the uniform endpoint difference d=a(v)-a(u) lies in K and

    A_L=alpha^L-(-2/q)^L,
    B_L=(-2)^L/q^(L-1).

Conditional independence of the paths gives the exact identity

    W_h(S) = alpha^b(S) F_h(J(S)),                 (2)

where F_h(J) is the terminal-uniform expectation of the product of the fully selected path factors (1).

### Computing F_h(J) without enumerating q terminal labels

Fix a set J of fully selected paths, and put H_J={g_(h,i): i in J}. The conditional product is equal to the baseline `P=prod_{i in J} A_(L_i)` at all d outside H_J. At a gain g in H_J its value becomes

    P_g=prod_(i in J) [A_(L_i)+B_(L_i)*1[g_(h,i)=g]].

Therefore

    F_h(J)= [(q-|H_J|)*P + sum_(g in H_J) P_g] / q. (3)

Because |H_J|<=|J|, this needs only O(k²) rational arithmetic operations per J, including the large-alphabet case. The number of path sets J is 2^k. The exact Fourier discrepancy becomes

    Delta(S)=W_0(S)-W_1(S)
            =alpha^b(S) [F_0(J(S))-F_1(J(S))].     (4)

For **q>2**, alpha≠0, so the answer to whether a Fourier coefficient distinguishes the two hypotheses depends **only on which paths are completely selected**. The proper-path edge choices change the coefficient magnitude and leave its zero/nonzero status unchanged.

This yields a compact exact support grammar with at most 2^k path-class states. Its total number of differing Fourier subsets is

    |D| = sum_(J:F_0(J)!=F_1(J))
                  prod_(i not in J) (2^(L_i)-1).    (5)

A path outside J must be selected properly, with 2^(L_i)-1 possibilities. At q=2, alpha=0, so every proper path must have *zero* selected edges to contribute a nonzero coefficient. The same sum applies with each proper-path count replaced by one.

For fixed k, the support count and membership circuit are computable in time polynomial in m and the bit length of q, while the explicit support D can contain exponentially many Fourier subsets. When k varies, the 2^k factor remains explicit. These statements concern the **clean** laws; the post-readout support for arbitrary hypothesis-specific masks may depend on individual edges within the paths.

The [BM-22 implementation](theta_support_circuits_BM22.py) computes (3)-(5) using exact fractions. Its independent controls compare every coefficient on q=2,4,8 small graphs with direct vertex-label enumeration and the earlier BM-12 transfer oracle.

## 2. BM-22/T1: sharp q=4 three-path support rule

Now set q=4, k=3, with flat path gains (0,0,0) and *three distinct* frustrated path gains (0,1,2). This is a **contrabalanced theta**: every pair of paths forms a frustrated cycle.

At q=4, the full-path factor (1) has a particularly simple form:

    L even: f_(L,g)(d) = (4/2^L) * 1[d=g],
    L odd:  f_(L,g)(d) = (2/2^L) * (1-2*1[d=g]). (6)

Using (6), the flat-versus-distinct-gain average differs on **every choice of two fully selected paths**. It agrees whenever zero or only one path is completely selected. For all **three** fully selected paths, the difference vanishes *precisely when one of the three path lengths is even and the other two are odd*: the even-path delta factor forces the terminal difference to its own gain, so the two other odd-path signs become +1 in the frustrated world and +1 in the flat world.

Consequently, with L_i>=1,

    |D| = sum_(i=0)^2 (2^(L_i)-1)
          + 1[the lengths are not exactly even,odd,odd].   (7)

The last indicator accounts for the single Fourier subset selecting all three paths. This support rule holds for arbitrary even/odd path lengths. Independent tests cover the K2,3 theta, the five-edge diamond, and mixed-length theta networks, including the cancellation example (2,3,3).

There is a structural consequence worth separating from the numerical signal. Even if all three paths are fully selected and the Fourier difference *cancels*, the supports from exactly **two** fully selected paths collectively contain every pair of observed edges. Thus the clique-expanded Fourier-support interaction graph is **complete on m vertices** (treewidth m−1), while the underlying simple theta has treewidth **two**. The clean support still has an exponentially large explicit list for large paths.

## 3. BM-22/T2: exact adversarial erasure for three even-length paths

Suppose all three lengths are **even**, with the same flat gains (0,0,0) and distinct frustrated gains (0,1,2). Let

    m=L_0+L_1+L_2,
    ell_min=min_{i<j}(L_i+L_j)=m-max_i L_i.

Allow separate adversarial readout-mask distributions Q0 and Q1 for the two hidden states. Each may have arbitrary within-episode correlations but must be independent of the *current* clean observation and satisfy the same uniform per-edge flip cap eta.

**Sharp theorem:**

    eta_sym(theta;q=4)
      = max(1/m, 1/(2*ell_min)).                    (8)

A **common** mask distribution Q0=Q1 attains this bound, so hypothesis-aware masks offer no further advantage for this special connection/length family.

### Lower bound I: full and complement Walsh characters

For q=4 and an even path, (6) is nonnegative and supported only at the path's gain. All three gains in the frustrated state are distinct. Therefore the frustrated clean Walsh coefficient is **zero** when at least two complete paths are selected, while the flat clean coefficient is **strictly positive**.

In particular, let E denote all m observed edges. The Fourier characters indexed by E and **every** E\{e} have positive flat coefficient and zero frustrated coefficient, since removing one edge leaves two complete paths. If the adversarial masks equalize the complete output laws, their flat-world mask distribution Q0 must consequently satisfy

    hatQ0(E)=0,    hatQ0(E\{e})=0 for every e.      (9)

Let K=number of flipped bits under Q0 and B=1[K odd]. The full character constraint yields E[B]=1/2. The complement constraints say that the expected number T of edges e for which the complement E\{e} has **odd** flip parity is m/2. Pointwise,

    T=K when K is even,
    T=m-K when K is odd,

and in either case

    T <= K+(m-2)B.

Taking expectations yields m/2<=E[K]+(m-2)/2 and therefore

    E[K] >= 1.

Since E[K] is the sum of the m edge-flip marginals, eta>=1/m. This lower bound holds for **every** legal hypothesis-aware and correlated mask law.

### Lower bound II: projected frustrated cycles

Project any equalized joint output law onto the edges of one two-path cycle. This yields a legal erasing mask pair under precisely BM-08's single-cycle contract. Every pair is frustrated with length L_i+L_j, and at q=4 BM-08 proved the sharp isolated-cycle bound

    eta >= 1/[2(L_i+L_j)].

Taking the strongest pair yields eta>=1/(2*ell_min). Combining both lower bounds gives (8)'s lower side.

### An explicit eight-state common-mask upper witness

Put

    eta* = max(1/m,1/(2*ell_min)),
    p_i = min(eta* L_i, 1/2),
    a_i = 1-2p_i.                                   (10)

These quantities obey p_i in [0,1/2], sum_i p_i=1, a_i>=0, sum_i a_i=1. The two cases are elementary:

- If every L_i<=m/2, eta*=1/m and p_i=L_i/m, summing to one.
- If some L_j>m/2, eta*=1/[2(m-L_j)], so p_j=1/2 and the other two p_i sum to 1/2.

Choose a three-bit **path-activation vector** T=(T_0,T_1,T_2) according to

    Pr(T=t)=1/8 * [1+sum_i a_i (-1)^t_i].          (11)

This is a normalized nonnegative distribution because the a_i are nonnegative and sum to one. Its first-order marginals are Pr(T_i=1)=p_i. All Fourier moments of the path-activation vector with order >=2 vanish:

    E[(-1)^(sum_{i in J}T_i)]=0,  |J|>=2.          (12)

Given T, for every activated path i independently choose exactly one of its L_i edges uniformly and flip that Boolean report; leave inactive paths untouched. Call the resulting common mask R.

Every edge on path i has flip marginal p_i/L_i<=eta*, and the maximum is exactly eta*. Its path-activation law has only eight possible T states; an efficient sampler chooses at most three individual edge positions.

To prove erasure, consider any Fourier edge set S with at least two **fully selected paths**, say J={i,j}. Conditional on the path activations, the mask character contributes (-1)^(T_i+T_j) from those complete paths. If the third path has s selected edges, its additional factor is

    1-(2s/L_k)*T_k.

The expectation of the product vanishes because E chi_{i,j}(T)=0 and E[chi_{i,j}(T) T_k]=(E chi_{i,j}-E chi_{i,j,k})/2=0 by (12). If all three paths are selected, (12) directly gives zero. If fewer than two are fully selected, the two **clean** Fourier coefficients already agree. By Walsh inversion, the two complete masked Boolean laws are therefore identical.

This establishes an admissible common mask with cap eta*, which matches both universal lower bounds and completes the proof of (8).

## 4. Exact examples and a 360-edge symbolic obstruction

| Three even path lengths | m | Sharp erasure eta* | Most relevant lower bound |
|---|---:|---:|---|
| (2,2,2) | 6 | 1/6 | 1/m, BM-09 |
| (2,2,4) | 8 | 1/8 | Both match |
| (2,4,4) | 10 | 1/10 | 1/m |
| (2,2,6) | 10 | 1/8 | Shortest-cycle projection |
| (2,4,8) | 14 | 1/12 | Shortest-cycle projection |
| (4,6,8) | 18 | 1/18 | 1/m |
| (2,2,20) | 24 | 1/8 | Shortest-cycle projection |
| (120,120,120) | 360 | **1/360** | 1/m |

At L=(2,2,2), the mask from (11) has 19 nonzero Boolean atoms. It attains the same 1/6 error cap as BM-09's **alternative** sparse ten-atom common mask; this is an independent construction of the exact same optimum.

At L=(120,120,120), the underlying graph is a simple 2-connected theta of treewidth **two**, with 360 edges and three frustrated overlapping cycles. Its exact clean Fourier discrepancy support has

    |D|=3*(2^120-1)+1                                (13)

members, and the full 360-edge character is one of them. Thus the clique-expanded residual-support interaction graph has treewidth **359**. The support count is computed from only eight full-path classes without materializing any Fourier coefficient table. Its full-edge discrepancy is exactly 2^(-356). Despite the immense raw support, the sharp state-aware **and common-mask** erasure cost is only **1/360**, and the eight-state activation law (11) gives a compact exact sampler. The lower proof is checked via closed Fourier zero identities and the Hamming/parity inequality for K=0..360; the upper proof checks path-activation Fourier moments without constructing any large observation law or numerical LP.

This is a stronger obstacle to using original-graph treewidth as a proxy for explicit residual-support complexity than BM-21's tree-attached triangle, because the new graph has **no articulation vertex** and its cycles interact along shared terminal paths.

### A subtle cancellation

With L=(2,131,133), q=4 and distinct path gains, exactly one path is even. The complete 266-edge Fourier discrepancy vanishes by the parity condition in section 2, but the support contains

    (2^2-1)+(2^131-1)+(2^133-1)

other indices. Every pair of observed edges still belongs to at least one support from two fully selected paths, so the full Fourier-support clique width remains m−1=265. This demonstrates that even the **largest Fourier character's vanishing** can be misleading as a proxy for the interaction width of the entire discrepancy family.

## 5. Frozen readout masks and compact orbit support counting

Equation (4) computes the clean Fourier values for any selected S. For explicit hypothesis-specific XOR mask laws Q0,Q1 with finite atom lists, the actual **post-readout** discrepancy at S is

    Delta_Q(S)=W_0(S) hatQ0(S)-W_1(S) hatQ1(S).      (14)

The implementation evaluates (14) exactly in time linear in the two mask support sizes after the theta circuit lookup. It makes **no universal polynomial claim for counting all post-readout supports** when Q0,Q1 are arbitrary correlated full-edge masks.

When both masks are **pathwise exchangeable**, however, the BM-14 Hamming/Krawtchouk orbit representation applies. The masked coefficient depends only on s=(s_0,...,s_(k-1)), with 0<=s_i<=L_i. Each s represents exactly

    prod_i binomial(L_i,s_i)

individual Walsh supports. By iterating the M=prod_i(L_i+1) path-count signatures, one can compute the **exact number** of post-readout nonzero Fourier discrepancies as a weighted sum, without listing the corresponding subsets of m individual edges. For fixed k this is polynomial in m, under the explicit rational path-orbit mask input grammar.

Independent tests verify the count against BM-19's registered partially masked five-edge diamond (6 remaining supports) and six-edge theta (7 remaining supports). They also check the q=8 BM-09 hypothesis-aware optimal mask pair, whose complete residual Fourier support becomes empty after symmetrization.

## 6. Reproduction, prior art and open ASMP frontier

New modules:

- [theta_support_circuits_BM22.py](theta_support_circuits_BM22.py): exact full-path conditional Fourier coefficients, clean support grammar/cardinality, q=4 three-path parity classification, sharp all-even erasure lower/upper theorem, explicit masks, exact samplers, and pathwise-symmetric frozen-readout support counts.
- [test_theta_support_circuits_BM22.py](test_theta_support_circuits_BM22.py): direct census on q=2,4,8 theta/diamond graphs; all Fourier subsets versus BM-12's independent oracle; q4 cancellations; multiple even-path sharp caps and complete output-law convolutions; BM-09 ten-atom comparison; BM-19 partial-mask residual support controls; q8 state-aware full erasure; and symbolic large-width examples without allocation.

All nontrivial finite examples are checked in exact rational arithmetic on the focused CPU-only GitHub Actions workflow. The 360-edge case uses the *algebraic* Fourier witness and short sampler, with no full law/LP materialization.

The result uses well-established gain-graph theta balance, factorization under terminal conditioning and Fourier symmetrization. Thomas Zaslavsky's [*Biased graphs I: Bias, balance, and gains* (1989)](https://doi.org/10.1016/0095-8956(89)90063-4) proves the gain-theta property, under which a theta cannot contain exactly two balanced cycles. The Fourier observation-channel erasure cost (8) is a further model-specific calculation built on that structure; independent prior-art review is needed before claiming publication novelty.

**The next research target** is a controlled extension to **2-connected networks with more than two terminals**, where neither cactus block factorization nor the path-permutation action applies uniformly. A meaningful ASMP-14 result would need compressed clean and post-readout support representations, costed attaining masks, and independently verifiable Fourier duals under the registered adversarial access model. Treewidth of the original graph, raw Fourier-support width, and active certificate width must remain separate complexity parameters. No authenticated intervention, real-world model safety certification or new Unique Games proof is established by BM-22.
