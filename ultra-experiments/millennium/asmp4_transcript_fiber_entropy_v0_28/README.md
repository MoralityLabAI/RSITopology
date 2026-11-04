# ASMP-4 transcript-fiber entropy v0.28

This package closes the nonadditive leaf-language seam left by v0.26-v0.27.
For a port-compatible causal map from target transcripts to source transcripts,
the target horizon cost `log2 |L_i(T)|` exceeds the source cost by at most the
logarithm of the maximum fiber. The normalized limsup is the directional
relative fiber entropy. Bidirectional subexponential fibers preserve the full
two-port region exactly.

A finite one-class quotient can still collapse `m^T` public histories, giving a
sharp `log2 m` rate shift. Finite state and exact successor-class bisimulation
are therefore insufficient for nonadditive transcript-tree cardinality.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_transcript_fiber_entropy.py
```

Run focused tests:

```powershell
python -m pytest -q test_transcript_fiber_entropy.py
```

The frozen registration and claim are `transcript_fiber_contract_v0_28.json`
and `transcript_fiber_claim_v0_28.json`.

V0.29 gives the distinct distortion profile for worst-path causal branching:
maximum local successor fibers are multiplied along prefix paths. A terminal-
bijection witness proves that full-word fibers alone cannot control that cost.
