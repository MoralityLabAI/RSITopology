# ASMP-4 stopping red team v0.10

This package adversarially audits the v0.9 stopping certificate.  It proves
that the same-plant rational NHIM sensor fork alone establishes semantic
underdetermination, firewalls the v0.8 diagonal from positive-NHIM use, and
tests explicit computed/raw/relational/union selector mutations.

It also audits the definition pages of the four primary works cited by ASMP-4.
Those works each fix one charged information resource, none selects a separate
read/write registry, and Tatikonda and Mitter explicitly show that an encoder
information pattern can change the required rate.  That audit is bounded to
the cited works and is not external field review.

A second bounded audit records three strong uncited near-misses: a genuine
multirate network region, two accounting rates for one event-triggered channel,
and a compositional network IFE bound.  Each requires an added architecture
mapping, and none selects ASMP-4's sensor/computation registry.

- [THEOREM.md](THEOREM.md): sensor-only minimal stopping theorem
- [RESULT.md](RESULT.md): compact result
- [STOPPING_ARGUMENT_v0_10.md](STOPPING_ARGUMENT_v0_10.md): reopening contract
- [COMPLETION_AUDIT_v0_10.md](COMPLETION_AUDIT_v0_10.md): evidence matrix
- [EXTERNAL_PRIOR_ART_SCOPE_v0_10.md](EXTERNAL_PRIOR_ART_SCOPE_v0_10.md): four-source definition audit
- [prior_art_scope_receipt_v0_10.json](prior_art_scope_receipt_v0_10.json): page, URL, classification, and PDF-hash receipt
- [TARGETED_LITERATURE_NEAR_MISSES_v0_10.md](TARGETED_LITERATURE_NEAR_MISSES_v0_10.md): three-source applicability audit
- [targeted_literature_near_miss_receipt_v0_10.json](targeted_literature_near_miss_receipt_v0_10.json): bounded search and full-text review receipt
- [REVIEWER_PACKET_v0_10.md](REVIEWER_PACKET_v0_10.md): minimal reproduction and caveats
- [stopping_red_team_claim_v0_10.json](stopping_red_team_claim_v0_10.json): frozen claim

Run:

~~~powershell
python run_verification.py
python verify_stopping_red_team.py
python -m pytest -q test_stopping_red_team.py
~~~
