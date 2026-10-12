# ASMP-3 adaptive transcript-coupling theorem v2.7

## Status and scope

```text
result_status = pathwise adaptive-protocol coupling and robustification theorem
parent_result = ASMP-3-WITNESS-TRANSPARENT-NORMAL-FORM-v2.5
supporting_results = ASMP-3-BLOCK-SELECTION-COMPOSITION-v1.9, ASMP-3-RESOLUTION-DISPOSITION-v2.6
interface_mode = WV-FIX with fresh post-history conditional replication blocks
changes_parent_problem = false
```

The v2.5 normal form assumed a coupling between the noisy and ideal terminal
decisions. This theorem derives that coupling for arbitrary adaptive semantic
query trees under the registered fresh-block noise class. It is a genuinely
broader theorem permitted by v2.6's stopping rule, not an extension of the old
finite grids.

## 1. Adaptive protocol model

Fix all public/private nonsemantic coins and every prover/verifier strategy
kernel. Conditional on those coins, the interaction is deterministic as a
function of its observed history. At each of at most `q` semantic decision
points, the complete current history determines:

- every prover message;
- the next quotient semantic class to query;
- whether to stop; and
- the terminal decision if stopping occurs.

Only after the next class is fixed, draw a fresh disjoint `d`-replica block.
Decode it by majority. Conditional on every matching prefix, the decoded block
has error probability at most `e=e_d(eta)` and is independent of earlier block
errors.

The ideal execution uses the same nonsemantic coins and strategy kernels but
feeds the exact ideal semantic answer at every query.

## 2. Pathwise coupling theorem

### Theorem 1

There is a coupling of the ideal and noisy executions such that

```text
Pr[the terminal histories or decisions differ]
  <= delta_q(d,eta)
  = 1-(1-e_d(eta))^q.                              (1)
```

The same bound covers adaptive query choice, prover messages depending on
public decoded answers, repeated classes, private/public randomized strategies,
and variable stopping.

### Proof

Share every nonsemantic coin between the executions. Induct on semantic query
rounds. If all earlier decoded answers equal their ideal answers, the complete
histories are identical. Therefore every strategy kernel produces the same
messages, the verifier selects the same next class, and both executions either
stop together or continue together.

At a continuing round, the fresh decoded block is correct with conditional
probability at least `1-e`. Thus the probability of `q` matching decoded
prefixes is at least `(1-e)^q`; early stopping only increases it. On that event
the entire histories and terminal decisions are identical. Taking the
complement proves (1). QED.

Conditional independence makes (1) exact for the registered constant-error
lane. With only a per-history conditional error bound, the same product lower
bound follows by the chain rule. A union-safe fallback is `q e`.

## 3. Adaptive robustification

Suppose the ideal protocol has completeness `c`, soundness `s`, and gap
`g=c-s`. Decision coupling gives

```text
c_noisy >= c-delta,
s_noisy <= s+delta,
g_noisy >= g-2delta.                               (2)
```

Choose the least odd `d` satisfying (1) for the target `delta`. The raw semantic
query charge is exactly

```text
q*d.                                                (3)
```

The release minimizes `d` for 42 `(q,eta,target)` combinations and records the
preceding odd depth as a failed certificate. For the example ideal gap `3/5`,
every target-`1/100` row retains gap at least `29/50`.

## 4. Derived v2.5 extraction margin

For a witness-transparent protocol whose noisy false-acceptance probability is
at most `s`, v2.5 extracts a finder with success

```text
alpha >= 1-s-delta.                                (4)
```

Equation (1) now supplies `delta`; it is no longer a separate coupling premise.
The release composes twelve exact operating points. Witness transparency and
efficient ideal simulation remain necessary contracts.

## 5. Exhaustive adaptive-tree audit

The finite audit enumerates every deterministic binary-history query policy and
every history-dependent stopping policy of depth at most three over two atom
IDs:

```text
128 query policies
128 stopping policies
4 semantic worlds
8 decoded-error patterns
= 524,288 coupled executions.
```

In every no-error case the complete path and stopping decision agree. No path
diverges without at least one decoded error. Conditioning on shared randomized
strategy coins reduces arbitrary randomized policies to these deterministic
pathwise kernels; adversarial message effects are absorbed into the arbitrary
history-to-action policy.

Thirty independently weighted error-pattern spaces reproduce (1). Thirty-six
tightness rows query fresh all-zero atoms and decide one exactly when the
observed history is nonzero, so decision mismatch occurs iff some decoded block
fails. Hence (1) cannot be improved for the declared class.

## 6. Selection and noise firewall

Freshness occurs after the current history fixes the next query. If candidate
blocks are pre-sampled, inspected, or selected after their errors are visible,
the v1.9 selection-risk theorem applies instead. Persistent latent flips,
globally correlated errors, and the truth-aware adaptive budget class of v1.4
do not satisfy this theorem's block contract.

The theorem also does not create witness transparency. A rejecting protocol
that does not expose a binding ideal `Refute` witness remains outside the v2.5
normal form.

## 7. Resolution effect

This result removes one of v2.6's identified subclass premises: the
ideal/noisy coupling margin is now constructive for the fresh conditional block
class, including fully adaptive histories. It does not settle the normative
FIX/ADM choice, protocols without rejection witnesses, universal interactive
lower bounds, other correlated-noise classes, or external review.

## 8. Novelty boundary

Synchronous coupling and sequential union/product bounds are standard. The
contribution is their typed ASMP-3 normal-form use: arbitrary adaptive strategic
histories, variable stopping, exact replication costs, a clean selection
firewall, exhaustive decision-tree receipts, and direct composition into the
protocol-to-finder converse.
