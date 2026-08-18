# Prior-art audit for ASMP-4 adaptive-history collapse v0.5

## Claim discipline

The v0.5 result is an exact repository-specific diagnosis of one ASMP-4
fixture. It does **not** claim novelty for variable-length source coding,
buffer-overflow exponents, exponential code-length moments, martingale overflow
bounds, dynamic programming, or adaptive switching between prefix codes.

The narrow contribution is the combination of:

- the v0.4 four-plan synchronous no-lag control fixture;
- a complete 4,968-codebook deadline census and 13-action reduction;
- its exact common-history Bellman frontier;
- the smallest two-block witness disproving fixed-schedule completeness; and
- an explicit pathwise write guard showing that the finite ASMP Pareto
  obstruction disappears in closed asymptotic rate.

## Primary-source comparison

| Source | Classical result relevant here | Relationship to v0.5 | Claim boundary |
| --- | --- | --- | --- |
| L. L. Campbell, [*A Coding Theorem and Rényi's Entropy*](https://doi.org/10.1016/S0019-9958(65)90332-3), 1965 | Studies exponential averages of codeword length and connects their optimum to Rényi entropy. The ordinary mean and maximum length appear as limiting cases. | v0.5's exponential process `lambda^S` is another use of code-length moment structure. | Exponential length criteria and their Rényi connection are classical. |
| F. Jelinek, [*Buffer Overflow in Variable Length Coding of Fixed Rate Sources*](https://doi.org/10.1109/TIT.1968.1054147), 1968 | Develops sequential variable-length encoders/decoders for a fixed-rate link, analyzes buffer-overflow probability, and relates optimal overflow behavior to generalized entropy. | This is the closest conceptual predecessor to treating `length-2` as a buffer increment with negative drift. | Buffer banking, overflow decay, and sequential instrumentation are prior art. |
| P. A. Humblet, [*Generalization of Huffman Coding to Minimize the Probability of Buffer Overflow*](https://doi.org/10.1109/TIT.1981.1056322), 1981 | Gives a prefix-code algorithm minimizing a moment-generating function of codeword length and uses it to optimize overflow decay. | v0.5 uses a fixed Huffman/balanced pair rather than claiming a new overflow-optimal code. | Moment-generating-function and overflow-exponent code design are classical. |
| F. Jelinek and K. S. Schneider, [*On Variable-Length-to-Block Coding*](https://doi.org/10.1109/TIT.1972.1054899), 1972 | Relates fixed-rate transmission, exponentially decaying overflow probability, memoryless sources, and Rényi-type exponents. | Supports the interpretation of sublinear slack and exponential hit bounds as a coding/buffering phenomenon rather than a new control resource. | Variable-to-fixed overflow exponents are prior art. |
| R. Nomura, [*Overflow Probability of Variable-Length Codes with Codeword Cost*](https://arxiv.org/abs/1310.2001), 2013 | Gives first- and second-order overflow thresholds for general sources with unequal code-symbol costs. | Reinforces that expected cost, tail cost, and worst threshold are distinct registered objectives. | General overflow-threshold theory is not claimed here. |
| A. Ehrenfeucht and J. Mycielski, [*Positional Strategies for Mean Payoff Games*](https://doi.org/10.1007/BF01768705), 1979 | Establishes positional optimal strategies for finite perfect-information mean-payoff games. | The variable-support write threshold is encoded as such a game after the coder chooses a prefix tree and the worst-history player chooses an enabled plan. | Positional determinacy is classical; the repository claim is only its ASMP-4 prefix-code instantiation and guard coupling. |

The v0.4 audit separately covers zero-delay causal source coding, cascade
coding, invariance entropy, and timing channels. Those sources remain relevant
and are not duplicated here.

## Exact difference from classical overflow formulations

The v0.5 guard never permits a write-budget violation or erases a symbol. It
uses the balanced identity relay after a public history-dependent threshold,
so every plan history is safe and has write total at most `2n+k`. The rare
event is not a safety failure; it only triggers a higher expected-read mode.
This converts a classical overflow-style exponential bound into a mixed
expected-read/worst-write ASMP certificate.

That distinction explains the repository result, but it is not evidence of a
new general source-coding theorem. A literature-level novelty claim would
require a much broader search and expert review.

## Audit conclusion

The safe statement is:

> Classical variable-length coding and overflow theory supply the qualitative
> mechanism. v0.5 gives an exact, independently verified instantiation showing
> that common-history block adaptation restores the lower corner in the
> registered ASMP-4 prefix-control fixture and throughout its four-plan
> probability phase. The finite-alphabet and public-predictor extensions are
> direct guarded-buffer corollaries. Positional mean-payoff determinacy supplies
> the variable-support write baseline. None is presented as a new general
> source-coding or game-theoretic principle.

The package should not use phrases such as "new overflow theorem," "novel
martingale code," or "first adaptive Huffman guard."
