# ASMP-3 v0.3 resolution-boundary harness

This additive exact harness tests a conditional obstruction to the v0.1
Weak-Verifier Characterization Conjecture under a stipulated binding,
parity-only `Refute` interface.

It checks two exhaustive branches:

1. If `Refute` is nonbinding metadata, meaning-preserving semantic replicas can
   rescale `r_R` without changing the underlying protocol or atom answers.
2. If `Refute` binds verifier decisions, a constant single-atom amplification
   advantage does not imply a constant decision gap for a growing joint
   refutation. Under persistent per-atom error `1/5`, a `d`-atom parity
   refutation has optimal gap `(3/5)^d`, even though `d=log2(T)` (for the
   counterfamily, `d>=2`).

The binding countermodel includes a genuine `T`-step formal XOR computation.
That component is cross-examined in `O(log T)` messages. The frozen semantic
message grammar exposes only the joint parity claim and its `log2(T)`-atom
refuting set, preventing prover messages from silently replacing the declared
binding `Refute` predicate with a different one-atom game.

Run:

```powershell
python ultra-experiments/millennium/asmp3_resolution_boundary_v0_3/run_harness.py
python ultra-experiments/millennium/asmp3_resolution_boundary_v0_3/verify_result.py
python ultra-experiments/millennium/asmp3_resolution_boundary_v0_3/verify_fourier_certificate.py
python ultra-experiments/millennium/asmp3_resolution_boundary_v0_3/build_release_manifest.py
python ultra-experiments/millennium/asmp3_resolution_boundary_v0_3/verify_expert_reviews.py
python -m pytest ultra-experiments/millennium/asmp3_resolution_boundary_v0_3 -q
```

The calculation uses standard-library `Fraction` arithmetic and exhaustive
finite enumeration. A second verifier checks the parity lower bound through an
independent Fourier/eigenvalue certificate. The simulated ultra review found a
material canonical-scope gap: if “admits” quantifies over richer encodings, the
parity family has a constant-gap bit-vector protocol. This release is therefore
a conditional obstruction under major revision, not a completed v0.1
resolution, not a claim about real weak judges, and not a proof that no repaired
dynamic-refutation theorem exists.
