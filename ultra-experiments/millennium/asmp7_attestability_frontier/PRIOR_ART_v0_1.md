# ASMP-7 finite attestation frontier: prior-art boundary

## Proposed contribution and disposition

The proposed result is **not** a new hypothesis-testing, randomized-response,
or property-testing theorem. Its mathematical ingredients are classical. The
surviving contribution is an application-specific, prospectively registered
instrument: one finite transformation-closed execution class in which
trace-only capability attestation is exactly impossible, while separately
charged semantic challenges admit an exact soundness/privacy/cost frontier.

Claim dispositions:

| Claim | Disposition |
|---|---|
| The count of reported-correct answers is sufficient for the frozen i.i.d. binary randomized-response channel | `classical` |
| A randomized upper-tail test is optimal for the frozen one-parameter binomial family | `classical` |
| An identical compliant/forbidden observation law forces `FP+FN >= 1` | `classical` |
| Random challenges can distinguish Boolean functions separated in Hamming accuracy | `classical` / property-testing specialization |
| The exact ASMP-7 trace-versus-charged-audit registry, receipts, and governance interpretation | `partial_extension` as an instrument, with no theorem-novelty claim |

## Search record

Search date: 2026-07-21.

Frozen search strings:

- `Warner randomized response 1965 survey technique DOI journal primary source`
- `Karlin Rubin theorem monotone likelihood ratio original paper binomial test primary source`
- `Blackwell comparison of experiments 1953 equivalent comparisons experiments primary source`
- `Neyman Pearson 1933 most efficient tests statistical hypotheses DOI primary`
- `Goldreich Goldwasser Ron property testing connection learning approximation JACM`
- `binary randomized response epsilon truth probability local differential privacy`

Sources searched: Project Euclid metadata, JASA/DOI metadata, Royal Society
metadata, ACM/JACM and author-hosted records, SIAM records, JMLR, arXiv, and
web search. Absence from this bounded search is not evidence of novelty.

## Closest work

1. Warner, “Randomized Response: A Survey Technique for Eliminating Evasive
   Answer Bias,” *JASA* 60(309), 1965,
   [doi:10.1080/01621459.1965.10480775](https://doi.org/10.1080/01621459.1965.10480775).
   This is the parent mechanism for the frozen binary truth-report channel.
2. Neyman and Pearson, “On the Problem of the Most Efficient Tests of
   Statistical Hypotheses,” 1933,
   [doi:10.1098/rsta.1933.0009](https://doi.org/10.1098/rsta.1933.0009), and
   Karlin and Rubin, “The Theory of Decision Procedures for Distributions with
   Monotone Likelihood Ratio,” *Annals of Mathematical Statistics* 27(2),
   1956, [doi:10.1214/aoms/1177728259](https://doi.org/10.1214/aoms/1177728259).
   They subsume the likelihood-ratio/upper-tail structure used here.
3. Blackwell, “Comparison of Experiments,” 1951, and “Equivalent Comparisons
   of Experiments,” 1953. Blackwell's risk ordering and garbling framework is
   the parent theory for comparing trace and charged-audit experiments. This
   seed reports only a finite Pareto frontier and does not claim a general
   Blackwell-minimal channel.
4. Goldreich, Goldwasser, and Ron, “Property Testing and Its Connection to
   Learning and Approximation,” *JACM* 45(4), 1998, pp. 653–750. Random queries
   to distinguish functions separated in Hamming distance are classical. The
   present semantic challenge is a tiny exact instance with separately gated
   false-positive and false-negative errors and a privacy channel.

## Hostile-referee reduction

A referee can correctly reduce the charged-audit computation to a binomial
test. That does not invalidate the instrument; it fixes its status. The only
ASMP-specific work is the access-class boundary:

- a finite, functionality-preserving representation monoid;
- a trace law that is physical-looking but independent of the truth table;
- a trusted challenge meter whose semantic access is explicit and charged;
- uniform composite errors over all compliant and forbidden truth tables; and
- an exact rational receipt showing which telemetry can and cannot certify the
  frozen policy.

The instrument assumes meter coverage. It does not prove that unmetered
executions are absent or that cryptographic integrity implies semantic
completeness.

## Conservative external description

“An exact finite case study applies classical randomized-response and binomial
testing theory to a transformation-closed capability-attestation registry. It
demonstrates trace-law overlap and computes the charged-audit frontier; it does
not solve ASMP-7 or establish that deployed capability is attestable.”

