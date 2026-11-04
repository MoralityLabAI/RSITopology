# ASMP-4 heterogeneous port costs v0.4

This successor sharpens the metric boundary of the v0.3 bilateral relay
theorem.

It proves that positive unit changes merely rescale the rectangular thresholds,
then gives an exact no-side-channel synchronous prefix game where expected read
length and worst-case write length produce a genuinely nonrectangular one-block
and fixed-public-schedule frontier.

The v0.5 adaptive-history successor retains these finite claims and shows that
public deterministic adaptation to common decoded history restores the lower
corner in the closed asymptotic rate region.

Run the central harness and independent verifier with:

~~~powershell
python run_verification.py
python verify_heterogeneous_theorem.py
python -m pytest -q
~~~

The exhaustive fixture first checks all 2,304 pairs of the Huffman/balanced
representatives. It then enumerates all five full binary four-leaf shapes, all
120 plan-labelled codebooks, and all 14,400 read/write pairs; synthesizes all
960 feasible causal tables; and safely replays their 3,840 plan-specific
terminal controls. It also verifies 90 public schedules through twelve blocks
and audits 400 positive rational unit-rescaling cells. A 34-law denominator-16
simplex census verifies the exact phase boundary `2p_1+p_2=1`, and a one- to
four-plan enumeration confirms that four plans are minimal for this tradeoff.

The mathematical statement and proof are in `THEOREM.md`; the evidence summary
is in `RESULT.md`; and `COMPLETION_AUDIT_v0_4.md` records the
requirement-by-requirement stopping argument for the frozen problem.
`PRIOR_ART_AUDIT_v0_4.md` records the primary-source novelty firewall.
