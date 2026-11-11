# BM-15: Exact gain-spike Fourier transfer on two-terminal series-parallel networks

**10 November 2026 | finite algebraic theorem and independent controls.** This extends [BM-12 theta-path transfer](THETA_FOURIER_TRANSFER_BM12.md) beyond parallel groups of simple paths. It takes the original conditional Fourier expectation through **arbitrary nesting of series and parallel compositions**. The operations and elementary finite-group averaging are standard transfer-matrix/statistical-mechanics mathematics; this note supplies a specific gain-valued sparse representation and exact regression controls for ASMP-14.

## 1. Frozen model and construction tree

Fix K=F2^s, |K|=q. A two-terminal series-parallel (TTSP) gain graph is built inductively from oriented edge leaves e=(u,v,g), with gain g in K, by operations:
- **series** A o B: identify target(A) with source(B), retaining two exterior terminals and disjoint original edge occurrences;
- **parallel** A || B: identify both corresponding terminals, retaining separate interior vertices and all edge occurrences.

The graph is compiled with distinguished terminals source=0 and target=1 and stable left-to-right leaf/edge order. For a queried subset S of its edge occurrences, uniform fresh vertex labels a in K^V yield the Boolean satisfaction indicators X_e=1[a(v)=a(u)+g_e]. Condition on the terminal difference d=a(target)-a(source) and define

    F_N,S(d)=E[prod_(e in S) (1-2 X_e) | d].

This is the conditional Walsh coefficient needed for the flat/nonflat monitor statistics. The unconditional Fourier coefficient is the average over d, which is itself uniform in K.

## 2. The exact transfer algebra (BM-15/T1)

**Theorem:** Every conditional transfer in a TTSP gain graph can be represented exactly as

    F(d)=a + sum_(g in K) b_g 1[d=g],                (1)

where a and b_g are rational, and only nonzero b_g are stored. Its base edge is:
- e omitted from S: a=1, no spikes;
- e in S with gain g: a=1, b_g=-2.

Write the messages for subgraphs A,B as (a,b) and (c,e), with totals B_sum=sum b_g and E_sum=sum e_g.

**Parallel operation.** Conditional on the shared terminal labels, disjoint interiors are independent; hence F_(A||B)(d)=F_A(d)F_B(d). Pointwise multiplication and 1[d=g]1[d=h]=1[g=h]1[d=g] give

    a_parallel = a*c,
    b_parallel(g)=a*e_g + c*b_g + b_g*e_g.         (2)

**Series operation.** The joining vertex has a uniform label conditional on the exterior terminal difference d; the two components' internal labels are independent once the join label is fixed. Writing the two segment differences x,d-x (XOR in F2^s),

    F_(A o B)(d) = (1/q) sum_(x in K) F_A(x)F_B(d-x). (3)

Expand the sparse-spike form and average. The exact output is

    a_series = a*c + (a*E_sum+c*B_sum)/q,
    b_series(g) = (1/q) sum_(x+y=g) b_x e_y.      (4)

The spike support is therefore closed under group convolution and pointwise product. Induction on the TTSP construction tree proves (1)-(4). No enumeration of q^|V| complete vertex assignments is required.

The unconditional Fourier coefficient is

    W_N(S) = a + (1/q) sum_g b_g.                  (5)

The algorithm operates on rational background and sparse gain dictionaries. Its arithmetic cost is proportional to local support unions for parallel joins and local support products for series joins, independent of vertex-label enumeration. **Worst-case support may grow exponentially with the number of edges**, potentially reaching min(q,2^m). Thus this is an exact *per-coefficient oracle*, with favorable speed on sparse-gain-support families; it does not prove a general polynomial-time algorithm in m and log q, nor compress the full adversarial mask erasure LP.

## 3. Independent test and BM-14 limitation

The [new oracle](series_parallel_transfer_BM15.py) also compiles any nested TTSP expression into a concrete finite `Game` with stable edge occurrences. [Independent tests](test_series_parallel_transfer_BM15.py) enumerate all internal vertex assignments conditional on each possible terminal label difference, compare **every** Fourier subset of the q=4 diamond and theta cases against [BM-12](THETA_FOURIER_TRANSFER_BM12.md), test q=8 parallel-path examples, and check the final unconditional statistic directly against the original uniform-label `finite_seed.satisfaction_law`.

A nested TTSP negative control has the expression

    (edge(0) o (edge(0) || edge(1)))
        ||
    (edge(0) o edge(0)).

The first exterior branch has three edge occurrences e0,e1,e2. The inner edges e1,e2 are parallel with distinct gains, so both cannot be satisfied at once, while e0,e1 form an acyclic pair. At q=4, the exact degree-two Walsh coefficients are

    W({e1,e2})=0,
    W({e0,e1})=1/4.                                   (6)

Consequently edges within the *same outer branch* need not be exchangeable. BM-14's mask-orbit averaging over all edges in a simple u-v path **cannot** be extended by treating arbitrary nested TTSP branches as simple paths. The BM-15 sparse terminal transfer remains valid because it preserves the internal series/parallel syntax.

As a scale control, a 40-edge network of two length-20 series paths over q=4096 yields a selected Fourier coefficient through the sparse transfer without enumerating its 4096^40 possible vertex labelings. This is an oracle demonstration with small spike support, not a full erasure-LP solve.

## 4. Structural implication

The algebra (1)-(4) suggests treating each cyclic block as a *boundary-response algebra* whose complexity depends on the number of distinct exposed gain spikes. More general separators with three or more vertices require multi-terminal messages; [BM-16](SEPARATOR_FACTOR_TRANSFER_BM16.md) handles that case with ordinary exact variable elimination and explicit q-dependent width costs.

BM-15 provides a useful reference for comparing three structural axes:
- **number of boundary terminals** controlling the dimension of a factor message;
- **gain-spike support** controlling symbolic Fourier-coefficient complexity in the two-terminal algebra;
- **mask-symmetry orbit count** controlling compression of the *entire adversarial erasure LP*, as in BM-14.

These quantities can differ substantially on the same network. An eventual ASMP-14 resource theorem must fix which one is being bounded.

### Prior art

- [Series-parallel graph recursive definition](https://mathworld.wolfram.com/Series-ParallelGraph.html).
- Mukhamedzhanova, Sabirov & Mukhamedzhanov, [*Algorithm for computing the partition function of the Potts model for SP-graphs* (2025)](https://arxiv.org/abs/2507.22579), for related statistical-mechanics series/parallel reductions.
- [BM-12 parallel-path transfer](THETA_FOURIER_TRANSFER_BM12.md) and [BM-14 exact path-orbit erasure LP](PATH_ORBIT_LP_BM14.md).

The theorem uses standard transfer identities and exact rational computations in a finite gain graph. It makes no claim about model alignment, reward-hacking prevalence or independently attested interventions.
