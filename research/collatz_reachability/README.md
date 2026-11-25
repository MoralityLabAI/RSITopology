# Collatz quotient obstructions and edit-sensitive certificates

This finite arithmetic control exercises a recurring question in the
repository's identity and edit work: which target claims follow from a
preserved label? The implementation separates a useful obstruction from the
unresolved cases, then audits an edit that preserves the label while changing
reachability.

All computations use small exact integer graphs. The connection to the
repository's model-edit program is an experimental design pattern. No spectral
bundle, neural model, reward optimizer, or physical edit is evaluated here.
This package leaves the existing lineage and holonomy authorization rules
unchanged.

## Arithmetic system

For positive `d = 1 mod 4`, the accelerated odd transition is

\[
T_d(n)=\frac{a(n)n+d}{2^{v_2(a(n)n+d)}},\qquad
a(n)=3\text{ if }n\equiv1\pmod4,\quad a(n)=1\text{ otherwise}.
\]

The odd integers at most `d` form a closed core. When `gcd(d,6)=1`, define
`q(n)` to be the least residue in the orbit of `n mod d` under multiplication
by 2 and 3. These multipliers are permutations, so the orbit also contains
their inverses. The transition formula gives `q(T_d(n))=q(n)`.

Consequently, `q(source) != q(target)` certifies that the original dynamics
cannot reach the target. Equality leaves a directed reachability question.
An explicit orbit provides the exact answer in these finite fixtures.

## Executed audit

The parameter set is `13,29,73,97,217,313,577,1001`. Every ordered pair of odd
core states is audited, including the zero-step path from each state to itself.

| Quantity | Count |
|---|---:|
| States across the eight graphs | 1,164 |
| Ordered source-target pairs | 375,096 |
| Reachable pairs | 17,770 |
| Different-quotient obstructions | 266,952 |
| False obstructions | 0 |
| Unreachable pairs sharing a quotient | 90,374 |
| Same-quotient pairs in different eventual basins | 7,334 |
| Pairs certified unreachable by a closed set | 357,326 |

These values are exact counts on the enumerated graphs. The eight parameters
were selected as development fixtures and remain fully exposed. Repeated
pairs and states provide no independent evidence about a trained monitor.

The audit records every parameter's denominators in `receipt.json`. For
example, `d=73` has one eventual cycle per quotient, yet 401 unreachable
ordered pairs share a quotient. Directed reachability also depends on where
a state lies along a transient path. Basin identity alone loses that detail.

## A certificate with an explicit action set

An unreachability certificate contains a finite set `C`, a source and a
target. Verification checks:

- the source belongs to `C` and the target lies outside it;
- all members are valid odd core states;
- every allowed successor of every member stays in `C`.

Induction on path length then keeps every reachable state in `C`. The
verifier evaluates integer transition equations independently of the census's
basin labels. It also checks every supplied extra edit edge.

For this deterministic finite system, the complete forward orbit of a source
is closed. It certifies every unreachable target, which explains the exact
count of 357,326. Exhaustive tests exercise the full verifier on all pairs for
`d=1,5,13,29,49,73`; the larger census checks each source's closure once and
counts target exclusions. A certificate can have size proportional to the
core, so this is a completeness result for the finite control rather than a
compression claim.

## An invariant-preserving edit defeats a basin proxy

At `d=13`, the odd cycles include `[1]` and `[5,7]`. Their residues share the
same multiplicative orbit. The set `{1}` proves that source 1 cannot reach
target 5 under the original law.

Now add the permitted edge `1 -> 5`. This edge preserves `q`. It immediately
makes the target reachable and invalidates the old closed-set certificate.
`verify_certificate(proof, ((1,5),))` rejects it. An unrelated edge `5 -> 7`
leaves that certificate valid because its source lies outside `{1}`.

This supplies a compact test case for a monitor that confuses invariant
agreement with target attainment. A proxy rewarding agreement with the
target's quotient already awards source 1 full credit, despite the original
dynamics keeping it on a different cycle. Rechecking the allowed transition
set resolves the edit case.

For a general controlled system, the proof applies when closure is checked
under **every** allowed action. Checking only the currently observed action
sequence leaves other routes unaudited. An update to the action set therefore
requires new verification against that set.

## Reproduce

```sh
python research/collatz_reachability/reachability.py --check
python -m unittest discover -s research/collatz_reachability -p 'test_*.py' -v
```

Python 3.11 or newer and the standard library suffice. The committed workflow
replays the deterministic receipt and checks forged membership, repeated
members, missing successors, wrong source/target, invalid parameters, and the
extra-edge witness. A vendored MathCan oracle is bound by SHA-256 in the
receipt. No paid compute is required, and the graphs stay within the
repository's permitted unit-scale controls.

## Transfer experiment

Use the alias witness as a synthetic negative control before proposing a
label-based model-edit gate. Preserve the label while changing a registered
target property; require the gate to report the unresolved claim. Compare a
label-only predictor with a verifier that checks a declared action set, then
measure certificate cost and selective coverage. Real model tests need their
own independent units, matched edit controls and outcome access contract.

Evidence card: unit = one finite arithmetic graph; `n_units=8` selected
parameters; `n_cases=375096` exhaustive ordered pairs; primary check =
soundness of a quotient obstruction; dose = one added directed edge in the
minimal witness; comparisons = quotient obstruction, exact reachability and
closed-set certificate; numerical resolution = exact integers; readout
exposure = fully inspected development fixtures; verdict = exact finite-domain
control. Scientific effect and sham floors for neural transfer remain unset.
