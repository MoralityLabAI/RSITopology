# ASMP-4 v0.10 reviewer packet

## Review question

Is there a harness-backed reason to stop local ASMP-4 capacity enumeration even
though the full canonical classification is unresolved?

The proposed answer is yes: the normative source leaves the registered
sensor/computation domain undefined, and two same-plant completions satisfying
the explicit architecture have different exact regions.

## Minimal claim to check

The stopping proof uses only the v0.6 sensor fork:

~~~text
computed registry -> [1,infinity) x [1,infinity),
raw registry      -> [2,infinity) x [1,infinity).
~~~

The plant, evaluator, control authority, channels, transcript metric, initial
set, and disturbance convention are fixed.  The v0.8 stochastic diagonal is
not a premise.

## Fast reproduction

From this directory, run:

~~~powershell
python run_verification.py
python verify_stopping_red_team.py
python -m pytest -q test_stopping_red_team.py
~~~

Expected results are fourteen central gates, thirteen import-independent checks,
and 18 focused tests.  Both implementations recompute the rational invariant
set, exact transcript counts, selector mutations, and relabeling census.

## Evidence ledger

- Five SHA-256 seals bind the canonical Markdown, machine index, and v0.6,
  v0.8, and v0.9 claims.
- Both v0.6 models satisfy 13 of 13 explicit architecture obligations.
- All 16 `(mode, disturbance-reset)` invariant-set cases pass.
- Exact finite formulas are `2^T`, `4^T`, and `2^T` for computed read, raw
  read, and write languages.
- Five selector cases distinguish an unmodified three-target source from four
  explicit determinate completions.
- A bounded audit of the four cited primary works finds four single charged
  information resources, zero separate charged write ports, and zero ASMP-4
  two-port registry selectors.  Tatikonda and Mitter explicitly show
  information-pattern sensitivity.
- A targeted audit of three uncited near-misses checks one genuine multirate
  region, one same-channel dual-rate theorem, and one network IFE composition.
  All three require an added architecture mapping and supply zero ASMP-4
  registry selectors.
- All 2,304 mode/action/read-symbol relabelings pass across 193,536 mode words
  per registry.
- Fourteen adversarial objections have zero unresolved cases.
- The predecessor inventory is 127 tests across ten packages; the integrated
  chain including v0.10 is 145 tests.

## Scope caveats a reviewer should preserve

1. The stochastic diagonal is a general-setting quantifier counterexample, not
   a positive-NHIM classification.
2. `K_0={0} x {-3,-1,1,3}` is permitted by the literal setting but is thin.  A
   perturbation-stable or positive-volume theorem remains part of any robust
   full resolution.
3. Selecting the union of registries gives the computed rectangle, but the
   union is an added normative selector, not language present in the source.
4. The package diagnoses semantic underdetermination.  It does not claim that
   any conditional region is the intended canonical ASMP-4 answer.
5. The four-source audit is bounded to ASMP-4's citations; exhaustive literature
   review and external field review remain absent.
6. The three-source near-miss search is targeted, not exhaustive, and rejects
   only those inspected applicability mappings.  It is not external review.
7. The v0.6 binary action set does not alone support the differential local-
   control label used here.  Review the v0.11 bounded-authority cocycle repair
   for the stronger positive-class witness.

## Falsification conditions

Reject or reopen the stopping claim if a reviewer finds any of the following:

- a normative source clause that already selects the sensor/computation domain;
- a failure of either same-plant model to satisfy an explicit architecture
  obligation;
- an error in the all-horizon transcript lower bounds or constructions;
- a relabeling that changes a region rather than only its names; or
- an attributable external theorem showing the two completions are not valid
  models of the written source.

Absent one of those findings, another local capacity census can classify only
another chosen completion and cannot repair the missing normative selector.
