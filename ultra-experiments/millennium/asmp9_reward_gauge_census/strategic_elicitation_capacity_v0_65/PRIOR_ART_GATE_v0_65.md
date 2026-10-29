# ASMP-9 strategic elicitation prior-art gate v0.65

## Verdict

The outcome-menu reduction and incentive-compatibility constraints are
classical.  More importantly, the positive random-pair escape from the
deterministic capacity bound is already explicit in Azrieli, Chambers, and
Healy (2021).  Version v0.65 may record a precise ASMP-9 specialization and
its finite capacity, support, margin, and commitment-timing ledger, but it may
not claim a new revelation principle, random-problem-selection mechanism,
strategyproofness theorem, or mechanism-with-verification result.

## Primary anchors

### Random problem selection

Yaron Azrieli, Christopher P. Chambers, and Paul J. Healy, "Constrained
Preference Elicitation," *Theoretical Economics* 16 (2021), 507-538:

<https://econtheory.org/ojs/index.php/te/article/viewFile/20210507/30637/874>

This is the load-bearing parent result for the randomized branch.  It
characterizes elicitation by random problem selection.  Its footnote 12
already gives the mechanism used here: the agent reports a complete ranking,
a pair is selected randomly, and the outcome reported higher in that pair is
awarded.  Version v0.65 therefore claims no novelty for that construction or
for the general random-problem-selection characterization.

### Revelation and strategic implementation

Roger B. Myerson, "Incentive Compatibility and the Bargaining Problem,"
*Econometrica* 47(1), 1979, 61-73:

<https://ideas.repec.org/a/ecm/emetrp/v47y1979i1p61-73.html>

The revelation principle makes direct incentive constraints the standard
language for strategically elicited private information.  The v0.65
interactive-to-complete-strategy reduction is below this theory.

### Manipulability of rich outcome rules

Allan Gibbard, "Manipulation of Voting Schemes: A General Result,"
*Econometrica* 41(4), 1973, 587-601:

<https://www.eecs.harvard.edu/cs286r/courses/fall11/papers/Gibbard73.pdf>

Gibbard's theorem concerns multi-person voting/game forms over unrestricted
preferences.  Version v0.65 does not invoke it as its proof.  It studies the
strict identifiability capacity of a single-agent deterministic outcome menu,
a much smaller statement.

### Menu and communication complexity

Shahar Dobzinski, "Computational Efficiency Requires Simple Taxation,"
FOCS 2016 / arXiv:1604.01971:

<https://arxiv.org/abs/1604.01971>

The taxation/menu principle and its communication-complexity refinements
already formalize how truthful mechanisms expose a menu from which an agent
selects a preferred outcome.  The v0.65 capacity formula is a no-payment,
single-agent, finite ordinal endpoint of that perspective.

### Verification changes the feasible mechanism class

Carmine Ventre, "Truthful optimization using mechanisms with verification,"
*Theoretical Computer Science* 518 (2014), 64-79:

<https://doi.org/10.1016/j.tcs.2013.07.034>

These positive results illustrate why verification must be treated as a new
access primitive rather than silently folded into an outcome-only mechanism.

### Strict elicitation can require calibrated proxy consequences

Elias Tsakas, "Belief Identification by Proxy," *Review of Economic Studies*
93(1), 2026, 697-724:

<https://academic.oup.com/restud/article/93/1/697/8114609>

This work explicitly uses strictly incentive-compatible elicitation with
proxy-contingent consequences.  It is a positive comparator outside v0.65's
no-transfer, no-proxy grammar.

## Admissible residual

The only durable contribution authorized here is an ASMP-9 access ledger:

```text
deterministic outcome-only elicitation
  -> finite outcome-menu capacity;

commitment followed by random problem selection
  -> classical full-ranking elicitation with a full-support requirement;

payments, audits, verified consequences, or changing targets
  -> enlarged access class requiring a separate theorem.
```

The residual finite specialization consists of:

- the exact deterministic capacity formula;
- the adjacent-swap proof that every outcome pair needs positive sampling
  probability in the full strict-ranking domain;
- the normalized worst-case incentive margin and its uniform maximin design;
  and
- the commitment-timing contrast between reporting before and after the
  random pair is revealed.

These calculations are useful because they prevent either an interactive
transcript or an unsealed randomized challenge from being mistaken for
identified value information.  They are not asserted to be new mechanism
design.

## Claim boundary

Version v0.65 does not establish a new mechanism-design theorem, cover
multiple agents, transfers, subjective-randomization failures, Bayesian
implementation, approximate incentives, bounded rationality, audits, dynamic
preferences, or physical human/model behavior.  It does not resolve ASMP-9.
