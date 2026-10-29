# Support-incidence quotient theorem v0.21

## Registered quotient

Let a finite support-zero-error sensor transducer have hidden states `S`, modes
`z`, active raw outputs `Y`, and event support `E(s,z) subseteq Y x S`. For an
active output `y`, define its full support-incidence signature

`sigma(y)={(s,z,s_next):(y,s_next) in E(s,z)}`.

Inactive declared symbols are omitted. Identify two active symbols exactly
when

`y ~ y' iff sigma(y)=sigma(y')`.

The quotient output is the signature class itself. The event
`(y,s_next) in E(s,z)` becomes `([y],s_next)`.

## Exact-support theorem

The signature quotient has the following properties.

1. **Full support preservation.** Given the signature classes, the original
   event-support relation is recovered up to duplicating or renaming raw labels
   with the same signature.
2. **Coarsest exact quotient.** Any quotient that merges two distinct
   signatures loses at least one event in their symmetric difference and
   cannot reconstruct both active incidence classes. Thus this is the coarsest
   quotient preserving the declared exact-support object.
3. **Feasibility preservation.** Equal signatures give identical current `q`
   witnesses and identical successor sets from every belief. Merging them
   neither creates nor removes a mixed reachable transition.
4. **Renaming invariance.** A bijective raw-label change leaves the set of
   signatures and the quotient observer unchanged.
5. **Duplicate-clone invariance.** The v0.20 `m` colors of a base symbol all
   have one signature. Every clone factor therefore produces the same quotient
   observer, language, and spectral radius.
6. **Idempotence.** Every active quotient symbol has a distinct signature, so
   applying the quotient again changes nothing.

This is exact canonicality for support-incidence preservation. It is not a
claim that retaining the full support relation is necessary for control.

## Semantic read rate

Let `A_sem` be the output-multiplicity adjacency matrix of the reachable
subset observer after quotienting, and let

`L_T_sem=e_I^T A_sem^T 1`.

Under the declared quotient-first charging rule, exact inner-collar counts are

- semantic reads: `L_T_sem ceil(rho*2^T)`;
- writes: `2^T ceil(rho*2^T)`.

Every feasible quotient experiment has region

`[1+log2(rho(A_sem)),infinity) x [2,infinity)`.

The formula follows from v0.18/v0.19 after replacing raw labels by their
registered signature classes. Feasibility and writes are unchanged.

## Separating fixtures

- The computed and golden transducers are already signature-reduced, so their
  semantic languages remain `2^T` and `2^T F_(T+2)`.
- A memoryless four-output duplicate fixture has two low labels with the same
  signature and two high labels with the same signature. Raw language is
  `4^T`; semantic language is `2^T`.
- An infeasible two-output overlap fixture collapses to one semantic class and
  remains infeasible.
- Cloning the first three fixtures by every factor `m=1,...,8` leaves their
  semantic observers exactly unchanged.

## Complete memoryless census

Revisit the v0.17 census in which each of four modes has a nonempty support
over `s=1,2,3,4` declared outputs. The central implementation enumerates all

`sum_(s=1)^4 (2^s-1)^4 = 53,108`

row-support relations. An independent implementation instead enumerates each
output column from the seven feasible signatures

`0, {low mode 1}, {low mode 2}, {both low}, {high mode 1}, {high mode 2}, {both high}`

and retains column sequences that cover all four mode rows.

Both derivations recover 724 feasible relations. Their joint histogram
`(raw active outputs, semantic classes)` is

- `(2,2):20`;
- `(3,2):30`, `(3,3):180`;
- `(4,2):14`, `(4,3):216`, `(4,4):264`.

Thus 260 feasible relations contain duplicate support signatures. The raw
active histogram `20,210,494` becomes semantic-class histogram `64,396,264`
for class counts `2,3,4`.

For a memoryless feasible quotient with `k` semantic classes, every semantic
word is possible, so exact reads are `k^T ceil(rho*2^T)` and the region is
`[1+log2(k),infinity) x [2,infinity)`.

## Deterministic embedding

All 104 labeled feasible deterministic relations are already
signature-reduced: distinct active output labels are supported by disjoint
nonempty mode sets. The quotient therefore removes no deterministic labels and
leaves the four v0.16 unlabeled partitions unchanged.

## Relation to the v0.20 stop

V0.21 executes one explicit resume route from the v0.20 stop certificate. Once
exact support incidence is declared to be the semantic object, irrelevant raw
clones are coordinate artifacts and their entropy disappears. The stop still
applies to any claim that this quotient was forced by the original source or
that a plant-only forced-raw value is canonical without a declared rule.

## Scope

The quotient is canonical only within the class of exact-support-preserving
maps. It can retain distinctions that a control-minimal statistic could safely
discard; the golden fixture already illustrates that possibility. This result
does not solve minimal causal sufficient-statistic coding, choose the source's
global semantics, handle continuous observations, or prove the nonlinear
coordinate-invariant ASMP-4 variational theorem.
