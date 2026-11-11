# BM-24: Wreath-product path symmetries and sharp erasure with a growing theta core

**10 November 2026 | exact symmetry theorem, rational mask/dual certificates, variable-core positive family.**

This is a targeted extension of the [BM-14 path-orbit LP](PATH_ORBIT_LP_BM14.md), [BM-22 theta circuit](IMPLICIT_THETA_SUPPORT_BM22.md), and [BM-23 fixed-core subdivision LP](FIXED_CORE_SUBDIVISION_BM23.md). The fixed-core restriction in BM-23 required a constant number of original core edge occurrences. Here the core is allowed to GROW: it consists of k parallel u-v core edges, subdivided into k paths, with repeated **joint path types** shared across the two hypotheses.

The results use established permutation-group orbit averaging, imprimitive wreath products, multivariate Krawtchouk kernels, and rational LP duality. They specialize those methods to the registered gain-game observation channel. This packet establishes exact consequences in the finite model and does not claim a new general-purpose LP algorithm, resolution of UGC, or operational AI-safety certification.

## 1. Observation, attacker and the additional group action

The alphabet is K=F2^s, q=2^s. There are k internally vertex-disjoint paths between terminals u,v. Each path has a positive integer length L and a total XOR gain g_h under hidden hypothesis h=0,1. A fresh uniform labeling of every vertex produces a full Boolean edge-satisfaction vector for each episode. A hypothesis-aware XOR readout adversary chooses a correlated distribution Q_h over all reported edge bits. It may differ between the two hypotheses but is **independent of the current clean satisfaction vector**; each edge's marginal flip probability is at most a common eta.

A **joint path type** is a triple

    tau = (L_tau, g_(0,tau), g_(1,tau)).

Let n_tau be the number of paths with that same type. Along any path, conditional on the endpoint label difference d, the vector of XOR residuals is uniform in an affine hyperplane of dimension L_tau−1. Its law is invariant under permutations of the L_tau residual coordinates. Independently of those internal permutations, paths of the same joint type have identical conditional distributions under **both** hypotheses and independent internal labels. Therefore the complete Boolean observation law under either hypothesis is invariant under

    Gamma=product_tau [ S_(L_tau)^n_tau rtimes S_(n_tau) ],  (1)

the product of imprimitive wreath-product actions. The group permutes edge positions within each path and also permutes entire paths of the same joint type.

For any successful complete-output equalizing pair Q0,Q1, average each law under Gamma. The clean laws are Gamma-invariant and Boolean XOR convolution commutes with coordinate permutations, so the averaged masks still equalize the complete distributions. On every group orbit the averaged per-edge flip marginal is the mean of original marginals, at most eta. Thus **some exact optimal hypothesis-aware correlated readout-mask pair is Gamma-invariant**.

This extends BM-14's within-path averaging. The new whole-path permutations are available even when the number of core paths k grows. Grouping requires equality of the **joint gain pairs** and path lengths under the two hypotheses. Inhomogeneous edge costs, per-edge identity-dependent interventions or mask access to the current clean vector can break the theorem's premises.

## 2. BM-24/T1: exact LP quotient over path-weight histograms

For one joint type tau with n=n_tau copies of length L=L_tau, let

    c=(c_0,...,c_L), sum_(j=0)^L c_j=n,

where c_j counts the paths whose readout mask flips exactly j edges. This **histogram** completely classifies a Gamma-orbit of mask vectors, because within each path the flipped positions may be permuted and copies with the same length and joint gains can be swapped.

By stars and bars, this type has exactly

    M_tau=binomial(n_tau+L_tau,L_tau)                (2)

mask orbits. The entire graph has

    M=product_tau M_tau.                             (3)

Walsh edge-subset characters are classified by an analogous histogram a, which counts paths with s selected edges. Let the clean Fourier coefficient at selected character signature a under hypothesis h be W_h(a).

### Clean Fourier coefficient oracle

Set alpha=1−2/q. For a type tau, let a_(tau,L) be the number of **completely selected** paths and let

    P=sum_tau sum_(s=0)^(L_tau-1) s*a_(tau,s)

be the selected-edge count among properly selected paths. For each fully selected path type define

    A_L=alpha^L-(-2/q)^L,
    B_L=(-2)^L/q^(L-1).

Conditional on terminal difference d, each properly selected path contributes alpha^s while a full path of gain g_(h,tau) contributes A_L+B_L*1[d=g_(h,tau)]. Independence of the path interiors gives

    W_h(a)=alpha^P*(1/q)*
       sum_(d in K) product_tau
       [A_(L_tau)+B_(L_tau)*1[d=g_(h,tau)]]^a_(tau,L_tau). (4)

The apparent q-term sum is evaluated **without looping over q**. Group its terms by the at most r distinct fully selected gains, with r=number of joint types. If B0=product_tau A_L^a_(tau,L), then (4)'s bracketed average is

    ((q-|G|)*B0 + sum_(g in G)
       product_tau [A_L+B_L*1[g_(h,tau)=g]]^a_(tau,L))/q, (5)

where G is the set of fully selected gains. The circuit therefore computes each Fourier orbit coefficient with polynomially many exact rational operations in r and the encoded lengths, without q^vertices label enumeration.

### Multivariate Krawtchouk mask kernel

For a single path of length L, a Walsh subset selecting s edges and a uniform mask flipping t edges has exact parity expectation

    K_L(s,t)=
      sum_j (-1)^j binom(s,j)binom(L−s,t−j) / binom(L,t). (6)

Let a and c be the corresponding selected-path and mask-weight histograms on n repeated paths. A uniform mask from orbit c randomly assigns its path weights to the n labeled paths, then independently chooses flipped positions within each path. The orbit Fourier kernel is

    Phi_L(a,c)=
      [ z_0^c_0 ... z_L^c_L ]
        product_(s=0)^L (sum_(t=0)^L K_L(s,t) z_t)^a_s
      / [n! / product_t c_t!].                       (7)

The coefficient extraction averages over every admissible assignment of mask weights to the selected-path types. A pure-Python **exact hypergeometric dynamic program** implements (7) by repeatedly assigning a remaining mask weight t with probability c_t/remaining_paths, multiplying by K_L(s,t). It also permits exact direct-comparison tests against complete Boolean mask orbit enumeration.

Across types the kernel is a product, Phi(a,c)=product_tau Phi_(L_tau)(a_tau,c_tau).

### The exact complete-output erasure LP

Let w_h(c) be the **total mask probability** on a Gamma-orbit c, normalized to sum_c w_h(c)=1. Every member of the orbit has the same probability. The full Walsh equalities, equivalent by invertibility to complete output-law equality, reduce to

    W_0(a)*sum_c w_0(c)Phi(a,c)
       =W_1(a)*sum_c w_1(c)Phi(a,c)                (8)

for every nonempty Walsh orbit a. The per-edge marginal cap for type tau is

    sum_c w_h(c)*
        [sum_(j=0)^L_tau j*c_(tau,j)]/(n_tau L_tau)
       <= eta.                                       (9)

The exact rational LP now has

| Measure | Size |
|---|---:|
| Histogram classes per hidden hypothesis | M=product_tau binom(n_tau+L_tau,L_tau) |
| Nonnegative primal variables, including eta | 2M+1 |
| Walsh equality plus normalization rows | M+1 |
| Per-type marginal inequality rows | 2r |

A rational dual likewise has M mask-orbit inequalities per hypothesis. [The verifier](repeated_theta_orbits_BM24.py) checks all those inequalities with exact fractions and can average earlier full-mask Fourier duals into type-histogram duals with unchanged objective.

**Polynomial-size theorem.** If the number r of joint types and maximum path length L_max are fixed, then M=O((k+L_max)^(r L_max)). Every matrix coefficient is a rational with polynomial bit length in k and log q. Standard rational LP optimization therefore solves the **entire** frozen hostile-readout erasure problem in polynomial time in k and log q for this class. In particular, for a fixed q and common length L, at most q² joint gain types can appear, so this covers K2,k networks with k tending to infinity. The dependence is XP with respect to variable r and L_max; **no FPT theorem in those varying parameters** is claimed.

## 3. BM-24/T2: a sharp growing-core erasure family

Take **n ordinary u-v paths** and **one exceptional u-v path**, all having length L>=1. Under the flat hypothesis, every path has gain zero. Under the frustrated hypothesis, all ordinary paths retain gain zero while the exceptional path has a fixed gain gamma !=0.

This graph has k=n+1 paths, m=(n+1)L edge reports, and cycle rank n. If L>=2 the ordinary graph is simple, 2-connected and has treewidth two, regardless of n. Its core K2,k grows with n. There are exactly two joint path types:

    tau_A=(L,0,0),  n_A=n;
    tau_B=(L,0,gamma),  n_B=1.

The exact mask-orbit count is only

    M=binom(n+L,L)*(L+1).                            (10)

### An explicit common eraser at 1/(4L), every alphabet q

The mask is the following **two-branch mixture**:

- With probability 1/2, leave the exceptional path untouched. Each ordinary path independently activates with probability 1/2; an activated ordinary path flips one uniformly chosen edge.
- With probability 1/2, leave every ordinary path untouched. The exceptional path activates with probability 1/2 and flips one uniformly chosen edge if active.

Every edge in the entire graph has marginal flip probability

    (1/2)*(1/2)*(1/L)=1/(4L).                        (11)

The mask is common under both hypotheses, internally correlated across paths through the initial branch choice, and independent of the current clean observation.

**Exact full-output proof.** A clean Fourier discrepancy can occur only when (i) the exceptional path is fully selected and (ii) **at least one** ordinary path is fully selected. If the exceptional path is proper, its conditional Fourier contribution is independent of its gain. If no ordinary path is fully selected, integrating over the uniform terminal difference makes the exceptional gain immaterial.

On any remaining distinguishing Fourier subset, the first mask branch has a zero character expectation because at least one fully selected ordinary path has unbiased flip parity. The second branch has zero expectation because the fully selected exceptional path has unbiased flip parity. Therefore the *common* mask's Fourier character is zero on **every** nonzero clean discrepancy, which equalizes the entire reported observation distributions by Walsh inversion.

The proof uses only these two logical path-selection cases and applies for **arbitrary n, L and q=2^s**. An exact sampler requires O(n) fair-bit and edge-position draws. The mask's orbit law has only **n+2 nonzero histogram atoms**, rather than all M classes.

### Sharp common-channel cost for all q

Project any fully equalized common-mask observation law onto the edges of one ordinary path and the exceptional path, forming a frustrated cycle of length 2L. Its clean full-cycle Fourier discrepancy is

    Delta(C)=(-2)^(2L)/q^(2L-1) !=0.

For a **common** XOR mask to erase this character, its full-cycle mask parity must be unbiased. Hence the odd-flip parity event has probability 1/2, and

    1/2 <= sum_(e in C) Pr(R_e=1) <= 2L * eta.

Therefore eta>=1/(4L), attained by (11), for **every** q.

### Sharp hypothesis-aware cost for q=2 or 4

When the adversary may choose different correlated error laws in the two hidden worlds, projecting onto the same frustrated 2L-cycle yields a legal BM-08 cycle erasure instance. BM-08 proves the sharp hypothesis-aware cycle threshold eta_star(q,2L)=1/(4L) for q=2 and q=4. Thus the common mask (11) already attains the optimum over the **entire wider hypothesis-aware class**:

    eta_sym(G_n,L;q) = 1/(4L),  q in {2,4}, n>=1.    (12)

For **q=4**, there is an even shorter global exact LP dual. Let C contain all 2L edges of the first ordinary path and the exceptional path. The clean Walsh coefficients there are

    W0(C)=2^(2−2L)>0,    W1(C)=0.

Set eta=1/(4L), normalize y_(flat)=eta, y_(frustrated)=0, put one Walsh dual multiplier y_C=−eta/W0(C), and marginal multipliers z_(flat,e)=−1/(2L) for e in C, zero for every other edge/world. The marginal multipliers sum to −1. For a mask flipping exactly j edges of C, the flat-world dual slack is

    [1−(−1)^j]/(4L) − j/(2L) <=0,                 (13)

and the frustrated-world slack is identically zero. Thus a **one-Fourier-character exact rational dual** proves (12) at any n and L, without enumerating the full mask space. The [tests](test_repeated_theta_orbits_BM24.py) also feed this dual and the common attaining mask into BM-17's independent generic all-mask primal/dual verifier on small complete graphs.

For q>=8 the **common-channel optimum** remains 1/(4L), while BM-08's projected hypothesis-aware cycle lower bound can be smaller. The global hypothesis-aware optimum for the growing-core family at those alphabets is not determined here.

## 4. Exact clean Fourier support count for two-edge paths

For L=2, q>=4, and any n>=1, the conditional full ordinary-path factor at endpoint difference d is

    f_A(d)=1−4/q+(4/q)*1[d=0],

so f_A(0)=1 and f_A(d!=0)=1−4/q in [0,1). For a selected Walsh subset S, let r be the number of fully selected ordinary paths. The clean Fourier discrepancy vanishes when the exceptional path is proper or when r=0. If the exceptional path is full and r>=1, the difference is a nonzero multiple of

    f_A(0)^r−f_A(gamma)^r
      = 1−(1−4/q)^r >0.

Every ordinary two-edge path has four selected-edge subsets, exactly one of them fully selected. The exceptional path must be fully selected. Consequently

    |D_clean|=4^n−3^n,    L=2, q>=4.                (14)

This is the **complete clean Fourier discrepancy count**, not a count of globally optimal hostile-mask residual signals after erasure.

The registered n=250, L=2, q=4 fixture has

| Property | Exact value |
|---|---:|
| Ordinary / total paths | 250 / 251 |
| Vertices / reported edges | 253 / 502 |
| Cycle rank | 250 |
| Original complete mask states per world | 2^502 |
| BM-14 separate-path orbit classes per world | 3^251 |
| BM-24 repeated-type orbit classes per world | **94,878** |
| Nonzero orbit atoms in attaining common mask | **252** |
| Clean differing Fourier characters | **4^250−3^250** |
| Exact q=4 fully hypothesis-aware erasure cap | **1/8** |

The 94,878-class LP is a **theoretical rational matrix**, not a claim that a dense full solve was run. The sharp 1/8 result has a small two-branch sampler and a one-character dual valid for the entire 2^502-mask constraint set. The code computes the exact integer support count, LP size, marginal rate and symbolic lower proof without materializing any complete Fourier or mask table.

## 5. Independent verification and novelty limits

The new exact-Python modules are:

- [repeated_theta_orbits_BM24.py](repeated_theta_orbits_BM24.py), which implements joint gain-type grouping, histogram orbit classification, full Fourier coefficient transfer, multivariate Krawtchouk orbit kernels, exact orbit primal and dual verifiers, a solver-ready LP matrix for bounded instances and resource-size receipts.
- [repeated_gain_erasure_BM24.py](repeated_gain_erasure_BM24.py), which implements the sharp growing-core erasure theorem, the O(n)-size common sampler, explicit small mask laws, the n+2-atom histogram witness, clean support counting and exact one-character q=4 dual.
- [test_repeated_theta_orbits_BM24.py](test_repeated_theta_orbits_BM24.py), which checks orbit kernels against direct full-mask enumeration, clean coefficients against independently enumerated uniform vertex labels for q=2,4,8, full postprocessed output laws, small solver-ready LP feasibility, earlier BM-09 q=4 and q=8 theta masks, a symmetrized BM-13 q=4 exact dual, and direct BM-17 rational primal/dual certification of the new sharp q=4 family. The n=250 fixture checks only the compact symbolic representation and sampler.

The underlying product action is a standard **wreath-product group**, and using invariant orbits to compress Fourier LPs has extensive precedent. Relevant mathematics includes [Symmetries, Graph Properties, and Quantum Speedups](https://doi.org/10.1137/23M1573975) for the imprimitive wreath action and [A Complete Linear Programming Hierarchy for Linear Codes](https://www.ias.edu/sites/default/files/CoJeJo22.pdf) for Fourier/coordinate-permutation orbit symmetrization. These support the method; an independent prior-art search is required before claiming that the exact gain-graph specialization or the closed n-path erasure threshold is new in the literature.

The ASMP-14 program now has a positive **growing-core** full-LP size theorem in a highly symmetric two-terminal family. Its open scope is to understand graph families with varying cores and **few or no repeated joint path types**, where these automorphisms disappear. Interventions with edge-dependent costs, state-dependent readout errors, and independently authenticated restoration roots require additional assumptions and experiments. None of the statements here imply an empirical guarantee about a deployed AI monitor.
