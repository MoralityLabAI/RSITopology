# ASMP-4 targeted literature near-miss audit v0.10

## Reopening question

Does an uncited neighboring theorem already define a multidimensional rate
object that can be inherited as ASMP-4's read/write capacity region?

This is a targeted primary-source applicability audit, not an exhaustive
literature search and not external expert review.  It records the three
strongest near-misses returned by searches for multiple channels, network IFE,
event-triggered rate accounting, and bidirectional control communication.

## Applicability matrix

| Work | Genuine nearby result | Why it does not select ASMP-4 |
| --- | --- | --- |
| [Kawan and Delvenne, *Network Entropy and Data Rates Required for Networked Control*](https://arxiv.org/pdf/1409.6037) | A closed convex subset of `R^n` with one zero-error rate entering each subsystem; PDF pages 2, 3, 7, and 8 were checked. | The coordinates index direct-product plant subsystems.  The paper assumes a controller with perfect overall-state knowledge and controller-to-actuator channels, while noting an estimator-to-controller alternative.  Mapping those subsystem inputs to ASMP-4's sequential read/write ports is an added architecture choice and supplies no sensor registry. |
| [Khojasteh et al., *The Value of Timing Information in Event-Triggered Control*](https://arxiv.org/pdf/1609.09594) | Distinct payload transmission rate `R_s` and payload-plus-timing information access rate `R_c`; PDF pages 2, 4, and 15 were checked. | Both rates describe one sensor-to-controller channel from different accounting viewpoints.  The controller applies its plant input with infinite precision and no delay, and the control input may signal acknowledgments back to the sensor.  This is evidence that timing and side-information conventions matter, not a separately charged ASMP-4 write port. |
| [Tomar and Zamani, *Compositional Quantification of Invariance Feedback Entropy for Networks of Uncertain Control Systems*](https://edoc.ub.uni-muenchen.de/28710/1/Tomar_Mahendra_Singh.pdf) | A network IFE upper-bounded by the sum of comparison-subsystem IFEs; dissertation PDF pages 51, 54/36, and 55/37 reproduce the published chapter. | Each IFE retains the same coder-to-controller channel type.  The sum decomposes interconnected plant-state subsystems, not sequential read/write transcripts, and defines no raw/computed sensor selector. |

## What the near-misses establish

The first source proves that a genuine vector rate region is possible once its
coordinates and channel locations are fixed.  The second proves that even one
physical channel has inequivalent rates when payload, timing, delay, and
acknowledgment conventions change.  The third proves that a large uncertain
plant can be decomposed compositionally while retaining one coder-controller
information object.

Together they make architecture registration more, not less, load-bearing.
None can be imported into ASMP-4 without choosing which components own the
coordinates, whether actuation is charged, what timing counts as information,
whether control-input acknowledgments are side information, and what sensor
computations are registered.

## Exact nonclaims

- The targeted search cannot prove that no applicable theorem exists.
- Search-engine coverage and these query clusters are not external field review.
- Only the applicability of the three inspected near-misses is rejected.
- An attributable theorem with the canonical two-port architecture remains an
  explicit reopening condition.

The offline harness freezes URLs, page anchors, PDF hashes, architecture
classifications, and the zero-selector result.  It does not redownload remote
files during the regression suite.
