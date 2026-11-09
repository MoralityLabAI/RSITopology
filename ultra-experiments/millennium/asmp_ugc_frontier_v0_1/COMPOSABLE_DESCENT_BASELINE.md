# ASMP-15: compositional descent of covering labels

**2026-11-09 | exact elementary proposition.** Companion to [ASMP-13/14 sharp bounds](SHARP_VISIBILITY_AND_DECODING_BOUNDS.md) and the [candidate index](CANDIDATES.md).

Let p:G'->G be an r-sheeted graph cover, q:G''->G' an s-sheeted cover, and a'' a K-valued labeling on G''. All graph maps must satisfy the exact covering local-bijection condition and be independently validated. Use uniform counting measure on vertices throughout.

For any cover f:X->Y, define

    eta_f(a)=min_{b:V(Y)->K} |{x:a(x)!=b(f(x))}|/|V(X)|.

The minimizer is the most frequent value in each fiber, with deterministic tie breaking. Choose an optimal intermediate labeling a' for q, and an optimal base labeling b for p applied to a'. Then normalized Hamming triangle inequality, together with preservation of normalized Hamming distance under a regular finite cover, proves

    eta_{p∘q}(a'')
      <= eta_q(a'') + eta_p(a').                             (T1)

The same holds for any finite sequence of covers by iteration; the right side is the sum of the per-level defects along a chosen sequence of closest intermediate labelings. It is a conservative certificate whose strictness must be measured, and it assumes the cover degrees are uniform. For nonuniform maps, use the correct pushforward/fiber masses.

If all the covers pull back the same base connection c and the base maximum degree is D, then the existing finite incidence-counting inequality gives

    phi_G(c) <= bad_fraction_G''(a'')
              + (D |V(G)| / |E(G)|) eta_{p∘q}(a'').

Composing with (T1) yields the **certified two-step estimate**

    phi_G(c) <= bad_fraction_G''(a'')
              + (D |V(G)| / |E(G)|)
                [eta_q(a'') + eta_p(a')].                     (T2)

A cover may be flat while the base connection is frustrated, so the descent term is a genuine obligation. The bound is a standard counting and Hamming triangle argument; it should serve as the *baseline* for ASMP-15 rather than a claim of novelty.

## Adversarial certificate checks

The cover validator previously checked that every base edge has one lifted outgoing edge from each source sheet. For a valid cover, its destination sheets must also form a permutation. The seed implementation now enforces **both** conditions before using the bound. A duplicated target sheet is a reproducible malformed-certificate control that must be rejected. In a real agent setting, signed receipts and immutable lineage would still be needed to bind those mathematical maps to the actual systems.

Tests check all binary and four-label two-by-two fibers, 128 seeded two-base-vertex towers, the non-descending flat-cover witness, and a malformed target-sheet rejection.

## Remaining open frontier

The effective problem for ASMP-15 is **adaptive and noisy descent**: how to compose and attest these bounds when a monitor sees only sparse edges, changes its cover adaptively, or observes uncertain fiber correspondences. Existing ASMP-7/5 already encompass much of this problem, so the candidate stays a subproblem. A genuinely new theorem needs sharp certificates with charged observation, proof and transport cost under a declared composition grammar.

See [finite implementation](tower_descent.py) and [tests](test_tower_descent.py).
