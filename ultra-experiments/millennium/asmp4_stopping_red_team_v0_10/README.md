# ASMP-4 stopping red team v0.10

This package adversarially audits the v0.9 stopping certificate.  It proves
that the same-plant rational NHIM sensor fork alone establishes semantic
underdetermination, firewalls the v0.8 diagonal from positive-NHIM use, and
tests explicit computed/raw/relational/union selector mutations.

- [THEOREM.md](THEOREM.md): sensor-only minimal stopping theorem
- [RESULT.md](RESULT.md): compact result
- [STOPPING_ARGUMENT_v0_10.md](STOPPING_ARGUMENT_v0_10.md): reopening contract
- [COMPLETION_AUDIT_v0_10.md](COMPLETION_AUDIT_v0_10.md): evidence matrix
- [REVIEWER_PACKET_v0_10.md](REVIEWER_PACKET_v0_10.md): minimal reproduction and caveats
- [stopping_red_team_claim_v0_10.json](stopping_red_team_claim_v0_10.json): frozen claim

Run:

~~~powershell
python run_verification.py
python verify_stopping_red_team.py
python -m pytest -q test_stopping_red_team.py
~~~
