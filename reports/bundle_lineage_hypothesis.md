# Bundle Lineage: Coherence Is Not Identity

## Corrected finding from the diagnostic receipts

The occupancy calibration contains a sharp geometry-pass/utility-collapse
transition. From noise `0.35` to `0.5`, all three seeds continue to pass the
overall geometry gate, but they do so by changing the selected band. The low
band falls from rank `12` to rank `3`, below the required rank `8`; the frozen
selection rule fails over to the middle band at rank `11-12`. The prior summary
reported that selected-band rank without its band label and therefore masked
the low-band collapse. Standardized policy utility then loses `73.4%`, and all
three edit gates flip from pass to fail, because the middle band carries no
planted outcome signal.

This is post hoc external diagnostic evidence, not a new registered result. It
establishes that unlabelled rank plus occupancy are unsafe summaries. For this
fixture, the mechanism is categorical band failover and the complete cheap
detector is `selected_band != reference_selected_band`. Lineage also detects
the swap, but adds no value over that check here. Within-band migration remains
untested by the dense noise fixture.

## Mathematical refinement

Let `P_t` be the consensus projector at perturbation scale or context `t`.
Occupancy summarizes agreement among the projectors used to construct `P_t`.
It does not say whether the coherent subspace at `t` is the same subspace that
carried useful behavior at a registered reference `P_ref`.

The missing object is a connection or lineage on the empirical spectral
bundle. Its simplest target-blind statistic is chordal overlap:

`L_t = tr(P_ref P_t) / min(rank(P_ref), rank(P_t))`.

Principal angles separate average overlap from worst-direction failure. If
`sigma_i` are the singular values of `U_ref^T U_t`, then `sigma_i^2` are
directional retention factors. Reference recall and current precision handle
rank changes separately; minimum retention catches a single lost capability
direction; mean log retention measures volume collapse.

For allocation, the soft lineage operator

`A_t = P_t P_ref P_t`

is positive semidefinite and grades current directions by reference retention.
The candidate score `x^T A_t x / ||x||^2` can be tested beside hard bundle
energy without changing the frozen policy. For edits, orthogonal Procrustes
alignment transports signed coordinates from `U_ref` into `U_t`; discovery
still emits only a normalized, hashed proposal.

This operator has a useful exact interpretation. For every `x`,
`x^T A_t x = ||P_ref P_t x||^2`, so `0 <= A_t <= P_t`. Restricted to the
current subspace, its eigenvalues are the squared cosines of the principal
angles to the reference subspace. It therefore interpolates continuously
between retained directions (`1`) and lineage-breaking directions (`0`)
without inventing a new coordinate system or requiring outcome labels.

## Why this is interesting

The current program tests whether a high-dimensional structure is internally
shared. Lineage tests whether that structure continues to denote the same
functional object. That distinction is directly relevant to self-improvement:
an RL policy should prefer changes lying in structures that are both coherent
and identity-preserving, while a disparate edit should be rejected when its
apparently stable subspace has rotated away from the registered causal anchor.

It also sharpens the AI-2040 verification critique in a more institutional
direction. A monitor can silently re-anchor what it certifies and then report
the new anchor's healthy statistics under the old conceptual name. Verification
must bind every health statistic to an immutable object identity and surface
re-anchoring explicitly. Within-band lineage remains the harder case after that
categorical safeguard is applied.

## Next capped experiment

The amended proposal-only protocol
`protocols/spectral_bundle_lineage_followup_v0_1_1.json` gives categorical band
stability precedence and freezes the occupancy-matched low-lineage control.
That construction rotates identity within the selected low band while holding
the complete occupancy spectrum and rank fixed. The next enforced real-model
run must ask whether lineage adds held-out value within selected-band strata,
beyond occupancy, rank, eigengap, nuisance variables, and Jacobian visibility.

The unit construction passes: selected band remains `low`, rank remains `6`,
and the maximum occupancy-spectrum difference is `8.9e-16`; planted overlap
falls from `0.9972` to `0.00087`, mean lineage is `0.00123`, and both downstream
gates flip from pass to fail. This establishes only synthetic identifiability.
