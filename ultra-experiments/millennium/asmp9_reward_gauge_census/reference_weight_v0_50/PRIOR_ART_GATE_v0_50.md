# ASMP-9 v0.50 prior-art gate

## Verdict

**Proceed only as a finite specialization of classical parametric and robust
shortest-path optimization.**

No vertex theorem, polyhedral optimizer region, multi-scenario path
intersection, or minimax-regret construction in v0.50 is a novelty claim.

## Robust and scenario-based shortest paths

Scenario-wise absolute robustness and robust deviation/minimax regret for
shortest paths are established subjects. In particular:

- H. Aissi, C. Bazgan, and D. Vanderpooten, "Min-max and min-max regret
  versions of combinatorial optimization problems: A survey," *European
  Journal of Operational Research* 197 (2009), 427-438. DOI:
  [10.1016/j.ejor.2008.09.012](https://doi.org/10.1016/j.ejor.2008.09.012).
- G. Yu and J. Yang, "On the Robust Shortest Path Problem," *Computers &
  Operations Research* 25 (1998), 457-468. PII:
  [S0305-0548(97)00085-3](https://doi.org/10.1016/S0305-0548(97)00085-3).

The v0.50 worst-case-regret diagnostic is therefore a direct finite scenario
specialization, not a new robustness criterion.

## Multiple objectives

Multiple-objective shortest paths and efficient path sets predate this work:

- J. C. N. Climaco and E. Q. V. Martins, "A bicriterion shortest path
  algorithm," *European Journal of Operational Research* 11 (1982),
  399-404. DOI:
  [10.1016/0377-2217(82)90205-3](https://doi.org/10.1016/0377-2217(82)90205-3).
- E. Q. V. Martins, "On a multicriteria shortest path problem," *European
  Journal of Operational Research* 16 (1984), 236-245. DOI:
  [10.1016/0377-2217(84)90077-8](https://doi.org/10.1016/0377-2217(84)90077-8).

Intersecting scenario-specific tight paths is an elementary exact test inside
that established framework.

## Parametric and polyhedral optimizer regions

For fixed paths, costs are linear in the declared weights. Describing the
region where one path remains optimal by pairwise linear inequalities and
checking a polytope on its extreme points are standard linear and parametric
optimization facts.

The term "reference-weight atlas" is application-specific language for these
regions. It does not create a new polyhedral theorem.

## Buehler context

Buehler confidence limits are minimal only relative to an imposed ordering,
and their efficiency can depend on that ordering:

- R. J. Buehler, "Confidence Intervals for the Product of Two Binomial
  Parameters," *Journal of the American Statistical Association* 52 (1957),
  482-493. DOI:
  [10.1080/01621459.1957.10501404](https://doi.org/10.1080/01621459.1957.10501404).
- C. J. Lloyd and P. Kabaila, "On the Optimality and Limitations of Buehler
  Bounds," *Australian & New Zealand Journal of Statistics* 45 (2003),
  167-174. DOI:
  [10.1111/1467-842X.00272](https://doi.org/10.1111/1467-842X.00272).

Version v0.50 adds no new claim about fixed-order Buehler optimality.

## Candidate residual

The exact two-outcome, one-objective, two-reference-law witness is recorded as
a smallest control for this ASMP-9 grammar. This search did not locate that
precise Buehler specialization, but its novelty status is:

```text
candidate-new elementary control; not established novelty.
```

Its value is diagnostic: it proves that a common order at one chosen
reference mixture need not survive even the simplest declared family.

## Durable contribution

The defensible contribution is the consolidation:

1. make the reference law an explicit component of the certificate;
2. return the exact region where an evidence order stays jointly optimal;
3. distinguish singleton-reference compatibility from family robustness; and
4. provide finite margin and obstruction receipts when robustness fails.

This closes a finite sensitivity subproblem. It does not establish efficient
large-width enumeration, continuous-experiment minimax theory, strategic
response robustness, or physical preference access.
