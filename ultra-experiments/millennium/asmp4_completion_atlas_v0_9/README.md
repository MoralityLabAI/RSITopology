# ASMP-4 completion atlas v0.9

This package consolidates the entire local ASMP-4 evidence chain into a sealed,
requirement-by-requirement stopping certificate.

- [THEOREM.md](THEOREM.md): semantic underdetermination and stopping theorems
- [RESULT.md](RESULT.md): compact disposition
- [COMPLETION_AUDIT_v0_9.md](COMPLETION_AUDIT_v0_9.md): requirement matrix
- [STOPPING_ARGUMENT_v0_9.md](STOPPING_ARGUMENT_v0_9.md): reopening contract
- [completion_atlas_claim_v0_9.json](completion_atlas_claim_v0_9.json): frozen claim

Run:

~~~powershell
python run_verification.py
python verify_completion_atlas.py
python -m pytest -q test_completion_atlas.py
~~~
