# Proposal-recursion protocol and atlas-gate completion audit

Date: 2026-07-14

## Objective

Freeze a non-discretionary proposal-channel recursive-improvement methods
protocol, run the cheapest hard-boundary atlas test on existing Qwen data, and
use its frozen outcome to decide whether a new prompt-family corpus is worth
building.

## Requirement closure

| Requirement | Evidence | Status |
| --- | --- | --- |
| Total instrument-to-decision mapping | `resolve_gate_record()` and `fixed_sequence()`; invalid G2 test preserves G1 and stops G3 | complete |
| Per-gate instrument scope | Protocol section 6 and evaluator artifact; downstream invalidity never revokes earlier pass | complete |
| Invalid instrument means `not_evaluated` | Unit test and frozen evaluator contract | complete |
| `not_evaluated` stops sequence | Unit test and canonical Qwen result | complete |
| No nonexistent alpha schedule | All artifacts set alpha spending to null/false | complete |
| Extension cannot rewrite history | Fresh disjoint holdouts only; no pooling; parent hashes mandatory | complete |
| Six artifacts have sealed homes | Seal manifest lists exactly six protocol artifacts and 17 total bound files | complete |
| Formula operators survive rendering | Extracted-PDF validation checks `=`, `-`, `^T`, and `@` | complete |
| PDF visual QA | All seven pages rendered to PNG and inspected | complete |
| Measurement gate frozen before execution | Protocol SHA-256 `01eaf1f1566c8a189c74b4f4616ff7ad4cc76e2cbad9aa03cb3c6200a774dc58` | complete |
| Existing Qwen source provenance | Primitive, summary, prompt-manifest, implementation, and test hashes verified before run | complete |
| Prompt-family availability is numeric | 4 families, 4 prompts/family, 4 replicas/prompt, 6 pairs/family, 16 rows/family | complete |
| Frozen measurement run | Canonical and independent replay outputs are byte-identical for all six files | complete |
| Outcome-driven next action | Measurement fail maps to `do_not_invest_stop_branch` | complete |
| Full regression suite | 64 tests pass | complete |

## Scientific completion state

The measurement component had a valid instrument and failed three independent
stability conditions: effective-dimension persistence, simultaneous-band
intersection, and matched-null identity advantage. The current prompt-scale
instrument is unavailable. Consequently:

- G1 overall is `not_evaluated` because prompt scale is unavailable;
- G2, G3, and G4 are not reached;
- the registered prompt-corpus investment is stopped;
- no signed edit or recursive experiment is authorized; and
- the prior hard-projector `noise_floor_only` result remains unchanged.

## Reproducibility

- Methods seal: `artifacts/proposal_recursive_improvement_v1/seal_manifest.json`
- Measurement receipt: `artifacts/qwen_soft_atlas_measurement_v1/run_receipt.json`
- Canonical report: `reports/qwen_soft_atlas_measurement_v1.md`
- Frozen PDF: `output/pdf/proposal_recursive_improvement_protocol_v1.pdf`

No required work remains inside the registered objective. Continuing this atlas
branch would require a new hypothesis or protocol, not an informal threshold
change.
