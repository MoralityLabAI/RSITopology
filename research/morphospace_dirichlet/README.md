# QD-01: quotient Dirichlet energy and the obstruction to autonomous macro-dynamics

**Status:** 2026-11-04 mathematical note with exact rational finite tests; not an empirical claim about Levin's biology or model sentience. Source inspiration: the Levin/Schindler interview on collective organizational identity and the repo's measured sheaf/spectral-control program. This is a graph-theoretic companion to [Compactification IDQ-01](https://github.com/MoralityLabAI/Compactification-Theory/pull/35) and [XenobotBench MOP-01](https://github.com/patrickdugan/XenobotBench/pull/3).

## 1. What spectral compression guarantees

Let V be a finite undirected weighted graph with nonnegative symmetric weights w_uv; choose a partition q:V→Z with nonempty fibres. For f:Z→R, its lift T f:V→R is (Tf)(u)=f(q(u)). Define the original Dirichlet energy using unordered edges once:

    E_V(x) = sum_{ {u,v} } w_uv (x(u)-x(v))^2.

For distinct macro-vertices a,b, aggregate **every crossing edge**:

    W_ab = sum_{ {u,v}: {q(u),q(v)}={a,b} } w_uv.

**Proposition QD-01/T1 (exact energy pullback).** For every f on Z,

    E_V(Tf) = E_Z(f)
            = sum_{ {a,b} } W_ab (f(a)-f(b))^2.                (1)

*Proof.* Every edge internal to one fibre contributes zero to E_V(Tf). Every crossing edge contributes w_uv times the square of the corresponding difference in f. Group the remaining summands by unordered macro-vertex pair. QED.

This is a standard quotient graph identity. It does **not** prove that the quotient has autonomous dynamics, that graph Laplacian eigenvalues are preserved, or that the partition corresponds to an organism or mind.

## 2. Stronger condition for dynamical autonomy

Define the combinatorial Laplacian

    (L_V x)(u)=sum_v w_uv [x(u)-x(v)].

For each u in fibre a and macro-vertex b≠a let

    d_{a→b}(u) = sum_{v:q(v)=b} w_uv.

A partition is *externally equitable* if d_{a→b}(u) is constant across all u in the same fibre a for every b≠a.

**Proposition QD-01/T2 (invariant lifted macrospace).** If q is externally equitable, the fibre-constant subspace T(R^Z) is invariant under L_V. Specifically,

    (L_V Tf)(u) = sum_{b≠a} d_{a→b}(u) [f(a)-f(b)]

depends only on a=q(u), so there exists a macro operator L_Z^eq with

    L_V T = T L_Z^eq.                                         (2)

*Proof.* Expand the Laplacian, group neighbours by fibre and use external equitability. Edges internal to a contribute zero. QED.

The reverse implication holds when the entire fibre-constant subspace is invariant: test one f for each basis vector of R^Z to recover every off-fibre coefficient. If the graph is weighted and the fibre sizes differ, the natural macro inner product uses fibre masses m_a=|q^{-1}(a)|; unweighted Euclidean spectra on Z generally differ.

## 3. Exact squared invariance defect

Let P be the orthogonal projection in R^V onto fibre-constant functions, so (Px)(u) is the **arithmetic mean** of x on the fibre containing u. For f define

    D_q(f)^2 = || (I-P) L_V T f ||_2^2.                         (3)

Write dbar_{a→b} for the arithmetic average of d_{a→b}(u) over u in fibre a. Then

    D_q(f)^2 =
      sum_{a in Z} sum_{u:q(u)=a}
      [ sum_{b != a} (d_{a→b}(u)-dbar_{a→b})(f(a)-f(b)) ]^2.    (4)

**Proof.** Compute L_V T f at each u, subtract its mean within that fibre, square and sum. QED. Equation (4) exactly measures failure of **this particular lifted observation** to evolve autonomously under the graph diffusion operator. It vanishes for all f exactly when the subspace is invariant.

**Counterexample:** vertices 0,1,2, with undirected edge weights w_02=1 and w_12=2; identify 0,1 as A and 2 as B. Energy pullback (1) holds with W_AB=3. Yet for f(A)=0, f(B)=1, (L_V Tf)(0)=-1 and (L_V Tf)(1)=-2. The fibre mean is -3/2, giving D_q(f)^2=1/2. Identical coarse Dirichlet energy is consistent with a nonzero autonomy defect.

## 4. Relevance and prospective falsifiers

RSITopology already distinguishes target-blind spectral geometry from actionable control evidence and has negative results where measured Qwen edge weights did not add source-specific selection value. QD-01 supplies a complementary **specific** null hypothesis: a compelling quotient energy or low-frequency spectrum may coexist with non-autonomous macro evolution.

A registered follow-up would:
- choose q and graph weights from **construction-only** data;
- predict D_q(f) on a held-out family of functions and interventions;
- compare with mass-matched random partitions, shuffled edge weights and degree-preserving graph nulls;
- report the change in autonomous macro-transition error and downstream recovery value; and
- use the existing lineage/holonomy identity gate before any signed real-model edit.

**Rejection gate:** if the autonomy defect remains at or above matched controls, an observed spectral compression should not be described as demonstrated higher-level agency. This note is finite combinatorial graph algebra and says nothing about nonphysical causation.

## 5. Reproduce

    python -m unittest discover -s research/morphospace_dirichlet -p 'test_*.py' -v

The companion implementation uses \`fractions.Fraction\`. The tests cover the identity, a nonequitable counterexample with defect 1/2, and an equitable control. No model inference, wet-lab work or external network is performed.
