# ASMP-3 protocol-quantifier fork theorem v0.7

## Theorem

For the complete oracle-relative game family in
`FROZEN_GAME_SPECIFICATION_v0_7.md`, let `n` be the formal payload scale,
`N=n+O(log n log log n)` the total input length,
`d=floor(log2 n)`, and let the persistent semantic error rate be `1/5`.

### A. Frozen-encoding reading

If admissible transcript encodings are frozen game data as in `G_fix`, then:

1. `r_R(N)=d=Theta(log T(N))`;
2. one uniform `Theta(T(N))` honest strategy finds a refutation against every
   realized efficient dishonest strategy;
3. `a_H(k)<=1/5` for every `k>=1`; but
4. the exact optimal completeness/soundness gap is

   ```text
   (3/5)^d -> 0.
   ```

Therefore the displayed sufficiency direction of the v0.1 Weak-Verifier
Characterization Conjecture is false under the frozen-encoding reading.

### B. Existential-encoding reading

If “admits a protocol” allows the protocol to add the canonical per-atom vector
messages of `G_admit`, then the same task relation, semantic worlds, oracle law,
prover budget, and verifier resource scale admit a protocol with:

```text
message cost = O(d),
semantic queries = 1,
completeness = 4/5,
soundness = 1/5,
gap = 3/5.
```

Therefore the parity family is not a counterexample under the
existential-encoding reading.

## Proof

### Refutation dimension

For a syntactically valid false XOR output, exactly one component claim is
false. A formal falsehood is localized without semantic atoms. A semantic
falsehood is refuted by the complete `d`-atom set. If the task output is correct
but both component claims are false, the formal falsehood again supplies an
empty-`S` refutation.

If any semantic index is omitted, two ideal completions differing only at that
index have opposite parities. Hence no strict subset refutes a parity claim.
Thus the maximum minimum is exactly `d`.

### Uniform honest strategy

The honest advocate computes the full formal XOR tree and semantic parity.
Malformed or aborted messages lose. A differing formal root is bisected: local
XOR consistency plus a parent disagreement forces exactly one child
disagreement, so after `d` rounds a false public leaf claim is exposed. If
formal roots agree, an opposite task output has the opposite semantic parity,
and the fixed complete semantic set refutes it.

This reasoning is pointwise in every realized move sequence, so randomization
and adaptivity by the dishonest advocate do not create another case.

### Frozen-encoding lower bound

Fix the public instance and common formal transcript. Label advocates by
semantic claim rather than honest role. Under the uniform even- and odd-parity
priors, every non-oracle transcript byte is identical.

Let `Y=z XOR E`. Any adaptive sequence of persistent queries, public coins, and
stopping decisions is a Markov kernel of `Y`, so total variation cannot
increase. For `rho=1-2/5=3/5`,

```text
P_h(Y=y)
  = 2^(-d) [1 + (-1)^(h+parity(y)) rho^d].
```

Therefore

```text
TV(P_0,P_1) = rho^d = (3/5)^d.
```

A pointwise completeness/soundness gap survives averaging over the two priors,
so it is at most this total variation. Observed parity attains the bound for
every ideal vector.

### Extended protocol

Honest `P_h` sends `z`. Any vector with opposite parity differs from `z` in at
least one coordinate. Querying a canonical differing coordinate returns the
honest bit with probability `4/5` and the dishonest bit with probability `1/5`.
The gap is `3/5`, with `O(d)` messages and verifier work.

## Canonical interpretation consequence

The v0.1 text contains both:

- an instruction to freeze message order, stopping, and admissible transcript
  encodings as part of the game; and
- the phrase “a task family admits ... a protocol.”

The theorem shows that choosing which phrase controls the semantic message
alphabet changes the truth value of the parity counterexample. The remaining
scope question is therefore textual/normative, not probabilistic and not
resolvable by extending the parity grid.

## Claim boundary

This theorem settles the earlier witness's complete-game and quantifier-fork
obligations. It does not by itself adjudicate authorial intent, prove that the
full ASMP-3 characterization program is impossible, or count as either required
external expert reproduction.
