# ASMP-3 randomized-finder amplification theorem v2.4

## Status and scope

```text
result_status = exact randomized-finder restart/noise/resource theorem
parent_result = ASMP-3-CONSTRUCTIVE-REFUTATION-PROTOCOL-v2.3
supporting_result = ASMP-3-HONEST-SEARCH-BARRIER-v2.1
interface_mode = WV-FIX
changes_parent_problem = false
```

The authoritative v0.1 ASMP-3 statement requires an efficient honest strategy,
which may be randomized. The v2.3 positive theorem instead assumes a uniform
finder that succeeds on every call. This release closes that mismatch for an
explicit randomized finder class, while charging every retry and preserving the
fresh post-selection noise rule.

It is a broader sufficient theorem. It does not derive a finder from every
positive protocol and is not the missing universal converse.

## 1. Randomized finder contract

Retain v2.3's sound-complete quotient `Refute`, registered atom encoding, and
fresh block-independent semantic noise. Replace its deterministic finder by a
uniform **Las Vegas-with-FAIL** algorithm `Find` satisfying, for every false
admissible transcript `tau`:

1. one call takes at most `H` honest-prover steps;
2. a successful return is always a valid quotient witness of size at most `r`;
3. the success probability is at least `alpha>0`;
4. failure is the explicit symbol `FAIL`; and
5. calls use independent fresh finder coins after `tau` is fixed.

The contract is uniform over adaptive and obfuscated legal advocate
transcripts. It permits no false successful witness, uncharged advice, or
preselection using semantic-noise samples.

## 2. Restart theorem

Run `k` independent finder calls and select the first success. If every call
fails, the critic declines and the advocate is accepted. The exact worst-case
finder failure bound is

```text
f_k(alpha) = (1-alpha)^k.                            (1)
```

For a target `zeta in (0,1)`, the least admissible attempt count is

```text
k_min(alpha,zeta)
  = min{k>=1 : (1-alpha)^k <= zeta}.                 (2)
```

Every attempt is charged, so honest finder time is `kH`. Finder amplification
does not multiply semantic queries or witness communication: only the selected
witness is sent and checked.

The producer certifies (2) by recording the preceding attempt, and exhaustively
enumerates all Boolean success/failure sequences for 18 small `(alpha,k)`
cells. The 378 weighted paths reproduce (1) exactly.

## 3. Composition with fresh semantic noise

After a successful witness has been selected, give each of its at most `r`
classes a fresh disjoint `d`-replica majority block. Let

```text
delta = 1-(1-e_d(eta))^r                             (3)
```

be the v1.9/v2.3 joint decoding-risk bound. Finder coins, witness selection,
and block noise occur in that order. Thus the finder success event cannot
select a favorable or unfavorable already-realized semantic-noise block.

### Theorem 1

Under these contracts, the randomized-finder protocol has

```text
completeness >= 1-delta,
soundness    <= f + (1-f)delta,
gap          >= 1-f-2delta+f*delta,                 (4)
```

where `f=(1-alpha)^k`.

### Proof

For a true transcript, soundness of `Refute` implies rejection can occur only
if at least one selected atom is decoded incorrectly. Hence acceptance is at
least `1-delta` against every critic strategy.

For a false transcript, all finder calls fail with probability at most `f`. If
at least one succeeds, its witness is valid. Conditional on that selected
witness, fresh decoding is correct with probability at least `1-delta`, and
the verifier rejects. False acceptance is therefore at most
`f+(1-f)delta`. Subtracting this value from the completeness lower bound gives
(4). QED.

If `f<=zeta` and `delta<=epsilon`, monotonicity gives the decoupled guarantee

```text
gap >= 1-zeta-2epsilon+zeta*epsilon.                 (5)
```

The deterministic v2.3 theorem is the endpoint `alpha=1`, hence `f=0` and gap
`1-2delta`.

## 4. Exact resource ledger

For `L`-bit atom IDs, the registered protocol charges

```text
honest finder time = kH,
semantic queries  = r*d,
critic message    = ceil(log2(r+1)) + r(L+1) bits.
```

The theorem applies only when `kH` fits the frozen honest-prover budget `T`.
Restarts are not free merely because they occur inside the prover.

The 72-cell registry crosses four one-shot success bounds, three refutation
sizes, three noise rates, and two paired finder/noise targets. It independently
minimizes both `k` and odd `d` and records the failed predecessor for each.

## 5. Inverse-polylogarithmic positive lane

Set `L=log2(T)`, `alpha=1/L`, `r=L`, `H=L^2`, `eta=1/5`, and both failure targets
to `1/L`. For `L=20,30,...,100`, exact minimization shows:

- finder time, queries, and message length are at most `L^4`;
- total honest finder time is below `T=2^L`; and
- gap is at least `1-3/L+1/L^2`, which tends to one.

The rows through `L=70` form the registered lane. `L=80,90,100` are emitted as
held-out confirmation rows under the same frozen formulas. This proves that an
always-successful one-shot finder is unnecessary: inverse-polylogarithmic
one-shot success suffices when the retry budget is explicitly available.

## 6. Retry obstruction for unstructured honest search

Restarting does not eliminate v2.1's search lower bound. In the unique-marker
family, a coordinated strategy using `q` new queries per attempt can cover at
most `kq` marker positions after `k` attempts. Its worst-marker success is at
most

```text
min(1,kq/N).
```

Therefore success at least `2/3` requires total work `kq>=2N/3`, even when
retries avoid all duplicate queries. The release checks six exact rows with
`N=2^n`, `q=n^3`, and `n=20,24,...,40`. Every amplified strategy exceeds the
registered one-trial budget and pays linear total search.

This is the sharp boundary: retries amplify a genuinely available randomized
finder, but cannot convert computationally inaccessible refutations into an
efficient honest strategy without paying the underlying search cost.

## 7. Remaining normal-form question

This theorem does not derive its Las Vegas-with-FAIL finder from an arbitrary
`WV-FIX` protocol. Such a converse needs a frozen operational rule connecting
protocol rejection paths to sound quotient witnesses, and must handle
interactive randomness, correlated finder failures, syntactic rejection,
variable stopping, and bounded-error strategies.

The next resolution question is whether every witness-transparent positive
protocol admits such an extractor with comparable resources, or whether an
explicit positive interface separates protocol soundness from local-witness
extraction.

## 8. Novelty boundary

Independent restart amplification and binomial majority bounds are standard.
The contribution is their typed ASMP-3 composition: per-transcript randomized
honest search, exact failure/noise gap accounting, explicit retry budget,
held-out scaling receipts, and a matching unstructured-search obstruction.
