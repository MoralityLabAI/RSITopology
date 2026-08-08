# ASMP-3 machine grammar v0.3

This package supplies the executable machine grammar requested after v2.21:
canonical bytes, strict validation, typed universal IR, exact gas, a bounded
universal Turing-machine simulator, FIX/ADM instance syntax, and a compiler for
the undecidability family.

Start with:

- `ASMP3_MACHINE_GRAMMAR_SPEC_v0_3.md` for the normative successor proposal;
- `BUILTIN_SEMANTICS_v0_3.md` for the frozen component macros;
- `ASMP3_MACHINE_GRAMMAR_REPORT_v0_3.md` for the research summary; and
- `RESOLUTION_EFFECT_v0_3.md` for the precise impact on ASMP-3.

Reproduce:

```powershell
python run_machine_grammar.py
python verify_machine_grammar.py
python -m pytest . -q
python build_release_manifest.py
```
