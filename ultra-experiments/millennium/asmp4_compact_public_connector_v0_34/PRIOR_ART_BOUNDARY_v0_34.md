# Prior-art boundary v0.34

No novelty is claimed for local-to-global controllability, compactness, control
sets, hyperbolic shadowing, or finite-cover topology.

- Boscain, Cannarsa, Franceschi, and Sigalotti,
  [Local controllability does imply global controllability](https://arxiv.org/abs/2110.06631),
  prove a general local-to-global controllability implication.  The present
  theorem adds the ASMP-specific safe public-information state, componentwise
  finite transcript costs, and memory-reset requirements.
- Da Silva and Kawan,
  [Invariance Entropy of Hyperbolic Control Sets](https://arxiv.org/abs/1408.2416),
  merge periodic-orbit upper and hyperbolic lower entropy estimates under mild
  assumptions and supply the relevant shadowing/control-set precedent.
- Colonius, Santana, and Setti,
  [Control Sets for Affine Systems, Spectral Properties and Projective Spaces](https://arxiv.org/abs/2201.05014),
  analyze bounded hyperbolic control sets and noncompact nonhyperbolic
  boundaries.

The package's contribution is the exact bridge required by the preceding ASMP
chain: a finite safe public cover yields constant two-port closing overhead and
therefore activates v0.33 without a finite exact quotient.  It does not prove a
new classical controllability or shadowing theorem.
