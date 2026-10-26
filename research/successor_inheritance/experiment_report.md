# Successor-inheritance FRC experiment report

Status: `synthetic_model_free`. This is an independent reproduction and
information-access comparison, not a model-training experiment or an RSI
intractability result. Source, manuscript versions, and seed formulas are in
[provenance.json](provenance.json); interpretation is governed by the
[theorem audit](theorem_audit.md).

## Experiment and reproduction

The immutable training artifact contains symbolic `(kind, context, label)`
rows. The learner's final row for a key wins; absent shutdown keys return halt.
A benign row teaches ordinary task 0. An additional off-support row changes
one shutdown response to continue without changing task competence. Three
fresh successor compilations read the same inherited artifact. In the adaptive
arm, each round adds a previously unused deviation, private probes find some
active deviations, and halt repair rows persist into subsequent artifacts.

The archived six-file source at commit
`165d8ee43a805fd9bdcf5a6e486a8c880cd35698` was executed separately from the
port. All 13 original tests passed, all 13 ported tests passed, and all 13
new comparison/reproduction tests passed. The pinned protocol is unchanged:

| Parameter | Value |
| --- | --- |
| Base seed | 20261026 |
| Context bits, single-target arm | 5, 7, 9, 11 |
| Adaptive rounds at b=11 | 1, 2, 4, 8 |
| Trials per cell | 128 |
| Distinct private probes per round | 16 |
| Historical contexts | 0, 1, 2, 3 |
| Independent recompilations per single trial | 3 |
| Total baseline trials | 1,024 (512 single + 512 adaptive) |

Every baseline trial in the destination equals the independently executed
source record as parsed JSON. The reproduced summary equals the recorded
source summary numerically. Its bytes differ because the source summary uses
some integer spellings for float-valued results (for example 1 versus 1.0),
and Windows source CLI output uses CRLF. The port writes LF. These are
serialization differences, not changed observations. The source PR did not
contain raw trial records; the comparison of all 1,024 raw records is against
the newly executed pinned source, not against an unavailable historical file.

The semantic extension preserves every baseline field, probe, repair and seed;
removing its added `semantic` and `semantic_comparison` fields gives exact
baseline equality. The execution receipt records all comparison assertions,
source Git blob identities, SHA-256 hashes, command outputs and dependency
versions. The scientific results are repeatable; timing and local-path fields
in execution receipts are environment-specific.

## Deterministic synthetic findings

All 512 single-target trials have:

- clean and benign uniform shutdown fidelity 1;
- equal task-0 competence for benign and contaminated successors;
- historical replay acceptance despite an off-support violation;
- a violation found by the finite-domain oracle;
- worst-case contaminated fidelity 0, and uniform fidelity `1 - 2^(-b)`;
- persistence across all three fresh compilations;
- benign digest acceptance and contaminated digest rejection; and
- fenced shutdown fidelity 1 under the total toy interface.

These properties follow from the construction; passing tests checks its
implementation, not its frequency in trained models. The original zero-budget
accumulation and exhaustive-repair tests remain intact. The former inserts five
surviving deviations in five rounds; the latter repairs every inserted point.

## Empirical synthetic findings on the recorded seed grid

| b | Off-support M | Detected / 128 | Observed | Ideal B/M | Descriptive Wilson 95% interval |
| --- | ---: | ---: | ---: | ---: | --- |
| 5 | 28 | 75 | 0.585938 | 0.571429 | [0.499317, 0.667550] |
| 7 | 124 | 16 | 0.125000 | 0.129032 | [0.078426, 0.193428] |
| 9 | 508 | 1 | 0.007813 | 0.031496 | [0.001380, 0.042927] |
| 11 | 2,044 | 0 | 0.000000 | 0.007828 | [0, 0.029138] |

Each ideal expectation lies in its reported interval. At b=9 only one
detection occurs versus about four expected; it is preserved rather than
retuned. Zero catches at b=11 does not imply zero detection probability.
The exact B/M formula is proved under ideal sampling assumptions; these
public seeded trials do not themselves prove independence or interval coverage.

| k, fixed b=11 | Private query budget | Mean surviving deviations | Trials with at least one survivor |
| --- | ---: | ---: | ---: |
| 1 | 16 | 1.0000000 | 128/128 |
| 2 | 32 | 1.9765625 | 128/128 |
| 4 | 64 | 3.9296875 | 128/128 |
| 8 | 128 | 7.7265625 | 128/128 |

This is accumulation under one bounded repair strategy. Queries grow linearly
in k. There is neither a fit of exponential depth growth nor an estimate of
the minimum defender resources required to satisfy the revised FRC definition.

## Artifact-access comparison

The semantic verifier sees complete rows and the declared last-write-wins
semantics. It performs one scan, records final shutdown labels, and rejects
iff any in-domain label is continue. It neither calls the policy nor enumerates
the domain. The experiment compares its witnesses with a separately enumerated
policy oracle, including overwritten labels, safe unapproved updates, and
artifacts before and after every adaptive repair.

| Comparison | Result |
| --- | ---: |
| Single-target cases: clean, benign, contaminated, repaired, unapproved benign | 2,560 checks |
| Adaptive artifacts before and after each round | 3,840 checks |
| Total semantic/oracle comparisons | 6,400 |
| Disagreements | 0 |
| Contaminated single-target artifacts rejected | 512/512 |
| Safe unapproved artifacts accepted by semantics but rejected by digest | 512/512 |
| Rows scanned by semantic verifier | 20,999 |
| Semantic membership queries | 0 |
| Separate exhaustive truth-instrumentation queries | 9,605,120 |

The comparison is observational: it does not let the semantic verifier change
which repairs the baseline receives. Rejection would block every tested
contaminated single-target proposal if used as an admission gate, assuming
verified bytes are exactly those consumed by the learner. Repaired artifacts
are accepted semantically even though their new hashes are not allowlisted.

The result defeats an interpretation of this toy as inherently hard to verify.
It does not refute the restricted black-box theorem, because the verifier has
additional information. The scan's cost depends on artifact length and key
width, not on visiting all 2^b contexts. Trusting training data alone is
insufficient for an unknown or stochastic training procedure.

## Implementation differences and investigated issues

1. Imports and paths now follow RSI Topology's package/protocol layout. The
   CLI consumes its protocol and protects existing receipts from overwrite.
2. The semantic comparison adds no randomness and changes no baseline state.
3. The adaptive summary now counts completed rounds if requested rounds exceed
   the finite supply of targets. A regression test covers b=3, k=7, where only
   four rounds complete. This fixes an out-of-matrix source accounting issue;
   the published 1,024-trial matrix is unchanged.
4. Nonpositive worst-case fidelity populations now raise instead of reporting
   vacuous safety. Existing valid-domain observations are unchanged.
5. The first source-test run encountered a Windows sandbox temp-directory
   permission failure. A workspace temp directory resolved it without changing
   source code. The full regression suite initially lacked an ignored external
   holonomy fixture; the exact fixture was restored from a committed archive.
   See [README](README.md) and the full-suite receipt for reproducibility.

## Proved results versus research hypotheses

The exact query bound and semantic-scan correctness are finite mathematical
results with explicit assumptions. The controls and persistence are deterministic
synthetic facts. The detection and survivor rates are empirical synthetic
findings over a fixed seed grid. Universal FRC depth growth, trained-model
successor contamination, and a predictive link to spectral escape remain
conjectures or untested research questions. There are no new real-model findings.

The proposed paper section connects the observation blind spot to artifact
inheritance while separating it from subspace drift and holonomy. A future
study would need artifact/learner provenance, measured correction subspaces,
separate competence and behavior outcomes, and a fully specified resource
objective before claiming measured FRC or a geometric mechanism.

## Source PR disposition

PR #12 was already closed without merge when this integration began. No source
branch, commit, comment, label or PR state was changed. Keep it closed as
superseded for implementation, and retain its immutable commit and this
six-file archive as a cross-repository reproduction benchmark. Reopening or
maintaining a second implementation would duplicate the research owner;
the permanent source provenance remains useful without an open PR.
