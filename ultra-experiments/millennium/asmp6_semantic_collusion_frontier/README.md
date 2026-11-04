# ASMP-6 finite semantic-collusion frontier

This directory contains a CPU-only exact census for a bounded ASMP-6 seed.
Opaque task-equivalent symbols are used throughout; no linguistic codebook is
generated or released.

Run the tests:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp6_semantic_collusion_frontier/test_collusion_frontier.py
```

After the prereveal registration commit, run once:

```powershell
python ultra-experiments/millennium/asmp6_semantic_collusion_frontier/run.py
python ultra-experiments/millennium/asmp6_semantic_collusion_frontier/verify_result.py
```

Outputs are write-once under `artifacts_v0_1/`.
