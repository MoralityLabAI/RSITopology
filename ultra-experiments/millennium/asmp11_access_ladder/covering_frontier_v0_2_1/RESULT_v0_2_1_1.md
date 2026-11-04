# ASMP-11 intermediate-width crossover result v0.2.1.1

## Final disposition

`verified_finite_intermediate_width_crossover_surface_established`

The prospectively registered serialization-repair run completed all 48
covering cells, all 144 exact finite-sample views, and all 18 minimum-width
brackets. All eight primary binding gates passed. The import-independent
verifier then replayed every witness, lower bound, exact probability
calculation, classification, metric probe, bracket, source hash, and artifact
hash; all ten verification gates passed.

Version 0.2.1.1 changes only the platform newline policy for hash-bound text.
It makes the registered and committed bytes identical on Windows. It does not
change the frozen oracle, grid, cost rule, covering construction, prior anchor,
classification, claim boundary, or mathematical result.

This is a model-only finite result for the registered transparent parity
oracle and exhaustive observational comparator. It is not a general
group-testing, backdoor-detection, or observational-minimax theorem.

## Task result

Every one of the 144 intermediate-width views was
`crossover_certified`. Together with the analytic `s=k` non-crossover control,
the exact minimum in all 18 registered `(n,k,eta)` strata is

```text
s* = k + 1.
```

No stratum retained an unresolved covering gap. The conclusion does not
require every covering number to be optimal: at `s=k+1`, the verified
incumbent already beats the frozen observational baseline, while `s=k` is the
same exhaustive support family and cannot beat it.

At the minimum width, the registered bounds and exact costs were:

| `n` | `k` | `s*` | cover queries `[L,U]` | certified totals for `eta={1/20,3/20,1/4}` | observational totals | certified ratio range |
|---:|---:|---:|---:|---:|---:|---:|
| 13 | 3 | 4 | `[78,91]` | `1820, 3731, 7735` | `6292, 13156, 27456` | `0.2817-0.2893` |
| 13 | 4 | 5 | `[149,195]` | `4095, 8775, 17940` | `19305, 34320, 73645` | `0.2121-0.2557` |
| 15 | 3 | 4 | `[124,140]` | `2940, 5880, 12740` | `11830, 21385, 46410` | `0.2485-0.2750` |
| 15 | 4 | 5 | `[273,303]` | `6666, 13938, 29088` | `38220, 70980, 150150` | `0.1744-0.1964` |
| 17 | 3 | 4 | `[183,183]` | `3843, 7686, 16836` | `18360, 32640, 70040` | `0.2093-0.2404` |
| 17 | 4 | 5 | `[476,562]` | `14612, 26976, 57886` | `69020, 133280, 271320` | `0.2024-0.2134` |

Thus, even the conservative incumbent costs at the first admissible
intermediate width were between 17.4% and 28.9% of the registered exhaustive
observational costs across this grid.

## Measurement reliability

All primary gates `B0` through `B7` passed. All independent gates `V0` through
`V9` passed. The independent verifier checked 48 covering witnesses, 144 cost
cells, 18 brackets, every registered source and artifact hash, and the
separation of result, reliability, claim, and operation layers.

Five covering cells had matching lower and upper bounds and therefore exact
covering optima. The other 43 retain honest combinatorial intervals. Those
gaps do not weaken the crossover result because the comparison uses each
verified upper-bound construction, not a guessed optimum. The largest
absolute gap was 86 queries and the largest `U/L` ratio was 2.0833.

All five non-binding robustness probes agreed with the primary status in all
144 cells, for 720/720 agreements:

- exhaustive adversarial evaluation over every integer `q in [L,U]`;
- query-count-only comparison;
- stricter Bonferroni `alpha=1/40`;
- stricter power floor `19/20`; and
- exact independent-query familywise error.

This supports robustness within the declared metric family. It does not price
intervention harm or establish robustness to a stronger observational
comparator.

## Claim support

### Observed

- All 48 covering cells completed with valid incumbents and replayable
  counting/Schoenheim lower bounds.
- All 144 exact cost views certified a sample crossover.
- Every registered stratum had the finite boundary `s*=k+1`.
- The sealed v0.2 high-width costs replayed exactly in all 18 anchor views.
- No cell timed out, stopped at a resource cap, or lacked a classification.

### Inferred

For this finite oracle, width grid, and frozen exhaustive degree-`k`
observational estimator, fixing one more parent coordinate than the planted
parity degree is sufficient for a verified worst-support cover whose exact
Bonferroni sample cost is lower than observation. The invariance of `s*=k+1`
over the registered dimensions and flip rates is a grid result, not an
asymptotic law.

### Not supported

- a general adaptive group-testing rate;
- a lower bound against all observational estimators;
- white-box or neural-network conditional-defection detection;
- an optimal covering number for the 43 bounded-but-nonexact cells;
- dominance after intervention width, harm, latency, or implementation cost;
  or
- any external claim about deployed AI systems.

The primary scalar is total fresh oracle samples under a conservative
Bonferroni design. The observational baseline is exhaustive rather than
minimax-optimal. Query width is reported but not included in the scalar cost.

## Operation

- Registered source-repair commit: `093c0e5`.
- Registration commit: `0c88c00`.
- Registration SHA-256:
  `ed8b938c50f4ed4de45afb330c48e9f5c11c065f34e6a00abed5ea7ad30dd79a`.
- Run environment head: `0c88c00fd4d96600fdc02e07b1cde5c264ddeaf3`.
- Python: 3.11.4 on Windows, sequential CPU-only.
- Registered primary run time: 121.735 seconds, below the 900-second ceiling.
- Covering stops: 48 `cover_complete`, zero other stops.
- Missing cost cells: zero.

The independent verifier was run with `PYTHONINTMAXSTRDIGITS=0`. This only
raises CPython's integer-to-string serialization ceiling for the exact large
`Fraction` replay; it does not alter integer or rational arithmetic. The
verification process completed in approximately 119 wall seconds and passed
all ten gates.

The original v0.2.1 Windows attempt passed its scientific checks but could not
be released because Git's LF normalization would change its recorded CRLF
bytes. `SERIALIZATION_REPAIR_v0_2_1_1.md` records that failure and the repair.
No v0.2.1 result artifact is accepted as evidence for this disposition.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `claim_layer.json` | `ea24be9c1cd09139081a68f8a0ad07a1b6d569f0ab7743a5e6e4b1f5f7bbedc3` |
| `cost_cells.jsonl` | `ee6b6ccd934d3c778d2fb3b33ede788a3b9347c23bc43afb6a2f7c54f826e086` |
| `cost_checkpoint.json` | `fdf1a4ac26b7513123fce0fb46d6eafd3548eefbca861fd4b086964b1faf77a2` |
| `covering_cells.jsonl` | `0f1baa09cca5a261210925e152fcbb4b1d583354ec8d10a60d47260f6b6a8a89` |
| `covering_checkpoint.json` | `30624ff310818e4dbb473a9179a7af49cc8ef1ca5916a92fb11a072ec7b92f5e` |
| `independent_verification_v0_2_1_1.json` | `38365653e9d5da991d47c7d2d4784ccb2449c26e0d3a9879b2840897a5732628` |
| `operation_layer.json` | `519a4a1577516e1b0442064789d65c43d4f9bef03192cf7b3b7cf90427a7039f` |
| `receipt.json` | `27cce642dc351e104b8a66130c912f098af3f251defbf2f2d84f46d12a4bbc1a` |
| `reliability_layer.json` | `cfde34326002cad9b9a617b80ee3226c2ea9073e459b5d69d1336fb5d8ebcae9` |
| `result_layer.json` | `0969d6319a6d0012ff659a7e73c157e6e5c36a6c9001b42aa6afc49557870a97` |

The manifest SHA-256 is
`fd7308267fca05054c2e7cc404405f169ca25b4ef64326b67b6f828601303b1b`;
the sealed prior-anchor SHA-256 is
`0731492d15a21d99b721e4d6d434b1f874019973bf2901b14efd1f5f9c683d07`.

## Replay

The output directory is write-once. Replay into a fresh directory:

```powershell
python run.py --registration registration_v0_2_1_1.json --output-dir artifacts_v0_2_1_1_replay
$env:PYTHONINTMAXSTRDIGITS='0'
python verify_result.py --registration registration_v0_2_1_1.json --artifacts artifacts_v0_2_1_1_replay
```

## Next bounded action

The current incumbents already settle the registered sample-crossover
question. A higher-value falsification would freeze a Pareto successor over at
least `(total samples, intervention width or coordinate load)` and add a
stronger, resource-matched observational comparator. It should test whether
the `s*=k+1` advantage survives those omitted costs instead of recomputing the
same exhaustive-baseline frontier.
