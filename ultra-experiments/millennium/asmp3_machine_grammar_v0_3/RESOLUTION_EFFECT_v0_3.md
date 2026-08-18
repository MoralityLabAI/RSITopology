# ASMP-3 machine-grammar resolution effect v0.3

## Before this package

V2.21 proved that the full standard-encoded membership set is undecidable under
every adequate effective encoding, across strict FIX and semantic-respecting
ADM. The remaining objection was institutional: v0.1 did not name literal
bytes, parser behavior, program costs, information ports, or an interface
catalog grammar.

## After adopting ASMP-3-MACHINE-v0.3

The successor decision set has one exact input language and one exact
membership predicate. The reference compiler produces valid canonical bytes
for every `U_TM_v1` machine index in both modes. Therefore the v2.21 mapping is
a literal computable many-one reduction:

```text
NONHALT <=m WV-MEMBERSHIP-v0.3(FIX)
NONHALT <=m WV-MEMBERSHIP-v0.3(ADM)
```

The successor's unrestricted uniform membership set is consequently
undecidable and its positive index set is not recursively enumerable.

This is a negative resolution of the machine-defined successor membership
question. It does not erase the exact positive finite/subclass theorems and it
does not say weak verification is universally impossible.

## Parent relationship

```text
v0.1 silently amended = no
new successor defined = ASMP-3-MACHINE-v0.3
v2.21 reduction retained = yes
FIX/ADM fork retained syntactically = yes
FIX/ADM reduction truth differs = no
```

If an authority adopts v0.3 as the intended closure of v0.1, the prior
machine-grammar blocker is removed. If it chooses a different grammar or a
narrower task domain, that successor needs a separate compiler/admissibility
audit.

## Remaining gate

The grammar can be proposed and mechanically verified internally. It cannot
declare itself authoritative or supply two independent expert teams. External
review remains 0/2.
