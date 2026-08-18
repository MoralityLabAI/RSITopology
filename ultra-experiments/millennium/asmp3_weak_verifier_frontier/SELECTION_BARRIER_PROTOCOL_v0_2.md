# ASMP-3 selected-atom calibration barrier v0.2

## Question

Can aggregate calibration over a large semantic-atom registry support uniform
soundness when a dishonest prover can select a false transcript whose unique
refutation lies on a verifier blind spot?

This exact harness addresses the selection step omitted by the v0.1
correlated-noise frontier. It does not model natural-language semantics or claim
a lower bound for every interactive protocol.

## Frozen finite game

There are `N` genuinely local binary semantic atoms. For each atom `j`, the
legal error family contains an oracle that is deterministically wrong on `j`
and correct on all other atoms. Its atom-averaged error is `1/N`.

Before adjudication, the verifier calibrates at most `m` distinct atoms. A
dishonest prover knows the oracle's blind atom and can submit a false transcript
whose unique local refutation is that atom. An honest challenger can identify
and name the refuting atom, so the construction isolates selected-adjudication
failure rather than localization failure. Repeating the semantic judgment on
the same atom returns the same wrong answer.

Two calibration regimes are separated:

1. A deterministic calibration set known to the adversary.
2. An optimally randomized set of at most `m` distinct atoms, with the blind
   atom fixed before the public calibration coins.

For the randomized regime, the sharp minimax false-accept probability is

```text
V(N,m) = (N-m)/N.
```

The lower bound follows because the sum of the `N` atom-inclusion
probabilities is at most `m`, so some atom is included with probability at most
`m/N`. Uniform sampling of a size-`m` subset attains equality for every atom.
Consequently, `V(N,m) <= epsilon` requires

```text
m >= ceil((1-epsilon) N).
```

For deterministic calibration, any `m<N` leaves an atom the adversary can
select, so worst-case false acceptance is one.

## Exact checks

- Brute-force every blind/calibration subset pair for all universes through
  `N=9` and compare with the hypergeometric miss formula.
- Check the one-blind-spot minimax identity for every `N<=32` and every
  `m<=N`.
- Evaluate `N={64,256,1024,4096}` at the round-robin comparator budget
  `m=2 ceil(log2 N)+12`.
- Require a false-accept ceiling of `1/20`.
- Verify that odd majority budgets `q={1,3,5,7,9}` retain unit false acceptance
  once the selected atom is a deterministic blind spot.

## Claim boundary and stop rule

This is a lower bound for calibration-only coverage of an unstructured atom
registry. It does not rule out protocols that prove a structural per-atom error
guarantee, cryptographically randomize a refutation after prover commitment,
restrict which refutations a prover can select, or use a semantic oracle class
without selectable blind spots.

If the exact checks pass, do not scale the existing aggregate
majority/correlation grid as an attempted ASMP-3 resolution. A meaningful
successor must add and justify one of those structural ingredients or move to a
formal asymptotic protocol theorem.
