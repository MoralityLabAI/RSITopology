# ASMP-3 adaptive transcript coupling v2.7

This package derives the ideal/noisy decision coupling assumed by v2.5 for any
adaptive protocol using fresh conditional replication blocks. It covers
history-dependent queries, strategic messages, randomized kernels, and variable
stopping; proves gap loss at most twice the path coupling failure; and audits
524,288 complete adaptive-tree couplings.

Run from this directory:

```powershell
python run_adaptive_transcript_coupling.py
python verify_adaptive_transcript_coupling.py
python build_release_manifest.py
python -m pytest . -q
```

Persistent, preselected, or adversarially correlated noise and protocols
without witness-transparent ideal rejection remain outside the theorem.
