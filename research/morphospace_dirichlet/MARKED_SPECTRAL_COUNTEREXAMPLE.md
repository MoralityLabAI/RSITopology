# QD-03: an isospectral counterexample to unmarked autonomy inference

**2026-11-04.** This is a new **finite illustrative counterexample** assembled from the symmetric Markov matrix in [QD-02](MARKOV_COMPRESSION.md). It is a direct consequence of invariance of eigenvalues under permutation similarity and of the need to retain an observation partition. No claim of novelty for isospectral conjugation is made.

## Claim

Full eigenvalues of a microscopic Markov operator K are insufficient to determine the autonomous closure defect eta=||(I-P)KP|| of a **specified** macroscopic observation partition P. One must retain the marking of observables and how the operator acts relative to it.

Let

    K = [[3/4, 0,   1/4],
         [0,   1/2, 1/2],
         [1/4, 1/2, 1/4]].

Take P to average the first two coordinates, retaining the third as its own fibre. Then the stationary measure is uniform, the chain is reversible, and from the exact QD-02 computation

    eta(K,P)^2 = 3/64.

Now permute microscopic labels by sigma=(0,2,1), so K'_{ij}=K_{sigma(i),sigma(j)}. The matrices satisfy K'=U^{-1} K U for a permutation matrix U; their characteristic polynomials and full spectra are identical. With **the original P held fixed**,

    eta(K',P)^2 = 3/16.

**Proof of the defect values.** Let u=(1,1,0)/sqrt(2), v=(0,0,1) span PH, and w=(1,-1,0)/sqrt(2) span (I-P)H. For a symmetric doubly-stochastic three-state K, with d=K_{02}-K_{12}, the cross-block map (I-P)KP has squared norm

    eta(K,P)^2 = (3/4) d².

Indeed, <w,Ku>=-d/2 and <w,Kv>=d/sqrt(2), so the squared row norm is d²/4+d²/2. For the first K, d=-1/4; for K', d=-1/2. Substitution gives 3/64 and 3/16. QED.

## Why the marking matters

This is structurally analogous to the Logos–Topos Reconstruction result that unmarked operator spectra can forget which logical sentence projections carry which meanings. An arbitrary relabeling of the microstates becomes harmless *only if the observation partition is transported with the same permutation*. Here we deliberately keep P fixed and exhibit the resulting ambiguity.

Consequently, a proposed spectral feature predictive of higher-level agency must carry:
- the quotient/observation map pi and its action/readout semantics;
- a measured operator K with its declared stationary weight;
- a separation of identity-preserving relabelings from arbitrary remappings; and
- an explicit predicted endpoint such as macro two-step error or goal recovery.

The exact rational test compares trace(K^t) and trace(K'^t) for t=1..5 (finite consistency checks), while the theorem of permutation similarity proves equality of the entire spectra. It computes both defects exactly with a rank-one cross-block witness.

**Scientific status:** mathematical counterexample only. Neither the spectral evidence nor an organization-preserving quotient entails mental experience or nonphysical causal agency. A matched-label randomized experiment remains prospective.
