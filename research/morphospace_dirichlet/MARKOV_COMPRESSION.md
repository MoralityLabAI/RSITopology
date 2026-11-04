# QD-02: a two-step spectral witness of non-autonomous macro-dynamics

**2026-11-04 mathematical extension of [QD-01](README.md).** The propositions are elementary operator identities for finite reversible Markov chains with a declared observation partition. They do **not** claim original discovery of spectral lumpability, measured model agency, or Platonic causation. Relevant precedents: [spectral Markov compression](https://pmc.ncbi.nlm.nih.gov/articles/PMC7971158/), [strong lumpability](https://pmc.ncbi.nlm.nih.gov/articles/PMC2786939/), and [Barr–Thomas eigenvector condition](https://doi.org/10.1287/opre.25.6.1028).

## 1. Setup: reversible chain and conditional expectation

Let S be a finite state set with strictly positive stationary probability measure mu, and K a stochastic transition operator (Kf)(s)=sum_t K(s,t)f(t). Assume detailed balance

    mu(s)K(s,t)=mu(t)K(t,s).

Then K is a **self-adjoint contraction** in H=L²(S,mu). For a chosen partition pi:S->Z, let P be the orthogonal conditional expectation (mu-weighted averaging over each fibre) and Q=I-P. Let A=PKP on P H. Define the off-fibre leakage operator

    B=QKP : P H -> Q H,       eta = ||B||_op.

The operator norm is the stationary-weighted L² norm; this is **not** a worst-case total-variation defect.

## 2. Exact lumpability and spectral obstruction

**Proposition QD-02/T1 (strong lumpability).** The following conditions are equivalent:

1. For all fibre mates s,t with pi(s)=pi(t), the aggregated K-transition probability to each macro fibre is identical.
2. K sends every fibre-constant function to a fibre-constant function: K(PH) subset PH.
3. QKP=0, equivalently eta=0.
4. [P,K]=PK-KP=0 (the last equivalence uses K=K*).

**Proof.** Apply K to macro-fibre indicator functions; their values are exactly the aggregated transition probabilities, proving 1 iff 2. Condition 2 is QKP=0. With K self-adjoint, (QKP)*=PKQ, so QKP=0 implies both off-diagonal blocks vanish and PK=KP. Conversely a commuting P trivially has QKP=0. QED.

The reversible condition is important for the fourth equivalence. A non-reversible transition operator can preserve PH while its orthogonal complement is not invariant.

## 3. Two-step return memory has **exactly quadratic** leakage

**Theorem QD-02/T2 (two-step macro defect identity).**

    P K² P - (P K P)²
      = P K Q K P
      = (Q K P)* (Q K P)
      = B*B.                                                   (1)

Consequently,

    || P K² P - (P K P)² ||_op = eta².                        (2)

**Proof.** Insert I=P+Q between the two K factors in PK²P. The P term gives (PKP)² and the Q term gives PKQKP. Self-adjointness identifies this with B*B, and the standard Hilbert operator identity ||B*B||=||B||² proves (2). QED.

Thus **one-step** projected macro dynamics may look exactly like A while a **two-step** measurement reveals hidden degrees of freedom via a positive semidefinite defect. This makes macro-memory auditable from action-conditioned two-time correlations without observing a putative "emergence threshold". The statement presupposes an accurately specified finite reversible Markov model.

## 4. Finite-horizon bounds

For f in PH, let u_t=K^t f and write a_t=P u_t, b_t=Q u_t. Because ||K||<=1 and ||P||=||Q||=1,

    ||b_t|| <= t eta ||f||.                                    (3)

By recursion a_{t+1}=A a_t + PKQ b_t, with ||PKQ||=eta, and ||A||<=1, we obtain

    ||P K^t f - A^t f||
      <= (t(t-1)/2) eta² ||f||.                               (4)

**Proof.** b_0=0. From b_{t+1}=QKP a_t+QKQ b_t, use ||a_t||<=||f|| and ||QKQ||<=1 to obtain (3) inductively. Let e_t=a_t-A^t f. Then e_0=0 and e_{t+1}=A e_t+PKQ b_t. Bound recursively, using (3) and ||PKQ||=eta: ||e_t||<=eta² sum_{j=0}^{t-1} j||f||. QED.

Equation (4) is **second order in the leakage norm** for the macro projected prediction, whereas hidden-state leakage is first order. A bound can become vacuous for long times; mixing or spectral gaps can improve it under additional hypotheses.

### Exact rational symmetric witness

With uniform stationary mu, take

    K = [[3/4, 0,   1/4],
         [0,   1/2, 1/2],
         [1/4, 1/2, 1/4]]

and fibres {0,1} and {2}. The orthogonal projection P averages the first two coordinates.

Then B=QKP is nonzero, eta²=3/64, and the two-step macro defect is

    D = (1/128) * [[1,1,-2],
                   [1,1,-2],
                   [-2,-2,4]].

This rank-one matrix has its sole nonzero eigenvalue 3/64, exactly eta². The dependency-free Fraction implementation reconstructs K,P,Q,A,D and checks (3)-(4) on every pair of macro values in {-1,0,1}² for horizons 0..6.

## 5. What a spectral agent experiment must measure

- **Fix the partition pi before evaluation** and record the stationary law mu; empirical averaging must be mu-weighted.
- Estimate K (with confidence intervals) from blinded perturbations, then quantify B and two-step residual D rather than citing a low-frequency spectrum alone.
- Compare to partitions with the same fibre-size histogram, scrambled edges, and a constant-observation null.
- For time-varying, non-reversible, agent-controlled systems use a separate validated operator contract; the self-adjoint identity (1) cannot simply be assumed.
- The hidden-subspace leakage may reflect useful memory, nuisance variables, or an inadequate observation map. Macro-autonomy is a **functional** condition, not a moral or phenomenal attribution.

**Cross-repo:** [IDQ-02 minimax theory](https://github.com/MoralityLabAI/Compactification-Theory/tree/research/ingression-quotients-20261104/research/ingression_dynamics_v1/MINIMAX_THEOREMS.md) supplies worst-case TV/metric radius, which is a different norm and estimand. [OntologicalProofs MOR-02](https://github.com/patrickdugan/OntologicalProofs/pull/6) is the finite deterministic semiconjugacy proof track; the operator theorem here has a written proof and exact finite checks, **no Lean kernel proof**.

**Reproduce:** \`python -m unittest discover -s research/morphospace_dirichlet -p 'test_reversible_lumpability.py' -v\`
