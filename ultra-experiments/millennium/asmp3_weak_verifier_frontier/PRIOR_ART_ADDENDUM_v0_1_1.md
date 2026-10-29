# ASMP-3 prior-art addendum v0.1.1

This additive note leaves the sealed v0.1 prior-art record unchanged and closes
two omissions identified after the exact run.

## Obfuscated arguments and selected blind spots

Barnes and Christiano's 2020
[obfuscated-arguments report](https://www.lesswrong.com/posts/PJLABqQ962hZEqhdB/debate-update-obfuscated-arguments-problem/)
studies large arguments containing rare fatal errors that an honest debater may
be unable to locate. *Scalable AI Safety via Doubly-Efficient Debate*
([arXiv:2311.14125](https://arxiv.org/abs/2311.14125)) identifies verifier
oracles that err on arbitrary or randomly selected query subsets as an open
direction.

The v0.1 atom-targeted construction is structurally adjacent but not identical.
It assumes an honest challenger has already located the decisive atom. The
failure occurs one stage later: the semantic verifier is systematically wrong
on the atom selected for adjudication. Thus the two problems are:

1. **localization failure:** the rare flaw cannot be found; and
2. **selected-adjudication failure:** the flaw is found, but the verifier's
   aggregate accuracy does not control its error on that selected atom.

The v0.1 result proves only the second failure in a finite synthetic model. It
does not solve or instantiate the computational localization problem in the
Barnes–Christiano construction.

## Correlated Condorcet jury theorems

The qualitative correlation result predates modern verifier ensembles:

- Boland, *Majority Systems and the Condorcet Jury Theorem* (1989),
  [DOI:10.2307/2348873](https://doi.org/10.2307/2348873), treats majority
  systems under heterogeneous competence and dependent decisions.
- Ladha, *The Condorcet Jury Theorem, Free Speech, and Correlated Votes*
  (1992), [DOI:10.2307/2111584](https://doi.org/10.2307/2111584), generalizes
  the jury theorem to correlated votes.
- Ladha, *Information Pooling through Majority-Rule Voting: Condorcet's Jury
  Theorem with Correlated Votes* (1995),
  [DOI:10.1016/0167-2681(94)00068-P](https://doi.org/10.1016/0167-2681(94)00068-P),
  analyzes correlated-voting models including Pólya-type dependence and shows
  that correlation can reduce majority effectiveness.

Accordingly, v0.1 does **not** claim novelty for the direction “positive
correlation weakens majority amplification” or “decorrelation helps.” Its
finite contribution is narrower:

- exact rational FP and FN at the registered `(q,rho,mu)` cells;
- a fixed-call-budget comparison between one, three, and nine stipulated
  independent verifier families;
- an operational 5% decision boundary; and
- the atom-average versus selected-atom counterexample.

Independence between families is an assumption of the registered model, not an
empirical finding about real verifier diversity.

