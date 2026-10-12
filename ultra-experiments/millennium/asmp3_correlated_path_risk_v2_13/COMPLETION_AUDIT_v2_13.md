# ASMP-3 correlated path-risk completion audit v2.13

## Disposition

The correlated-noise block in the repaired online ASMP-3 theorem is resolved.
The sufficient quantity is the total error probability on the selected adaptive
path, not independence of individual oracle answers.  Persistent common-mode
noise therefore remains extractable at positive margin when `s + eta < 1`, even
though repetition cannot amplify it.

## Evidence gates

The producer and checker each require all ten gates:

1. the online extraction lower bound depends only on selected-path risk;
2. common-mode path risk is exactly `eta` for every tested query count;
3. the matching-prefix chain bound uses no independence;
4. the exchangeable Jensen bound passes exact exhaustive audit;
5. fixed marginals fail under public-seed-correlated selection;
6. the v1.8 persistent non-amplification result is preserved;
7. every v2.10 composition row has positive common-mode finder margin;
8. no common-mode amplification claim is made;
9. equal fixed marginals can induce different path risk; and
10. time, query, restart, and independence flags are explicit.

The exact audit comprises 24 common-mode rows, 20 conditional-chain rows,
18,012 exchangeable cases, 20 controller comparisons, 31 marginal-firewall
counterexamples, and 12 online compositions.  The exchangeable audit contains
7,716 registered and 10,296 held-out cases, zero Jensen violations, and 3,252
equality cases.

## Reproduction

From this directory:

```powershell
python run_correlated_path_risk.py
python verify_correlated_path_risk.py
python build_release_manifest.py
python -m pytest . -q
```

Expected focused result: producer `10/10`, clean-room verifier `10/10`, and ten
passing tests.

The release regression completed with `390 passed` across 34 ASMP-3 test files.
All 30 ASMP-3 clean-room verifier entrypoints also exited successfully.  The
pre-existing expert-review verifier correctly retained its external status at
`0/2; complete=false`; that is an explicit acceptance gate, not an internal
verification failure.

## Claim boundary

This release does not infer adaptive path control from fixed semantic-class
marginals.  Its one-query counterfamily makes the bad class depend on the public
selection seed, so each fixed-class error tends to zero as `N` grows while the
selected-path error stays one.  A usable noise definition must specify the joint
law relative to public coins or directly bound selected-path risk.

This release also leaves unchanged the broader v2.12 disposition: the literal
v0.1 iff is internally refuted, the repaired online six-clause subclass is
constructively characterized and black-box minimal, unrestricted classification
is not established, the normative definition remains unclosed, and external
acceptance remains separate.
