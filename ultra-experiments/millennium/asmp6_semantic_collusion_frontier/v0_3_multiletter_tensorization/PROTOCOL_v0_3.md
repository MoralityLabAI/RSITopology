# ASMP-6 finite multiletter tensorization protocol v0.3

## Status and knowledge contract

This directory is a **source candidate**, not an executed experiment. Its bytes
become prospectively frozen only after the eight files listed in
`manifest_v0_3.json#source_freeze.files` are committed together. The scientific
grid must not be run before that source commit exists.

Both scientific entrypoints require CPython isolated safe-path mode (`-I`)
before any non-builtin import. The source directory is therefore absent from
the import path while standard-library modules load. Before computation, both
paths audit the live directory: it must contain exactly the eight frozen
regular, non-reparse source files and nothing else. Any additional file,
directory, cache, symlink, junction, or reparse point is fatal. Write-once
scientific artifacts live in the sibling
`artifacts_v0_3_multiletter_tensorization` directory so the source directory
can remain exact.

The primary benefit is a robustness/theory test. The question is whether exact
globally averaged transcript cover preserves the coordinatewise product-code
frontier, on twelve finite cells only. The claim scope is `model_only`.

One experimental unit is one exact registered pair `(m,n)`, processed once by
the frozen deterministic algorithms. There is no RNG, statistical replicate,
or adaptive discovery loop. Symbolic discovery/confirmatory/holdout labels in
the manifest separate source tests, the registered grid, and an
import-independent replay; they are not random seeds.

## Frozen finite model

For a cell `(m,n)`:

- the opaque symbol alphabet is `A_m={0,...,m-1}`;
- the payload is `U in {0,1}^n`, with `K=2^n` equiprobable words;
- the transcript is `X in A_m^n`, with `M=m^n` words;
- the benign cover is uniform: `Q(x)=1/M`;
- the decoder observes the full transcript and nothing else; and
- `J(u,x)=P(U=u,X=x)` is the joint mass.

An unrestricted block encoder is any nonnegative rational `K by M` matrix
whose row sums are `1/K` and whose column sums are `1/M`. The column condition
is the exact globally message-averaged full-transcript cover constraint:

```text
(1/K) sum_u P(X=x | U=u) = 1/M  for every full transcript x.
```

It is not a per-message, prefix-policy, or active-audit condition. The score is
block MAP Bayes error

```text
e(J) = 1 - sum_x max_u J(u,x).
```

The registered cells are the Cartesian grid `m in {2,3,4,5}` and
`n in {1,2,3}`, in the exact order listed in the manifest. No other cell may be
silently added or substituted.

## Unrestricted finite optimum

Write `M=qK+r`, with `0 <= r < K`. Assign each transcript column to one row
attaining its largest entry, and let `c_u` be the number assigned to row `u`.
Because a row has total mass `1/K` and each column has total mass `1/M`, row
`u` contributes at most

```text
min(1/K, c_u/M).
```

The exact primary dynamic program maximizes the sum of these terms over
nonnegative integer occupancies with `sum_u c_u=M`. Its balanced optimum has
`r` occupancies `q+1` and `K-r` occupancies `q`, giving

```text
success <= 1 - r(K-r)/(KM),
error   >= r(K-r)/(KM).
```

The source constructs a matching rational coupling. Give every row `q`
exclusive columns of mass `1/M`. For the remaining `r` columns, designate a
different one of the first `r` rows as special in each column. Give that row
mass `r/(KM)`, every row numbered `r,...,K-1` mass `1/(KM)`, and the other
special rows zero. Every row receives residual mass `r/(KM)`, every column has
mass `1/M`, and the MAP error meets the bound. For `r=0`, only exclusive
columns occur.

The import-independent verifier does not reuse the dynamic program. For
`f(c)=min(1/K,c/M)`, it enumerates every integer marginal gain and every
pairwise balancing exchange, verifies discrete concavity, selects the `M`
largest marginal gains, and checks that the balanced quotient-remainder
occupancy attains that independently reconstructed upper bound. It separately
reconstructs the joint witness and rechecks every row, column, maximum, and
reported fraction. Cell identity, joint feasibility/MAP score, occupancy bound,
and product formula have distinct evidence channels and verifier gates.

## Product/memoryless comparator

The comparator is a genuine `n`-fold product code with an independent payload
bit per coordinate:

```text
P(x | u) = product_t p_t(x_t | u_t),
(p_t(.|0) + p_t(.|1))/2 = Q_m  for every t.
```

No factor may depend on another payload bit or coordinate; there is no shared
latent variable or key. MAP success factorizes. The sharp v0.2 one-shot error
is

```text
e_m = 0        when m is even,
e_m = 1/(2m)   when m is odd.
```

Therefore the registered product optimum is

```text
e_product(m,n) = 1 - (1-e_m)^n.
```

The source materializes the exact tensor-product joint witness rather than
trusting this scalar formula alone. This product class is deliberately
separate from the unrestricted block class.

## Controls, metric robustness, and falsifiers

1. **`n=1` reproduction.** Every `n=1` cell must exactly reproduce v0.2.
2. **Full per-message cover.** `P(x|u)=1/M` for all `u,x` has zero payload and
   MAP error `1-1/K`.
3. **Global-only pathology.** At `m=2,n=2`, four payload words are paired into
   duplicate even- and odd-parity conditional laws. The averaged full
   transcript is uniform and every message law has uniform one-coordinate
   marginals, yet its error is `1/2`, below blind error `3/4`. This is a
   diagnostic of the weak global-only cover semantics, not an operational
   channel claim.
The metric-robustness layer is exactly five frozen probe families, separately
identified in the manifest and result:

- `P1_message_and_transcript_relabeling` (invariance): reverse both label
  axes for both witnesses in every cell; feasibility and error must persist.
- `P2_odd_alphabet_block_sensitivity` (sensitivity): at odd `m in {3,5}` the
  two classes tie at `n=1` and separate strictly at `n in {2,3}`.
- `P3_encoder_class_inclusion` (monotonicity): unrestricted error must never
  exceed product-subclass error.
- `P4_global_only_parity_pathology` (anti-gaming): the parity diagnostic must
  pass full global cover and coordinate marginals while retaining information.
- `P5_per_message_cover_blind_control` (clean control): full per-message cover
  must equal blind guessing on every cell.

The `n=1` reproduction remains a separate task gate. Import-independent replay
remains a separate measurement-reliability gate and is not counted as a metric
probe.

The primary prediction is falsified by any bound/witness mismatch. The product
prediction is falsified by any infeasible tensor witness or formula mismatch.
The control layer is falsified by any one-shot mismatch, any per-message-cover
advantage over uniform guessing, or any failure of the parity diagnostic.

Mutation tests must fail closed after changing the prior, payload count,
cover law, grid, score, product factorization, decoder information, resource
limits, conclusion layers, claim boundary, source-file list, or write-once
policy. They also reject float/NaN input, dimension mismatch, negative mass,
non-normalization, marginal-only cover checks, artifact overwrite, unexpected
live entries, shadow-module candidates, reparse points, result-layer changes,
and primary-gate tampering.

## Resources and deterministic stops

Only Python's standard library and `fractions.Fraction` are allowed. Execution
is sequential. The fixed ceilings are twelve cells, `K*M <= 1000` joint
entries per cell, `M <= 125`, at most `1008` primary DP row-state positions,
64 MiB peak traced Python allocation, 60 wall seconds, and one MiB per JSON
artifact. `tracemalloc` does not measure process RSS or native-library memory;
the result records that limitation and makes no unmeasured RAM claim.

The runner checks source/manifest binding before the first cell. It records
elapsed wall nanoseconds, traced peak Python bytes, completed-cell count, and
maximum joint, transcript, and DP state counts. It checks the resource envelope
before each cell and wall/traced-memory limits after each completed cell. On an
algorithm, wall, or traced-memory stop it retains only the completed prefix,
marks the run incomplete, and downgrades every conclusion layer. If the final
canonical payload exceeds the artifact-byte ceiling, it fails closed before
exclusive path creation and emits no artifact. Unexpected errors likewise
produce no scientific artifact. Primary and verification output paths are
opened exclusively; reruns must use a new path and may never overwrite prior
evidence.

## Five conclusion layers

The result and verification use exactly these layers:

- **Metric robustness:** registered controls and invariance checks.
- **Task result:** the finite unrestricted-versus-product comparison.
- **Measurement reliability:** exact feasibility, optimization certificate,
  source binding, and independent replay status.
- **Claim support:** only the registered uniform finite model.
- **Operational decision:** repair on any failure; otherwise retain the finite
  boundary and design a separately registered active-audit or stronger-cover
  successor.

The primary result can say only `awaiting_independent_verification` in its
measurement and operational layers, and its claim-support layer remains
`pending_independent_verification`. Only a passing import-independent verifier
may advance those layers.

## Claim boundary

This protocol concerns finite opaque-symbol probability matrices, a uniform
iid benign cover, equiprobable payload words in `{0,1}^n`, and exact globally
averaged full-transcript cover on `m=2..5`, `n=1..3`. It contains no language,
learned encoder, semantic coordination, key, decoder side information, active
auditor, prefix-conditional policy, or deployment model. It proves no
asymptotic capacity, square-root law, general tensorization theorem, or ASMP-6
resolution.
