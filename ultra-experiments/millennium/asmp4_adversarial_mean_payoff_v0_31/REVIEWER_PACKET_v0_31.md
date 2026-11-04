# Reviewer packet v0.31

## Claim under review

For finite public turn-based games with nonnegative rational read/write edge
costs and arbitrary controller memory,

`R = intersection_tau union_C upward(conv(cycle means in C of G_tau))`,

where `tau` ranges over memoryless adversary policies and `C` over reachable
cyclic SCCs after fixing `tau`.

## Fast review path

1. Check the sign identity in `THEOREM.md`:
   `liminf average(R-c)=R-limsup average(c)`.
2. Check that the cited classical theorem really supplies memoryless spoilers
   for conjunctive mean-payoff-`inf` objectives.
3. Check the one-player SCC multicycle equivalence and the order
   `intersection_tau union_C`; neither quantifier may be swapped.
4. Run the central and independent commands in `README.md`.
5. Inspect the connector fixture: `(1,1)` is in the cycle hull, no single cycle
   attains it, and every finite period has positive slack `1/(k+1)`.

## Strongest falsification targets

- Find a losing budget with no memoryless adversary spoiler.
- Find a fixed-policy one-player win whose reachable SCC cycle hull misses the
  lower budget orthant, or the converse.
- Show that a global convex hull across irreversible SCCs is operationally
  achievable; the controller fork is the counterboundary.
- Produce a finite-memory realizer of the exact connector boundary `(1,1)`;
  the ultimately periodic cycle argument rules it out.
- Replace cost `limsup` by cost `liminf`; the burst fixture separates them.

## Integrity and independence

Both implementations seal the canonical source, v0.25 claim, and v0.26 claim.
The independent verifier has separate reachability, SCC, cycle, segment
feasibility, census, and fixture code; an AST audit rejects an import of the
central module.

## Scope warning

This packet begins after a finite exact public quotient has been supplied. It
does not establish that an arbitrary nonlinear or continuous-belief plant has
such a quotient.
