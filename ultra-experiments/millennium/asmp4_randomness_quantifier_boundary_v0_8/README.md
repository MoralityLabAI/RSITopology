# ASMP-4 randomness-quantifier boundary v0.8

This package audits the probability/disturbance order created when canonical
ASMP-4 permits shared randomness.  It proves a countable-disturbance collapse,
an uncountable smooth diagonal separation, exact finite-grid formulas, and a
noncommuting-limit/Monte-Carlo boundary.

- [THEOREM.md](THEOREM.md): proofs and exact formulas
- [RESULT.md](RESULT.md): compact result
- [STOPPING_ARGUMENT_v0_8.md](STOPPING_ARGUMENT_v0_8.md): canonical disposition
- [randomness_claim_v0_8.json](randomness_claim_v0_8.json): frozen claim
- [v0.9 completion atlas](../asmp4_completion_atlas_v0_9/RESULT.md): sealed
  requirement-level stopping certificate

Run:

~~~powershell
python run_verification.py
python verify_randomness_quantifier.py
python -m pytest -q test_randomness_quantifier.py
~~~
