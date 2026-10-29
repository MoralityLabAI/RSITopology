# ASMP-3 typed successor draft v0.2

This directory converts the exact v0.7 protocol fork into a nonnormative typed
problem-definition repair.

It separates:

```text
WV-FIX:  message interface fixed before protocol algorithms;
WV-ADM:  protocol may select an interface from a declared class.
```

It also moves `Refute` to the same layer as the protocol class being
characterized, quotients registered semantic replicas, and replaces the
single-atom noise condition with a joint transcript-conditional risk object.

Run:

```powershell
python validate_typed_successor.py
python build_release_manifest.py
python -m pytest . -q
```

The draft does not amend ASMP-3 v0.1. An authoritative maintainer or review
process must adopt, revise, or reject it as a successor version.
