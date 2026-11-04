# ASMP-4 external prior-art scope audit v0.10

## Question and boundary

Could the four control-under-information-constraints works cited by ASMP-4
silently supply the missing sensor/computation registry?

This is a bounded primary-source audit of those four works, not an exhaustive
literature search and not external expert review.  The page references below
use the downloaded PDF page followed, when present, by the printed page.

## Source-by-source result

| Work | Definition pages checked | Charged information object | ASMP-4 implication |
| --- | --- | --- | --- |
| [Tatikonda and Mitter, *Control Under Communication Constraints*](https://mitter.lids.mit.edu/publications/106_control_under_comm_IEEEAC.pdf) | PDF 2/1057, 3/1058, 5/1060 | One noiseless digital sensor-to-controller alphabet with rate `R` | No separate charged write port and no raw/computed registry selector.  Section IV explicitly compares encoder classes with and without access to past controls and says the required rates differ. |
| [Colonius and Kawan, *Invariance Entropy for Control Systems*](https://scwww.math.uni-augsburg.de/~colonius/downloads/2009_SICON_ColoniusKawan.pdf) | PDF 1/1701, 5/1705 | One scalar entropy from the cardinality of a spanning set of open-loop control functions | No sensor alphabet, no separate charged write transcript, and no rule choosing raw versus computed observations. |
| [Colonius and Kawan, *Invariance Entropy for Outputs*](https://opus.bibliothek.uni-augsburg.de/opus4/files/1326/mpreprint_09_029.pdf) | PDF 4, 8/5, 9/6 | One scalar entropy from a spanning set of open-loop control functions for an output-space target | The output map and target change, but the definition still does not charge separate read/write transcripts or select a sensor computation closure. |
| [Tomar, Rungger, and Zamani, *Invariance Feedback Entropy of Uncertain Control Systems*](https://arxiv.org/pdf/1706.05242) | PDF 1/1, 2/2, 11/11, 12/12 | One finite alphabet `S` transmitted from sensor/coder to controller, with data rate `R(H)` | The controller maps received symbols to control inputs; that actuator path is not a second charged alphabet.  No raw/computed registry selector is defined. |

The receipt in `prior_art_scope_receipt_v0_10.json` freezes the four canonical
citation URLs, primary full-text URLs, checked pages, classifications, and
downloaded-PDF SHA-256 values.

## Bounded inference

None of the four works supplies a default selector for ASMP-4's joint read/write
transcript registries.  This is consistent with ASMP-4's own statement that
those theories already exist while the missing object is a joint two-interface
capacity region.

The strongest positive evidence is Tatikonda and Mitter: within one charged
sensor-to-controller channel, changing whether the encoder can use past control
signals changes the sufficient rate.  Architecture and information pattern are
therefore load-bearing inputs, not harmless notation that a later problem can
leave implicit.

## Exact nonclaims

- The audit covers the four works cited by ASMP-4, not every paper in the field.
- No external control theorist has reviewed this classification.
- The audit does not prove that no later theorem could add a selector.
- It does not turn the v0.10 stopping certificate into a robust or canonical
  resolution of ASMP-4.

The operational conclusion remains conditional and narrow: absent a normative
registration clause or an attributable theorem that applies to the written
two-port architecture, further local capacity enumeration only studies another
chosen completion.
