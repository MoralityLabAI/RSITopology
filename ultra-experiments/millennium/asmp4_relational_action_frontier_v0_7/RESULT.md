# ASMP-4 relational-action frontier result v0.7

## Result

The nonunique-safe-action seam left open by v0.6 has an exact answer for a
four-mode full-reset plant.  With safe relation

~~~text
0:{a,d}, 1:{a,e}, 2:{d}, 3:{e}
~~~

and registered sensor grammar

~~~text
{{0,1},{2},{3}}  or  {{0},{1},{2},{3}},
~~~

where the choice may depend on arbitrary public read history, the complete
closed achievable region is

~~~text
r_read >= log2 3,
r_write >= 1,
theta*r_read + (1-theta)*r_write >= log2 3,
theta = log2(3/2).
~~~

Its Pareto boundary joins `(log2 3,log2 3)` to `(2,1)`.  The coordinatewise
lower corner `(log2 3,1)` is excluded, so the region is genuinely
nonrectangular.

## All-horizon certificate

For each write word `w`, let `c_w` count complete read words producing it.
The concave potential `sum_w c_w^theta` grows by at least a factor of three at
every registered node.  This yields, for every horizon and every adaptive safe
tree,

~~~text
R_T>=3^T, W_T>=2^T, R_T^theta W_T^(1-theta)>=3^T.
~~~

Public time sharing of the two local schemes attains equality and fills the
entire boundary.  The proof therefore covers history adaptation rather than
extrapolating a bounded enumeration.

## Exhaustive evidence

Central and import-independent implementations agree on all 2,800 nonempty
safe-action relations with three actions through four modes and every set
partition.  Across 24,221 feasible relation/partition cells, strict local
read/write tradeoffs occur first at four modes: exactly 72 relations and 72
partition pairs, all with signature `(3,3)->(4,2)`.

The two implementations also agree on the complete adaptive tree frontier
through horizon three.  At the last layer they independently enumerate 84,672
candidate trees, retain 1,872 undominated read-count/write-language states,
and obtain the same 20 Pareto count pairs.  Every pair satisfies the
all-horizon converse.

## Stronger registration fork

The same plant, safe-action relation, evaluator, full-reset disturbance, and
terminal-language metric now have three pairwise-distinct exact regions:

- all computed sensor partitions: `[1,infinity) x [1,infinity)`;
- the two-partition adaptive grammar: the nonrectangular wedge above; and
- forced raw sensing: `[2,infinity) x [1,infinity)`.

Only the registered sensor grammar changes.  This realizes the canonical
statement's architecture-dependent tradeoff clause while strengthening the
v0.6 conclusion that no registration-independent region is selected by the
source wording.

## Continuous and coding robustness

An exact rational embedding uses normal multiplier `3/2` and a bivariate
Lagrange polynomial whose zeros on the registered mode/control grid are
exactly the six safe pairs.  All safe-pair control derivatives are nonzero,
all six unsafe pairs leave the evaluator-safe normal set, and all 7,776 safe
paths through horizon five replay exactly.

Prefix-free worst-case coding changes each finite port budget by less than one
bit and leaves the asymptotic region unchanged.  Independent shared seeds do
not improve the zero-error region under worst-seed, seed-averaged-log, or
union-alphabet accounting.

Randomized observation kernels do not open a support-cardinality loophole
either.  Every zero-error randomized causal support tree contains a safe
deterministic subtree with no larger read or write language.  Two independent
censuses exhaust 53,108 labeled sensor supports through four labels: 994 are
zero-error feasible, including 950 genuinely randomized kernels; 4,280 sensor
selections and 3,058 controller-support kernels produce zero derandomization
failures.

## Disposition

This is an exact conditional solution of a previously explicit v0.6 nonclaim,
not a registration-independent resolution of canonical ASMP-4.  The harness
now shows a rectangle, a nonrectangle, and a second rectangle on the same
plant.  Further local enumeration cannot decide which omitted sensor registry
the canonical phrase “registered causal code” intended.

The v0.8 successor additionally shows that randomized-code feasibility depends
on whether probability is inside or outside the universal disturbance
quantifier. Its result is compatible with this package because the present
derandomization theorem explicitly assumes support-zero-error safety.
