# ASMP-3 rational polyhedral TV frontier v0.9

This package lifts the v0.8 finite transcript-separation theorem from explicit
law lists to rational H-polytopes.

It provides:

- a polynomial-size TV-distance LP;
- a constructive terminal-verifier/Farkas dual LP;
- matching exact rational lower and upper certificates;
- interval-noise, hull-collision, and joint-event robust fixtures; and
- a clean-room checker.

Run:

```powershell
python run_polyhedral_tv_frontier.py
python verify_polyhedral_tv_frontier.py
python build_release_manifest.py
python -m pytest . -q
```

The complexity claim is conditional on polynomial-size rational descriptions
of the complete truthful and false terminal-law polytopes.
