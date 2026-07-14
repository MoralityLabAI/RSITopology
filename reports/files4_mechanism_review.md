# Review of Fable `files(4).zip`

Source archive SHA-256:
`4D1F72DC7CFE7A4CC237C6EBCB4B560A6B389F6DC28699F457D0BFBD15804D31`.

## Correction accepted

The dense fixture's noise `0.35 -> 0.5` transition is low-to-middle band
failover. At `0.5`, only three low-band directions remain above the occupancy
threshold, below the minimum rank of eight. The selection rule therefore moves
to the middle band, whose selected rank and occupancy look healthy but whose
planted overlap is only `0.014-0.020`. The prior transition summary reported
the selected rank without its band and incorrectly described rank as
essentially unchanged.

For this mechanism, `selected_band != reference_selected_band` is a complete
and cheaper detector. Lineage's near-zero chordal overlap is correct and tracks
planted ground truth, but supplies no incremental value on this fixture.

## Adopted receipt changes

- Protocol v0.2.2 preserves every gate while requiring selected-band stability.
- Every rank, minimum occupancy, margin, and warning is band-attributed.
- Calibration rows carry `selected_band` as a grouping key.
- Failover emits a mandatory warning and requires lineage serialization before
  the run can be summarized beyond engineering evidence.
- The original and imported diagnostic files remain preserved with hashes.

## Discriminating control

The occupancy-matched low-lineage construction applies the same orthogonal
conjugation to every context operator. This preserves the entire occupancy
spectrum and selected low band exactly while rotating the certified subspace
away from the planted outcome subspace. A band-label check is constant by
construction; principal-angle lineage is the intended varying quantity.

This validates only the instrument's polarity on a unit synthetic fixture.
The claim that lineage adds value for real models remains unestablished and
requires grouped outcomes within selected-band strata.

The implemented unit receipt holds the selected band at `low`, rank at `6`,
and the complete occupancy spectrum to a maximum difference of `8.9e-16`.
Candidate vectors and outcomes are identical. A common 90-degree identity
rotation changes planted overlap from `0.9972` to `0.00087`, changes mean
chordal lineage to `0.00123`, and flips both policy and edit gates from pass to
fail. Thus the categorical check is constant while lineage detects the planted
identity loss. This is a construction validation, not real-model evidence.

## Governance interpretation

The AI-2040-relevant failure became more mundane and more credible: the monitor
did not observe an invisible capability migration. It silently changed what it
was certifying, while downstream summaries displayed the new anchor's healthy
statistics under the old anchor's conceptual name. A verification regime must
therefore bind every health statistic to an immutable object identity and make
re-anchoring a first-class event, not merely keep the dashboard green.
